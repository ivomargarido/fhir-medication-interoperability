from config.fhir_systems import (
    HOSPITAL_PATIENT_SYSTEM,
    HOSPITAL_PRACTITIONER_SYSTEM,
    HOSPITAL_MEDICATION_SYSTEM,
    EMERGENCY_ENCOUNTER_SYSTEM,
    EMERGENCY_PRESCRIPTION_SYSTEM,
    EMERGENCY_ADMINISTRATION_SYSTEM
)

from src.identity.practitioner_resolver import (
    resolve_practitioner_id
)

from src.terminology.medication_resolver import (
    resolve_medication_id
)


def map_emergency_medication_administration(
    er_administration_id,
    df_administrations,
    df_practitioner_identifiers,
    df_medication_mapping
):
    # ---------------------------------------------------------
    # 1. PROCURAR A ADMINISTRAÇÃO
    # ---------------------------------------------------------

    # Procuramos a administração através do identificador
    # local utilizado no sistema de Urgência.
    administration_matches = df_administrations[
        df_administrations["er_administration_id"]
        == er_administration_id
    ]

    # Se não existir correspondência,
    # não conseguimos criar o MedicationAdministration.
    if len(administration_matches) == 0:
        return None

    # O identificador da administração deve ser único.
    # Mais do que uma linha representa um problema
    # de qualidade dos dados.
    if len(administration_matches) > 1:
        raise ValueError(
            f"Multiple administrations found for "
            f"{er_administration_id}"
        )

    # Selecionamos a única linha encontrada.
    administration = administration_matches.iloc[0]

    # ---------------------------------------------------------
    # 2. RESOLVER O MEDICAMENTO
    # ---------------------------------------------------------

    # O sistema de Urgência utiliza um código local
    # para o medicamento, por exemplo PARA-INF.
    #
    # A camada terminológica converte esse código
    # para o conceito canónico do projeto, MED001.
    medication_id = resolve_medication_id(
        source_system="EMERGENCY",
        source_code=administration["medication_code"],
        df_medication_mapping=df_medication_mapping
    )

    # Se não conseguirmos resolver o medicamento,
    # não criamos uma referência inválida.
    if medication_id is None:
        raise ValueError(
            f"Unknown medication code: "
            f"{administration['medication_code']}"
        )

    # ---------------------------------------------------------
    # 3. RESOLVER O ENFERMEIRO
    # ---------------------------------------------------------

    # O sistema de origem contém o identificador local
    # do enfermeiro, por exemplo NUR014.
    #
    # Resolvemo-lo para o identificador canónico
    # de Practitioner, por exemplo PRAC002.
    practitioner_id = resolve_practitioner_id(
        source_system="EMERGENCY",
        source_id=administration["nurse_id"],
        df_practitioner_identifiers=(
            df_practitioner_identifiers
        )
    )

    # Se o profissional não puder ser resolvido,
    # interrompemos a transformação.
    if practitioner_id is None:
        raise ValueError(
            f"Unknown practitioner: "
            f"{administration['nurse_id']}"
        )

    # ---------------------------------------------------------
    # 4. NORMALIZAR O STATUS
    # ---------------------------------------------------------

    # O sistema de origem utiliza "GIVEN".
    #
    # Uma administração já realizada corresponde
    # a "completed" em FHIR.
    status_mapping = {
        "GIVEN": "completed"
    }

    source_status = administration["status"]

    # Se aparecer um estado desconhecido,
    # não inferimos automaticamente o equivalente.
    if source_status not in status_mapping:
        raise ValueError(
            f"Unknown administration status: "
            f"{source_status}"
        )

    fhir_status = status_mapping[source_status]

    # ---------------------------------------------------------
    # 5. CONSTRUIR O MEDICATIONADMINISTRATION
    # ---------------------------------------------------------

    medication_administration = {
        "resourceType": "MedicationAdministration",

        # -----------------------------------------------------
        # IDENTIFICADOR DA ADMINISTRAÇÃO
        # -----------------------------------------------------

        # Preservamos o identificador local
        # atribuído pelo sistema da Urgência.
        "identifier": [
            {
                "system": EMERGENCY_ADMINISTRATION_SYSTEM,
                "value": administration[
                    "er_administration_id"
                ]
            }
        ],

        # -----------------------------------------------------
        # STATUS
        # -----------------------------------------------------

        # Estado convertido para o vocabulário FHIR.
        "status": fhir_status,

        # -----------------------------------------------------
        # MEDICAMENTO
        # -----------------------------------------------------

        # Referenciamos o medicamento através
        # do identificador canónico MED001.
        "medicationReference": {
            "identifier": {
                "system": HOSPITAL_MEDICATION_SYSTEM,
                "value": medication_id
            }
        },

        # -----------------------------------------------------
        # DOENTE
        # -----------------------------------------------------

        # Referenciamos o doente através
        # do identificador hospitalar canónico.
        "subject": {
            "identifier": {
                "system": HOSPITAL_PATIENT_SYSTEM,
                "value": administration[
                    "hospital_patient_id"
                ]
            }
        },

        # -----------------------------------------------------
        # CONTEXTO CLÍNICO
        # -----------------------------------------------------

        # A administração ocorreu durante
        # o Encounter da Urgência.
        #
        # Esta ligação deve ser preservada mesmo que
        # o doente seja posteriormente internado.
        "context": {
            "identifier": {
                "system": EMERGENCY_ENCOUNTER_SYSTEM,
                "value": administration[
                    "er_encounter_id"
                ]
            }
        },

        # -----------------------------------------------------
        # PRESCRIÇÃO ORIGINAL
        # -----------------------------------------------------

        # Ligamos a administração à prescrição
        # que lhe deu origem.
        "request": {
            "identifier": {
                "system": EMERGENCY_PRESCRIPTION_SYSTEM,
                "value": administration[
                    "er_prescription_id"
                ]
            }
        },

        # -----------------------------------------------------
        # MOMENTO DA ADMINISTRAÇÃO
        # -----------------------------------------------------

        # effectiveDateTime representa o momento
        # em que o medicamento foi efetivamente administrado.
        "effectiveDateTime": (
            administration["administered_at"].isoformat()
        ),

        # -----------------------------------------------------
        # PROFISSIONAL QUE ADMINISTROU
        # -----------------------------------------------------

        # Referenciamos o enfermeiro
        # através do Practitioner canónico.
        "performer": [
            {
                "actor": {
                    "identifier": {
                        "system": HOSPITAL_PRACTITIONER_SYSTEM,
                        "value": practitioner_id
                    }
                }
            }
        ],

        # -----------------------------------------------------
        # DOSE EFETIVAMENTE ADMINISTRADA
        # -----------------------------------------------------

        # Aqui registamos aquilo que foi realmente
        # administrado ao doente.
        "dosage": {
            # Texto legível para inspeção humana.
            "text": (
                f"{administration['dose_value']} "
                f"{administration['dose_unit']} "
                f"{administration['route']}"
            ),

            # Nesta V1 a via ainda é representada
            # apenas através de texto.
            "route": {
                "text": administration["route"]
            },

            # Quantidade efetivamente administrada.
            "dose": {
                "value": float(
                    administration["dose_value"]
                ),
                "unit": administration[
                    "dose_unit"
                ]
            }
        }
    }

    # ---------------------------------------------------------
    # 6. DEVOLVER O RECURSO FHIR
    # ---------------------------------------------------------

    return medication_administration