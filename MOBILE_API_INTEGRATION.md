# Mobile API Integration

## Architecture

Mobile Application
        ↓
     HTTPS
        ↓
   REST API
        ↓
      JWT
        ↓
     Django
        ↓
   PostgreSQL

## Authentication Flow

1. Mobile application sends username/email and password.
2. Django validates the credentials.
3. Django returns Access Token and Refresh Token.
4. Mobile stores the tokens securely.
5. Mobile sends Access Token in API requests.

Authorization Header:

Authorization: Bearer <access_token>

## Token Refresh Flow

1. Access Token expires.
2. API returns HTTP 401 Unauthorized.
3. Mobile sends Refresh Token.
4. Django validates the Refresh Token.
5. Django generates a new Access Token.
6. Mobile retries the failed API request.

## API Communication

Mobile communicates with Django through HTTPS REST APIs.

Example:

POST /api/v1/auth/login/
GET /api/v1/profile/
GET /api/v1/services/
POST /api/v1/bookings/

## Expected Response

{
    "success": true,
    "message": "Request successful",
    "data": {}
}