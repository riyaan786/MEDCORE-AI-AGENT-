import re

from app.tools import (
    get_earliest_appointment,
    get_patient,
    get_doctors_by_specialty,
    book_patient_appointment,
    get_patient_appointments,
    get_appointment,
    cancel_patient_appointment,
    reschedule_patient_appointment,
)


def extract_patient_id(text):
    match = re.search(r"\bP\d+\b", text, re.IGNORECASE)
    if match:
        return match.group(0).upper()
    return None


def extract_appointment_id(text):
    match = re.search(r"\bA\d+\b", text, re.IGNORECASE)
    if match:
        return match.group(0).upper()
    return None


def extract_specialty(text):
    text = text.lower()
    specialties = {
        "cardiology": [
            "cardiology", "cardiologist", "cardiologists",
            "heart specialist", "heart specialists",
            "heart doctor", "heart doctors",
        ],
        "dermatology": [
            "dermatology", "dermatologist", "dermatologists",
            "skin specialist", "skin specialists",
            "skin doctor", "skin doctors",
        ],
        "neurology": [
            "neurology", "neurologist", "neurologists",
            "brain specialist", "brain specialists",
            "brain doctor",
        ],
        "orthopedics": [
            "orthopedics", "orthopedic", "orthopedist",
            "orthopedists", "orthopaedic",
            "bone specialist", "bone specialists",
            "bone doctors",
        ],
        "general medicine": [
            "general medicine", "general physician",
            "general doctor", "primary care",
        ],
    }
    for specialty, phrases in specialties.items():
        for phrase in phrases:
            if phrase in text:
                return specialty
    return None


def extract_date(text):
    text = text.lower()
    match = re.search(r"\b(\d{4})-(\d{2})-(\d{2})\b", text)
    if match:
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    months = {
        "january": "01", "february": "02", "march": "03",
        "april": "04", "may": "05", "june": "06",
        "july": "07", "august": "08", "september": "09",
        "october": "10", "november": "11", "december": "12",
        "jan": "01", "feb": "02", "mar": "03", "apr": "04",
        "jun": "06", "jul": "07", "aug": "08",
        "sep": "09", "oct": "10", "nov": "11", "dec": "12",
    }
    month_pattern = "|".join(months.keys())
    match = re.search(
        r"\b(" + month_pattern + r")\s+(\d{1,2})\b", text
        )
    if match:
        month = months[match.group(1)]
        day = match.group(2).zfill(2)
        return f"2026-{month}-{day}"
    return None


def classify_request(user_request):

    text = user_request.lower().strip()

    unsafe_phrases = [
        "diagnose me", "diagnosis", "what disease",
        "what condition do i have",
        "what is wrong with me",
        "what's wrong with me",
        "prescribe", "prescription", "medication",
        "medicine for", "what medicine",
        "what medication", "what pill", "what pills",
        "treatment for", "what treatment",
        "how should i treat", "how do i treat",
        "how can i treat", "cure my", "cure this",
    ]

    if any(p in text for p in unsafe_phrases):
        return "unsafe_medical_request"

    weather_phrases = [
        "weather", "temperature outside", "forecast",
        "rain today", "raining today",
        "is it raining", "will it rain",
    ]

    if any(p in text for p in weather_phrases):
        return "out_of_scope"

    programming_phrases = [
        "write python", "write a python",
        "python function", "python code",
        "write code", "generate code",
        "programming", "debug my code",
        "fix my code", "javascript", "java code",
        "c++ code", "sort a list", "coding",
    ]

    if any(p in text for p in programming_phrases):
        return "out_of_scope"

    joke_phrases = [
        "tell me a joke", "tell a joke",
        "make me laugh", "say something funny",
        "funny joke", "joke please",
    ]

    if any(p in text for p in joke_phrases):
        return "out_of_scope"

    general_knowledge_phrases = [
        "capital of", "who is ", "who was ",
        "when was ", "where is ", "how old is ",
        "history of", "population of",
        "president of", "prime minister of",
    ]

    if any(p in text for p in general_knowledge_phrases):
        return "out_of_scope"

    patient_id = extract_patient_id(user_request)

    appointment_words = [
        "appointment", "book", "schedule",
        "cancel", "reschedule", "shift", "move",
    ]

    if patient_id and any(w in text for w in [
        "patient", "record", "medical record",
        "details", "information", "info",
        "find", "show",
    ]) and not any(w in text for w in appointment_words):
        return "patient_lookup"

    if (patient_id and any(w in text for w in [
        "book", "booking", "schedule",
        "reserve", "appointment",
    ]) and extract_specialty(user_request)):
        return "appointment_booking"

    specialty = extract_specialty(user_request)

    if specialty and any(w in text for w in [
        "appointment", "available", "availability",
        "booking", "schedule", "slot", "see", "visit",
    ]):
        return "appointment_lookup"

    if specialty and any(w in text for w in [
        "doctor", "doctors", "specialist",
        "specialists",
    ]):
        return "doctor_lookup"

    if any(p in text for p in [
        "i need an appointment", "i need a doctor",
        "i need to see a doctor",
        "i want an appointment",
        "i want to see a doctor", "can i see a doctor",
        "can i book an appointment",
        "i want to book an appointment",
    ]):
        return "incomplete_appointment"

    if patient_id and any(w in text for w in [
        "appointment", "appointments",
    ]):
        return "appointment_lookup_patient"

    if any(p in text for p in [
        "cancel", "can't make", "cant make",
        "can't attend", "cant attend",
    ]) and (patient_id or extract_appointment_id(user_request)):
        return "appointment_cancellation"

    if any(p in text for p in [
        "reschedule", "shift", "move",
        "change my appointment",
    ]) and (patient_id or extract_appointment_id(user_request)):
        return "appointment_rescheduling"

    if any(p in text for p in [
        "help me with my health",
        "help with my health",
        "health question", "health advice",
        "medical advice",
        "i have a health question",
    ]):
        return "unsafe_medical_request"

    if text in ["help", "i need help",
                "can you help me", "help me"]:
        return "out_of_scope"

    return "out_of_scope"
    return "out_of_scope"


def normalize_arguments(
    tool_name,
    arguments,
    user_request,
):

    if tool_name == "get_patient":

        patient_id = extract_patient_id(
            user_request
        )

        if not patient_id:
            return None

        return {"patient_id": patient_id}

    if tool_name == "get_earliest_appointment":

        specialty = extract_specialty(
            user_request
        )

        if not specialty:
            specialty = arguments.get("specialty")

        if not specialty:
            return None

        return {"specialty": specialty}

    if tool_name == "get_doctors_by_specialty":

        specialty = extract_specialty(
            user_request
        )

        if not specialty:
            specialty = arguments.get("specialty")

        if not specialty:
            return None

        return {"specialty": specialty}

    if tool_name == "book_patient_appointment":

        patient_id = extract_patient_id(
            user_request
        )

        appointment_id = arguments.get(
            "appointment_id"
        )

        if not patient_id:
            return None

        if not appointment_id:
            return None

        return {
            "appointment_id": appointment_id,
            "patient_id": patient_id,
        }

    if tool_name == "get_patient_appointments":

        patient_id = extract_patient_id(
            user_request
        )

        if not patient_id:
            patient_id = arguments.get(
                "patient_id"
            )

        if not patient_id:
            return None

        return {"patient_id": patient_id}

    if tool_name == "get_appointment":

        appointment_id = extract_appointment_id(
            user_request
        )

        if not appointment_id:
            appointment_id = arguments.get(
                "appointment_id"
            )

        if not appointment_id:
            return None

        return {"appointment_id": appointment_id}

    if tool_name == "cancel_patient_appointment":

        appointment_id = extract_appointment_id(
            user_request
        )

        if not appointment_id:
            appointment_id = arguments.get(
                "appointment_id"
            )

        patient_id = extract_patient_id(
            user_request
        )

        return {
            "appointment_id": appointment_id,
            "patient_id": patient_id,
        }

    if tool_name == "reschedule_patient_appointment":

        appointment_id = extract_appointment_id(
            user_request
        )

        if not appointment_id:
            appointment_id = arguments.get(
                "appointment_id"
            )

        if not appointment_id:
            return None

        new_date = arguments.get("new_date")

        if not new_date:
            new_date = extract_date(
                user_request
            )

        return {
            "appointment_id": appointment_id,
            "new_date": new_date,
        }



def execute_tool(
    tool_name,
    arguments,
    user_request,
):

    if tool_name == "get_patient":

        normalized = normalize_arguments(
            tool_name,
            arguments,
            user_request,
        )

        if normalized is None:
            return {
                "success": False,
                "error": "A valid patient ID is required.",
            }

        return get_patient(normalized["patient_id"])

    if tool_name == "get_earliest_appointment":

        normalized = normalize_arguments(
            tool_name,
            arguments,
            user_request,
        )

        if normalized is None:
            return {
                "success": False,
                "error": (
                    "I need a medical specialty to "
                    "find an appointment."
                ),
            }

        return get_earliest_appointment(
            normalized["specialty"]
        )

    if tool_name == "get_doctors_by_specialty":

        normalized = normalize_arguments(
            tool_name,
            arguments,
            user_request,
        )

        if normalized is None:
            return {
                "success": False,
                "error": (
                    "I need a medical specialty "
                    "to find doctors."
                ),
            }

        return get_doctors_by_specialty(
            normalized["specialty"]
        )

    if tool_name == "book_patient_appointment":

        normalized = normalize_arguments(
            tool_name,
            arguments,
            user_request,
        )

        if normalized is None:
            return {
                "success": False,
                "error": (
                    "A patient ID and appointment "
                    "ID are required."
                ),
            }

        return book_patient_appointment(
            normalized["appointment_id"],
            normalized["patient_id"],
        )

    if tool_name == "get_patient_appointments":

        normalized = normalize_arguments(
            tool_name,
            arguments,
            user_request,
        )

        if normalized is None:
            return {
                "success": False,
                "error": (
                    "A valid patient ID is "
                    "required."
                ),
            }

        return get_patient_appointments(
            normalized["patient_id"]
        )

    if tool_name == "get_appointment":

        normalized = normalize_arguments(
            tool_name,
            arguments,
            user_request,
        )

        if normalized is None:
            return {
                "success": False,
                "error": (
                    "A valid appointment ID is "
                    "required."
                ),
            }

        return get_appointment(
            normalized["appointment_id"]
        )

    if tool_name == "cancel_patient_appointment":

        normalized = normalize_arguments(
            tool_name,
            arguments,
            user_request,
        )

        if (
            normalized.get("appointment_id")
            is None
        ):
            return {
                "success": False,
                "error": (
                    "An appointment ID is required "
                    "to cancel."
                ),
            }

        return cancel_patient_appointment(
            normalized["appointment_id"],
            normalized.get("patient_id"),
        )

    if tool_name == "reschedule_patient_appointment":

        normalized = normalize_arguments(
            tool_name,
            arguments,
            user_request,
        )

        if normalized is None:
            return {
                "success": False,
                "error": (
                    "An appointment ID is required "
                    "to reschedule."
                ),
            }

        return reschedule_patient_appointment(
            normalized["appointment_id"],
            new_date=normalized.get("new_date"),
        )

    return {
        "success": False,
        "error": f"Unknown tool: {tool_name}",
    }
    return None