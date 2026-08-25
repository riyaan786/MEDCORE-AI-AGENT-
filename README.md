# MEDCORE AI Agent

A production-oriented AI hospital operations agent built around a **small local LLaMA model**.

MEDCORE AI demonstrates how a relatively small language model can be turned into a reliable domain-specific AI agent through strong engineering: tool routing, deterministic business logic, validation, RAG, safety boundaries, stateful workflows, persistence, and systematic evaluation.

The project is designed with an **FDE (Forward Deployed Engineer) mindset**: understand the customer's operational requirements, translate them into reliable AI workflows, integrate the right tools and data, test real-world failure cases, and build a system that can actually be deployed and maintained.

---

## Why MEDCORE AI?

Large language models are powerful, but an LLM alone is not a reliable hospital operations system.

MEDCORE AI separates **language understanding** from **business-critical execution**.

The model determines what the user is trying to accomplish, while deterministic application code handles the actual hospital operations.

This architecture makes the system more predictable, testable, and maintainable.

A key goal of this project was to demonstrate that **good agent engineering can make a small local model surprisingly capable**.

---

## Architecture

```text
User
  │
  ▼
FastAPI API
  │
  ▼
AI Agent / Request Router
  │
  ├── Patient Operations
  │     └── get_patient
  │
  ├── Doctor Operations
  │     └── get_doctors_by_specialty
  │
  ├── Appointment Operations
  │     ├── Find earliest appointment
  │     ├── Find appointments
  │     ├── Book appointment
  │     ├── Cancel appointment
  │     └── Reschedule appointment
  │
  ├── RAG
  │     └── Hospital knowledge / policies
  │
  └── Safety / Scope Validation
          │
          ▼
    Hospital Data Layer
          │
          ▼
      JSON Persistence
```

The LLM is not trusted to directly modify hospital data.

Instead:

```text
Natural language
      ↓
Intent / argument extraction
      ↓
Validated tool call
      ↓
Deterministic business logic
      ↓
Persistent hospital data
      ↓
Structured response
```

---

## Core Capabilities

### Patient Operations

* Look up patients by patient ID
* Validate unknown patient IDs
* Return structured patient information
* Retrieve appointments belonging to a patient

Example:

```text
"Look up patient P1001."
```

Result:

```text
Patient P1001: Arjun Mehta.
Date of birth: 1985-04-12.
Phone: 555-0101.
```

---

### Doctor & Specialty Operations

The agent can identify doctors by medical specialty.

Example:

```text
"Who are the cardiologists?"
```

The system routes the request to:

```text
get_doctors_by_specialty
```

It can also handle flexible wording such as:

```text
"Show me available cardiology doctors."
"Who are the dermatologists?"
"Can you show me the heart specialists?"
```

---

### Appointment Availability

The agent can find the earliest available appointment for a specialty.

Example:

```text
"I want to see a heart specialist as soon as possible."
```

The system identifies cardiology as the required specialty and calls:

```text
get_earliest_appointment
```

Example response:

```text
The earliest available cardiology appointment is on
2026-08-26 at 10:30.
Appointment ID: A1003.
```

---

### Appointment Booking

The system supports booking appointments for patients while validating the required information.

Example:

```text
"Book a cardiology appointment for patient P1003."
```

The agent can:

1. Identify the requested specialty.
2. Identify the patient.
3. Find an appropriate available appointment.
4. Validate the patient.
5. Book the appointment.
6. Persist the updated state.

---

### Appointment Lookup

Users can retrieve appointments associated with a patient.

Example:

```text
"Show me appointments for patient P1002."
```

---

### Appointment Cancellation

The system supports cancellation using appointment or patient information.

Example:

```text
"I need to cancel appointment A1003."
```

The operation is handled by deterministic application logic rather than allowing the LLM to modify data directly.

---

### Appointment Rescheduling

Appointments can also be rescheduled.

Example:

```text
"I need to reschedule appointment A1001 to 2026-08-28."
```

The agent extracts and validates the appointment ID and requested date before modifying the appointment.

---

## RAG

MEDCORE AI includes a retrieval-augmented generation layer for hospital knowledge.

The purpose of RAG is to allow the agent to answer questions using **provided hospital knowledge and policies** rather than relying entirely on the model's internal knowledge.

This creates a separation between:

```text
General language reasoning
        +
Hospital-specific knowledge
        ↓
Grounded response
```

This approach is important for enterprise AI systems where responses need to be grounded in customer-provided information.

---

## Safety & Scope Control

The agent is intentionally restricted to hospital operations.

It does **not** attempt to diagnose patients, prescribe medication, or provide treatment recommendations.

Examples that are rejected:

```text
"I have chest pain. Diagnose me."

"What medicine should I take for my headache?"

"What treatment should I use for my infection?"

"What disease do I have?"
```

The system also rejects unrelated requests such as:

```text
"What's the weather today?"

"What's the capital of India?"

"Tell me a joke."

"Write a Python function."
```

This demonstrates an important production-agent principle:

> An agent should not simply answer every question it receives. It should understand its operational boundaries and fail safely outside them.

---

## Flexible Request Handling

The system is designed to handle different ways of expressing the same intent.

For example:

```text
"Look up patient P1001."

"Show me the record for patient P1001."

"What is the medical record info for P1001?"
```

All can resolve to:

```text
get_patient
```

Similarly:

```text
"Find the earliest cardiology appointment."

"What is the next available cardiology slot?"

"I want to see a heart specialist as soon as possible."
```

can resolve to the appointment workflow.

This is important in real deployments because customers do not communicate using a fixed set of predefined commands.

---

## Stateful Operations

Appointment workflows modify application state.

The project therefore includes persistence and state management for operations such as:

* Booking
* Cancellation
* Rescheduling
* Appointment lookup

The system also provides data reset functionality so evaluations can run against a known initial state.

This allows repeatable testing of stateful agent behavior.

---

## Evaluation

The project includes a dedicated evaluation suite covering:

* Patient lookup
* Unknown patients
* Appointment availability
* Doctor lookup
* Appointment booking
* Appointment cancellation
* Appointment rescheduling
* Patient appointment lookup
* Flexible phrasing
* Missing information
* Invalid IDs
* Unavailable specialties
* Medical safety boundaries
* Out-of-scope requests
* Malformed inputs
* Stateful workflows

Current evaluation result:

```text
PASSED: 45/45
ACCURACY: 100.0%
```

The evaluation suite is designed to test more than whether the model produces a reasonable sentence.

It checks whether the agent:

1. Identifies the correct intent.
2. Selects the correct tool.
3. Extracts the correct arguments.
4. Executes the correct business operation.
5. Handles failure conditions.
---

## FDE Engineering Focus

This project is intentionally built around the responsibilities of an **FDE / AI Engineer working directly with customers**.

The focus is not simply:

> "Build a chatbot."

Instead, the project demonstrates the engineering process of turning customer requirements into a working AI system.

### Customer requirement

> Hospital staff need an AI assistant that can find patients, identify doctors, manage appointments, and answer hospital-specific questions while avoiding unsafe medical advice.

### Engineering translation

```text
Customer requirement
        ↓
Identify workflows
        ↓
Define tools
        ↓
Define data contracts
        ↓
Build routing
        ↓
Implement deterministic business logic
        ↓
Add RAG
        ↓
Add safety boundaries
        ↓
Add persistence
        ↓
Create evaluations
        ↓
Test failure cases
        ↓
Iterate until reliable
```

This project emphasizes the FDE principle that **successful AI deployments require much more than the underlying model**.

---

## Why Use a Small Local Model?

MEDCORE AI intentionally uses a relatively small local LLaMA model rather than depending on a large cloud model.

The goal is to demonstrate that system quality can come from the engineering surrounding the model.

The project focuses on:

* Constrained domain
* Explicit tools
* Deterministic business logic
* Argument normalization
* Validation
* RAG
* Safety filtering
* Stateful workflows
* Evaluation-driven development

This makes the project particularly useful as an example of **agent engineering rather than model-size engineering**.

---

## Project Structure

```text
MEDCORE-AI-AGENT/
│
├── app/
│   ├── agent.py
│   ├── api.py
│   ├── appointment_service.py
│   ├── eval_runner.py
│   ├── evaluation_cases.py
│   ├── evals.py
│   ├── hospital_data.py
│   ├── llm.py
│   ├── main.py
│   ├── rag.py
│   ├── terminal.py
│   └── tools.py
│
├── data/
│   ├── appointments.json
│   ├── doctors.json
│   ├── patients.json
│   ├── hospital_policies.txt
│   └── hospital_knowledge/
│       └── hospital_faq.md
│
├── docs/
│   └── customer_requirements.md
│
├── requirements.txt
├── logging.toml
├── .gitignore
└── README.md
```

---

## Running the Project

Clone the repository:

```bash
git clone https://github.com/riyaan786/MEDCORE-AI-AGENT-.git
cd MEDCORE-AI-AGENT-
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the evaluation suite:

```bash
python -m app.eval_runner
```

Expected result:

```text
PASSED: 45/45
ACCURACY: 100.0%
```

### Running the API server

```bash
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
```

### Running the terminal interface

```bash
python -m app.terminal
```

---

## API

The project exposes a FastAPI interface.

Health check:

```text
GET /health
```

Chat endpoint:

```text
POST /chat
```

Example request:

```json
{
  "message": "Look up patient P1001."
}
```

Example response:

```json
{
  "success": true,
  "tool": "get_patient",
  "response": "Patient P1001: Arjun Mehta. Date of birth: 1985-04-12. Phone: 555-0101."
}
```

---

## Design Principles

### 1. LLMs interpret; tools execute

The model should not directly manipulate critical application state.

### 2. Fail safely

Unknown patients, unavailable appointments, missing arguments, unsupported requests, and unsafe medical requests should produce controlled failures.

### 3. Evaluate continuously

Agent quality should be measured through repeatable test cases rather than subjective demos.

### 4. Separate customer knowledge from model knowledge

Hospital-specific information belongs in the application's knowledge layer.

### 5. Build for real users

Users will phrase requests differently, omit information, make mistakes, and ask unsupported questions.

The system must handle those situations deliberately.

---

## Status

**Core agent implementation: Complete**

**Evaluation: 45/45 — 100%**

**Focus: AI Agent Engineering / FDE Engineering**

This repository is intended as a portfolio and engineering demonstration of building, integrating, testing, and evaluating an AI agent around a real operational workflow.
