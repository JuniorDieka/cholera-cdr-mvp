-- Gold Layer Dimensional Model - Cholera CDR MVP
-- Star schema for epidemiological analytics

-- Dimension: Country (SCD Type 2)
-- Master reference for countries with SCD support
CREATE TABLE IF NOT EXISTS gold.dim_country (
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

-- Dimension: Date
-- Calendar and epidemiological date dimensions
CREATE TABLE IF NOT EXISTS gold.dim_date (
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

-- Dimension: Report
-- Master reference for all reports
CREATE TABLE IF NOT EXISTS gold.dim_report (
    report_key INT IDENTITY(1,1) PRIMARY KEY,
    report_id STRING(50) NOT NULL UNIQUE,
    report_date DATE,
    report_type STRING(20) DEFAULT 'Weekly',  -- 'Weekly', 'Outbreak', 'Ad-hoc'
    data_source STRING(50) DEFAULT 'PDF',
    quality_score DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bridge: Quality Flags
-- Connects reports to quality check results
CREATE TABLE IF NOT EXISTS gold.bridge_quality_flags (
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

-- Fact: Cholera Cases
-- Fact table for case-related metrics
CREATE TABLE IF NOT EXISTS gold.fact_cholera_cases (
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

-- Fact: Cholera Deaths
-- Fact table for death-related metrics
CREATE TABLE IF NOT EXISTS gold.fact_cholera_deaths (
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

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_dim_country_code ON gold.dim_country(country_code);
CREATE IF NOT EXISTS idx_dim_country_current ON gold.dim_country(is_current);
CREATE IF NOT EXISTS idx_dim_date_date ON gold.dim_date(date);
CREATE NOT EXISTS idx_dim_date_epi_year ON gold.dim_date(epi_year);
CREATE INDEX IF NOT EXISTS idx_dim_date_epi_week ON gold_dim_date(epi_year, epi_week);
CREATE INDEX IF NOT EXISTS idx_dim_report_id ON gold.dim_report(report_id);
CREATE INDEX IF NOT EXISTS idx_dim_report_date ON gold.dim_report(report_date);
CREATE INDEX IF NOT EXISTS idx_fact_cases_report ON gold.fact_cholera_cases(report_key);
CREATE INDEX IF NOT EXISTS idx_fact_cases_country ON gold.fact_cholera_cases(country_key);
CREATE INDEX IF NOT EXISTS idx_fact_cases_date ON gold.fact_cholera_cases(date_key);
CREATE INDEX IF NOT EXISTS idx_fact_deaths_report ON gold.fact_cholera_deaths(report_key);
CREATE INDEX IF NOT EXISTS idx_fact_deaths_country ON gold.fact_cholera_deaths(country_key);
CREATE IF NOT EXISTS idx_fact_deaths_date ON gold.fact_cholera_deaths(date_key);
CREATE INDEX IF NOT EXISTS idx_bridge_flags_report ON gold.bridge_quality_flags(report_key);
