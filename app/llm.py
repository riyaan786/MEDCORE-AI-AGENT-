
import re
import requests

from app.rag import retrieve
from app.agent import (
    execute_tool,
    extract_patient_id,
    extract_appointment_id,
    extract_specialty,
    extract_date,
)
from app.hospital_data import get_doctor_by_id


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


# =============================================================
# APPOINTMENT ID
# ============================================================

def extract_appointment_id(text):

    match = re.search(
        r"\bA\d+\b",
        text,
        re.IGNORECASE,
    )

    if match:

        return match.group(0).upper()

    return None


# ============================================================
# DATE EXTRACTION
# ============================================================

def extract_date(text):

    text = text.lower()

    match = re.search(
        r"\b(\d{4})-(\d{2})-(\d{2})\b",
        text,
    )

    if match:

        return (
            f"{match.group(1)}"
            f"-{match.group(2)}"
            f"-{match.group(3)}"
        )

    months = {
        "january": "01", "february": "02",
        "march": "03", "april": "04",
        "may": "05", "june": "06",
        "july": "07", "august": "08",
        "september": "09", "october": "10",
        "november": "11", "december": "12",
        "jan": "01", "feb": "02", "mar": "03",
        "apr": "04", "jun": "06", "jul": "07",
        "aug": "08", "sep": "09", "oct": "10",
        "nov": "11", "dec": "12",
    }

    month_pattern = "|".join(months.keys())

    match = re.search(
        r"\b(" + month_pattern + r")\s+(\d{1,2})\b",
        text,
    )

    if match:

        month = months[match.group(1)]

        day = match.group(2).zfill(2)

        return f"2026-{month}-{day}"

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

    # Flexible pattern: "show me" + "doctor/specialist"
    if "show me" in text and (
        "doctor" in text or "specialist" in text
    ):
        return True

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
        "what does that mean",
        "what does this mean",
        "what does that mean for me",
        "what does this mean for me",
        "best pill",
        "best medication",
        "best medicine",
        "what is the best pill",
        "what's the best pill",
        "what is the best medication",
        "what's the best medication",
        "what is the best medicine",
        "what's the best medicine",
        "having chest pain",
        "having chest pains",
        "with chest pain",
        "bad headache",
        "severe headache",
        "terrible headache",
        "having a rash",
        "with a rash",
        "skin rash",
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
    # EXTRACT IDS FOR ROUTING
    # ========================================================

    patient_id = extract_patient_id(user_request)
    appointment_id = extract_appointment_id(user_request)

    # ========================================================
    # APPOINTMENT CANCELLATION
    # ========================================================

    if any(phrase in text for phrase in [
        "cancel", "can't make", "cant make",
        "can't attend", "cant attend",
        "need to cancel", "want to cancel",
    ]):
        if appointment_id:
            result = execute_tool("cancel_patient_appointment",
                {"appointment_id": appointment_id}, user_request)
            if not result.get("success"):
                return {"tool": "cancel_patient_appointment",
                    "success": False,
                    "response": result.get("error",
                        "Could not cancel the appointment.")}
            appt = result.get("appointment", {})
            return {"tool": "cancel_patient_appointment",
                "success": True,
                "response": f"I've cancelled your appointment "
                    f"{appointment_id} scheduled for "
                    f"{appt.get('date', '?')} at "
                    f"{appt.get('time', '?')}."}
        elif patient_id:
            ar = execute_tool("get_patient_appointments",
                {"patient_id": patient_id}, user_request)
            apps = ar.get("appointments", [])
            sched = [a for a in apps if a["status"] == "scheduled"]
            if not sched:
                return {"tool": None, "success": False,
                    "response": f"No scheduled appointments found for {patient_id}."}
            tgt = sched[0]
            result = execute_tool("cancel_patient_appointment",
                {"appointment_id": tgt["appointment_id"]}, user_request)
            if not result.get("success"):
                return {"tool": "cancel_patient_appointment",
                    "success": False,
                    "response": result.get("error", "Could not cancel.")}
            appt = result.get("appointment", {})
            return {"tool": "cancel_patient_appointment",
                "success": True,
                "response": f"I've cancelled appointment "
                    f"{tgt['appointment_id']} scheduled for "
                    f"{appt.get('date', '?')} at "
                    f"{appt.get('time', '?')}."}
        else:
            return {"tool": None, "success": False,
                "response": "I can help you cancel an appointment. "
                    "Please provide the appointment ID (e.g., A1001) "
                    "or patient ID (e.g., P1001)."}

    # ========================================================
    # APPOINTMENT RESCHEDULING
    # ========================================================

    if any(phrase in text for phrase in [
        "reschedule", "shift", "move",
        "change my appointment", "change appointment",
    ]):
        new_date = extract_date(user_request)
        if appointment_id:
            result = execute_tool("reschedule_patient_appointment",
                {"appointment_id": appointment_id, "new_date": new_date},
                user_request)
            if not result.get("success"):
                return {"tool": "reschedule_patient_appointment",
                    "success": False,
                    "response": result.get("error", "Could not reschedule.")}
            old = result.get("old_appointment", {})
            new = result.get("new_appointment", {})
            return {"tool": "reschedule_patient_appointment",
                "success": True,
                "response": f"I've rescheduled your appointment from "
                    f"{result.get('old_appointment_id', '?')} "
                    f"({old.get('date', '?')} at {old.get('time', '?')}) "
                    f"to {new.get('appointment_id', '?')} "
                    f"({new.get('date', '?')} at {new.get('time', '?')})."}
        elif patient_id:
            ar = execute_tool("get_patient_appointments",
                {"patient_id": patient_id}, user_request)
            apps = ar.get("appointments", [])
            sched = [a for a in apps if a["status"] == "scheduled"]
            if not sched:
                return {"tool": None, "success": False,
                    "response": f"No scheduled appointments found for {patient_id}."}
            tgt = sched[0]
            result = execute_tool("reschedule_patient_appointment",
                {"appointment_id": tgt["appointment_id"], "new_date": new_date},
                user_request)
            if not result.get("success"):
                return {"tool": "reschedule_patient_appointment",
                    "success": False,
                    "response": result.get("error", "Could not reschedule.")}
            old = result.get("old_appointment", {})
            new = result.get("new_appointment", {})
            return {"tool": "reschedule_patient_appointment",
                "success": True,
                "response": f"I've rescheduled your appointment from "
                    f"{result.get('old_appointment_id', '?')} "
                    f"({old.get('date', '?')} at {old.get('time', '?')}) "
                    f"to {new.get('appointment_id', '?')} "
                    f"({new.get('date', '?')} at {new.get('time', '?')})."}
        else:
            return {"tool": None, "success": False,
                "response": "I can help you reschedule. Please provide "
                    "the appointment ID (e.g., A1001) or patient ID (e.g., P1001)."}

    # ========================================================
    # APPOINTMENT LOOKUP BY PATIENT
    # ========================================================

    if patient_id and any(w in text for w in [
        "appointment", "appointments",
        "my appointment", "what appointment",
    ]) and not any(w in text for w in [
        "book", "booking", "schedule", "reserve",
    ]):
        result = execute_tool("get_patient_appointments",
            {"patient_id": patient_id}, user_request)
        if not result.get("success"):
            return {"tool": "get_patient_appointments",
                "success": False,
                "response": result.get("error", "Could not find appointments.")}
        apps = result.get("appointments", [])
        if not apps:
            return {"tool": "get_patient_appointments",
                "success": True,
                "response": f"No appointments found for {patient_id}."}
        strs = []
        for a in apps:
            doc = get_doctor_by_id(a.get("doctor_id"))
            dn = doc["name"] if doc else "Unknown"
            strs.append(f"{a['appointment_id']} on {a['date']} "
                f"at {a['time']} with {dn} ({a['status']})")
        return {"tool": "get_patient_appointments",
            "success": True,
            "response": f"Appointments for {patient_id}: " + "; ".join(strs)}

    # ========================================================
    # APPOINTMENT BOOKING
    # ========================================================

    if (patient_id and any(w in text for w in [
        "book", "booking", "schedule", "reserve",
        "want to schedule", "want to book",
    ]) and extract_specialty(user_request)):
        specialty = extract_specialty(user_request)
        fr = execute_tool("get_earliest_appointment",
            {"specialty": specialty}, user_request)
        if not fr.get("success"):
            return {"tool": "book_patient_appointment",
                "success": False,
                "response": fr.get("error", f"No available {specialty} appointments.")}
        slot = fr["appointment"]
        br = execute_tool("book_patient_appointment",
            {"appointment_id": slot["appointment_id"], "patient_id": patient_id},
            user_request)
        if not br.get("success"):
            return {"tool": "book_patient_appointment",
                "success": False,
                "response": br.get("error", "Could not book the appointment.")}
        booked = br["appointment"]
        doctor = get_doctor_by_id(booked.get("doctor_id"))
        dn = doctor["name"] if doctor else "Unknown"
        return {"tool": "book_patient_appointment",
            "success": True,
            "response": f"I've booked a {specialty} appointment "
                f"for {patient_id}. Appointment "
                f"{booked['appointment_id']} on {booked['date']} "
                f"at {booked['time']} with {dn}."}
    # ========================================================
    # 6. PATIENT LOOKUP
    # ========================================================

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
            "have",
        ]
    ) and not any(
        word in text
        for word in [
            "appointment",
            "appointments",
            "book",
            "schedule",
            "cancel",
            "reschedule",
            "shift",
            "move",
            "booking",
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

    # ========================================================
    # Booking request without patient ID
    # ========================================================

    if not patient_id and specialty and (
        re.search(r"\bbook\b", text)
        or "schedule" in text
    ):
        return {
            "tool": "book_patient_appointment",
            "success": False,
            "response": (
                "To book an appointment, I need a "
                "patient ID. Please provide the "
                "patient ID (e.g., P1001)."
            ),
        }

    if specialty and looks_like_appointment(
        user_request
    ) and "doctor" not in text and "specialist" not in text:

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

