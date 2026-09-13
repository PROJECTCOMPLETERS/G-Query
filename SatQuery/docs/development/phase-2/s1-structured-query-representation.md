# SatQuery AI — Phase 2 Step 1

## Structured Query Representation

**Phase:** Phase 2 — Query Understanding & Task Routing
**Owner:** Nian — Tech Lead / System Architect
**Status:** Finalized

---

## 1. Purpose

The Structured Query Representation defines the standard internal representation produced by the SatQuery Query Engine.

Its purpose is to convert a user's natural-language request into structured information that downstream components can process consistently.

The Query Engine is responsible for understanding the request. It does not execute machine-learning models.

The architecture follows:

```text
Natural-Language Query
        ↓
   Query Engine
        ↓
Structured Query
        ↓
    Task Engine
```

---

## 2. Query Engine Responsibility

The Query Engine is responsible for identifying:

* User question
* Intent
* Entities
* Input observations/images
* Image modality
* Temporal information
* Spatial/context information
* Requested capabilities
* Missing information

The Query Engine produces the Structured Query as its output.

It must not:

* Execute ML models
* Select or load a specific pretrained model
* Perform raster processing
* Determine whether satellite data is technically compatible
* Perform final data-readiness validation

Those responsibilities belong to downstream components.

---

## 3. Structured Query Schema

The initial Phase 2 Structured Query is defined as:

```json
{
  "question": "Where are the buildings in this image?",

  "intent": "visual_understanding",

  "entities": [
    "buildings"
  ],

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
    "required": true,
    "information": null
  },

  "requested_capabilities": [
    "visual_grounding"
  ],

  "missing_information": []
}
```

This schema is the architectural baseline for Phase 2.

---

## 4. Field Definitions

### 4.1 `question`

The original natural-language question provided by the user.

Example:

```text
"Where are the buildings in this image?"
```

The original question should be preserved because downstream analysis may require the user's exact request.

---

### 4.2 `intent`

Represents the user's high-level objective.

Examples include:

```text
visual_understanding
change_analysis
classification
comparison
```

The final supported intent/task taxonomy will be defined separately in Step 2.

Therefore, the `intent` field must remain extensible.

---

### 4.3 `entities`

Represents important objects, concepts, or targets identified from the user's request.

Example:

```json
"entities": [
  "buildings"
]
```

Another example:

```json
"entities": [
  "roads",
  "buildings"
]
```

---

### 4.4 `inputs`

Represents the observations or image inputs referred to by the query.

Example:

```json
"inputs": [
  {
    "input_id": "obs_001",
    "type": "image"
  }
]
```

For two-image analysis:

```json
"inputs": [
  {
    "input_id": "obs_001",
    "type": "image"
  },
  {
    "input_id": "obs_002",
    "type": "image"
  }
]
```

### Input architecture rule

The actual image/raster data is **not embedded inside the Structured Query**.

The Structured Query contains references such as `input_id`.

The actual data is handled by the input/data layer.

This allows the Query Engine to remain independent of the physical storage and processing mechanism.

---

## 5. Modality

The `modality` field represents the known or identified imagery modality.

Possible values may include:

```text
optical
sar
optical_sar
unknown
```

If the Query Engine cannot determine the modality from the query, the value may remain unknown/null.

The Data Engine can subsequently determine modality from the actual available data.

Example:

```json
"modality": null
```

---

## 6. Temporal Information

Temporal information represents time-related requirements or information contained in the query.

Example:

```text
"What changed between the images from 2020 and 2025?"
```

Structured representation:

```json
"temporal": {
  "required": true,
  "information": {
    "start": "2020",
    "end": "2025"
  }
}
```

If temporal information is required but not specified:

```json
"temporal": {
  "required": true,
  "information": null
}
```

The exact temporal representation can be extended when the task and data requirements are finalized.

---

## 7. Spatial Information

Spatial information represents geographic or spatial context contained in the query.

Example:

```text
"Show flooded areas around Madurai."
```

Conceptually:

```json
"spatial": {
  "required": true,
  "information": "Madurai"
}
```

Spatial information may later include geographic coordinates, regions, bounding boxes, polygons, or other supported spatial representations.

---

## 8. Requested Capabilities

`requested_capabilities` represents the capabilities required to satisfy the user's request.

This is intentionally capability-based rather than tied permanently to a fixed ML model.

Examples:

```text
visual_question_answering
visual_grounding
counting
image_understanding
classification
comparison
```

A request may require more than one capability.

Example:

```json
"requested_capabilities": [
  "visual_question_answering",
  "visual_grounding"
]
```

This allows SatQuery to take advantage of the capabilities of modern VLMs while remaining extensible for satellite-specific analysis pipelines.

---

## 9. Missing Information

`missing_information` contains information required to continue processing but not currently available.

Example:

User:

```text
"Compare these images."
```

Available:

```text
1 observation
```

Required:

```text
2 observations
```

Structured representation:

```json
"missing_information": [
  "second_image"
]
```

The system must not attempt execution when required information is missing.

Instead, the missing information is passed to the appropriate clarification/interaction layer.

---

## 10. Example — Single Image VQA

### User Query

```text
"How many buildings are visible in this image?"
```

### Structured Query

```json
{
  "question": "How many buildings are visible in this image?",

  "intent": "visual_understanding",

  "entities": [
    "buildings"
  ],

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
    "visual_question_answering",
    "counting"
  ],

  "missing_information": []
}
```

---

## 11. Example — Visual Grounding

### User Query

```text
"Where are the buildings in this image?"
```

### Structured Query

```json
{
  "question": "Where are the buildings in this image?",

  "intent": "visual_understanding",

  "entities": [
    "buildings"
  ],

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
    "required": true,
    "information": null
  },

  "requested_capabilities": [
    "visual_grounding"
  ],

  "missing_information": []
}
```

---

## 12. Example — Multi-Image Change Analysis

### User Query

```text
"What changed between these two satellite images?"
```

### Structured Query

```json
{
  "question": "What changed between these two satellite images?",

  "intent": "change_analysis",

  "entities": [
    "change"
  ],

  "inputs": [
    {
      "input_id": "obs_001",
      "type": "image"
    },
    {
      "input_id": "obs_002",
      "type": "image"
    }
  ],

  "modality": null,

  "temporal": {
    "required": true,
    "information": null
  },

  "spatial": {
    "required": true,
    "information": null
  },

  "requested_capabilities": [
    "comparison"
  ],

  "missing_information": []
}
```

---

## 13. Module Boundary

The Query Engine ends at the Structured Query.

```text
                    Query Engine
                         │
                         │
                         ↓
              ┌──────────────────┐
              │ Structured Query │
              └────────┬─────────┘
                       │
                       ↓
                  Task Engine
                       │
                       ↓
               Task + Requirements
                       │
                       ↓
                  Data Engine
                       │
                       ↓
                 Data Readiness
                       │
                       ↓
                Execution Plan
                       │
                       ↓
                    Phase 3
```

The Query Engine does not take over the responsibilities of the Task Engine, Data Engine, or Model Engine.

---

## 14. Downstream Contract

The Structured Query becomes the input contract for the Task Engine.

The Task Engine receives:

```text
Structured Query
        ↓
Determine task
        ↓
Determine requirements
        ↓
Identify required data
        ↓
Identify required capabilities
        ↓
Select analysis pipeline
```

The Task Engine is responsible for converting the structured understanding into the requirements needed for execution.

---

## 15. Design Principles

### Principle 1 — Separation of concerns

Query understanding must remain separate from task execution.

### Principle 2 — Reference, don't embed

Images and large raster data are referenced through input/observation identifiers rather than embedded inside the Structured Query.

### Principle 3 — Capability-based design

The architecture should represent what capabilities are required rather than coupling Phase 2 to one specific model.

### Principle 4 — Extensibility

New VLM capabilities and satellite-analysis capabilities should be addable without redesigning the complete Structured Query.

### Principle 5 — Missing information must be explicit

The system must identify missing required information rather than attempting an invalid execution.

### Principle 6 — Stable downstream contract

The Structured Query must provide a consistent interface for the Task Engine.

---

## 16. Step 1 Definition of Done

Step 1 is considered complete when:

* Query Engine responsibility is defined.
* Structured Query fields are defined.
* Input/observation references are defined.
* Actual image data is separated from query metadata.
* Intent representation is defined.
* Entity representation is defined.
* Modality representation is defined.
* Temporal representation is defined.
* Spatial representation is defined.
* Requested capabilities are defined.
* Missing-information representation is defined.
* Query Engine → Task Engine boundary is defined.
* Example Structured Queries are documented.

**Status: FINALIZED**
