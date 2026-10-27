import pandas as pd


def validation_report_to_dataframe(validation_report):
    # Converte a lista de dicionários produzida
    # pela pipeline de validação num DataFrame.
    df_report = pd.DataFrame(validation_report)

    # Devolve a tabela pronta para inspeção,
    # filtragem ou exportação.
    return df_report