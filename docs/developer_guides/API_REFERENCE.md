# API Reference

## 📚 Core Modules

### PDF Parser (`src.pdf_parser.extractor`)

#### `extract_kpi_panel(pdf_path: str) -> Dict[str, Any]`
Extract KPI data from cholera situation reports.

**Parameters:**
- `pdf_path`: Path to PDF file

**Returns:** Dictionary with extracted metrics
```python
{
    'confirmed_cases': int,
    'suspected_cases': int,
    'deaths': int,
    'cfr_percent': float,
    'affected_countries': int
}
```

**Example:**
```python
from src.pdf_parser.extractor import extract_kpi_panel
kpi = extract_kpi_panel('data/sample/cholera_sitrep_2025_wk06.pdf')
print(f"Cases: {kpi.get('confirmed_cases', 0)}")
```

#### `extract_narrative(pdf_path: str) -> Dict[str, str]`
Extract narrative sections from PDF.

**Returns:** Dictionary with narrative texts
```python
{
    'update_to_event': str,
    'epi_week_summary': str
}
```

---

### Epidemiological Analytics (`src.epi_analytics.metrics`)

#### `calculate_incidence_rate(cases: int, population: int, multiplier: int = 100000) -> float`
Calculate incidence rate per population.

**Parameters:**
- `cases`: Number of cases
- `population`: Population size  
- `multiplier`: Rate multiplier (default: 100,000)

**Returns:** Incidence rate per multiplier population

**Example:**
```python
from src.epi_analytics.metrics import calculate_incidence_rate
rate = calculate_incidence_rate(cases=1000, population=5000000)
print(f"Incidence rate: {rate:.2f} per 100,000")
```

#### `calculate_cfr(deaths: int, confirmed_cases: int) -> float`
Calculate Case Fatality Rate as percentage.

**Returns:** CFR as percentage

**Example:**
```python
from src.epi_analytics.metrics import calculate_cfr
cfr = calculate_cfr(deaths=25, confirmed_cases=1000)
print(f"CFR: {cfr:.2f}%")
```

#### `moving_average(series: pd.Series, window: int = 4) -> pd.Series`
Calculate rolling average for smoothing trends.

#### `growth_rate(current: int, previous: int) -> float`
Calculate week-over-week growth rate percentage.

#### `detect_anomalies(series: pd.Series, threshold: float = 2.5) -> pd.Series`
Flag outliers using modified z-score.

---

### Quality Assurance Engine (`src.epi_analytics.qa_engine`)

#### `QualityEngine`
Main class for data quality validation.

**Initialization:**
```python
from src.epi_analytics.qa_engine import QualityEngine
engine = QualityEngine(tolerance_cfr=0.5, tolerance_cases=0.05)
```

**Methods:**

##### `validate_cfr_consistency(report_id, confirmed_cases, deaths, reported_cfr=None)`
Validate CFR consistency between calculated and reported values.

**Returns:** List of `QualityCheck` objects

##### `validate_case_totals(report_id, confirmed_cases, suspected_cases, country_breakdown=None)`
Validate case totals against country breakdowns.

##### `validate_epidemiological_week(report_id, report_date, epi_year, epi_week)`
Validate epidemiological week consistency.

##### `validate_data_completeness(report_id, data_dict)`
Validate required and important fields are present.

##### `validate_value_ranges(report_id, data_dict)`
Validate values are within reasonable ranges.

##### `run_comprehensive_validation(report_id, data_dict, country_breakdown=None)`
Run all validation types.

##### `get_quality_score(checks) -> float`
Calculate overall quality score (0-100).

**Example:**
```python
from src.epi_analytics.qa_engine import QualityEngine
from datetime import datetime

engine = QualityEngine()
data = {
    'confirmed_cases': 1000,
    'deaths': 25,
    'cfr_percent': 2.5,
    'report_date': datetime(2025, 2, 8),
    'epi_year': 2025,
    'epi_week': 6
}

checks = engine.run_comprehensive_validation('test_report', data)
score = engine.get_quality_score(checks)
print(f"Quality Score: {score:.1f}")
```

---

### Forecasting (`src.epi_analytics.forecasting`)

#### `train_prophet_model(df, forecast_weeks=4)`
Train Prophet model for case forecasting.

**Parameters:**
- `df`: DataFrame with 'ds' (date) and 'y' (cases) columns
- `forecast_weeks`: Number of weeks to predict

**Returns:** Tuple of (model, forecast_df, metrics_dict)

**Note:** Requires Stan backend - use mock for testing.

#### `explain_forecast(model, forecast) -> Dict[str, Any]`
Generate explainability outputs for Prophet forecast.

#### `evaluate_model_performance(actual, predicted) -> Dict[str, float]`
Evaluate model performance with multiple metrics.

#### `forecast_summary(forecast) -> pd.DataFrame`
Create summary of forecast results.

---

### Mock Prophet (`src.epi_analytics.mock_prophet`)

#### `mock_train_prophet_model(df, forecast_weeks=4)`
Mock Prophet model training for testing without Stan dependency.

**Use for testing when Stan backend is not available.**

---

## 📊 Data Models (`src.data_models.schemas`)

### Pydantic Models

#### `ReportSummary`
Schema for report summary validation.

#### `CountryWeekly`  
Schema for country weekly data validation.

#### `QualityCheck`
Schema for quality check results.

**Example:**
```python
from src.data_models.schemas import ReportSummary
from datetime import datetime

report = ReportSummary(
    report_id="2025_wk06",
    report_date=datetime(2025, 2, 8),
    confirmed_cases=1000,
    deaths=25,
    cfr_percent=2.5
)
```

---

## 🔧 Configuration (`src.config`)

### Environment Variables
Key configuration options:

```python
from src.config import get_config

config = get_config()
print(f"Data path: {config.data_path}")
print(f"Quality thresholds: {config.quality_thresholds}")
```

---

## 🧪 Testing Utilities

### Fixtures (`tests/conftest`)

#### `sample_pdf_path`
Path to sample PDF for testing.

#### `sample_kpi_data`
Sample KPI data dictionary.

#### `expected_report_schema`
Expected schema for report summary.

---

## 📋 Error Handling

### Common Exceptions

#### `ValueError`
- Invalid input parameters
- Division by zero in calculations

#### `FileNotFoundError`
- PDF file not found
- Missing data files

#### `ValidationError`
- Pydantic validation failures
- Data quality check failures

### Error Handling Patterns

```python
try:
    result = extract_kpi_panel(pdf_path)
except FileNotFoundError:
    print(f"PDF not found: {pdf_path}")
except Exception as e:
    print(f"Extraction error: {e}")
```

---

## 🔍 Performance Considerations

### Memory Usage
- Process large PDFs in chunks
- Clear intermediate data structures

### Processing Speed
- Use vectorized operations with pandas/numpy
- Cache frequently accessed data

### Scalability
- Designed for batch processing
- Compatible with cloud deployment

---

## 📚 Type Hints

All functions use Python type hints for better IDE support and error prevention:

```python
def calculate_incidence_rate(
    cases: int, 
    population: int, 
    multiplier: int = 100000
) -> float:
    """Calculate incidence rate per population."""
    pass
```

---

*This API reference covers the most commonly used functions. For complete details, see the source code documentation.*
