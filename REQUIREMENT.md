# Saved Services Feature — Requirement Analysis

## 1. Problem

Customers may find services that they want to use later but currently have no way to save or bookmark them.

The Saved Services feature allows customers to save services for future reference, remove saved services, and view their saved services.

Customers should also receive a notification when a saved service becomes unavailable.

---

## 2. Users

### Customer
- Save an available service.
- View saved services.
- Remove a saved service.
- Receive notification when a saved service becomes unavailable.

### Provider
- Manage their own services.
- Cannot access another customer's saved services.

### Administrator
- Can manage services according to existing administrator permissions.
- Does not automatically gain access to another customer's personal saved-service list unless explicitly authorized.

---

## 3. Functional Requirements

### FR-01 — Save Service
An authenticated customer can save an existing service.

### FR-02 — Duplicate Prevention
A customer cannot save the same service more than once.

### FR-03 — List Saved Services
An authenticated customer can retrieve their saved services.

### FR-04 — Remove Saved Service
An authenticated customer can remove one of their saved services.

### FR-05 — Service Validation
A service must exist before it can be saved.

### FR-06 — Customer Ownership
Customers can access only their own saved services.

### FR-07 — Availability Notification
When a saved service becomes unavailable, the system should create/send a notification to customers who saved that service.

### FR-08 — Authentication
All Saved Services APIs require JWT authentication.

### FR-09 — Authorization
Only customers can create and manage their saved services.

---

## 4. Non-Functional Requirements

### Security
- JWT authentication must be required.
- Object-level access control must prevent IDOR.
- Customers must not access another customer's saved services.
- Input validation must be applied.

### Performance
- Saved services should use efficient database queries.
- Customer and service relationships should use appropriate database indexes/constraints.
- List APIs should support pagination through the project's existing pagination architecture.

### Reliability
- Duplicate saves must be prevented at database level.
- Notification processing should use Celery and Redis.
- Background task failures should not corrupt saved-service data.

### Maintainability
- Follow the existing Django/DRF architecture.
- Business logic should be implemented through the service layer.
- APIs should follow the existing /api/v1/ structure.
- Existing response and error-handling conventions should be followed.

---

## 5. Business Rules

1. Only authenticated customers can save services.
2. A customer can save a service only once.
3. The same service can be saved by multiple customers.
4. A customer can remove only their own saved service.
5. A customer can view only their own saved services.
6. A non-existing service cannot be saved.
7. Duplicate save requests must be rejected safely.
8. When a saved service becomes unavailable, affected customers should receive a notification.
9. Notification processing should happen asynchronously through Celery.
10. Database integrity must be enforced using appropriate constraints.

---

## 6. Edge Cases

### EC-01 — Duplicate Save
Customer attempts to save the same service twice.

Expected:
- Request is rejected.
- No duplicate database record is created.

### EC-02 — Service Not Found
Customer attempts to save a non-existing service.

Expected:
- Return HTTP 404.

### EC-03 — Unauthorized User
Unauthenticated user attempts to access Saved Services APIs.

Expected:
- Return HTTP 401.

### EC-04 — Non-Customer User
Provider or unauthorized role attempts to create a saved service.

Expected:
- Return HTTP 403.

### EC-05 — Another Customer's Saved Service
Customer attempts to delete another customer's saved service.

Expected:
- Access is denied.

### EC-06 — Remove Non-Existing Saved Service
Customer attempts to delete a saved-service record that does not exist.

Expected:
- Return HTTP 404.

### EC-07 — Service Becomes Unavailable
A service previously saved by customers becomes inactive/unavailable.

Expected:
- Celery task identifies affected customers.
- Notification is created for affected customers.

### EC-08 — Repeated Notification Task
The background task is retried.

Expected:
- Duplicate notifications should be avoided where appropriate.

### EC-09 — Concurrent Save
Two requests attempt to save the same service for the same customer simultaneously.

Expected:
- Only one SavedService record exists.
- Database uniqueness constraint protects data integrity.

---

## 7. Expected API Endpoints

POST   /api/v1/saved-services/

GET    /api/v1/saved-services/

DELETE /api/v1/saved-services/{id}/

---

## 8. Background Workflow

Service becomes unavailable
        ?
Detect affected SavedService records
        ?
Celery Task
        ?
Create Notification
        ?
Customer receives notification

---

## 9. Acceptance Criteria

- Requirement is documented.
- Database model is implemented.
- Unique customer/service relationship is enforced.
- APIs are implemented.
- JWT authentication is enforced.
- Customer ownership is enforced.
- Service layer is used.
- Celery integration is implemented.
- Notifications are created.
- Duplicate saves are prevented.
- Negative scenarios are tested.
- Automated tests pass.
- API documentation is updated.
- Git history remains clean.
