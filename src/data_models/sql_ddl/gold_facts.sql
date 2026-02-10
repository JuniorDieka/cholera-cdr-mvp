-- Gold Layer Fact Tables - Cholera CDR MVP
-- Fact tables for analytical metrics

-- Fact: Cholera Cases
-- Stores case-related metrics at the most granular level
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
-- Stores death-related metrics at the most granular level
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

-- Create indexes for fact tables
CREATE INDEX IF NOT EXISTS idx_fact_cases_report ON gold.fact_cholera_cases(report_key);
CREATE INDEX IF NOT EXISTS idx_fact_cases_country ON gold.fact_cholera_cases(country_key);
CREATE INDEX IF NOT EXISTS idx_fact_cases_date ON gold.fact_cholera_cases(date_key);
CREATE INDEX IF NOT EXISTS idx_fact_cases_cases ON gold.fact_cholera_cases(new_cases);
CREATE INDEX IF NOT EXISTS idx_fact_deaths_report ON gold.fact_cholera_deaths(report_key);
CREATE INDEX IF NOT EXISTS idx_fact_deaths_country ON gold.fact_cholera_deaths(country_key);
CREATE INDEX IF NOT EXISTS idx_fact_deaths_date ON gold.fact_cholera_deaths(date_key);
CREATE INDEX IF NOT EXISTS idx_fact_deaths_deaths ON gold.fact_cholera_deaths(new_deaths);

-- Create partitioned views for better performance (optional for large datasets)
-- This would be implemented in a production environment
-- CREATE VIEW gold.vw_cases_by_country AS
-- SELECT 
--     c.country_name,
--     d.date,
--     f.new_cases,
--     f.cumulative_cases,
--     f.attack_rate
-- FROM gold.fact_cholera_cases f
-- JOIN gold.dim_country c ON f.country_key = c.country_key
-- JOIN gold.dim_date d ON f.date_key = d.date_key
-- WHERE c.is_current = TRUE;
