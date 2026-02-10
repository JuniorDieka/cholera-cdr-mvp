# Deployment Guide

## 🚀 Deployment Overview

This guide covers deployment strategies for the Cholera CDR MVP, from local development to Microsoft Fabric production.

## 📋 Deployment Environments

### 1. Local Development
- **Purpose:** Development and testing
- **Status:** ✅ Complete (86.1% test coverage)
- **Requirements:** Python 3.12+, local dependencies

### 2. Microsoft Fabric (Target)
- **Purpose:** Production deployment
- **Status:** 🔄 Pending (awaiting Fabric account)
- **Requirements:** Microsoft Fabric workspace, Lakehouse

### 3. CI/CD Pipeline
- **Purpose:** Automated testing and deployment
- **Status:** 📋 Planned
- **Requirements:** GitHub Actions, Azure DevOps

---

## 🏠 Local Development Deployment

### Prerequisites
```bash
# Verify Python version
python --version  # Should be 3.12+

# Clone repository
git clone <repository-url>
cd cholera-cdr-mvp

# Setup virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit configuration
# Set local paths, quality thresholds, etc.
```

### Verification
```bash
# Run tests (excluding Prophet Stan dependency)
python -m pytest tests/ -v --no-cov -k "not test_forecasting"

# Should show: 31 passed, 5 failed (Prophet issue)
```

### Local Services
```bash
# Test PDF extraction
python -c "from src.pdf_parser.extractor import extract_kpi_panel; print(extract_kpi_panel('data/sample/cholera_sitrep_2025_wk06.pdf'))"

# Test analytics
python -c "from src.epi_analytics.metrics import calculate_cfr; print(f'CFR: {calculate_cfr(25, 1000)}%')"

# Test QA engine
python -c "from src.epi_analytics.qa_engine import QualityEngine; engine = QualityEngine(); print('QA engine loaded')"
```

---

## ☁️ Microsoft Fabric Deployment

### Architecture Overview

```
Microsoft Fabric Workspace
├── Lakehouse (Bronze Layer)
│   ├── Raw PDFs
│   ├── Source Data
│   └── Reference Data
├── Lakehouse (Silver Layer)  
│   ├── Cleansed Tables
│   ├── Validated Data
│   └── Quality Metrics
├── Lakehouse (Gold Layer)
│   ├── Dimension Tables
│   ├── Fact Tables
│   └── Aggregates
├── Notebooks
│   ├── PDF Processing
│   ├── Data Transformation
│   └── ML Forecasting
└── Power BI
    ├── Dashboards
    ├── Reports
    └── Semantic Models
```

### Prerequisites

#### Microsoft Fabric Account
- **Fabric Capacity:** F64 or higher recommended
- **Workspace Permissions:** Admin or Contributor
- **Lakehouse Access:** Read/Write permissions

#### Required Services
- **Fabric Lakehouse** (Bronze, Silver, Gold)
- **Fabric Notebooks** (for Python scripts)
- **Power BI** (for dashboards)
- **Data Factory** (for pipelines)

### Deployment Steps

#### 1. Create Fabric Workspace
```bash
# In Fabric Portal:
# 1. Create new workspace
# 2. Set workspace permissions
# 3. Configure capacity settings
```

#### 2. Setup Lakehouses
```python
# Create three lakehouses:
# - cholera-bronze (raw data)
# - cholera-silver (cleansed data) 
# - cholera-gold (analytical data)

# Use Fabric UI or PowerShell:
# New > Lakehouse > Configure > Create
```

#### 3. Upload Reference Data
```python
# Upload reference files to Bronze layer:
# - country_codes_iso3166.csv
# - epi_week_calendar.csv
# - Sample PDFs for testing
```

#### 4. Convert Python Scripts to Notebooks

##### PDF Processing Notebook
```python
# notebooks/01_pdf_processing.ipynb

# Cell 1: Imports
from src.pdf_parser.extractor import extract_kpi_panel, extract_narrative
import pandas as pd

# Cell 2: Process PDFs
def process_pdf_batch(pdf_paths):
    results = []
    for pdf_path in pdf_paths:
        kpi = extract_kpi_panel(pdf_path)
        narrative = extract_narrative(pdf_path)
        results.append({**kpi, **narrative})
    return pd.DataFrame(results)

# Cell 3: Save to Bronze Lakehouse
df = process_pdf_batch(pdf_file_paths)
df.to_csv('/lakehouse/bronze/raw_reports.csv', index=False)
```

##### Data Transformation Notebook
```python
# notebooks/02_data_transformation.ipynb

# Cell 1: Load Bronze Data
import pandas as pd
bronze_df = spark.read.csv('/lakehouse/bronze/raw_reports.csv')

# Cell 2: Apply Quality Checks
from src.epi_analytics.qa_engine import QualityEngine
engine = QualityEngine()

# Cell 3: Transform to Silver
silver_df = transform_bronze_to_silver(bronze_df, engine)
silver_df.write.format('delta').save('/lakehouse/silver/cleansed_reports')
```

##### ML Forecasting Notebook
```python
# notebooks/03_ml_forecasting.ipynb

# Cell 1: Load Silver Data
silver_df = spark.read.format('delta').load('/lakehouse/silver/cleansed_reports')

# Cell 2: Prepare Data for Prophet
import pandas as pd
df = silver_df.toPandas()
df['ds'] = pd.to_datetime(df['report_date'])
df = df.rename(columns={'confirmed_cases': 'y'})

# Cell 3: Train Prophet Model
from src.epi_analytics.forecasting import train_prophet_model
model, forecast, metrics = train_prophet_model(df, forecast_weeks=4)

# Cell 4: Save Results
forecast.to_csv('/lakehouse/gold/forecasts.csv', index=False)
```

#### 5. Create Power BI Semantic Model
```python
# In Power BI:
# 1. Connect to Gold Lakehouse
# 2. Create semantic model
# 3. Define relationships
# 4. Create measures
# 5. Build dashboards
```

#### 6. Setup Data Pipelines
```python
# In Data Factory:
# 1. Create pipeline for PDF processing
# 2. Create pipeline for data transformation
# 3. Create pipeline for ML forecasting
# 4. Schedule weekly refresh
```

### Environment Variables for Fabric
```python
# In Fabric Notebook settings:
FABRIC_WORKSPACE_ID = "your-workspace-id"
FABRIC_LAKEHOUSE_BRONZE_ID = "bronze-lakehouse-id"
FABRIC_LAKEHOUSE_SILVER_ID = "silver-lakehouse-id"
FABRIC_LAKEHOUSE_GOLD_ID = "gold-lakehouse-id"

# Data paths
BRONZE_PATH = "/lakehouse/bronze"
SILVER_PATH = "/lakehouse/silver"
GOLD_PATH = "/lakehouse/gold"

# Quality thresholds
QUALITY_THRESHOLD_CFR = 0.5
QUALITY_THRESHOLD_CASES = 0.05
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/ci-cd.yml

name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: |
        python -m pytest tests/ -v --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  deploy-fabric:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to Fabric
      run: |
        # Use Fabric REST API or PowerShell
        # Deploy notebooks and pipelines
        echo "Deploying to Microsoft Fabric"
```

### Azure DevOps Pipeline

```yaml
# azure-pipelines.yml

trigger:
- main

pool:
  vmImage: 'ubuntu-latest'

steps:
- task: UsePythonVersion@0
  inputs:
    versionSpec: '3.12'

- script: |
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
  displayName: 'Install dependencies'

- script: |
    python -m pytest tests/ -v --cov=src
  displayName: 'Run tests'

- task: PublishTestResults@2
  condition: succeededOrFailed()

- task: PublishCodeCoverageResults@1
  inputs:
    codeCoverageTool: Cobertura
    summaryFileLocation: $(System.DefaultWorkingDirectory)/**/coverage.xml
```

---

## 📊 Monitoring and Logging

### Application Monitoring

#### Health Checks
```python
# notebooks/monitoring/health_checks.ipynb

def check_data_quality():
    """Check data quality metrics."""
    engine = QualityEngine()
    
    # Load latest data
    latest_data = get_latest_reports()
    
    # Run validation
    checks = engine.run_comprehensive_validation('health_check', latest_data)
    score = engine.get_quality_score(checks)
    
    return score, checks

def check_pipeline_status():
    """Check pipeline execution status."""
    # Monitor Data Factory pipelines
    # Check notebook execution
    # Verify data freshness
    pass
```

#### Logging Configuration
```python
import logging

# Configure logging for Fabric
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/lakehouse/logs/cholera_cdr.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### Performance Monitoring

#### Key Metrics
- **Data Processing Time:** PDF extraction and transformation
- **Model Training Time:** Prophet model training duration
- **Data Quality Score:** Overall data quality percentage
- **Pipeline Success Rate:** Percentage of successful pipeline runs

#### Alerting
```python
# Set up alerts in Fabric:
# 1. Data quality score < 80%
# 2. Pipeline failures
# 3. Data freshness > 7 days
# 4. Model performance degradation
```

---

## 🔒 Security and Governance

### Access Control

#### Fabric Workspace Permissions
```python
# Role-based access:
# - Admin: Full access
# - Contributor: Can edit notebooks and data
# - Viewer: Read-only access to dashboards
# - Data Engineer: Can run pipelines
```

#### Data Classification
```python
# Classify data sensitivity:
# - Public: Aggregated metrics
# - Internal: Country-level data
# - Confidential: Patient-level data (if applicable)
# - Restricted: Personally identifiable information
```

### Compliance

#### Data Protection
```python
# Implement data protection:
# - Anonymize personal data
# - Encrypt sensitive fields
# - Implement data retention policies
# - Audit data access
```

#### Regulatory Compliance
- **GDPR:** Data protection and privacy
- **HIPAA:** Healthcare data protection (if applicable)
- **Local Regulations:** Country-specific data laws

---

## 🚀 Production Deployment Checklist

### Pre-Deployment
- [ ] All tests passing (31/36)
- [ ] Code quality checks passing
- [ ] Documentation updated
- [ ] Security review completed
- [ ] Performance testing completed
- [ ] Backup strategy defined

### Deployment Steps
- [ ] Create Fabric workspace
- [ ] Setup lakehouses (Bronze, Silver, Gold)
- [ ] Upload reference data
- [ ] Deploy notebooks
- [ ] Create Power BI semantic model
- [ ] Build dashboards
- [ ] Setup data pipelines
- [ ] Configure monitoring
- [ ] Test end-to-end workflow

### Post-Deployment
- [ ] Monitor pipeline execution
- [ ] Verify data quality
- [ ] Check dashboard performance
- [ ] Validate user access
- [ ] Document deployment

---

## 🔄 Rollback Strategy

### Rollback Triggers
- Data quality score < 70%
- Pipeline failure rate > 20%
- Dashboard performance issues
- Security incidents

### Rollback Procedures
```python
# 1. Stop all pipelines
# 2. Restore previous data version
# 3. Revert notebook changes
# 4. Update Power BI model
# 5. Notify stakeholders
```

---

## 📞 Support and Maintenance

### Maintenance Tasks
- **Weekly:** Monitor data quality and pipeline performance
- **Monthly:** Review and update ML models
- **Quarterly:** Update reference data and documentation
- **Annually:** Security audit and compliance review

### Support Channels
- **Technical Issues:** Development team
- **Data Issues:** Data engineering team
- **User Issues:** Business analyst team
- **Security Issues:** Security team

### Documentation Updates
- Keep API reference current
- Update deployment guides
- Maintain troubleshooting guides
- Document known issues and solutions

---

## 🎯 Success Metrics

### Technical Metrics
- **Test Coverage:** > 85%
- **Pipeline Success Rate:** > 95%
- **Data Quality Score:** > 80%
- **System Uptime:** > 99%

### Business Metrics
- **Data Freshness:** < 7 days
- **Report Accuracy:** > 95%
- **User Satisfaction:** > 4.5/5
- **Processing Time:** < 4 hours

---

*This deployment guide covers the complete deployment process from local development to Microsoft Fabric production. For specific technical details, refer to the API reference and testing guides.*
