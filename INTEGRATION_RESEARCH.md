# External Integration Research

## Provider
HTTPBin — HTTP Request & Response Testing Service

## Purpose
HTTPBin is used as a mock/sandbox HTTP service for testing external
API integrations without depending on a production provider.

## Base URL
https://httpbin.org

## Endpoint
POST /anything

## Authentication
Authentication is not required for the HTTPBin sandbox.

The Django application does not hardcode or expose any external
credentials. If a future provider requires credentials, they will
be loaded only from environment variables.

## Request Example

POST https://httpbin.org/anything

Content-Type: application/json

{
  "service_id": 101,
  "customer_id": 20,
  "action": "availability_check"
}

## Response
HTTPBin echoes the submitted request and returns HTTP 200.

## Failure Testing

HTTPBin can simulate:
- HTTP 500: /status/500
- HTTP 503: /status/503
- Delayed response: /delay/5

## Integration Requirements

- External API URL from environment variables
- Timeout required
- Retry handling
- Safe exception handling
- No secrets in logs
- Response validation
- Automated positive and negative tests
