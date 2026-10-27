def resolve_patient_id(
    source_system,
    source_patient_id,
    df_emergency_patients,
    df_pharmacy_patients,
    df_inpatient_patients
):
    # Escolhemos a tabela correta consoante o sistema de origem.
    if source_system == "EMERGENCY":
        df_source = df_emergency_patients
        id_column = "er_patient_id"

    elif source_system == "PHARMACY":
        df_source = df_pharmacy_patients
        id_column = "pharmacy_patient_id"

    elif source_system == "INPATIENT":
        df_source = df_inpatient_patients
        id_column = "ip_patient_id"

    else:
        # Se recebemos um sistema desconhecido,
        # não conseguimos fazer a resolução de identidade.
        raise ValueError(
            f"Unknown source system: {source_system}"
        )

    # Procuramos o identificador local na tabela do sistema.
    matches = df_source[
        df_source[id_column] == source_patient_id
    ]

    # Se não existir correspondência,
    # devolvemos None.
    if len(matches) == 0:
        return None

    # Se existir mais de uma correspondência,
    # temos um problema de qualidade/duplicação.
    if len(matches) > 1:
        raise ValueError(
            f"Multiple patient mappings found for "
            f"{source_system} / {source_patient_id}"
        )

    # Devolvemos o hospital_patient_id,
    # que é a identidade canónica usada no nosso projeto.
    return matches.iloc[0]["hospital_patient_id"]