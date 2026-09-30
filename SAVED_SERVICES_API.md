# Saved Services API Design

## Authentication

All endpoints require JWT authentication.

Authorization header:

Authorization: Bearer <access_token>

---

## 1. Save Service

POST /api/v1/saved-services/

### Request

{
    "service": 1
}

### Response — Success

HTTP 201 Created

{
    "id": 1,
    "service": 1,
    "created_at": "2026-09-30T12:00:00Z"
}

### Permissions

Authenticated customers only.

### Errors

401 — Authentication required
403 — Customer permission required
404 — Service not found
400 — Service already saved

---

## 2. List Saved Services

GET /api/v1/saved-services/

### Response — Success

HTTP 200 OK

{
    "count": 1,
    "results": [
        {
            "id": 1,
            "service": 1,
            "created_at": "2026-09-30T12:00:00Z"
        }
    ]
}

### Permissions

Authenticated customers can view only their own saved services.

### Errors

401 — Authentication required

---

## 3. Remove Saved Service

DELETE /api/v1/saved-services/{id}/

### Response — Success

HTTP 204 No Content

### Permissions

A customer can delete only their own saved-service record.

### Errors

401 — Authentication required
403 — Permission denied
404 — Saved service not found

---

## Security

- JWT authentication required.
- Customer ownership enforced.
- Object-level authorization enforced.
- Duplicate records prevented by database unique constraint.
- Service existence validated.
- Unauthorized access must not expose another customer's saved services.

---

## Database Integrity

Unique constraint:

(customer, service)

This prevents duplicate saved-service records, including duplicate concurrent requests.

---

## Background Processing

When a saved service becomes unavailable:

Service Updated
    ?
Celery Task
    ?
Find SavedService records
    ?
Create Notification
    ?
Customer

---

## Status Codes

201 — Saved successfully
200 — Saved services retrieved
204 — Saved service removed
400 — Validation / duplicate save
401 — Authentication required
403 — Permission denied
404 — Resource not found
