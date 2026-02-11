-- ============================================
-- Gold Layer Dimensions - Star Schema
-- ============================================
-- File: 02_gold_dimensions.sql
-- Purpose: Create Gold layer dimension tables for Power BI analytics
-- Author: Africa CDC Cholera CDR MVP
-- Date: 2026-02-11
-- ============================================

-- Drop existing tables (for re-deployment)
DROP TABLE IF EXISTS gold.dim_country;
DROP TABLE IF EXISTS gold.dim_date;
DROP TABLE IF EXISTS gold.dim_report;

-- ============================================
-- Dimension: Country
-- ============================================
-- Description: Country master data with geographic and demographic attributes
-- Type: SCD Type 1 (overwrite on change)
-- Grain: One row per country

CREATE TABLE gold.dim_country (
    -- Surrogate Key
    country_key INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY COMMENT 'Surrogate key',
    
    -- Natural Key
    country_code STRING NOT NULL UNIQUE COMMENT 'ISO 3166-1 alpha-3 country code',
    
    -- Country Attributes
    country_name STRING NOT NULL COMMENT 'Official country name',
    who_region STRING COMMENT 'WHO region (AFRO, EMRO, etc.)',
    au_region STRING COMMENT 'African Union region',
    
    -- Demographic Attributes
    population BIGINT COMMENT 'Total population',
    
    -- SCD Type 1 Attributes
    is_current BOOLEAN DEFAULT TRUE COMMENT 'Is this the current record',
    valid_from DATE DEFAULT CURRENT_DATE COMMENT 'Valid from date',
    valid_to DATE DEFAULT '9999-12-31' COMMENT 'Valid to date',
    
    -- Audit Columns
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Record creation timestamp',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Record last update timestamp',
    
    -- Constraints
    CHECK (population >= 0)
)
USING DELTA
COMMENT 'Country dimension with geographic and demographic attributes'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- Create index on natural key
CREATE INDEX idx_country_code ON gold.dim_country (country_code);

-- ============================================
-- Dimension: Date
-- ============================================
-- Description: Date dimension with epidemiological week calendar
-- Type: Static dimension (pre-populated)
-- Grain: One row per date

CREATE TABLE gold.dim_date (
    -- Surrogate Key
    date_key INT PRIMARY KEY COMMENT 'Date key in YYYYMMDD format',
    
    -- Date Attributes
    date DATE NOT NULL UNIQUE COMMENT 'Actual date',
    
    -- Epidemiological Calendar
    epi_year INT NOT NULL COMMENT 'Epidemiological year',
    epi_week INT NOT NULL COMMENT 'Epidemiological week (1-53)',
    
    -- Gregorian Calendar
    calendar_year INT NOT NULL COMMENT 'Calendar year',
    calendar_quarter INT NOT NULL COMMENT 'Calendar quarter (1-4)',
    calendar_month INT NOT NULL COMMENT 'Calendar month (1-12)',
    calendar_month_name STRING COMMENT 'Month name (January, February, etc.)',
    
    -- Day Attributes
    day_of_week INT COMMENT 'Day of week (0=Monday, 6=Sunday)',
    day_of_week_name STRING COMMENT 'Day name (Monday, Tuesday, etc.)',
    is_weekend BOOLEAN COMMENT 'Is weekend (Saturday or Sunday)',
    
    -- Audit Columns
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Record creation timestamp',
    
    -- Constraints
    CHECK (epi_week BETWEEN 1 AND 53),
    CHECK (calendar_quarter BETWEEN 1 AND 4),
    CHECK (calendar_month BETWEEN 1 AND 12),
    CHECK (day_of_week BETWEEN 0 AND 6)
)
USING DELTA
PARTITIONED BY (calendar_year)
COMMENT 'Date dimension with epidemiological week calendar'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- Create index on epi week
CREATE INDEX idx_epi_week ON gold.dim_date (epi_year, epi_week);

-- ============================================
-- Dimension: Report
-- ============================================
-- Description: Report metadata with quality scores
-- Type: SCD Type 1 (overwrite on change)
-- Grain: One row per report

CREATE TABLE gold.dim_report (
    -- Surrogate Key
    report_key INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY COMMENT 'Surrogate key',
    
    -- Natural Key
    report_id STRING NOT NULL UNIQUE COMMENT 'Report identifier (YYYY_wkWW)',
    
    -- Temporal Attributes
    report_date DATE COMMENT 'Report end date',
    epi_year INT COMMENT 'Epidemiological year',
    epi_week INT COMMENT 'Epidemiological week',
    
    -- Report Attributes
    report_type STRING DEFAULT 'Weekly' COMMENT 'Report type (Weekly, Monthly, etc.)',
    data_source STRING DEFAULT 'PDF' COMMENT 'Data source (PDF, API, Manual, etc.)',
    
    -- Quality Attributes
    quality_score DECIMAL(5,2) COMMENT 'Overall quality score (0-100)',
    data_completeness_pct DECIMAL(5,2) COMMENT 'Data completeness percentage (0-100)',
    
    -- Source Metadata
    source_file STRING COMMENT 'Source file name',
    
    -- Audit Columns
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Record creation timestamp',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Record last update timestamp',
    
    -- Constraints
    CHECK (quality_score BETWEEN 0 AND 100),
    CHECK (data_completeness_pct BETWEEN 0 AND 100)
)
USING DELTA
COMMENT 'Report dimension with quality metadata'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- Create index on natural key
CREATE INDEX idx_report_id ON gold.dim_report (report_id);

-- ============================================
-- Sample Data Population (Optional)
-- ============================================

-- Populate dim_date with date range (2020-2030)
-- This would typically be done via a separate ETL process
-- INSERT INTO gold.dim_date (date_key, date, epi_year, epi_week, ...)
-- SELECT ... FROM epi_week_calendar;

-- ============================================
-- Sample Queries for Validation
-- ============================================

-- Verify dimension creation
-- SELECT COUNT(*) as country_count FROM gold.dim_country;
-- SELECT COUNT(*) as date_count FROM gold.dim_date;
-- SELECT COUNT(*) as report_count FROM gold.dim_report;

-- Check dimension integrity
-- SELECT country_code, COUNT(*) as dup_count 
-- FROM gold.dim_country 
-- GROUP BY country_code 
-- HAVING COUNT(*) > 1;

-- Date range coverage
-- SELECT MIN(date) as min_date, MAX(date) as max_date 
-- FROM gold.dim_date;
