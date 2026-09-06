# SatQuery AI — Upload API

## 1. Purpose

The Upload API accepts satellite files and connects them to an existing SatQuery dataset.

---

# 2. Upload Satellite File

## Endpoint

```http
POST /api/v1/datasets/{dataset_id}/files
```

## Content Type

```text
multipart/form-data
```

## Request

The request contains the satellite file as a multipart file field.

Example conceptual request:

```text
dataset_id = 66f...

file = chennai_flood.tif
```

The binary file must not be encoded into a JSON request.

---

# 3. Processing Flow

```text
Frontend
   │
   │ multipart/form-data
   ▼
FastAPI
   │
   ▼
Orchestration
   │
   ▼
Data Engine
   │
   ├── Validate file
   ├── Read metadata
   ├── Extract raster information
   └── Prepare dataset information
   │
   ▼
Storage Layer
   │
   ├── MongoDB
   │     └── Dataset metadata
   │
   └── GridFS
         └── Satellite file
```

---

# 4. Successful Response

HTTP:

```text
200 OK
```

Example:

```json
{
  "dataset_id": "66f...",
  "file_id": "77a...",
  "filename": "chennai_flood.tif",
  "processing_status": "validated"
}
```

---

# 5. Processing Response

If processing has not completed:

```json
{
  "dataset_id": "66f...",
  "file_id": "77a...",
  "filename": "chennai_flood.tif",
  "processing_status": "processing"
}
```

The frontend can use the dataset status to determine whether the resource is ready.

---

# 6. Retrieve File

## Endpoint

```http
GET /api/v1/datasets/{dataset_id}/files/{file_id}
```

The backend retrieves the file through the Storage Layer.

```text
Frontend
   ↓
FastAPI
   ↓
Storage
   ↓
GridFS
   ↓
Satellite file
```

---

# 7. Delete File

## Endpoint

```http
DELETE /api/v1/datasets/{dataset_id}/files/{file_id}
```

The operation removes the corresponding stored file and its dataset reference.

## Response

HTTP:

```text
200 OK
```

Example:

```json
{
  "file_id": "77a...",
  "deleted": true
}
```

---

# 8. Upload Rules

1. Uploads must belong to an existing dataset.
2. File validation is performed by the backend/Data Engine.
3. Technical metadata should be extracted from the file where possible.
4. Large files are stored in GridFS.
5. Dataset metadata is stored in MongoDB.
6. The frontend never communicates directly with GridFS.
7. Failed processing must produce a defined error/status.

**Status: FINALIZED**
