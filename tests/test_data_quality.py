"""Unit tests for quality assurance engine."""
import pytest
from datetime import datetime
from src.epi_analytics.qa_engine import QualityEngine, QualityCheck


def test_quality_engine_initialization():
    """Test quality engine initialization."""
    engine = QualityEngine()
    
    assert engine.tolerance_cfr == 0.5
    assert engine.tolerance_cases == 0.05
    assert len(engine.checks) == 0


def test_cfr_validation_with_match():
    """Test CFR validation when values match."""
    engine = QualityEngine(tolerance_cfr=0.5)
    
    checks = engine.validate_cfr_consistency(
        "test_report", 
        confirmed_cases=1000, 
        deaths=25, 
        reported_cfr=2.5
    )
    
    # Should pass (2.5% calculated vs 2.5% reported)
    assert len(checks) == 0


def test_cfr_validation_with_warning():
    """Test CFR validation with small difference."""
    engine = QualityEngine(tolerance_cfr=0.5)
    
    checks = engine.validate_cfr_consistency(
        "test_report", 
        confirmed_cases=1000, 
        deaths=25, 
        reported_cfr=2.8  # 0.3% difference
    )
    
    # Should generate warning
    assert len(checks) == 1
    assert checks[0].severity == 'WARNING'
    assert checks[0].check_type == 'CFR_MISMATCH'


def test_cfr_validation_with_error():
    """Test CFR validation with large difference."""
    engine = QualityEngine(tolerance_cfr=0.5)
    
    checks = engine.validate_cfr_consistency(
        "test_report", 
        confirmed_cases=1000, 
        deaths=25, 
        reported_cfr=5.0  # 2.5% difference
    )
    
    # Should generate error
    assert len(checks) == 1
    assert checks[0].severity == 'ERROR'
    assert checks[0].check_type == 'CFR_MISMATCH'


def test_cfr_validation_missing_reported():
    """Test CFR validation when no reported CFR."""
    engine = QualityEngine()
    
    checks = engine.validate_cfr_consistency(
        "test_report", 
        confirmed_cases=1000, 
        deaths=25
        # No reported_cfr parameter
    )
    
    # Should generate info check
    assert len(checks) == 1
    assert checks[0].severity == 'INFO'
    assert checks[0].check_type == 'CFR_MISSING'


def test_cfr_validation_zero_cases():
    """Test CFR validation with zero cases."""
    engine = QualityEngine()
    
    checks = engine.validate_cfr_consistency(
        "test_report", 
        confirmed_cases=0, 
        deaths=0, 
        reported_cfr=0.0
    )
    
    # Should handle gracefully (no division by zero)
    assert len(checks) == 0


def test_case_totals_validation_with_match():
    """Test case totals validation when breakdown matches."""
    engine = QualityEngine()
    
    country_data = [
        {'country_name': 'Country A', 'confirmed_cases': 500, 'suspected_cases': 300},
        {'country_name': 'Country B', 'confirmed_cases': 300, 'suspected_cases': 200}
    ]
    
    checks = engine.validate_case_totals(
        "test_report",
        confirmed_cases=800,
        suspected_cases=500,
        country_breakdown=country_data
    )
    
    # Should pass (800 confirmed vs 500+300, 500 suspected vs 300+200)
    assert len(checks) == 0


def test_case_totals_validation_with_mismatch():
    """Test case totals validation with mismatch."""
    engine = QualityEngine()
    
    country_data = [
        {'country_name': 'Country A', 'confirmed_cases': 500, 'suspected_cases': 300},
        {'country_name': 'Country B', 'confirmed_cases': 200, 'suspected_cases': 200}
    ]
    
    checks = engine.validate_case_totals(
        "test_report",
        confirmed_cases=800,  # Reported 800, breakdown total is 700
        suspected_cases=500,
        country_breakdown=country_data
    )
    
    # Should generate warning (100 difference, within 5% tolerance of 800)
    assert len(checks) == 1
    assert checks[0].severity == 'WARNING'
    assert checks[0].check_type == 'CASES_TOTAL_MISMATCH'


def test_epidemiological_week_validation():
    """Test epidemiological week validation."""
    engine = QualityEngine()
    
    # Correct date/week combination
    checks = engine.validate_epidemiological_week(
        "test_report",
        report_date=datetime(2025, 2, 8),  # Saturday of epi week 6, 2025
        epi_year=2025,
        epi_week=6
    )
    
    assert len(checks) == 0
    
    # Incorrect year
    checks = engine.validate_epidemiological_week(
        "test_report",
        report_date=datetime(2025, 2, 8),  # epi year 2025
        epi_year=2024,
        epi_week=6
    )
    
    assert len(checks) == 1
    assert checks[0].severity == 'ERROR'
    assert checks[0].check_type == 'EPI_YEAR_MISMATCH'
    
    # Incorrect week
    checks = engine.validate_epidemiological_week(
        "test_report",
        report_date=datetime(2025, 2, 8),  # epi week 6
        epi_year=2025,
        epi_week=7
    )
    
    assert len(checks) == 1
    assert checks[0].severity == 'ERROR'
    assert checks[0].check_type == 'EPI_WEEK_MISMATCH'


def test_data_completeness_validation():
    """Test data completeness validation."""
    engine = QualityEngine()
    
    # Complete data
    complete_data = {
        'confirmed_cases': 1000,
        'deaths': 25,
        'suspected_cases': 1500,
        'cfr_percent': 2.5,
        'affected_countries': 5
    }
    
    checks = engine.validate_data_completeness("test_report", complete_data)
    assert len(checks) == 0
    
    # Missing required field
    incomplete_data = {
        'deaths': 25,
        'suspected_cases': 1500,
        'cfr_percent': 2.5,
        'affected_countries': 5
    }
    
    checks = engine.validate_data_completeness("test_report", incomplete_data)
    assert len(checks) == 1
    assert checks[0].severity == 'ERROR'
    assert checks[0].check_type == 'REQUIRED_FIELD_MISSING'
    
    # Missing important field
    incomplete_data_2 = {
        'confirmed_cases': 1000,
        'deaths': 25,
        'suspected_cases': 1500,
        'affected_countries': 5
    }
    
    checks = engine.validate_data_completeness("test_report", incomplete_data_2)
    assert len(checks) == 1
    assert checks[0].severity == 'WARNING'
    assert checks[0].check_type == 'IMPORTANT_FIELD_MISSING'


def test_value_ranges_validation():
    """Test value ranges validation."""
    engine = QualityEngine()
    
    # Valid data
    valid_data = {
        'confirmed_cases': 1000,
        'deaths': 25,
        'cfr_percent': 2.5,
        'affected_countries': 5
    }
    
    checks = engine.validate_value_ranges("test_report", valid_data)
    assert len(checks) == 0
    
    # Negative values
    invalid_data = {
        'confirmed_cases': -100,
        'deaths': 25,
        'cfr_percent': 2.5,
        'affected_countries': 5
    }
    
    checks = engine.validate_value_ranges("test_report", invalid_data)
    assert len(checks) == 1
    assert checks[0].severity == 'ERROR'
    assert checks[0].check_type == 'NEGATIVE_VALUE'
    
    # CFR out of range
    invalid_data_2 = {
        'confirmed_cases': 1000,
        'deaths': 25,
        'cfr_percent': 150.0,  # > 100%
        'affected_countries': 5
    }
    
    checks = engine.validate_value_ranges("test_report", invalid_data_2)
    assert len(checks) == 1
    assert checks[0].severity == 'ERROR'
    assert checks[0].check_type == 'CFR_OUT_OF_RANGE'


def test_quality_score_calculation():
    """Test quality score calculation."""
    engine = QualityEngine()
    
    # Perfect data
    perfect_checks = []
    score = engine.get_quality_score(perfect_checks)
    assert score == 100.0
    
    # All warnings
    warning_checks = [
        QualityCheck(
            check_id="test1",
            report_id="test",
            check_type="TEST",
            severity="WARNING",
            expected_value="test",
            actual_value="test",
            check_timestamp=datetime.now()
        ),
        QualityCheck(
            check_id="test2",
            report_id="test",
            check_type="TEST",
            severity="WARNING",
            expected_value="test",
            actual_value="test",
            check_timestamp=datetime.now()
        )
    ]
    
    score = engine.get_quality_score(warning_checks)
    assert score == 50.0  # Average of 50 and 50
    
    # Mixed severity
    mixed_checks = [
        QualityCheck(
            check_id="test1",
            report_id="test",
            check_type="TEST",
            severity="ERROR",
            expected_value="test",
            actual_value="test",
            check_timestamp=datetime.now()
        ),
        QualityCheck(
            check_id="test2",
            report_id="test",
            check_type="TEST",
            severity="WARNING",
            expected_value="test",
            actual_value="test",
            check_timestamp=datetime.now()
        ),
        QualityCheck(
            check_id="test3",
            report_id="test",
            check_type="TEST",
            severity="INFO",
            expected_value="test",
            actual_value="test",
            check_timestamp=datetime.now()
        )
    ]
    
    score = engine.get_quality_score(mixed_checks)
    assert score == 46.7  # (0 + 50 + 90) / 3


def test_comprehensive_validation():
    """Test comprehensive validation workflow."""
    engine = QualityEngine()
    
    # Test data with some issues
    test_data = {
        'report_id': '2025_wk06',
        'confirmed_cases': 1000,
        'suspected_cases': 1500,
        'deaths': 25,
        'cfr_percent': 3.0,  # 1.0% difference from calculated
        'affected_countries': 5,
        'report_date': datetime(2025, 2, 8),
        'epi_year': 2025,
        'epi_week': 6
    }
    
    country_breakdown = [
        {'country_name': 'Country A', 'confirmed_cases': 500, 'suspected_cases': 300},
        {'country_name': 'Country B', 'confirmed_cases': 300, 'suspected_cases': 200}
    ]
    
    # Run comprehensive validation
    checks = engine.run_comprehensive_validation(
        '2025_wk06',
        test_data,
        country_breakdown
    )
    
    # Should detect CFR mismatch
    cfr_checks = [c for c in checks if c.check_type == 'CFR_MISMATCH']
    assert len(cfr_checks) == 1
    assert cfr_checks[0].severity == 'WARNING'
    
    # Should have some checks but not critical errors
    error_checks = [c for c in checks if c.severity == 'ERROR']
    assert len(error_checks) == 0
    
    # Calculate quality score
    score = engine.get_quality_score(checks)
    assert score >= 80.0  # Should be good quality
