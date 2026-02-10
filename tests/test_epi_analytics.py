"""Unit tests for epidemiological analytics."""
import pytest
import pandas as pd
from src.epi_analytics.metrics import (
    calculate_incidence_rate,
    calculate_cfr,
    moving_average,
    growth_rate
)


def test_incidence_rate_calculation():
    """Test incidence rate formula."""
    rate = calculate_incidence_rate(cases=100, population=1000000, multiplier=100000)
    assert rate == 10.0


def test_cfr_calculation():
    """Test CFR percentage calculation."""
    cfr = calculate_cfr(deaths=25, confirmed_cases=1000)
    assert cfr == 2.5


def test_cfr_with_zero_cases():
    """Test CFR handles zero cases gracefully."""
    cfr = calculate_cfr(deaths=0, confirmed_cases=0)
    assert cfr == 0.0


def test_moving_average():
    """Test moving average calculation."""
    series = pd.Series([10, 20, 30, 40])
    ma = moving_average(series, window=2)
    assert ma.iloc[-1] == 35.0


def test_growth_rate_positive():
    """Test positive growth rate."""
    rate = growth_rate(current=120, previous=100)
    assert rate == 20.0


def test_growth_rate_negative():
    """Test negative growth rate."""
    rate = growth_rate(current=80, previous=100)
    assert rate == -20.0
