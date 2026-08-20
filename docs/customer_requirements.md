# MedCore AI — Customer Requirements

## Customer

MedCore Health

## Industry

Healthcare

## Project Goal

Build an AI system that helps healthcare staff complete routine
workflows while maintaining appropriate human oversight for
sensitive situations.

## Customer Problems

### 1. Appointment Operations

Staff need a faster way to find and manage patient appointments.

The system should be able to:
- Find available doctors and appointment slots
- Look up appointment information
- Schedule appointments
- Cancel appointments

### 2. Hospital Policy Knowledge

Staff spend time searching through hospital policies.

The system should:
- Answer questions about approved hospital policies
- Retrieve relevant policy information
- Avoid inventing information
- Clearly indicate when the available policy information is insufficient

### 3. Patient Support and Escalation

The hospital wants AI to handle routine support requests while
recognizing situations that require human intervention.

The system should:
- Handle routine requests
- Identify requests requiring escalation
- Route sensitive cases to a human workflow
- Avoid providing medical diagnosis or treatment

## Initial Success Criteria

### Appointment Operations
Target: 95% successful completion on defined test scenarios.

### Policy Knowledge
Target: 90%+ correct and grounded responses on evaluation scenarios.

### Patient Support
Target: 95% correct classification of routine versus escalation cases.

## Important Constraint

All patient and hospital data used during development will be
synthetic. No real patient information will be used.