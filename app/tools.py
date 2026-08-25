from app.appointment_service import (
    find_earliest_appointment,
    book_appointment,
    find_patient_appointments,
    find_appointment_by_id,
    cancel_appointment,
    reschedule_appointment,
)

from app.hospital_data import (
    get_patients,
    get_doctors,
)


def get_patient(patient_id):

    patients = get_patients()

    for patient in patients:

        if patient["patient_id"] == patient_id:

            return {
                "success": True,
                "patient": patient,
            }

    return {
        "success": False,
        "error": f"Patient {patient_id} was not found.",
    }


def get_earliest_appointment(specialty):

    appointment = find_earliest_appointment(
        specialty
    )

    if appointment is None:

        return {
            "success": False,
            "error": (
                f"No available {specialty} "
                "appointments found."
            ),
        }

    return {
        "success": True,
        "specialty": specialty,
        "appointment": appointment,
    }


def get_doctors_by_specialty(specialty):

    doctors = get_doctors()

    matches = [
        doctor
        for doctor in doctors
        if doctor["specialty"].lower()
        == specialty.lower()
    ]

    if not matches:

        return {
            "success": False,
            "error": (
                f"No doctors found for {specialty}."
            ),
        }

    return {
        "success": True,
        "specialty": specialty,
        "doctors": matches,
    }


def get_patient_appointments(patient_id):

    patients = get_patients()

    patient_exists = any(
        patient["patient_id"] == patient_id
        for patient in patients
    )

    if not patient_exists:

        return {
            "success": False,
            "error": (
                f"Patient {patient_id} "
                "was not found."
            ),
        }

    appointments = find_patient_appointments(
        patient_id
    )

    return {
        "success": True,
        "patient_id": patient_id,
        "appointments": appointments,
    }


def get_appointment(appointment_id):

    appointment = find_appointment_by_id(
        appointment_id
    )

    if appointment is None:

        return {
            "success": False,
            "error": (
                f"Appointment {appointment_id} "
                "was not found."
            ),
        }

    return {
        "success": True,
        "appointment": appointment,
    }


def book_patient_appointment(
    appointment_id,
    patient_id,
):

    patients = get_patients()

    patient_exists = any(
        patient["patient_id"] == patient_id
        for patient in patients
    )

    if not patient_exists:

        return {
            "success": False,
            "error": (
                f"Patient {patient_id} "
                "was not found."
            ),
        }

    return book_appointment(
        appointment_id,
        patient_id,
    )


def cancel_patient_appointment(
    appointment_id,
    patient_id=None,
):

    patients = get_patients()

    patient_exists = any(
        patient["patient_id"] == patient_id
        for patient in patients
    ) if patient_id else True

    if patient_id and not patient_exists:

        return {
            "success": False,
            "error": (
                f"Patient {patient_id} "
                "was not found."
            ),
        }

    return cancel_appointment(
        appointment_id,
        patient_id,
    )


def reschedule_patient_appointment(
    appointment_id,
    new_date=None,
):

    return reschedule_appointment(
        appointment_id,
        new_date=new_date,
    )