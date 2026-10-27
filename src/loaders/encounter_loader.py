import pandas as pd


def load_emergency_encounters(file_path):
    df = pd.read_csv(
        file_path,
        parse_dates=[
            "admission_datetime",
            "discharge_datetime"
        ]
    )

    return df