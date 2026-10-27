from config.fhir_systems import (
    HOSPITAL_PATIENT_SYSTEM,
    HOSPITAL_PRACTITIONER_SYSTEM,
    HOSPITAL_MEDICATION_SYSTEM,
    EMERGENCY_ENCOUNTER_SYSTEM,
    EMERGENCY_PRESCRIPTION_SYSTEM
)

from src.identity.practitioner_resolver import (
    resolve_practitioner_id
)

from src.terminology.medication_resolver import (
    resolve_medication_id
)


def map_emergency_medication_request(
    er_prescription_id,
    df_prescriptions,
    df_practitioner_identifiers,
    df_medication_mapping
):
    # ---------------------------------------------------------
    # 1. PROCURAR A PRESCRIÇÃO
    # ---------------------------------------------------------

    # Procuramos a prescrição da Urgência através
    # do identificador local.
    prescription_matches = df_prescriptions[
        df_prescriptions["er_prescription_id"]
        == er_prescription_id
    ]

    # Se não existir correspondência,
    # não conseguimos criar o MedicationRequest.
    if len(prescription_matches) == 0:
        return None

    # O identificador da prescrição deve ser único.
    if len(prescription_matches) > 1:
        raise ValueError(
            f"Multiple prescriptions found for "
            f"{er_prescription_id}"
        )

    # Selecionamos a única linha encontrada.
    prescription = prescription_matches.iloc[0]

    # ---------------------------------------------------------
    # 2. RESOLVER O PRESCRITOR
    # ---------------------------------------------------------

    # O sistema de Urgência utiliza um identificador local
    # para o médico, por exemplo DOC023.
    #
    # Resolvemo-lo para o nosso identificador canónico
    # de Practitioner, por exemplo PRAC001.
    practitioner_id = resolve_practitioner_id(
        source_system="EMERGENCY",
        source_id=prescription["prescriber_id"],
        df_practitioner_identifiers=(
            df_practitioner_identifiers
        )
    )

    # Se o prescritor não puder ser resolvido,
    # não criamos uma referência inválida.
    if practitioner_id is None:
        raise ValueError(
            f"Unknown practitioner: "
            f"{prescription['prescriber_id']}"
        )

    # ---------------------------------------------------------
    # 3. RESOLVER O MEDICAMENTO
    # ---------------------------------------------------------

    # O sistema de Urgência utiliza um código local
    # para o medicamento, por exemplo PARA-INF.
    #
    # A camada terminológica converte-o no conceito
    # canónico do projeto, por exemplo MED001.
    medication_id = resolve_medication_id(
        source_system="EMERGENCY",
        source_code=prescription["medication_code"],
        df_medication_mapping=df_medication_mapping
    )

    # Se o medicamento não puder ser resolvido,
    # interrompemos a transformação.
    if medication_id is None:
        raise ValueError(
            f"Unknown medication code: "
            f"{prescription['medication_code']}"
        )

    # ---------------------------------------------------------
    # 4. NORMALIZAR O STATUS
    # ---------------------------------------------------------

    # Fazemos o mapping entre os estados do sistema
    # de origem e os estados permitidos em FHIR.
    status_mapping = {
        "ACTIVE": "active",
        "CANCELLED": "cancelled",
        "FINISHED": "completed"
    }

    source_status = prescription["status"]

    # Se aparecer um estado que não conhecemos,
    # não tentamos inferir automaticamente o equivalente.
    if source_status not in status_mapping:
        raise ValueError(
            f"Unknown prescription status: "
            f"{source_status}"
        )

    fhir_status = status_mapping[source_status]

    # ---------------------------------------------------------
    # 5. CONSTRUIR O MEDICATIONREQUEST
    # ---------------------------------------------------------

    medication_request = {
        "resourceType": "MedicationRequest",

        # -----------------------------------------------------
        # IDENTIFICADOR DA PRESCRIÇÃO
        # -----------------------------------------------------

        # Preservamos o identificador local da prescrição
        # da Urgência.
        "identifier": [
            {
                "system": EMERGENCY_PRESCRIPTION_SYSTEM,
                "value": prescription[
                    "er_prescription_id"
                ]
            }
        ],

        # -----------------------------------------------------
        # STATUS E INTENT
        # -----------------------------------------------------

        # Estado da prescrição convertido para FHIR.
        "status": fhir_status,

        # "order" indica que estamos perante
        # uma ordem terapêutica efetiva.
        "intent": "order",

        # -----------------------------------------------------
        # MEDICAMENTO
        # -----------------------------------------------------

        # Referenciamos o medicamento através
        # do seu identificador canónico.
        #
        # Ainda não utilizamos Medication/<resource.id>,
        # porque não temos IDs atribuídos
        # por um servidor FHIR.
        "medicationReference": {
            "identifier": {
                "system": HOSPITAL_MEDICATION_SYSTEM,
                "value": medication_id
            }
        },

        # -----------------------------------------------------
        # DOENTE
        # -----------------------------------------------------

        # Identificamos o doente através
        # do hospital_patient_id.
        "subject": {
            "identifier": {
                "system": HOSPITAL_PATIENT_SYSTEM,
                "value": prescription[
                    "hospital_patient_id"
                ]
            }
        },

        # -----------------------------------------------------
        # ENCOUNTER
        # -----------------------------------------------------

        # Preservamos o contexto clínico onde
        # a prescrição foi criada.
        "encounter": {
            "identifier": {
                "system": EMERGENCY_ENCOUNTER_SYSTEM,
                "value": prescription[
                    "er_encounter_id"
                ]
            }
        },

        # -----------------------------------------------------
        # DATA DA PRESCRIÇÃO
        # -----------------------------------------------------

        # Momento em que a prescrição foi criada.
        "authoredOn": (
            prescription["prescribed_at"].isoformat()
        ),

        # -----------------------------------------------------
        # PRESCRITOR
        # -----------------------------------------------------

        # Referenciamos o Practitioner canónico
        # resultante da identity resolution.
        "requester": {
            "identifier": {
                "system": HOSPITAL_PRACTITIONER_SYSTEM,
                "value": practitioner_id
            }
        },

        # -----------------------------------------------------
        # INSTRUÇÕES DE ADMINISTRAÇÃO
        # -----------------------------------------------------

        "dosageInstruction": [
            {
                # Texto legível que resume
                # a instrução terapêutica.
                "text": (
                    f"{prescription['dose_value']} "
                    f"{prescription['dose_unit']} "
                    f"{prescription['route']} "
                    f"{prescription['frequency']}"
                ),

                # Nesta V1 a via de administração
                # ainda é representada apenas como texto.
                "route": {
                    "text": prescription["route"]
                },

                # Dose prescrita.
                "doseAndRate": [
                    {
                        "doseQuantity": {
                            "value": float(
                                prescription[
                                    "dose_value"
                                ]
                            ),
                            "unit": prescription[
                                "dose_unit"
                            ]
                        }
                    }
                ]
            }
        ]
    }

    # ---------------------------------------------------------
    # 6. REPRESENTAR FREQUÊNCIA "ONCE"
    # ---------------------------------------------------------

    # Para uma prescrição ONCE sabemos que existe
    # apenas uma administração planeada.
    #
    # Representamos isso através de repeat.count = 1.
    if prescription["frequency"] == "ONCE":
        medication_request[
            "dosageInstruction"
        ][0]["timing"] = {
            "repeat": {
                "count": 1
            }
        }

    # ---------------------------------------------------------
    # 7. DEVOLVER O RECURSO FHIR
    # ---------------------------------------------------------

    return medication_request