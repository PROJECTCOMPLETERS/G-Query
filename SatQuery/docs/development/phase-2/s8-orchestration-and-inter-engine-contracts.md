# SatQuery AI — Phase 2 Step 8: Orchestration & Inter-Engine Contracts


**Status:** Finalized
**Owner:** Nian — Tech Lead / System Architect

---

## 1. Purpose

Step 8 defines how the SatQuery engines communicate with each other.

The goal is to establish clear contracts between:

* Query Engine
* Task Engine
* Data Engine
* Model Engine
* Response Engine

Each engine communicates through defined inputs, outputs, and statuses rather than depending on another engine's internal implementation.

---

# 2. Core Orchestration

```text
User
 ↓
Query Engine
 ↓
Structured Query
 ↓
Task Engine
 ↓
Task + Requirements
 ↓
Data Engine
 ↓
Data Readiness
 ↓
Execution Plan
 ↓
Model Engine
 ↓
Analysis Result
 ↓
Response Engine
 ↓
User
```

---

# 3. Engine Responsibility Boundary

| Component       | Responsibility                                   |
| --------------- | ------------------------------------------------ |
| Query Engine    | Understand the user query                        |
| Task Engine     | Determine task, requirements, and execution plan |
| Data Engine     | Validate actual data suitability                 |
| Model Engine    | Execute required ML capabilities                 |
| Response Engine | Produce the user-facing response                 |

### Boundary Principle

> **Task Engine decides what needs to happen; Data Engine decides whether the available data is suitable; Model Engine executes the required ML capability.**

---

# 4. Contract 1 — Query Engine → Task Engine

The Query Engine sends a `StructuredQuery`.

### Example

```json
{
  "question": "How many buildings are in this image?",
  "intent": "count",
  "entities": [
    "building"
  ],
  "inputs": [
    {
      "input_id": "obs_001",
      "type": "image"
    }
  ],
  "modality": "optical",
  "temporal": {
    "required": false,
    "information": null
  },
  "spatial": {
    "required": false,
    "information": null
  },
  "requested_capabilities": [
    "counting"
  ],
  "missing_information": []
}
```

### Responsibility

The Query Engine answers:

> **What does the user mean?**

The Task Engine answers:

> **What should SatQuery do about it?**

---

# 5. Contract 2 — Task Engine → Data Engine

The Task Engine converts the identified task into `Data Requirements`.

### Example

```json
{
  "task": "object_counting",
  "inputs": {
    "min_observations": 1,
    "type": "image"
  },
  "modality": {
    "required": true,
    "allowed": [
      "compatible"
    ]
  },
  "temporal": {
    "required": false
  },
  "spatial": {
    "required": false
  },
  "quality": {
    "valid_data": true,
    "sufficient_resolution": true
  },
  "task_specific": {
    "target_object": "building"
  }
}
```

The Data Engine evaluates the actual available data against these requirements.

---

# 6. Contract 3 — Data Engine → Task Engine

The Data Engine returns a data-readiness result.

## Ready

```json
{
  "status": "ready",
  "ready": true,
  "available_observations": [
    "obs_001"
  ],
  "missing_information": []
}
```

## Not Ready

```json
{
  "status": "not_ready",
  "ready": false,
  "available_observations": [
    "obs_001"
  ],
  "missing_information": [
    "second_observation"
  ]
}
```

The Task Engine uses this result to determine whether to:

* Proceed
* Ask for clarification
* Wait for data
* Reject the request

---

# 7. Contract 4 — Task Engine → Model Engine

When all requirements are satisfied, the Task Engine produces an `ExecutionPlan`.

### Example

```json
{
  "task": "object_counting",
  "input_observations": [
    "obs_001"
  ],
  "required_modalities": [
    "optical"
  ],
  "temporal_requirements": {
    "required": false
  },
  "spatial_requirements": {
    "required": false
  },
  "preprocessing": [],
  "model_requirements": {
    "capabilities": [
      "object_detection",
      "counting"
    ]
  },
  "expected_output": {
    "type": "count",
    "target": "building"
  }
}
```

The Model Engine receives **capability requirements**, not a forced model selection.

Actual model selection belongs to Phase 3.

---

# 8. Contract 5 — Model Engine → Response Engine

The Model Engine returns an `AnalysisResult`.

### Example

```json
{
  "status": "success",
  "task": "object_counting",
  "result": {
    "target": "building",
    "count": 47
  },
  "metadata": {}
}
```

The Response Engine converts the result into a user-facing response.

```text
Model Result
     ↓
Response Engine
     ↓
"47 buildings were detected."
```

---

# 9. Clarification Contract

If required information is missing or ambiguous:

```text
Task Engine
     ↓
NEEDS_CLARIFICATION
```

The system returns:

```json
{
  "status": "needs_clarification",
  "missing_information": [
    "target_object"
  ],
  "question": "Which objects should I count?"
}
```

The request must **not** continue to the Model Engine.

After the user responds:

```text
User Answer
    ↓
Update Structured Query
    ↓
Task Engine
    ↓
Re-evaluate Requirements
```

---

# 10. Global Status Model

SatQuery uses consistent processing states:

```text
RECEIVED
VALIDATING
TASK_IDENTIFIED
NEEDS_CLARIFICATION
WAITING_FOR_DATA
NOT_READY
READY
EXECUTION_PLANNED
EXECUTING
COMPLETED
FAILED
UNSUPPORTED
```

Not every engine needs every state.

### Query Engine

```text
RECEIVED
    ↓
VALIDATING
    ↓
READY / NEEDS_CLARIFICATION
```

### Task Engine

```text
VALIDATING
    ↓
TASK_IDENTIFIED
    ↓
READY / NEEDS_CLARIFICATION / UNSUPPORTED
```

### Data Engine

```text
WAITING_FOR_DATA
    ↓
READY / NOT_READY
```

### Model Engine

```text
EXECUTION_PLANNED
    ↓
EXECUTING
    ↓
COMPLETED / FAILED
```

---

# 11. Failure Boundaries

Each engine reports failures within its own responsibility boundary.

### Query Engine

```text
Query parsing / understanding failure
```

### Task Engine

```text
Invalid task mapping
Unsupported task
Invalid execution plan
```

### Data Engine

```text
Missing data
Invalid data
Incompatible data
Insufficient data quality
```

### Model Engine

```text
Model loading failure
Inference failure
Pipeline execution failure
```

### Response Engine

```text
Result formatting / response generation failure
```

The system must preserve the origin of the failure instead of hiding it behind a generic error.

---

# 12. Complete Orchestration

```text
┌──────────────┐
│     USER     │
└──────┬───────┘
       ↓
┌──────────────┐
│ Query Engine │
└──────┬───────┘
       ↓
 Structured Query
       ↓
┌──────────────┐
│ Task Engine  │
└──────┬───────┘
       ↓
 Task + Requirements
       ↓
┌──────────────┐
│ Data Engine  │
└──────┬───────┘
       ↓
 Data Readiness
       │
   ┌───┴────┐
   │        │
 READY    NOT READY
   │        │
   ↓        ↓
Execution  Clarify /
 Plan      Wait
   │
   ↓
┌──────────────┐
│ Model Engine │
└──────┬───────┘
       ↓
 Analysis Result
       ↓
┌────────────────┐
│ Response Engine│
└──────┬─────────┘
       ↓
      USER
```

---

# 13. Clarification Flow

```text
Task Engine
     ↓
Required Information Missing
     ↓
NEEDS_CLARIFICATION
     ↓
Frontend displays question
     ↓
User provides answer
     ↓
Structured Query updated
     ↓
Task Engine re-evaluates
     ↓
Requirements satisfied?
     │
 ┌───┴────┐
YES       NO
 │         │
 ↓         ↓
Continue  Clarify again
```

Clarification is therefore a **control-flow state**, not an execution step.

---

# 14. Data Readiness Flow

```text
Task Engine
     ↓
Data Requirements
     ↓
Data Engine
     ↓
┌───────────────────┐
│ Check actual data │
└─────────┬─────────┘
          ↓
     Data Ready?
      ┌───┴───┐
     YES      NO
      ↓        ↓
Execution   NOT_READY
Plan          / Clarify
```

The Data Engine owns the actual data validation.

---

# 15. Execution Flow

Once data is ready:

```text
Data Readiness
     ↓
Task Engine
     ↓
Execution Plan
     ↓
Model Engine
     ↓
Model Execution
     ↓
Analysis Result
     ↓
Response Engine
     ↓
User
```

---

# 16. Phase 2 → Phase 3 Boundary

## Phase 2 Defines

```text
Structured Query
Task Taxonomy
Query → Task Mapping
Data Requirements
Model Requirements
Clarification Rules
Task Engine
Execution Plan
Inter-Engine Contracts
```

## Phase 3 Implements

```text
Actual Models
Model Loading
Model Selection
Model Inference
Preprocessing Implementation
Model Pipelines
Inference Optimization
Analysis Execution
```

Therefore:

```text
                PHASE 2
                   │
                   │ Execution Plan
                   ▼
             ┌─────────────┐
             │   PHASE 3   │
             │             │
             │ Model Engine│
             │      ↓      │
             │Actual Models│
             │      ↓      │
             │  Inference  │
             └─────────────┘
```

---

# 17. Simplest-Capable-Path Rule

The orchestration system should select the **simplest pipeline capable of satisfying the request**.

Example:

```text
"What is in this image?"
        ↓
General Image Understanding
        ↓
General VLM
```

No specialized satellite pipeline is required if the request only requires general image understanding.

However:

```text
"Where are the buildings?"
        ↓
Spatial Object Analysis
        ↓
Detection / Grounding Pipeline
```

And:

```text
"What changed between these satellite images?"
        ↓
Multi-Observation Analysis
        ↓
Change Analysis Pipeline
```

---

# 18. Example — Complete Request

### User

> "How many buildings are in this satellite image?"

### Query Engine

```text
Intent → count
Target → building
Input → image
Capability → counting
```

### Task Engine

```text
Task → Object Counting
```

### Data Requirements

```text
Observation → available
Target → available
Image → available
Resolution → must be checked
```

### Data Engine

```text
Data suitable?
      ↓
     YES
```

### Execution Plan

```text
Object Detection
        +
Counting
```

### Model Engine

Executes the required capability.

### Response Engine

Produces:

> "47 buildings were detected."

---

# 19. Example — Missing Observation

### User

> "What changed between these images?"

Only one observation is available.

```text
Query Engine
      ↓
Structured Query
      ↓
Task Engine
      ↓
Change Analysis
      ↓
Requires ≥2 observations
      ↓
Second observation missing
      ↓
NEEDS_CLARIFICATION
```

Response:

> "Please provide the second satellite image."

No model execution occurs.

---

# 20. Example — Multi-Observation Request

### User

> "What changed between these two satellite images?"

```text
Query Engine
      ↓
2 observations
      ↓
Task Engine
      ↓
Change Analysis
      ↓
Data Requirements
      ↓
Data Engine
      ↓
Check:
 ✓ Two observations
 ✓ Valid imagery
 ✓ Compatible coverage
 ✓ Temporal relationship
      ↓
Execution Plan
```

Logical pipeline:

```text
Observation A
       +
Observation B
       ↓
Alignment / Normalization
       ↓
Change Detection
       ↓
Changed Regions
       ↓
Interpretation
```

---

# 21. Contract Design Principles

### 21.1 Loose Coupling

Engines must communicate through contracts rather than internal implementation details.

### 21.2 Single Responsibility

Each engine owns its defined responsibility.

### 21.3 Explicit State

Every major transition should have a recognizable status.

### 21.4 Execution Safety

No execution should occur when blocking requirements remain unresolved.

### 21.5 Phase Separation

Phase 2 defines requirements and contracts; Phase 3 implements model execution.

### 21.6 Traceability

A request should be traceable through:

```text
Query
 → Structured Query
 → Task
 → Requirements
 → Data Readiness
 → Execution Plan
 → Model Result
 → Response
```

---

# 22. Definition of Done

* [x] Engine communication architecture defined
* [x] Query Engine → Task Engine contract defined
* [x] Task Engine → Data Engine contract defined
* [x] Data Engine → Task Engine readiness contract defined
* [x] Task Engine → Model Engine execution contract defined
* [x] Model Engine → Response Engine result contract defined
* [x] Clarification contract defined
* [x] Global status model defined
* [x] Failure boundaries defined
* [x] Complete orchestration defined
* [x] Clarification flow defined
* [x] Data readiness flow defined
* [x] Phase 2 → Phase 3 boundary defined
* [x] Simplest-capable-path rule defined
* [x] End-to-end examples defined
* [x] Contract design principles defined

---

## Status : FINALIZED**

