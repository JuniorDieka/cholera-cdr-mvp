"""Pydantic data models for validation."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator


class ReportSummary(BaseModel):
    \"\"\"Silver layer report summary schema.\"\"\"
    report_id: str = Field(..., description="Unique report identifier")
    report_date: datetime
    epi_year: int = Field(..., ge=2020, le=2030)
    epi_week: int = Field(..., ge=1, le=53)
    confirmed_cases: int = Field(..., ge=0)
    suspected_cases: int = Field(..., ge=0)
    deaths: int = Field(..., ge=0)
    cfr_percent: Optional[float] = Field(None, ge=0, le=100)
    affected_countries: int = Field(..., ge=0)
    risk_assessment: str
    data_source: str = "PDF"
    ingested_at: datetime
    quality_flag: str = Field(..., pattern="^(PASS|WARNING|FAIL)$")
    
    @validator('cfr_percent')
    def validate_cfr(cls, v, values):
        if v is not None and 'deaths' in values and 'confirmed_cases' in values:
            calculated_cfr = (values['deaths'] / values['confirmed_cases']) * 100
            if abs(calculated_cfr - v) > 0.5:
                raise ValueError(f"CFR mismatch: stated {v}, calculated {calculated_cfr}")
        return v


class CountryWeekly(BaseModel):
    \"\"\"Silver layer country weekly data schema.\"\"\"
    country_weekly_id: str
    report_id: str
    country_name: str
    epi_year: int = Field(..., ge=2020, le=2030)
    epi_week: int = Field(..., ge=1, le=53)
    new_cases: int = Field(..., ge=0)
    cumulative_cases: int = Field(..., ge=0)
    new_deaths: int = Field(..., ge=0)
    cumulative_deaths: int = Field(..., ge=0)
    cfr_percent: Optional[float] = Field(None, ge=0, le=100)
    data_source: str = "PDF"
    ingested_at: datetime


class QualityCheck(BaseModel):
    \"\"\"Data quality check result schema.\"\"\"
    check_id: str
    report_id: str
    check_type: str
    severity: str = Field(..., pattern="^(ERROR|WARNING|INFO)$")
    expected_value: str
    actual_value: str
    check_timestamp: datetime


if __name__ == "__main__":
    # Test schema validation
    print("Testing Pydantic schemas...")
    report = ReportSummary(
        report_id="2025_wk06",
        report_date=datetime.now(),
        epi_year=2025,
        epi_week=6,
        confirmed_cases=1000,
        suspected_cases=1500,
        deaths=25,
        cfr_percent=2.5,
        affected_countries=5,
        risk_assessment="MODERATE",
        ingested_at=datetime.now(),
        quality_flag="PASS"
    )
    print(f" Report validated: {report.report_id}")
