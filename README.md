# Central Data Repository (CDR) - Cholera Surveillance MVP

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🌍 Overview

Federated Central Data Repository for Africa CDC cholera surveillance. Automated weekly PDF ingestion, epidemiological analytics, ML forecasting, and Power BI dashboards. Built with Microsoft Fabric (OneLake, Lakehouse, Warehouse), Python, and CI/CD best practices.

**Current Status:** 🟢 Local setup complete | 🟡 Awaiting Microsoft Fabric deployment

## 🎯 Key Features

- ✅ Automated weekly PDF data extraction
- ✅ Bronze/Silver/Gold medallion architecture design
- ✅ Epidemiological analytics (incidence, CFR, trends)
- 🚧 ML forecasting (Prophet, 4-week ahead)
- 🚧 Power BI interactive dashboards
- ✅ Data quality validation framework
- 🚧 RBAC and audit logging

## 🏗️ Architecture

**Data Flow:** PDF Reports → Bronze (Raw) → Silver (Cleansed) → Gold (Analytics) → Power BI

**Tech Stack:**
- **Platform:** Microsoft Fabric (OneLake, Lakehouse, Warehouse)
- **Languages:** Python 3.11+, SQL, DAX
- **Libraries:** pandas, pdfplumber, Prophet, scikit-learn, pydantic
- **BI:** Power BI (Direct Lake mode)
- **DevOps:** Git, pytest, pre-commit hooks

## 🚀 Quick Start

### Prerequisites
- Windows 10/11 with PowerShell
- Python 3.11 or 3.12
- Visual Studio Code 1.85+
- Git 2.40+

### Local Setup
```powershell
# Clone repository
git clone https://github.com/africacdc/cholera-cdr-mvp.git
cd cholera-cdr-mvp

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Generate sample data
python scripts/utilities/generate_sample_data.py

# Run tests
pytest tests/ -v --cov=src
```

### Configuration

1. Copy `.env.example` to `.env`
2. Update Fabric workspace IDs (once available)
3. Configure Azure AD credentials

## 📊 Project Structure
```
cholera-cdr-mvp/
├── src/                       # Source code
│   ├── pdf_parser/            # PDF extraction logic
│   ├── epi_analytics/         # Epidemiological metrics
│   ├── data_models/           # Pydantic schemas & SQL DDL
│   └── config.py              # Configuration management
├── tests/                     # Test suite (pytest)
├── notebooks/                 # Jupyter/Fabric notebooks (future)
├── data/                      # Data storage
│   ├── sample/                # Sample cholera SitRep PDFs
│   └── reference/             # Reference data (country codes, regions)
├── docs/                      # Documentation
├── scripts/                   # Utility scripts
└── powerbi/                   # Power BI assets (future)
```

## 📖 Documentation

- **Setup Guide:** See Quick Start above
- **Data Dictionary:** `docs/data_dictionary.xlsx` (coming soon)
- **Architecture:** `docs/architecture/` (coming soon)

## 🧪 Testing
```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/test_pdf_extraction.py -v

# View coverage report
start htmlcov/index.html
```

## 📦 Core Modules

### PDF Parser
Extract structured data from cholera situation reports:
```python
from src.pdf_parser.extractor import extract_kpi_panel

kpi_data = extract_kpi_panel("data/sample/cholera_sitrep_2025_wk06.pdf")
# Returns: {'confirmed_cases': 1234, 'deaths': 45, 'cfr_percent': 3.65, ...}
```

### Epidemiological Analytics
Calculate key public health metrics:
```python
from src.epi_analytics.metrics import calculate_cfr, calculate_incidence_rate

cfr = calculate_cfr(deaths=45, confirmed_cases=1234)  # 3.65%
incidence = calculate_incidence_rate(cases=1234, population=5000000)  # 24.68 per 100k
```

### Data Models
Pydantic validation for data quality:
```python
from src.data_models.schemas import ReportSummary

report = ReportSummary(
    report_id="2025_wk06",
    confirmed_cases=1234,
    deaths=45,
    # ... validates schema and CFR consistency
)
```

## 🔄 Development Workflow

1. **Create feature branch:** `git checkout -b feature/your-feature`
2. **Make changes:** Edit code, add tests
3. **Run tests:** `pytest tests/ -v`
4. **Format code:** `black src/ tests/`
5. **Lint code:** `ruff check src/ tests/`
6. **Commit:** `git commit -m "feat: your feature"`
7. **Push:** `git push origin feature/your-feature`

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file

## 📧 Contact

**Africa CDC Data Team**  
Email: cdr-support@africacdc.org  
GitHub: @africacdc

## 🙏 Acknowledgments

Built in support of Africa CDC's mission to strengthen public health institutions across the African continent through data-driven decision-making.

---

**Protecting Today, Preparing for Tomorrow** 🌍🩺📊