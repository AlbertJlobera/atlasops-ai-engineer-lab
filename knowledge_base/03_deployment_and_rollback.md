# Deployment and Rollback Policy
Version: 3.0
Updated: 2026-08-30
Owner: Release Engineering

## Normal deployment
Production deployments use the approved CI/CD workflow.

Direct manual deployment from a developer workstation is prohibited.

## Rollback
An automatic rollback may be initiated by the deployment platform when:
- the post-deployment health check fails,
- HTTP 5xx rate exceeds 5% for five consecutive minutes,
- the new version cannot establish required database connectivity.

A human operator may manually initiate rollback when:
- there is confirmed functional regression,
- there is a serious production defect attributable to the new release,
- the incident commander determines rollback is the safest recovery action.

## Important limitation
Rollback must NOT be used automatically when the release includes a non-backward-compatible database migration.

For a non-backward-compatible migration, follow the database recovery procedure and obtain approval from the incident commander and database owner.

## Verification after rollback
Verify:
1. service health,
2. error rate,
3. core business transaction,
4. Kafka consumer status if applicable.

The incident timeline must record the rollback and its result.
