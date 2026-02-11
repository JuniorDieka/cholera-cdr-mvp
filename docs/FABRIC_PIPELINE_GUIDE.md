# Microsoft Fabric Data Pipeline - Complete Implementation Guide

## 📋 **Overview**

This guide provides the complete implementation for the Cholera CDR MVP data pipeline, designed to run locally during development and deploy directly to Microsoft Fabric when capacity becomes available.

## 🏗️ **Pipeline Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                    BRONZE LAYER (Raw Data)                   │
│  Notebook 01: PDF Extraction                                 │
│  - Extract KPIs from PDFs                                    │
│  - Extract country breakdowns                                │
│  - Log extraction metadata                                   │
│  Output: bronze.report_summary, bronze.country_weekly        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   SILVER LAYER (Cleansed Data)               │
│  Notebook 02: Silver Transformation                          │
│  - Standardize country codes (ISO 3166)                      │
│  - Calculate/validate CFR                                    │
│  - Run comprehensive QA checks                               │
│  - Calculate quality scores                                  │
│  Output: silver.report_summary, silver.country_weekly,       │
│          silver.data_quality_checks                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  GOLD LAYER (Dimensional Model)              │
│  Notebook 03: Gold Dimensional Model                         │
│  - Create dimensions: dim_country, dim_date, dim_report      │
│  - Create facts: fact_cholera_cases, fact_cholera_deaths    │
│  - Generate surrogate keys                                   │
│  - Establish relationships                                   │
│  Output: Star schema for Power BI                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    ANALYTICS LAYER                           │
│  Notebook 04: Epidemiological Analytics                      │
│  - Calculate incidence rates                                 │
│  - Calculate moving averages (4-week)                        │
│  - Detect anomalies (Modified Z-Score)                       │
│  - Generate weekly summaries                                 │
│  Output: gold.epi_analytics_weekly                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    ML FORECASTING                            │
│  Notebook 05: ML Forecasting (Prophet)                       │
│  - Train Prophet models (4-week ahead)                       │
│  - Generate forecasts with uncertainty                       │
│  - Evaluate model performance                                │
│  - Extract explainability components                         │
│  Output: gold.forecast_cases_4wk, gold.model_performance     │
└─────────────────────────────────────────────────────────────┘
```

## ✅ **Completed Deliverables**

### Notebooks Created
- ✅ `notebooks/01_pdf_extraction.ipynb` - Bronze layer PDF extraction
- ✅ `notebooks/02_silver_transformation.ipynb` - Silver layer cleansing & QA
- ⏳ `notebooks/03_gold_dimensional_model.ipynb` - To be created
- ⏳ `notebooks/04_epi_analytics.ipynb` - To be created  
- ⏳ `notebooks/05_ml_forecasting.ipynb` - To be created

### Key Features Implemented
- **Environment Auto-Detection**: Automatically detects Fabric vs Local execution
- **Dual-Mode Paths**: Uses Fabric paths (`/lakehouse/default/`) or local paths
- **Comprehensive Logging**: Full error handling and progress tracking
- **Quality Validation**: Integrated QA engine with quality scoring
- **Data Lineage**: Tracks extraction timestamps and source files
- **Testing Framework**: Built-in validation checks in each notebook

## 🚀 **Quick Start - Local Testing**

### 1. Prerequisites
```bash
# Ensure you're in the project root
cd D:\Projects\cholera-cdr-mvp

# Activate virtual environment
venv\Scripts\activate

# Verify dependencies
pip list | findstr "pdfplumber pandas pydantic"
```

### 2. Run Notebook 01 (PDF Extraction)
```bash
# Open in Jupyter
jupyter notebook notebooks/01_pdf_extraction.ipynb

# Or run from command line
jupyter nbconvert --to notebook --execute notebooks/01_pdf_extraction.ipynb
```

**Expected Output:**
```
💻 Running locally
📄 Found 3 PDF files:
  - cholera_sitrep_2025_wk06.pdf
  - cholera_sitrep_2025_wk07.pdf
  - cholera_sitrep_2025_wk08.pdf

✅ 2025_wk06: 1,234 cases, 9 countries
✅ 2025_wk07: 1,456 cases, 9 countries
✅ 2025_wk08: 1,567 cases, 9 countries

✅ Extraction complete: 3 reports, 27 country records
✅ Parquet files saved to: data/bronze_tables
```

### 3. Run Notebook 02 (Silver Transformation)
```bash
jupyter notebook notebooks/02_silver_transformation.ipynb
```

**Expected Output:**
```
✅ Loaded 3 reports
✅ Loaded 27 country records
✅ Transformed 3 reports
   - Reports with dates: 3
   - Average completeness: 95.0%
✅ Transformed 27 country records
   - Unique countries: 9
✅ Ran 12 quality checks
Average quality score: 87.5
```

## 📊 **SQL DDL Scripts**

### Silver Layer Tables

```sql
-- File: src/data_models/sql_ddl/01_silver_tables.sql

-- Silver: Report Summary
CREATE TABLE silver.report_summary (
    report_id STRING NOT NULL,
    epi_year INT,
    epi_week INT,
    report_date DATE,
    confirmed_cases INT,
    suspected_cases INT,
    deaths INT,
    cfr_percent DECIMAL(5,2),
    affected_countries INT,
    source_file STRING,
    extraction_timestamp TIMESTAMP,
    country_breakdown_count INT,
    calculated_cfr DECIMAL(5,2),
    data_completeness_pct DECIMAL(5,2),
    data_quality_score DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (report_id)
)
USING DELTA
PARTITIONED BY (epi_year, epi_week);

-- Silver: Country Weekly
CREATE TABLE silver.country_weekly (
    report_id STRING NOT NULL,
    country_code STRING NOT NULL,
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
)
USING DELTA
PARTITIONED BY (epi_year, epi_week);

-- Silver: Data Quality Checks
CREATE TABLE silver.data_quality_checks (
    check_id STRING,
    report_id STRING NOT NULL,
    check_type STRING NOT NULL,
    severity STRING NOT NULL,
    expected_value STRING,
    actual_value STRING,
    description STRING,
    check_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_date DATE
)
USING DELTA
PARTITIONED BY (severity);
```

### Gold Layer Dimensions

```sql
-- File: src/data_models/sql_ddl/02_gold_dimensions.sql

-- Dimension: Country
CREATE TABLE gold.dim_country (
    country_key INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    country_code STRING NOT NULL UNIQUE,
    country_name STRING NOT NULL,
    who_region STRING,
    au_region STRING,
    population BIGINT,
    is_current BOOLEAN DEFAULT TRUE,
    valid_from DATE DEFAULT CURRENT_DATE,
    valid_to DATE DEFAULT '9999-12-31',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
USING DELTA;

-- Dimension: Date
CREATE TABLE gold.dim_date (
    date_key INT PRIMARY KEY,  -- YYYYMMDD format
    date DATE NOT NULL UNIQUE,
    epi_year INT NOT NULL,
    epi_week INT NOT NULL,
    calendar_year INT NOT NULL,
    calendar_quarter INT NOT NULL,
    calendar_month INT NOT NULL,
    calendar_month_name STRING,
    day_of_week INT,
    day_of_week_name STRING,
    is_weekend BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
USING DELTA
PARTITIONED BY (calendar_year);

-- Dimension: Report
CREATE TABLE gold.dim_report (
    report_key INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    report_id STRING NOT NULL UNIQUE,
    report_date DATE,
    epi_year INT,
    epi_week INT,
    report_type STRING DEFAULT 'Weekly',
    data_source STRING DEFAULT 'PDF',
    quality_score DECIMAL(5,2),
    data_completeness_pct DECIMAL(5,2),
    source_file STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
USING DELTA;
```

### Gold Layer Facts

```sql
-- File: src/data_models/sql_ddl/03_gold_facts.sql

-- Fact: Cholera Cases
CREATE TABLE gold.fact_cholera_cases (
    case_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    report_key INT NOT NULL,
    country_key INT NOT NULL,
    date_key INT NOT NULL,
    new_cases INT NOT NULL DEFAULT 0,
    cumulative_cases INT NOT NULL DEFAULT 0,
    confirmed_cases INT NOT NULL DEFAULT 0,
    suspected_cases INT NOT NULL DEFAULT 0,
    attack_rate DECIMAL(10,2),
    incidence_rate DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_key) REFERENCES gold.dim_report(report_key),
    FOREIGN KEY (country_key) REFERENCES gold.dim_country(country_key),
    FOREIGN KEY (date_key) REFERENCES gold.dim_date(date_key)
)
USING DELTA
PARTITIONED BY (date_key);

-- Fact: Cholera Deaths
CREATE TABLE gold.fact_cholera_deaths (
    death_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    report_key INT NOT NULL,
    country_key INT NOT NULL,
    date_key INT NOT NULL,
    new_deaths INT NOT NULL DEFAULT 0,
    cumulative_deaths INT NOT NULL DEFAULT 0,
    cfr_percent DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_key) REFERENCES gold.dim_report(report_key),
    FOREIGN KEY (country_key) REFERENCES gold.dim_country(country_key),
    FOREIGN KEY (date_key) REFERENCES gold.dim_date(date_key)
)
USING DELTA
PARTITIONED BY (date_key);
```

## 🔄 **Local Pipeline Execution**

### Option 1: Manual Execution
```bash
# Run notebooks in sequence
jupyter nbconvert --to notebook --execute notebooks/01_pdf_extraction.ipynb
jupyter nbconvert --to notebook --execute notebooks/02_silver_transformation.ipynb
# jupyter nbconvert --to notebook --execute notebooks/03_gold_dimensional_model.ipynb
# jupyter nbconvert --to notebook --execute notebooks/04_epi_analytics.ipynb
# jupyter nbconvert --to notebook --execute notebooks/05_ml_forecasting.ipynb
```

### Option 2: Python Orchestration Script
```python
# File: scripts/run_local_pipeline.py
import subprocess
import sys
from pathlib import Path
from datetime import datetime

notebooks = [
    "notebooks/01_pdf_extraction.ipynb",
    "notebooks/02_silver_transformation.ipynb",
    # Add remaining notebooks as they're created
]

def run_pipeline():
    print(f"\n🚀 Starting pipeline execution at {datetime.now()}\n")
    
    for notebook in notebooks:
        print(f"📓 Executing: {notebook}")
        
        result = subprocess.run([
            "jupyter", "nbconvert",
            "--to", "notebook",
            "--execute",
            notebook,
            "--output", notebook
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {notebook} completed successfully\n")
        else:
            print(f"❌ {notebook} failed:")
            print(result.stderr)
            sys.exit(1)
    
    print(f"\n✅ Pipeline completed at {datetime.now()}")

if __name__ == "__main__":
    run_pipeline()
```

## 📦 **Microsoft Fabric Deployment**

### Pre-Deployment Checklist

- [ ] Fabric workspace created (`cdr-cholera-dev`)
- [ ] Lakehouse created (`lakehouse_cholera_cdr`)
- [ ] Folder structure created (`bronze/pdfs/`, `reference/`)
- [ ] Sample PDFs uploaded to Bronze layer
- [ ] Reference data uploaded (country codes, epi calendar)
- [ ] Notebooks reviewed and tested locally

### Deployment Steps

1. **Upload Notebooks to Fabric**
   - Navigate to your Fabric workspace
   - Click `+ New` → `Import` → `Notebook`
   - Upload each notebook from `notebooks/` directory
   - Attach each notebook to `lakehouse_cholera_cdr`

2. **Create Warehouse (Optional)**
   - Click `+ New` → `Warehouse`
   - Name: `warehouse_cholera_cdr`
   - Run SQL DDL scripts to create schema

3. **Test Execution**
   - Run Notebook 01 in Fabric
   - Verify Bronze tables created
   - Run Notebook 02
   - Verify Silver tables created

4. **Create Data Pipeline**
   - Click `+ New` → `Data pipeline`
   - Add notebook activities in sequence
   - Configure schedule (weekly on Sundays)
   - Add email notifications

### Post-Deployment Validation

```sql
-- Check Bronze layer
SELECT COUNT(*) as report_count FROM bronze.report_summary;
SELECT COUNT(*) as country_count FROM bronze.country_weekly;

-- Check Silver layer
SELECT COUNT(*) as report_count FROM silver.report_summary;
SELECT AVG(data_quality_score) as avg_quality FROM silver.report_summary;

-- Check quality issues
SELECT severity, COUNT(*) as issue_count 
FROM silver.data_quality_checks 
GROUP BY severity;
```

## 🎯 **Next Development Steps**

### Immediate (This Week)
1. ✅ Complete Notebook 03 (Gold Dimensional Model)
2. ✅ Complete Notebook 04 (Epi Analytics)
3. ✅ Complete Notebook 05 (ML Forecasting)
4. ✅ Create Power BI mock data
5. ✅ Test complete pipeline locally

### Short-term (Next 2 Weeks)
1. Deploy to Fabric when capacity available
2. Create Power BI dashboard
3. Set up automated pipeline schedule
4. Configure monitoring and alerts

### Medium-term (Next Month)
1. Implement incremental loads (append mode)
2. Add more sophisticated ML models
3. Expand to additional data sources
4. Implement row-level security

## 📞 **Troubleshooting**

### Common Issues

**Issue: "Module not found" errors**
```bash
# Solution: Ensure src is in Python path
export PYTHONPATH="${PYTHONPATH}:D:/Projects/cholera-cdr-mvp/src"
# Or add to notebook:
import sys
sys.path.insert(0, 'D:/Projects/cholera-cdr-mvp/src')
```

**Issue: "No PDF files found"**
```bash
# Solution: Check paths
ls data/sample/*.pdf
# Ensure PDFs exist in correct location
```

**Issue: "QA engine not available"**
```bash
# Solution: Install dependencies
pip install pydantic
# Or use simplified validation (built into notebooks)
```

**Issue: Fabric notebook fails**
```
# Solution: Check Lakehouse attachment
# Verify paths use /lakehouse/default/ prefix
# Check Delta table permissions
```

## 📚 **Additional Resources**

- **Project Documentation**: `docs/developer_guides/README.md`
- **Architecture Decisions**: `docs/architecture/`
- **API Reference**: `docs/developer_guides/API_REFERENCE.md`
- **Testing Guide**: `docs/developer_guides/TESTING.md`
- **Deployment Guide**: `docs/developer_guides/DEPLOYMENT.md`

## ✅ **Success Criteria**

Your pipeline is ready when:

- ✅ All 5 notebooks execute locally without errors
- ✅ Bronze/Silver/Gold tables created successfully
- ✅ Data quality scores > 80% average
- ✅ No ERROR severity quality checks
- ✅ Forecasts generated with reasonable uncertainty
- ✅ Power BI can connect to Gold layer
- ✅ Documentation complete and accurate

---

**Last Updated**: February 11, 2026  
**Status**: Notebooks 01-02 Complete, 03-05 In Progress  
**Next Milestone**: Complete all notebooks and test end-to-end locally
