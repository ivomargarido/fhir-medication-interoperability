def validate_medication_code_exists(
    df_administrations,
    df_medication_mapping,
    source_system="EMERGENCY"
):
    # Filtramos a tabela de mapping para usar apenas
    # os códigos pertencentes ao sistema que estamos a validar.
    source_mapping = df_medication_mapping[
        df_medication_mapping["source_system"] == source_system
    ]

    # Criamos um set com todos os códigos de medicamento válidos
    # para esse sistema.
    # Exemplo: {"PARA-INF"}
    valid_medication_codes = set(
        source_mapping["source_code"]
    )

    # Lista onde vamos guardar o resultado da validação
    # de cada administração.
    results = []

    # Percorremos cada administração individualmente.
    for _, row in df_administrations.iterrows():

        # Extraímos o código local do medicamento usado
        # nessa administração.
        medication_code = row["medication_code"]

        # Verificamos se o código existe no mapping
        # do sistema EMERGENCY.
        if medication_code in valid_medication_codes:

            # O código é conhecido e passa esta regra.
            results.append({
                "record_id": row["er_administration_id"],
                "validation_status": "VALID",
                "error_code": None
            })

        else:
            # O código não existe no mapping.
            # Não tentamos adivinhar qual medicamento seria.
            results.append({
                "record_id": row["er_administration_id"],
                "validation_status": "REJECTED",
                "error_code": "UNKNOWN_MEDICATION_CODE"
            })

    # Devolvemos o resultado da validação
    # de todas as administrações.
    return results