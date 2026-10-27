def resolve_practitioner_id(
    source_system,
    source_id,
    df_practitioner_identifiers
):
    # Filtramos a tabela de identificadores para procurar
    # exatamente a combinação source_system + source_id.
    matches = df_practitioner_identifiers[
        (df_practitioner_identifiers["source_system"] == source_system)
        & (df_practitioner_identifiers["source_id"] == source_id)
    ]

    # Se não encontrarmos nenhuma linha,
    # significa que o profissional local não está mapeado
    # para uma identidade canónica.
    if len(matches) == 0:
        return None

    # Se encontrarmos mais de uma linha,
    # existe ambiguidade no mapping.
    # Isso não deveria acontecer porque source_system + source_id
    # deve ser único.
    if len(matches) > 1:
        raise ValueError(
            f"Multiple practitioner mappings found for "
            f"{source_system} / {source_id}"
        )

    # Se existe exatamente uma correspondência,
    # devolvemos o practitioner_master_id.
    return matches.iloc[0]["practitioner_master_id"]