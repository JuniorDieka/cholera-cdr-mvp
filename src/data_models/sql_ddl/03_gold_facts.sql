-- ============================================
-- Gold Layer Fact Tables - Star Schema
-- ============================================
-- File: 03_gold_facts.sql
-- Purpose: Create Gold layer fact tables for cholera case and death metrics
-- Author: Africa CDC Cholera CDR MVP
-- Date: 2026-02-11
-- ============================================

-- Drop existing tables (for re-deployment)
DROP TABLE IF EXISTS gold.fact_cholera_cases;
DROP TABLE IF EXISTS gold.fact_cholera_deaths;

-- ============================================
-- Fact: Cholera Cases
-- ============================================
-- Description: Fact table for case-related metrics
-- Grain: One row per country per week
-- Source: Silver layer country_weekly + dimensions

CREATE TABLE gold.fact_cholera_cases (
    -- Surrogate Key
    case_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY COMMENT 'Surrogate key',
    
    -- Foreign Keys (Dimension References)
    report_key INT NOT NULL COMMENT 'FK to dim_report',
    country_key INT NOT NULL COMMENT 'FK to dim_country',
    date_key INT NOT NULL COMMENT 'FK to dim_date',
    
    -- Case Metrics
    new_cases INT NOT NULL DEFAULT 0 COMMENT 'New cases reported this week',
    cumulative_cases INT NOT NULL DEFAULT 0 COMMENT 'Cumulative cases to date',
    confirmed_cases INT NOT NULL DEFAULT 0 COMMENT 'Confirmed cases',
    suspected_cases INT NOT NULL DEFAULT 0 COMMENT 'Suspected cases',
    
    -- Calculated Metrics
    attack_rate DECIMAL(10,2) COMMENT 'Cumulative cases per 100,000 population',
    incidence_rate DECIMAL(10,2) COMMENT 'New cases per 100,000 population',
    
    -- Audit Columns
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Record creation timestamp',
    
    -- Constraints
    CHECK (new_cases >= 0),
    CHECK (cumulative_cases >= 0),
    CHECK (confirmed_cases >= 0),
    CHECK (suspected_cases >= 0),
    
    -- Foreign Key Constraints
    FOREIGN KEY (report_key) REFERENCES gold.dim_report(report_key),
    FOREIGN KEY (country_key) REFERENCES gold.dim_country(country_key),
    FOREIGN KEY (date_key) REFERENCES gold.dim_date(date_key)
)
USING DELTA
PARTITIONED BY (date_key)
COMMENT 'Fact table for cholera case metrics'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- Create indexes for query optimization
CREATE INDEX idx_fact_cases_report ON gold.fact_cholera_cases (report_key);
CREATE INDEX idx_fact_cases_country ON gold.fact_cholera_cases (country_key);
CREATE INDEX idx_fact_cases_date ON gold.fact_cholera_cases (date_key);
CREATE INDEX idx_fact_cases_composite ON gold.fact_cholera_cases (country_key, date_key);

-- ============================================
-- Fact: Cholera Deaths
-- ============================================
-- Description: Fact table for death-related metrics
-- Grain: One row per country per week
-- Source: Silver layer country_weekly + dimensions

CREATE TABLE gold.fact_cholera_deaths (
    -- Surrogate Key
    death_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY COMMENT 'Surrogate key',
    
    -- Foreign Keys (Dimension References)
    report_key INT NOT NULL COMMENT 'FK to dim_report',
    country_key INT NOT NULL COMMENT 'FK to dim_country',
    date_key INT NOT NULL COMMENT 'FK to dim_date',
    
    -- Death Metrics
    new_deaths INT NOT NULL DEFAULT 0 COMMENT 'New deaths reported this week',
    cumulative_deaths INT NOT NULL DEFAULT 0 COMMENT 'Cumulative deaths to date',
    
    -- Calculated Metrics
    cfr_percent DECIMAL(5,2) COMMENT 'Case Fatality Rate (%)',
    
    -- Audit Columns
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Record creation timestamp',
    
    -- Constraints
    CHECK (new_deaths >= 0),
    CHECK (cumulative_deaths >= 0),
    CHECK (cfr_percent BETWEEN 0 AND 100),
    
    -- Foreign Key Constraints
    FOREIGN KEY (report_key) REFERENCES gold.dim_report(report_key),
    FOREIGN KEY (country_key) REFERENCES gold.dim_country(country_key),
    FOREIGN KEY (date_key) REFERENCES gold.dim_date(date_key)
)
USING DELTA
PARTITIONED BY (date_key)
COMMENT 'Fact table for cholera death metrics'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- Create indexes for query optimization
CREATE INDEX idx_fact_deaths_report ON gold.fact_cholera_deaths (report_key);
CREATE INDEX idx_fact_deaths_country ON gold.fact_cholera_deaths (country_key);
CREATE INDEX idx_fact_deaths_date ON gold.fact_cholera_deaths (date_key);
CREATE INDEX idx_fact_deaths_composite ON gold.fact_cholera_deaths (country_key, date_key);

-- ============================================
-- Z-ORDER Optimization (for Delta Lake)
-- ============================================
-- Run these periodically for better query performance

-- OPTIMIZE gold.fact_cholera_cases ZORDER BY (country_key, date_key);
-- OPTIMIZE gold.fact_cholera_deaths ZORDER BY (country_key, date_key);

-- ============================================
-- Sample Queries for Validation
-- ============================================

-- Verify fact table creation
-- SELECT COUNT(*) as case_count FROM gold.fact_cholera_cases;
-- SELECT COUNT(*) as death_count FROM gold.fact_cholera_deaths;

-- Check for orphaned foreign keys
-- SELECT COUNT(*) as orphaned_cases
-- FROM gold.fact_cholera_cases f
-- LEFT JOIN gold.dim_report r ON f.report_key = r.report_key
-- WHERE r.report_key IS NULL;

-- Verify metrics
-- SELECT 
--     SUM(new_cases) as total_cases,
--     SUM(new_deaths) as total_deaths,
--     ROUND(SUM(new_deaths) * 100.0 / NULLIF(SUM(new_cases), 0), 2) as overall_cfr
-- FROM gold.fact_cholera_cases c
-- JOIN gold.fact_cholera_deaths d 
--     ON c.report_key = d.report_key 
--     AND c.country_key = d.country_key 
--     AND c.date_key = d.date_key;
