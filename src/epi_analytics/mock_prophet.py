"""Mock Prophet for testing without Stan backend."""
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any


class MockProphet:
    """Mock Prophet class for testing without Stan backend."""
    
    def __init__(self, **kwargs):
        self.yearly_seasonality = kwargs.get('yearly_seasonality', True)
        self.weekly_seasonality = kwargs.get('weekly_seasonality', False)
        self.changepoint_prior_scale = kwargs.get('changepoint_prior_scale', 0.05)
        self.interval_width = kwargs.get('interval_width', 0.95)
        self.fitted_ = False
    
    def fit(self, df: pd.DataFrame):
        """Mock fit method."""
        self.fitted_ = True
        return self
    
    def make_future_dataframe(self, periods: int, freq: str = 'W') -> pd.DataFrame:
        """Mock future dataframe creation."""
        if not self.fitted_:
            raise ValueError("Model must be fitted before making future dataframe")
        
        # This should include historical data + future periods
        # For mock purposes, we'll just return the future periods
        # The actual Prophet would include historical data
        last_date = pd.Timestamp.now()
        future_dates = pd.date_range(start=last_date, periods=periods, freq=freq)
        return pd.DataFrame({'ds': future_dates})
    
    def predict(self, future_df: pd.DataFrame) -> pd.DataFrame:
        """Mock prediction."""
        if not self.fitted_:
            raise ValueError("Model must be fitted before prediction")
        
        # Generate mock predictions for all dates (historical + future)
        n_rows = len(future_df)
        base_value = 100
        
        # Create predictions that include historical fitting
        forecast_data = {
            'ds': future_df['ds'],
            'yhat': base_value + np.random.normal(0, 10, n_rows),
            'yhat_lower': base_value - 20 + np.random.normal(0, 5, n_rows),
            'yhat_upper': base_value + 20 + np.random.normal(0, 5, n_rows),
            'trend': np.linspace(base_value - 10, base_value + 10, n_rows),
            'yearly': np.random.normal(2, 1, n_rows),
            'weekly': np.zeros(n_rows)  # No weekly seasonality in our mock
        }
        
        return pd.DataFrame(forecast_data)


def mock_train_prophet_model(
    df: pd.DataFrame, 
    forecast_weeks: int = 4
) -> Tuple[MockProphet, pd.DataFrame, Dict[str, float]]:
    """
    Mock Prophet model training for testing.
    
    Args:
        df: DataFrame with 'ds' and 'y' columns
        forecast_weeks: Number of weeks to predict
        
    Returns:
        Tuple of (model, forecast_df, metrics_dict)
    """
    # Initialize mock model
    model = MockProphet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        changepoint_prior_scale=0.05,
        interval_width=0.95
    )
    
    # Fit model
    model.fit(df)
    
    # Create combined dataframe (historical + future)
    last_date = df['ds'].max()
    future_dates = pd.date_range(start=last_date + pd.Timedelta(weeks=1), periods=forecast_weeks, freq='W')
    
    # Combine historical and future dates
    all_dates = pd.concat([df['ds'], pd.Series(future_dates)], ignore_index=True)
    combined_df = pd.DataFrame({'ds': all_dates})
    
    # Generate predictions for all dates
    forecast = model.predict(combined_df)
    
    # Calculate mock metrics (only on historical data)
    historical_forecast = forecast[:len(df)]
    y_true = df['y'].values
    y_pred = historical_forecast['yhat'].values
    
    # Ensure same length
    min_len = min(len(y_true), len(y_pred))
    y_true = y_true[:min_len]
    y_pred = y_pred[:min_len]
    
    mae = np.mean(np.abs(y_true - y_pred))
    rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
    mape = np.mean(np.abs((y_true - y_pred) / (y_true + 1e-8))) * 100  # Avoid division by zero
    
    metrics = {
        'MAE': mae,
        'RMSE': rmse,
        'MAPE': mape
    }
    
    return model, forecast, metrics


if __name__ == "__main__":
    # Test mock Prophet
    print("Testing Mock Prophet...")
    
    # Create sample data
    dates = pd.date_range(start='2024-01-01', periods=52, freq='W')
    cases = [100 + i*2 + np.random.normal(0, 10) for i in range(52)]
    
    df = pd.DataFrame({
        'ds': dates,
        'y': cases
    })
    
    # Train model
    model, forecast, metrics = mock_train_prophet_model(df, forecast_weeks=4)
    
    print(f"Mock Model Performance:")
    for metric, value in metrics.items():
        print(f"  {metric}: {value:.2f}")
    
    print(f"Forecast shape: {forecast.shape}")
    print("Mock Prophet working correctly!")
