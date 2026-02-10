"""Pytest configuration and shared fixtures."""
import pytest
from pathlib import Path
from datetime import datetime


@pytest.fixture
def sample_pdf_path():
    """Return path to sample PDF."""
    return Path("data/sample/cholera_sitrep_2025_wk06.pdf")


@pytest.fixture
def sample_kpi_data():
    """Return sample KPI data dictionary."""
    return {
        'confirmed_cases': 1000,
        'suspected_cases': 1500,
        'deaths': 25,
        'cfr_percent': 2.5,
        'affected_countries': 5
    }


@pytest.fixture
def expected_report_schema():
    """Expected schema for report_summary table."""
    return {
        'report_id': str,
        'report_date': 'datetime',
        'confirmed_cases': int,
        'deaths': int,
        'cfr_percent': float
    }
