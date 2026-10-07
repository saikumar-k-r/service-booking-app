\# Mobile API Reliability



\## Objective

Keep APIs reliable when mobile devices have slow networks, retries,

duplicate requests, and temporary disconnections.



\## Retry Scenarios

\- Network timeout

\- Temporary connection loss

\- HTTP 502/503/504

\- App resume after background execution

\- Duplicate submit/tap



\## Idempotency

POST operations that create business resources should use an

`Idempotency-Key`.



The server stores:

\- User

\- Idempotency key

\- Request fingerprint

\- Response status

\- Response body

\- Completion state

\- Timestamps



Same key + same request:

\- Returns the original response.



Same key + different request:

\- Returns HTTP 409 Conflict.



\## Pagination

Sync APIs use cursor pagination.



Example:



GET /api/v1/reliability/sync/?limit=20



\## Versioning

Synchronized resources contain:

\- version

\- updated\_at

\- deleted



\## Incremental Sync



GET /api/v1/reliability/sync/?since=2026-10-07T10:00:00Z



Only records updated after the supplied timestamp are returned.



\## Partial Failure

When a mobile request times out, retry using the exact same

Idempotency-Key and request body.



Do not generate a new key for the same logical operation.



\## Client Retry Rules



1\. Generate one unique UUID for each logical POST.

2\. Send it as `Idempotency-Key`.

3\. Reuse the same key during retries.

4\. Do not retry validation errors such as HTTP 400.

5\. Retry temporary failures such as 502/503/504.

6\. Use exponential backoff.

7\. Stop after a reasonable retry limit.

8\. Persist the last successful sync cursor/timestamp.

9\. Resume synchronization from the last successful position.

10\. Treat a replayed successful response as success.



\## API Endpoints



POST /api/v1/reliability/reliable-operation/



GET /api/v1/reliability/sync/



\## Postman Demo



\### First Request



Header:



Idempotency-Key: mobile-request-001



Body:



{

&#x20;   "booking\_id": 101

}



Expected:



HTTP 200

Idempotent-Replay: false



\### Duplicate Request



Send the exact same request again.



Expected:



HTTP 200

Idempotent-Replay: true



\### Conflicting Request



Reuse the same key with:



{

&#x20;   "booking\_id": 999

}



Expected:



HTTP 409 Conflict



\## Sync Demo



GET:



/api/v1/reliability/sync/?limit=20



Optional:



/api/v1/reliability/sync/?since=2026-10-07T10:00:00Z



Verify:

\- cursor pagination

\- version

\- updated\_at

\- deleted flag

\- resource data



\## Reliability Test Scenarios



\- Missing idempotency key

\- Successful POST

\- Duplicate POST

\- Same key with different payload

\- Incremental sync

\- Deleted resource synchronization

\- Full automated test suite

