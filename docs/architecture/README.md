# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records for the Cholera CDR MVP project.

## What are ADRs?

Architecture Decision Records (ADRs) capture important architectural decisions made during the development process. Each ADR documents:

- The context and problem being addressed
- The decision made and its rationale
- Any alternatives considered and rejected
- The consequences of the decision

## ADR Format

Each ADR follows this structure:

```
# ADR-XXX: [Title]

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Context
[What is the situation or problem?]

## Decision
[What decision was made?]

## Rationale
[Why was this decision made?]

## Alternatives Considered
[What other options were considered?]

## Consequences
[What are the results of this decision?]
```

## Current ADRs

- **ADR-001**: Use Microsoft Fabric as primary data platform
- **ADR-002**: Implement Medallion Architecture (Bronze-Silver-Gold)
- **ADR-003**: Choose Prophet for time series forecasting
- **ADR-004**: Design star schema for analytical queries
- **ADR-005**: Implement comprehensive quality assurance framework

## ADR Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| 001 | Microsoft Fabric Platform | Accepted | 2025-02-10 |
| 002 | Medallion Architecture | Accepted | 2025-02-10 |
| 003 | Prophet Forecasting | Accepted | 2025-02-10 |
| 004 | Star Schema Design | Accepted | 2025-02-10 |
| 005 | Quality Assurance Framework | Accepted | 2025-02-10 |

## Process

1. Create new ADRs for significant architectural decisions
2. Review ADRs with the team before acceptance
3. Update ADRs when decisions change
4. Maintain ADRs as living documentation
