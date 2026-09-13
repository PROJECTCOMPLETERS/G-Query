# SatQuery AI — Phase 2 Step 12: Team Handoff & Implementation Contracts

**Status:** FINALIZED
**Owner:** Nian — Tech Lead / System Architect
**Phase:** Phase 2 — Architecture & Planning
**Purpose:** Convert the approved Phase 2 architecture into clear implementation contracts and team responsibilities.

---

## 1. Purpose

Steps 1–11 established the SatQuery AI architecture, task taxonomy, data requirements, model requirements, execution planning, orchestration, error handling, and end-to-end flow.

Step 12 formally hands this architecture to the implementation team.

The purpose is to ensure that every team member knows:

* What they are responsible for
* What they receive from other components
* What they must produce
* Which contracts they must follow
* Where their responsibility ends
* Which decisions they must not make independently

**Step 12 does not implement the engines. It locks the implementation boundaries and contracts.**

---

# 2. Final Phase 2 Architecture

```text
                         USER
                           │
                           ▼
                    ┌─────────────┐
                    │ Query Engine│
                    └──────┬──────┘
                           │
                  Structured Query
                           │
                           ▼
                    ┌─────────────┐
                    │ Task Engine │
                    └──────┬──────┘
                           │
                  Task + Requirements
                           │
                           ▼
                    ┌─────────────┐
                    │ Data Engine │
                    └──────┬──────┘
                           │
                     Data Readiness
                           │
                           ▼
                  Execution Plan
                           │
                           ▼
                    ┌─────────────┐
                    │ Model Engine│
                    │   Phase 3   │
                    └──────┬──────┘
                           │
                     Analysis Result
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
      Response Engine              Spatial Output
             │                           │
             ▼                           ▼
           USER                       MapLibre
```

The **orchestrator/backend** coordinates these transitions.

Individual engines must not bypass the defined architecture.

---

# 3. Canonical Contract Principles

All cross-component communication must follow these principles.

### 3.1 One contract per boundary

The following contracts are canonical:

```text
Query Engine
     ↓
Structured Query

Task Engine
     ↓
Data Requirements

Data Engine
     ↓
Data Readiness

Task Engine
     ↓
Execution Plan

Model Engine
     ↓
Analysis Result
```

Clarification and error contracts apply across the appropriate boundaries.

---

# 4. Canonical Request Identification

Every request should have a unique:

```text
request_id
```

The `request_id` is used to trace:

```text
request
  ↓
structured query
  ↓
task
  ↓
data readiness
  ↓
execution plan
  ↓
model execution
  ↓
analysis result
  ↓
response
```

This provides end-to-end traceability for debugging, testing, and monitoring.

---

# 5. Canonical Observation References

Actual image/raster data must **not** be embedded inside the Structured Query.

The query should reference observations using IDs.

Example:

```json
{
  "input_id": "obs_001",
  "type": "image"
}
```

The actual data is resolved by the Data Engine.

The same observation references must remain consistent through the pipeline.

```text
Structured Query
      ↓
obs_001
      ↓
Data Engine
      ↓
Execution Plan
      ↓
Model Engine
```

This prevents engines from becoming tightly coupled to physical file storage.

---

# 6. Contract Versioning

Cross-engine contracts should include a schema version.

Example:

```json
{
  "schema_version": "1.0"
}
```

This allows contracts to evolve without silently breaking existing components.

Contract changes should be reviewed by the Tech Lead before becoming integration requirements.

---

# 7. Structured Query Contract

The Query Engine produces the canonical Structured Query.

```json
{
  "schema_version": "1.0",
  "request_id": "req_001",
  "question": "How many buildings are in this image?",
  "intent": "object_counting",
  "entities": [],
  "inputs": [
    {
      "input_id": "obs_001",
      "type": "image"
    }
  ],
  "modality": null,
  "temporal": {
    "required": false,
    "information": null
  },
  "spatial": {
    "required": false,
    "information": null
  },
  "requested_capabilities": [
    "object_detection",
    "counting"
  ],
  "missing_information": []
}
```

### Query Engine owns

* Natural-language interpretation
* Intent
* Entity extraction
* Input references
* Modality information
* Temporal information
* Spatial information
* Requested capabilities
* Missing/ambiguous information

### Query Engine does not own

* ML inference
* Model selection
* Actual data validation
* Model execution
* Final spatial rendering

---

# 8. Data Requirements Contract

The Task Engine converts the task into data requirements.

Example:

```json
{
  "schema_version": "1.0",
  "request_id": "req_001",
  "task": "object_counting",
  "inputs": {
    "min_observations": 1,
    "type": "image"
  },
  "modality": {
    "required": true,
    "allowed": ["compatible"]
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

### Task Engine owns

* Determining requirements
* Determining required inputs
* Determining required capabilities
* Determining whether missing information blocks execution

### Data Engine owns

* Checking actual data
* Checking validity
* Checking compatibility
* Checking resolution/quality
* Checking spatial compatibility
* Checking temporal suitability

---

# 9. Data Readiness Contract

The Data Engine returns whether the available data can satisfy the requirements.

Example:

```json
{
  "schema_version": "1.0",
  "request_id": "req_001",
  "ready": true,
  "available_observations": [
    "obs_001"
  ],
  "missing_information": [],
  "reason": null
}
```

If data is unavailable:

```json
{
  "schema_version": "1.0",
  "request_id": "req_002",
  "ready": false,
  "available_observations": [
    "obs_001"
  ],
  "missing_information": [
    "second_observation"
  ],
  "reason": "A second observation is required for change analysis."
}
```

### Important distinction

```text
User information missing
        ↓
NEEDS_CLARIFICATION

Required data unavailable
        ↓
NOT_READY
```

These must not be treated as the same condition.

---

# 10. Execution Plan Contract

Once requirements and data readiness are satisfied, the Task Engine creates the Execution Plan.

```json
{
  "schema_version": "1.0",
  "request_id": "req_001",
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

The Execution Plan defines **what must be executed**, not the implementation of the individual model.

---

# 11. Model Engine Boundary

The Model Engine is primarily a **Phase 3 implementation responsibility**.

Phase 2 provides:

```text
Task
 ↓
Required Capability
 ↓
Input Requirements
 ↓
Preprocessing Category
 ↓
Expected Output
```

Phase 3 determines:

```text
Required Capability
       ↓
Actual Model
       ↓
Model Loading
       ↓
Preprocessing
       ↓
Inference
       ↓
Postprocessing
```

Phase 2 must not hard-code specific models such as YOLO, SAM, or a particular VLM as architectural requirements.

---

# 12. Analysis Result Contract

The Model Engine returns an analysis result.

Conceptually:

```json
{
  "schema_version": "1.0",
  "request_id": "req_001",
  "status": "completed",
  "task": "object_counting",
  "result": {
    "type": "count",
    "target": "building",
    "count": 42
  },
  "spatial_output": null,
  "metadata": {}
}
```

For spatial tasks, the result may additionally contain a structured spatial output.

The exact spatial representation must be standardized during implementation before MapLibre integration.

---

# 13. Clarification Contract

When required information is missing or ambiguous:

```json
{
  "schema_version": "1.0",
  "request_id": "req_001",
  "status": "needs_clarification",
  "missing_information": [
    "target_object"
  ],
  "question": "Which objects should I count?"
}
```

Clarification is a normal control-flow state.

It is **not an error**.

```text
User Query
    ↓
Missing Required Information
    ↓
NEEDS_CLARIFICATION
    ↓
User Answer
    ↓
Update Structured Query
    ↓
Re-evaluate Requirements
```

---

# 14. Error Contract

All engines should return structured errors.

```json
{
  "schema_version": "1.0",
  "request_id": "req_001",
  "status": "failed",
  "error": {
    "code": "DATA_INSUFFICIENT",
    "message": "The provided observation does not contain sufficient resolution.",
    "stage": "data_engine",
    "recoverable": false
  }
}
```

Canonical error categories:

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

---

# 15. Status Lifecycle

The overall request lifecycle should follow the architecture:

```text
RECEIVED
   ↓
VALIDATING
   ↓
TASK_IDENTIFIED
   ↓
REQUIREMENTS_CHECKED
   ↓
WAITING_FOR_DATA
   ↓
READY
   ↓
EXECUTION_PLANNED
   ↓
EXECUTING
   ↓
COMPLETED
```

Alternative states:

```text
NEEDS_CLARIFICATION
NOT_READY
UNSUPPORTED
FAILED
```

The **orchestrator owns the overall request lifecycle**.

Individual engines may maintain their own internal states, but they must not create conflicting interpretations of the global request status.

---

# 16. Retry, Idempotency & Recovery

Retries should only be used for failures that are potentially recoverable.

Examples:

```text
Temporary service failure → RETRY
Model loading timeout     → RETRY
Invalid user input        → DO NOT RETRY
Unsupported task          → DO NOT RETRY
Invalid raster            → DO NOT RETRY
```

The backend/orchestrator should ensure that retrying a request does not unintentionally duplicate operations.

Fallback is allowed only when the alternative still satisfies the user's intended task.

No unrelated capability may be silently substituted.

---

# 17. Team Handoff — Leo

## Leo — Backend / Orchestration

### Owns

* Backend API
* Request lifecycle
* Orchestration
* Cross-engine communication
* Contract implementation
* Request IDs
* Status management
* Error propagation
* Retry/recovery behavior
* Integration layer

### Receives

```text
User request
Structured Query
Task requirements
Data readiness
Execution plan
Model result
```

### Produces

```text
API responses
Orchestration
Clarification responses
Execution routing
Error responses
```

### Must preserve

```text
Query Engine → Task Engine
Task Engine → Data Engine
Data Engine → Task Engine
Task Engine → Model Engine
Model Engine → Response Engine
```

Leo should **not move ML logic into the backend orchestration layer**.

---

# 18. Team Handoff — Rubin

## Rubin — Data Engine

### Owns

* Data ingestion/access
* Observation resolution
* Data validation
* Raster/image validity
* Modality compatibility
* Spatial compatibility
* Temporal suitability
* Data quality/readiness
* Data preprocessing requirements from the data side

### Receives

```text
Data Requirements
Observation IDs
```

### Produces

```text
Data Readiness
Available observations
Missing/unusable data
Data validation results
```

Rubin should not determine which ML model is used.

---

# 19. Team Handoff — Prithi

## Prithi — Frontend

### Owns

* Query input interface
* Sending user requests
* Displaying clarification questions
* Receiving clarification answers
* Displaying status
* Displaying analysis results
* Displaying errors
* General result presentation

### Frontend flow

```text
User
 ↓
Query
 ↓
Backend
 ↓
Status
 ↓
Clarification / Result / Error
 ↓
User
```

Prithi should not implement Task Engine or Model Engine logic in the frontend.

---

# 20. Team Handoff — Vignesh

## Vignesh — MapLibre / Spatial Visualization

### Owns

* MapLibre integration
* Spatial result visualization
* Map layers
* Spatial feature rendering
* Interaction with spatial outputs

### Receives

```text
Analysis Result
        ↓
Spatial Output
```

### Produces

```text
Map visualization
Spatial layers
Interactive geographic results
```

The spatial representation must be agreed upon with Nian and Leo before final integration.

---

# 21. Team Handoff — Jack

## Jack — Testing / QA

### Owns

Testing the defined architecture and contracts.

### Required test categories

```text
1. Normal query
2. Query ambiguity
3. Missing information
4. Missing observation
5. Invalid data
6. Unsupported task
7. Multi-observation query
8. Model failure
9. Pipeline failure
10. Response failure
11. End-to-end integration
12. Spatial result flow
```

### Important tests

```text
"How many buildings?"
        ↓
Object Detection + Counting

"Where are the buildings?"
        ↓
Object Detection + Visual Grounding

"What changed?"
        ↓
Requires multiple observations

"Which objects should I count?"
        ↓
Clarification

Second image unavailable
        ↓
NOT_READY
```

Jack should test against the **contracts**, not implementation assumptions.

---

# 22. Team Handoff — Nian

## Nian — Tech Lead / System Architect

Nian owns the architectural integrity of the entire system.

### Responsibilities

* Maintain architecture consistency
* Maintain canonical contracts
* Review cross-engine interfaces
* Resolve architectural conflicts
* Prevent responsibility leakage
* Review integration
* Approve contract changes
* Coordinate team boundaries
* Validate Phase 2 → Phase 3 handoff
* Ensure implementation follows the approved architecture

### Nian does not need to implement every engine.

The role is:

```text
Define
   ↓
Coordinate
   ↓
Review
   ↓
Integrate
   ↓
Approve
```

---

# 23. Responsibility Matrix

| Area         | Nian                | Leo       | Rubin        | Prithi  | Vignesh | Jack     |
| ------------ | ------------------- | --------- | ------------ | ------- | ------- | -------- |
| Architecture | **Own**             | Support   | Support      | Support | Support | Support  |
| Query Engine | **Define/Review**   | Integrate | —            | —       | —       | Test     |
| Task Engine  | **Define/Review**   | Integrate | —            | —       | —       | Test     |
| Data Engine  | Define requirements | Integrate | **Own**      | —       | —       | Test     |
| Backend      | Review              | **Own**   | Support      | Support | Support | Test     |
| Frontend     | Review              | Support   | —            | **Own** | —       | Test     |
| MapLibre     | Review              | Support   | Spatial data | —       | **Own** | Test     |
| Model Engine | Define requirements | Integrate | Data support | —       | —       | Test     |
| Testing      | Define expectations | Support   | Support      | Support | Support | **Own**  |
| Contracts    | **Own**             | Implement | Implement    | Consume | Consume | Validate |
| Integration  | **Own**             | **Own**   | Support      | Support | Support | Validate |

---

# 24. Rules for Team Collaboration

### Rule 1 — No silent contract changes

If an implementation requires changing a contract, the change must be reviewed before being adopted.

### Rule 2 — No responsibility leakage

```text
Query Engine ≠ Model Engine
Task Engine ≠ Data Engine
Data Engine ≠ Model Engine
Frontend ≠ Backend orchestration
MapLibre ≠ Analysis Engine
```

### Rule 3 — Orchestrator controls routing

Engines should not independently call unrelated engines and create hidden dependencies.

### Rule 4 — Capability before model

The architecture specifies:

```text
"object_detection"
```

not:

```text
"YOLO"
```

during Phase 2.

### Rule 5 — Clarification is not failure

Missing user information should enter clarification flow.

### Rule 6 — Data unavailable is different from user information missing

```text
NEEDS_CLARIFICATION ≠ NOT_READY
```

### Rule 7 — Every request must be traceable

`request_id` must follow the request throughout the pipeline.

---

# 25. Spatial Output Handoff

Spatial analysis requires a common representation between Model/Analysis Engine and MapLibre.

The implementation team must finalize:

```text
Spatial output type
        ↓
Geometry representation
        ↓
Coordinate reference
        ↓
Feature properties
        ↓
Confidence
        ↓
Layer metadata
```

The exact representation is an **implementation contract to be finalized before spatial integration**, rather than being assumed independently by Vignesh or the Model Engine.

---

# 26. Implementation Sequence

The team should not all begin by independently implementing everything.

Recommended sequence:

```text
        Nian
         │
         ▼
Canonical Contracts
         │
         ▼
       Leo
Backend + Orchestration
         │
    ┌────┴────┐
    ▼         ▼
 Rubin      Prithi
Data        Frontend
Engine
    │         │
    └────┬────┘
         ▼
     Integration
         │
         ▼
      Vignesh
     Map/Spatial
         │
         ▼
       Jack
     Integration
       Testing
         │
         ▼
        Nian
   Architecture Review
         │
         ▼
     Phase 3 Model
       Integration
```

This is a coordination sequence, not a strict requirement that every person's work be completely sequential.

---

# 27. Phase 2 → Phase 3 Boundary

Phase 2 finishes at:

```text
User Query
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
```

Phase 3 begins with:

```text
Execution Plan
     ↓
Model Selection
     ↓
Model Loading
     ↓
Preprocessing
     ↓
Inference
     ↓
Postprocessing
     ↓
Analysis Result
```

Therefore:

> **Phase 2 defines what must happen. Phase 3 implements how the ML analysis happens.**

---

# 28. Final Implementation Checklist

### Architecture

* [x] Architecture approved
* [x] Engine boundaries defined
* [x] Task taxonomy defined
* [x] Query → Task mapping defined
* [x] Data requirements defined
* [x] Model requirements defined
* [x] Clarification rules defined
* [x] Execution plan defined
* [x] Orchestration defined
* [x] Error handling defined
* [x] End-to-end flow defined

### Contracts

* [x] Structured Query
* [x] Data Requirements
* [x] Data Readiness
* [x] Execution Plan
* [x] Clarification
* [x] Error
* [x] Request identification
* [x] Observation references
* [x] Status lifecycle
* [x] Contract versioning

### Team Handoff

* [x] Leo responsibilities defined
* [x] Rubin responsibilities defined
* [x] Prithi responsibilities defined
* [x] Vignesh responsibilities defined
* [x] Jack responsibilities defined
* [x] Nian responsibilities defined
* [x] Integration boundaries defined

### Remaining implementation decisions

* [ ] Final API endpoint definitions
* [ ] Exact spatial output schema
* [ ] Sync/async execution behavior
* [ ] Concrete retry/idempotency implementation
* [ ] Authentication/access handling
* [ ] Detailed observability/metrics

These are implementation-level decisions and **do not invalidate the Phase 2 architecture**.

---

# 29. Final Decision

**SatQuery AI Phase 2 architecture is finalized and ready for implementation handoff.**

The team now has:

```text
Architecture
     +
Contracts
     +
Responsibilities
     +
Integration Rules
     +
Error/Clarification Rules
     +
Execution Boundary
     ↓
IMPLEMENTATION READY
```

### Phase 2 Status

> **FINALIZED — TEAM HANDOFF APPROVED**

### Next Phase

**Implementation begins with the agreed contracts and backend/orchestration foundation, followed by Data Engine, Frontend, Spatial integration, testing, and finally Phase 3 Model Engine integration.**

---

# Data Engine → Model Engine Handoff Addendum

The Data Engine now exposes a generic handoff builder through
`data_engine.model_input.build_model_input()`.

The contract contains:

* `schema_version`
* `observation_id`
* `input.type`
* `input.path` for a prepared raster when available
* `input.tensor` when a later model-specific pipeline has produced one
* validated raster/spatial/acquisition metadata
* executed preprocessing operations

The Data Engine does **not** decide model-specific tensor layout, channel
ordering, normalization statistics, tiling, model loading, or inference.
Those decisions remain with the Phase 3 Model Engine. The generic contract
therefore supports a prepared raster handoff immediately while allowing the
Phase 3 pipeline to attach a tensor once its exact representation is fixed.

For spatial preparation, the generic Data Engine execution layer now provides
reprojection, resolution resampling, grid alignment to a reference raster,
and generic percentile-based numeric normalization. These are reusable raster
operations, not model-specific preprocessing.
