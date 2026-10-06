# External API Integration Setup

## Objective

Production-style integration between Django REST APIs and an external HTTP service with timeout, retry, validation, safe error handling, logging, and automated tests.

## Selected Provider

HTTPBin sandbox.

Base URL:

https://httpbin.org

Endpoint:

POST /anything

Authentication:

No authentication is required for the HTTPBin sandbox.

## Django API

POST:

/api/v1/integrations/external/check/

Authentication:

JWT/Bearer authentication is required.

Request:

```json
{
    "service_id": 101
}