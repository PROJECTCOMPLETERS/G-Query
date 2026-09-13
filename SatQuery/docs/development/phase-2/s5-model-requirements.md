# SatQuery AI — Phase 2 Step 5: Model Requirements


**Owner:** Nian — Tech Lead / System Architect
**Phase:** Phase 2 — Query Understanding & Task Routing

---

## 1. Purpose

This document defines the **model requirements for each SatQuery task** before model execution.

The purpose is to establish a clear contract between the **Phase 2 Task Engine** and the **Phase 3 Model Engine**.

The architecture separates responsibilities:

* **Query Engine:** understands the user's request.
* **Task Engine:** determines the required task and capabilities.
* **Data Engine:** determines whether the available data satisfies the requirements.
* **Model Engine:** selects and executes the appropriate model or analysis pipeline.
* **Response Engine:** converts results into a user-facing response.

Phase 2 defines **what capability is required**. Phase 3 determines **which model or pipeline provides that capability**.

---

# 2. Model Requirement Principles

For each task, model requirements describe:

1. Required capability
2. Required modality
3. Number of inputs
4. Input format
5. Preprocessing requirements
6. Target/objective
7. Expected output
8. Confidence information when supported

Conceptually:

```text
Task
  ↓
Required Modality
  ↓
Number of Inputs
  ↓
Input Format
  ↓
Preprocessing
  ↓
Required Capability
  ↓
Expected Output
```

---

# 3. Capability vs Model

Phase 2 defines **capabilities**, not specific models.

### Phase 2

```text
Task
 ↓
Required capability
```

Examples:

* Object Detection
* Object Identification
* Counting
* Visual Grounding
* Classification
* Change Detection
* Image Comparison
* Satellite VQA

### Phase 3

```text
Required Capability
        ↓
   Model Engine
        ↓
 Select suitable model
        ↓
 Preprocess
        ↓
 Execute
        ↓
 Return result
```

Specific model selection, integration, and execution belong to Phase 3.

---

# 4. Spatial Object Analysis

## 4.1 Object Detection

**Goal:** Detect instances of a specified object or object category.

### Model requirements

| Requirement         | Definition                                    |
| ------------------- | --------------------------------------------- |
| Required capability | Object Detection                              |
| Required modality   | Compatible with input observation             |
| Number of inputs    | ≥1                                            |
| Input format        | Image/raster                                  |
| Preprocessing       | Model/pipeline-specific                       |
| Target              | Object category specified by query            |
| Expected output     | Detected object instances + spatial locations |
| Confidence          | When supported                                |

### Example

Query:

> “Find all buildings in this satellite image.”

```json
{
  "task": "object_detection",
  "required_capabilities": [
    "object_detection"
  ],
  "inputs": {
    "count": 1,
    "format": "image"
  },
  "target": "building",
  "expected_output": {
    "detections": true,
    "locations": true
  }
}
```

### Expected output

```text
Detection
├── object/class
├── location
└── confidence (if available)
```

---

# 5. Object Identification

## 5.1 Object Identification

**Goal:** Determine what an observed object is.

### Model requirements

| Requirement         | Definition                        |
| ------------------- | --------------------------------- |
| Required capability | Object Identification             |
| Required modality   | Compatible with input observation |
| Number of inputs    | ≥1                                |
| Input format        | Image/raster                      |
| Preprocessing       | Model/pipeline-specific           |
| Target              | Object/category to identify       |
| Expected output     | Identified object/category        |
| Confidence          | When supported                    |

### Example

Query:

> “Identify the objects visible in this image.”

```json
{
  "task": "object_identification",
  "required_capabilities": [
    "object_identification"
  ],
  "inputs": {
    "count": 1,
    "format": "image"
  },
  "expected_output": {
    "identified_objects": true
  }
}
```

### Expected output

```text
Object Identification
├── Object/category
└── Confidence (if supported)
```

---

# 6. Object Counting

## 6.1 Object Counting

**Goal:** Determine how many instances of a target object are present.

### Model requirements

| Requirement           | Definition                        |
| --------------------- | --------------------------------- |
| Required capability   | Object Counting                   |
| Supporting capability | Object Detection                  |
| Required modality     | Compatible with input observation |
| Number of inputs      | ≥1                                |
| Input format          | Image/raster                      |
| Preprocessing         | Model/pipeline-specific           |
| Target                | Object/category to count          |
| Expected output       | Object instances + total count    |
| Confidence            | When supported                    |

### Example

Query:

> “How many buildings are in this satellite image?”

```json
{
  "task": "object_counting",
  "required_capabilities": [
    "object_detection",
    "counting"
  ],
  "inputs": {
    "count": 1,
    "format": "image"
  },
  "target": "building",
  "expected_output": {
    "detections": true,
    "count": true
  }
}
```

### Processing concept

```text
Image
  ↓
Object Detection
  ↓
Individual Instances
  ↓
Counting
  ↓
Total Count
```

---

# 7. Visual Grounding

## 7.1 Visual Grounding

**Goal:** Connect a user-referenced object or concept to its spatial location within an image.

### Model requirements

| Requirement         | Definition                        |
| ------------------- | --------------------------------- |
| Required capability | Visual Grounding                  |
| Required modality   | Compatible with input observation |
| Number of inputs    | ≥1                                |
| Input format        | Image/raster                      |
| Preprocessing       | Model/pipeline-specific           |
| Target              | User-referenced object/concept    |
| Expected output     | Spatial location/region           |
| Confidence          | When supported                    |

### Example

Query:

> “Where are the buildings?”

```json
{
  "task": "visual_grounding",
  "required_capabilities": [
    "visual_grounding"
  ],
  "inputs": {
    "count": 1,
    "format": "image"
  },
  "target": "building",
  "expected_output": {
    "locations": true
  }
}
```

### Expected output

```text
Visual Grounding
├── Target
├── Spatial region/location
└── Confidence (if supported)
```

The exact spatial representation—such as bounding boxes, masks, or coordinates—is determined during the Model Engine output contract.

---

# 8. Satellite Image Understanding

## 8.1 Scene Understanding

**Goal:** Understand the overall scene represented by a satellite observation.

### Model requirements

* **Capability:** Scene/Image Understanding
* **Modality:** Compatible satellite/image modality
* **Inputs:** 1
* **Input:** Image/raster
* **Preprocessing:** Model/pipeline-specific
* **Output:** Scene-level description or interpretation

### Example

> “What is in this satellite image?”

```text
Satellite Image
      ↓
Scene Understanding
      ↓
Scene Interpretation
```

---

## 8.2 Image Classification

**Goal:** Assign an observation to a defined class/category.

### Model requirements

```text
Image Classification
│
├── Input: image/raster
├── Inputs: ≥1
├── Modality: compatible
├── Capability: classification
├── Target: classification objective/category
└── Output:
    ├── predicted class
    └── confidence (if supported)
```

---

## 8.3 Land-use / Land-cover Understanding

**Goal:** Determine or interpret land-use/land-cover information.

### Model requirements

```text
LULC Understanding
│
├── Input: image/raster
├── Inputs: ≥1
├── Modality: compatible
├── Capability: LULC understanding/classification
├── Target: LULC objective/category
└── Output:
    ├── land-use/land-cover interpretation
    └── confidence (if supported)
```

---

## 8.4 Satellite VQA

**Goal:** Answer a natural-language question about a satellite observation.

### Model requirements

| Requirement         | Definition                        |
| ------------------- | --------------------------------- |
| Required capability | Satellite VQA                     |
| Required modality   | Compatible with input observation |
| Number of inputs    | ≥1                                |
| Input format        | Image/raster + question           |
| Preprocessing       | Model/pipeline-specific           |
| Target              | User's question                   |
| Expected output     | Natural-language answer           |
| Confidence          | When supported                    |

Conceptually:

```text
Image
  +
Question
  ↓
Satellite VQA
  ↓
Answer
```

---

# 9. VLM-Assisted Satellite Reasoning

SatQuery may use VLM-assisted reasoning for satellite questions that do not require specialized processing.

The system should prefer the **simplest capable path**.

```text
Satellite Query
      ↓
Requires specialized capability?
      │
   ┌──┴──┐
  No     Yes
  ↓       ↓
 VLM   Specialized
       capability
```

This prevents ordinary satellite questions from unnecessarily requiring specialized processing.

---

# 10. Multi-Observation Analysis

## 10.1 Image Comparison

**Goal:** Compare two or more observations.

### Model requirements

* **Capability:** Image Comparison
* **Inputs:** ≥2
* **Input:** Multiple images/rasters
* **Modality:** Compatible modalities
* **Preprocessing:** Alignment/normalization when required
* **Spatial relationship:** Comparable areas
* **Output:** Similarities and/or differences

```text
Observation A ──┐
                ├──> Comparison
Observation B ──┘
```

---

## 10.2 Change Analysis

**Goal:** Identify changes between observations over time.

### Model requirements

```text
Change Analysis
│
├── Inputs: ≥2 observations
├── Modality: compatible
├── Temporal relationship: required
├── Spatial coverage: comparable
├── Capability: change detection/analysis
└── Output:
    ├── changed regions/features
    └── change description
```

---

## 10.3 Optical–Optical Comparison

### Model requirements

* ≥2 optical observations
* Optical-compatible processing
* Comparable spatial coverage
* Appropriate preprocessing/alignment when required
* Optical comparison capability
* Comparison result

---

## 10.4 SAR–SAR Comparison

### Model requirements

* ≥2 SAR observations
* SAR-compatible processing
* Comparable spatial coverage
* Appropriate preprocessing when required
* SAR comparison capability
* Comparison/change result

---

## 10.5 Optical–SAR Comparison

**Goal:** Compare optical and SAR observations.

### Model requirements

* ≥2 observations
* One optical observation
* One SAR observation
* Comparable spatial coverage
* Cross-modality comparison capability
* Modality-specific preprocessing when required
* Cross-modality interpretation/comparison output

```text
Optical Observation
       +
SAR Observation
       ↓
Cross-Modality Comparison
       ↓
Difference / Interpretation
```

---

# 11. Geospatial / Environmental Analysis

## 11.1 Flood Analysis

**Goal:** Detect or analyze flooded areas.

### Model requirements

* **Capability:** Flood Detection / Flood Analysis
* **Inputs:** ≥1
* **Input:** Image/raster
* **Modality:** Compatible
* **Target:** Flooded area
* **Preprocessing:** Capability/model-specific
* **Output:** Flooded regions/areas + analysis
* **Confidence:** When supported

```text
Satellite Observation
        ↓
Flood Analysis
        ↓
Flooded Region
```

---

## 11.2 Water Analysis

**Goal:** Identify or analyze water bodies.

### Model requirements

```text
Water Analysis
│
├── Input: image/raster
├── Inputs: ≥1
├── Modality: compatible
├── Capability: water detection/analysis
├── Target: water / water bodies
└── Output:
    ├── water regions/features
    └── confidence (if supported)
```

---

## 11.3 Surface / Land Analysis

**Goal:** Analyze land or surface characteristics.

### Model requirements

```text
Surface / Land Analysis
│
├── Input: image/raster
├── Inputs: ≥1
├── Modality: compatible
├── Capability: surface/land analysis
├── Target: query-defined
└── Output:
    └── surface/land interpretation
```

The exact capability depends on the user's analysis objective.

---

## 11.4 Other Satellite Analysis

Used for satellite-analysis requests that do not fit a more specific capability.

### Model requirements

```text
Other Satellite Analysis
│
├── Input: image/raster
├── Inputs: ≥1
├── Modality: compatible
├── Capability: determined by analysis objective
├── Target: query-defined
└── Output:
    └── analysis result
```

Phase 2 should not prescribe a specific model for this category.

---

# 12. Compound Capabilities

A single query can require multiple model capabilities.

### Example 1 — Counting

> “How many buildings are there?”

```text
Object Detection
        +
Counting
```

### Example 2 — Detection + Grounding

> “Find all buildings and show where they are.”

```text
Object Detection
        +
Visual Grounding
```

### Example 3 — Comparison + Counting

> “Which image shows more buildings?”

```text
Image Comparison
        +
Object Detection
        +
Counting
```

### Example 4 — Change + Detection

> “Are there new buildings in the second image?”

```text
Change Detection
        +
Object Detection
        +
Temporal Reasoning
```

The Task Engine is responsible for producing these combined capability requirements.

---

# 13. Final Model Requirements Matrix

| Task                              | Inputs | Modality      | Required Capability               | Preprocessing                         | Expected Output                                  |
| --------------------------------- | -----: | ------------- | --------------------------------- | ------------------------------------- | ------------------------------------------------ |
| Object Detection                  |     ≥1 | Compatible    | Object Detection                  | Model/pipeline-specific               | Objects + locations + confidence if supported    |
| Object Identification             |     ≥1 | Compatible    | Object Identification             | Model/pipeline-specific               | Object/category + confidence if supported        |
| Object Counting                   |     ≥1 | Compatible    | Object Detection + Counting       | Model/pipeline-specific               | Instances + total count                          |
| Visual Grounding                  |     ≥1 | Compatible    | Visual Grounding                  | Model/pipeline-specific               | Target location/region + confidence if supported |
| Scene Understanding               |      1 | Compatible    | Scene/Image Understanding         | Model/pipeline-specific               | Scene interpretation                             |
| Image Classification              |     ≥1 | Compatible    | Classification                    | Model/pipeline-specific               | Predicted class + confidence if supported        |
| Land-use/Land-cover Understanding |     ≥1 | Compatible    | LULC Understanding/Classification | Model/pipeline-specific               | LULC interpretation                              |
| Satellite VQA                     |     ≥1 | Compatible    | Satellite VQA                     | Model/pipeline-specific               | Natural-language answer                          |
| Image Comparison                  |     ≥2 | Compatible    | Image Comparison                  | Alignment/normalization when required | Similarities/differences                         |
| Change Analysis                   |     ≥2 | Compatible    | Change Detection/Analysis         | Alignment/normalization when required | Changed regions/features + description           |
| Optical–Optical Comparison        |     ≥2 | Optical       | Optical Comparison                | Optical-specific                      | Comparison result                                |
| SAR–SAR Comparison                |     ≥2 | SAR           | SAR Comparison                    | SAR-specific                          | Comparison/change result                         |
| Optical–SAR Comparison            |     ≥2 | Optical + SAR | Cross-Modality Comparison         | Modality-specific                     | Cross-modality interpretation                    |
| Flood Analysis                    |     ≥1 | Compatible    | Flood Detection/Analysis          | Capability-specific                   | Flooded regions/analysis                         |
| Water Analysis                    |     ≥1 | Compatible    | Water Detection/Analysis          | Capability-specific                   | Water regions/features                           |
| Surface/Land Analysis             |     ≥1 | Compatible    | Surface/Land Analysis             | Capability-specific                   | Surface/land interpretation                      |
| Other Satellite Analysis          |     ≥1 | Compatible    | Query-defined capability          | Capability-specific                   | Analysis result                                  |

---

# 14. Standard Model Requirement Structure

Every task should be expressible using a consistent conceptual structure:

```json
{
  "task": "...",
  "modality": "...",
  "inputs": {
    "count": 1,
    "format": "image"
  },
  "preprocessing": [],
  "required_capabilities": [],
  "expected_output": {}
}
```

Example:

```json
{
  "task": "object_counting",
  "modality": "compatible",
  "inputs": {
    "count": 1,
    "format": "image"
  },
  "preprocessing": [],
  "required_capabilities": [
    "object_detection",
    "counting"
  ],
  "expected_output": {
    "detections": true,
    "count": true
  }
}
```

This is an **architecture-level representation**. The final API schema will be defined during Task Engine → Model Engine integration.

---

# 15. Expected Output Principle

The Model Engine must provide output appropriate for the requested task.

```text
Object Detection
    ↓
Objects + locations
```

```text
Object Counting
    ↓
Instances + total count
```

```text
Visual Grounding
    ↓
Target + spatial location
```

```text
Classification
    ↓
Class + confidence
```

```text
Change Analysis
    ↓
Changed regions + interpretation
```

```text
Satellite VQA
    ↓
Natural-language answer
```

The Model Engine may internally produce additional information, but the contract defines the information expected by downstream components.

---

# 16. Phase 2 → Phase 3 Boundary

```text
┌─────────────────────────────────────┐
│              PHASE 2                │
│                                     │
│ Query → Task → Requirements         │
│                                     │
│ Defines:                            │
│ • Task                              │
│ • Required capabilities             │
│ • Inputs                            │
│ • Modality                          │
│ • Preprocessing requirements        │
│ • Expected output                   │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│              PHASE 3                │
│                                     │
│ Model Engine                        │
│                                     │
│ Decides:                            │
│ • Model selection                   │
│ • Model integration                 │
│ • Model execution                   │
│ • Model-specific preprocessing      │
│ • Model-specific output handling    │
└─────────────────────────────────────┘
```

---

# 17. Responsibility Boundary

### Nian — Tech Lead / System Architect

Responsible for defining:

* Required capabilities
* Input requirements
* Modality requirements
* Preprocessing requirements at architecture level
* Expected outputs
* Combined capability behavior
* Phase 2 → Phase 3 contract

### Phase 3 Model Engine

Responsible for:

* Selecting models
* Integrating models
* Implementing model-specific preprocessing
* Executing models
* Handling model-specific outputs
* Meeting the Phase 2 capability contract

---

# 18. Design Rules

### Rule 1 — Capability before model

Phase 2 specifies capabilities; Phase 3 selects models.

### Rule 2 — Task determines capability

The required model capability comes from the task determined by the Task Engine.

### Rule 3 — Multiple capabilities are allowed

A task may require multiple capabilities.

### Rule 4 — Input requirements must be explicit

The Model Engine must know the expected number and type of inputs.

### Rule 5 — Modality must be explicit

Optical, SAR, and cross-modality requirements must be represented where relevant.

### Rule 6 — Output must satisfy the task

The expected output is defined by the task rather than by a particular model.

### Rule 7 — Model implementation belongs to Phase 3

Phase 2 does not select, train, or implement individual models.

---

# 19. Definition of Done

* [x] Model requirement principles defined
* [x] Object Detection requirements defined
* [x] Object Identification requirements defined
* [x] Object Counting requirements defined
* [x] Visual Grounding requirements defined
* [x] Scene Understanding requirements defined
* [x] Image Classification requirements defined
* [x] LULC requirements defined
* [x] Satellite VQA requirements defined
* [x] Image Comparison requirements defined
* [x] Change Analysis requirements defined
* [x] Optical–Optical requirements defined
* [x] SAR–SAR requirements defined
* [x] Optical–SAR requirements defined
* [x] Flood Analysis requirements defined
* [x] Water Analysis requirements defined
* [x] Surface/Land Analysis requirements defined
* [x] Other Satellite Analysis requirements defined
* [x] Final model requirements matrix defined
* [x] Capability vs model boundary defined
* [x] Combined capability behavior defined
* [x] Phase 2 → Phase 3 boundary defined

---

## Status : FINALIZED**

