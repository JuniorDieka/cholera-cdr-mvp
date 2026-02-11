-- ============================================
-- Silver Layer Tables - Cleansed Data
-- ============================================
-- File: 01_silver_tables.sql
-- Purpose: Create Silver layer Delta tables for cleansed cholera surveillance data
-- Author: Africa CDC Cholera CDR MVP
-- Date: 2026-02-11
-- ============================================

-- Drop existing tables (for re-deployment)
DROP TABLE IF EXISTS silver.report_summary;
DROP TABLE IF EXISTS silver.country_weekly;
DROP TABLE IF EXISTS silver.data_quality_checks;

-- ============================================
-- Silver: Report Summary
-- ============================================
-- Description: Cleansed weekly cholera situation reports
-- Grain: One row per report (weekly)
-- Source: Bronze layer report_summary

CREATE TABLE silver.report_summary (
    -- Primary Key
    report_id STRING NOT NULL COMMENT 'Unique report identifier (YYYY_wkWW)',
    
    -- Temporal Attributes
    epi_year INT COMMENT 'Epidemiological year',
    epi_week INT COMMENT 'Epidemiological week (1-53)',
    report_date DATE COMMENT 'Report end date (derived from epi week)',
    
    -- Case Metrics
    confirmed_cases INT COMMENT 'Total confirmed cholera cases',
    suspected_cases INT DEFAULT 0 COMMENT 'Total suspected cholera cases',
    deaths INT COMMENT 'Total deaths',
    cfr_percent DECIMAL(5,2) COMMENT 'Case Fatality Rate (%)',
    affected_countries INT COMMENT 'Number of affected countries',
    
    -- Calculated Metrics
    calculated_cfr DECIMAL(5,2) COMMENT 'Calculated CFR for validation',
    
    -- Data Quality Attributes
    data_completeness_pct DECIMAL(5,2) COMMENT 'Data completeness percentage (0-100)',
    data_quality_score DECIMAL(5,2) COMMENT 'Overall quality score (0-100)',
    
    -- Source Metadata
    source_file STRING COMMENT 'Source PDF filename',
    extraction_timestamp TIMESTAMP COMMENT 'When data was extracted',
    country_breakdown_count INT COMMENT 'Number of country records extracted',
    
    -- Audit Columns
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Record creation timestamp',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Record last update timestamp',
    
    -- Constraints
    PRIMARY KEY (report_id)
)
USING DELTA
PARTITIONED BY (epi_year, epi_week)
COMMENT 'Cleansed weekly cholera situation reports'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- ============================================
-- Silver: Country Weekly
-- ============================================
-- Description: Cleansed country-level weekly cholera data
-- Grain: One row per country per week
-- Source: Bronze layer country_weekly

CREATE TABLE silver.country_weekly (
    -- Composite Key
    report_id STRING NOT NULL COMMENT 'Report identifier',
    country_code STRING NOT NULL COMMENT 'ISO 3166-1 alpha-3 country code',
    
    -- Country Attributes
    country_name STRING COMMENT 'Country name (original from source)',
    
    -- Temporal Attributes
    epi_year INT COMMENT 'Epidemiological year',
    epi_week INT COMMENT 'Epidemiological week (1-53)',
    report_date DATE COMMENT 'Report end date',
    
    -- Case Metrics
    confirmed_cases INT DEFAULT 0 COMMENT 'Confirmed cases for this country',
    suspected_cases INT DEFAULT 0 COMMENT 'Suspected cases for this country',
    deaths INT DEFAULT 0 COMMENT 'Deaths for this country',
    cfr_percent DECIMAL(5,2) COMMENT 'Country-level CFR (%)',
    
    -- Source Metadata
    extraction_timestamp TIMESTAMP COMMENT 'When data was extracted',
    
    -- Audit Columns
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Record creation timestamp',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Record last update timestamp',
    
    -- Constraints
    PRIMARY KEY (report_id, country_code)
)
USING DELTA
PARTITIONED BY (epi_year, epi_week)
COMMENT 'Cleansed country-level weekly cholera data'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- ============================================
-- Silver: Data Quality Checks
-- ============================================
-- Description: Quality validation results for each report
-- Grain: One row per quality check per report
-- Source: QA Engine validation

CREATE TABLE silver.data_quality_checks (
    -- Primary Key
    check_id STRING COMMENT 'Unique check identifier',
    
    -- Check Attributes
    report_id STRING NOT NULL COMMENT 'Report being validated',
    check_type STRING NOT NULL COMMENT 'Type of quality check (CFR_CONSISTENCY, CASE_TOTAL, etc.)',
    severity STRING NOT NULL COMMENT 'Severity level (PASS, WARNING, ERROR)',
    
    -- Check Results
    expected_value STRING COMMENT 'Expected value',
    actual_value STRING COMMENT 'Actual value found',
    description STRING COMMENT 'Human-readable description of the issue',
    
    -- Temporal Attributes
    check_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'When check was performed',
    
    -- Resolution Tracking
    resolved BOOLEAN DEFAULT FALSE COMMENT 'Whether issue has been resolved',
    resolved_date DATE COMMENT 'Date issue was resolved',
    resolution_notes STRING COMMENT 'Notes on how issue was resolved',
    
    -- Constraints
    CHECK (severity IN ('PASS', 'WARNING', 'ERROR'))
)
USING DELTA
PARTITIONED BY (severity)
COMMENT 'Quality validation results for cholera reports'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- ============================================
-- Indexes for Query Optimization
-- ============================================

-- Note: Delta Lake automatically creates indexes on partition columns
-- Additional Z-ORDER optimization can be applied:

-- OPTIMIZE silver.report_summary ZORDER BY (report_date);
-- OPTIMIZE silver.country_weekly ZORDER BY (country_code, report_date);
-- OPTIMIZE silver.data_quality_checks ZORDER BY (report_id, check_type);

-- ============================================
-- Sample Queries for Validation
-- ============================================

-- Verify table creation
-- SELECT COUNT(*) as report_count FROM silver.report_summary;
-- SELECT COUNT(*) as country_count FROM silver.country_weekly;
-- SELECT COUNT(*) as check_count FROM silver.data_quality_checks;

-- Check data quality summary
-- SELECT severity, COUNT(*) as issue_count 
-- FROM silver.data_quality_checks 
-- GROUP BY severity;

-- Average quality score
-- SELECT AVG(data_quality_score) as avg_quality 
-- FROM silver.report_summary;
