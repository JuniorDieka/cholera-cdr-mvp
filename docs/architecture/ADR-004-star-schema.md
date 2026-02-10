# ADR-004: Design star schema for analytical queries

## Status
Accepted

## Context
The Cholera CDR MVP requires a robust analytical data model that supports:

- Fast and efficient querying for epidemiological analysis
- Power BI semantic model integration
- Historical trend analysis and reporting
- Multi-dimensional analysis (by country, time, metrics)
- Scalability for growing data volumes
- Clear business semantics for public health officials

The current Silver layer provides cleansed data but lacks an optimized structure for analytical queries.

## Decision
Implement a star schema dimensional model in the Gold layer with conformed dimensions and fact tables.

## Rationale

### Star Schema Benefits
1. **Query Performance**: Optimized for analytical queries with minimal joins
2. **Business Semantics**: Clear, business-friendly table and column names
3. **Scalability**: Handles large data volumes efficiently
4. **Power BI Integration**: Native support for semantic models
5. **Flexibility**: Easy to add new dimensions and metrics
6. **Consistency**: Conformed dimensions ensure data consistency across reports

### Epidemiological Suitability
- **Time Dimension**: Supports epidemiological weeks and calendar dates
- **Geography Dimension**: Hierarchical country/region structure
- **Report Dimension**: Tracks data sources and quality metrics
- **Fact Tables**: Separate tables for cases and deaths for different analysis needs

## Alternatives Considered

### 1. Snowflake Schema
**Pros:**
- More normalized structure
- Reduces data redundancy
- Good for very large datasets

**Cons:**
- More complex queries with additional joins
- Slower query performance
- Over-engineering for current data volumes
- More complex maintenance

### 2. Flat Denormalized Tables
**Pros:**
- Simple structure
- Fast queries (no joins)
- Easy to understand

**Cons:**
- Data redundancy
- Maintenance complexity
- Inconsistent data risk
- Poor scalability

### 3. Data Vault Modeling
**Pros:**
- Excellent for historical tracking
- Audit-friendly structure
- Supports slowly changing dimensions

**Cons:**
- Complex to implement and maintain
- Overkill for current requirements
- Steep learning curve
- Limited Power BI optimization

### 4. Operational Data Store (ODS)
**Pros:**
- Real-time data availability
- Transaction-focused structure
- Good for operational reporting

**Cons:**
- Not optimized for analytics
- Complex for historical analysis
- Higher storage requirements
- Limited dimensional analysis

## Consequences

### Positive
- **Query Performance**: Significant improvement in analytical query speed
- **Business Understanding**: Clear, intuitive structure for analysts
- **Power BI Integration**: Seamless semantic model creation
- **Scalability**: Handles growth in data volume and complexity
- **Consistency**: Enforced data quality through conformed dimensions
- **Flexibility**: Easy to add new analytical capabilities

### Negative
- **Storage Requirements**: Increased storage due to dimension tables
- **ETL Complexity**: Additional transformation logic required
- **Maintenance Overhead**: Need to maintain dimensional hierarchies
- **Learning Curve**: Team needs to understand star schema concepts

### Neutral
- **Development Time**: Initial implementation requires additional ETL development
- **Query Complexity**: Some queries require multiple fact table joins
- **Data Latency**: Additional ETL steps may increase data latency

## Implementation Details

### Dimension Tables

#### Dim Country (SCD Type 2)
```sql
CREATE TABLE gold.dim_country (
    country_key INT IDENTITY(1,1) PRIMARY KEY,
    country_code STRING(3) NOT NULL,  -- ISO 3166-1 alpha-3
    country_name STRING(100) NOT NULL,
    who_region STRING(50),
    au_region STRING(50),  -- East, West, Central, Southern, North
    population BIGINT,
    is_current BOOLEAN DEFAULT TRUE,
    valid_from DATE DEFAULT CURRENT_DATE,
    valid_to DATE DEFAULT '9999-12-31'
);
```

#### Dim Date
```sql
CREATE TABLE gold.dim_date (
    date_key INT PRIMARY KEY,  -- YYYYMMDD format
    date DATE NOT NULL,
    epi_year INT NOT NULL,
    epi_week INT NOT NULL,
    calendar_year INT NOT NULL,
    calendar_quarter INT NOT NULL,
    calendar_month INT NOT NULL,
    day_of_week STRING(10),
    is_weekend BOOLEAN,
    month_name STRING(20),
    quarter_name STRING(10)
);
```

#### Dim Report
```sql
CREATE TABLE gold.dim_report (
    report_key INT IDENTITY(1,1) PRIMARY KEY,
    report_id STRING(50) NOT NULL UNIQUE,
    report_date DATE,
    report_type STRING(20) DEFAULT 'Weekly',
    data_source STRING(50) DEFAULT 'PDF',
    quality_score DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Fact Tables

#### Fact Cholera Cases
```sql
CREATE TABLE gold.fact_cholera_cases (
    case_key BIGINT IDENTITY(1,1) PRIMARY KEY,
    report_key INT NOT NULL,
    country_key INT NOT NULL,
    date_key INT NOT NULL,
    new_cases INT NOT NULL,
    cumulative_cases INT NOT NULL,
    confirmed_cases INT NOT NULL,
    suspected_cases INT NOT NULL,
    attack_rate DECIMAL(10,2),  -- Cases per 100,000 population
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_key) REFERENCES gold.dim_report(report_key),
    FOREIGN KEY (country_key) REFERENCES gold.dim_country(country_key),
    FOREIGN KEY (date_key) REFERENCES gold.dim_date(date_key)
);
```

#### Fact Cholera Deaths
```sql
CREATE TABLE gold.fact_cholera_deaths (
    death_key BIGINT IDENTITY(1,1) PRIMARY KEY,
    report_key INT NOT NULL,
    country_key INT NOT NULL,
    date_key INT NOT NULL,
    new_deaths INT NOT NULL,
    cumulative_deaths INT NOT NULL,
    cfr_percent DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_key) REFERENCES gold.dim_report(report_key),
    FOREIGN KEY (country_key) REFERENCES gold.dim_country(country_key),
    FOREIGN KEY (date_key) REFERENCES gold.dim_date(date_key)
);
```

### Bridge Tables

#### Bridge Quality Flags
```sql
CREATE TABLE gold.bridge_quality_flags (
    flag_key INT IDENTITY(1,1) PRIMARY KEY,
    report_key INT NOT NULL,
    flag_type STRING NOT NULL,
    severity STRING NOT NULL,
    flag_description STRING,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_key) REFERENCES gold.dim_report(report_key)
);
```

### Key Features

#### Conformed Dimensions
- **Country**: Standardized country codes and hierarchies
- **Date**: Both calendar and epidemiological time dimensions
- **Report**: Consistent reporting metadata across all facts

#### Slowly Changing Dimensions
- **Country**: Type 2 SCD to track population changes
- **Report**: Type 1 SCD for metadata updates

#### Degenerate Dimensions
- **Quality Flags**: Bridge table for quality metrics
- **Forecast Data**: Can be stored as degenerate dimensions

## ETL Process

### Silver to Gold Transformation
```python
# Pseudocode for ETL process
def transform_silver_to_gold():
    # Load Silver data
    silver_data = spark.read.format("delta").load("/lakehouse/silver")
    
    # Transform to dimensional model
    country_dim = create_country_dimension(silver_data)
    date_dim = create_date_dimension(silver_data)
    report_dim = create_report_dimension(silver_data)
    
    # Create fact tables
    cases_fact = create_cases_fact(silver_data, country_dim, date_dim, report_dim)
    deaths_fact = create_deaths_fact(silver_data, country_dim, date_dim, report_dim)
    
    # Save to Gold layer
    save_to_gold_layer(country_dim, date_dim, report_dim, cases_fact, deaths_fact)
```

### Data Quality Integration
- Quality scores stored in report dimension
- Quality flags linked via bridge table
- Data lineage tracked through report metadata

## Power BI Integration

### Semantic Model Structure
```
Power BI Semantic Model
├── Dim Country (One)
├── Dim Date (One)  
├── Dim Report (One)
├── Fact Cholera Cases (Many)
└── Fact Cholera Deaths (Many)
```

### Key Measures
```dax
// Case Fatality Rate
CFR % = DIVIDE([Fact Cholera Deaths][Sum new_deaths], 
               [Fact Cholera Cases][Sum confirmed_cases]) * 100

// Attack Rate
Attack Rate = DIVIDE([Fact Cholera Cases][Sum new_cases], 
                    [Dim Country][Population]) * 100000

// Weekly Growth
Weekly Growth = DIVIDE(
    [Current Week Cases] - [Previous Week Cases],
    [Previous Week Cases]
) * 100
```

## Future Considerations

### Schema Evolution
- **New Dimensions**: Add province/state level for subnational analysis
- **Additional Facts**: Add vaccination data, intervention metrics
- **Aggregated Facts**: Pre-computed aggregates for faster reporting

### Performance Optimization
- **Partitioning**: Partition fact tables by date for better performance
- **Indexing**: Optimize indexes for common query patterns
- **Materialized Views**: Create views for complex analytical queries

### Data Governance
- **Data Lineage**: Track data flow from source to analytical tables
- **Quality Metrics**: Monitor data quality in dimensional model
- **Access Control**: Implement row-level security for country data

## Related Decisions
- **ADR-001**: Microsoft Fabric Platform - Star schema implemented in Fabric Lakehouse
- **ADR-002**: Medallion Architecture - Gold layer contains dimensional model
- **ADR-005**: Quality Assurance Framework - Quality metrics integrated into dimensions

## References
- [Star Schema Design Best Practices](https://www.kimballgroup.com/data-warehouse-education/star-schema-design/)
- [Power BI Semantic Modeling](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-semantic-model)
- [Epidemiological Data Modeling](https://www.cdc.gov/epidemiology/manual/)

---

**Decision Date:** February 10, 2026  
**Review Date:** February 10, 2026  
**Next Review:** When new analytical requirements emerge or performance issues arise
