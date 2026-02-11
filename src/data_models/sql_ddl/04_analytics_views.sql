-- ============================================
-- Gold Layer Analytics Views
-- ============================================
-- File: 04_analytics_views.sql
-- Purpose: Create analytical views for Power BI and reporting
-- Author: Africa CDC Cholera CDR MVP
-- Date: 2026-02-11
-- ============================================

-- Drop existing views (for re-deployment)
DROP VIEW IF EXISTS gold.vw_epi_weekly_summary;
DROP VIEW IF EXISTS gold.vw_country_trends;
DROP VIEW IF EXISTS gold.vw_hotspot_detection;
DROP VIEW IF EXISTS gold.vw_forecast_accuracy;

-- ============================================
-- View: Weekly Epidemiological Summary
-- ============================================
-- Description: Aggregated weekly metrics across all countries
-- Use Case: Executive dashboard, trend analysis

CREATE VIEW gold.vw_epi_weekly_summary AS
SELECT 
    -- Temporal Attributes
    d.date,
    d.epi_year,
    d.epi_week,
    d.calendar_year,
    d.calendar_month,
    d.calendar_month_name,
    
    -- Aggregated Metrics
    COUNT(DISTINCT fc.country_key) as affected_countries,
    SUM(fc.new_cases) as total_new_cases,
    SUM(fc.cumulative_cases) as total_cumulative_cases,
    SUM(fd.new_deaths) as total_new_deaths,
    SUM(fd.cumulative_deaths) as total_cumulative_deaths,
    
    -- Calculated Metrics
    ROUND(SUM(fd.new_deaths) * 100.0 / NULLIF(SUM(fc.new_cases), 0), 2) as weekly_cfr,
    ROUND(AVG(fc.incidence_rate), 2) as avg_incidence_rate,
    ROUND(AVG(fc.attack_rate), 2) as avg_attack_rate,
    
    -- Report Quality
    ROUND(AVG(r.quality_score), 1) as avg_quality_score,
    ROUND(AVG(r.data_completeness_pct), 1) as avg_completeness_pct
    
FROM gold.dim_date d
LEFT JOIN gold.fact_cholera_cases fc ON d.date_key = fc.date_key
LEFT JOIN gold.fact_cholera_deaths fd 
    ON fc.report_key = fd.report_key 
    AND fc.country_key = fd.country_key 
    AND fc.date_key = fd.date_key
LEFT JOIN gold.dim_report r ON fc.report_key = r.report_key

GROUP BY 
    d.date, d.epi_year, d.epi_week, 
    d.calendar_year, d.calendar_month, d.calendar_month_name

ORDER BY d.date DESC;

-- ============================================
-- View: Country Trends
-- ============================================
-- Description: Time series data by country for trend analysis
-- Use Case: Country-specific dashboards, comparative analysis

CREATE VIEW gold.vw_country_trends AS
SELECT 
    -- Country Attributes
    c.country_code,
    c.country_name,
    c.au_region,
    c.who_region,
    c.population,
    
    -- Temporal Attributes
    d.date,
    d.epi_year,
    d.epi_week,
    
    -- Case Metrics
    fc.new_cases,
    fc.cumulative_cases,
    fc.confirmed_cases,
    fc.suspected_cases,
    fc.incidence_rate,
    fc.attack_rate,
    
    -- Death Metrics
    fd.new_deaths,
    fd.cumulative_deaths,
    fd.cfr_percent,
    
    -- Calculated Trends (using window functions)
    LAG(fc.new_cases, 1) OVER (PARTITION BY c.country_code ORDER BY d.date) as prev_week_cases,
    
    ROUND(
        (fc.new_cases - LAG(fc.new_cases, 1) OVER (PARTITION BY c.country_code ORDER BY d.date)) * 100.0 / 
        NULLIF(LAG(fc.new_cases, 1) OVER (PARTITION BY c.country_code ORDER BY d.date), 0),
        2
    ) as week_over_week_growth_pct,
    
    ROUND(
        AVG(fc.new_cases) OVER (
            PARTITION BY c.country_code 
            ORDER BY d.date 
            ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
        ),
        2
    ) as cases_4wk_moving_avg,
    
    ROUND(
        AVG(fd.new_deaths) OVER (
            PARTITION BY c.country_code 
            ORDER BY d.date 
            ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
        ),
        2
    ) as deaths_4wk_moving_avg,
    
    -- Report Metadata
    r.report_id,
    r.quality_score

FROM gold.dim_country c
CROSS JOIN gold.dim_date d
LEFT JOIN gold.fact_cholera_cases fc 
    ON c.country_key = fc.country_key 
    AND d.date_key = fc.date_key
LEFT JOIN gold.fact_cholera_deaths fd 
    ON fc.report_key = fd.report_key 
    AND fc.country_key = fd.country_key 
    AND fc.date_key = fd.date_key
LEFT JOIN gold.dim_report r ON fc.report_key = r.report_key

WHERE c.is_current = TRUE

ORDER BY c.country_name, d.date DESC;

-- ============================================
-- View: Hotspot Detection
-- ============================================
-- Description: Countries with anomalous case increases
-- Use Case: Early warning system, outbreak detection

CREATE VIEW gold.vw_hotspot_detection AS
WITH country_stats AS (
    SELECT 
        country_key,
        MEDIAN(new_cases) as median_cases,
        MEDIAN(ABS(new_cases - MEDIAN(new_cases) OVER (PARTITION BY country_key))) as mad_cases
    FROM gold.fact_cholera_cases
    GROUP BY country_key
),
recent_data AS (
    SELECT 
        fc.country_key,
        c.country_code,
        c.country_name,
        c.au_region,
        d.date,
        d.epi_year,
        d.epi_week,
        fc.new_cases,
        fc.incidence_rate,
        cs.median_cases,
        cs.mad_cases,
        -- Modified Z-Score
        CASE 
            WHEN cs.mad_cases = 0 THEN 0
            ELSE ROUND(0.6745 * (fc.new_cases - cs.median_cases) / cs.mad_cases, 2)
        END as modified_z_score
    FROM gold.fact_cholera_cases fc
    JOIN gold.dim_country c ON fc.country_key = c.country_key
    JOIN gold.dim_date d ON fc.date_key = d.date_key
    JOIN country_stats cs ON fc.country_key = cs.country_key
    WHERE d.date >= CURRENT_DATE - INTERVAL '4 weeks'
)
SELECT 
    country_code,
    country_name,
    au_region,
    date,
    epi_year,
    epi_week,
    new_cases,
    incidence_rate,
    modified_z_score,
    CASE 
        WHEN ABS(modified_z_score) > 3.5 THEN 'CRITICAL'
        WHEN ABS(modified_z_score) > 2.5 THEN 'WARNING'
        ELSE 'NORMAL'
    END as anomaly_severity,
    CASE 
        WHEN modified_z_score > 0 THEN 'INCREASING'
        WHEN modified_z_score < 0 THEN 'DECREASING'
        ELSE 'STABLE'
    END as trend_direction
FROM recent_data
WHERE ABS(modified_z_score) > 2.5  -- Only show anomalies
ORDER BY ABS(modified_z_score) DESC, date DESC;

-- ============================================
-- View: Forecast Accuracy
-- ============================================
-- Description: Model performance metrics and forecast vs actual comparison
-- Use Case: Model monitoring, forecast evaluation

CREATE VIEW gold.vw_forecast_accuracy AS
SELECT 
    -- Forecast Metadata
    f.forecast_week_end_date,
    f.predicted_cases,
    f.predicted_cases_lower,
    f.predicted_cases_upper,
    f.confidence_level,
    f.model_type,
    f.forecast_date,
    
    -- Actual Data (when available)
    d.date as actual_date,
    SUM(fc.new_cases) as actual_cases,
    
    -- Accuracy Metrics
    CASE 
        WHEN SUM(fc.new_cases) IS NOT NULL THEN
            ABS(f.predicted_cases - SUM(fc.new_cases))
        ELSE NULL
    END as absolute_error,
    
    CASE 
        WHEN SUM(fc.new_cases) IS NOT NULL AND SUM(fc.new_cases) > 0 THEN
            ROUND(ABS(f.predicted_cases - SUM(fc.new_cases)) * 100.0 / SUM(fc.new_cases), 2)
        ELSE NULL
    END as percentage_error,
    
    CASE 
        WHEN SUM(fc.new_cases) IS NOT NULL THEN
            CASE 
                WHEN SUM(fc.new_cases) BETWEEN f.predicted_cases_lower AND f.predicted_cases_upper 
                THEN 'WITHIN_INTERVAL'
                ELSE 'OUTSIDE_INTERVAL'
            END
        ELSE 'PENDING'
    END as forecast_status,
    
    -- Model Performance
    mp.mae,
    mp.rmse,
    mp.mape

FROM gold.forecast_cases_4wk f
LEFT JOIN gold.dim_date d ON f.forecast_week_end_date = d.date
LEFT JOIN gold.fact_cholera_cases fc ON d.date_key = fc.date_key
LEFT JOIN gold.model_performance mp ON f.model_type = mp.model_type

GROUP BY 
    f.forecast_week_end_date, f.predicted_cases, f.predicted_cases_lower, 
    f.predicted_cases_upper, f.confidence_level, f.model_type, f.forecast_date,
    d.date, mp.mae, mp.rmse, mp.mape

ORDER BY f.forecast_week_end_date;

-- ============================================
-- Materialized Views (Optional for Performance)
-- ============================================
-- For large datasets, consider materializing frequently-used views

-- CREATE MATERIALIZED VIEW gold.mv_weekly_summary AS
-- SELECT * FROM gold.vw_epi_weekly_summary;

-- Refresh schedule (example):
-- REFRESH MATERIALIZED VIEW gold.mv_weekly_summary;

-- ============================================
-- Sample Queries for Validation
-- ============================================

-- Test weekly summary view
-- SELECT * FROM gold.vw_epi_weekly_summary ORDER BY date DESC LIMIT 10;

-- Test country trends view
-- SELECT * FROM gold.vw_country_trends 
-- WHERE country_code = 'ZWE' 
-- ORDER BY date DESC LIMIT 10;

-- Test hotspot detection
-- SELECT * FROM gold.vw_hotspot_detection;

-- Test forecast accuracy
-- SELECT * FROM gold.vw_forecast_accuracy 
-- WHERE forecast_status != 'PENDING';
