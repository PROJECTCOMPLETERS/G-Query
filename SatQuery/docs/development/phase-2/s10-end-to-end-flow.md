# SatQuery AI — Phase 2 Step 10: Integration & End-to-End Flow


**Status:** **Finalized**
**Owner:** Nian — Tech Lead / System Architect

---

## 1. Purpose

Step 10 defines how the individual SatQuery components work together as one complete system.

Previous Phase 2 steps defined:

* Query representation
* Task taxonomy
* Query → Task mapping
* Data requirements
* Model requirements
* Clarification rules
* Task Engine
* Execution Plan
* Inter-engine contracts
* Error handling

This step integrates those definitions into complete end-to-end flows.

---

# 2. Complete System Architecture

```text
                         USER
                           │
                           ▼
                  ┌─────────────────┐
                  │   Query Engine  │
                  └────────┬────────┘
                           │
                    Structured Query
                           │
                           ▼
                  ┌─────────────────┐
                  │   Task Engine   │
                  └────────┬────────┘
                           │
                  Task + Requirements
                           │
                           ▼
                  ┌─────────────────┐
                  │   Data Engine   │
                  └────────┬────────┘
                           │
                    Data Readiness
                           │
                           ▼
                  ┌─────────────────┐
                  │ Execution Plan  │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Model Engine   │
                  └────────┬────────┘
                           │
                    Analysis Result
                           │
                ┌──────────┴──────────┐
                │                     │
                ▼                     ▼
         Spatial Result          Text / Analysis
                │                     │
                ▼                     ▼
           Map / UI             Response Engine
                │                     │
                └──────────┬──────────┘
                           ▼
                          USER
```

---

# 3. End-to-End Request Lifecycle

Every standard request follows:

```text
User Request
    ↓
Query Understanding
    ↓
Structured Query
    ↓
Task Identification
    ↓
Requirement Evaluation
    ↓
Data Validation
    ↓
Execution Plan
    ↓
Model Execution
    ↓
Analysis Result
    ↓
Response / Visualization
    ↓
User
```

A request may leave this path temporarily for clarification, waiting, recovery, or failure handling.

---

# 4. Stage 1 — User Input

The user provides a natural-language request.

Example:

> "How many buildings are in this satellite image?"

The request may contain:

* Natural-language question
* Uploaded observation(s)
* Date/time
* Location
* Target object
* Modality
* Spatial constraints
* Temporal constraints

---

# 5. Stage 2 — Query Engine

The Query Engine converts the user's request into a Structured Query.

Example:

```json id="r8ml6a"
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

The Query Engine does not execute the requested analysis.

---

# 6. Stage 3 — Task Engine

The Task Engine receives the Structured Query and determines the task.

```text
Structured Query
       ↓
Task Identification
       ↓
Object Counting
```

It then determines:

* Required observations
* Required modality
* Required spatial information
* Required temporal information
* Required data quality
* Required model capabilities
* Expected output

---

# 7. Stage 4 — Requirement Evaluation

The Task Engine evaluates whether the request contains all information required for the selected task.

```text
Task Requirements
        VS
Available Information
```

Possible outcomes:

```text
READY
NEEDS_CLARIFICATION
NOT_READY
UNSUPPORTED
```

---

# 8. Stage 5 — Data Engine

If the task requires actual data validation, the Task Engine sends the Data Requirements to the Data Engine.

```text
Task Engine
     ↓
Data Requirements
     ↓
Data Engine
     ↓
Actual Data Validation
```

The Data Engine checks the available observations against the requirements.

Examples:

* Data exists
* Data is valid
* Modality is compatible
* Spatial coverage is compatible
* Temporal requirements are satisfied
* Data quality is sufficient

---

# 9. Stage 6 — Data Readiness

The Data Engine returns a readiness result.

### Ready

```json id="f8x7ba"
{
  "status": "ready",
  "ready": true,
  "available_observations": [
    "obs_001"
  ],
  "missing_information": []
}
```

### Not Ready

```json id="t3qrrp"
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

The Task Engine uses this result to determine the next step.

---

# 10. Stage 7 — Execution Plan

When all requirements are satisfied, the Task Engine generates the Execution Plan.

```json id="l7w2b3"
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

---

# 11. Stage 8 — Model Engine

The Model Engine receives the Execution Plan.

The Model Engine is responsible for:

* Model selection
* Model loading
* Preprocessing implementation
* Inference
* Postprocessing
* Producing the expected result

These implementation responsibilities belong to Phase 3.

---

# 12. Stage 9 — Analysis Result

The Model Engine returns an analysis result.

Example:

```json id="x7h0p2"
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

---

# 13. Stage 10 — Result Routing

The result may contain different types of information.

```text
Analysis Result
      │
 ┌────┴─────────┐
 │              │
Text         Spatial
 │              │
 ↓              ↓
Response      Map / UI
Engine
```

### Text results

Examples:

* Counts
* Classifications
* Descriptions
* Explanations

These are passed to the Response Engine.

### Spatial results

Examples:

* Bounding boxes
* Polygons
* Segmentation masks
* Geographic regions
* Detected object locations

These can be passed to the frontend/map layer for visualization.

---

# 14. Normal Successful Flow

Example:

> "How many buildings are in this image?"

```text
User
 ↓
Query Engine
 ↓
Structured Query
 ↓
Task Engine
 ↓
Object Counting
 ↓
Data Engine
 ↓
Data Ready
 ↓
Execution Plan
 ↓
Model Engine
 ↓
47 detected buildings
 ↓
Response Engine
 ↓
User
```

---

# 15. Clarification Flow

Example:

> "How many objects are here?"

The target is ambiguous.

```text
User
 ↓
Query Engine
 ↓
Structured Query
 ↓
Task Engine
 ↓
Target missing / ambiguous
 ↓
NEEDS_CLARIFICATION
 ↓
Frontend
 ↓
"Which objects should I count?"
 ↓
User
 ↓
Answer: "Buildings"
 ↓
Update Structured Query
 ↓
Task Engine
 ↓
Re-evaluate
```

The Model Engine is not called during clarification.

---

# 16. Missing Observation Flow

Example:

> "What changed between these images?"

Only one observation is available.

```text
User
 ↓
Query Engine
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
 ↓
User provides second image
 ↓
Update Structured Query
 ↓
Re-evaluate
 ↓
Data Engine
 ↓
Continue
```

---

# 17. Data Not Ready Flow

If the required information is known but the actual data is unavailable:

```text
Task Engine
 ↓
Data Requirements
 ↓
Data Engine
 ↓
Data unavailable
 ↓
NOT_READY
```

The system does not proceed to model execution.

The appropriate next action may be:

```text
WAIT
CLARIFY
ABORT
```

depending on the reason the data is unavailable.

---

# 18. Multi-Observation Flow

Example:

> "What changed between these two satellite images?"

```text
                    USER
                      │
                      ▼
               Query Engine
                      │
               Structured Query
                      │
                      ▼
                Task Engine
                      │
                Change Analysis
                      │
                      ▼
                Data Engine
                      │
              Validate Both Images
                      │
                      ▼
               Data Readiness
                      │
                      ▼
               Execution Plan
                      │
                      ▼
               Model Engine
                      │
                      ▼
              Change Detection
                      │
                      ▼
               Analysis Result
                      │
              ┌───────┴────────┐
              ▼                ▼
        Changed Regions     Explanation
              │                │
              ▼                ▼
             Map          Response Engine
              │                │
              └───────┬────────┘
                      ▼
                     USER
```

---

# 19. Model Failure Flow

If model execution fails:

```text
Execution Plan
      ↓
Model Engine
      ↓
Model Failure
      ↓
Classify Failure
      │
 ┌────┴──────────┐
 │               │
Recoverable   Permanent
 │               │
 ↓               ↓
Retry /        Fallback /
Recover        Abort
```

The error must preserve the model execution stage and error code.

---

# 20. Complete Failure-Recovery Integration

```text
Failure
   ↓
Identify Owner
   ↓
Classify
   ↓
User input required?
 ┌─┴───┐
YES   NO
 │     │
 ↓     ↓
Clarify  Recoverable?
          │
       ┌──┴──┐
      YES    NO
       │      │
       ↓      ↓
   Retry /  Fallback?
   Recover     │
           ┌──┴──┐
          YES    NO
           │      │
           ↓      ↓
        Fallback Abort
```

---

# 21. Frontend Integration

The frontend interacts primarily with system-level request and response states.

```text
Frontend
   ↓
Backend / Orchestrator
   ↓
Query Engine
   ↓
...
```

The frontend must be able to display:

```text
READY
NEEDS_CLARIFICATION
WAITING_FOR_DATA
NOT_READY
EXECUTING
COMPLETED
FAILED
UNSUPPORTED
```

### Clarification

Frontend receives:

```json id="q4l7v9"
{
  "status": "needs_clarification",
  "missing_information": [
    "target_object"
  ],
  "question": "Which objects should I count?"
}
```

Frontend displays the question and sends the user's answer back.

---

# 22. Map / Spatial Integration

Spatial outputs must be distinguishable from ordinary textual results.

Possible spatial outputs include:

```text
Bounding Boxes
Polygons
Segmentation Masks
Geographic Coordinates
Changed Regions
Detected Features
```

Conceptual flow:

```text
Model Engine
     ↓
Spatial Analysis Result
     ↓
Map / Spatial Output Layer
     ↓
MapLibre / Frontend
```

The Model Engine should return structured spatial information rather than directly controlling the frontend.

---

# 23. Backend Integration

The backend/orchestration layer coordinates the engines.

Conceptually:

```text
Request
   ↓
Query Engine
   ↓
Task Engine
   ↓
Data Engine
   ↓
Task Engine
   ↓
Model Engine
   ↓
Response Engine
   ↓
Response
```

The orchestration layer should not duplicate the internal logic of individual engines.

Its responsibility is to:

* Route requests
* Maintain state
* Pass contracts
* Handle transitions
* Propagate errors
* Return the final result

---

# 24. End-to-End State Flow

```text
RECEIVED
   ↓
VALIDATING
   ↓
TASK_IDENTIFIED
   ↓
REQUIREMENTS_CHECKED
   │
   ├──────────────→ NEEDS_CLARIFICATION
   │                       │
   │                       ↓
   │                 User Answer
   │                       │
   │                       └──────→ REQUIREMENTS_CHECKED
   │
   ↓
WAITING_FOR_DATA
   │
   ├──────────────→ NOT_READY
   │
   ↓
READY
   ↓
EXECUTION_PLANNED
   ↓
EXECUTING
   │
   ├──────────────→ FAILED
   │
   ↓
COMPLETED
```

---

# 25. Traceability

Every request should maintain a trace across the complete pipeline.

```text
request_id
    ↓
Structured Query
    ↓
Task
    ↓
Requirements
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

This allows the team to determine exactly where a request is currently located and where a failure occurred.

---

# 26. End-to-End Test Scenarios

The following scenarios should be used during integration testing.

### Test 1 — Simple VLM/Image Understanding

```text
Input:
"What is in this image?"

Expected:
Query → General Image Understanding
      → Model Execution
      → Natural-language response
```

---

### Test 2 — Object Detection

```text
Input:
"Find all buildings."

Expected:
Query → Object Detection
      → Data Validation
      → Execution Plan
      → Detection Result
```

---

### Test 3 — Object Counting

```text
Input:
"How many buildings are there?"

Expected:
Object Detection + Counting
```

---

### Test 4 — Visual Grounding

```text
Input:
"Where are the buildings?"

Expected:
Detection / Grounding
      ↓
Spatial output
      ↓
Map/UI
```

---

### Test 5 — Missing Target

```text
Input:
"How many objects are there?"

Expected:
NEEDS_CLARIFICATION
```

---

### Test 6 — Change Analysis

```text
Input:
"What changed between these images?"

Expected:
Requires ≥2 observations
      ↓
Change Analysis
```

---

### Test 7 — Missing Second Observation

```text
Input:
"What changed?"

Available:
1 observation

Expected:
NEEDS_CLARIFICATION
```

---

### Test 8 — Flood Analysis

```text
Input:
"Identify the flooded area."

Expected:
Geospatial / Environmental Analysis
      ↓
Flood Detection / Analysis
      ↓
Spatial Result
```

---

### Test 9 — Unsupported Task

```text
Input:
Unsupported analysis request

Expected:
UNSUPPORTED
```

---

### Test 10 — Model Failure

```text
Valid request
      ↓
Valid data
      ↓
Execution Plan
      ↓
Model Failure

Expected:
MODEL_ERROR
      ↓
Recovery / Retry / Fallback / Abort
```

---

# 27. Phase 2 → Phase 3 Integration Boundary

## Phase 2 provides

```text
Structured Query
Task
Data Requirements
Model Requirements
Execution Plan
Expected Output
Error / Status Contracts
```

## Phase 3 provides

```text
Model Selection
Model Loading
Preprocessing Implementation
Inference
Postprocessing
Actual Analysis Pipelines
Model Optimization
```

The handoff is:

```text
                 PHASE 2
                    │
             Execution Plan
                    │
                    ▼
              ┌──────────┐
              │ PHASE 3  │
              │          │
              │  Models  │
              │    ↓     │
              │ Inference│
              └──────────┘
```

---

# 28. Integration Principles

1. **Each engine communicates through defined contracts.**
2. **No engine should depend on another engine's internal implementation.**
3. **The orchestrator routes information but does not duplicate engine logic.**
4. **Blocking requirements prevent execution.**
5. **Clarification returns the request to requirement evaluation.**
6. **Data readiness must be established before model execution.**
7. **Execution Plan is the Phase 2 → Phase 3 handoff.**
8. **Spatial results must remain structured and independent of frontend rendering.**
9. **Errors must preserve their source and stage.**
10. **Every request must be traceable end-to-end.**
11. **The simplest capable pipeline should be preferred.**
12. **Unsupported requests must be explicitly rejected.**

---

# 29. Team Integration Boundaries

### Leo — Backend

Responsible for implementing the backend/API orchestration around the defined contracts.

Integration points:

```text
API
 ↓
Query Engine
 ↓
Task Engine
 ↓
Data Engine
 ↓
Model Engine
 ↓
Response
```

---

### Rubin — Data Engine

Responsible for implementing:

```text
Data Requirements
        ↓
Data Validation
        ↓
Data Readiness
```

---

### Prithi — Frontend

Responsible for:

```text
User Input
    ↓
Request
    ↓
Status Display
    ↓
Clarification Interaction
    ↓
Result Display
```

---

### Vignesh — Map / Spatial

Responsible for:

```text
Spatial Analysis Result
        ↓
Map Representation
        ↓
MapLibre Visualization
```

---

### Jack — Testing

Responsible for validating:

* Normal flows
* Clarification flows
* Missing-data flows
* Error flows
* Engine integration
* End-to-end scenarios

---

### Nian — Tech Lead

Responsible for:

* Contract consistency
* Architecture integrity
* Cross-engine integration
* Boundary enforcement
* Phase 2 → Phase 3 handoff
* Integration review
* Final architecture approval

---

# 30. Definition of Done

* [x] Complete request lifecycle defined
* [x] Query Engine integration defined
* [x] Task Engine integration defined
* [x] Data Engine integration defined
* [x] Data readiness flow defined
* [x] Execution Plan integration defined
* [x] Model Engine integration defined
* [x] Response Engine integration defined
* [x] Clarification flow defined
* [x] Missing-data flow defined
* [x] Multi-observation flow defined
* [x] Model failure flow defined
* [x] Frontend integration defined
* [x] Spatial/map integration defined
* [x] Backend integration defined
* [x] End-to-end state flow defined
* [x] Traceability defined
* [x] Integration test scenarios defined
* [x] Phase 2 → Phase 3 boundary defined
* [x] Team integration responsibilities defined
* [x] Integration principles defined

---

## Status : FINALIZED