# ADR-001: Use Microsoft Fabric as Primary Data Platform

## Status
Accepted

## Context
The Africa CDC Cholera CDR MVP requires a scalable, cloud-native data platform that can handle:

- Large volumes of PDF documents and extracted data
- Complex epidemiological analytics and ML forecasting
- Interactive dashboards with real-time updates
- Multi-environment deployment (dev/test/prod)
- Integration with existing Microsoft ecosystem

## Decision
Adopt Microsoft Fabric as the primary data platform for the Cholera CDR MVP.

## Rationale
Microsoft Fabric provides:

1. **Integrated Platform**: Combines data lake, warehouse, and analytics in one platform
2. **OneLake Storage**: Built-in lakehouse with Delta Lake support
3. **Scalable Compute**: Auto-scaling Spark notebooks and warehouse compute
4. **Power BI Integration**: Native integration for dashboards
5. **Security & Governance**: Enterprise-grade security and compliance
6. **Cost Efficiency**: Pay-as-you-go pricing model
7. **Microsoft Ecosystem**: Seamless integration with Azure AD and other services

## Alternatives Considered

1. **AWS + Custom Stack**: 
   - Pros: More flexible, potentially cheaper
   - Cons: Higher complexity, more integration work

2. **Google Cloud Platform**:
   - Pros: Strong ML capabilities
   - Cons: Less integrated BI tools, smaller ecosystem

3. **On-Premise Solution**:
   - Pros: Full control
   - Cons: High maintenance costs, limited scalability

## Consequences

### Positive
- Reduced development complexity through integrated platform
- Built-in scalability and performance optimization
- Strong security and compliance features
- Simplified operations and maintenance

### Negative
- Vendor lock-in to Microsoft ecosystem
- Learning curve for team members unfamiliar with Fabric
- Potential cost increases at scale

### Neutral
- Requires Microsoft Fabric capacity (F64+ recommended)
- Team training needed for Fabric-specific features
- Migration path needed if platform changes in future
