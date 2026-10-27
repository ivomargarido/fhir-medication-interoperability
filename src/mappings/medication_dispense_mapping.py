from config.fhir_systems import (
    HOSPITAL_PATIENT_SYSTEM,
    HOSPITAL_PRACTITIONER_SYSTEM,
    HOSPITAL_MEDICATION_SYSTEM,
    EMERGENCY_PRESCRIPTION_SYSTEM,
    PHARMACY_DISPENSE_SYSTEM
)

from src.identity.practitioner_resolver import (
    resolve_practitioner_id
)

from src.terminology.medication_resolver import (
    resolve_medication_id
)


def map_pharmacy_medication_dispense(
    dispense_id,
    df_dispenses,
    df_pharmacy_orders,
    df_practitioner_identifiers,
    df_medication_mapping
):
    # ---------------------------------------------------------
    # 1. PROCURAR A DISPENSA
    # ---------------------------------------------------------

    # Procuramos a dispensa através do identificador
    # local utilizado pelo sistema da Farmácia.
    dispense_matches = df_dispenses[
        df_dispenses["dispense_id"] == dispense_id
    ]

    # Se não existir correspondência,
    # não conseguimos criar o MedicationDispense.
    if len(dispense_matches) == 0:
        return None

    # O identificador da dispensa deve ser único.
    # Mais do que uma linha representa um problema
    # de qualidade dos dados.
    if len(dispense_matches) > 1:
        raise ValueError(
            f"Multiple dispenses found for {dispense_id}"
        )

    # Selecionamos a única dispensa encontrada.
    dispense = dispense_matches.iloc[0]

    # ---------------------------------------------------------
    # 2. PROCURAR A ORDEM LOCAL DA FARMÁCIA
    # ---------------------------------------------------------

    # A dispensa conhece apenas o pharmacy_order_id,
    # por exemplo PH-O291.
    #
    # Precisamos dessa ordem local para chegar
    # à prescrição clínica original ER-RX001.
    order_matches = df_pharmacy_orders[
        df_pharmacy_orders["pharmacy_order_id"]
        == dispense["pharmacy_order_id"]
    ]

    # A ordem local da Farmácia é necessária
    # para identificar a prescrição original.
    if len(order_matches) == 0:
        raise ValueError(
            f"Pharmacy order not found: "
            f"{dispense['pharmacy_order_id']}"
        )

    # O identificador da ordem também deve ser único.
    if len(order_matches) > 1:
        raise ValueError(
            f"Multiple pharmacy orders found for "
            f"{dispense['pharmacy_order_id']}"
        )

    # Selecionamos a única ordem encontrada.
    pharmacy_order = order_matches.iloc[0]

    # ---------------------------------------------------------
    # 3. RESOLVER O MEDICAMENTO
    # ---------------------------------------------------------

    # A Farmácia utiliza o seu código local
    # para o medicamento, por exemplo PAR10MGML.
    #
    # A camada terminológica converte esse código
    # para o conceito canónico do projeto, MED001.
    medication_id = resolve_medication_id(
        source_system="PHARMACY",
        source_code=dispense["drug_code"],
        df_medication_mapping=df_medication_mapping
    )

    # Se não conseguirmos resolver o medicamento,
    # não criamos uma referência inválida.
    if medication_id is None:
        raise ValueError(
            f"Unknown pharmacy medication code: "
            f"{dispense['drug_code']}"
        )

    # ---------------------------------------------------------
    # 4. RESOLVER O FARMACÊUTICO
    # ---------------------------------------------------------

    # O dataset contém o identificador local
    # do farmacêutico, por exemplo PHA006.
    #
    # Resolvemo-lo para o identificador canónico
    # de Practitioner, por exemplo PRAC003.
    pharmacist_id = resolve_practitioner_id(
        source_system="PHARMACY",
        source_id=dispense["pharmacist_id"],
        df_practitioner_identifiers=(
            df_practitioner_identifiers
        )
    )

    # Se o farmacêutico não puder ser resolvido,
    # interrompemos a transformação.
    if pharmacist_id is None:
        raise ValueError(
            f"Unknown pharmacist: "
            f"{dispense['pharmacist_id']}"
        )

    # ---------------------------------------------------------
    # 5. NORMALIZAR O STATUS
    # ---------------------------------------------------------

    # Fazemos o mapping entre os estados
    # do sistema da Farmácia e FHIR.
    status_mapping = {
        "DISPENSED": "completed",
        "CANCELLED": "cancelled",
        "IN_PROGRESS": "in-progress"
    }

    source_status = dispense["status"]

    # Se aparecer um estado que não conhecemos,
    # não tentamos inferir o equivalente.
    if source_status not in status_mapping:
        raise ValueError(
            f"Unknown dispense status: "
            f"{source_status}"
        )

    fhir_status = status_mapping[source_status]

    # ---------------------------------------------------------
    # 6. CONSTRUIR O MEDICATIONDISPENSE
    # ---------------------------------------------------------

    medication_dispense = {
        "resourceType": "MedicationDispense",

        # -----------------------------------------------------
        # IDENTIFICADOR DA DISPENSA
        # -----------------------------------------------------

        # Preservamos o identificador local
        # atribuído pelo sistema da Farmácia.
        "identifier": [
            {
                "system": PHARMACY_DISPENSE_SYSTEM,
                "value": dispense["dispense_id"]
            }
        ],

        # -----------------------------------------------------
        # STATUS
        # -----------------------------------------------------

        # Estado da dispensa convertido para FHIR.
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
                "value": dispense[
                    "hospital_patient_id"
                ]
            }
        },

        # -----------------------------------------------------
        # PRESCRIÇÃO ORIGINAL
        # -----------------------------------------------------

        # A Farmácia possui uma ordem interna PH-O291,
        # mas essa ordem NÃO é uma segunda prescrição FHIR.
        #
        # Através de source_order_id chegamos
        # à prescrição original ER-RX001.
        "authorizingPrescription": [
            {
                "identifier": {
                    "system": EMERGENCY_PRESCRIPTION_SYSTEM,
                    "value": pharmacy_order[
                        "source_order_id"
                    ]
                }
            }
        ],

        # -----------------------------------------------------
        # QUANTIDADE DISPENSADA
        # -----------------------------------------------------

        # Esta quantidade representa aquilo
        # que foi fisicamente dispensado.
        #
        # Não deve ser confundida com
        # a dose prescrita ou administrada.
        "quantity": {
            "value": float(
                dispense["quantity"]
            ),
            "unit": dispense[
                "quantity_unit"
            ]
        },

        # -----------------------------------------------------
        # MOMENTO DA DISPENSA
        # -----------------------------------------------------

        # Registamos o momento em que
        # o medicamento foi efetivamente entregue/dispensado.
        "whenHandedOver": (
            dispense["dispensed_at"].isoformat()
        ),

        # -----------------------------------------------------
        # PROFISSIONAL RESPONSÁVEL
        # -----------------------------------------------------

        # Referenciamos o farmacêutico
        # através do Practitioner canónico.
        "performer": [
            {
                "actor": {
                    "identifier": {
                        "system": HOSPITAL_PRACTITIONER_SYSTEM,
                        "value": pharmacist_id
                    }
                }
            }
        ]
    }

    # ---------------------------------------------------------
    # 7. DEVOLVER O RECURSO FHIR
    # ---------------------------------------------------------

    return medication_dispense