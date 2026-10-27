from config.fhir_systems import (
    HOSPITAL_PATIENT_SYSTEM,
    EMERGENCY_PATIENT_SYSTEM,
    PHARMACY_PATIENT_SYSTEM,
    INPATIENT_PATIENT_SYSTEM
)


def map_patient(
    hospital_patient_id,
    df_emergency_patients,
    df_pharmacy_patients,
    df_inpatient_patients
):
    # ---------------------------------------------------------
    # 1. PROCURAR O DOENTE NOS VÁRIOS SISTEMAS
    # ---------------------------------------------------------

    # Procuramos o doente na tabela da Urgência
    # através do hospital_patient_id comum.
    emergency_matches = df_emergency_patients[
        df_emergency_patients["hospital_patient_id"]
        == hospital_patient_id
    ]

    # Procuramos o mesmo doente na tabela da Farmácia.
    pharmacy_matches = df_pharmacy_patients[
        df_pharmacy_patients["hospital_patient_id"]
        == hospital_patient_id
    ]

    # Procuramos o mesmo doente na tabela do Internamento.
    inpatient_matches = df_inpatient_patients[
        df_inpatient_patients["hospital_patient_id"]
        == hospital_patient_id
    ]

    # ---------------------------------------------------------
    # 2. VERIFICAR SE O DOENTE EXISTE
    # ---------------------------------------------------------

    # Se o hospital_patient_id não existir em nenhum
    # dos três sistemas, não conseguimos criar o Patient.
    if (
        len(emergency_matches) == 0
        and len(pharmacy_matches) == 0
        and len(inpatient_matches) == 0
    ):
        return None

    # ---------------------------------------------------------
    # 3. CONSTRUIR OS IDENTIFIERS FHIR
    # ---------------------------------------------------------

    # O primeiro identifier é sempre o identificador
    # hospitalar canónico usado para ligar os vários sistemas.
    identifiers = [
        {
            "system": HOSPITAL_PATIENT_SYSTEM,
            "value": hospital_patient_id
        }
    ]

    # Se o doente existir na Urgência,
    # preservamos também o identificador local desse sistema.
    if len(emergency_matches) > 0:
        emergency_patient = emergency_matches.iloc[0]

        identifiers.append({
            "system": EMERGENCY_PATIENT_SYSTEM,
            "value": emergency_patient["er_patient_id"]
        })

    # Se o doente existir na Farmácia,
    # preservamos o respetivo identificador local.
    if len(pharmacy_matches) > 0:
        pharmacy_patient = pharmacy_matches.iloc[0]

        identifiers.append({
            "system": PHARMACY_PATIENT_SYSTEM,
            "value": pharmacy_patient["pharmacy_patient_id"]
        })

    # Se o doente existir no Internamento,
    # preservamos também esse identificador local.
    if len(inpatient_matches) > 0:
        inpatient_patient = inpatient_matches.iloc[0]

        identifiers.append({
            "system": INPATIENT_PATIENT_SYSTEM,
            "value": inpatient_patient["ip_patient_id"]
        })

    # ---------------------------------------------------------
    # 4. CONSTRUIR O RECURSO BASE PATIENT
    # ---------------------------------------------------------

    patient_resource = {
        "resourceType": "Patient",
        "identifier": identifiers
    }

    # ---------------------------------------------------------
    # 5. ESCOLHER A FONTE DOS DADOS DEMOGRÁFICOS
    # ---------------------------------------------------------

    # Nesta V1 damos prioridade aos dados da Urgência.
    #
    # Se o doente não existir na Urgência,
    # usamos os dados do Internamento.
    #
    # A tabela da Farmácia não contém birth_date nem sex.
    demographic_source = None

    if len(emergency_matches) > 0:
        demographic_source = emergency_matches.iloc[0]

    elif len(inpatient_matches) > 0:
        demographic_source = inpatient_matches.iloc[0]

    # ---------------------------------------------------------
    # 6. ADICIONAR DATA DE NASCIMENTO E SEXO
    # ---------------------------------------------------------

    if demographic_source is not None:

        # Convertemos a data de nascimento para o formato
        # YYYY-MM-DD exigido pelo campo FHIR birthDate.
        patient_resource["birthDate"] = (
            demographic_source["birth_date"].strftime("%Y-%m-%d")
        )

        # Fazemos um mapping simples do código local
        # para os valores permitidos em Patient.gender.
        gender_mapping = {
            "M": "male",
            "F": "female"
        }

        source_sex = demographic_source["sex"]

        # Só adicionamos gender se conhecermos
        # explicitamente a correspondência.
        if source_sex in gender_mapping:
            patient_resource["gender"] = (
                gender_mapping[source_sex]
            )

    # ---------------------------------------------------------
    # 7. DEVOLVER O RECURSO FHIR
    # ---------------------------------------------------------

    return patient_resource