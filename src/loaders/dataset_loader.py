from pathlib import Path

from src.loaders.patient_loader import load_emergency_patients
from src.loaders.encounter_loader import load_emergency_encounters
from src.loaders.prescription_loader import load_emergency_prescriptions
from src.loaders.administration_loader import load_emergency_administrations

from src.loaders.pharmacy_loader import (
    load_pharmacy_patients,
    load_pharmacy_orders,
    load_pharmacy_dispenses
)

from src.loaders.inpatient_loader import (
    load_inpatient_patients,
    load_inpatient_encounters,
    load_inpatient_medication_orders
)

from src.loaders.reference_loader import (
    load_practitioners,
    load_practitioner_identifiers,
    load_medication_master,
    load_medication_code_mapping
)


def load_valid_dataset(project_root):
    data_path = (
        Path(project_root)
        / "data"
        / "canonical"
        / "valid"
    )

    dataset = {
        "emergency_patients": load_emergency_patients(
            data_path / "emergency_patients.csv"
        ),

        "emergency_encounters": load_emergency_encounters(
            data_path / "emergency_encounters.csv"
        ),

        "emergency_prescriptions": load_emergency_prescriptions(
            data_path / "emergency_prescriptions.csv"
        ),

        "emergency_administrations": load_emergency_administrations(
            data_path / "emergency_administrations.csv"
        ),

        "pharmacy_patients": load_pharmacy_patients(
            data_path / "pharmacy_patients.csv"
        ),

        "pharmacy_orders": load_pharmacy_orders(
            data_path / "pharmacy_orders.csv"
        ),

        "pharmacy_dispenses": load_pharmacy_dispenses(
            data_path / "pharmacy_dispenses.csv"
        ),

        "inpatient_patients": load_inpatient_patients(
            data_path / "inpatient_patients.csv"
        ),

        "inpatient_encounters": load_inpatient_encounters(
            data_path / "inpatient_encounters.csv"
        ),

        "inpatient_medication_orders": load_inpatient_medication_orders(
            data_path / "inpatient_medication_orders.csv"
        ),

        "practitioners": load_practitioners(
            data_path / "practitioners.csv"
        ),

        "practitioner_identifiers": load_practitioner_identifiers(
            data_path / "practitioner_identifiers.csv"
        ),

        "medication_master": load_medication_master(
            data_path / "medication_master.csv"
        ),

        "medication_code_mapping": load_medication_code_mapping(
            data_path / "medication_code_mapping.csv"
        )
    }

    return dataset