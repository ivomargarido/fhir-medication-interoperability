import pandas as pd


def load_pharmacy_patients(file_path):
    return pd.read_csv(file_path)


def load_pharmacy_orders(file_path):
    return pd.read_csv(
        file_path,
        parse_dates=["order_datetime"]
    )


def load_pharmacy_dispenses(file_path):
    return pd.read_csv(
        file_path,
        parse_dates=["dispensed_at"]
    )