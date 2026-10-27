def validate_prescription_exists(df_administrations, df_prescriptions):
    # Criamos um conjunto com todos os IDs de prescrições válidas.
    # Usamos set porque é eficiente para verificar se um valor existe.
    valid_prescription_ids = set(
        df_prescriptions["er_prescription_id"]
    )

    # Lista onde vamos guardar o resultado da validação
    # de cada administração.
    results = []

    # Percorremos cada linha do DataFrame de administrações.
    for _, row in df_administrations.iterrows():

        # Extraímos o ID da prescrição associada à administração atual.
        prescription_id = row["er_prescription_id"]

        # Verificamos se esse ID existe no conjunto de prescrições válidas.
        if prescription_id in valid_prescription_ids:

            # Se existir, a administração passa esta regra de validação.
            results.append({
                "record_id": row["er_administration_id"],
                "validation_status": "VALID",
                "error_code": None
            })

        else:
            # Se não existir, rejeitamos o registo e indicamos
            # explicitamente a causa da falha.
            results.append({
                "record_id": row["er_administration_id"],
                "validation_status": "REJECTED",
                "error_code": "MISSING_PRESCRIPTION"
            })

    # Devolvemos os resultados de todas as administrações avaliadas.
    return results