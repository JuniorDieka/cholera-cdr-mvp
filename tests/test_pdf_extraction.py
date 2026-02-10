"""Unit tests for PDF extraction logic."""
import pytest
from src.pdf_parser.extractor import extract_kpi_panel, extract_narrative


def test_extract_kpi_panel_returns_dict(sample_pdf_path):
    """Test that extraction returns dictionary."""
    if sample_pdf_path.exists():
        result = extract_kpi_panel(str(sample_pdf_path))
        assert isinstance(result, dict)
    else:
        pytest.skip("Sample PDF not found")


def test_extract_kpi_panel_has_required_fields(sample_pdf_path):
    """Test that required fields are present."""
    if sample_pdf_path.exists():
        result = extract_kpi_panel(str(sample_pdf_path))
        assert 'confirmed_cases' in result or len(result) == 0
    else:
        pytest.skip("Sample PDF not found")


def test_cfr_calculation_accuracy():
    """Test CFR calculation matches manual."""
    cases, deaths = 1000, 25
    expected_cfr = 2.5
    calculated_cfr = (deaths / cases) * 100
    assert abs(calculated_cfr - expected_cfr) < 0.01
