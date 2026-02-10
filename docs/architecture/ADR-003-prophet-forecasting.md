# ADR-003: Choose Prophet for time series forecasting

## Status
Accepted

## Context
The Cholera CDR MVP requires time series forecasting capabilities for predicting cholera case trends. The forecasting module needs to:

- Handle weekly epidemiological data
- Provide uncertainty intervals for predictions
- Support explainability for public health officials
- Integrate with the existing Python analytics stack
- Be maintainable by the data science team

## Decision
Choose Prophet (Facebook's time series forecasting library) as the primary forecasting engine.

## Rationale

### Prophet Advantages
1. **Designed for Business Forecasting**: Specifically built for forecasting business metrics like epidemiological data
2. **Automatic Seasonality Detection**: Handles yearly, weekly, and daily seasonality automatically
3. **Uncertainty Intervals**: Built-in uncertainty estimation for prediction intervals
4. **Explainability**: Provides trend and seasonality components for interpretation
5. **Python Integration**: Native Python library with pandas DataFrame support
6. **Robust to Missing Data**: Handles gaps and irregularities in time series data
7. **Easy to Use**: Simple API suitable for public health analysts

### Epidemiological Suitability
- **Weekly Data Handling**: Optimized for weekly epidemiological reporting cycles
- **Holiday Effects**: Can incorporate known events (outbreaks, interventions)
- **Trend Detection**: Identifies underlying trends in disease spread
- **Scalable**: Can handle multiple countries and regions simultaneously

## Alternatives Considered

### 1. ARIMA/SARIMA Models
**Pros:**
- Classical statistical approach
- Well-understood methodology
- Good for stationary time series

**Cons:**
- Requires statistical expertise
- Manual parameter tuning
- Less intuitive for non-statisticians
- Poor handling of missing data

### 2. LSTM Neural Networks
**Pros:**
- Can capture complex patterns
- State-of-the-art performance
- Handles multiple variables

**Cons:**
- Requires large datasets
- Complex to train and tune
- Less interpretable ("black box")
- Overkill for weekly epidemiological data

### 3. Exponential Smoothing (ETS)
**Pros:**
- Simple and fast
- Good for short-term forecasting
- Widely understood

**Cons:**
- Limited complexity
- No built-in seasonality detection
- Less flexible than Prophet

### 4. Custom Statistical Models
**Pros:**
- Tailored to specific needs
- Full control over methodology

**Cons:**
- High development cost
- Maintenance burden
- Risk of implementation errors

## Consequences

### Positive
- **Rapid Development**: Prophet's simple API accelerates implementation
- **Maintainability**: Well-documented library with active community support
- **User Adoption**: Easy for public health officials to understand and use
- **Integration**: Works seamlessly with existing pandas-based analytics stack
- **Explainability**: Provides trend and seasonality breakdowns for reporting

### Negative
- **Stan Dependency**: Requires Stan backend for statistical modeling
- **Performance**: May be slower than simpler models for large datasets
- **Limited Flexibility**: Less customizable than custom implementations
- **Learning Curve**: Team needs to understand Prophet's assumptions and limitations

### Neutral
- **Model Complexity**: More complex than simple statistical methods but less than deep learning
- **Compute Requirements**: Moderate CPU requirements for model training
- **Data Requirements**: Works with limited historical data (minimum 2-3 months recommended)

## Implementation Details

### Core Functions
```python
from src.epi_analytics.forecasting import train_prophet_model

# Train forecasting model
model, forecast, metrics = train_prophet_model(df, forecast_weeks=4)
```

### Key Features Implemented
- **Automatic Seasonality Detection**: Yearly patterns in cholera transmission
- **Trend Analysis**: Long-term disease trajectory
- **Uncertainty Estimation**: 95% confidence intervals for predictions
- **Explainability**: Trend and seasonal component breakdown
- **Performance Metrics**: MAE, RMSE, MAPE for model evaluation

### Mock Implementation
For testing without Stan backend dependency:
```python
from src.epi_analytics.mock_prophet import mock_train_prophet_model
model, forecast, metrics = mock_train_prophet_model(df, forecast_weeks=4)
```

## Future Considerations

### Model Improvements
- **Multivariate Forecasting**: Incorporate climate data, population movement
- **Hierarchical Forecasting**: Country-level to regional aggregation
- **Anomaly Detection**: Automatic outbreak identification
- **Model Comparison**: Evaluate against alternative approaches

### Operational Considerations
- **Model Retraining**: Schedule periodic model updates with new data
- **Performance Monitoring**: Track forecast accuracy over time
- **User Training**: Educate analysts on interpreting Prophet outputs
- **Integration**: Connect with Power BI for visualization

## Related Decisions
- **ADR-001**: Microsoft Fabric Platform - Prophet will run in Fabric notebooks
- **ADR-002**: Medallion Architecture - Forecasting outputs stored in Gold layer
- **ADR-005**: Quality Assurance Framework - Forecast accuracy monitored by QA engine

## References
- [Prophet Documentation](https://facebook.github.io/prophet/)
- [Forecasting Principles for Epidemiology](https://www.cdc.gov/epidemiology/)
- [Time Series Forecasting in Public Health](https://www.who.int/publications/i/item/forecasting-epidemiological-data)

---

**Decision Date:** February 10, 2026  
**Review Date:** February 10, 2026  
**Next Review:** When Prophet 2.0 is released or performance issues arise
