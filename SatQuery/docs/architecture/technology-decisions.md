# SatQuery AI — Phase 1 Technology Decisions

## 1. Purpose

This document records the major technology decisions made for SatQuery AI Phase 1.

The purpose is to document not only **what technology was selected**, but also **why it was selected**.

These decisions provide a common technical direction for the development team.

---

## 2. Decision Summary

| Decision              | Selected Technology |
| --------------------- | ------------------- |
| Frontend framework    | React               |
| Frontend language     | TypeScript          |
| Frontend build tool   | Vite                |
| UI styling            | Tailwind CSS        |
| Frontend state        | Zustand             |
| Map library           | MapLibre GL JS      |
| Backend language      | Python              |
| API framework         | FastAPI             |
| Validation            | Pydantic            |
| API server            | Uvicorn             |
| Database              | MongoDB             |
| Database driver       | PyMongo             |
| Large-file storage    | MongoDB GridFS      |
| Raster processing     | Rasterio            |
| Geospatial processing | GDAL                |
| Numerical processing  | NumPy               |
| Vector processing     | GeoPandas           |
| Geometry              | Shapely             |
| Projection/CRS        | PyProj              |

---

# 3. Frontend Decisions

## TD-001 — React

**Decision:** Use React for the SatQuery frontend.

**Reasoning:**

SatQuery requires an interactive interface combining:

* Conversational interaction
* Satellite-data input
* Results
* Maps
* Future AI-analysis interactions

React provides a suitable component-based architecture for building this interface.

**Status:** Accepted

---

## TD-002 — TypeScript

**Decision:** Use TypeScript instead of plain JavaScript.

**Reasoning:**

SatQuery will exchange structured information between the frontend and backend.

TypeScript provides:

* Type safety
* Better API contract handling
* Easier refactoring
* Better maintainability

**Status:** Accepted

---

## TD-003 — MapLibre GL JS

**Decision:** Use MapLibre GL JS for map visualization.

**Reasoning:**

Satellite analysis requires a geographic visualization component.

MapLibre provides the foundation for:

* Interactive maps
* Geographic navigation
* Satellite-data visualization
* Future result overlays

**Status:** Accepted

---

# 4. Backend Decisions

## TD-004 — Python

**Decision:** Use Python for the backend.

**Reasoning:**

Python provides a strong ecosystem covering both:

* Geospatial/remote-sensing processing
* AI and machine-learning integration

This reduces the need to introduce a second backend language when later phases add model execution.

**Status:** Accepted

---

## TD-005 — FastAPI

**Decision:** Use FastAPI as the backend API framework.

**Reasoning:**

FastAPI provides:

* Python integration
* Request/response validation
* API documentation
* Asynchronous support
* A clean HTTP API boundary

It also fits naturally with the later AI-processing architecture.

**Status:** Accepted

---

## TD-006 — Pydantic

**Decision:** Use Pydantic for API data validation and schemas.

**Reasoning:**

SatQuery contains multiple architectural modules that must exchange predictable data structures.

Pydantic provides a standard way to validate API inputs and outputs.

**Status:** Accepted

---

# 5. Database and Storage Decisions

## TD-007 — MongoDB

**Decision:** Use MongoDB as the Phase 1 database.

**Reasoning:**

SatQuery needs to store flexible dataset metadata and application state.

MongoDB is appropriate for documents whose metadata may evolve as the project develops.

MongoDB will store structured information rather than acting as the primary mechanism for large satellite binary files.

**Status:** Accepted**

---

## TD-008 — MongoDB GridFS

**Decision:** Use MongoDB GridFS for large satellite files.

**Reasoning:**

Satellite imagery can be significantly larger than a normal MongoDB document should contain.

GridFS provides a mechanism for storing large files while keeping them associated with MongoDB.

This allows Phase 1 to use:

```text
MongoDB
   +
GridFS
```

as the storage foundation without introducing S3.

**Status:** Accepted

---

## TD-009 — No S3 in Phase 1

**Decision:** Amazon S3 is not part of the Phase 1 storage architecture.

**Reasoning:**

The current project requirement is to establish a simple, manageable storage foundation.

MongoDB + GridFS is sufficient for the planned Phase 1 scope.

S3 may be reconsidered later if scale, deployment requirements, or cost/operational considerations justify it.

**Status:** Accepted

---

## TD-010 — No PostgreSQL in Phase 1

**Decision:** PostgreSQL is not part of the Phase 1 database architecture.

**Reasoning:**

The project has selected MongoDB as its primary database.

Introducing PostgreSQL alongside MongoDB would create additional database complexity without a Phase 1 requirement.

**Status:** Accepted

---

# 6. Geospatial Processing Decisions

## TD-011 — Rasterio + GDAL

**Decision:** Use Rasterio and GDAL for raster/geospatial processing.

**Reasoning:**

SatQuery operates on remote-sensing imagery.

The Data Engine requires established tools for:

* Raster reading
* Metadata extraction
* Raster transformations
* Geospatial operations
* Raster format handling

**Status:** Accepted

---

## TD-012 — NumPy

**Decision:** Use NumPy for numerical array processing.

**Reasoning:**

Satellite raster data is naturally represented as numerical arrays.

NumPy provides the fundamental array-processing layer required by the Data Engine and will also be useful for later model-processing stages.

**Status:** Accepted

---

# 7. Architecture Decisions

## TD-013 — Storage Abstraction

**Decision:** Applications and engines should communicate with storage through the `storage/` abstraction rather than directly depending on MongoDB/GridFS throughout the codebase.

**Reasoning:**

This separates:

```text
What SatQuery needs
        from
How SatQuery stores it
```

Therefore:

```text
Application
     ↓
Storage Interface
     ↓
MongoDB / GridFS
```

This reduces coupling and makes future storage changes easier.

**Status:** Accepted

---

## TD-014 — FastAPI as Backend Boundary

**Decision:** The frontend communicates with SatQuery through FastAPI APIs.

**Reasoning:**

The frontend should remain independent of backend implementation details.

Therefore:

```text
Frontend
   ↓
FastAPI
   ↓
Internal architecture
```

The frontend must not directly access databases, geospatial libraries, or model implementations.

**Status:** Accepted

---

# 8. Deferred Infrastructure Decisions

The following technologies are deliberately deferred:

### Celery

Deferred until background/long-running task execution becomes necessary.

### Redis

Deferred until a concrete requirement for queues, caching, or task coordination exists.

### S3

Deferred until storage scale or deployment requirements justify object storage.

### Kubernetes

Deferred until distributed production deployment becomes necessary.

### Advanced Model Serving

Deferred until Phase 3 model integration.

---

# 9. Decision Change Policy

Technology decisions are not changed casually.

A proposed replacement must answer:

1. Why is the current technology insufficient?
2. What problem does the replacement solve?
3. What modules will be affected?
4. What migration work is required?
5. What new dependencies or complexity are introduced?
6. Does the change affect other phases?

A core technology change should be reviewed by the **Tech Lead/System Architect**.

---

## 10. Final Decision

The Phase 1 technology foundation is:

```text
React + TypeScript
        ↓
FastAPI + Python
        ↓
Orchestration
        ↓
Data Engine
        ↓
Storage Abstraction
        ↓
MongoDB + GridFS
```

**Status: FINALIZED**

**Task:** NIAN-P1-003 — Finalize Phase 1 Technology Stack
