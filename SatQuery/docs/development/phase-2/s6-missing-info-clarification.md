# SatQuery AI — Phase 2 Step 6: Missing Information & Clarification Rules


**Status:** Finalized
**Owner:** Nian — Tech Lead / System Architect

---

## 1. Purpose

SatQuery must determine whether the information required to understand and execute a user request is available.

If required information is missing or genuinely ambiguous, and cannot be safely inferred from the query, available observations, or context, SatQuery must ask the user for clarification **before execution**.

This document defines:

* Missing-information categories
* Missing vs. ambiguous information
* Clarification decision rules
* Safe inference and defaults
* Execution-blocking rules
* Clarification response contract
* Frontend/backend responsibilities
* Re-processing after clarification

---

# 2. Core Principle

```text
User Query
    ↓
Query Understanding
    ↓
Identify Information
    ↓
Is Required Information Available?
    │
 ┌──┴───────────────┐
 │                  │
Yes                No
 │                  │
 ↓                  ↓
Proceed       Can it be safely inferred?
                    │
              ┌─────┴─────┐
             Yes          No
              │            │
              ↓            ↓
            Infer      Safe default?
                           │
                     ┌─────┴─────┐
                    Yes          No
                     │            │
                     ↓            ↓
                  Default      Ask User
                                  ↓
                            User Clarification
                                  ↓
                            Update Query
                                  ↓
                           Re-evaluate Requirements
```

### Mandatory rule

> **SatQuery must not execute a task while a blocking required input remains unresolved.**

---

# 3. Missing vs. Ambiguous Information

SatQuery must distinguish between three states.

### 3.1 Available

The required information is explicitly present or can be reliably obtained from the available context.

Example:

```text
"How many buildings are in this image?"
```

The target object is clearly `building`.

**Action:** Proceed.

---

### 3.2 Missing

The required information is not provided.

Example:

```text
"Compare these images."
```

If only one observation is available, the second observation is missing.

**Action:** Ask for the missing observation.

---

### 3.3 Ambiguous

Information exists but has multiple possible interpretations that could materially change the result.

Example:

```text
"Find the objects."
```

The object class is unspecified.

**Action:** Ask the user which objects they want to find.

---

# 4. Missing Information Categories

SatQuery recognizes the following categories.

| Category             | Example                                            |
| -------------------- | -------------------------------------------------- |
| `observation`        | Satellite image is missing                         |
| `second_observation` | Second image required for comparison               |
| `date`               | "Show the image from..."                           |
| `time`               | Specific observation time required                 |
| `date_range`         | "What changed during this period?"                 |
| `location`           | Geographic location is required                    |
| `place_name`         | User refers to an unspecified place                |
| `target_object`      | "Find objects" — object unspecified                |
| `modality`           | Optical vs SAR cannot be determined                |
| `analysis_objective` | User says "analyze this" without a clear objective |
| `spatial_constraint` | A specific region/area is required                 |

The actual requirement depends on the task identified by the Task Engine.

---

# 5. Clarification Decision Outcomes

Every unresolved requirement must result in one of five decisions.

### 5.1 PROCEED

The information is already available.

```text
Requirement → Available
             ↓
           PROCEED
```

Example:

```text
"How many buildings are in this image?"
```

Target = buildings.

---

### 5.2 INFER

The information can be safely determined from available context without materially changing the intended result.

```text
Requirement → Safely inferable
             ↓
            INFER
```

Inference must be conservative.

SatQuery must not make assumptions that could significantly change the requested analysis.

---

### 5.3 USE_DEFAULT

A safe default exists and using it will not materially alter the interpretation.

```text
Requirement → Safe default exists
             ↓
         USE_DEFAULT
```

Defaults should only be used where the architecture explicitly permits them.

---

### 5.4 ASK_USER

The information is required or materially affects the result, but cannot be safely inferred.

```text
Requirement → Required + unresolved
             ↓
           ASK_USER
```

Example:

```text
"Where are the objects?"
```

Possible clarification:

> "Which objects should I look for?"

---

### 5.5 REJECT

The requested operation is unsupported.

```text
Task / Capability unsupported
             ↓
           REJECT
```

SatQuery should explain the limitation rather than attempting execution.

---

# 6. Decision Rules

The decision process is:

```text
1. Is the information available?
       ↓
      YES → PROCEED

2. If not, can it be safely inferred?
       ↓
      YES → INFER

3. If not, is there an approved safe default?
       ↓
      YES → USE_DEFAULT

4. If unresolved information is required:
       ↓
     ASK_USER

5. If the requested capability/task is unsupported:
       ↓
     REJECT
```

An additional rule applies to ambiguity:

```text
If information is ambiguous
AND
the ambiguity can affect the result
        ↓
    ASK_USER
```

---

# 7. Requirement-Specific Rules

## 7.1 Observation

If the task requires an observation and none is available:

```text
ASK_USER
```

Example:

```text
"Analyze this image."
```

No image is provided.

Response:

> "Please provide a satellite image to analyze."

---

## 7.2 Second Observation

Multi-observation tasks require multiple observations.

Example:

```text
"What changed between these images?"
```

Only one image is available.

```text
second_observation → missing
                  ↓
              ASK_USER
```

Response:

> "Please provide the second satellite image so I can compare the observations."

---

## 7.3 Target Object

Target-dependent operations require a target.

Example:

```text
"Find the objects in this image."
```

If the object type cannot be determined:

```text
target_object → ambiguous
             ↓
          ASK_USER
```

Response:

> "Which objects should I look for?"

---

## 7.4 Date / Time

Date or time must be requested when it is required to identify the intended observation or analysis period and cannot be determined from available context.

Example:

```text
"Show me the satellite image from that date."
```

If the referenced date is unavailable:

```text
date → missing
     ↓
 ASK_USER
```

---

## 7.5 Location / Place Name

Location must be requested when the requested analysis depends on a specific geographic location and that location cannot be determined from the available information.

Example:

```text
"Analyze the flood in this area."
```

If "this area" cannot be resolved:

```text
location → ambiguous
         ↓
      ASK_USER
```

---

## 7.6 Modality

If the task specifically requires a modality and the available data does not establish it:

```text
modality → unresolved
         ↓
      ASK_USER
```

This is particularly relevant for modality-specific operations such as:

* Optical–Optical comparison
* SAR–SAR comparison
* Optical–SAR comparison

---

## 7.7 Analysis Objective

A vague request may not provide enough information to determine the intended operation.

Example:

```text
"Analyze this satellite image."
```

If a general analysis is acceptable:

```text
USE_DEFAULT → General Analysis
```

If the intended objective materially affects the result:

```text
ASK_USER
```

Example:

> "What would you like me to analyze—buildings, water, land cover, or changes?"

---

# 8. Multiple Missing Information

SatQuery should not ask unnecessary questions.

When multiple pieces of information are missing:

```text
User Query
    ↓
Determine task
    ↓
Determine blocking requirements
    ↓
Ask only for information necessary
for the next meaningful decision
```

Example:

```text
"Compare the flood situation."
```

If no observations exist, the first blocking requirement is the observations.

SatQuery should request the required images first rather than asking unrelated questions about modality, date, and location simultaneously.

After the user provides the required information, the system re-evaluates the remaining requirements.

---

# 9. Clarification Response Contract

The backend must expose clarification in a structured form.

### Response

```json
{
  "status": "needs_clarification",
  "missing_information": [
    "target_object"
  ],
  "question": "Which objects should I look for?"
}
```

### Status Values

```text
READY
NEEDS_CLARIFICATION
NOT_READY
UNSUPPORTED
```

### Standard Missing Information Names

```text
observation
second_observation
target_object
date
time
date_range
location
place_name
modality
analysis_objective
spatial_constraint
```

The exact list returned depends on the unresolved requirement.

---

# 10. Clarification Is Not Execution

A clarification state must stop execution.

```text
NEEDS_CLARIFICATION
        ↓
    No execution
        ↓
    Ask user
        ↓
  Receive answer
        ↓
Update structured query
        ↓
Re-evaluate requirements
        ↓
READY?
   ┌────┴────┐
  YES        NO
   ↓          ↓
Execute    Clarify again
```

The Model Engine must **not execute a model** while the system is in `NEEDS_CLARIFICATION`.

---

# 11. Re-processing After Clarification

When the user answers a clarification question:

```text
User Answer
    ↓
Update Existing Structured Query
    ↓
Query / Requirement Re-evaluation
    ↓
Task Engine
    ↓
Data Requirements
    ↓
Data Readiness
```

The system should update the existing query rather than creating an unrelated new request.

Example:

### Initial query

```text
"How many objects are in this image?"
```

Detected:

```text
target_object = missing
```

System:

> "Which objects should I count?"

User:

> "Buildings."

Updated structured query:

```json
{
  "question": "How many objects are in this image?",
  "requested_capabilities": [
    "counting"
  ],
  "missing_information": [],
  "target_object": "building"
}
```

The Task Engine then re-evaluates the request.

---

# 12. Responsibility Boundaries

## Query Engine

Responsible for:

* Understanding the query
* Extracting available information
* Detecting missing information
* Detecting ambiguity
* Representing unresolved information

Not responsible for:

* Executing models
* Checking actual data availability
* Selecting specific models

---

## Task Engine

Responsible for:

* Determining what information the selected task requires
* Determining whether missing information blocks execution
* Evaluating task requirements
* Determining the next processing step

---

## Data Engine

Responsible for:

* Checking whether required observations actually exist
* Checking data validity
* Checking compatibility
* Checking spatial/temporal suitability
* Reporting data readiness

---

## Frontend / Interaction Layer

Responsible for:

* Displaying clarification questions
* Collecting the user's answer
* Sending the answer back to the backend
* Displaying system status

---

## Model Engine

Responsible for:

* Model execution after requirements are satisfied

It must not execute while the system is waiting for clarification.

---

# 13. Example Decision Cases

| User Request                                | Problem                                       | Decision    |
| ------------------------------------------- | --------------------------------------------- | ----------- |
| "How many buildings are here?" + image      | Nothing missing                               | PROCEED     |
| "Find the objects."                         | Target unclear                                | ASK_USER    |
| "Compare these images." + 2 images          | Requirements satisfied                        | PROCEED     |
| "What changed?" + 1 image                   | Second observation missing                    | ASK_USER    |
| "Analyze this image."                       | Objective vague but general analysis possible | USE_DEFAULT |
| "Compare optical and SAR." + modality known | Requirements satisfied                        | PROCEED     |
| "Compare these." + 1 image                  | Second observation missing                    | ASK_USER    |
| Unsupported analysis                        | Capability unavailable                        | REJECT      |

---

# 14. Architectural Contract

The clarification mechanism follows this contract:

```text
                    ┌──────────────────┐
                    │    User Query    │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │   Query Engine   │
                    └────────┬─────────┘
                             ↓
                  Structured Query
                             ↓
                    ┌──────────────────┐
                    │    Task Engine   │
                    └────────┬─────────┘
                             ↓
                  Required Information
                             ↓
                  ┌──────────┴──────────┐
                  │                     │
              Satisfied             Unresolved
                  │                     │
                  ↓                     ↓
              Continue             Clarification
                                        ↓
                                   User Answer
                                        ↓
                                 Update Query
                                        ↓
                                 Re-evaluate
```

This establishes a clean boundary between **understanding**, **requirement evaluation**, **clarification**, and **execution**.

---

# 15. Definition of Done

Step 6 is complete when:

* [x] Missing-information categories are defined
* [x] Missing vs. ambiguous information is defined
* [x] Required vs. optional information is handled
* [x] Safe inference rules are defined
* [x] Safe-default rules are defined
* [x] Clarification decision outcomes are defined
* [x] Execution-blocking rules are defined
* [x] Standard clarification response is defined
* [x] Frontend/backend responsibilities are defined
* [x] Re-processing after clarification is defined
* [x] Unsupported-task handling is defined
* [x] Multi-missing-information behavior is defined
* [x] Clarification examples are defined

---

## Step 6 Final Status

**✅ FINALIZED**

```text
Phase 2
│
├── Step 1 — Structured Query Representation       ✅
├── Step 2 — Task Taxonomy                         ✅
├── Step 3 — Query → Task Mapping                  ✅
├── Step 4 — Data Requirements                     ✅
├── Step 5 — Model Requirements                    ✅
└── Step 6 — Missing Information & Clarification   ✅
```

### Status : FINALIZED**