# Quick Start Guide

## 🚀 Get Running in 5 Minutes

### Prerequisites
- Python 3.12+
- Git

### Setup Commands
```bash
# 1. Clone and setup
git clone <repository-url>
cd cholera-cdr-mvp
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 3. Run tests
python -m pytest tests/ -v --no-cov -k "not test_forecasting"

# 4. Test PDF extraction
python -c "from src.pdf_parser.extractor import extract_kpi_panel; print(extract_kpi_panel('data/sample/cholera_sitrep_2025_wk06.pdf'))"

# 5. Test analytics
python -c "from src.epi_analytics.metrics import calculate_cfr; print(f'CFR: {calculate_cfr(25, 1000)}%')"
```

### Expected Results
- ✅ Tests should show: 31 passed, 5 failed (Prophet Stan issue)
- ✅ PDF extraction should return dictionary with case data
- ✅ Analytics should calculate: CFR: 2.5%

You're ready for development! 🎉
