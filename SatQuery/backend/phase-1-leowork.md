# SatQuery AI — Phase 1 Backend Documentation

## 1. Overview

The SatQuery AI backend provides the foundation for uploading, validating, storing, retrieving, and managing remote-sensing raster datasets.

The Phase 1 backend is responsible for:

* Dataset creation and management
* Raster file upload
* Raster validation
* Raster metadata extraction
* Spatial information handling
* File storage using GridFS
* Dataset metadata storage using MongoDB
* File retrieval
* File deletion
* Dataset deletion with associated file cleanup
* Request validation
* Standardized API errors
* Pagination
* Automated backend testing

Phase 1 intentionally does **not** implement:

* Natural-language query understanding
* Vision-language model inference
* Object detection
* Change detection
* SAR analysis
* Optical/SAR fusion
* Map rendering
* Frontend logic

---

# 2. Backend Architecture

The backend follows a layered architecture:

```text
                    Client / Frontend
                           │
                           ▼
                       FastAPI
                           │
                           ▼
                        Services
                    /             \
                   ▼               ▼
          Dataset Service      File Service
                   │               │
                   └───────┬───────┘
                           ▼
                  Storage Abstraction
                    /             \
                   ▼               ▼
               MongoDB           GridFS
              Metadata        Raster Files
```

The important architectural rule is that the API layer does not directly communicate with MongoDB or GridFS.

Instead:

```text
API
 ↓
Service
 ↓
Storage Interface
 ↓
Storage Implementation
 ↓
Database / File Storage
```

This keeps storage technology replaceable.

For example, the current implementation uses:

```text
MongoDB
+
GridFS
```

but the service layer does not need to know the low-level MongoDB/GridFS implementation.

---

# 3. Technology Stack

## Backend

* Python
* FastAPI
* Pydantic
* Pydantic Settings
* PyMongo
* MongoDB
* GridFS
* Pytest
* FastAPI TestClient

## Raster/Data Processing

The backend uses the existing Data Engine for:

* File-type detection
* Raster validation
* Metadata extraction

The backend does not implement raster parsing itself.

---

# 4. Storage Architecture

## MongoDB

MongoDB stores dataset-level information.

A dataset contains:

```text
dataset_id
name
dataset_type
processing
observations
```

The observations contain:

* Source information
* Acquisition information
* Spatial information
* Raster information
* File information

## GridFS

GridFS stores the actual raster files.

This is important because raster files can be several megabytes or larger, while MongoDB documents have size limitations.

The relationship is:

```text
MongoDB Dataset
      │
      └── Observation
              │
              └── file.file_id
                       │
                       ▼
                    GridFS
                       │
                       └── Actual raster file
```

MongoDB therefore stores the metadata/reference, while GridFS stores the actual binary file.

---

# 5. API Base Path

All backend API endpoints use:

```text
/api/v1
```

Therefore, for example:

```text
/api/v1/health
/api/v1/datasets
```

The API version is configured through the application settings.

---

# 6. Health Endpoint

## GET `/api/v1/health`

### Purpose

Checks whether the backend API is running.

### Request

No request body is required.

Example:

```http
GET /api/v1/health
```

### Response

HTTP `200 OK`

```json
{
  "status": "ok"
}
```

### Use

This endpoint is useful for:

* Backend availability checks
* Docker/deployment health checks
* Frontend/backend connectivity testing
* Automated tests

---

# 7. Create Dataset

## POST `/api/v1/datasets`

### Purpose

Creates a new dataset.

A dataset is the logical container for one or more observations/files.

### Request Body

```json
{
  "name": "Chennai Satellite Dataset",
  "dataset_type": "single"
}
```

### Fields

#### `name`

Type:

```text
string
```

Requirements:

```text
minimum length: 1
maximum length: 200
```

#### `dataset_type`

Allowed values:

```text
single
temporal
multimodal
```

These are represented by the `DatasetType` enum.

### Successful Response

HTTP:

```text
201 Created
```

Example:

```json
{
  "dataset_id": "6aa11d3a490053ab6f186d26",
  "name": "Chennai Satellite Dataset",
  "dataset_type": "single",
  "processing": {
    "status": "uploading"
  },
  "observations": []
}
```

### Initial Dataset State

When the dataset is created:

```text
processing.status = uploading
```

and:

```text
observations = []
```

---

# 8. Get Dataset

## GET `/api/v1/datasets/{dataset_id}`

### Purpose

Retrieves a specific dataset and its observations.

### Request

Example:

```http
GET /api/v1/datasets/6aa11d3a490053ab6f186d26
```

### Path Parameter

`dataset_id`

The ID must be a valid MongoDB ObjectId.

### Successful Response

HTTP:

```text
200 OK
```

Example:

```json
{
  "dataset_id": "6aa11d3a490053ab6f186d26",
  "name": "Chennai Satellite Dataset",
  "dataset_type": "single",
  "processing": {
    "status": "uploading"
  },
  "observations": []
}
```

If files have been uploaded, the observations array contains their metadata.

### Invalid Dataset ID

Example:

```http
GET /api/v1/datasets/not-a-valid-id
```

Response:

```text
400 Bad Request
```

```json
{
  "error": {
    "code": "INVALID_DATASET_ID",
    "message": "..."
  }
}
```

### Dataset Does Not Exist

For a syntactically valid but nonexistent ObjectId:

```text
404 Not Found
```

```json
{
  "error": {
    "code": "DATASET_NOT_FOUND",
    "message": "Dataset was not found."
  }
}
```

---

# 9. List Datasets

## GET `/api/v1/datasets`

### Purpose

Returns datasets using pagination.

### Query Parameters

```text
page
page_size
```

Example:

```http
GET /api/v1/datasets?page=1&page_size=20
```

### `page`

Minimum:

```text
1
```

### `page_size`

Minimum:

```text
1
```

### Response

HTTP:

```text
200 OK
```

Example:

```json
{
  "items": [
    {
      "dataset_id": "6aa11d3a490053ab6f186d26",
      "name": "Chennai Satellite Dataset",
      "dataset_type": "single",
      "processing": {
        "status": "uploading"
      },
      "observations": []
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 1
}
```

Pagination prevents the API from returning an unnecessarily large number of datasets in a single response.

---

# 10. Delete Dataset

## DELETE `/api/v1/datasets/{dataset_id}`

### Purpose

Deletes a dataset and cleans up its associated stored files.

### Request

```http
DELETE /api/v1/datasets/6aa11d3a490053ab6f186d26
```

### Processing

The service:

```text
1. Find dataset
       ↓
2. Read observations
       ↓
3. Delete associated GridFS files
       ↓
4. Delete MongoDB dataset
```

### Successful Response

HTTP:

```text
204 No Content
```

There is no response body.

### Result

Both the dataset and its associated GridFS files are removed.

This was specifically tested by checking that the GridFS file no longer exists after dataset deletion.

---

# 11. Upload File

## POST `/api/v1/datasets/{dataset_id}/files`

### Purpose

Uploads a raster file and associates it with a dataset.

### Request

The request uses:

```text
multipart/form-data
```

with the file field:

```text
file
```

Example:

```http
POST /api/v1/datasets/6aa11d3a490053ab6f186d26/files
Content-Type: multipart/form-data
```

### Supported Extensions

The API currently accepts:

```text
.jpg
.jpeg
.png
.tif
.tiff
```

The extension is checked before raster processing.

---

# 12. Upload Processing Flow

The upload process is:

```text
Client
  │
  ▼
FastAPI Upload Endpoint
  │
  ▼
UploadService
  │
  ├── Verify dataset exists
  │
  ├── Check file extension
  │
  ▼
Temporary File
  │
  ▼
Data Engine
  │
  ├── Detect file type
  ├── Validate raster
  └── Extract metadata
  │
  ▼
Delete temporary file
  │
  ▼
GridFS
  │
  └── Store actual uploaded file
  │
  ▼
Create Observation
  │
  ▼
MongoDB
  │
  └── Add observation to dataset
```

The temporary file is only used because the Data Engine operates on file paths.

It is not the permanent file.

---

# 13. Upload Response

### Successful Response

HTTP:

```text
200 OK
```

Example:

```json
{
  "dataset_id": "6aa11d3a490053ab6f186d26",
  "file_id": "6aa11d73490053ab6f186d27",
  "status": "uploaded"
}
```

### Meaning of `file_id`

The `file_id` identifies the file stored in GridFS.

It is also used by the observation metadata to establish the relationship between MongoDB metadata and the actual stored file.

---

# 14. File Validation

The backend performs two levels of validation.

## API-level validation

The file extension is checked:

```text
.jpg
.jpeg
.png
.tif
.tiff
```

Unsupported extensions result in:

```text
UNSUPPORTED_FILE_TYPE
```

## Data Engine validation

After copying the upload to a temporary file, the Data Engine performs:

```text
detect_file_type()
validate_file()
extract_metadata()
```

This prevents an incorrectly named or invalid raster file from being treated as a valid dataset.

---

# 15. Raster Metadata

The extracted metadata is converted into the common `Observation` schema.

The raster information contains:

```json
{
  "width": 1001,
  "height": 1001,
  "band_count": 3,
  "bands": [],
  "dtypes": [
    "uint16",
    "uint16",
    "uint16"
  ],
  "band_names": [
    "band_1",
    "band_2",
    "band_3"
  ],
  "nodata": null,
  "resolution": [
    10,
    10
  ]
}
```

Each band stores:

* Index
* Name
* Data type
* Width
* Height
* NoData value

---

# 16. Spatial Metadata

Spatial information includes:

```text
CRS status
source CRS
native bounds
WGS84 bounds
footprint
centroid
map readiness
map unavailable reason
transform
```

For example:

```json
{
  "crs_status": "valid",
  "source_crs": "EPSG:32631",
  "native_bounds": {
    "west": 590520,
    "south": 5780620,
    "east": 600530,
    "north": 5790630
  },
  "wgs84_bounds": {
    "west": 4.32357,
    "south": 52.16689,
    "east": 4.47285,
    "north": 52.25860
  },
  "centroid_wgs84": [
    4.39821,
    52.21275
  ],
  "map_ready": true
}
```

This allows later map functionality to consume standardized spatial information without having to understand the original raster format.

---

# 17. Source Metadata

The source describes the original uploaded input.

For an uploaded file:

```json
{
  "kind": "local_file",
  "locator": "6aa11d73490053ab6f186d27",
  "display_name": "sample.tif",
  "media_type": "image/tiff"
}
```

The important design decision is that `locator` and `display_name` do **not** reference the temporary processing file.

The temporary path:

```text
C:\Users\...\Temp\tmpxxxxx.tif
```

exists only during processing.

The persistent observation instead references the stored file identity.

---

# 18. Get File

## GET `/api/v1/datasets/{dataset_id}/files/{file_id}`

### Purpose

Retrieves the actual raster file associated with a dataset.

### Request

```http
GET /api/v1/datasets/6aa11d3a490053ab6f186d26/files/6aa11d73490053ab6f186d27
```

### Processing

```text
Request
  ↓
FileService
  ↓
Verify dataset exists
  ↓
Verify file belongs to dataset
  ↓
Get file from GridFS
  ↓
Stream file to client
```

### Successful Response

HTTP:

```text
200 OK
```

The response is streamed using `StreamingResponse`.

For a TIFF:

```text
Content-Type: image/tiff
```

The response also contains a download disposition similar to:

```text
Content-Disposition: attachment; filename="sample.tif"
```

### Why streaming is used

The backend should not unnecessarily load the entire raster into memory.

Instead, the file is read in chunks and streamed to the client.

The current chunk size is:

```text
1 MB
```

---

# 19. Delete File

## DELETE `/api/v1/datasets/{dataset_id}/files/{file_id}`

### Purpose

Deletes a file from both:

* GridFS
* Dataset observations in MongoDB

### Processing

```text
DELETE request
      ↓
Verify dataset
      ↓
Verify file belongs to dataset
      ↓
Delete GridFS file
      ↓
Remove observation from MongoDB
```

### Successful Response

HTTP:

```text
204 No Content
```

The dataset itself remains.

Only the selected file/observation is removed.

---

# 20. File Ownership Validation

A file cannot simply be retrieved or deleted by its `file_id`.

The service first checks whether that file belongs to the requested dataset.

Conceptually:

```text
Dataset A
 └── File X

GET Dataset B / File X
          ↓
     FILE_NOT_FOUND
```

This prevents a client from accessing a file through a different dataset ID.

---

# 21. File Not Found

For a nonexistent file:

```text
404 Not Found
```

with:

```json
{
  "error": {
    "code": "FILE_NOT_FOUND",
    "message": "File was not found."
  }
}
```

This is tested for both:

```text
GET file
DELETE file
```

---

# 22. Error Handling

The backend uses standardized error codes.

Current error codes include:

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

The API wraps application errors into a common structure:

```json
{
  "error": {
    "code": "DATASET_NOT_FOUND",
    "message": "Dataset was not found.",
    "details": null
  }
}
```

This gives the frontend a predictable error format.

---

# 23. Request Validation

FastAPI/Pydantic handles request validation.

For example, an invalid dataset creation request:

```json
{
  "name": "",
  "dataset_type": "single"
}
```

fails because `name` requires at least one character.

The API returns:

```text
422 Unprocessable Entity
```

with:

```text
VALIDATION_ERROR
```

---

# 24. Dependency Injection

The API uses FastAPI dependency injection to obtain services.

Conceptually:

```text
Route
  ↓
get_dataset_service()
  ↓
DatasetService
```

The service is constructed with storage implementations.

For example:

```text
DatasetService
 ├── MongoDBDatasetStorage
 └── GridFSFileStorage
```

This keeps route functions thin.

The route handles HTTP concerns while the service handles business logic.

---

# 25. Storage Interfaces

The backend defines abstractions for storage.

## FileStorage

Provides operations such as:

```text
save()
get()
delete()
```

The current implementation is:

```text
GridFSFileStorage
```

## DatasetStorage

Provides operations such as:

```text
create()
get()
list()
delete()
add_observation()
remove_observation()
```

The current implementation is:

```text
MongoDBDatasetStorage
```

This allows the underlying storage implementation to be replaced later without rewriting the service layer.

---

# 26. Configuration

Application configuration is centralized in:

```text
app/core/config.py
```

Important settings include:

```text
app_name
app_version
api_prefix
mongodb_uri
mongodb_database
```

MongoDB configuration can be supplied through environment variables.

This avoids hard-coding deployment-specific configuration into application code.

---

# 27. Test Suite

The backend currently has:

```text
16 tests
```

All tests pass:

```text
16 passed
```

There is currently one warning from the Starlette/AnyIO dependency stack.

It originates from:

```text
starlette/testclient.py
```

and is not from SatQuery application code.

---

# 28. Tested Functionality

The test suite covers:

### Dataset

```text
✓ Create dataset
✓ Get dataset
✓ List datasets
✓ Delete dataset
✓ Invalid dataset ID
✓ Dataset not found
✓ Dataset request validation
```

### File

```text
✓ Upload file
✓ Retrieve file
✓ Delete file
✓ Unsupported file type
✓ Upload to nonexistent dataset
✓ File not found
✓ Delete nonexistent file
```

### Storage Cleanup

```text
✓ Dataset deletion removes GridFS files
```

### API

```text
✓ Health endpoint
```

---

# 29. Test Isolation

A pytest fixture is used to clean the database before and after tests.

The cleanup covers:

```text
datasets
GridFS files
GridFS chunks
```

This prevents data created by one test from affecting another test.

The test lifecycle is:

```text
Clean database
      ↓
Run test
      ↓
Clean database
```

---

# 30. Current Project Structure

The backend follows this organization:

```text
backend/
│
├── app/
│   ├── api/
│   │   ├── dependencies.py
│   │   ├── router.py
│   │   └── routes/
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── exceptions.py
│   │
│   ├── schemas/
│   │   ├── common/
│   │   │   ├── acquisition.py
│   │   │   ├── dataset.py
│   │   │   ├── error.py
│   │   │   ├── file.py
│   │   │   ├── observation.py
│   │   │   ├── pagination.py
│   │   │   ├── processing.py
│   │   │   ├── raster.py
│   │   │   ├── source.py
│   │   │   └── spatial.py
│   │   ├── dataset.py
│   │   └── upload.py
│   │
│   ├── services/
│   │   ├── dataset_service.py
│   │   ├── file_service.py
│   │   ├── metadata_mapper.py
│   │   └── upload_service.py
│   │
│   ├── storage/
│   │   ├── interfaces/
│   │   │   ├── dataset_storage.py
│   │   │   └── file_storage.py
│   │   ├── implementations/
│   │   │   ├── gridfs_file_storage.py
│   │   │   └── mongodb_dataset_storage.py
│   │   └── mongodb.py
│   │
│   └── main.py
│
├── data_engine/
│
├── tests/
│   ├── conftest.py
│   ├── sample.tif
│   ├── test_datasets.py
│   └── test_health.py
│
├── pyproject.toml
└── requirements.txt
```

---

# 31. Complete API Summary

| Method | Endpoint                                        | Purpose                | Success |
| ------ | ----------------------------------------------- | ---------------------- | ------- |
| GET    | `/api/v1/health`                                | Health check           | 200     |
| POST   | `/api/v1/datasets`                              | Create dataset         | 201     |
| GET    | `/api/v1/datasets`                              | List datasets          | 200     |
| GET    | `/api/v1/datasets/{dataset_id}`                 | Get dataset            | 200     |
| DELETE | `/api/v1/datasets/{dataset_id}`                 | Delete dataset + files | 204     |
| POST   | `/api/v1/datasets/{dataset_id}/files`           | Upload raster          | 200     |
| GET    | `/api/v1/datasets/{dataset_id}/files/{file_id}` | Retrieve raster        | 200     |
| DELETE | `/api/v1/datasets/{dataset_id}/files/{file_id}` | Delete raster          | 204     |

---

# 32. End-to-End Example

A typical workflow is:

### Step 1 — Create dataset

```http
POST /api/v1/datasets
```

```json
{
  "name": "Sentinel Dataset",
  "dataset_type": "single"
}
```

Backend creates:

```text
Dataset ID
```

---

### Step 2 — Upload TIFF

```http
POST /api/v1/datasets/{dataset_id}/files
```

with:

```text
sample.tif
```

Backend:

```text
Validate extension
       ↓
Create temporary file
       ↓
Data Engine validation
       ↓
Extract raster metadata
       ↓
Delete temporary file
       ↓
Store actual file in GridFS
       ↓
Create Observation
       ↓
Store observation in MongoDB
```

---

### Step 3 — Get dataset

```http
GET /api/v1/datasets/{dataset_id}
```

The response now contains:

```text
Dataset
 └── Observation
      ├── Source
      ├── Acquisition
      ├── Spatial
      ├── Raster
      └── File
```

---

### Step 4 — Retrieve file

```http
GET /api/v1/datasets/{dataset_id}/files/{file_id}
```

The backend verifies ownership and streams the file from GridFS.

---

### Step 5 — Delete file

```http
DELETE /api/v1/datasets/{dataset_id}/files/{file_id}
```

The file is removed from GridFS and the observation is removed from MongoDB.

---

### Step 6 — Delete dataset

```http
DELETE /api/v1/datasets/{dataset_id}
```

The dataset and its associated GridFS files are removed.

---

# 33. Phase 1 Backend Completion

The backend foundation now provides the required infrastructure for the next SatQuery phases.

The resulting foundation is:

```text
                  SatQuery AI
                       │
                       ▼
                    FastAPI
                       │
                       ▼
                    Services
                       │
              ┌────────┴────────┐
              ▼                 ▼
          MongoDB             GridFS
        Dataset Metadata     Raster Files
              │                 │
              └────────┬────────┘
                       ▼
                 Observation
                       │
                       ▼
              Future AI Pipeline
```

The backend is therefore ready to serve as the foundation for subsequent functionality such as query processing, model inference, and advanced remote-sensing analysis.

---

# 34. Known Technical Consideration

Dataset/file operations currently involve multiple storage operations.

For example:

```text
Delete GridFS file
       ↓
Delete MongoDB observation
```

and:

```text
Delete GridFS files
       ↓
Delete MongoDB dataset
```

These operations are not currently a single distributed transaction.

This is acceptable for the current Phase 1 foundation, but transactional/rollback behavior can be considered later as the system becomes more production-critical.

The current implementation prioritizes the storage abstraction and clear separation of responsibilities.
