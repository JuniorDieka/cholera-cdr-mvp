-- Silver Layer Tables - Cholera CDR MVP
-- These tables store cleansed and conformed data from PDF extraction

-- Report Summary Table
-- One row per weekly cholera situation report
CREATE TABLE IF NOT EXISTS silver.report_summary (
    report_id STRING PRIMARY KEY,
    report_date DATE NOT NULL,
    epi_year INT NOT NULL,
    epi_week INT NOT NULL,
    confirmed_cases INT NOT NULL,
    suspected_cases INT NOT NULL,
    deaths INT NOT NULL,
    cfr_percent DECIMAL(5,2),
    affected_countries INT NOT NULL,
    first_reported_date DATE,
    risk_assessment STRING,
    data_source STRING DEFAULT 'PDF',
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    quality_flag STRING DEFAULT 'PASS'  -- 'PASS', 'WARNING', 'FAIL'
);

-- Country Weekly Table
-- Granular country-level data per epi-week
CREATE TABLE IF NOT EXISTS silver.country_weekly (
    country_weekly_id STRING PRIMARY KEY,
    report_id STRING NOT NULL,
    country_name STRING NOT NULL,
    epi_year INT NOT NULL,
    epi_week INT NOT NULL,
    new_cases INT NOT NULL,
    cumulative_cases INT NOT NULL,
    new_deaths INT NOT NULL,
    cumulative_deaths INT NOT NULL,
    cfr_percent DECIMAL(5,2),
    provinces_affected INT,
    data_source STRING DEFAULT 'PDF',
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES silver.report_summary(report_id)
);

-- Narrative Extracts Table
-- Free-text narratives with entity recognition
CREATE TABLE IF NOT EXISTS silver.narrative_extracts (
    narrative_id STRING PRIMARY KEY,
    report_id STRING NOT NULL,
    narrative_type STRING NOT NULL,  -- 'update_to_event', 'epi_week_summary', 'country_detail'
    narrative_text TEXT,
    extracted_entities JSON,  -- Countries, numbers, dates
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES silver.report_summary(report_id)
);

-- Data Quality Checks Table
-- Validation flags and mismatch detection
CREATE TABLE IF NOT EXISTS silver.data_quality_checks (
    check_id STRING PRIMARY KEY,
    report_id STRING NOT NULL,
    check_type STRING NOT NULL,  -- 'CFR_MISMATCH', 'CASE_SUM_MISMATCH', 'MISSING_COUNTRY'
    severity STRING NOT NULL,      -- 'ERROR', 'WARNING', 'INFO'
    expected_value STRING,
    actual_value STRING,
    check_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES silver.report_summary(report_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_report_summary_date ON silver.report_summary(report_date);
CREATE INDEX IF NOT EXISTS idx_report_summary_epi_week ON silver.report_summary(epi_year, epi_week);
CREATE INDEX IF NOT EXISTS idx_country_weekly_country ON silver.country_weekly(country_name);
CREATE INDEX IF NOT EXISTS idx_country_weekly_date ON silver.country_weekly(epi_year, epi_week);
CREATE INDEX IF NOT EXISTS idx_quality_checks_report ON silver.data_quality_checks(report_id);
CREATE INDEX IF NOT EXISTS idx_quality_checks_severity ON silver.data_quality_checks(severity);
CREATE INDEX IF NOT EXISTS idx_narratives_report ON silver.narrative_extracts(report_id);
CREATE INDEX IF NOT EXISTS idx_narratives_type ON silver.narrative_extracts(narrative_type);
