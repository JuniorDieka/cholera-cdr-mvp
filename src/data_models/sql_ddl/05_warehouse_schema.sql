-- ============================================
-- Warehouse Schema Master Deployment Script
-- ============================================
-- File: 05_warehouse_schema.sql
-- Purpose: Master script to deploy complete data warehouse schema
-- Author: Africa CDC Cholera CDR MVP
-- Date: 2026-02-11
-- ============================================
-- Execution Order: Run this script to create all tables in correct order
-- Dependencies: None (creates all objects)
-- ============================================

-- ============================================
-- STEP 1: Create Schemas/Databases
-- ============================================

CREATE SCHEMA IF NOT EXISTS bronze COMMENT 'Raw data from source systems';
CREATE SCHEMA IF NOT EXISTS silver COMMENT 'Cleansed and validated data';
CREATE SCHEMA IF NOT EXISTS gold COMMENT 'Business-ready dimensional model';

-- ============================================
-- STEP 2: Bronze Layer (Raw Data)
-- ============================================
-- Note: Bronze tables are typically created by ingestion process
-- Included here for completeness

CREATE TABLE IF NOT EXISTS bronze.report_summary (
    report_id STRING,
    epi_year INT,
    epi_week INT,
    confirmed_cases INT,
    suspected_cases INT,
    deaths INT,
    cfr_percent DECIMAL(5,2),
    affected_countries INT,
    source_file STRING,
    extraction_timestamp TIMESTAMP,
    country_breakdown_count INT
) USING DELTA
COMMENT 'Raw report summary data from PDF extraction';

CREATE TABLE IF NOT EXISTS bronze.country_weekly (
    report_id STRING,
    country_name STRING,
    epi_year INT,
    epi_week INT,
    confirmed_cases INT,
    suspected_cases INT,
    deaths INT,
    extraction_timestamp TIMESTAMP
) USING DELTA
COMMENT 'Raw country-level weekly data from PDF extraction';

CREATE TABLE IF NOT EXISTS bronze.extraction_metadata (
    report_id STRING,
    file_name STRING,
    file_size_bytes BIGINT,
    page_count INT,
    extraction_timestamp TIMESTAMP,
    kpi_extracted BOOLEAN,
    countries_extracted INT,
    status STRING,
    error_message STRING
) USING DELTA
COMMENT 'Metadata about PDF extraction process';

-- ============================================
-- STEP 3: Silver Layer (Cleansed Data)
-- ============================================

-- Silver: Report Summary
CREATE TABLE IF NOT EXISTS silver.report_summary (
    report_id STRING PRIMARY KEY,
    epi_year INT,
    epi_week INT,
    report_date DATE,
    confirmed_cases INT,
    suspected_cases INT DEFAULT 0,
    deaths INT,
    cfr_percent DECIMAL(5,2),
    affected_countries INT,
    calculated_cfr DECIMAL(5,2),
    data_completeness_pct DECIMAL(5,2),
    data_quality_score DECIMAL(5,2),
    source_file STRING,
    extraction_timestamp TIMESTAMP,
    country_breakdown_count INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) USING DELTA
PARTITIONED BY (epi_year, epi_week)
COMMENT 'Cleansed weekly cholera situation reports';

-- Silver: Country Weekly
CREATE TABLE IF NOT EXISTS silver.country_weekly (
    report_id STRING,
    country_code STRING,
    country_name STRING,
    epi_year INT,
    epi_week INT,
    report_date DATE,
    confirmed_cases INT DEFAULT 0,
    suspected_cases INT DEFAULT 0,
    deaths INT DEFAULT 0,
    cfr_percent DECIMAL(5,2),
    extraction_timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (report_id, country_code)
) USING DELTA
PARTITIONED BY (epi_year, epi_week)
COMMENT 'Cleansed country-level weekly cholera data';

-- Silver: Data Quality Checks
CREATE TABLE IF NOT EXISTS silver.data_quality_checks (
    check_id STRING,
    report_id STRING,
    check_type STRING,
    severity STRING,
    expected_value STRING,
    actual_value STRING,
    description STRING,
    check_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_date DATE,
    resolution_notes STRING,
    CHECK (severity IN ('PASS', 'WARNING', 'ERROR'))
) USING DELTA
PARTITIONED BY (severity)
COMMENT 'Quality validation results for cholera reports';

-- ============================================
-- STEP 4: Gold Layer - Dimensions
-- ============================================

-- Dimension: Country
CREATE TABLE IF NOT EXISTS gold.dim_country (
    country_key INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    country_code STRING UNIQUE,
    country_name STRING,
    who_region STRING,
    au_region STRING,
    population BIGINT,
    is_current BOOLEAN DEFAULT TRUE,
    valid_from DATE DEFAULT CURRENT_DATE,
    valid_to DATE DEFAULT '9999-12-31',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (population >= 0)
) USING DELTA
COMMENT 'Country dimension with geographic and demographic attributes';

-- Dimension: Date
CREATE TABLE IF NOT EXISTS gold.dim_date (
    date_key INT PRIMARY KEY,
    date DATE UNIQUE,
    epi_year INT,
    epi_week INT,
    calendar_year INT,
    calendar_quarter INT,
    calendar_month INT,
    calendar_month_name STRING,
    day_of_week INT,
    day_of_week_name STRING,
    is_weekend BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (epi_week BETWEEN 1 AND 53),
    CHECK (calendar_quarter BETWEEN 1 AND 4),
    CHECK (calendar_month BETWEEN 1 AND 12),
    CHECK (day_of_week BETWEEN 0 AND 6)
) USING DELTA
PARTITIONED BY (calendar_year)
COMMENT 'Date dimension with epidemiological week calendar';

-- Dimension: Report
CREATE TABLE IF NOT EXISTS gold.dim_report (
    report_key INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    report_id STRING UNIQUE,
    report_date DATE,
    epi_year INT,
    epi_week INT,
    report_type STRING DEFAULT 'Weekly',
    data_source STRING DEFAULT 'PDF',
    quality_score DECIMAL(5,2),
    data_completeness_pct DECIMAL(5,2),
    source_file STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (quality_score BETWEEN 0 AND 100),
    CHECK (data_completeness_pct BETWEEN 0 AND 100)
) USING DELTA
COMMENT 'Report dimension with quality metadata';

-- ============================================
-- STEP 5: Gold Layer - Facts
-- ============================================

-- Fact: Cholera Cases
CREATE TABLE IF NOT EXISTS gold.fact_cholera_cases (
    case_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    report_key INT,
    country_key INT,
    date_key INT,
    new_cases INT DEFAULT 0,
    cumulative_cases INT DEFAULT 0,
    confirmed_cases INT DEFAULT 0,
    suspected_cases INT DEFAULT 0,
    attack_rate DECIMAL(10,2),
    incidence_rate DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (new_cases >= 0),
    CHECK (cumulative_cases >= 0),
    FOREIGN KEY (report_key) REFERENCES gold.dim_report(report_key),
    FOREIGN KEY (country_key) REFERENCES gold.dim_country(country_key),
    FOREIGN KEY (date_key) REFERENCES gold.dim_date(date_key)
) USING DELTA
PARTITIONED BY (date_key)
COMMENT 'Fact table for cholera case metrics';

-- Fact: Cholera Deaths
CREATE TABLE IF NOT EXISTS gold.fact_cholera_deaths (
    death_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    report_key INT,
    country_key INT,
    date_key INT,
    new_deaths INT DEFAULT 0,
    cumulative_deaths INT DEFAULT 0,
    cfr_percent DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (new_deaths >= 0),
    CHECK (cumulative_deaths >= 0),
    CHECK (cfr_percent BETWEEN 0 AND 100),
    FOREIGN KEY (report_key) REFERENCES gold.dim_report(report_key),
    FOREIGN KEY (country_key) REFERENCES gold.dim_country(country_key),
    FOREIGN KEY (date_key) REFERENCES gold.dim_date(date_key)
) USING DELTA
PARTITIONED BY (date_key)
COMMENT 'Fact table for cholera death metrics';

-- ============================================
-- STEP 6: Gold Layer - Analytics Tables
-- ============================================

-- Analytics: Weekly Summary
CREATE TABLE IF NOT EXISTS gold.epi_analytics_weekly (
    epi_year INT,
    epi_week INT,
    date DATE,
    new_cases INT,
    new_deaths INT,
    confirmed_cases INT,
    suspected_cases INT,
    affected_countries INT,
    weekly_cfr DECIMAL(5,2),
    cases_prev_week INT,
    weekly_change_pct DECIMAL(5,2),
    cumulative_cases INT,
    cumulative_deaths INT,
    anomaly_count INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) USING DELTA
COMMENT 'Weekly epidemiological summary with trends';

-- Analytics: Country Trends
CREATE TABLE IF NOT EXISTS gold.epi_country_trends (
    country_key INT,
    country_code STRING,
    country_name STRING,
    au_region STRING,
    date DATE,
    epi_year INT,
    epi_week INT,
    new_cases INT,
    new_deaths INT,
    cumulative_cases_country INT,
    cumulative_deaths_country INT,
    cases_4wk_ma DECIMAL(10,2),
    deaths_4wk_ma DECIMAL(10,2),
    growth_rate_pct DECIMAL(5,2),
    incidence_rate DECIMAL(10,2),
    attack_rate_cumulative DECIMAL(10,2),
    cfr_percent DECIMAL(5,2),
    trend_direction STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) USING DELTA
COMMENT 'Country-level time series with moving averages';

-- Analytics: Hotspot Detection
CREATE TABLE IF NOT EXISTS gold.epi_hotspot_detection (
    country_key INT,
    country_code STRING,
    country_name STRING,
    au_region STRING,
    date DATE,
    epi_year INT,
    epi_week INT,
    new_cases INT,
    cases_4wk_ma DECIMAL(10,2),
    cases_modified_z DECIMAL(5,2),
    anomaly_severity STRING,
    incidence_rate DECIMAL(10,2),
    detection_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) USING DELTA
COMMENT 'Anomaly detection results for outbreak alerts';

-- ============================================
-- STEP 7: Gold Layer - ML Forecasting
-- ============================================

-- Forecast: 4-Week Cases
CREATE TABLE IF NOT EXISTS gold.forecast_cases_4wk (
    forecast_week_end_date DATE,
    predicted_cases INT,
    predicted_cases_lower INT,
    predicted_cases_upper INT,
    confidence_level INT,
    forecast_date DATE,
    forecast_horizon_weeks INT,
    model_type STRING,
    model_version STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) USING DELTA
COMMENT '4-week ahead case forecasts with uncertainty intervals';

-- Model Performance
CREATE TABLE IF NOT EXISTS gold.model_performance (
    model_id STRING PRIMARY KEY,
    model_type STRING,
    model_version STRING,
    training_date DATE,
    training_records INT,
    forecast_horizon_weeks INT,
    mae DECIMAL(10,2),
    rmse DECIMAL(10,2),
    mape DECIMAL(5,2),
    seasonality_mode STRING,
    interval_width DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) USING DELTA
COMMENT 'ML model performance metrics and metadata';

-- ============================================
-- STEP 8: Create Indexes
-- ============================================

-- Silver Layer Indexes
CREATE INDEX IF NOT EXISTS idx_silver_report_date ON silver.report_summary(report_date);
CREATE INDEX IF NOT EXISTS idx_silver_country_code ON silver.country_weekly(country_code);

-- Gold Dimension Indexes
CREATE INDEX IF NOT EXISTS idx_dim_country_code ON gold.dim_country(country_code);
CREATE INDEX IF NOT EXISTS idx_dim_date_epi_week ON gold.dim_date(epi_year, epi_week);
CREATE INDEX IF NOT EXISTS idx_dim_report_id ON gold.dim_report(report_id);

-- Gold Fact Indexes
CREATE INDEX IF NOT EXISTS idx_fact_cases_report ON gold.fact_cholera_cases(report_key);
CREATE INDEX IF NOT EXISTS idx_fact_cases_country ON gold.fact_cholera_cases(country_key);
CREATE INDEX IF NOT EXISTS idx_fact_cases_date ON gold.fact_cholera_cases(date_key);
CREATE INDEX IF NOT EXISTS idx_fact_deaths_report ON gold.fact_cholera_deaths(report_key);
CREATE INDEX IF NOT EXISTS idx_fact_deaths_country ON gold.fact_cholera_deaths(country_key);
CREATE INDEX IF NOT EXISTS idx_fact_deaths_date ON gold.fact_cholera_deaths(date_key);

-- ============================================
-- STEP 9: Optimization (Optional)
-- ============================================

-- Run these after initial data load for better performance
-- OPTIMIZE silver.report_summary ZORDER BY (report_date);
-- OPTIMIZE silver.country_weekly ZORDER BY (country_code, report_date);
-- OPTIMIZE gold.fact_cholera_cases ZORDER BY (country_key, date_key);
-- OPTIMIZE gold.fact_cholera_deaths ZORDER BY (country_key, date_key);

-- ============================================
-- STEP 10: Validation Queries
-- ============================================

-- Verify all tables created
-- SELECT 'bronze.report_summary' as table_name, COUNT(*) as row_count FROM bronze.report_summary
-- UNION ALL
-- SELECT 'silver.report_summary', COUNT(*) FROM silver.report_summary
-- UNION ALL
-- SELECT 'gold.dim_country', COUNT(*) FROM gold.dim_country
-- UNION ALL
-- SELECT 'gold.dim_date', COUNT(*) FROM gold.dim_date
-- UNION ALL
-- SELECT 'gold.dim_report', COUNT(*) FROM gold.dim_report
-- UNION ALL
-- SELECT 'gold.fact_cholera_cases', COUNT(*) FROM gold.fact_cholera_cases
-- UNION ALL
-- SELECT 'gold.fact_cholera_deaths', COUNT(*) FROM gold.fact_cholera_deaths;

-- ============================================
-- Deployment Complete
-- ============================================
-- All tables, indexes, and constraints created successfully
-- Next Steps:
-- 1. Run data ingestion pipeline (Notebooks 01-05)
-- 2. Populate reference dimensions (dim_country, dim_date)
-- 3. Verify data quality
-- 4. Connect Power BI to Gold layer
-- ============================================
