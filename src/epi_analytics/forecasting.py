"""ML forecasting module for cholera surveillance data."""
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error


def train_prophet_model(
    df: pd.DataFrame, 
    forecast_weeks: int = 4
) -> Tuple[Prophet, pd.DataFrame, Dict[str, float]]:
    """
    Train Prophet model for case forecasting.
    
    Args:
        df: DataFrame with 'ds' (date) and 'y' (cases) columns
        forecast_weeks: Number of weeks to predict
        
    Returns:
        Tuple of (model, forecast_df, metrics_dict)
    """
    # Initialize model
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        changepoint_prior_scale=0.05,
        interval_width=0.95
    )
    
    # Fit model
    model.fit(df)
    
    # Make future dataframe
    future = model.make_future_dataframe(periods=forecast_weeks, freq='W')
    forecast = model.predict(future)
    
    # Calculate metrics on training data
    y_true = df['y'].values
    y_pred = forecast['yhat'][:len(y_true)].values
    
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    
    metrics = {
        'MAE': mae,
        'RMSE': rmse,
        'MAPE': mape
    }
    
    return model, forecast, metrics


def explain_forecast(model: Prophet, forecast: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate explainability outputs for Prophet forecast.
    
    Args:
        model: Trained Prophet model
        forecast: Forecast DataFrame
        
    Returns:
        Dictionary with explainability information
    """
    # Extract trend and uncertainty information
    trend_data = forecast[['ds', 'trend']].tail(forecast_weeks).to_dict('records')
    
    # Extract uncertainty intervals
    uncertainty_data = forecast[['ds', 'yhat_lower', 'yhat_upper']].tail(forecast_weeks).to_dict('records')
    
    # Get changepoints
    changepoints = model.changepoints.tolist()
    
    # Check seasonality
    seasonality_info = 'Annual pattern detected' if model.yearly_seasonality else 'No clear seasonality'
    
    return {
        'trend': trend_data,
        'uncertainty': uncertainty_data,
        'changepoints': changepoints,
        'seasonality': seasonality_info,
        'forecast_weeks': len(forecast)
    }


def evaluate_model_performance(
    actual: pd.Series, 
    predicted: pd.Series
) -> Dict[str, float]:
    """
    Evaluate model performance with multiple metrics.
    
    Args:
        actual: Actual values
        predicted: Predicted values
        
    Returns:
        Dictionary of performance metrics
    """
    # Ensure same length
    min_len = min(len(actual), len(predicted))
    actual = actual[:min_len]
    predicted = predicted[:min_len]
    
    # Calculate metrics
    mae = mean_absolute_error(actual, predicted)
    rmse = np.sqrt(mean_squared_error(actual, predicted))
    
    # MAPE (avoid division by zero)
    mask = actual != 0
    mape = np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100 if mask.any() else 0
    
    # Mean Absolute Scaled Error (MASE)
    naive_forecast = actual.shift(1).dropna()
    mase = mean_absolute_error(actual[1:], predicted[1:]) / mean_absolute_error(actual[1:], naive_forecast) if len(naive_forecast) > 0 else 0
    
    return {
        'MAE': mae,
        'RMSE': rmse,
        'MAPE': mape,
        'MASE': mase
    }


def forecast_summary(
    forecast: pd.DataFrame, 
    confidence_level: float = 0.95
) -> pd.DataFrame:
    """
    Create a summary of forecast results.
    
    Args:
        forecast: Prophet forecast DataFrame
        confidence_level: Confidence level for intervals
        
    Returns:
        Summary DataFrame with key forecast information
    """
    # Return all forecast data
    forecast_data = forecast
    
    # Calculate key metrics
    summary_data = []
    
    for _, row in forecast_data.iterrows():
        summary_data.append({
            'forecast_date': row['ds'],
            'predicted_cases': row['yhat'],
            'lower_bound': row['yhat_lower'],
            'upper_bound': row['yhat_upper'],
            'uncertainty_width': row['yhat_upper'] - row['yhat_lower'],
            'trend': row['trend'],
            'yearly': row.get('yearly', 0),
            'weekly': row.get('weekly', 0)
        })
    
    return pd.DataFrame(summary_data)


if __name__ == "__main__":
    # Test forecasting module
    print("Testing ML forecasting module...")
    
    # Create sample data
    dates = pd.date_range(start='2024-01-01', periods=52, freq='W')
    cases = [100 + i*2 + np.random.normal(0, 10) for i in range(52)]
    
    df = pd.DataFrame({
        'ds': dates,
        'y': cases
    })
    
    # Train model
    model, forecast, metrics = train_prophet_model(df, forecast_weeks=4)
    
    print(f"Model Performance:")
    for metric, value in metrics.items():
        print(f"  {metric}: {value:.2f}")
    
    # Generate explanation
    explanation = explain_forecast(model, forecast)
    print(f"Forecast explanation: {explanation['seasonality']}")
