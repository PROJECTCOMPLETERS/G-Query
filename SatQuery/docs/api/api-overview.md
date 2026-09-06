# SatQuery AI — API Overview

## 1. Purpose

This document defines the Phase 1 API architecture and communication conventions for SatQuery AI.

The API provides the communication boundary between the React frontend and the FastAPI backend.

```text
React / TypeScript
        │
        │ HTTP
        ▼
     FastAPI
        │
        ▼
 Orchestration
        │
   ┌────┴─────┐
   ▼          ▼
Data Engine  Storage
                │
           MongoDB + GridFS
```

---

## 2. Base URL

All Phase 1 APIs use:

```text
/api/v1
```

Example:

```text
/api/v1/datasets
```

API versioning is used so future breaking changes can be introduced without immediately breaking existing clients.

---

## 3. Communication Format

### JSON

Metadata and structured request/response data use:

```text
application/json
```

### File Upload

Satellite files use:

```text
multipart/form-data
```

Satellite binary data must not be embedded directly inside JSON requests.

---

## 4. Phase 1 Endpoints

| Method | Endpoint                                        | Purpose               |
| ------ | ----------------------------------------------- | --------------------- |
| GET    | `/api/v1/health`                                | Backend health        |
| POST   | `/api/v1/datasets`                              | Create dataset        |
| GET    | `/api/v1/datasets`                              | List datasets         |
| GET    | `/api/v1/datasets/{dataset_id}`                 | Get dataset           |
| DELETE | `/api/v1/datasets/{dataset_id}`                 | Delete dataset        |
| POST   | `/api/v1/datasets/{dataset_id}/files`           | Upload satellite file |
| GET    | `/api/v1/datasets/{dataset_id}/files/{file_id}` | Retrieve file         |
| DELETE | `/api/v1/datasets/{dataset_id}/files/{file_id}` | Delete file           |

---

## 5. API Responsibility

The API layer is responsible for:

* Receiving requests
* Validating requests
* Calling orchestration/services
* Returning structured responses
* Returning consistent errors

The API layer is not responsible for implementing:

* Raster processing
* GDAL operations
* MongoDB business logic
* GridFS implementation
* AI model inference

---

## 6. Object Identifier Convention

MongoDB's internal `_id` is represented externally as:

```json
{
  "dataset_id": "66f..."
}
```

The frontend does not need to know MongoDB's internal BSON representation.

---

## 7. Phase 1 Scope

Phase 1 APIs focus on:

```text
Dataset
    ↓
File
    ↓
Validation
    ↓
Metadata
    ↓
Storage
    ↓
Retrieval
```

Query, task, model, fusion, and conversational-analysis APIs are deferred to later phases.

**Status: FINALIZED**
