import json
import logging
import threading
from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data"

_lock = threading.Lock()


def load_json(filename):

    file_path = DATA_DIR / filename

    with _lock:

        with open(file_path, "r") as file:

            return json.load(file)


def save_json(filename, data):

    file_path = DATA_DIR / filename

    with _lock:

        with open(file_path, "w") as file:

            json.dump(
                data,
                file,
                indent=2,
            )


def get_patients():

    return load_json("patients.json")


def get_doctors():

    return load_json("doctors.json")


def get_appointments():

    return load_json("appointments.json")


def save_appointments(appointments):

    save_json("appointments.json", appointments)


def get_appointment_by_id(appointment_id):

    appointments = get_appointments()

    for appointment in appointments:

        if appointment["appointment_id"] == appointment_id:

            return appointment

    return None


def get_appointments_by_patient(patient_id):

    appointments = get_appointments()

    return [
        appointment
        for appointment in appointments
        if appointment.get("patient_id") == patient_id
    ]


def get_doctor_by_id(doctor_id):

    doctors = get_doctors()

    for doctor in doctors:

        if doctor["doctor_id"] == doctor_id:

            return doctor

    return None


# ============================================================
# DATA RESET FOR EVALUATIONS
# ============================================================

# Snapshots of original data for reset
_ORIGINAL_APPOINTMENTS = None


def reset_data():
    """Restore JSON data files to their original state.

    Called before evaluation runs to ensure a clean
    state for deterministic testing.
    """

    global _ORIGINAL_APPOINTMENTS

    if _ORIGINAL_APPOINTMENTS is None:
        _ORIGINAL_APPOINTMENTS = get_appointments()

    else:
        save_appointments(list(_ORIGINAL_APPOINTMENTS))

    logger = logging.getLogger(__name__)
    logger.info("Data files reset to original state")