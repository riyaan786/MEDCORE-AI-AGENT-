
import re
import requests

from app.rag import retrieve
from app.agent import execute_tool


OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:1b"


# ============================================================
# SPECIALTY DETECTION
# ============================================================

def detect_specialty(text):

    text = text.lower()

    specialties = {
        "cardiology": [
            "cardiology",
            "cardiologist",
            "cardiologists",
            "heart specialist",
            "heart doctor",
            "heart specialist doctor",
        ],
        "dermatology": [
            "dermatology",
            "dermatologist",
            "dermatologists",
            "skin specialist",
            "skin doctor",
        ],
        "neurology": [
            "neurology",
            "neurologist",
            "neurologists",
            "brain specialist",
            "brain doctor",
        ],
        "orthopedics": [
            "orthopedics",
            "orthopedic",
            "orthopaedic",
            "orthopedist",
            "orthopedic doctor",
            "bone specialist",
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


# ============================================================
# APPOINTMENT DETECTION
# ============================================================

def looks_like_appointment(text):

    text = text.lower()

    appointment_phrases = [
        "appointment",
        "appointments",
        "book",
        "booking",
        "bookings",
        "schedule",
        "scheduling",
        "available",
        "availability",
        "slot",
        "slots",
        "earliest",
        "next available",
        "as soon as possible",
        "soon as possible",
        "need to see",
        "want to see",
        "would like to see",
        "can i see",
        "find me a doctor",
        "see a doctor",
        "see a specialist",
    ]

    return any(
        phrase in text
        for phrase in appointment_phrases
    )


# ============================================================
# PATIENT ID
# ============================================================

def extract_patient_id(text):

    match = re.search(
        r"\bP\d+\b",
        text,
        re.IGNORECASE,
    )

    if match:
        return match.group(0).upper()

    return None


# ============================================================
# DOCTOR LOOKUP DETECTION
# ============================================================

def looks_like_doctor_lookup(text):

    text = text.lower()

    doctor_phrases = [
        "who are the",
        "who is the",
        "which doctors",
        "which doctor",
        "show me the doctors",
        "show me doctors",
        "show doctors",
        "list the doctors",
        "list doctors",
        "doctors in",
        "doctors for",
        "specialists in",
        "specialists for",
        "show me the specialists",
        "show me specialists",
        "list the specialists",
        "list specialists",
        "who are the doctors",
        "who are the specialists",
    ]

    return any(
        phrase in text
        for phrase in doctor_phrases
    )


# ============================================================
# OLLAMA
# ============================================================

def ask_llama(messages, json_mode=False):

    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0
        },
    }

    if json_mode:
        payload["format"] = "json"

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=60,
    )

    response.raise_for_status()

    data = response.json()

    return data["message"]["content"].strip()


# ============================================================
# MAIN AGENT
# ============================================================

def run_agent(user_request):

    text = user_request.lower()

    # ========================================================
    # 1. MEDICAL SAFETY
    # ========================================================

    unsafe_phrases = [
        "diagnose me",
        "diagnose my",
        "can you diagnose",
        "please diagnose",
        "give me a diagnosis",
        "what is my diagnosis",
        "what's my diagnosis",
        "what disease do i have",
        "what disease do i",
        "what condition do i have",
        "what condition is this",
        "what do i have",
        "do i have cancer",
        "do i have covid",
        "do i have an infection",
        "is this cancer",
        "is this an infection",
        "what illness do i have",
        "what illness is this",
        "tell me what's wrong with me",
        "tell me what is wrong with me",
        "figure out what's wrong",
        "figure out what is wrong",
        "identify my disease",
        "identify my condition",
        "identify the disease",
        "identify the condition",
        "prescribe",
        "prescription",
        "write me a prescription",
        "give me a prescription",
        "prescribe me",
        "what should i take",
        "what can i take",
        "what medicine should i take",
        "what medication should i take",
        "which medicine should i take",
        "which medication should i take",
        "medicine for",
        "medication for",
        "what drug should i take",
        "which drug should i take",
        "should i take antibiotics",
        "do i need antibiotics",
        "what antibiotics should i take",
        "what painkiller should i take",
        "what dosage should i take",
        "how much medicine should i take",
        "how many pills should i take",
        "how often should i take",
        "what dose should i take",
        "change my medication",
        "stop taking my medication",
        "start taking medication",
        "treatment for",
        "what treatment should i use",
        "what treatment do i need",
        "how should i treat",
        "how do i treat",
        "how can i treat",
        "treat my condition",
        "treat my disease",
        "treat my infection",
        "cure my condition",
        "cure my disease",
        "how do i cure",
        "how can i cure",
        "home treatment",
        "home remedy for",
        "remedy for",
        "what should i do for my symptoms",
        "what should i do about my symptoms",
        "how serious are my symptoms",
        "are my symptoms serious",
        "what do my symptoms mean",
        "what are these symptoms",
        "is this symptom",
        "is this normal medically",
        "should i be worried about this symptom",
        "what's causing my symptoms",
        "what is causing my symptoms",
        "why am i having these symptoms",
        "why do i have these symptoms",
        "can you interpret my symptoms",
        "interpret my symptoms",
        "analyze my symptoms",
        "analyze my medical condition",
        "analyze my test results",
        "interpret my test results",
        "what do my test results mean",
        "read my lab results",
        "interpret my lab results",
        "what does my blood test mean",
        "what does my scan mean",
        "interpret my xray",
        "interpret my x-ray",
        "read my xray",
        "read my x-ray",
        "what does my mri mean",
        "interpret my mri",
        "what does my ct scan mean",
        "interpret my ct scan",
        "what does my ultrasound mean",
        "interpret my ultrasound",
        "medical advice",
        "health advice",
        "medical recommendation",
        "health recommendation",
        "recommend a treatment",
        "recommend medication",
        "recommend medicine",
        "recommend a drug",
        "should i see a doctor for this symptom",
    ]

    if any(
        phrase in text
        for phrase in unsafe_phrases
    ):

        return {
            "tool": None,
            "success": False,
            "response": (
                "I can't provide medical diagnosis, "
                "prescriptions, or treatment advice."
            ),
        }

    # ========================================================
    # 2. PATIENT LOOKUP
    # ========================================================

    patient_id = extract_patient_id(
        user_request
    )

    if patient_id and any(
        word in text
        for word in [
            "patient",
            "record",
            "medical record",
            "details",
            "information",
            "info",
            "profile",
            "file",
        ]
    ):

        result = execute_tool(
            "get_patient",
            {
                "patient_id": patient_id
            },
            user_request,
        )

        if not result.get("success"):

            return {
                "tool": "get_patient",
                "success": False,
                "response": result.get(
                    "error",
                    "The patient could not be found.",
                ),
            }

        patient = result["patient"]

        return {
            "tool": "get_patient",
            "success": True,
            "response": (
                f"Patient {patient['patient_id']}: "
                f"{patient['name']}. "
                f"Date of birth: "
                f"{patient['date_of_birth']}. "
                f"Phone: "
                f"{patient['phone']}."
            ),
        }

    # ========================================================
    # 3. APPOINTMENT LOOKUP
    #
    # IMPORTANT:
    # THIS MUST COME BEFORE DOCTOR LOOKUP.
    #
    # Otherwise:
    # "Find the earliest cardiology appointment"
    # can accidentally be interpreted as a doctor lookup.
    # ========================================================

    specialty = detect_specialty(
        user_request
    )

    if specialty and looks_like_appointment(
        user_request
    ):

        result = execute_tool(
            "get_earliest_appointment",
            {
                "specialty": specialty
            },
            user_request,
        )

        if not result.get("success"):

            return {
                "tool": "get_earliest_appointment",
                "success": False,
                "response": result.get(
                    "error",
                    "No appointment could be found.",
                ),
            }

        appointment = result["appointment"]

        return {
            "tool": "get_earliest_appointment",
            "success": True,
            "response": (
                "The earliest available "
                f"{specialty} appointment is on "
                f"{appointment['date']} at "
                f"{appointment['time']}. "
                f"Appointment ID: "
                f"{appointment['appointment_id']}."
            ),
        }

    # ========================================================
    # 4. DOCTOR / SPECIALIST LOOKUP
    # ========================================================

    if specialty and looks_like_doctor_lookup(
        user_request
    ):

        result = execute_tool(
            "get_doctors_by_specialty",
            {
                "specialty": specialty
            },
            user_request,
        )

        if not result.get("success"):

            return {
                "tool": "get_doctors_by_specialty",
                "success": False,
                "response": result.get(
                    "error",
                    f"No doctors found for {specialty}.",
                ),
            }

        doctors = result.get(
            "doctors",
            []
        )

        if not doctors:

            return {
                "tool": "get_doctors_by_specialty",
                "success": False,
                "response": (
                    f"No doctors found for {specialty}."
                ),
            }

        doctor_names = []

        for doctor in doctors:

            doctor_names.append(
                f"{doctor['name']} "
                f"(Doctor ID: {doctor['doctor_id']})"
            )

        return {
            "tool": "get_doctors_by_specialty",
            "success": True,
            "response": (
                f"Available {specialty} doctors: "
                + ", ".join(doctor_names)
            ),
        }

    # ========================================================
    # 5. INCOMPLETE APPOINTMENT
    # ========================================================

    if any(
        phrase in text
        for phrase in [
            "i need an appointment",
            "i need a doctor",
            "i want an appointment",
            "i want to book an appointment",
            "i would like an appointment",
            "i'd like an appointment",
            "book me an appointment",
            "schedule me an appointment",
            "i want to see a doctor",
            "i need to see a doctor",
            "i would like to see a doctor",
            "i'd like to see a doctor",
            "can i see a doctor",
        ]
    ):

        return {
            "tool": None,
            "success": False,
            "response": (
                "Sure. Which medical specialty "
                "do you need an appointment for?"
            ),
        }

    # ========================================================
    # 6. OUT OF SCOPE
    # ========================================================

    out_of_scope_phrases = [
        "weather",
        "capital of",
        "tell me a joke",
        "make me laugh",
        "programming",
        "python",
        "write code",
        "code for",
        "sort a list",
        "javascript",
        "java code",
        "recipe",
        "football",
        "soccer",
        "cricket",
        "movie",
        "music",
        "song",
        "politics",
        "president",
        "stock price",
        "bitcoin",
        "news",
        "travel",
        "can you help me with my health",
"help me with my health",
"health question",
"health-related question",
"health related question",
        "hotel",
    ]

    if any(
        phrase in text
        for phrase in out_of_scope_phrases
    ):

        return {
            "tool": None,
            "success": False,
            "response": (
                "This request is outside the scope "
                "of the hospital operations assistant."
            ),
        }

    # ========================================================
    # 7. RAG INFORMATION
    # ========================================================

    documents = retrieve(
        user_request,
        top_k=3,
    )

    context = ""

    for document in documents:

        context += (
            f"\nSOURCE: {document['source']}\n"
            f"{document['text']}\n"
        )

    if context:

        answer_prompt = f"""
Answer the user's question using ONLY the hospital
knowledge below.

User:
{user_request}

Hospital knowledge:
{context}

Rules:

- Do not invent information.
- Do not diagnose.
- Do not prescribe medication.
- Do not provide treatment recommendations.
- Stay within hospital operations.
- If the knowledge does not contain the answer,
  say that the information is not available.
- Give a concise natural-language answer.
"""

        answer = ask_llama(
            [
                {
                    "role": "system",
                    "content": (
                        "You are MedCore AI, a hospital "
                        "operations assistant. "
                        "You only answer questions related "
                        "to hospital operations and the "
                        "provided hospital knowledge."
                    ),
                },
                {
                    "role": "user",
                    "content": answer_prompt,
                },
            ]
        )

        return {
            "tool": None,
            "success": True,
            "response": answer,
        }

    # ========================================================
    # 8. FINAL FALLBACK
    # ========================================================

    return {
        "tool": None,
        "success": False,
        "response": (
            "This request is outside the scope "
            "of the hospital operations assistant."
        ),
    }

