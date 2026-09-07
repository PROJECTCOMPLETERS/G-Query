# SatQuery AI — API Error Handling

## 1. Purpose

All Phase 1 APIs use a consistent error-response structure.

This allows the frontend to handle backend failures predictably.

---

# 2. Error Response Structure

```json
{
  "error": {
    "code": "DATASET_NOT_FOUND",
    "message": "Dataset was not found.",
    "details": null
  }
}
```

---

# 3. Error Fields

### `code`

Machine-readable error identifier.

Example:

```text
DATASET_NOT_FOUND
```

### `message`

Human-readable explanation.

### `details`

Optional additional information.

It may be `null` when no additional information is required.

---

# 4. Standard Error Codes

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

---

# 5. HTTP Status Codes

| HTTP Status | Meaning                                    |
| ----------- | ------------------------------------------ |
| `200`       | Successful operation                       |
| `201`       | Resource created                           |
| `204`       | Successful operation with no response body |
| `400`       | Invalid request                            |
| `404`       | Resource not found                         |
| `415`       | Unsupported media/file type                |
| `422`       | Request validation failure                 |
| `500`       | Internal server error                      |

The exact status code must correspond to the actual failure rather than being chosen arbitrarily.

---

# 6. Example Errors

## Dataset Not Found

```json
{
  "error": {
    "code": "DATASET_NOT_FOUND",
    "message": "Dataset was not found.",
    "details": null
  }
}
```

HTTP:

```text
404 Not Found
```

---

## Unsupported File

```json
{
  "error": {
    "code": "UNSUPPORTED_FILE_TYPE",
    "message": "The uploaded file type is not supported.",
    "details": {
      "filename": "example.xyz"
    }
  }
}
```

HTTP:

```text
415 Unsupported Media Type
```

---

## Validation Failure

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request contains invalid data.",
    "details": null
  }
}
```

HTTP:

```text
422 Unprocessable Entity
```

---

# 7. Error Responsibility

```text
FastAPI
   │
   ├── Request validation
   │
   ├── Error translation
   │
   └── Consistent API response
```

Internal implementation errors should not expose:

* MongoDB connection details
* GridFS internals
* Stack traces
* Internal file paths
* Sensitive implementation information

---

# 8. Frontend Handling

The frontend should primarily use:

```text
error.code
```

for programmatic behavior and:

```text
error.message
```

for user-facing messaging.

Example:

```text
DATASET_NOT_FOUND
        ↓
Show dataset unavailable message
```

---

# 9. Final Principle

All Phase 1 endpoints should return predictable success and error structures.

The API is the stable communication contract between the frontend and backend.

**Status: FINALIZED**
