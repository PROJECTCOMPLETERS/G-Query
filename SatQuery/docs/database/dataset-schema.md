# SatQuery AI — MongoDB Dataset Schema

## 1. Purpose

This document defines the MongoDB dataset schema for **SatQuery AI Phase 1 — Foundation & Input**.

The schema defines:

* What a SatQuery dataset represents
* Dataset metadata
* Satellite observations
* Spatial information
* Raster information
* File references
* Processing state
* MongoDB collections
* GridFS relationships
* Required and optional fields
* Indexing strategy
* Metadata ownership

The schema is designed to support Phase 1 while remaining extensible for later query, task, model, temporal, and multimodal analysis.

---

# 2. Dataset Concept

A **dataset** represents a logical satellite-data resource available to SatQuery.

A dataset is **not the physical satellite file itself**.

The relationship is:

```text
Dataset
   │
   ├── Metadata
   ├── Observations
   ├── Spatial information
   ├── Processing information
   │
   └── File references
           │
           ▼
         GridFS
           │
           ▼
    Actual satellite files
```

MongoDB stores the structured dataset information.

GridFS stores the large satellite files.

---

# 3. MongoDB Collections

Phase 1 uses the following collections:

```text
MongoDB
│
├── datasets
│
├── fs.files
│
└── fs.chunks
```

### `datasets`

Stores SatQuery dataset documents.

### `fs.files`

Managed by MongoDB GridFS and stores file metadata.

### `fs.chunks`

Managed by MongoDB GridFS and stores file chunks.

The application should primarily interact with the `datasets` collection and the GridFS API rather than directly manipulating `fs.chunks`.

---

# 4. Dataset Document

The logical structure of a dataset is:

```json
{
  "_id": "ObjectId",

  "name": "Chennai_Flood_2026",

  "description": "Satellite imagery of Chennai region",

  "dataset_type": "single",

  "observations": [],

  "spatial": {},

  "files": [],

  "processing": {}
}
```

The exact MongoDB BSON types are used during implementation.

---

# 5. Dataset Identity

```json
{
  "_id": "ObjectId",
  "name": "Chennai_Flood_2026",
  "description": "Satellite imagery of Chennai region"
}
```

## `_id`

MongoDB's native unique identifier.

**Required:** Yes

**Type:** `ObjectId`

The `_id` uniquely identifies the dataset.

---

## `name`

Human-readable dataset name.

**Required:** Yes

**Type:** String

Example:

```text
Chennai_Flood_2026
```

---

## `description`

Optional human-readable description.

**Required:** No

**Type:** String

---

# 6. Dataset Type

```json
{
  "dataset_type": "single"
}
```

The dataset type describes the logical organization of observations.

Allowed values:

```text
single
temporal
multimodal
```

### `single`

Represents a dataset containing one primary observation.

```text
Dataset
└── Observation
```

### `temporal`

Represents multiple observations associated with different acquisition times.

```text
Dataset
├── Observation A
└── Observation B
```

This supports future change-analysis workflows.

### `multimodal`

Represents observations from different sensing modalities.

Example:

```text
Dataset
├── Optical observation
└── SAR observation
```

This supports future optical-SAR analysis.

---

# 7. Observations

Observations are the core satellite-data units inside a dataset.

Conceptually:

```text
Dataset
│
└── observations[]
       │
       ├── observation
       ├── observation
       └── ...
```

An observation represents a satellite acquisition associated with a particular sensing source and time.

Example:

```json
{
  "observations": [
    {
      "observation_id": "obs_001",

      "source": {
        "platform": "Sentinel-2",
        "satellite": "Sentinel-2A",
        "sensor": "MSI",
        "provider": "ESA"
      },

      "modality": "optical",

      "acquisition": {
        "datetime": "2026-08-20T05:30:00Z"
      }
    }
  ]
}
```

---

# 8. Observation Identity

Each observation contains:

```json
{
  "observation_id": "obs_001"
}
```

**Required:** Yes

The identifier is unique within the dataset.

It allows later components to refer to individual observations.

---

# 9. Source Information

Each observation may contain:

```json
{
  "source": {
    "platform": "Sentinel-2",
    "satellite": "Sentinel-2A",
    "sensor": "MSI",
    "provider": "ESA"
  }
}
```

Fields:

| Field       | Required | Purpose                   |
| ----------- | -------- | ------------------------- |
| `platform`  | No       | Satellite/platform family |
| `satellite` | No       | Specific satellite        |
| `sensor`    | No       | Sensor/instrument         |
| `provider`  | No       | Data provider             |

These fields are generally derived from the source data and metadata.

---

# 10. Modality

Each observation has a modality.

Allowed Phase 1 values:

```text
optical
sar
multispectral
```

Example:

```json
{
  "modality": "sar"
}
```

The controlled values allow later components to identify which processing/model pipeline is appropriate.

---

# 11. Acquisition Information

Each observation can contain:

```json
{
  "acquisition": {
    "datetime": "2026-08-20T05:30:00Z"
  }
}
```

For future temporal datasets:

```json
{
  "acquisition": {
    "start_datetime": "...",
    "end_datetime": "..."
  }
}
```

The acquisition information is important for:

* Temporal analysis
* Dataset organization
* Future change detection
* Query filtering

---

# 12. Spatial Information

The dataset contains spatial information:

```json
{
  "spatial": {
    "crs": "EPSG:4326",
    "bbox": [
      80.1,
      12.8,
      80.4,
      13.2
    ]
  }
}
```

## `crs`

Coordinate Reference System.

Example:

```text
EPSG:4326
```

## `bbox`

Bounding box represented as:

```text
[minX, minY, maxX, maxY]
```

The spatial metadata is primarily extracted by the Data Engine.

---

# 13. Raster Information

Raster-specific technical information belongs to the observation.

Example:

```json
{
  "raster": {
    "width": 2048,
    "height": 2048,
    "bands": 4,
    "dtype": "uint16",
    "resolution": {
      "x": 10,
      "y": 10
    }
  }
}
```

Fields:

| Field          | Required | Purpose                |
| -------------- | -------- | ---------------------- |
| `width`        | No       | Raster width           |
| `height`       | No       | Raster height          |
| `bands`        | No       | Number of raster bands |
| `dtype`        | No       | Pixel data type        |
| `resolution.x` | No       | Pixel resolution in X  |
| `resolution.y` | No       | Pixel resolution in Y  |

These values should normally be extracted from the uploaded data.

---

# 14. Files

Files are represented through references.

Example:

```json
{
  "files": [
    {
      "gridfs_id": "ObjectId",
      "filename": "chennai_flood.tif",
      "content_type": "image/tiff",
      "size_bytes": 123456789
    }
  ]
}
```

## `gridfs_id`

Reference to the corresponding GridFS file.

**Required:** Yes for a stored file

**Type:** `ObjectId`

---

## `filename`

Original or assigned filename.

**Required:** Yes

---

## `content_type`

MIME type of the stored file.

Example:

```text
image/tiff
```

---

## `size_bytes`

File size in bytes.

This may also be available through GridFS metadata, but storing the relevant reference information in the dataset document allows application-level access without requiring a GridFS lookup for every dataset display.

---

# 15. Dataset-to-GridFS Relationship

The relationship is:

```text
datasets
   │
   │ files[].gridfs_id
   ▼
GridFS
   │
   ├── fs.files
   └── fs.chunks
```

Example:

```text
Dataset
_id = 100

files:
[
  {
    gridfs_id = 500
  }
]

GridFS
file_id = 500
      ↓
satellite_image.tif
```

The dataset document does not contain the complete satellite binary.

---

# 16. Processing Information

Each dataset contains processing state.

```json
{
  "processing": {
    "status": "validated",
    "created_at": "2026-09-06T10:00:00Z",
    "updated_at": "2026-09-06T10:05:00Z"
  }
}
```

---

# 17. Processing Status Lifecycle

The Phase 1 status lifecycle is:

```text
UPLOADING
    ↓
UPLOADED
    ↓
VALIDATING
    ↓
VALIDATED
    ↓
PROCESSING
    ↓
PROCESSED
```

A failure can occur during processing:

```text
UPLOADING ──→ FAILED
UPLOADED  ──→ FAILED
VALIDATING ─→ FAILED
PROCESSING ─→ FAILED
```

Possible values:

```text
uploading
uploaded
validating
validated
processing
processed
failed
```

The application should use the defined values consistently.

---

# 18. Timestamps

The processing section contains:

```text
created_at
updated_at
```

These should use UTC timestamps.

Example:

```json
{
  "created_at": "2026-09-06T10:00:00Z",
  "updated_at": "2026-09-06T10:05:00Z"
}
```

---

# 19. Required vs Optional Fields

## Required

The minimum dataset should contain:

```text
_id
name
dataset_type
observations
files
processing.status
processing.created_at
processing.updated_at
```

A stored dataset should have at least one valid file reference.

---

## Optional

The following can be absent when the source data does not provide them:

```text
description

source.platform
source.satellite
source.sensor
source.provider

acquisition.datetime
acquisition.start_datetime
acquisition.end_datetime

spatial.crs
spatial.bbox

raster.width
raster.height
raster.bands
raster.dtype
raster.resolution
```

This avoids rejecting valid data simply because a particular metadata field is unavailable.

---

# 20. Metadata Ownership

SatQuery distinguishes between **user-provided metadata** and **Data Engine-derived metadata**.

## User-provided

Examples:

```text
name
description
```

## Data Engine-derived

Examples:

```text
CRS
bounding box
raster dimensions
band count
dtype
resolution
source metadata
acquisition metadata
```

The Data Engine is authoritative for technical metadata extracted from the uploaded file.

Conceptually:

```text
User Input
   │
   ├── name
   └── description
          │
          ▼
      Data Engine
          │
          ├── CRS
          ├── bbox
          ├── dimensions
          ├── bands
          ├── resolution
          └── other technical metadata
```

---

# 21. Indexing Strategy

Phase 1 should use a minimal indexing strategy.

## Required/important indexes

### `_id`

MongoDB automatically indexes `_id`.

### Processing status

```text
processing.status
```

Useful for finding datasets based on processing state.

### Acquisition time

```text
observations.acquisition.datetime
```

Useful for future temporal queries.

### Modality

```text
observations.modality
```

Useful for identifying optical/SAR datasets.

### Spatial information

Spatial indexing should be introduced when the application requires geographic querying.

A `2dsphere` index may be used for an appropriate GeoJSON spatial representation.

The initial schema should not introduce unnecessary indexes before the corresponding query requirements exist.

---

# 22. Unique Constraints

The primary unique identifier is:

```text
_id
```

Dataset names should **not** be required to be globally unique.

Example:

```text
Dataset A
name = "Sentinel_Image"

Dataset B
name = "Sentinel_Image"
```

This can be valid because the datasets may represent different observations or sources.

Filenames should also not be globally unique.

Two datasets may legitimately contain files with the same filename.

---

# 23. Single Dataset

Example conceptual representation:

```text
dataset_type: single

observations:
    └── Observation 1
          ├── modality
          ├── source
          ├── acquisition
          └── raster
```

---

# 24. Temporal Dataset

Example:

```text
dataset_type: temporal

observations:
    ├── Observation 1
    │      └── acquisition: T1
    │
    └── Observation 2
           └── acquisition: T2
```

This representation provides the foundation for later change analysis.

---

# 25. Multimodal Dataset

Example:

```text
dataset_type: multimodal

observations:
    ├── Observation 1
    │      └── modality: optical
    │
    └── Observation 2
           └── modality: sar
```

This provides the foundation for later optical-SAR analysis.

---

# 26. Complete Example

```json
{
  "_id": "ObjectId",

  "name": "Chennai_Flood_2026",

  "description": "Satellite imagery for Chennai flood analysis",

  "dataset_type": "single",

  "observations": [
    {
      "observation_id": "obs_001",

      "source": {
        "platform": "Sentinel-2",
        "satellite": "Sentinel-2A",
        "sensor": "MSI",
        "provider": "ESA"
      },

      "modality": "multispectral",

      "acquisition": {
        "datetime": "2026-08-20T05:30:00Z"
      },

      "raster": {
        "width": 2048,
        "height": 2048,
        "bands": 4,
        "dtype": "uint16",
        "resolution": {
          "x": 10,
          "y": 10
        }
      }
    }
  ],

  "spatial": {
    "crs": "EPSG:4326",
    "bbox": [
      80.1,
      12.8,
      80.4,
      13.2
    ]
  },

  "files": [
    {
      "gridfs_id": "ObjectId",
      "filename": "chennai_flood.tif",
      "content_type": "image/tiff",
      "size_bytes": 123456789
    }
  ],

  "processing": {
    "status": "validated",
    "created_at": "2026-09-06T10:00:00Z",
    "updated_at": "2026-09-06T10:05:00Z"
  }
}
```

---

# 27. Architectural Relationship

The finalized Phase 1 data flow is:

```text
User
  │
  ▼
Frontend
  │
  ▼
FastAPI
  │
  ▼
Orchestration
  │
  ▼
Data Engine
  │
  ├── Validate
  ├── Read raster
  ├── Extract metadata
  └── Prepare dataset information
          │
          ▼
     Storage Layer
        /       \
       ▼         ▼
   MongoDB     GridFS
       │         │
       │         └── Satellite file
       │
       └── Dataset document
```

---

# 28. Design Principles

The schema follows these principles:

1. One primary `datasets` collection.
2. Large files are stored in GridFS.
3. MongoDB stores structured metadata and state.
4. Dataset documents reference GridFS files.
5. Observations represent satellite acquisitions.
6. A single dataset model supports single, temporal, and multimodal datasets.
7. Technical metadata is primarily Data Engine-derived.
8. User metadata and technical metadata remain conceptually distinct.
9. Required fields are kept minimal.
10. Indexes are introduced according to actual query requirements.
11. Dataset names and filenames are not globally unique.
12. The schema remains extensible for later SatQuery phases.

---

# 29. Final Decision

The finalized Phase 1 storage model is:

```text
                 MongoDB
                    │
             ┌──────┴──────┐
             │             │
             ▼             ▼
        datasets        GridFS
             │          /       \
             │      fs.files   fs.chunks
             │
             └── files[].gridfs_id
```

The finalized logical dataset model is:

```text
Dataset
│
├── Identity
│
├── dataset_type
│
├── observations[]
│   ├── identity
│   ├── source
│   ├── modality
│   ├── acquisition
│   └── raster
│
├── spatial
│
├── files[]
│   └── gridfs_id
│
└── processing
    ├── status
    ├── created_at
    └── updated_at
```

**Status: FINALIZED**

**Task:** NIAN-P1-004 — Define MongoDB Dataset Schema
