\# Reliability API



\## Authentication



All endpoints require:



Authorization: Bearer <access\_token>



\---



\## 1. Reliable POST



POST http://127.0.0.1:8000/api/v1/reliability/reliable-operation/



Headers:



Content-Type: application/json

Idempotency-Key: mobile-request-001



Body:



{

&#x20;   "booking\_id": 101

}



\### First Request



HTTP 200



Header:



Idempotent-Replay: false



\### Duplicate Request



Send the same key and body again.



HTTP 200



Header:



Idempotent-Replay: true



\### Conflicting Request



Use the same key with a different body.



HTTP 409 Conflict



\---



\## 2. Incremental Sync



GET http://127.0.0.1:8000/api/v1/reliability/sync/?limit=20



Optional:



GET http://127.0.0.1:8000/api/v1/reliability/sync/?since=2026-10-07T10:00:00Z



Response includes:



\- sync

\- items

\- id

\- type

\- version

\- updated\_at

\- deleted

\- data

\- next cursor

\- previous cursor



\---



\## Mobile Retry Flow



1\. Create Idempotency-Key UUID.

2\. Send POST request.

3\. If successful, stop.

4\. If timeout occurs, retry with the SAME key.

5\. If 502/503/504 occurs, retry with backoff.

6\. Never create a new key for the same operation.

7\. Resume sync using the last successful cursor.

