"""Epidemiological analytics package."""

from .metrics import (
    calculate_incidence_rate,
    calculate_cfr,
    moving_average,
    growth_rate,
    detect_anomalies
)

from .forecasting import (
    train_prophet_model,
    explain_forecast,
    evaluate_model_performance,
    forecast_summary
)

from .qa_engine import (
    QualityEngine,
    QualityCheck
)

__all__ = [
    'calculate_incidence_rate',
    'calculate_cfr', 
    'moving_average',
    'growth_rate',
    'detect_anomalies',
    'train_prophet_model',
    'explain_forecast',
    'evaluate_model_performance',
    'forecast_summary',
    'QualityEngine',
    'QualityCheck'
]