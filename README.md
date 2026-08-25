# MEDCORE AI — Hospital Operations AI Agent

A production-oriented AI agent for hospital operations, built with a strong **FDE (Forward Deployed Engineer) mindset**.

MEDCORE AI is designed around a simple principle:

> **Understand the customer's operational problem first, then engineer the AI system around it.**

Instead of building a generic chatbot, this project focuses on practical hospital workflows such as patient lookup, doctor discovery, appointment availability, booking, cancellation, rescheduling, appointment history, RAG-based hospital knowledge, safety handling, evaluation, and stateful data operations.

---

## Why This Project

The goal of MEDCORE AI is not to demonstrate that an LLM can generate text.

The goal is to demonstrate that an AI system can:

* Understand real user requests
* Determine whether a request is inside the system's scope
* Route requests to the correct tool
* Extract and normalize structured information
* Execute deterministic backend operations
* Maintain state when operations modify data
* Handle invalid and incomplete requests
* Refuse unsafe medical requests
* Retrieve information from hospital knowledge sources
* Be evaluated systematically rather than judged only by conversation quality
* Be debugged and improved using measurable evaluation results

This reflects the type of engineering required when deploying AI systems for real customers.

---

## Core Architecture

```text
User Request
     │
     ▼
   LLM
     │
     ▼
Request Classification
     │
     ├── Patient Operations
     │
     ├── Doctor Discovery
     │
     ├── Appointment Operations
     │
     ├── Hospital Knowledge / RAG
     │
     ├── Safety Handling
     │
     └── Out-of-Scope Handling
     │
     ▼
Tool Selection + Argument Extraction
     │
     ▼
Deterministic Python Tools
     │
     ▼
Hospital Data Layer
     │
     ├── Patients
     ├── Doctors
     └── Appointments
     │
     ▼
Structured Response
```

The LLM is used for understanding and routing, while important business operations are handled by deterministic Python code.

---

## AI Model

MEDCORE AI intentionally uses a **small local LLaMA-family model** rather than relying on a large hosted proprietary model.

This was an engineering constraint.

The objective was to demonstrate that good system architecture, routing, tool design, evaluation, safety controls, and deterministic backend logic can make a relatively small model significantly more useful.

The project therefore focuses on **engineering quality around the model**, rather than simply increasing model size.

---

## Features

### Patient Operations

* Patient lookup by patient ID
* Patient validation
* Handling unknown patients
* Structured patient information retrieval

Example:

```text
"Look up patient P1001."
```

---

### Doctor Discovery

The agent can identify available doctors by specialty.

Example:

```text
"Show me available cardiology doctors."
```

The system returns matching doctors and their IDs rather than treating every appointment request as an appointment lookup.

---

### Appointment Availability

The agent can find the earliest available appointment for a specialty.

Example:

```text
"Find the earliest cardiology appointment."
```

---

### Appointment Booking

The system supports booking appointments for patients while validating:

* Patient existence
* Specialty availability
* Appointment availability
* Booking state

Example:

```text
"Book a cardiology appointment for patient P1003."
```

---

### Appointment Lookup

The system can retrieve appointments associated with a patient.

Example:

```text
"Show me appointments for patient P1002."
```

---

### Appointment Cancellation

Appointments can be cancelled using appointment information or patient context.

Example:

```text
"I need to cancel appointment A1003."
```

---

### Appointment Rescheduling

Appointments can be moved to another date while preserving system state.

Example:

```text
"I need to reschedule appointment A1001 to 2026-08-28."
```

---

### Stateful Operations

Appointment booking, cancellation, and rescheduling modify persistent application state.

This allows the system to demonstrate that it is not simply producing simulated responses.

---

## Flexible Request Handling

The system supports multiple ways of expressing similar requests.

For example:

```text
"Find the earliest cardiology appointment."

"What is the next available cardiology slot?"

"Show me an available cardiology appointment."
```

These can be normalized into the appropriate backend operation.

This is important for real deployments because customers do not interact with software using one perfectly defined sentence structure.

---

## RAG

MEDCORE AI includes a Retrieval-Augmented Generation component for hospital knowledge.

Hospital knowledge can be stored in:

```text
data/hospital_knowledge/
```

The RAG layer allows the agent to retrieve relevant hospital information instead of relying entirely on model memory.

This architecture can be extended to include:

* Hospital policies
* FAQs
* Operational procedures
* Scheduling policies
* Department information
* Internal documentation

---

## Safety

The system explicitly handles medical requests that are outside the intended operational scope.

For example:

```text
"I have chest pain. Diagnose me."

"What medicine should I take for my headache?"

"What treatment should I use for my infection?"
```

The system does not attempt to diagnose patients or prescribe treatment.

This is treated as an **engineering and evaluation requirement**, not merely a prompt instruction.

Indirect variations are also tested to reduce simple keyword-based bypasses.

---

## Evaluation

The project includes a dedicated evaluation suite covering:

* Patient lookup
* Unknown patients
* Doctor discovery
* Appointment availability
* Appointment booking
* Appointment lookup
* Appointment cancellation
* Appointment rescheduling
* Flexible phrasing
* Missing information
* Invalid patients
* Unavailable specialties
* Out-of-scope requests
* Medical safety cases
* Indirect medical requests
* Malformed input
* Stateful operations

Current evaluation result:

```text
45 / 45 tests passed
Accuracy: 100.0%
```

The evaluation framework is designed to measure both:

1. **Tool selection**
2. **Tool execution success**

This makes it possible to identify whether a failure originates from routing, argument extraction, backend logic, or data state.

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
│   └── hospital_knowledge/
│       └── hospital_faq.md
│
├── docs/
│   └── customer_requirements.md
│
├── .gitignore
└── README.md
```

---

## Running Locally

Clone the repository:

```bash
git clone https://github.com/riyaan786/MEDCORE-AI-AGENT-.git
cd MEDCORE-AI-AGENT-
```

Create the virtual environment:

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

Run the application:

```bash
python -m app.main
```

---

## Running the Evaluation Suite

Run:

```bash
python -m app.eval_runner
```

The evaluation suite provides detailed information about:

* Request
* Selected tool
* Tool arguments
* Tool success
* Response
* Pass/fail result
* Overall accuracy

---

## Engineering Approach

MEDCORE AI follows several principles important to real-world AI deployments.

### 1. Customer-first engineering

The system begins with operational requirements rather than starting with a model and looking for a problem to solve.

### 2. Deterministic tools

Critical hospital operations are implemented using deterministic Python services rather than allowing the LLM to directly manipulate application state.

### 3. Explicit routing

Requests are classified before being executed.

### 4. Validation

Patient IDs, appointment IDs, specialties, and dates are validated before operations are performed.

### 5. Stateful behavior

Operations that change appointment state are persisted and can be verified through subsequent requests.

### 6. Evaluation-driven development

Features are accompanied by evaluation cases so that improvements can be measured objectively.

### 7. Safety by design

Medical diagnosis, medication recommendations, and treatment recommendations are explicitly outside the agent's operational scope.

### 8. Small-model engineering

The project demonstrates how careful architecture can compensate for a relatively small local model.

---

## FDE Perspective

This project was built specifically to demonstrate **Forward Deployed Engineering skills**.

An FDE working with an AI system needs more than model knowledge.

They need to understand:

* What the customer actually needs
* Which workflows should be automated
* Where deterministic systems are safer than LLMs
* How to integrate AI with existing software
* How to debug model/tool failures
* How to evaluate reliability
* How to handle edge cases
* How to design safe failure behavior
* How to translate vague customer requirements into engineering requirements
* How to continuously improve the system using real evaluation results

MEDCORE AI is therefore intentionally more than an LLM wrapper.

It demonstrates the complete engineering loop:

```text
Customer Requirement
        ↓
System Design
        ↓
AI + Tools
        ↓
Backend Integration
        ↓
Evaluation
        ↓
Failure Analysis
        ↓
Engineering Improvements
        ↓
Re-evaluation
```

---

## Current Status

**Core agent implementation: Complete**

**Evaluation suite: 45/45 — 100%**

The current repository represents a functional hospital-operations AI agent with patient operations, doctor discovery, appointment workflows, RAG, safety handling, persistence, API support, and evaluation infrastructure.

Future development can extend the system with additional integrations and production infrastructure without changing the core architecture.

---

## Disclaimer

MEDCORE AI is an engineering project and demonstration system.

It is **not a medical diagnostic system** and should not be used to diagnose conditions, prescribe medication, or recommend medical treatment.
