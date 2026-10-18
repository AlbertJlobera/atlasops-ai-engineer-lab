# Production Access and Security
Version: 5.2
Updated: 2026-09-18
Owner: Security Engineering

## Production access
All production access is identity-based and auditable.

Shared production accounts are prohibited.

## Roles
### Support-L1
May:
- view service health,
- view dashboards,
- read incident metadata.

May not:
- restart production services,
- execute administrative operations,
- query production databases directly.

### Support-L2
May:
- perform all Support-L1 actions,
- execute approved diagnostic tools,
- restart a service when the runbook explicitly allows it.

May not:
- modify production database records directly,
- change IAM policies,
- bypass approval controls.

### Platform-Admin
May execute administrative operations within the approved operational procedures.

Privileged actions must be logged.

## Break-glass access
Emergency elevated access:
- requires a declared SEV-1 or an approved security incident,
- must be time-limited,
- requires justification,
- is audited,
- must be reviewed after the incident.

## Secrets
API keys, database passwords and tokens must not be stored in source code or committed to Git repositories.
