# SatQuery AI — Health API

## 1. Endpoint

```http
GET /api/v1/health
```

## 2. Purpose

Determines whether the SatQuery backend is running.

---

## 3. Request

No request body is required.

---

## 4. Successful Response

HTTP:

```text
200 OK
```

Response:

```json
{
  "status": "ok"
}
```

---

## 5. Responsibility

The health endpoint belongs to the FastAPI API layer.

It should remain lightweight and should not perform expensive satellite processing.

**Status: FINALIZED**
