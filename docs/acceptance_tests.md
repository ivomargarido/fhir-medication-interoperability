# Acceptance Tests

This document records the acceptance tests used to check whether the synthetic
FHIR prototype behaves as expected.

The tests focus on the main clinical question: can medication information from
the Emergency Department remain available after admission while keeping its
original context?

## AT-01 — Emergency to Inpatient Medication Continuity

**Objective**

Check that medication administered in the Emergency Department can still be
retrieved after the patient is admitted.

**Expected behaviour**

- the administration remains linked to the Emergency encounter;
- the Inpatient encounter exists separately;
- the administration is still available through the same patient;
- the administration is not reclassified as an Inpatient event.

**Result:** PASS

---

## AT-02 — Cross-System Patient Identity

**Objective**

Check that different local patient identifiers can be linked to the same
patient.

```text
Emergency   ER-P001
Pharmacy    PH-P874
Inpatient   IP-P144
                |
                v
              PAT001
```

**Expected behaviour**

Information from the three simulated systems is associated with the same
patient identity.

**Result:** PASS

---

## AT-03 — Prescription Continuity Through Pharmacy

**Objective**

Check that the pharmacy dispense remains linked to the original Emergency
prescription.

The Pharmacy system has its own local processing order, but this is not treated
as a second clinical prescription.

**Expected behaviour**

```text
Emergency prescription
        |
        v
MedicationRequest
        |
        v
MedicationDispense
```

**Result:** PASS

---

## AT-04 — Medication Terminology Resolution

**Objective**

Check that different local medication codes can be understood as the same
medication.

```text
Emergency   PARA-INF
Pharmacy    PAR10MGML
Inpatient   PCM-IV
                |
                v
              MED001
```

**Expected behaviour**

The three local codes resolve to the same canonical medication concept.

**Result:** PASS

---

## AT-05 — Preservation of Clinical Context

**Objective**

Check that the medication administration keeps the encounter where it actually
occurred.

```text
Emergency Encounter
ER-E001
status: finished

Medication Administration
ER-ADM001
context: ER-E001

Inpatient Encounter
IP-E001
status: in-progress
```

**Expected behaviour**

The medication administration remains linked to the Emergency encounter even
after the Inpatient encounter begins.

**Result:** PASS

---

## Summary

| Test | What was checked | Result |
|---|---|---|
| AT-01 | Emergency medication remains available after admission | PASS |
| AT-02 | Different local patient IDs resolve to the same patient | PASS |
| AT-03 | Pharmacy dispense remains linked to the original prescription | PASS |
| AT-04 | Different local medication codes resolve to the same medication | PASS |
| AT-05 | Medication administration keeps the original Emergency context | PASS |

These tests support the expected behaviour of the synthetic proof of concept.

They do not demonstrate interoperability with real hospital production systems.
