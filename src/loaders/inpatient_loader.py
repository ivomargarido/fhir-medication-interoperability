import pandas as pd


def load_inpatient_patients(file_path):
    return pd.read_csv(
        file_path,
        parse_dates=["birth_date"]
    )


def load_inpatient_encounters(file_path):
    return pd.read_csv(
        file_path,
        parse_dates=[
            "admission_datetime",
            "discharge_datetime"
        ]
    )


def load_inpatient_medication_orders(file_path):
    return pd.read_csv(
        file_path,
        parse_dates=["start_datetime"]
    )