import pandas as pd


def load_emergency_prescriptions(file_path):
    df = pd.read_csv(
        file_path,
        parse_dates=["prescribed_at"]
    )

    return df