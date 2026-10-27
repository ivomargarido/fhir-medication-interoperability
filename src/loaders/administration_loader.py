import pandas as pd


def load_emergency_administrations(file_path):
    df = pd.read_csv(
        file_path,
        parse_dates=["administered_at"]
    )

    return df