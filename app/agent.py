import re

from app.tools import (
    get_earliest_appointment,
    get_patient,
    get_doctors_by_specialty,
    book_patient_appointment,
)


def extract_patient_id(text):

    match = re.search(
        r"\bP\d+\b",
        text,
        re.IGNORECASE,
    )

    if match:
        return match.group(0).upper()

    return None


def extract_specialty(text):

    text = text.lower()

    specialties = {
        "cardiology": [
            "cardiology",
            "cardiologist",
            "cardiologists",
            "heart specialist",
            "heart specialists",
            "heart doctor",
            "heart doctors",
        ],
        "dermatology": [
            "dermatology",
            "dermatologist",
            "dermatologists",
            "skin specialist",
            "skin specialists",
            "skin doctor",
            "skin doctors",
        ],
        "neurology": [
            "neurology",
            "neurologist",
            "neurologists",
            "brain specialist",
            "brain specialists",
            "brain doctor",
        ],
        "orthopedics": [
            "orthopedics",
            "orthopedic",
            "orthopedist",
            "orthopedists",
            "orthopaedic",
            "bone specialist",
            "bone specialists",
            "bone doctor",
        ],
        "general medicine": [
            "general medicine",
            "general physician",
            "general doctor",
            "primary care",
        ],
    }

    for specialty, phrases in specialties.items():

        for phrase in phrases:

            if phrase in text:
                return specialty

    return None


def classify_request(user_request):

    text = user_request.lower().strip()

    # ==================================================
    # UNSAFE MEDICAL REQUESTS
    # ==================================================

    unsafe_phrases = [
        "diagnose me",
        "diagnosis",
        "what disease",
        "what disease do i have",
        "what condition do i have",
        "what is wrong with me",
        "what's wrong with me",
        "prescribe",
        "prescription",
        "medication",
        "medicine for",
        "what medicine",
        "what medication",
        "what pill",
        "what pills",
        "treatment for",
        "what treatment",
        "how should i treat",
        "how do i treat",
        "how can i treat",
        "cure my",
        "cure this",
    ]

    if any(
        phrase in text
        for phrase in unsafe_phrases
    ):
        return "unsafe_medical_request"

    # ==================================================
    # OUT-OF-SCOPE REQUESTS
    # ==================================================

    weather_phrases = [
        "weather",
        "temperature outside",
        "forecast",
        "rain today",
        "raining today",
        "is it raining",
        "will it rain",
    ]

    if any(
        phrase in text
        for phrase in weather_phrases
    ):
        return "out_of_scope"

    programming_phrases = [
        "write python",
        "write a python",
        "python function",
        "python code",
        "write code",
        "generate code",
        "programming",
        "debug my code",
        "fix my code",
        "javascript",
        "java code",
        "c++ code",
        "sort a list",
        "coding",
    ]

    if any(
        phrase in text
        for phrase in programming_phrases
    ):
        return "out_of_scope"

    joke_phrases = [
        "tell me a joke",
        "tell a joke",
        "make me laugh",
        "say something funny",
        "funny joke",
        "joke please",
    ]

    if any(
        phrase in text
        for phrase in joke_phrases
    ):
        return "out_of_scope"

    general_knowledge_phrases = [
        "capital of",
        "who is ",
        "who was ",
        "when was ",
        "where is ",
        "how old is ",
        "history of",
        "population of",
        "president of",
        "prime minister of",
    ]

    if any(
        phrase in text
        for phrase in general_knowledge_phrases
    ):
        return "out_of_scope"

    # ==================================================
    # PATIENT LOOKUP
    # ==================================================

    patient_id = extract_patient_id(
        user_request
    )

    if (
        patient_id
        and any(
            word in text
            for word in [
                "patient",
                "record",
                "medical record",
                "details",
                "information",
                "info",
                "look up",
                "find",
                "show",
            ]
        )
    ):
        return "patient_lookup"

    # ==================================================
    # APPOINTMENT BOOKING
    # ==================================================

    if (
        patient_id
        and any(
            word in text
            for word in [
                "book",
                "booking",
                "schedule",
                "reserve",
                "appointment",
            ]
        )
    ):
        return "appointment_booking"

    # ==================================================
    # APPOINTMENT LOOKUP
    # ==================================================

    specialty = extract_specialty(
        user_request
    )

    if (
        specialty
        and any(
            word in text
            for word in [
                "appointment",
                "available",
                "availability",
                "booking",
                "schedule",
                "slot",
                "see",
                "visit",
            ]
        )
    ):
        return "appointment_lookup"

    # ==================================================
    # DOCTOR LOOKUP
    # ==================================================

    if (
        specialty
        and any(
            word in text
            for word in [
                "doctor",
                "doctors",
                "specialist",
                "specialists",
            ]
        )
    ):
        return "doctor_lookup"

    # ==================================================
    # INCOMPLETE APPOINTMENT REQUEST
    # ==================================================

    if any(
        phrase in text
        for phrase in [
            "i need an appointment",
            "i need a doctor",
            "i need to see a doctor",
            "i want an appointment",
            "i want to see a doctor",
            "can i see a doctor",
            "can i book an appointment",
            "i want to book an appointment",
        ]
    ):
        return "incomplete_appointment"

    # ==================================================
    # GENERIC HELP / HEALTH
    # ==================================================

    if any(
        phrase in text
        for phrase in [
            "help me with my health",
            "help with my health",
            "health question",
            "health advice",
            "medical advice",
            "i have a health question",
        ]
    ):
        return "unsafe_medical_request"

    if text in [
        "help",
        "i need help",
        "can you help me",
        "help me",
    ]:
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

        return {
            "patient_id": patient_id
        }

    if tool_name == "get_earliest_appointment":

        specialty = extract_specialty(
            user_request
        )

        if not specialty:
            specialty = arguments.get(
                "specialty"
            )

        if not specialty:
            return None

        return {
            "specialty": specialty
        }

    if tool_name == "get_doctors_by_specialty":

        specialty = extract_specialty(
            user_request
        )

        if not specialty:
            specialty = arguments.get(
                "specialty"
            )

        if not specialty:
            return None

        return {
            "specialty": specialty
        }

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

    return None


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
                "error": (
                    "A valid patient ID is required."
                ),
            }

        return get_patient(
            normalized["patient_id"]
        )

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
                    "I need a medical specialty "
                    "to find an appointment."
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

    return {
        "success": False,
        "error": f"Unknown tool: {tool_name}",
    }