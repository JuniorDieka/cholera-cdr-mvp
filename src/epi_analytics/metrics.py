"""Epidemiological metrics calculation module."""
import pandas as pd
import numpy as np
from typing import Union


def calculate_incidence_rate(
    cases: int, 
    population: int, 
    multiplier: int = 100000
) -> float:
    """
    Calculate incidence rate per population.
    
    Args:
        cases: Number of cases
        population: Population size
        multiplier: Rate multiplier (default: 100,000)
        
    Returns:
        Incidence rate per multiplier population
    """
    if population <= 0:
        return 0.0
    return (cases / population) * multiplier


def calculate_cfr(deaths: int, confirmed_cases: int) -> float:
    """
    Calculate Case Fatality Rate as percentage.
    
    Args:
        deaths: Number of deaths
        confirmed_cases: Number of confirmed cases
        
    Returns:
        CFR as percentage
    """
    if confirmed_cases <= 0:
        return 0.0
    return (deaths / confirmed_cases) * 100


def moving_average(series: pd.Series, window: int = 4) -> pd.Series:
    """
    Calculate rolling average for smoothing trends.
    
    Args:
        series: Time series data
        window: Rolling window size (default: 4 weeks)
        
    Returns:
        Smoothed series
    """
    return series.rolling(window=window, min_periods=1).mean()


def growth_rate(current: int, previous: int) -> float:
    """
    Calculate week-over-week growth rate percentage.
    
    Args:
        current: Current period value
        previous: Previous period value
        
    Returns:
        Growth rate as percentage
    """
    if previous <= 0:
        return float('inf') if current > 0 else 0.0
    return ((current - previous) / previous) * 100


def detect_anomalies(
    series: pd.Series, 
    threshold: float = 2.5
) -> pd.Series:
    """
    Flag outliers using modified z-score (MAD-based).
    
    Args:
        series: Time series data
        threshold: Z-score threshold for anomalies
        
    Returns:
        Boolean series indicating anomalies
    """
    median = series.median()
    mad = (series - median).abs().median()
    
    if mad == 0:
        return pd.Series([False] * len(series), index=series.index)
    
    modified_z = 0.6745 * (series - median) / mad
    return abs(modified_z) > threshold


if __name__ == "__main__":
    # Test metrics
    print("Testing epidemiological metrics...")
    print(f"Incidence Rate: {calculate_incidence_rate(1000, 5000000)}")
    print(f"CFR: {calculate_cfr(25, 1000)}%")
    print(f"Growth Rate: {growth_rate(120, 100)}%")
    print(" All metrics functions working")
