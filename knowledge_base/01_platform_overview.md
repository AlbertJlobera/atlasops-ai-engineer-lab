# AtlasOps Platform — Technical Overview
Version: 2.3
Updated: 2026-09-12
Owner: Platform Engineering

## Overview
AtlasOps is composed of several internal services.

### api-gateway
Entry point for client and internal API requests.
Health endpoint:
`GET /health`

A healthy response returns HTTP 200 and:
`{"status": "ok"}`

### calculation-service
Executes business calculations requested through the platform.

The service exposes:
- `POST /v1/calculations`
- `GET /v1/calculations/{calculation_id}`
- `GET /health`

Requests are asynchronous. A successful submission returns HTTP 202 with a calculation identifier.

### event-worker
Consumes messages from the Kafka topic `atlas.calculation.events`.

The normal consumer group is:
`atlas-event-worker-v2`

Operational alerts are triggered when consumer lag remains above 5,000 messages for more than 10 minutes.

### PostgreSQL
Stores operational state and calculation metadata.

Production access must never be performed using shared credentials.

### Redis
Used for short-lived cache entries and distributed locks.

Redis must not be treated as the source of truth for calculation state.
