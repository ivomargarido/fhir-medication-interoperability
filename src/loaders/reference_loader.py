import pandas as pd


def load_practitioners(file_path):
    return pd.read_csv(file_path)


def load_practitioner_identifiers(file_path):
    return pd.read_csv(file_path)


def load_medication_master(file_path):
    return pd.read_csv(file_path)


def load_medication_code_mapping(file_path):
    return pd.read_csv(file_path)