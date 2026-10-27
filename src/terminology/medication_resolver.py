def resolve_medication_id(
    source_system,
    source_code,
    df_medication_mapping
):
    # Procuramos na tabela de mapping a combinação exata
    # entre o sistema de origem e o código local do medicamento.
    matches = df_medication_mapping[
        (df_medication_mapping["source_system"] == source_system)
        & (df_medication_mapping["source_code"] == source_code)
    ]

    # Se não existir nenhuma correspondência,
    # não tentamos adivinhar qual é o medicamento.
    if len(matches) == 0:
        return None

    # Se existir mais de uma correspondência,
    # temos um problema de qualidade no mapping terminológico.
    if len(matches) > 1:
        raise ValueError(
            f"Multiple medication mappings found for "
            f"{source_system} / {source_code}"
        )

    # Se existir exatamente uma correspondência,
    # devolvemos o identificador canónico do medicamento.
    return matches.iloc[0]["canonical_medication_id"]