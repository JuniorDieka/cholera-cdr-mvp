"""Unit tests for ML forecasting module."""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.epi_analytics.forecasting import (
    train_prophet_model,
    explain_forecast,
    evaluate_model_performance,
    forecast_summary
)


def test_prophet_model_training():
    """Test Prophet model training with sample data."""
    # Create sample data
    dates = pd.date_range(start='2024-01-01', periods=52, freq='W')
    cases = [100 + i*2 + np.random.normal(0, 10) for i in range(52)]
    
    df = pd.DataFrame({
        'ds': dates,
        'y': cases
    })
    
    # Train model
    model, forecast, metrics = train_prophet_model(df, forecast_weeks=4)
    
    # Verify model was trained
    assert model is not None
    assert isinstance(forecast, pd.DataFrame)
    assert len(forecast) == len(df) + 4  # Original + forecast
    
    # Verify metrics
    assert 'MAE' in metrics
    assert 'RMSE' in metrics
    assert 'MAPE' in metrics
    assert all(m >= 0 for m in metrics.values())


def test_forecast_explainability():
    """Test forecast explainability features."""
    # Create sample data
    dates = pd.date_range(start='2024-01-01', periods=26, freq='W')
    cases = [100 + i*2 for i in range(26)]
    
    df = pd.DataFrame({
        'ds': dates,
        'y': cases
    })
    
    # Train model
    model, forecast, _ = train_prophet_model(df, forecast_weeks=4)
    
    # Test explainability
    explanation = explain_forecast(model, forecast)
    
    assert 'trend' in explanation
    assert 'uncertainty' in explanation
    assert 'changepoints' in explanation
    assert 'seasonality' in explanation
    assert explanation['forecast_weeks'] == 4


def test_model_performance_evaluation():
    """Test model performance evaluation."""
    # Create sample data
    actual = pd.Series([100, 120, 110, 130, 140, 125, 135, 150, 145, 160])
    predicted = pd.Series([105, 118, 112, 128, 142, 123, 133, 148, 147, 158])
    
    # Evaluate performance
    metrics = evaluate_model_performance(actual, predicted)
    
    # Verify metrics
    assert 'MAE' in metrics
    assert 'RMSE' in metrics
    assert 'MAPE' in metrics
    assert 'MASE' in metrics
    assert all(m >= 0 for m in metrics.values())


def test_forecast_summary():
    """Test forecast summary generation."""
    # Create sample forecast data
    dates = pd.date_range(start='2024-01-01', periods=8, freq='W')
    forecast_data = {
        'ds': dates,
        'yhat': [100, 110, 105, 115, 120, 125, 130, 135],
        'yhat_lower': [95, 105, 100, 110, 115, 120, 125, 130],
        'yhat_upper': [105, 115, 110, 120, 125, 130, 135, 140],
        'trend': [90, 92, 94, 96, 98, 100, 102, 104],
        'yearly': [2, 2, 2, 2, 2, 2, 2, 2],
        'weekly': [0, 0, 0, 0, 0, 0, 0, 0]
    }
    
    forecast = pd.DataFrame(forecast_data)
    
    # Generate summary
    summary = forecast_summary(forecast)
    
    # Verify summary structure
    assert isinstance(summary, pd.DataFrame)
    assert len(summary) == 8
    assert 'forecast_date' in summary.columns
    assert 'predicted_cases' in summary.columns
    assert 'lower_bound' in summary.columns
    assert 'upper_bound' in summary.columns
    assert 'uncertainty_width' in summary.columns


def test_prophet_model_with_insufficient_data():
    """Test Prophet model behavior with minimal data."""
    # Create very small dataset
    dates = pd.date_range(start='2024-01-01', periods=4, freq='W')
    cases = [100, 110, 105, 115]
    
    df = pd.DataFrame({
        'ds': dates,
        'y': cases
    })
    
    # Should still work but with warnings
    model, forecast, metrics = train_prophet_model(df, forecast_weeks=2)
    
    assert model is not None
    assert len(forecast) == 6  # 4 original + 2 forecast


def test_forecast_with_zero_cases():
    """Test forecasting with zero cases."""
    # Create data with zero cases
    dates = pd.date_range(start='2024-01-01', periods=10, freq='W')
    cases = [0, 0, 5, 0, 0, 0, 0, 0, 0, 0]
    
    df = pd.DataFrame({
        'ds': dates,
        'y': cases
    })
    
    # Should handle zero cases gracefully
    model, forecast, metrics = train_prophet_model(df, forecast_weeks=2)
    
    assert model is not None
    assert len(forecast) == 12  # 10 original + 2 forecast


def test_model_reproducibility():
    """Test that model training is reproducible."""
    # Create sample data
    dates = pd.date_range(start='2024-01-01', periods=20, freq='W')
    cases = [100 + i*2 + np.random.normal(0, 5) for i in range(20)]
    
    df = pd.DataFrame({
        'ds': dates,
        'y': cases
    })
    
    # Train model twice
    model1, forecast1, metrics1 = train_prophet_model(df, forecast_weeks=2)
    model2, forecast2, metrics2 = train_prophet_model(df, forecast_weeks=2)
    
    # Results should be identical for deterministic algorithms
    assert metrics1['MAE'] == metrics2['MAE']
    assert metrics1['RMSE'] == metrics2['RMSE']
    assert metrics1['MAPE'] == metrics2['MAPE']
