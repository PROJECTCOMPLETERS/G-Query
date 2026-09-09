# SatQuery AI — Phase 1 Technology Scope

## 1. Purpose

This document defines the technology scope of **SatQuery AI Phase 1 — Foundation & Input**.

The purpose is to establish a clear boundary between:

* What the team must build now
* What the architecture must anticipate
* What must intentionally wait for later phases

Phase 1 is a foundation phase, not the complete SatQuery AI system.

---

# 2. Phase 1 Objective

The objective of Phase 1 is to establish the technical foundation required for SatQuery to:

```text
Accept
  ↓
Validate
  ↓
Process
  ↓
Store
  ↓
Retrieve
  ↓
Display
```

satellite data.

The system should establish the infrastructure required for later conversational AI and satellite-analysis capabilities.

---

# 3. In Scope

## 3.1 Frontend

Phase 1 includes the foundation for:

* React application
* TypeScript
* Chat interface shell
* Satellite data input/upload interface
* Dataset information display
* Results display foundation
* Map interface
* Frontend API communication
* Basic application state

Technologies:

```text
React
TypeScript
Vite
Tailwind CSS
Zustand
MapLibre GL JS
```

---

## 3.2 Backend

Phase 1 includes:

* FastAPI application
* API routing foundation
* Request validation
* Response schemas
* Health endpoint
* Dataset/input endpoints
* Basic orchestration integration
* Error-handling foundation

Technologies:

```text
Python
FastAPI
Pydantic
Uvicorn
```

---

## 3.3 Data Engine

Phase 1 establishes the Data Engine foundation for:

* Data ingestion
* File validation
* Raster loading
* Metadata extraction
* Basic preprocessing
* Geospatial information
* Temporal information
* Dataset validation

Technologies:

```text
Rasterio
GDAL
NumPy
GeoPandas
Shapely
PyProj
```

---

## 3.4 Storage

Phase 1 establishes:

* Storage abstraction
* MongoDB connection
* Dataset metadata storage
* Application/state storage where required
* GridFS file storage
* File retrieval
* Storage references

Architecture:

```text
Storage Layer
     │
     ├── MongoDB
     │     └── Metadata / State
     │
     └── GridFS
           └── Satellite Files
```

---

## 3.5 Map Visualization

Phase 1 establishes map functionality for:

* Geographic navigation
* Dataset visualization
* Satellite imagery display
* Geographic metadata visualization

Technology:

```text
MapLibre GL JS
```

---

# 4. Out of Scope

The following capabilities are not implemented as Phase 1 functionality.

## 4.1 Advanced Query Understanding

Deferred to Phase 2:

* Natural-language query classification
* Intent prediction
* Entity extraction
* Query planning
* Missing-information detection
* Task mapping

---

## 4.2 Advanced Task Engine

Deferred to Phase 2:

* Intelligent task routing
* Complete task execution pipelines
* Complex analysis planning

---

## 4.3 AI Model Integration

Deferred to Phase 3:

* GeoChat integration
* RS-DINO integration
* Change-detection model integration
* SAR model integration
* Model adapters
* Model registry
* Advanced inference orchestration

---

## 4.4 Multimodal Fusion

Deferred to Phase 4:

* Optical + SAR fusion
* Temporal fusion
* Feature fusion
* Cross-modal representation
* Unified multimodal representation

---

## 4.5 Production Infrastructure

Deferred primarily to Phase 5:

* Celery-based background workers
* Redis infrastructure
* Production monitoring
* Advanced logging infrastructure
* Production optimization
* Large-scale deployment architecture
* Advanced authentication/authorization
* Production-grade asynchronous processing

---

# 5. Technology Boundary

The Phase 1 technology boundary is:

```text
┌─────────────────────────────────────┐
│              FRONTEND               │
│ React + TypeScript + MapLibre       │
└─────────────────┬───────────────────┘
                  │
               HTTP/JSON
                  │
┌─────────────────▼───────────────────┐
│              FASTAPI                │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│           ORCHESTRATION             │
└──────────────┬───────────┬──────────┘
               │           │
               ▼           ▼
       ┌────────────┐ ┌──────────────┐
       │ Data Engine│ │   Storage    │
       └─────┬──────┘ │ Abstraction  │
             │        └──────┬───────┘
             │               │
             ▼          ┌────┴─────┐
      Geospatial        ▼          ▼
      Processing     MongoDB     GridFS
```

---

# 6. Technologies Explicitly Excluded from Phase 1

The following are not part of the Phase 1 core stack:

```text
PostgreSQL
Amazon S3
Redis
Celery
Kubernetes
Advanced model-serving infrastructure
Distributed inference infrastructure
Production monitoring platforms
```

Their absence is intentional.

They can be reconsidered when a later phase creates a real requirement for them.

---

# 7. Phase 1 Principle

The team should follow:

> **Build the minimum technical foundation required for the next phase without prematurely implementing the next phase.**

This means the architecture should provide clean extension points for:

```text
Phase 2 → Query Engine + Task Engine
Phase 3 → Model Engine
Phase 4 → Fusion Engine
Phase 5 → Production Infrastructure
```

without implementing those systems during Phase 1.

---

# 8. Phase Transition

Phase 1 is ready to transition toward Phase 2 when the foundation supports:

```text
Satellite Input
      ↓
Validation
      ↓
Processing
      ↓
Metadata
      ↓
MongoDB / GridFS
      ↓
Map / UI
      ↓
Backend API
```

reliably and through the defined module boundaries.

---

# 9. Final Phase 1 Scope

### Build Now

```text
React
TypeScript
Vite
Tailwind
Zustand
MapLibre

FastAPI
Pydantic
Uvicorn

Rasterio
GDAL
NumPy
GeoPandas
Shapely
PyProj

MongoDB
PyMongo
GridFS

Storage Abstraction
Basic Orchestration
```

### Build Later

```text
Query Engine          → Phase 2
Task Engine           → Phase 2
Model Engine          → Phase 3
Fusion Engine         → Phase 4
Celery / Redis        → Phase 5
Production deployment → Phase 5
```

**Status: FINALIZED**

**Task:** NIAN-P1-003 — Finalize Phase 1 Technology Stack
