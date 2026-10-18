# Support FAQ
Version: 1.8
Updated: 2026-09-20
Owner: Support Enablement

## Can Support-L1 restart production services?
No. Support-L1 can inspect health and dashboards but cannot restart production services.

## Is Redis the authoritative source for calculation status?
No. PostgreSQL is the source of truth.

## What should I do if a question is not covered by the documentation?
Do not invent an operational procedure.
State that the available documentation is insufficient and escalate to the relevant owner.

## Can engineers deploy directly from their laptops?
No. Production deployments must use the approved CI/CD workflow.

## Should a service be restarted whenever a timeout occurs?
No. A timeout does not automatically justify a restart. Follow the incident-specific runbook and inspect health and resource conditions first.
