import logging

from app.hospital_data import (
    get_doctors,
    get_appointments,
    save_appointments,
    get_appointment_by_id,
    get_appointments_by_patient,
    get_doctor_by_id,
)


logger = logging.getLogger(__name__)


def find_earliest_appointment(specialty):

    available = find_available_appointments(
        specialty,
    )

    if not available:

        return None

    return available[0]


def find_available_appointments(
    specialty,
    exclude_id=None,
    after_date=None,
):

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
        and (
            exclude_id is None
            or appointment["appointment_id"]
            != exclude_id
        )
    ]

    if after_date:

        available = [
            appointment
            for appointment in available
            if appointment.get("date", "") >= after_date
        ]

    available.sort(
        key=lambda appointment: (
            appointment["date"],
            appointment["time"],
        )
    )

    return available


def find_appointment_by_id(appointment_id):

    return get_appointment_by_id(appointment_id)


def find_patient_appointments(patient_id):

    return get_appointments_by_patient(patient_id)


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
            appointment["status"] = "scheduled"

            save_appointments(appointments)

            logger.info(
                "Appointment %s booked for patient %s",
                appointment_id,
                patient_id,
            )

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


def cancel_appointment(appointment_id, patient_id=None):

    appointments = get_appointments()

    for appointment in appointments:

        if appointment["appointment_id"] == appointment_id:

            if patient_id and appointment.get("patient_id") != patient_id:
                return {
                    "success": False,
                    "error": (
                        "This appointment does not "
                        "belong to the specified "
                        "patient."
                    ),
                }

            if appointment["status"] == "cancelled":

                return {
                    "success": False,
                    "error": "This appointment is already cancelled.",
                }

            previous_status = appointment["status"]

            appointment["status"] = "cancelled"

            if patient_id:
                appointment["patient_id"] = None

            save_appointments(appointments)

            logger.info(
                "Appointment %s cancelled "
                "(was %s)",
                appointment_id,
                previous_status,
            )

            return {
                "success": True,
                "appointment": appointment,
                "previous_status": previous_status,
            }

    return {
        "success": False,
        "error": (
            f"Appointment {appointment_id} "
            "was not found."
        ),
    }


def reschedule_appointment(appointment_id, new_date=None):

    old_appointment = get_appointment_by_id(appointment_id)

    if old_appointment is None:

        return {
            "success": False,
            "error": (
                f"Appointment {appointment_id} "
                "was not found."
            ),
        }

    if old_appointment.get("status") != "scheduled":
        return {
            "success": False,
            "error": (
                "Only scheduled appointments can be "
                "rescheduled."
            ),
        }

    patient_id = old_appointment.get("patient_id")

    doctor = get_doctor_by_id(
        old_appointment["doctor_id"]
    )

    if doctor is None:

        return {
            "success": False,
            "error": "Doctor not found.",
        }

    specialty = doctor["specialty"]

    cancel_result = cancel_appointment(
        appointment_id,
        patient_id,
    )

    if not cancel_result.get("success"):

        return cancel_result

    available = find_available_appointments(
        specialty,
        exclude_id=appointment_id,
        after_date=new_date,
    )

    if not available:

        logger.warning(
            "No available appointments in %s after "
            "%s to reschedule to",
            specialty,
            new_date,
        )

        return {
            "success": False,
            "error": (
                "No available appointments were found "
                "to reschedule to."
            ),
            "cancelled_appointment_id": appointment_id,
        }

    new_appointment = available[0]

    book_result = book_appointment(
        new_appointment["appointment_id"],
        patient_id,
    )

    if not book_result.get("success"):

        return book_result

    logger.info(
        "Appointment %s rescheduled to %s",
        appointment_id,
        new_appointment["appointment_id"],
    )

    return {
        "success": True,
        "old_appointment_id": appointment_id,
        "old_appointment": old_appointment,
        "new_appointment": book_result["appointment"],
        "specialty": specialty,
    }