from config.fhir_systems import (
    HOSPITAL_MEDICATION_SYSTEM,
    MEDICATION_CODE_SYSTEM
)


def map_medication(
    canonical_medication_id,
    df_medication_master
):
    # ---------------------------------------------------------
    # 1. PROCURAR O MEDICAMENTO NA TABELA MASTER
    # ---------------------------------------------------------

    # Procuramos o medicamento através do identificador
    # canónico utilizado pelo projeto.
    medication_matches = df_medication_master[
        df_medication_master["canonical_medication_id"]
        == canonical_medication_id
    ]

    # Se não existir correspondência,
    # não conseguimos criar o recurso Medication.
    if len(medication_matches) == 0:
        return None

    # O identificador canónico deve ser único.
    # Mais do que uma linha indica um problema
    # de qualidade dos dados.
    if len(medication_matches) > 1:
        raise ValueError(
            f"Multiple medications found for "
            f"{canonical_medication_id}"
        )

    # Selecionamos a única linha encontrada.
    medication = medication_matches.iloc[0]

    # ---------------------------------------------------------
    # 2. CONSTRUIR O RECURSO MEDICATION
    # ---------------------------------------------------------

    medication_resource = {
        "resourceType": "Medication",

        # -----------------------------------------------------
        # IDENTIFICADOR CANÓNICO
        # -----------------------------------------------------

        # Preservamos o identificador canónico interno
        # utilizado pela nossa camada de interoperabilidade.
        #
        # Exemplo:
        # MED001
        "identifier": [
            {
                "system": HOSPITAL_MEDICATION_SYSTEM,
                "value": canonical_medication_id
            }
        ],

        # -----------------------------------------------------
        # CONCEITO DO MEDICAMENTO
        # -----------------------------------------------------

        # O elemento code representa o conceito clínico
        # correspondente ao medicamento.
        #
        # Nesta V1 utilizamos um CodeSystem sintético próprio
        # do projeto. Ainda não estamos a usar SNOMED CT,
        # ATC ou outra terminologia externa.
        "code": {
            "coding": [
                {
                    "system": MEDICATION_CODE_SYSTEM,
                    "code": canonical_medication_id,
                    "display": medication["substance"]
                }
            ],

            # Mantemos também uma representação textual
            # facilmente legível por humanos.
            "text": medication["substance"]
        },

        # -----------------------------------------------------
        # FORMA FARMACÊUTICA
        # -----------------------------------------------------

        # Nesta primeira versão representamos a forma
        # farmacêutica apenas como texto.
        #
        # Exemplo:
        # SOLUTION_FOR_INFUSION
        #
        # Não estamos ainda a normalizar este valor
        # através de um CodeSystem externo.
        "form": {
            "text": medication["form"]
        }
    }

    # ---------------------------------------------------------
    # 3. DEVOLVER O RECURSO FHIR
    # ---------------------------------------------------------

    return medication_resource