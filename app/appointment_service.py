from app.hospital_data import (
    get_doctors,
    get_appointments,
)


def find_earliest_appointment(specialty):

    appointments = get_appointments()
    doctors = get_doctors()

    matching_doctor_ids = {
        doctor["doctor_id"]
        for doctor in doctors
        if doctor["specialty"].lower()
        == specialty.lower()
    }

    available = [
        appointment
        for appointment in appointments
        if appointment["doctor_id"]
        in matching_doctor_ids
        and appointment["status"] == "available"
    ]

    if not available:
        return None

    available.sort(
        key=lambda appointment: (
            appointment["date"],
            appointment["time"],
        )
    )

    return available[0]


def book_appointment(appointment_id, patient_id):

    appointments = get_appointments()

    for appointment in appointments:

        if appointment["appointment_id"] == appointment_id:

            if appointment["status"] != "available":
                return {
                    "success": False,
                    "error": "This appointment is no longer available.",
                }

            appointment["patient_id"] = patient_id
            appointment["status"] = "booked"

            return {
                "success": True,
                "appointment": appointment,
            }

    return {
        "success": False,
        "error": (
            f"Appointment {appointment_id} "
            "was not found."
        ),
    }