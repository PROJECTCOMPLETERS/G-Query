# SatQuery AI

## Common Data Structures

**Task:** NIAN-P1-006
**Phase:** Phase 1 — Foundation & Input
**Status:** Finalized
**Owner:** Nian — Tech Lead / System Architect

---

## 1. Purpose

This document defines the common data structures used across the SatQuery AI system.

These structures act as **domain-level contracts** between different modules.

They provide a consistent representation of information such as:

* Datasets
* Satellite observations
* Satellite sources
* Acquisition information
* Spatial information
* Raster information
* Stored files
* Processing state
* API errors
* Pagination

The purpose is to prevent different modules from inventing their own incompatible representations of the same information.

---

## 2. Why Common Data Structures Are Needed

SatQuery contains multiple independent modules:

```text
Frontend
    ↓
Backend
    ↓
Orchestration
    ↓
Data Engine
    ↓
Storage
    ↓
MongoDB / GridFS
```

Later phases introduce:

```text
Query Engine
Task Engine
Model Engine
Fusion Engine
Response Engine
```

Without common structures, each module could represent the same dataset differently.

For example:

```text
Frontend:
datasetId

Backend:
dataset_id

Database:
_id

Data Engine:
dataset_object

GridFS:
file_id
```

These differences can create unnecessary coupling and integration problems.

Therefore, SatQuery uses common domain structures as the stable language between modules.

---

# 3. Design Principles

The common data structures follow these principles.

### 3.1 Domain-oriented

Structures describe SatQuery concepts rather than implementation details.

### 3.2 Technology-independent

They should not expose MongoDB, GridFS, Rasterio, GDAL, React, or ML implementation details unnecessarily.

### 3.3 Stable across phases

The structures should remain useful when Phase 2–5 modules are introduced.

### 3.4 Explicit contracts

Required and optional information should be clearly defined.

### 3.5 No implementation objects

Common structures must not contain framework or library objects.

Examples that must NOT appear:

```text
Rasterio Dataset
GDAL Dataset
MongoDB Collection
GridFS Bucket
PyTorch Tensor
FastAPI Request
React Component
ML Model Object
```

---

# 4. Core Common Structures

SatQuery Phase 1 defines the following structures:

```text
Common Data Structures
│
├── Dataset
├── Observation
├── SatelliteSource
├── Acquisition
├── SpatialInfo
├── RasterInfo
├── FileReference
├── ProcessingInfo
├── APIError
└── Pagination
```

---

# 5. Dataset

The `Dataset` structure represents the logical satellite dataset handled by SatQuery.

A dataset may contain one or more observations and associated files.

### Structure

```text
Dataset
├── id
├── name
├── description
├── dataset_type
├── observations[]
├── spatial
├── files[]
└── processing
```

### Fields

| Field        | Type            | Required | Description                           |
| ------------ | --------------- | -------: | ------------------------------------- |
| id           | string          |      Yes | Public dataset identifier             |
| name         | string          |      Yes | Dataset name                          |
| description  | string          |       No | Human-readable description            |
| dataset_type | enum            |      Yes | `single`, `temporal`, or `multimodal` |
| observations | Observation[]   |      Yes | Satellite observations                |
| spatial      | SpatialInfo     |       No | Dataset spatial information           |
| files        | FileReference[] |      Yes | Associated stored files               |
| processing   | ProcessingInfo  |      Yes | Dataset processing state              |

### Example

```json
{
  "id": "ds_001",
  "name": "Chennai Satellite Image",
  "description": "Optical satellite observation",
  "dataset_type": "single",
  "observations": [],
  "spatial": {},
  "files": [],
  "processing": {}
}
```

---

# 6. Observation

An `Observation` represents a satellite observation within a dataset.

A dataset can contain multiple observations.

This becomes particularly important for:

* Temporal analysis
* Change detection
* Multimodal analysis

### Structure

```text
Observation
├── observation_id
├── source
├── modality
├── acquisition
└── raster
```

### Fields

| Field          | Type            | Required | Description                                  |
| -------------- | --------------- | -------: | -------------------------------------------- |
| observation_id | string          |      Yes | Unique observation identifier within dataset |
| source         | SatelliteSource |       No | Satellite/platform information               |
| modality       | enum            |      Yes | `optical`, `sar`, or `multispectral`         |
| acquisition    | Acquisition     |       No | Acquisition information                      |
| raster         | RasterInfo      |       No | Raster technical information                 |

### Example

```json
{
  "observation_id": "obs_001",
  "source": {},
  "modality": "optical",
  "acquisition": {},
  "raster": {}
}
```

---

# 7. SatelliteSource

`SatelliteSource` represents information about the source of a satellite observation.

### Structure

```text
SatelliteSource
├── satellite
├── sensor
├── provider
└── product
```

### Fields

| Field     | Type   | Required | Description                 |
| --------- | ------ | -------: | --------------------------- |
| satellite | string |       No | Satellite/platform name     |
| sensor    | string |       No | Sensor/instrument name      |
| provider  | string |       No | Data provider/source        |
| product   | string |       No | Product or processing level |

### Example

```json
{
  "satellite": "Sentinel-1",
  "sensor": "SAR",
  "provider": "ESA",
  "product": "GRD"
}
```

---

# 8. Acquisition

`Acquisition` describes when and under what acquisition conditions an observation was captured.

### Structure

```text
Acquisition
├── datetime
├── start_datetime
├── end_datetime
└── orbit
```

### Fields

| Field          | Type     | Required | Description                            |
| -------------- | -------- | -------: | -------------------------------------- |
| datetime       | datetime |       No | Observation acquisition time           |
| start_datetime | datetime |       No | Start time for an acquisition interval |
| end_datetime   | datetime |       No | End time for an acquisition interval   |
| orbit          | string   |       No | Orbit information if available         |

The structure supports both single acquisition times and acquisition intervals.

---

# 9. SpatialInfo

`SpatialInfo` represents the geographic properties of an observation or dataset.

### Structure

```text
SpatialInfo
├── crs
├── bbox
├── geometry
└── resolution
```

### Fields

| Field      | Type   | Required | Description                    |
| ---------- | ------ | -------: | ------------------------------ |
| crs        | string |       No | Coordinate reference system    |
| bbox       | array  |       No | Bounding box                   |
| geometry   | object |       No | Geographic footprint           |
| resolution | object |       No | Spatial resolution information |

### Example

```json
{
  "crs": "EPSG:4326",
  "bbox": [80.20, 12.90, 80.35, 13.10]
}
```

Spatial information is important for:

* Map visualization
* Geographic filtering
* Spatial analysis
* Later geospatial query processing

---

# 10. RasterInfo

`RasterInfo` contains technical information about raster data.

### Structure

```text
RasterInfo
├── width
├── height
├── bands
├── dtype
├── crs
└── resolution
```

### Fields

| Field      | Type    | Required | Description      |
| ---------- | ------- | -------: | ---------------- |
| width      | integer |       No | Raster width     |
| height     | integer |       No | Raster height    |
| bands      | integer |       No | Number of bands  |
| dtype      | string  |       No | Raster data type |
| crs        | string  |       No | Raster CRS       |
| resolution | object  |       No | Pixel resolution |

### Example

```json
{
  "width": 2048,
  "height": 2048,
  "bands": 4,
  "dtype": "uint16",
  "crs": "EPSG:4326"
}
```

This information is primarily extracted by the **Data Engine** during validation and ingestion.

---

# 11. FileReference

`FileReference` represents a stored satellite file without exposing storage implementation details to the rest of the application.

### Structure

```text
FileReference
├── gridfs_id
├── filename
├── content_type
└── size_bytes
```

### Fields

| Field        | Type    | Required | Description                         |
| ------------ | ------- | -------: | ----------------------------------- |
| gridfs_id    | string  |      Yes | Reference to the stored GridFS file |
| filename     | string  |      Yes | Original filename                   |
| content_type | string  |       No | MIME/content type                   |
| size_bytes   | integer |       No | File size                           |

### Example

```json
{
  "gridfs_id": "68c123abc456",
  "filename": "sentinel_image.tif",
  "content_type": "image/tiff",
  "size_bytes": 52428800
}
```

The common structure exposes the **reference**, not the GridFS bucket itself.

---

# 12. ProcessingInfo

`ProcessingInfo` represents the current processing state of a dataset.

### Structure

```text
ProcessingInfo
├── status
├── created_at
├── updated_at
└── error
```

### Processing Status

The controlled status values are:

```text
uploading
uploaded
validating
validated
processing
processed
failed
```

### Fields

| Field      | Type     | Required | Description                             |
| ---------- | -------- | -------: | --------------------------------------- |
| status     | enum     |      Yes | Current processing state                |
| created_at | datetime |      Yes | Dataset creation time                   |
| updated_at | datetime |      Yes | Last state update                       |
| error      | string   |       No | Error information when processing fails |

### Example

```json
{
  "status": "validated",
  "created_at": "2026-09-06T10:00:00Z",
  "updated_at": "2026-09-06T10:02:00Z",
  "error": null
}
```

---

# 13. APIError

`APIError` defines the standard error structure returned by the backend.

### Structure

```text
APIError
└── error
    ├── code
    ├── message
    └── details
```

### Example

```json
{
  "error": {
    "code": "DATASET_NOT_FOUND",
    "message": "Dataset was not found.",
    "details": null
  }
}
```

### Standard Error Codes

```text
VALIDATION_ERROR
INVALID_DATASET_ID
DATASET_NOT_FOUND
FILE_NOT_FOUND
UNSUPPORTED_FILE_TYPE
INVALID_RASTER
PROCESSING_FAILED
STORAGE_ERROR
INTERNAL_ERROR
```

The structure ensures that frontend developers do not need to interpret different error formats from different backend modules.

---

# 14. Pagination

`Pagination` provides a common representation for paginated API responses.

### Structure

```text
Pagination
├── page
├── page_size
├── total
└── total_pages
```

### Fields

| Field       | Type    | Required | Description                    |
| ----------- | ------- | -------: | ------------------------------ |
| page        | integer |      Yes | Current page                   |
| page_size   | integer |      Yes | Number of items requested      |
| total       | integer |      Yes | Total number of matching items |
| total_pages | integer |      Yes | Total number of pages          |

### Example

```json
{
  "page": 1,
  "page_size": 20,
  "total": 73,
  "total_pages": 4
}
```

---

# 15. Relationship Between Structures

The structures form the following hierarchy:

```text
Dataset
│
├── Observation[]
│   │
│   ├── SatelliteSource
│   ├── Acquisition
│   └── RasterInfo
│
├── SpatialInfo
│
├── FileReference[]
│
└── ProcessingInfo
```

This allows SatQuery to represent datasets without coupling the domain model directly to MongoDB documents.

---

# 16. Module Usage

Different modules consume different common structures.

| Module          | Main Structures                                                                                            |
| --------------- | ---------------------------------------------------------------------------------------------------------- |
| Frontend        | Dataset, Observation, SpatialInfo, FileReference, ProcessingInfo, APIError, Pagination                     |
| Backend         | All API-relevant structures                                                                                |
| Data Engine     | Dataset, Observation, SatelliteSource, Acquisition, SpatialInfo, RasterInfo, FileReference, ProcessingInfo |
| Storage         | Dataset, FileReference, ProcessingInfo                                                                     |
| Orchestration   | Dataset, ProcessingInfo and execution-related structures                                                   |
| Query Engine    | Dataset/Observation metadata in later phases                                                               |
| Task Engine     | Dataset/Observation metadata in later phases                                                               |
| Model Engine    | Dataset/Observation/Raster-related information in later phases                                             |
| Response Engine | Result/evidence structures to be expanded in later phases                                                  |

---

# 17. Implementation Location

The recommended implementation is:

```text
backend/
└── schemas/
    ├── common/
    │   ├── dataset.py
    │   ├── observation.py
    │   ├── source.py
    │   ├── acquisition.py
    │   ├── spatial.py
    │   ├── raster.py
    │   ├── file.py
    │   ├── processing.py
    │   ├── error.py
    │   └── pagination.py
    │
    ├── dataset.py
    └── upload.py
```

The `common/` directory contains reusable domain structures.

Feature-specific request/response schemas remain outside `common/`.

For example:

```text
schemas/
├── common/
│   ├── dataset.py
│   ├── observation.py
│   └── ...
│
├── dataset.py
└── upload.py
```

---

# 18. Separation From Database Models

Common structures are **not database models**.

The distinction is:

```text
Common Schema
      │
      ▼
Application / Module Contract
      │
      ▼
Storage Layer
      │
      ▼
MongoDB / GridFS
```

For example:

```text
Dataset
   │
   ├── id
   ├── name
   ├── observations
   └── files
          │
          ▼
Storage abstraction
          │
          ▼
MongoDB document
          │
          └── GridFS reference
```

This allows the storage implementation to change without forcing every module to change.

---

# 19. Separation From API Schemas

Common structures are also not necessarily identical to API request/response models.

For example:

```text
API Request
    ↓
Pydantic validation
    ↓
Domain/Common Structure
    ↓
Service / Engine
    ↓
Storage
```

The API layer may expose only the fields required by a particular endpoint.

This prevents API-specific concerns from leaking into the domain layer.

---

# 20. Phase 1 Scope

Phase 1 only defines the structures required for:

* Dataset management
* Satellite data ingestion
* File management
* Metadata representation
* Processing state
* API communication
* Pagination
* Error handling

The following are intentionally deferred:

```text
Query structures
Task structures
Model inference structures
Change-detection result structures
Fusion structures
VQA structures
Evidence structures
Confidence structures
Chat-message structures
Agent execution structures
```

These will be defined when their respective phases are implemented.

---

# 21. Future Compatibility

The common structures are designed so that later phases can build upon them.

For example:

```text
Phase 1
Dataset
   ↓
Phase 2
Query → Dataset
   ↓
Phase 3
Task → Dataset → Model
   ↓
Phase 4
Dataset → Optical + SAR → Fusion
   ↓
Phase 5
Execution → Result → Evidence → Response
```

The goal is to avoid redesigning the fundamental dataset representation every time a new engine is introduced.

---

# 22. Final Architecture Principle

The common data structures are the **shared language of SatQuery modules**.

They define **what information means**, while individual modules define **how that information is processed**.

```text
Common Structures
       │
       ├── Define WHAT
       │
       ▼
Module Implementations
       │
       └── Define HOW
```

Therefore:

> **Common structures define stable domain contracts and must remain independent from implementation-specific technologies.**

---

# 23. Completion Criteria

NIAN-P1-006 is considered complete when:

* [x] Core common structures are identified.
* [x] Dataset structure is defined.
* [x] Observation structure is defined.
* [x] Satellite source structure is defined.
* [x] Acquisition structure is defined.
* [x] Spatial structure is defined.
* [x] Raster structure is defined.
* [x] File reference structure is defined.
* [x] Processing information structure is defined.
* [x] API error structure is defined.
* [x] Pagination structure is defined.
* [x] Module usage is defined.
* [x] Implementation location is defined.
* [x] Database/API separation is defined.
* [x] Phase 1 scope is defined.
* [x] Future-phase compatibility is defined.

**Status: COMPLETE**
