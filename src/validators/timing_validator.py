def validate_administration_after_prescription(
    df_administrations,
    df_prescriptions
):
    # Vamos criar uma estrutura que associa cada ID de prescrição
    # à respetiva data/hora de prescrição.
    #
    # Exemplo:
    # {
    #     "ER-RX001": Timestamp("2026-10-06 14:50:00+01:00")
    # }
    prescription_times = dict(
        zip(
            df_prescriptions["er_prescription_id"],
            df_prescriptions["prescribed_at"]
        )
    )

    # Lista onde vamos guardar o resultado
    # da validação de cada administração.
    results = []

    # Percorremos todas as administrações.
    for _, row in df_administrations.iterrows():

        # Identificamos qual a prescrição associada
        # à administração atual.
        prescription_id = row["er_prescription_id"]

        # Guardamos a data/hora da administração.
        administered_at = row["administered_at"]

        # Primeiro verificamos se a prescrição existe.
        #
        # Esta função tem como objetivo principal validar tempo,
        # mas não conseguimos comparar timestamps se não soubermos
        # quando a prescrição ocorreu.
        if prescription_id not in prescription_times:
            results.append({
                "record_id": row["er_administration_id"],
                "validation_status": "NOT_EVALUATED",
                "error_code": "PRESCRIPTION_NOT_FOUND"
            })

            # Passamos imediatamente para a próxima administração.
            continue

        # Obtemos a data/hora em que a prescrição foi criada.
        prescribed_at = prescription_times[prescription_id]

        # Comparamos os dois momentos.
        if administered_at >= prescribed_at:

            # A administração ocorreu depois (ou exatamente no mesmo
            # momento) da prescrição, portanto passa esta regra.
            results.append({
                "record_id": row["er_administration_id"],
                "validation_status": "VALID",
                "error_code": None
            })

        else:
            # A administração ocorreu antes da prescrição.
            # Isto é temporalmente incoerente.
            results.append({
                "record_id": row["er_administration_id"],
                "validation_status": "REJECTED",
                "error_code": "ADMINISTRATION_BEFORE_PRESCRIPTION"
            })

    # Devolvemos todos os resultados.
    return results