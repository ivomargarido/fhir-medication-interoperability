import pandas as pd


def load_emergency_patients(file_path):
    df = pd.read_csv(
        file_path,
        parse_dates=["birth_date"]
    )

    return df