import json
from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data"


def load_json(filename):
    file_path = DATA_DIR / filename

    with open(file_path, "r") as file:
        return json.load(file)


def get_patients():
    return load_json("patients.json")


def get_doctors():
    return load_json("doctors.json")


def get_appointments():
    return load_json("appointments.json")