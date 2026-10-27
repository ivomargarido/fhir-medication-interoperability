import pandas as pd

from config.fhir_systems import (
    HOSPITAL_PATIENT_SYSTEM,
    EMERGENCY_ENCOUNTER_SYSTEM,
    INPATIENT_ENCOUNTER_SYSTEM
)


def map_emergency_encounter(
    er_encounter_id,
    df_emergency_encounters
):
    # ---------------------------------------------------------
    # 1. PROCURAR O ENCOUNTER DA URGÊNCIA
    # ---------------------------------------------------------

    # Procuramos o episódio de Urgência através
    # do identificador local do sistema.
    encounter_matches = df_emergency_encounters[
        df_emergency_encounters["er_encounter_id"]
        == er_encounter_id
    ]

    # Se não existir correspondência,
    # não conseguimos criar o recurso Encounter.
    if len(encounter_matches) == 0:
        return None

    # O identificador do encounter deve ser único.
    # Mais do que uma linha representa um problema
    # de qualidade dos dados.
    if len(encounter_matches) > 1:
        raise ValueError(
            f"Multiple emergency encounters found for "
            f"{er_encounter_id}"
        )

    # Selecionamos a única linha encontrada.
    encounter = encounter_matches.iloc[0]

    # ---------------------------------------------------------
    # 2. DETERMINAR O STATUS FHIR
    # ---------------------------------------------------------

    # Se existir uma data/hora de alta,
    # consideramos o encounter terminado.
    if pd.notna(encounter["discharge_datetime"]):
        encounter_status = "finished"

    # Caso contrário, o encounter continua em curso.
    else:
        encounter_status = "in-progress"

    # ---------------------------------------------------------
    # 3. CONSTRUIR O RECURSO ENCOUNTER
    # ---------------------------------------------------------

    encounter_resource = {
        "resourceType": "Encounter",

        # Preservamos o identificador local
        # do episódio de Urgência.
        "identifier": [
            {
                "system": EMERGENCY_ENCOUNTER_SYSTEM,
                "value": er_encounter_id
            }
        ],

        # Estado normalizado para FHIR.
        "status": encounter_status,

        # Classificamos este encounter como emergência.
        #
        # Aqui usamos o CodeSystem oficial HL7 v3-ActCode,
        # pelo que este URI NÃO deve ser substituído
        # pelos namespaces sintéticos do projeto.
        "class": {
            "system": (
                "http://terminology.hl7.org/"
                "CodeSystem/v3-ActCode"
            ),
            "code": "EMER",
            "display": "emergency"
        },

        # Identificamos o doente pelo identificador
        # hospitalar canónico.
        #
        # Ainda não usamos Patient/<resource.id>
        # porque o servidor FHIR ainda não atribuiu
        # IDs técnicos aos recursos.
        "subject": {
            "identifier": {
                "system": HOSPITAL_PATIENT_SYSTEM,
                "value": encounter["hospital_patient_id"]
            }
        },

        # Registamos o início do episódio.
        "period": {
            "start": (
                encounter["admission_datetime"].isoformat()
            )
        }
    }

    # ---------------------------------------------------------
    # 4. ADICIONAR O FIM DO PERÍODO, SE EXISTIR
    # ---------------------------------------------------------

    # Um encounter terminado deve incluir period.end.
    if pd.notna(encounter["discharge_datetime"]):
        encounter_resource["period"]["end"] = (
            encounter["discharge_datetime"].isoformat()
        )

    # ---------------------------------------------------------
    # 5. DEVOLVER O RECURSO FHIR
    # ---------------------------------------------------------

    return encounter_resource


def map_inpatient_encounter(
    ip_encounter_id,
    df_inpatient_encounters
):
    # ---------------------------------------------------------
    # 1. PROCURAR O ENCOUNTER DE INTERNAMENTO
    # ---------------------------------------------------------

    # Procuramos o episódio de Internamento através
    # do identificador local do sistema.
    encounter_matches = df_inpatient_encounters[
        df_inpatient_encounters["ip_encounter_id"]
        == ip_encounter_id
    ]

    # Se não existir correspondência,
    # não conseguimos criar o recurso Encounter.
    if len(encounter_matches) == 0:
        return None

    # O identificador do encounter deve ser único.
    if len(encounter_matches) > 1:
        raise ValueError(
            f"Multiple inpatient encounters found for "
            f"{ip_encounter_id}"
        )

    # Selecionamos a única linha encontrada.
    encounter = encounter_matches.iloc[0]

    # ---------------------------------------------------------
    # 2. DETERMINAR O STATUS FHIR
    # ---------------------------------------------------------

    # Se existir discharge_datetime,
    # o episódio já terminou.
    if pd.notna(encounter["discharge_datetime"]):
        encounter_status = "finished"

    # Caso contrário, continua ativo.
    else:
        encounter_status = "in-progress"

    # ---------------------------------------------------------
    # 3. CONSTRUIR O RECURSO ENCOUNTER
    # ---------------------------------------------------------

    encounter_resource = {
        "resourceType": "Encounter",

        # Preservamos o identificador local
        # do Internamento.
        "identifier": [
            {
                "system": INPATIENT_ENCOUNTER_SYSTEM,
                "value": ip_encounter_id
            }
        ],

        # Estado normalizado para FHIR.
        "status": encounter_status,

        # Classificamos este encounter como internamento.
        #
        # IMP = inpatient encounter no CodeSystem
        # oficial HL7 v3-ActCode.
        "class": {
            "system": (
                "http://terminology.hl7.org/"
                "CodeSystem/v3-ActCode"
            ),
            "code": "IMP",
            "display": "inpatient encounter"
        },

        # Identificamos o mesmo doente através
        # do identificador hospitalar canónico.
        "subject": {
            "identifier": {
                "system": HOSPITAL_PATIENT_SYSTEM,
                "value": encounter["hospital_patient_id"]
            }
        },

        # Registamos o início do internamento.
        "period": {
            "start": (
                encounter["admission_datetime"].isoformat()
            )
        },

        # Nesta V1 representamos o serviço clínico
        # apenas como texto.
        #
        # Não estamos ainda a criar um Coding formal
        # para PEDIATRICS.
        "serviceType": {
            "text": encounter["service"]
        }
    }

    # ---------------------------------------------------------
    # 4. ADICIONAR O FIM DO PERÍODO, SE EXISTIR
    # ---------------------------------------------------------

    # Se o internamento já tiver terminado,
    # acrescentamos period.end.
    if pd.notna(encounter["discharge_datetime"]):
        encounter_resource["period"]["end"] = (
            encounter["discharge_datetime"].isoformat()
        )

    # ---------------------------------------------------------
    # 5. DEVOLVER O RECURSO FHIR
    # ---------------------------------------------------------

    return encounter_resource
    