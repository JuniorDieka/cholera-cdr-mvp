# Cholera CDR - Surveillance Data Pipeline

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Microsoft Fabric](https://img.shields.io/badge/Microsoft-Fabric-orange.svg)](https://www.microsoft.com/en-us/microsoft-fabric)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

Automated cholera surveillance pipeline for 53 African countries. Extracts data from weekly PDF reports, performs epidemiological analysis, detects hotspots, and generates 4-week forecasts using Microsoft Fabric and Python.

**Status:** ✅ Local MVP Complete | ⏳ Awaiting Fabric Capacity

---

## Key Features

- **Automated PDF Extraction** - Processes weekly situation reports
- **Medallion Architecture** - Bronze → Silver → Gold data layers
- **Epi Analytics** - Trends, anomaly detection, CFR calculations
- **ML Forecasting** - 4-week predictions with confidence intervals
- **Data Quality** - 6 automated validation rules
- **Platform Agnostic** - Works with Power BI or Apache Superset

---

## Quick Start

```powershell
# Clone and setup
git clone https://github.com/JuniorDieka/cholera-cdr-mvp.git
cd cholera-cdr-mvp
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Run notebooks in order
jupyter notebook notebooks/
# 01_pdf_extraction → 02_silver_transformation → 03_gold_dimensional_model
# → 04_epi_analytics → 05_ml_forecasting
```

---

## Architecture

```
Weekly PDF Reports
        ↓
┌──────────────────────────┐
│  BRONZE (Raw Ingestion)  │
│  ✓ PDF Parsing           │
└──────────────────────────┘
        ↓
┌──────────────────────────┐
│  SILVER (Cleansing)      │
│  ✓ Validation & QA       │
└──────────────────────────┘
        ↓
┌──────────────────────────┐
│  GOLD (Analytics)        │
│  ✓ Star Schema           │
│  ✓ ML Forecasting        │
└──────────────────────────┘
        ↓
   Power BI / Superset
```

**Tech Stack:** Python 3.12, pandas, Prophet, pdfplumber, Microsoft Fabric, Delta Lake

---

## Project Structure

```
cholera-cdr-mvp/
├── notebooks/          # 5 Jupyter notebooks (Bronze/Silver/Gold/Analytics/ML)
├── src/                # Python modules (PDF parser, epi analytics, data models)
├── data/
│   ├── sample/         # 3 synthetic test PDFs
│   └── reference/      # Country codes, AU regions, epi calendar
├── tests/              # pytest suite (86% coverage)
└── docs/               # Implementation guides
```

---

## Integration with Africa CDC Systems

### **Event Management System (EMS)**

This CDR complements Africa CDC's EMS (built on DHIS2), adding automated extraction, trend analysis, and ML forecasting to weekly cholera reports.

**Future:** Direct DHIS2 API integration will replace PDF extraction, leveraging existing member state infrastructure.

### **Apache Superset Alternative**

For organizations with limited BI budgets, CDR works with Apache Superset as an open-source alternative to Power BI.

**What CDR Adds:**
- Automated data pipeline (PDF → validated tables)
- Pre-calculated epi metrics (CFR, incidence, attack rates)
- Anomaly detection & ML forecasting
- Star schema dimensional model

---

## 🔒 Disclosure Control

**Important:** This repository contains **synthetic test data only**. No real patient data, PII, or sensitive epidemiological information is included.

**Public Repository Includes:**
- ✅ Source code and documentation
- ✅ 3 synthetic sample PDFs
- ✅ Reference data (country codes, regions)

**Excluded (Confidential):**
- 🔒 Real situation reports from Africa CDC
- 🔒 Actual case/death counts from member states
- 🔒 Production data and credentials

**Compliance:** Adheres to Africa CDC Data Sharing Policies, GDPR principles, and WHO surveillance guidelines.

---

## Deployment

**Local Development:** ✅ Complete (runs on Windows/Mac/Linux)

**Microsoft Fabric:**
1. Deploy notebooks to Fabric workspace
2. Connect to OneLake for data storage
3. Enable Power BI Direct Lake mode
4. Configure DHIS2 API integration (future)

**Security:** Azure AD auth, RBAC, row-level security, audit logging

---

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/name`)
3. Write tests (`pytest tests/ -v`)
4. Commit changes (`git commit -m 'feat: description'`)
5. Push and open Pull Request

**Security Issues:** Email jnrdieka@gmail.com (do not create public issues)

---

## Acknowledgments

Built based on experience with Africa CDC Event Management System and field visits to member states. Special thanks to:
- Africa CDC Epidemic Intelligence Unit
- Member states for collaboration and feedback
- Open-source community (pandas, Prophet, pdfplumber)

---

## License

MIT License - See [LICENSE](LICENSE)

---

**📈 Ready to Deploy | 🚀 Built for Scale | 🌍 Designed for Impact**

*Last Updated: June 11, 2026*
