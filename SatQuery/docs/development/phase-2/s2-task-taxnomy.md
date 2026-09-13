# SatQuery AI — Phase 2 Step 2

## Task Taxonomy

**Phase:** Phase 2 — Query Understanding & Task Routing
**Owner:** Nian — Tech Lead / System Architect
**Status:** Finalized

---

## 1. Purpose

The Task Taxonomy defines the major categories of analysis that SatQuery can route a satellite or geospatial request into.

The taxonomy is designed around **analysis requirements and capabilities**, rather than being permanently tied to a particular ML model.

SatQuery should also avoid unnecessarily routing ordinary image questions through the satellite-analysis pipeline.

---

## 2. Core Routing Principle

SatQuery uses the simplest capable execution path.

```text
User Query + Input
        ↓
  Query Understanding
        ↓
Specialized satellite/
geospatial analysis required?
       / \
     NO   YES
     ↓     ↓
General   SatQuery
VLM Path  Task Routing
     ↓       ↓
  Answer   Requirements
```

### General VLM Path

If the user provides a normal image and asks a normal image-understanding question, the request can be handled directly by the general VLM.

Example:

```text
"What color is the car in this image?"
        ↓
General VLM
        ↓
Answer
```

It does not need to enter the specialized satellite/geospatial pipeline.

### SatQuery Path

If the request requires satellite, geospatial, spatial, temporal, multi-observation, or specialized environmental analysis, it enters the SatQuery pipeline.

Example:

```text
"What changed between these satellite images?"
        ↓
SatQuery
        ↓
Multi-Observation Analysis
```

---

# 3. SatQuery Task Families

SatQuery defines five major task families:

```text
1. Spatial Object Analysis

2. Satellite Image Understanding

3. Multi-Observation Analysis

4. Geospatial / Environmental Analysis

5. VLM-Assisted Satellite Reasoning
```

---

# 4. Spatial Object Analysis

Spatial Object Analysis covers requests involving the identification, localization, counting, or grounding of objects within satellite imagery.

```text
Spatial Object Analysis
│
├── Object Detection
├── Object Identification
├── Object Counting
└── Visual Grounding
```

### Examples

```text
"Find all the buildings."
        ↓
Object Detection
```

```text
"Where are the roads?"
        ↓
Visual Grounding
```

```text
"How many ships are visible?"
        ↓
Object Counting
```

The exact implementation may use VLM capabilities, specialized models, or a combination of both.

---

# 5. Satellite Image Understanding

Satellite Image Understanding covers requests that require understanding or interpreting a satellite observation.

```text
Satellite Image Understanding
│
├── Scene Understanding
├── Image Classification
├── Land-use / Land-cover Understanding
└── Satellite VQA
```

### Examples

```text
"What type of landscape is shown?"
        ↓
Scene Understanding
```

```text
"Classify this image as urban, agricultural, or forest."
        ↓
Image Classification
```

```text
"What is happening in this satellite image?"
        ↓
Satellite VQA / Reasoning
```

VQA is therefore supported within the satellite-analysis path when the query requires satellite-image understanding.

Generic VQA on an ordinary image remains part of the General VLM Path.

---

# 6. Multi-Observation Analysis

Multi-Observation Analysis handles requests requiring two or more satellite observations.

```text
Multi-Observation Analysis
│
├── Image Comparison
├── Change Analysis
├── Optical–Optical Comparison
├── SAR–SAR Comparison
└── Optical–SAR Comparison
```

### Examples

```text
"Compare these two optical images."
        ↓
Optical–Optical Comparison
```

```text
"What changed between these images?"
        ↓
Change Analysis
```

```text
"Compare this optical image with the SAR image."
        ↓
Optical–SAR Comparison
```

The taxonomy includes the multi-observation categories specified for Phase 2.

---

# 7. Geospatial / Environmental Analysis

This family covers satellite analysis focused on geographic or environmental phenomena.

```text
Geospatial / Environmental Analysis
│
├── Flood Analysis
├── Water Analysis
├── Surface / Land Analysis
└── Other Satellite Analysis
```

### Examples

```text
"Identify the flooded area."
        ↓
Flood Analysis
```

```text
"Show the water bodies."
        ↓
Water Analysis
```

```text
"Analyze the land in this region."
        ↓
Surface / Land Analysis
```

The Phase 2 architecture explicitly includes flood/water analysis and allows additional satellite-analysis tasks as required by the project.

---

# 8. VLM-Assisted Satellite Reasoning

Not every satellite request requires a specialized satellite-analysis model or raster-processing pipeline.

When a capable VLM can directly answer a satellite-image question, SatQuery may use the VLM as the analysis component.

```text
Satellite Image
      +
Natural-language Question
      ↓
VLM
      ↓
Reasoned Answer
```

### Examples

```text
"Describe the development visible in this satellite image."
```

```text
"What structures appear to be present?"
```

```text
"What is unusual about this scene?"
```

The Task Engine determines whether the request can be handled through VLM reasoning or requires a specialized analysis pipeline.

---

# 9. Task vs Capability

A task and a model capability are different concepts.

### Task

Describes **what SatQuery is trying to accomplish**.

### Capability

Describes **what the model or analysis pipeline needs to do**.

For example:

```text
User:
"How many buildings are visible?"
```

Task:

```text
Satellite Image Understanding
```

Required capabilities:

```text
visual_question_answering
object_identification
counting
```

Another example:

```text
User:
"Where are the buildings?"
```

Task:

```text
Spatial Object Analysis
```

Required capability:

```text
visual_grounding
```

Another:

```text
User:
"What changed between these images?"
```

Task:

```text
Multi-Observation Analysis
```

Required capabilities may include:

```text
comparison
change_detection
```

The capabilities will be represented through the `requested_capabilities` field established in Step 1.

---

# 10. Task Taxonomy Structure

The finalized taxonomy is:

```text
SATQUERY TASK TAXONOMY
│
├── Spatial Object Analysis
│   ├── Object Detection
│   ├── Object Identification
│   ├── Object Counting
│   └── Visual Grounding
│
├── Satellite Image Understanding
│   ├── Scene Understanding
│   ├── Image Classification
│   ├── Land-use / Land-cover Understanding
│   └── Satellite VQA
│
├── Multi-Observation Analysis
│   ├── Image Comparison
│   ├── Change Analysis
│   ├── Optical–Optical Comparison
│   ├── SAR–SAR Comparison
│   └── Optical–SAR Comparison
│
├── Geospatial / Environmental Analysis
│   ├── Flood Analysis
│   ├── Water Analysis
│   ├── Surface / Land Analysis
│   └── Other Satellite Analysis
│
└── VLM-Assisted Satellite Reasoning
```

---

# 11. Relationship With Step 1

Step 1 defines **how the query is represented**.

Step 2 defines **what type of SatQuery work the request represents**.

```text
Step 1
Natural Language
      ↓
Structured Query
      ↓
Step 2
Task Taxonomy
      ↓
Selected Task
      +
Requested Capabilities
```

Example:

```text
User:
"Where are the buildings in this satellite image?"
```

Structured Query:

```text
intent:
    visual_understanding

entities:
    buildings

inputs:
    obs_001

requested_capabilities:
    visual_grounding
```

Task Taxonomy:

```text
Spatial Object Analysis
        ↓
Visual Grounding
```

---

# 12. General VLM vs SatQuery

The following distinction is part of the architecture:

| Request                                               | Path           |
| ----------------------------------------------------- | -------------- |
| Normal image + simple question                        | General VLM    |
| Normal image + ordinary description                   | General VLM    |
| Satellite image + object localization                 | SatQuery       |
| Satellite image + geospatial question                 | SatQuery       |
| Two satellite observations + comparison               | SatQuery       |
| Satellite observations + change analysis              | SatQuery       |
| Satellite image + flood analysis                      | SatQuery       |
| Satellite image + complex spatial analysis            | SatQuery       |
| Satellite image + question answerable directly by VLM | SatQuery → VLM |

The final row does not imply that every satellite question requires a specialized model. SatQuery can route to the VLM when it is the appropriate capability.

---

# 13. Extensibility

The taxonomy is intentionally extensible.

New task families can be added when the project requires them without redesigning the Structured Query architecture.

For example:

```text
Future
│
├── Crop / Agriculture Analysis
├── Disaster Analysis
├── Urban Growth Analysis
├── Infrastructure Analysis
└── Other Domain-Specific Analysis
```

These are examples of possible future extensions, not currently locked Phase 2 tasks.

---

# 14. Boundary With Model Selection

The Task Taxonomy does not select a specific pretrained model.

The flow is:

```text
Query
  ↓
Structured Query
  ↓
Task
  ↓
Required Capabilities
  ↓
Data Requirements
  ↓
Model Requirements
  ↓
Execution Plan
  ↓
Phase 3 Model Execution
```

Phase 2 defines the required task and capabilities. Actual pretrained-model selection and integration are primarily part of Phase 3.

---

# 15. Step 2 Definition of Done

Step 2 is complete when:

* The general VLM fallback path is defined.
* The conditions for entering the SatQuery pipeline are defined.
* Major SatQuery task families are defined.
* Spatial Object Analysis is defined.
* Satellite Image Understanding is defined.
* Multi-Observation Analysis is defined.
* Geospatial / Environmental Analysis is defined.
* VLM-Assisted Satellite Reasoning is defined.
* Task and capability are clearly separated.
* Existing Phase 2 task categories are incorporated.
* The taxonomy is extensible.
* The taxonomy can be used by the Task Engine for routing.

## Status : FINALIZED**
