#!/usr/bin/env python3
"""
Generate mock data for Power BI dashboard development.
Creates realistic cholera surveillance data for testing.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

# Create output directory
output_dir = Path(__file__).parent.parent / "powerbi" / "mock_data"
output_dir.mkdir(parents=True, exist_ok=True)

# Set random seed for reproducibility
np.random.seed(42)

# ============================================
# Mock Cases Data (52 weeks, 9 countries)
# ============================================

countries = ['Zimbabwe', 'Zambia', 'Mozambique', 'Malawi', 'Tanzania', 
             'Kenya', 'Uganda', 'Ethiopia', 'Somalia']
country_codes = ['ZWE', 'ZMB', 'MOZ', 'MWI', 'TZA', 'KEN', 'UGA', 'ETH', 'SOM']
au_regions = ['Southern', 'Southern', 'Southern', 'Southern', 'East', 
              'East', 'East', 'East', 'East']

start_date = datetime(2024, 1, 7)  # First Sunday of 2024
cases_data = []

for week in range(52):
    week_date = start_date + timedelta(weeks=week)
    epi_year = 2024
    epi_week = week + 1
    
    for i, country in enumerate(countries):
        # Base cases with country variation
        base_cases = np.random.randint(50, 300)
        
        # Seasonal pattern (higher in rainy season)
        seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * week / 52)
        
        # Outbreak simulation (Zimbabwe and Mozambique weeks 20-30)
        outbreak_factor = 1.5 if (country in ['Zimbabwe', 'Mozambique'] and 20 <= week <= 30) else 1.0
        
        new_cases = int(base_cases * seasonal_factor * outbreak_factor)
        new_deaths = int(new_cases * np.random.uniform(0.015, 0.035))
        cfr = round((new_deaths / new_cases * 100) if new_cases > 0 else 0, 2)
        
        cases_data.append({
            'date': week_date.strftime('%Y-%m-%d'),
            'epi_year': epi_year,
            'epi_week': epi_week,
            'country_code': country_codes[i],
            'country_name': country,
            'new_cases': new_cases,
            'cumulative_cases': 0,  # Will be calculated
            'new_deaths': new_deaths,
            'cfr_percent': cfr,
            'au_region': au_regions[i]
        })

df_cases = pd.DataFrame(cases_data)

# Calculate cumulative cases by country
for country_code in df_cases['country_code'].unique():
    mask = df_cases['country_code'] == country_code
    df_cases.loc[mask, 'cumulative_cases'] = df_cases.loc[mask, 'new_cases'].cumsum()

# Save to CSV
df_cases.to_csv(output_dir / 'mock_cases.csv', index=False)
print(f"✅ Created mock_cases.csv with {len(df_cases)} rows (52 weeks × 9 countries)")

# ============================================
# Mock Forecast Data (4 weeks ahead)
# ============================================

last_date = df_cases['date'].max()
last_date_dt = datetime.strptime(last_date, '%Y-%m-%d')

forecast_data = []

for week in range(1, 5):
    forecast_date = last_date_dt + timedelta(weeks=week)
    epi_week = 52 + week
    
    # Predict based on recent trend
    recent_avg = df_cases.tail(4 * 9)['new_cases'].mean()
    predicted = int(recent_avg * np.random.uniform(0.9, 1.1))
    
    forecast_data.append({
        'forecast_date': forecast_date.strftime('%Y-%m-%d'),
        'epi_week': epi_week if epi_week <= 53 else epi_week - 53,
        'predicted_cases': predicted,
        'lower_bound': int(predicted * 0.7),
        'upper_bound': int(predicted * 1.3),
        'confidence_level': 95
    })

df_forecast = pd.DataFrame(forecast_data)
df_forecast.to_csv(output_dir / 'mock_forecast.csv', index=False)
print(f"✅ Created mock_forecast.csv with {len(df_forecast)} rows (4 weeks forecast)")

# ============================================
# Mock Quality Checks Data
# ============================================

quality_data = []
check_id = 1

# Sample quality checks for recent reports
for week in [50, 51, 52]:
    report_id = f"2024_wk{week:02d}"
    
    # CFR consistency check
    quality_data.append({
        'check_id': f'QC{check_id:04d}',
        'check_date': (start_date + timedelta(weeks=week-1)).strftime('%Y-%m-%d'),
        'check_type': 'CFR_CONSISTENCY',
        'severity': 'PASS',
        'expected_value': '2.5',
        'actual_value': '2.48',
        'affected_report': report_id,
        'status': 'PASS'
    })
    check_id += 1
    
    # Case total reconciliation
    quality_data.append({
        'check_id': f'QC{check_id:04d}',
        'check_date': (start_date + timedelta(weeks=week-1)).strftime('%Y-%m-%d'),
        'check_type': 'CASE_TOTAL_RECONCILIATION',
        'severity': 'WARNING' if week == 51 else 'PASS',
        'expected_value': '1500',
        'actual_value': '1485' if week == 51 else '1500',
        'affected_report': report_id,
        'status': 'WARNING' if week == 51 else 'PASS'
    })
    check_id += 1
    
    # Data completeness
    quality_data.append({
        'check_id': f'QC{check_id:04d}',
        'check_date': (start_date + timedelta(weeks=week-1)).strftime('%Y-%m-%d'),
        'check_type': 'DATA_COMPLETENESS',
        'severity': 'PASS',
        'expected_value': '100',
        'actual_value': '95' if week == 50 else '100',
        'affected_report': report_id,
        'status': 'PASS'
    })
    check_id += 1

# Add one ERROR example
quality_data.append({
    'check_id': f'QC{check_id:04d}',
    'check_date': (start_date + timedelta(weeks=48)).strftime('%Y-%m-%d'),
    'check_type': 'CFR_CONSISTENCY',
    'severity': 'ERROR',
    'expected_value': '2.5',
    'actual_value': '5.2',
    'affected_report': '2024_wk49',
    'status': 'ERROR'
})

df_quality = pd.DataFrame(quality_data)
df_quality.to_csv(output_dir / 'mock_quality_checks.csv', index=False)
print(f"✅ Created mock_quality_checks.csv with {len(df_quality)} rows")

print("\n✅ All mock data files created successfully!")
print(f"   Output directory: {output_dir}")
