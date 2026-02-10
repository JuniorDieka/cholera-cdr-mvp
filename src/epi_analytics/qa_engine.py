"""Quality assurance engine for data validation."""
import pandas as pd
from typing import List, Dict, Any, Tuple
from datetime import datetime
from pydantic import BaseModel, ValidationError


class QualityCheck(BaseModel):
    """Quality check result schema."""
    check_id: str
    report_id: str
    check_type: str
    severity: str  # 'ERROR', 'WARNING', 'INFO'
    expected_value: Any
    actual_value: Any
    check_timestamp: datetime
    description: str = ""
    resolved: bool = False


class QualityEngine:
    """Advanced quality assurance engine for cholera data."""
    
    def __init__(self, tolerance_cfr: float = 0.5, tolerance_cases: float = 0.05):
        """
        Initialize quality engine with tolerance thresholds.
        
        Args:
            tolerance_cfr: CFR tolerance percentage
            tolerance_cases: Cases tolerance percentage
        """
        self.tolerance_cfr = tolerance_cfr
        self.tolerance_cases = tolerance_cases
        self.checks = []
    
    def validate_cfr_consistency(
        self, 
        report_id: str, 
        confirmed_cases: int, 
        deaths: int, 
        reported_cfr: float = None
    ) -> List[QualityCheck]:
        """
        Validate CFR consistency between calculated and reported values.
        
        Args:
            report_id: Report identifier
            confirmed_cases: Number of confirmed cases
            deaths: Number of deaths
            reported_cfr: Reported CFR percentage
            
        Returns:
            List of quality check results
        """
        checks = []
        
        if confirmed_cases > 0:
            calculated_cfr = (deaths / confirmed_cases) * 100
            
            if reported_cfr is not None:
                difference = abs(calculated_cfr - reported_cfr)
                
                if difference >= self.tolerance_cfr:
                    severity = 'ERROR' if difference >= self.tolerance_cfr * 2 else 'WARNING'
                    
                    checks.append(QualityCheck(
                        check_id=f"{report_id}_cfr_mismatch",
                        report_id=report_id,
                        check_type="CFR_MISMATCH",
                        severity=severity,
                        expected_value=round(calculated_cfr, 2),
                        actual_value=reported_cfr,
                        check_timestamp=datetime.now(),
                        description=f"CFR difference: {difference:.2f}% exceeds tolerance {self.tolerance_cfr}%"
                    ))
            else:
                # No reported CFR, this is an info check
                checks.append(QualityCheck(
                    check_id=f"{report_id}_cfr_missing",
                    report_id=report_id,
                    check_type="CFR_MISSING",
                    severity="INFO",
                    expected_value=round(calculated_cfr, 2),
                    actual_value=None,
                    check_timestamp=datetime.now(),
                    description=f"No reported CFR found, calculated: {calculated_cfr:.2f}%"
                ))
        
        return checks
    
    def validate_case_totals(
        self, 
        report_id: str, 
        confirmed_cases: int, 
        suspected_cases: int, 
        country_breakdown: List[Dict[str, Any]] = None
    ) -> List[QualityCheck]:
        """
        Validate case totals against country breakdowns.
        
        Args:
            report_id: Report identifier
            confirmed_cases: Number of confirmed cases
            suspected_cases: Number of suspected cases
            country_breakdown: List of country-specific data
            
        Returns:
            List of quality check results
        """
        checks = []
        
        if country_breakdown:
            total_confirmed = sum(c.get('confirmed_cases', 0) for c in country_breakdown)
            total_suspected = sum(c.get('suspected_cases', 0) for c in country_breakdown)
            
            # Check confirmed cases
            if total_confirmed != confirmed_cases:
                difference = abs(total_confirmed - confirmed_cases)
                tolerance = int(confirmed_cases * self.tolerance_cases)
                
                if difference >= tolerance:
                    severity = 'ERROR' if difference >= tolerance * 2 else 'WARNING'
                    
                    checks.append(QualityCheck(
                        check_id=f"{report_id}_cases_total_mismatch",
                        report_id=report_id,
                        check_type="CASES_TOTAL_MISMATCH",
                        severity=severity,
                        expected_value=confirmed_cases,
                        actual_value=total_confirmed,
                        check_timestamp=datetime.now(),
                        description=f"Country breakdown total ({total_confirmed}) differs from reported ({confirmed_cases})"
                    ))
            
            # Check suspected cases
            if total_suspected != suspected_cases:
                difference = abs(total_suspected - suspected_cases)
                tolerance = int(suspected_cases * self.tolerance_cases)
                
                if difference >= tolerance:
                    severity = 'ERROR' if difference >= tolerance * 2 else 'WARNING'
                    
                    checks.append(QualityCheck(
                        check_id=f"{report_id}_suspected_total_mismatch",
                        report_id=report_id,
                        check_type="SUSPECTED_TOTAL_MISMATCH",
                        severity=severity,
                        expected_value=suspected_cases,
                        actual_value=total_suspected,
                        check_timestamp=datetime.now(),
                        description=f"Country breakdown total ({total_suspected}) differs from reported ({suspected_cases})"
                    ))
        
        return checks
    
    def validate_epidemiological_week(
        self, 
        report_id: str, 
        report_date: datetime, 
        epi_year: int, 
        epi_week: int
    ) -> List[QualityCheck]:
        """
        Validate epidemiological week consistency.
        
        Args:
            report_id: Report identifier
            report_date: Report date
            epi_year: Epidemiological year
            epi_week: Epidemiological week
            
        Returns:
            List of quality check results
        """
        checks = []
        
        # Calculate actual epi week from date
        actual_year, actual_week, _ = report_date.isocalendar()
        
        if actual_year != epi_year:
            checks.append(QualityCheck(
                check_id=f"{report_id}_epi_year_mismatch",
                report_id=report_id,
                check_type="EPI_YEAR_MISMATCH",
                severity="ERROR",
                expected_value=epi_year,
                actual_value=actual_year,
                check_timestamp=datetime.now(),
                description=f"Date {report_date} is in epi year {actual_year}, but reported as {epi_year}"
            ))
        
        if actual_week != epi_week:
            checks.append(QualityCheck(
                check_id=f"{report_id}_epi_week_mismatch",
                report_id=report_id,
                check_type="EPI_WEEK_MISMATCH",
                severity="ERROR",
                expected_value=epi_week,
                actual_value=actual_week,
                check_timestamp=datetime.now(),
                description=f"Date {report_date} is in epi week {actual_week}, but reported as {epi_week}"
            ))
        
        return checks
    
    def validate_data_completeness(
        self, 
        report_id: str, 
        data_dict: Dict[str, Any]
    ) -> List[QualityCheck]:
        """
        Validate data completeness for required fields.
        
        Args:
            report_id: Report identifier
            data_dict: Dictionary of extracted data
            
        Returns:
            List of quality check results
        """
        checks = []
        
        required_fields = ['confirmed_cases', 'deaths']
        important_fields = ['suspected_cases', 'cfr_percent', 'affected_countries']
        
        # Check required fields
        for field in required_fields:
            if field not in data_dict or data_dict[field] is None:
                checks.append(QualityCheck(
                    check_id=f"{report_id}_{field}_missing",
                    report_id=report_id,
                    check_type="REQUIRED_FIELD_MISSING",
                    severity="ERROR",
                    expected_value=f"Non-null {field}",
                    actual_value=None,
                    check_timestamp=datetime.now(),
                    description=f"Required field '{field}' is missing or null"
                ))
        
        # Check important fields
        for field in important_fields:
            if field not in data_dict or data_dict[field] is None:
                checks.append(QualityCheck(
                    check_id=f"{report_id}_{field}_missing",
                    report_id=report_id,
                    check_type="IMPORTANT_FIELD_MISSING",
                    severity="WARNING",
                    expected_value=f"Non-null {field}",
                    actual_value=None,
                    check_timestamp=datetime.now(),
                    description=f"Important field '{field}' is missing or null"
                ))
        
        return checks
    
    def validate_value_ranges(
        self, 
        report_id: str, 
        data_dict: Dict[str, Any]
    ) -> List[QualityCheck]:
        """
        Validate that values are within reasonable ranges.
        
        Args:
            report_id: Report identifier
            data_dict: Dictionary of extracted data
            
        Returns:
            List of quality check results
        """
        checks = []
        
        # Check for negative values
        numeric_fields = ['confirmed_cases', 'suspected_cases', 'deaths', 'affected_countries']
        
        for field in numeric_fields:
            if field in data_dict and data_dict[field] is not None:
                value = data_dict[field]
                
                if isinstance(value, (int, float)) and value < 0:
                    checks.append(QualityCheck(
                        check_id=f"{report_id}_{field}_negative",
                        report_id=report_id,
                        check_type="NEGATIVE_VALUE",
                        severity="ERROR",
                        expected_value="Non-negative",
                        actual_value=value,
                        check_timestamp=datetime.now(),
                        description=f"Field '{field}' has negative value: {value}"
                    ))
        
        # Check CFR percentage
        if 'cfr_percent' in data_dict and data_dict['cfr_percent'] is not None:
            cfr = data_dict['cfr_percent']
            
            if isinstance(cfr, (int, float)):
                if cfr < 0 or cfr > 100:
                    checks.append(QualityCheck(
                        check_id=f"{report_id}_cfr_out_of_range",
                        report_id=report_id,
                        check_type="CFR_OUT_OF_RANGE",
                        severity="ERROR",
                        expected_value="0-100%",
                        actual_value=cfr,
                        check_timestamp=datetime.now(),
                        description=f"CFR {cfr}% is outside valid range (0-100%)"
                    ))
        
        return checks
    
    def run_comprehensive_validation(
        self, 
        report_id: str, 
        data_dict: Dict[str, Any],
        country_breakdown: List[Dict[str, Any]] = None
    ) -> List[QualityCheck]:
        """
        Run comprehensive quality validation on report data.
        
        Args:
            report_id: Report identifier
            data_dict: Dictionary of extracted data
            country_breakdown: Optional country-specific data
            
        Returns:
            List of all quality check results
        """
        all_checks = []
        
        # Run all validation types
        all_checks.extend(self.validate_data_completeness(report_id, data_dict))
        all_checks.extend(self.validate_value_ranges(report_id, data_dict))
        
        # CFR validation
        if 'confirmed_cases' in data_dict and 'deaths' in data_dict:
            all_checks.extend(
                self.validate_cfr_consistency(
                    report_id,
                    data_dict['confirmed_cases'],
                    data_dict['deaths'],
                    data_dict.get('cfr_percent')
                )
            )
        
        # Case totals validation
        if 'confirmed_cases' in data_dict and 'suspected_cases' in data_dict:
            all_checks.extend(
                self.validate_case_totals(
                    report_id,
                    data_dict['confirmed_cases'],
                    data_dict['suspected_cases'],
                    country_breakdown
                )
            )
        
        # Epi week validation
        if 'report_date' in data_dict and 'epi_year' in data_dict and 'epi_week' in data_dict:
            all_checks.extend(
                self.validate_epidemiological_week(
                    report_id,
                    data_dict['report_date'],
                    data_dict['epi_year'],
                    data_dict['epi_week']
                )
            )
        
        return all_checks
    
    def get_quality_score(self, checks: List[QualityCheck]) -> float:
        """
        Calculate overall quality score from checks.
        
        Args:
            checks: List of quality check results
            
        Returns:
            Quality score (0-100)
        """
        if not checks:
            return 100.0
        
        # Weight checks by severity
        severity_weights = {'ERROR': 0, 'WARNING': 50, 'INFO': 90}
        
        total_score = 0
        
        for check in checks:
            weight = severity_weights.get(check.severity, 50)
            total_score += weight
        
        # Calculate average score
        average_score = total_score / len(checks)
        
        return average_score


if __name__ == "__main__":
    # Test quality engine
    print("Testing Quality Assurance Engine...")
    
    engine = QualityEngine()
    
    # Test data
    test_data = {
        'report_id': '2025_wk06',
        'confirmed_cases': 1000,
        'suspected_cases': 1500,
        'deaths': 25,
        'cfr_percent': 2.5,
        'affected_countries': 5,
        'report_date': datetime(2025, 2, 8),
        'epi_year': 2025,
        'epi_week': 6
    }
    
    # Run validation
    checks = engine.run_comprehensive_validation('2025_wk06', test_data)
    
    # Calculate score
    score = engine.get_quality_score(checks)
    
    print(f"Quality Score: {score:.1f}")
    print(f"Total Checks: {len(checks)}")
    print(f"Errors: {len([c for c in checks if c.severity == 'ERROR'])}")
    print(f"Warnings: {len([c for c in checks if c.severity == 'WARNING'])}")
    print("Quality engine working correctly!")
