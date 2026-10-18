# Known Issues
Version: 2.7
Updated: 2026-09-28
Owner: Engineering Support

## KI-104 — Duplicate status events
Affected component: event-worker
Status: Open

Under rare retry conditions, the worker may receive duplicate calculation status events.

Expected handling:
Consumers must treat events as idempotent using `event_id`.

Do not delete duplicated Kafka messages manually.

## KI-119 — Stale Redis calculation status
Affected component: Redis cache
Status: Mitigated

A user may briefly see a stale calculation status after processing completes.

The authoritative status is stored in PostgreSQL.

If Redis and PostgreSQL disagree, use PostgreSQL as the source of truth.

## KI-127 — Health check healthy while one calculation type degrades
Affected component: calculation-service
Status: Investigating

The `/health` endpoint can remain healthy while one calculation type experiences increased timeouts.

For suspected CALC-017 incidents, do not rely exclusively on `/health`; also inspect error rate and latency by calculation type.
