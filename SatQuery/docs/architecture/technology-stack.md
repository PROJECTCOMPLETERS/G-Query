# SatQuery AI — Phase 1 Technology Stack

## 1. Purpose

This document defines the finalized technology stack for **SatQuery AI Phase 1 — Foundation & Input**.

The purpose of this stack is to provide a stable foundation for:

* Satellite data input
* Dataset validation and processing
* Metadata management
* Satellite file storage
* Map visualization
* Backend API communication
* Basic application orchestration

The stack is intentionally limited to technologies required for Phase 1. Technologies belonging primarily to later phases are not introduced prematurely.

---

## 2. Technology Stack Overview

| Layer                 | Technology     | Purpose                                          |
| --------------------- | -------------- | ------------------------------------------------ |
| Frontend              | React          | User interface                                   |
| Frontend Language     | TypeScript     | Type-safe frontend development                   |
| Frontend Build        | Vite           | Development and production build                 |
| Styling               | Tailwind CSS   | UI styling                                       |
| Frontend State        | Zustand        | Client/application state                         |
| Map Visualization     | MapLibre GL JS | Geospatial and satellite visualization           |
| Backend               | Python         | Backend and processing ecosystem                 |
| API Framework         | FastAPI        | HTTP API layer                                   |
| Validation            | Pydantic       | Request/response validation                      |
| ASGI Server           | Uvicorn        | FastAPI application server                       |
| Database              | MongoDB        | Structured data and application state            |
| Database Driver       | PyMongo        | Python → MongoDB communication                   |
| File Storage          | MongoDB GridFS | Large satellite/binary file storage              |
| Raster Processing     | Rasterio       | Raster data access and processing                |
| Geospatial Processing | GDAL           | Raster/geospatial operations                     |
| Numerical Processing  | NumPy          | Numerical array processing                       |
| Vector Processing     | GeoPandas      | Vector/geospatial data processing                |
| Geometry              | Shapely        | Geometry operations                              |
| CRS/Projection        | PyProj         | Coordinate reference systems and transformations |

---

## 3. Frontend Stack

### 3.1 React

React is used to build the SatQuery user interface.

Phase 1 responsibilities include:

* Chat interface foundation
* Satellite data input/upload interface
* Dataset information display
* Result display foundation
* Map interface integration

The frontend communicates with the backend through defined APIs.

The frontend must not directly communicate with:

* MongoDB
* GridFS
* GDAL
* Rasterio
* Machine-learning models

---

### 3.2 TypeScript

TypeScript is used as the frontend programming language.

It provides:

* Static type checking
* Safer API integration
* Shared data-model definitions
* Better maintainability as the project grows

---

### 3.3 Vite

Vite is used as the frontend development and build tool.

Responsibilities:

* Local development server
* Frontend bundling
* Development build workflow

---

### 3.4 Tailwind CSS

Tailwind CSS is used for frontend styling.

It provides a consistent styling system while allowing the team to build the SatQuery interface efficiently.

---

### 3.5 Zustand

Zustand is used for frontend application state.

Potential Phase 1 state includes:

* Current dataset
* Upload state
* Selected satellite image
* Map state
* Current application/session state

---

### 3.6 MapLibre GL JS

MapLibre GL JS is used for map-based visualization.

Phase 1 responsibilities include:

* Displaying geographic context
* Displaying satellite imagery
* Supporting geographic navigation
* Preparing the interface for later analysis-result visualization

---

## 4. Backend Stack

### 4.1 Python

Python is the primary backend language.

Python is selected because SatQuery's later stages require a strong ecosystem for:

* Remote sensing
* Geospatial processing
* Machine learning
* Computer vision
* AI model integration

---

### 4.2 FastAPI

FastAPI is the primary backend API framework.

FastAPI provides the main communication boundary between the frontend and backend.

Basic flow:

```text
React
  ↓
HTTP / JSON
  ↓
FastAPI
  ↓
Orchestration
  ↓
SatQuery Engines
```

Phase 1 API responsibilities include:

* Health checking
* Dataset/input operations
* Upload handling
* Metadata operations
* Basic result communication

---

### 4.3 Pydantic

Pydantic is used for:

* Request validation
* Response validation
* API schemas
* Internal structured data contracts where appropriate

This helps ensure that modules communicate using predictable structures.

---

### 4.4 Uvicorn

Uvicorn is used as the ASGI server for running the FastAPI application.

---

## 5. Data Processing Stack

The Data Engine owns satellite-data processing.

### 5.1 Rasterio

Rasterio is used for raster data access and processing.

It will support operations involving satellite raster files such as:

* Reading raster metadata
* Reading raster bands
* Raster dimensions
* Transform information
* CRS information
* Windowed reading where required

---

### 5.2 GDAL

GDAL provides lower-level geospatial and raster processing capabilities.

It may be used for:

* Raster format handling
* Geospatial transformations
* Raster metadata operations
* Operations not conveniently handled through higher-level interfaces

---

### 5.3 NumPy

NumPy provides numerical array processing.

Satellite raster data will commonly be represented as numerical arrays during processing.

---

### 5.4 GeoPandas

GeoPandas provides vector/geospatial data handling where required.

---

### 5.5 Shapely

Shapely provides geometry operations.

---

### 5.6 PyProj

PyProj provides coordinate reference system and projection operations.

---

## 6. Database and Storage Stack

### 6.1 MongoDB

MongoDB is the primary database for Phase 1.

MongoDB stores:

* Dataset metadata
* Dataset state
* Processing metadata
* Application state
* References to stored files
* Other structured SatQuery information

MongoDB is **not intended to store large satellite binary files directly as normal documents**.

---

### 6.2 MongoDB GridFS

GridFS is used for storing large satellite files and other large binary objects.

Examples include:

* GeoTIFF files
* Large raster files
* Other satellite data files

Conceptual architecture:

```text
                 SatQuery
                    │
                    ▼
              Storage Layer
                 /      \
                /        \
               ▼          ▼
          MongoDB       GridFS
        metadata       large files
```

The application should interact with the storage abstraction rather than depending directly on GridFS throughout the codebase.

---

### 6.3 PyMongo

PyMongo is used by the backend/database implementation to communicate with MongoDB.

---

## 7. Storage Architecture

SatQuery separates **what the application needs from storage** from **how the storage is implemented**.

```text
Application / Engines
        │
        ▼
   storage/
   abstraction
        │
        ▼
   database/
 implementation
      /    \
     ▼      ▼
 MongoDB  GridFS
```

### `storage/`

Defines storage operations required by SatQuery.

Examples:

* Save dataset
* Get dataset
* Update dataset
* Delete dataset
* Store file
* Retrieve file
* Delete file
* Return storage references

### `database/`

Contains the MongoDB/GridFS-specific implementation.

This separation allows storage implementation details to remain isolated from the rest of the application.

---

## 8. Frontend-to-Backend Communication

The frontend communicates with the backend through HTTP APIs.

```text
┌──────────────┐
│   React UI   │
└──────┬───────┘
       │
       │ HTTP / JSON
       ▼
┌──────────────┐
│   FastAPI    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│Orchestration │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Data Engine  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│Storage Layer │
└──────┬───────┘
       │
   ┌───┴────┐
   ▼        ▼
MongoDB   GridFS
```

---

## 9. Phase 1 Development Environment

The expected development environment includes:

* Python
* Node.js
* npm
* MongoDB
* Git
* Docker

Docker is treated as a development/deployment tool rather than a SatQuery application module.

---

## 10. Technologies Deferred to Later Phases

The following are intentionally not part of the core Phase 1 implementation:

* Celery
* Redis
* S3
* PostgreSQL
* Advanced ML model-serving infrastructure
* Multimodal fusion infrastructure
* Distributed inference infrastructure
* Production monitoring infrastructure
* Kubernetes

These may be introduced in later phases if the architecture requires them.

---

## 11. Phase 1 Technology Boundary

Phase 1 concentrates on:

```text
Input
  ↓
Validation
  ↓
Processing
  ↓
Metadata
  ↓
Storage
  ↓
Visualization
```

Phase 1 does not implement the complete AI query pipeline.

Future phases will introduce:

```text
Natural Language Query
        ↓
Query Engine
        ↓
Task Engine
        ↓
Model Engine
        ↓
Fusion Engine
        ↓
Response Engine
```

---

## 12. Finalized Technology Stack

The following stack is approved for SatQuery AI Phase 1:

**Frontend**

React + TypeScript + Vite + Tailwind CSS + Zustand + MapLibre GL JS

**Backend**

Python + FastAPI + Pydantic + Uvicorn

**Geospatial/Data Processing**

Rasterio + GDAL + NumPy + GeoPandas + Shapely + PyProj

**Database/Storage**

MongoDB + PyMongo + GridFS

---

## 13. Technology Freeze

This document represents the finalized Phase 1 technology stack.

Any replacement of a core technology should be treated as an architecture decision and reviewed before implementation.

Examples:

```text
MongoDB → PostgreSQL
GridFS → S3
FastAPI → another API framework
React → another frontend framework
```

Such changes must not be made independently by individual modules without architecture review.

**Status: FINALIZED**

**Task:** NIAN-P1-003 — Finalize Phase 1 Technology Stack
