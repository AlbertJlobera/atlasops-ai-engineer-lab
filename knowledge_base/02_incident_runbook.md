# Incident Runbook
Version: 4.1
Updated: 2026-09-25
Owner: Site Reliability Engineering

## Severity
SEV-1: complete outage or critical production impact.
SEV-2: major degradation with workaround unavailable or severely limited.
SEV-3: partial degradation with viable workaround.
SEV-4: minor issue or informational incident.

## CALC-017 — Calculation timeout
Meaning:
The calculation-service exceeded the internal processing timeout.

First checks:
1. Confirm `calculation-service` health.
2. Check CPU and memory saturation.
3. Check PostgreSQL connection pool utilization.
4. Inspect the request duration distribution.
5. Check whether the error is isolated to a specific calculation type.

Do not immediately restart the service if health checks are passing.

Escalation:
- Escalate to the calculation-service owner if CALC-017 affects more than 5% of calculations for 10 consecutive minutes.
- Declare SEV-2 if more than 20% of calculations fail for 10 consecutive minutes.
- Declare SEV-1 if the service becomes unavailable to all production users.

## Kafka consumer lag
If `atlas-event-worker-v2` exceeds 5,000 messages of lag for more than 10 minutes:
1. Confirm brokers are reachable.
2. Check whether the consumer group has active members.
3. Review processing latency.
4. Review recent deployments.
5. Scale workers only after confirming the downstream database is not saturated.

Do not purge the topic as a remediation step.

## Database connection exhaustion
Symptoms may include:
- HTTP 503,
- connection acquisition timeouts,
- increased request latency.

Actions:
1. Check active vs maximum connections.
2. Identify long-running transactions.
3. Verify application pool configuration.
4. Do not increase the database maximum connections as the first response.
