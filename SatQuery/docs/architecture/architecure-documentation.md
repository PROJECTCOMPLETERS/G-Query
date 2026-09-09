# SatQuery AI

## Architecture Documentation

**Task:** NIAN-P1-008
**Phase:** Phase 1 — Foundation & Input
**Owner:** Nian — Tech Lead / System Architect
**Status:** Finalized

---

## 1. Purpose

This task establishes the official architecture documentation for SatQuery AI.

The documentation records the architectural decisions finalized during Phase 1 and provides a common reference for the entire development team.

The documentation must describe:

* Overall system architecture
* Component/module responsibilities
* Module dependencies
* Data flow
* API contracts
* Technology stack
* Technology decisions
* Common data structures
* Phase 1 scope
* Git workflow
* Future-phase architecture

---

# 2. Documentation Structure

The official documentation is organized as follows:

```text
docs/
│
├── architecture/
│   ├── system-architecture.md
│   ├── component-architecture.md
│   ├── data-flow.md
│   ├── query-flow.md
│   ├── inference-flow.md
│   ├── multimodal-fusion.md
│   ├── deployment-architecture.md
│   ├── technology-stack.md
│   ├── technology-decisions.md
│   ├── phase-1-scope.md
│   └── common-data-structures.md
│
├── api/
│   ├── api-overview.md
│   ├── health-api.md
│   ├── dataset-api.md
│   ├── upload-api.md
│   └── error-handling.md
│
└── development/
    └── git-workflow.md
```

---

# 3. Architecture Documentation Principles

The documentation follows several rules.

### 3.1 Documentation must reflect the actual architecture

Documentation must not describe components or technologies as implemented when they are only planned.

### 3.2 Finalized decisions must remain consistent

All architecture documents must agree with:

* Module boundaries
* Technology stack
* MongoDB + GridFS storage
* API contracts
* Common data structures
* Phase 1 scope

### 3.3 Future architecture is clearly separated

Future-phase components may be documented for architectural planning, but their implementation status must be explicit.

```text
Phase 1
    ↓
Implemented foundation

Phase 2
    ↓
Planned query understanding

Phase 3
    ↓
Planned model execution

Phase 4
    ↓
Planned multimodal fusion

Phase 5
    ↓
Planned production/deployment capabilities
```

---

# 4. System Architecture Documentation

File:

```text
docs/architecture/system-architecture.md
```

This document defines the complete high-level SatQuery architecture.

The primary architecture is:

```text
                         SATQUERY
                            │
                            ▼
                    ┌───────────────┐
                    │   CHAT UI     │
                    │ React + TS    │
                    │ Tailwind      │
                    │ MapLibre      │
                    └───────┬───────┘
                            │
                         HTTP/JSON
                            │
                            ▼
                    ┌───────────────┐
                    │    FastAPI    │
                    │   API Layer   │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Orchestration │
                    │    Layer      │
                    └───────┬───────┘
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
       Query Engine    Data Engine    Task Engine
             │              │              │
             │              ▼              ▼
             │          Storage       Model Engine
             │          Layer              │
             │          /   \              │
             │         ▼     ▼             │
             │     MongoDB  GridFS         │
             │                             │
             └──────────────┬──────────────┘
                            ▼
                     Fusion Engine
                       Phase 4
                            │
                            ▼
                    Response Engine
                            │
                            ▼
                         Chat UI
```

The architecture document must identify which components are active in Phase 1 and which belong to later phases.

---

# 5. Component Architecture Documentation

File:

```text
docs/architecture/component-architecture.md
```

This document defines the responsibilities and boundaries of each major module.

```text
Frontend
Backend
Orchestration
Query Engine
Data Engine
Model Engine
Fusion Engine
Task Engine
Response Engine
Storage
Database
Workers
```

Each component must document:

* Responsibility
* Inputs
* Outputs
* Dependencies
* Forbidden responsibilities
* Phase of implementation

The module-boundary decisions finalized in **NIAN-P1-002** are authoritative.

---

# 6. Data Flow Documentation

File:

```text
docs/architecture/data-flow.md
```

This document explains how satellite data moves through SatQuery.

The Phase 1 conceptual flow is:

```text
User
  ↓
Chat UI / Upload UI
  ↓
FastAPI
  ↓
Orchestration / Services
  ↓
Data Engine
  ↓
Storage Layer
  ↓
MongoDB + GridFS
```

For retrieval:

```text
MongoDB / GridFS
       ↓
Storage Layer
       ↓
Data Engine
       ↓
Application
       ↓
Frontend
```

The storage implementation remains hidden behind the storage abstraction.

---

# 7. Query Flow Documentation

File:

```text
docs/architecture/query-flow.md
```

This document describes how natural-language queries will eventually move through SatQuery.

The planned flow is:

```text
User Query
    ↓
Chat UI
    ↓
FastAPI
    ↓
Orchestration
    ↓
Query Engine
    ↓
Task Engine
    ↓
Model / Data / Fusion Engines
    ↓
Response Engine
    ↓
Chat UI
```

This is primarily a **future-phase architecture document**.

Natural-language query understanding is not considered a completed Phase 1 capability.

---

# 8. Inference Flow Documentation

File:

```text
docs/architecture/inference-flow.md
```

This document describes the planned model execution architecture.

The conceptual future flow is:

```text
Query
  ↓
Task
  ↓
Model Selection
  ↓
Model Adapter
  ↓
Inference
  ↓
Result
  ↓
Response Engine
```

Model integration is primarily a Phase 3 responsibility.

---

# 9. Multimodal Fusion Documentation

File:

```text
docs/architecture/multimodal-fusion.md
```

This document describes the planned architecture for combining different satellite modalities.

Examples include:

```text
Optical
   +
SAR
   ↓
Alignment
   ↓
Feature Extraction
   ↓
Feature Fusion
   ↓
Unified Representation
   ↓
Analysis
```

Multimodal fusion is primarily planned for Phase 4.

Phase 1 does not implement the fusion engine.

---

# 10. Deployment Architecture Documentation

File:

```text
docs/architecture/deployment-architecture.md
```

This document describes the planned deployment architecture.

Phase 1 should avoid prematurely introducing unnecessary infrastructure.

Potential future infrastructure may include:

```text
Frontend
Backend
Workers
Redis
MongoDB
Model Services
Containerization
Cloud Infrastructure
```

The exact production deployment architecture will be finalized as the project approaches Phase 5.

---

# 11. Technology Stack Documentation

File:

```text
docs/architecture/technology-stack.md
```

The finalized Phase 1 technology stack is:

### Frontend

```text
React
TypeScript
Vite
Tailwind CSS
Zustand
MapLibre GL JS
```

### Backend

```text
Python
FastAPI
Pydantic
Uvicorn
```

### Data Processing

```text
Rasterio
GDAL
NumPy
GeoPandas
Shapely
PyProj
```

### Database and Storage

```text
MongoDB
PyMongo
GridFS
```

S3 and PostgreSQL are not part of the Phase 1 storage architecture.

---

# 12. Technology Decisions Documentation

File:

```text
docs/architecture/technology-decisions.md
```

This document records the reasoning behind major technology choices.

Important decisions include:

### MongoDB

Used for structured dataset metadata and application state.

### GridFS

Used for storing large satellite files through MongoDB.

### FastAPI

Used as the backend API boundary.

### React + TypeScript

Used for the interactive frontend.

### MapLibre

Used for satellite/geospatial visualization.

### Rasterio + GDAL

Used for raster processing and geospatial data handling.

The purpose of this document is to prevent architectural decisions from being forgotten or repeatedly debated.

---

# 13. Phase 1 Scope Documentation

File:

```text
docs/architecture/phase-1-scope.md
```

This document defines what Phase 1 is responsible for.

### Phase 1 focuses on:

```text
Foundation
Input
Dataset management
File ingestion
Validation
Metadata
Storage
Basic map visualization
API foundation
Common structures
Integration foundation
```

### Phase 1 does not implement:

```text
Natural-language query intelligence
Advanced query classification
VQA
Pretrained model execution
Change detection inference
SAR/optical fusion
Agentic model selection
Production-scale worker architecture
```

Those capabilities belong to later phases.

---

# 14. Common Data Structures Documentation

File:

```text
docs/architecture/common-data-structures.md
```

This document records the structures finalized in **NIAN-P1-006**:

```text
Dataset
Observation
SatelliteSource
Acquisition
SpatialInfo
RasterInfo
FileReference
ProcessingInfo
APIError
Pagination
```

These structures act as shared domain contracts between modules.

They are not:

* MongoDB models
* GridFS objects
* FastAPI request objects
* React objects
* Rasterio objects
* PyTorch tensors
* ML model objects

---

# 15. API Documentation

API documentation is located under:

```text
docs/api/
```

The Phase 1 API documentation covers:

```text
api-overview.md
health-api.md
dataset-api.md
upload-api.md
error-handling.md
```

The API base path is:

```text
/api/v1
```

The documentation records the API contracts finalized in **NIAN-P1-005**.

Query, analysis, inference, and fusion APIs are not finalized during Phase 1.

---

# 16. Git Workflow Documentation

File:

```text
docs/development/git-workflow.md
```

This document records the Git workflow finalized in **NIAN-P1-007**.

Core rules include:

```text
main is protected
        ↓
Developers work on separate branches
        ↓
Branch names are developer preference
        ↓
Pull Request
        ↓
Code Review
        ↓
Merge into main
```

### Approval and merge authority

For normal Pull Requests:

* Any team member other than the PR author may review and approve.
* At least one approval is required.
* **Only Nian can merge into `main`.**

For architecture-sensitive changes:

* **Nian's approval is mandatory.**
* **Nian performs the merge.**

---

# 17. Documentation Relationships

The documentation set should work together rather than operate as isolated files.

```text
System Architecture
        │
        ├── Component Architecture
        │
        ├── Data Flow
        │
        ├── Query Flow
        │
        ├── Inference Flow
        │
        ├── Multimodal Fusion
        │
        └── Deployment Architecture
                 │
                 ▼
        Technology Decisions
                 │
                 ▼
          Phase 1 Scope
```

API documentation and Git workflow documentation support the architecture from different perspectives.

---

# 18. Source of Truth

When documentation conflicts, the most recently finalized architectural decision takes precedence.

The following are authoritative Phase 1 decisions:

```text
P1-001  System Architecture
P1-002  Module Boundaries
P1-003  Technology Stack
P1-004  MongoDB Dataset Schema
P1-005  API Contracts
P1-006  Common Data Structures
P1-007  Git Workflow
```

Documentation should be updated whenever one of these decisions is formally changed.

---

# 19. Documentation Maintenance

Documentation is part of the development process.

A Pull Request that changes:

* Architecture
* API contracts
* Database schema
* Module boundaries
* Technology decisions
* Common structures

should also update the relevant documentation.

The principle is:

```text
Architecture Change
       ↓
Implementation Change
       ↓
Documentation Change
```

Documentation must not be allowed to become inconsistent with the implementation.

---

# 20. Phase Separation

SatQuery documentation must clearly distinguish:

```text
                    SATQUERY
                       │
          ┌────────────┴────────────┐
          │                         │
       CURRENT                   FUTURE
          │                         │
       Phase 1              Phase 2 → Phase 5
          │                         │
   Foundation/Input        Intelligence/Analysis
```

This prevents the team from accidentally implementing future functionality during Phase 1.

---

# 21. Documentation Completion Criteria

NIAN-P1-008 is complete when:

* [x] System architecture documentation defined
* [x] Component architecture documentation defined
* [x] Data flow documentation defined
* [x] Query flow documentation defined
* [x] Inference flow documentation defined
* [x] Multimodal fusion documentation defined
* [x] Deployment architecture documentation defined
* [x] Technology stack documentation defined
* [x] Technology decisions documentation defined
* [x] Phase 1 scope documentation defined
* [x] Common data structures documentation defined
* [x] API documentation structure defined
* [x] Git workflow documentation defined
* [x] Phase 1 and future-phase boundaries documented
* [x] Documentation consistency rules defined

**Status: COMPLETE**

---

## Final Decision

**NIAN-P1-008 — Create Architecture Documentation: COMPLETE**

The architecture documentation now serves as the team's **reference point for implementation**, while future-phase documents remain architectural plans rather than claims of implemented functionality.
