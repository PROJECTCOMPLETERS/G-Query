# SatQuery AI — Phase 2 Step 4: Data Requirements



**Owner:** Nian — Tech Lead / System Architect
**Phase:** Phase 2 — Query Understanding & Task Routing

---

## 1. Purpose

This document defines the **data requirements for each SatQuery task** before analysis can be executed.

The purpose is to establish a clear contract between the **Task Engine** and **Data Engine**.

The architecture separates responsibilities:

* **Nian / Phase 2:** defines what data each task requires.
* **Task Engine:** determines the task and produces the required data requirements.
* **Data Engine:** checks whether the available data satisfies those requirements.
* **Model Engine / Phase 3:** executes the selected model or analysis capability.

The Data Engine must therefore validate actual data against these requirements rather than deciding what the user's task is.

---

# 2. Data Requirement Principles

Every task may have requirements covering:

1. **Input requirements**
2. **Modality requirements**
3. **Temporal requirements**
4. **Spatial requirements**
5. **Data validity and quality**
6. **Task-specific requirements**

Not every requirement is mandatory for every task.

For example:

* Single-image analysis does not inherently require temporal information.
* Change analysis requires multiple observations and a temporal relationship.
* Spatial information becomes required when the user specifies a geographic or spatial constraint.

---

# 3. Requirement Categories

```text
Data Requirements
│
├── Input Requirements
│   ├── Number of observations
│   └── Input type
│
├── Modality Requirements
│   ├── Optical
│   ├── SAR
│   └── Compatible / supported
│
├── Temporal Requirements
│   ├── Not required
│   ├── Optional
│   └── Required
│
├── Spatial Requirements
│   ├── Spatial coverage
│   ├── User-specified region
│   └── Spatial compatibility
│
├── Quality Requirements
│   ├── Valid/readable data
│   └── Sufficient resolution/detail
│
└── Task-Specific Requirements
    ├── Target object
    ├── User question
    ├── Classification objective
    └── Analysis objective
```

---

# 4. Spatial Object Analysis

Spatial Object Analysis contains tasks that identify, detect, count, or locate objects within an observation.

## 4.1 Object Detection

**Purpose:** Find instances of a specified object or object category.

### Requirements

* At least **1 image/observation**
* Valid image/raster
* Modality compatible with the selected detection capability
* Target object should be identifiable
* Sufficient resolution/detail when required by the detection capability
* Temporal information is not required for single-image detection
* Spatial information is optional unless explicitly requested

### Example

> “Find all buildings in this satellite image.”

```text
Task:
    Object Detection

Required:
    ✓ 1 observation
    ✓ Valid image/raster
    ✓ Compatible modality
    ✓ Target = buildings
    ✓ Suitable visual detail/resolution
```

---

## 4.2 Object Identification

**Purpose:** Determine what an observed object is.

### Requirements

* At least **1 image/observation**
* Valid image/raster
* Compatible modality
* Object/target may be specified or inferred from the request
* Sufficient visual information for identification
* Temporal information is not required for single-image identification
* Spatial information is optional unless explicitly requested

### Example

> “Identify the objects visible in this image.”

```text
Task:
    Object Identification

Required:
    ✓ 1 observation
    ✓ Valid image/raster
    ✓ Compatible modality
    ✓ Sufficient visual information
```

---

## 4.3 Object Counting

**Purpose:** Determine the number of instances of a target object.

### Requirements

* At least **1 image/observation**
* Valid image/raster
* Compatible modality
* Target object must be known
* Sufficient visual detail/resolution to distinguish individual objects
* Temporal information is not required for single-image counting
* Spatial information is optional unless explicitly requested

### Example

> “How many buildings are in this satellite image?”

```text
Task:
    Object Counting

Required:
    ✓ 1 observation
    ✓ Valid image/raster
    ✓ Compatible modality
    ✓ Target = buildings
    ✓ Sufficient resolution/detail
```

Counting may require object detection as an underlying capability:

```text
Image
  ↓
Object Detection
  ↓
Identify target instances
  ↓
Count
  ↓
Total
```

---

## 4.4 Visual Grounding

**Purpose:** Locate a specified object or concept within an image.

### Requirements

* At least **1 image/observation**
* Valid image/raster
* Compatible modality
* Target object/concept must be specified or identifiable
* Sufficient visual detail/resolution
* Temporal information is not required for single-image grounding
* Geographic constraints are required only when explicitly requested

### Example

> “Where are the buildings?”

```text
Task:
    Visual Grounding

Required:
    ✓ 1 observation
    ✓ Valid image/raster
    ✓ Compatible modality
    ✓ Target = buildings
    ✓ Sufficient visual detail
```

---

# 5. Satellite Image Understanding

Satellite Image Understanding covers understanding the overall content and meaning of satellite observations.

## 5.1 Scene Understanding

**Purpose:** Understand the overall scene represented by an observation.

### Requirements

* 1 image/observation
* Valid image/raster
* Compatible modality
* Sufficient visual information
* Spatial information only when explicitly requested
* Temporal information is not inherently required

### Example

> “What is in this satellite image?”

---

## 5.2 Image Classification

**Purpose:** Assign an image or scene to a relevant class or category.

### Requirements

* At least **1 image/observation**
* Valid image/raster
* Compatible modality
* Classification objective/category
* Sufficient visual information
* Temporal information is not inherently required
* Spatial information is optional unless explicitly requested

### Example

> “Classify this satellite image.”

---

## 5.3 Land-use / Land-cover Understanding

**Purpose:** Understand land-use or land-cover represented in an observation.

### Requirements

* At least **1 image/observation**
* Valid image/raster
* Compatible modality
* Sufficient spatial/visual detail
* Target LULC objective/category
* Spatial information when a specific region is requested

### Example

> “What type of land cover is shown in this area?”

---

## 5.4 Satellite VQA

**Purpose:** Answer a question about a satellite observation.

### Requirements

* At least **1 image/observation**
* Valid image/raster
* Compatible modality
* User question
* Sufficient visual information
* Temporal/spatial information when required by the question

### Example

> “Are there roads visible in this satellite image?”

---

# 6. Multi-Observation Analysis

Multi-Observation Analysis operates on two or more observations.

## 6.1 Image Comparison

**Purpose:** Compare two or more observations and identify similarities or differences.

### Requirements

* At least **2 observations**
* Valid images/rasters
* Compatible modalities
* Comparable spatial coverage
* Compatible data
* Temporal information is optional for general comparison

### Example

> “Compare these two satellite images.”

```text
Observation A ──┐
                ├──> Comparison
Observation B ──┘
```

---

## 6.2 Change Analysis

**Purpose:** Determine what changed between observations.

### Requirements

* At least **2 observations**
* Valid images/rasters
* Compatible spatial coverage
* Compatible input data
* Temporal relationship
* Sufficient visual/data information

### Example

> “What changed between these two images?”

```text
Observation 1
     ↓
   Time T1
     ↓
   Change
     ↓
   Time T2
     ↓
Observation 2
```

Temporal information is a key requirement when the user asks for temporal change.

---

## 6.3 Optical–Optical Comparison

### Requirements

* At least **2 observations**
* Both compatible with optical processing
* Valid image/raster inputs
* Comparable spatial coverage
* Sufficient visual/data information
* Temporal information when the comparison is temporal

---

## 6.4 SAR–SAR Comparison

### Requirements

* At least **2 observations**
* Both compatible with SAR processing
* Valid image/raster inputs
* Comparable spatial coverage
* Sufficient data information
* Temporal information when the comparison is temporal

---

## 6.5 Optical–SAR Comparison

### Requirements

* At least **2 observations**
* One compatible optical observation
* One compatible SAR observation
* Valid image/raster inputs
* Comparable spatial coverage
* Appropriate information for cross-modality comparison

```text
Optical Observation
        +
SAR Observation
        ↓
Optical–SAR Comparison
```

---

# 7. Geospatial / Environmental Analysis

This category covers analysis of environmental and surface phenomena.

## 7.1 Flood Analysis

**Purpose:** Detect or analyze flooded areas.

### Requirements

* At least **1 observation**
* Valid image/raster
* Compatible modality
* Flood-related target/objective
* Sufficient information for flood analysis
* Spatial information when a particular region is specified
* Temporal information when temporal flood analysis is requested

### Example

> “Identify the flooded area.”

---

## 7.2 Water Analysis

**Purpose:** Identify or analyze water bodies or water-related regions.

### Requirements

* At least **1 observation**
* Valid image/raster
* Compatible modality
* Water/water-body target
* Sufficient visual/data information
* Spatial constraint when explicitly requested

### Example

> “Show the water bodies.”

---

## 7.3 Surface / Land Analysis

**Purpose:** Analyze land or surface characteristics.

### Requirements

* At least **1 observation**
* Valid image/raster
* Compatible modality
* Sufficient surface/land information
* Spatial information when specified
* Temporal information when required by the analysis

---

## 7.4 Other Satellite Analysis

This category is used when the request is satellite/geospatial analysis but does not fit a more specific task.

### Requirements

* At least **1 observation**
* Valid image/raster
* Compatible modality
* User-defined analysis objective
* Sufficient information for the requested analysis
* Additional spatial/temporal requirements as determined by the query

The system should not invent specialized data requirements until the analysis objective is known.

---

# 8. Final Data Requirements Matrix

| Task                              | Inputs | Modality      | Temporal        | Spatial  | Key Requirements                                   |
| --------------------------------- | -----: | ------------- | --------------- | -------- | -------------------------------------------------- |
| Object Detection                  |     ≥1 | Compatible    | Not required    | Optional | Target identifiable; sufficient resolution         |
| Object Identification             |     ≥1 | Compatible    | Not required    | Optional | Target identifiable; sufficient visual information |
| Object Counting                   |     ≥1 | Compatible    | Not required    | Optional | Target specified; sufficient resolution/detail     |
| Visual Grounding                  |     ≥1 | Compatible    | Not required    | Optional | Target specified; sufficient resolution/detail     |
| Scene Understanding               |      1 | Compatible    | Not required    | Optional | Usable visual information                          |
| Image Classification              |     ≥1 | Compatible    | Not required    | Optional | Classification objective; sufficient information   |
| Land-use/Land-cover Understanding |     ≥1 | Compatible    | Not required    | Optional | Sufficient spatial/visual detail                   |
| Satellite VQA                     |     ≥1 | Compatible    | Not required    | Optional | User question; sufficient visual information       |
| Image Comparison                  |     ≥2 | Compatible    | Optional        | Required | Comparable observations                            |
| Change Analysis                   |     ≥2 | Compatible    | Required        | Required | Temporal relationship; compatible coverage         |
| Optical–Optical Comparison        |     ≥2 | Optical       | When applicable | Required | Comparable optical observations                    |
| SAR–SAR Comparison                |     ≥2 | SAR           | When applicable | Required | Comparable SAR observations                        |
| Optical–SAR Comparison            |     ≥2 | Optical + SAR | When applicable | Required | Cross-modality compatible coverage                 |
| Flood Analysis                    |     ≥1 | Compatible    | Optional        | Optional | Flood-related information                          |
| Water Analysis                    |     ≥1 | Compatible    | Not required    | Optional | Water/water-body information                       |
| Surface/Land Analysis             |     ≥1 | Compatible    | Optional        | Optional | Surface/land information                           |
| Other Satellite Analysis          |     ≥1 | Compatible    | Depends         | Depends  | User-defined analysis objective                    |

---

# 9. Data Requirement Contract

The requirements passed toward the Data Engine can be represented conceptually as:

```json
{
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

This is an **architecture-level representation**. The final API schema will be defined when the Task Engine → Data Engine integration contract is finalized.

---

# 10. Data Readiness

After receiving task requirements, the Data Engine determines whether the available data is suitable.

```text
Task Requirements
        ↓
   Data Engine
        ↓
   Data Readiness
        │
        ├── ready = true
        │
        └── ready = false
              ↓
        Missing Information
```

Example:

> “What changed between these two images?”

If only one observation is available:

```json
{
  "ready": false,
  "missing_information": [
    "second_observation"
  ]
}
```

The system must not execute the task until the required information is available.

---

# 11. Responsibility Boundary

```text
                 Phase 2
                   │
                   ▼
              Task Engine
                   │
          Determines task
                   │
                   ▼
        Data Requirements
                   │
                   ▼
            Data Engine
                   │
          Checks actual data
                   │
                   ▼
           Data Readiness
                   │
                   ▼
                 Phase 3
             Model Engine
```

### Nian — System Architect

Defines:

* Task data requirements
* Input requirements
* Modality requirements
* Temporal requirements
* Spatial requirements
* Quality requirements
* Task-specific requirements
* Data-readiness expectations

### Rubin — Data Engine

Determines:

* What data is actually available
* Whether inputs satisfy the requirements
* Data compatibility
* Data readiness
* Missing required data

### Phase 3 Model Engine

Responsible for:

* Model selection
* Model integration
* Model execution
* Model-specific processing

---

# 12. Design Rules

### Rule 1 — Requirements are task-dependent

Different tasks require different data.

### Rule 2 — Multiple observations must be explicit

Comparison and change tasks must not execute with insufficient observations.

### Rule 3 — Temporal requirements are conditional

Temporal information is required for temporal analysis but not ordinary single-image analysis.

### Rule 4 — Spatial requirements are conditional

Spatial constraints become required when the user's query specifies a particular region or when the task requires spatial compatibility.

### Rule 5 — Data validation belongs to the Data Engine

Nian defines the requirements; Rubin validates the actual data.

### Rule 6 — Model selection is outside Phase 2

Phase 2 defines the required capability/data contract without implementing or selecting the individual ML model.

---

# 13. Definition of Done

Step 4 is complete when:

* [x] Data requirement principles are defined
* [x] Spatial Object Analysis requirements are defined
* [x] Satellite Image Understanding requirements are defined
* [x] Multi-Observation Analysis requirements are defined
* [x] Geospatial/Environmental Analysis requirements are defined
* [x] Final task matrix is defined
* [x] Requirement categories are standardized
* [x] Data-readiness concept is defined
* [x] Nian/Rubin responsibility boundary is defined
* [x] Missing-data behavior is defined
* [x] Phase 3 boundary is defined

---

## Status : FINALIZED**

