# SatQuery AI — Phase 2 Step 7: Task Engine Architecture & Execution Plan


**Status:** Finalized
**Owner:** Nian — Tech Lead / System Architect

---

## 1. Purpose

The Task Engine is the decision-making layer that converts the **Structured Query** produced by the Query Engine into a defined **SatQuery task, requirements, analysis pipeline, and execution plan**.

It connects query understanding with data readiness and the Phase 3 Model Engine.

```text
User Query
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
Phase 3 Model Engine
```

---

# 2. Task Engine Responsibility

The Task Engine determines:

* What task the user is requesting
* What requirements that task has
* What information/data is required
* What model capabilities are required
* What logical analysis pipeline should be used
* Whether clarification is required
* Whether the request is ready for execution
* What execution plan should be passed toward Phase 3

The Task Engine **does not implement or execute individual ML models**.

---

# 3. Component Boundary

```text
┌────────────────────┬──────────────────────────────┐
│ Component          │ Responsibility               │
├────────────────────┼──────────────────────────────┤
│ Query Engine       │ Understand the user query    │
│ Task Engine        │ Determine task and plan      │
│ Data Engine        │ Validate actual data         │
│ Model Engine       │ Execute ML capabilities      │
│ Response Engine    │ Produce user-facing response │
└────────────────────┴──────────────────────────────┘
```

### Boundary principle

> **Task Engine decides what needs to happen; Data Engine decides whether the available data is suitable; Model Engine decides how the required ML capability is executed.**

---

# 4. Input Contract

The Task Engine receives the Structured Query from the Query Engine.

Example:

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

The Task Engine uses this information to determine the appropriate task and requirements.

---

# 5. Task Engine Processing Pipeline

```text
Structured Query
       ↓
Validate Query
       ↓
Identify Task
       ↓
Map Task → Requirements
       ↓
Check Missing Requirements
       ↓
Determine Data Requirements
       ↓
Determine Model Capabilities
       ↓
Select Logical Pipeline
       ↓
Generate Execution Plan
```

---

# 6. Task Identification

The Task Engine maps the Structured Query to the task taxonomy defined in Phase 2 Step 2.

### Task Families

```text
1. Spatial Object Analysis

2. Satellite Image Understanding

3. Multi-Observation Analysis

4. Geospatial / Environmental Analysis

5. VLM-Assisted Satellite Reasoning
```

Example:

```text
"How many buildings are in this image?"
              ↓
Spatial Object Analysis
              ↓
Object Counting
```

Another example:

```text
"What changed between these two images?"
              ↓
Multi-Observation Analysis
              ↓
Change Analysis
```

---

# 7. Task → Requirement Mapping

Once the task is identified, the Task Engine retrieves its requirements.

For example:

```text
Object Counting
      │
      ├── Minimum observations: 1
      ├── Image/raster: required
      ├── Compatible modality: required
      ├── Target object: required
      ├── Valid data: required
      ├── Sufficient resolution: required
      │
      └── Model capability:
             Object Detection + Counting
```

The Task Engine should use the predefined Phase 2 requirements rather than inventing new requirements during execution.

---

# 8. Missing Requirement Evaluation

The Task Engine compares:

```text
Required Information
        VS
Available Information
```

Example:

```text
Task: Change Analysis

Required:
✓ Observation 1
✗ Observation 2
✓ Compatible spatial coverage
✓ Temporal relationship

Result:
NEEDS_CLARIFICATION
```

The Task Engine must stop the execution flow and return a clarification requirement.

```json
{
  "status": "needs_clarification",
  "missing_information": [
    "second_observation"
  ],
  "question": "Please provide the second satellite image."
}
```

This follows the rules defined in Step 6.

---

# 9. Data Engine Handoff

After determining what data is required, the Task Engine passes the requirements to the Data Engine.

```text
Task Engine
     ↓
Data Requirements
     ↓
Data Engine
     ↓
Data Readiness
```

### Responsibility distinction

**Task Engine:**

> What data does this task require?

**Data Engine:**

> Does the available data satisfy those requirements?

The Task Engine should not independently determine whether a raster's actual quality, resolution, or spatial compatibility is sufficient.

---

# 10. Model Capability Requirements

The Task Engine determines the required **capabilities**, not the specific model.

Example:

```text
"Find all buildings and show where they are."
                    ↓
             Spatial Object Analysis
                    ↓
        ┌───────────┴───────────┐
        ↓                       ↓
Object Detection        Visual Grounding
```

The Task Engine should not select:

```text
YOLO
SAM
specific VLM
specific checkpoint
specific model version
```

Actual model selection and integration belong to Phase 3.

---

# 11. Logical Pipeline Selection

The Task Engine selects the **logical analysis pipeline** required by the task.

It does not select the implementation-specific ML model.

### Object Counting

```text
Image
  ↓
Object Detection
  ↓
Detected Instances
  ↓
Count
  ↓
Result
```

### Visual Grounding

```text
Image
  ↓
Object Detection / Grounding
  ↓
Target Locations
  ↓
Spatial Result
```

### Change Analysis

```text
Observation A
       +
Observation B
       ↓
Alignment / Normalization
       ↓
Change Analysis
       ↓
Changed Regions
       ↓
Interpretation
```

---

# 12. Execution Plan

When all required information and data are ready, the Task Engine produces an execution plan.

### Execution Plan Schema

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

---

# 13. Execution Plan Fields

| Field                   | Purpose                                       |
| ----------------------- | --------------------------------------------- |
| `task`                  | Identified SatQuery task                      |
| `input_observations`    | Observation references required for execution |
| `required_modalities`   | Modalities required by the task               |
| `temporal_requirements` | Temporal information needed                   |
| `spatial_requirements`  | Spatial constraints needed                    |
| `preprocessing`         | Required preprocessing category               |
| `model_requirements`    | Required model capabilities                   |
| `expected_output`       | Expected result structure/type                |

Actual model names, checkpoints, and implementation details are not part of the Phase 2 execution plan.

---

# 14. Execution Readiness Flow

```text
Structured Query
       ↓
Task Identification
       ↓
Task Requirements
       ↓
Requirements Satisfied?
       │
   ┌───┴────┐
  NO        YES
   │          │
   ↓          ↓
Clarify    Data Requirements
              ↓
          Data Engine
              ↓
          Data Ready?
          │       │
         NO      YES
          │       │
          ↓       ↓
      NOT_READY  Execution Plan
                    ↓
              Phase 3 Model Engine
```

---

# 15. Task Engine States

The Task Engine uses explicit processing states.

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
```

Possible alternative states:

```text
NEEDS_CLARIFICATION
NOT_READY
UNSUPPORTED
```

### State meanings

**RECEIVED**
Structured Query has entered the Task Engine.

**VALIDATING**
The Structured Query is checked for required structural information.

**TASK_IDENTIFIED**
A SatQuery task has been determined.

**REQUIREMENTS_CHECKED**
Task requirements have been evaluated.

**WAITING_FOR_DATA**
The Data Engine must validate or provide required data.

**READY**
All execution prerequisites are satisfied.

**EXECUTION_PLANNED**
A valid execution plan has been produced.

**NEEDS_CLARIFICATION**
Required information is missing or ambiguous.

**NOT_READY**
Required data is unavailable or unsuitable.

**UNSUPPORTED**
The requested task/capability is outside the supported system scope.

---

# 16. Clarification Handling

If required information is unresolved:

```text
Task Engine
    ↓
NEEDS_CLARIFICATION
    ↓
No Model Execution
    ↓
User Clarification
    ↓
Update Structured Query
    ↓
Re-evaluate Requirements
```

Example:

```text
User:
"How many objects are here?"
```

If the target cannot be determined:

```text
target_object → ambiguous
```

Response:

> "Which objects should I count?"

After:

> "Buildings."

The Structured Query is updated and the Task Engine processes it again.

---

# 17. Simplest-Capable-Path Rule

SatQuery should use the **simplest pipeline capable of satisfying the request**.

Example:

```text
"What is in this image?"
        ↓
General Image Understanding
        ↓
General VLM
```

A specialized satellite-analysis pipeline should not be invoked unnecessarily.

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

This keeps the architecture efficient and avoids unnecessary model processing.

---

# 18. Example — Object Counting

### User Query

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

### Requirements

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

### Phase 3

The Model Engine selects and executes the appropriate models.

---

# 19. Example — Missing Observation

### User Query

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

# 20. Example — Multi-Observation Analysis

### User Query

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

# 21. End-to-End Task Engine Architecture

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
                  │                 │
                  │ Task Identify   │
                  │ Requirements    │
                  │ Capability      │
                  │ Pipeline        │
                  │ Planning        │
                  └────────┬────────┘
                           │
                    Data Requirements
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
                  │    Phase 3      │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Response Engine │
                  └─────────────────┘
```

---

# 22. Integration Contracts

### Query Engine → Task Engine

**Input:** Structured Query

**Output:** Task identification and requirement evaluation.

---

### Task Engine → Data Engine

**Input:** Data Requirements

**Output:** Data Readiness

---

### Task Engine → Model Engine

**Input:** Execution Plan

**Output:** Model execution request in Phase 3.

---

### Task Engine → Frontend / Interaction Layer

When clarification is required:

**Input:**

```json
{
  "status": "needs_clarification",
  "missing_information": [
    "target_object"
  ],
  "question": "Which objects should I look for?"
}
```

---

# 23. Architectural Rules

1. **Task Engine does not execute ML models.**
2. **Task Engine does not directly validate raster suitability.**
3. **Data Engine owns actual data readiness.**
4. **Model Engine owns model selection and execution in Phase 3.**
5. **Execution is blocked when required information is unresolved.**
6. **Clarification updates the existing Structured Query.**
7. **Requirements are evaluated again after clarification.**
8. **Logical pipeline selection occurs before model implementation.**
9. **The simplest capable pipeline should be preferred.**
10. **Unsupported tasks must not be silently converted into unrelated tasks.**

---

# 24. Definition of Done

* [x] Task Engine responsibility defined
* [x] Structured Query → Task flow defined
* [x] Task taxonomy integration defined
* [x] Task → Requirement mapping defined
* [x] Missing requirement handling defined
* [x] Data Engine boundary defined
* [x] Model capability boundary defined
* [x] Logical pipeline selection defined
* [x] Execution Plan schema defined
* [x] Task Engine states defined
* [x] Clarification handling defined
* [x] Simplest-capable-path rule defined
* [x] End-to-end orchestration documented
* [x] Integration contracts defined
* [x] Phase 3 handoff defined

---

## Status : FINALIZED**

