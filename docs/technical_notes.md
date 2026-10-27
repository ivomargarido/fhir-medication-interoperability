# Technical Notes

This document records a small number of technical decisions and findings from
the prototype.

It is not intended to be full software documentation.

## 1. Canonical model before FHIR

The simulated Emergency, Pharmacy and Inpatient systems use different local
identifiers and medication codes.

Before creating FHIR resources, these local values are linked to a common
canonical representation.

Example:

```text
ER-P001
PH-P874
IP-P144
   |
   v
PAT001
```

The same approach is used for professionals and medication.

This keeps the source-system representation separate from the common model used
for interoperability.

## 2. Prescription, dispensing and administration are different events

The prototype keeps these concepts separate:

- `MedicationRequest`
- `MedicationDispense`
- `MedicationAdministration`

A prescription does not mean that medication was dispensed, and dispensing
does not mean that it was administered.

## 3. The Pharmacy local order is not a second prescription

The Pharmacy system contains a local order used for internal processing.

In this prototype, that order is not converted into a second
`MedicationRequest`.

The `MedicationDispense` remains linked to the original Emergency
prescription.

## 4. Keep the original Encounter

Medication administered in the Emergency Department remains linked to the
Emergency encounter.

When the patient is later admitted, a new Inpatient encounter is created.

The administration is not moved to the Inpatient encounter.

This preserves the original clinical meaning of the event.

## 5. Functional identifier vs FHIR resource reference

During local server testing, an important difference became clear.

Example:

```text
Functional identifier:
PAT001

Technical FHIR reference:
Patient/1000
```

`PAT001` represents the patient identity used by the project.

`Patient/1000` points to a specific resource stored on the local FHIR server.

The project therefore keeps the idea of clinical/business identity separate
from the technical server resource ID.

## 6. FHIR validation

The generated resources were checked against FHIR R4 4.0.1 with the HL7 FHIR
Validator.

The final set had:

```text
0 structural FHIR errors
```

Some non-critical warnings remained, including warnings related to
human-readable narrative and the synthetic medication code system.

These were accepted within the limited scope of the prototype.

## 7. Local HAPI FHIR server

A local HAPI FHIR JPA Server was used to test storage, search and basic resource
linking.

The server was only a local test environment.

It does not represent the architecture of SClínico, GLINTT or any real hospital
integration platform.

## 8. Scope kept intentionally small

The project does not attempt to implement:

- a full Master Patient Index;
- production terminology services;
- medication reconciliation;
- clinical decision support;
- production security;
- audit infrastructure;
- real-time integration;
- production deployment.

The goal was to test one medication interoperability scenario clearly.

## 9. AI-assisted technical implementation

A substantial part of the technical implementation was developed with AI
assistance, including Python code, FHIR mapping code, validation utilities,
local server setup and REST testing.

The clinical problem, workflow, scope, validation requirements, acceptance
criteria and interpretation of the results were defined and reviewed as part of
the project work.
