# SatQuery AI — Phase 2 Step 9: Error Handling, Validation & Failure Recovery


**Status:** **Finalized**
**Owner:** Nian — Tech Lead / System Architect

---

## 1. Purpose

Step 9 defines how SatQuery handles failures and invalid states throughout the system.

The architecture must ensure that every failure is:

* Detected by the responsible component
* Clearly classified
* Propagated without losing its origin
* Recovered when possible
* Retried only when appropriate
* Clarified when user input is required
* Safely terminated when recovery is not possible

### Core principle

> **Every failure must have a clear owner, a defined response, and a defined recovery or termination path.**

---

# 2. Error Handling Architecture

```text
User Query
    ↓
Query Engine
    │
    ├── Invalid Query
    ├── Ambiguous Query
    └── Unsupported Request
    ↓
Task Engine
    │
    ├── Invalid Task
    └── Unsupported Task
    ↓
Data Engine
    │
    ├── Missing Data
    ├── Invalid Data
    ├── Incompatible Data
    └── Insufficient Quality
    ↓
Execution Plan
    ↓
Model Engine
    │
    ├── Model Failure
    ├── Inference Failure
    └── Pipeline Failure
    ↓
Response Engine
    │
    └── Response Failure
    ↓
User
```

---

# 3. Error Categories

SatQuery uses the following primary error categories:

```text
QUERY_ERROR
VALIDATION_ERROR
CLARIFICATION_REQUIRED
TASK_ERROR
DATA_ERROR
MODEL_ERROR
PIPELINE_ERROR
RESPONSE_ERROR
UNSUPPORTED_ERROR
SYSTEM_ERROR
```

These categories identify the general location and nature of a failure.

---

# 4. Query Errors

Query errors occur when the system cannot reliably interpret the user's request.

### Examples

```text
"Do something with this."
```

when the intended operation cannot safely be determined.

Or:

```text
"Compare..."
```

when the required observations are unavailable.

### Handling

```text
User Query
    ↓
Query Engine
    ↓
Can intent be determined?
    │
 ┌──┴────┐
YES      NO
 │        │
 ↓        ↓
Continue Clarify
```

If the problem can be resolved through user input:

```text
NEEDS_CLARIFICATION
```

If the requested capability is outside the system:

```text
UNSUPPORTED
```

---

# 5. Validation Errors

Validation ensures that invalid information does not move further through the pipeline.

Validation may occur at multiple engine boundaries.

### Examples

* Invalid Structured Query
* Missing required field
* Invalid input type
* Invalid task
* Invalid Data Requirements
* Invalid Execution Plan
* Invalid Model input

### Example

```json
{
  "status": "validation_error",
  "error": {
    "code": "INVALID_STRUCTURED_QUERY",
    "message": "Required input information is missing."
  }
}
```

### Rule

> **Invalid input should be rejected as early as possible at the boundary where it becomes detectable.**

---

# 6. Clarification Required

Clarification is **not a system failure**.

It is a normal control-flow state.

```text
Missing / Ambiguous Information
          ↓
  NEEDS_CLARIFICATION
          ↓
       Ask User
          ↓
      User Answer
          ↓
   Update Structured Query
          ↓
      Re-evaluate
```

Example:

```json
{
  "status": "needs_clarification",
  "missing_information": [
    "target_object"
  ],
  "question": "Which objects should I count?"
}
```

The Model Engine must not execute while the request is waiting for clarification.

---

# 7. Task Errors

Task errors originate from the Task Engine.

Examples:

* Unsupported task
* Invalid task mapping
* Conflicting task requirements
* Invalid task configuration
* Unable to generate a valid execution plan

### Example

```json
{
  "status": "unsupported",
  "error": {
    "code": "UNSUPPORTED_TASK",
    "message": "This analysis task is not currently supported."
  }
}
```

The Task Engine owns task-level errors.

---

# 8. Data Errors

The Data Engine owns errors related to actual data.

Examples:

```text
Missing observation
Invalid raster
Unsupported format
Incompatible modality
Insufficient resolution
Invalid spatial coverage
Insufficient temporal information
Corrupted data
```

### Example

```json
{
  "status": "not_ready",
  "error": {
    "code": "INSUFFICIENT_DATA",
    "message": "The available observation does not satisfy the task requirements."
  }
}
```

The Task Engine then determines whether the request should:

* Ask the user for additional information
* Wait for data
* Stop execution

---

# 9. Data Error vs. Clarification

These two conditions must remain distinct.

### User information is missing

```text
User did not provide second image
        ↓
NEEDS_CLARIFICATION
```

### Required data is unavailable

```text
User requested an observation
        ↓
Data Engine checks available data
        ↓
Required data does not exist
        ↓
NOT_READY
```

Therefore:

> **Clarification concerns unresolved user requirements; Data Engine errors concern the actual availability or suitability of data.**

---

# 10. Model Errors

Model Engine errors occur during model loading, input preparation, or inference.

Examples:

```text
Model unavailable
Model loading failure
Invalid model input
Out-of-memory failure
Inference failure
Model timeout
Unexpected model output
```

### Example

```json
{
  "status": "failed",
  "error": {
    "code": "MODEL_INFERENCE_FAILED",
    "message": "Model execution failed."
  }
}
```

The Model Engine owns technical recovery from model-level failures.

---

# 11. Pipeline Errors

A model pipeline may contain multiple stages:

```text
Input
 ↓
Preprocessing
 ↓
Model
 ↓
Postprocessing
 ↓
Result
```

A failure may occur at any stage.

Examples:

```text
PREPROCESSING_FAILED
MODEL_FAILED
POSTPROCESSING_FAILED
```

The failure should identify the stage where it occurred.

---

# 12. Response Errors

A successful model execution does not guarantee successful response generation.

Example:

```text
Model Execution
      ↓
Successful Analysis Result
      ↓
Response Engine
      ↓
Formatting / Generation Failure
```

Example:

```json
{
  "status": "failed",
  "error": {
    "code": "RESPONSE_GENERATION_FAILED",
    "message": "The analysis completed but the response could not be generated."
  }
}
```

The system should distinguish a response failure from an analysis/model failure.

---

# 13. Error Ownership

| Error            | Owner                                |
| ---------------- | ------------------------------------ |
| Query error      | Query Engine                         |
| Validation error | Responsible Engine                   |
| Clarification    | Query/Task + Interaction Layer       |
| Task error       | Task Engine                          |
| Data error       | Data Engine                          |
| Model error      | Model Engine                         |
| Pipeline error   | Component executing the failed stage |
| Response error   | Response Engine                      |
| System error     | Infrastructure/System Layer          |

---

# 14. Recovery Strategies

SatQuery supports six recovery outcomes:

```text
RECOVER
RETRY
CLARIFY
WAIT
FALLBACK
ABORT
```

### RECOVER

The responsible component can correct the problem internally.

### RETRY

A temporary failure may succeed when attempted again.

### CLARIFY

Additional user information is required.

### WAIT

Required data or processing is not currently available.

### FALLBACK

Another supported path can safely satisfy the same user request.

### ABORT

Execution cannot safely continue.

---

# 15. Retry Rules

Retries should only be used for failures that are potentially temporary.

```text
Failure
  ↓
Is failure transient?
  │
 ┌┴──────┐
YES      NO
 │        │
 ↓        ↓
Retry   Do not retry
```

### Possible retry cases

* Temporary service unavailability
* Temporary timeout
* Temporary infrastructure failure

### Normally non-retryable cases

* Invalid input
* Unsupported task
* Missing observation
* Unsupported modality
* Invalid raster

SatQuery must avoid repeatedly retrying permanent failures.

---

# 16. Fallback Rules

Fallback is permitted only when the alternative path preserves the intended task.

### Valid fallback

```text
General image question
        ↓
Preferred path unavailable
        ↓
General VLM is capable
        ↓
FALLBACK
```

### Invalid silent fallback

```text
Change Detection
        ↓
Change model unavailable
        ↓
Unrelated VLM
        ↓
NOT ALLOWED
```

The system must never silently substitute an unrelated capability.

---

# 17. Error Response Contract

A standard error structure is used across the system.

```json
{
  "status": "failed",
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable description.",
    "stage": "task_engine",
    "recoverable": false
  }
}
```

### Fields

| Field               | Purpose                                    |
| ------------------- | ------------------------------------------ |
| `status`            | Overall processing state                   |
| `error.code`        | Machine-readable error identifier          |
| `error.message`     | Human-readable description                 |
| `error.stage`       | Component/stage where the failure occurred |
| `error.recoverable` | Whether recovery may be possible           |

---

# 18. Standard Error Codes

Initial error codes:

```text
QUERY_INVALID
QUERY_AMBIGUOUS
STRUCTURED_QUERY_INVALID

TASK_UNSUPPORTED
TASK_INVALID
TASK_REQUIREMENTS_INVALID

DATA_MISSING
DATA_INVALID
DATA_INCOMPATIBLE
DATA_INSUFFICIENT
DATA_QUALITY_INSUFFICIENT

MODEL_UNAVAILABLE
MODEL_INPUT_INVALID
MODEL_INFERENCE_FAILED
MODEL_TIMEOUT

PREPROCESSING_FAILED
POSTPROCESSING_FAILED
PIPELINE_FAILED

RESPONSE_GENERATION_FAILED

SYSTEM_ERROR
TIMEOUT
```

The error-code set can be extended as implementation requirements become clearer.

---

# 19. Error Propagation

Errors must propagate across engine boundaries without losing their origin.

Example:

```text
Model Engine
     ↓
MODEL_INFERENCE_FAILED
     ↓
Orchestration Layer
     ↓
Response Engine
     ↓
User-facing message
```

The user-facing message may be simplified, but internal error information must remain available for debugging and recovery.

---

# 20. User-Facing Error Principle

Technical implementation details should not unnecessarily be exposed to the user.

### Internal error

```text
CUDA out of memory during tensor allocation
```

### User-facing response

> "The analysis could not be completed because the processing system ran out of resources. Please try again."

The internal diagnostic remains available for developers.

---

# 21. Logging & Traceability

Each request should be traceable throughout the pipeline.

```text
request_id
    ↓
Structured Query
    ↓
Task
    ↓
Data Readiness
    ↓
Execution Plan
    ↓
Model Execution
    ↓
Analysis Result
    ↓
Response
```

The system should retain enough information to determine:

* What happened
* Which component handled it
* What state was reached
* Where the failure occurred
* Why it occurred
* Whether recovery was attempted
* What the final outcome was

This is required for debugging and integration testing.

---

# 22. Complete Failure Flow

```text
                     USER QUERY
                          │
                          ▼
                  ┌───────────────┐
                  │ Query Engine  │
                  └───────┬───────┘
                          │
                    Validate Query
                          │
                 ┌────────┴────────┐
                 │                 │
               Valid             Invalid
                 │                 │
                 ↓                 ↓
          Structured Query     Clarify/Reject
                 │
                 ▼
          ┌───────────────┐
          │  Task Engine  │
          └───────┬───────┘
                  │
             Validate Task
                  │
             ┌────┴─────┐
           Valid       Invalid
             │            │
             ↓            ↓
      Data Requirements  Reject
             │
             ▼
       ┌───────────────┐
       │  Data Engine  │
       └───────┬───────┘
               │
          Validate Data
               │
          ┌────┴────┐
        Ready     Not Ready
          │          │
          ↓          ↓
    Execution Plan  Clarify/Wait
          │
          ▼
    ┌───────────────┐
    │ Model Engine  │
    └───────┬───────┘
            │
         Execute
            │
       ┌────┴────┐
    Success    Failure
       │          │
       ↓          ↓
     Result   Retry/Fallback/
                 Abort
       │
       ▼
 ┌───────────────┐
 │Response Engine│
 └───────┬───────┘
         │
         ▼
        USER
```

---

# 23. End-to-End Recovery Logic

```text
Failure
  ↓
Identify failure owner
  ↓
Classify failure
  ↓
Is user information required?
  │
 ┌┴──────┐
YES     NO
 │       │
 ↓       ↓
Clarify  Is it recoverable?
           │
        ┌──┴───┐
       YES     NO
        │       │
        ↓       ↓
  Retry/Recover Can safe
        │       │
        │     fallback?
        │       │
        │    ┌──┴──┐
        │   YES    NO
        │    │      │
        │    ↓      ↓
        │ Fallback Abort
        ↓
      Continue
```

---

# 24. Architectural Rules

1. **Every error must have a clear owner.**
2. **Clarification is a normal control-flow state, not a system failure.**
3. **Execution must stop when a blocking requirement fails.**
4. **Only potentially recoverable failures should be retried.**
5. **Permanent failures must not be repeatedly retried.**
6. **Fallback must preserve the user's intended task.**
7. **Unsupported operations must be explicitly reported.**
8. **Error origin must be preserved across engine boundaries.**
9. **Technical errors should be separated from user-facing messages.**
10. **Every request must be traceable through the pipeline.**
11. **Each engine must handle failures within its responsibility boundary.**
12. **Recovery must never produce an unsafe or misleading result.**

---

# 25. Definition of Done

* [x] Error categories defined
* [x] Query error handling defined
* [x] Validation rules defined
* [x] Clarification handling defined
* [x] Task errors defined
* [x] Data errors defined
* [x] Data error vs clarification distinguished
* [x] Model errors defined
* [x] Pipeline errors defined
* [x] Response errors defined
* [x] Error ownership defined
* [x] Recovery strategies defined
* [x] Retry rules defined
* [x] Fallback rules defined
* [x] Error response contract defined
* [x] Standard error codes defined
* [x] Error propagation defined
* [x] Logging and traceability requirements defined
* [x] User-facing error principles defined
* [x] Complete failure flow defined
* [x] Recovery logic defined
* [x] Architectural rules defined

---

## Status : FINALIZED