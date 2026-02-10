"""Configuration management for Cholera CDR MVP."""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SAMPLE_DATA_DIR = DATA_DIR / "sample"
REFERENCE_DATA_DIR = DATA_DIR / "reference"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
LOGS_DIR = PROJECT_ROOT / "logs"

# Create logs directory if it doesn't exist
LOGS_DIR.mkdir(exist_ok=True)

# Fabric configuration
FABRIC_WORKSPACE_ID: str = os.getenv("FABRIC_WORKSPACE_ID", "")
FABRIC_LAKEHOUSE_ID: str = os.getenv("FABRIC_LAKEHOUSE_ID", "")
FABRIC_WAREHOUSE_ID: str = os.getenv("FABRIC_WAREHOUSE_ID", "")
ONELAKE_ENDPOINT: str = os.getenv("ONELAKE_ENDPOINT", "")

# Data layer paths
BRONZE_PATH: str = os.getenv("BRONZE_PATH", "Files/bronze/pdfs")
SILVER_SCHEMA: str = os.getenv("SILVER_SCHEMA", "silver")
GOLD_SCHEMA: str = os.getenv("GOLD_SCHEMA", "gold")

# Quality thresholds
MIN_EXTRACTION_CONFIDENCE: float = float(os.getenv("MIN_EXTRACTION_CONFIDENCE", "0.90"))
CFR_TOLERANCE_PERCENT: float = float(os.getenv("CFR_TOLERANCE_PERCENT", "0.5"))

# ML model parameters
PROPHET_FORECAST_WEEKS: int = int(os.getenv("PROPHET_FORECAST_WEEKS", "4"))
PROPHET_CHANGEPOINT_PRIOR: float = float(os.getenv("PROPHET_CHANGEPOINT_PRIOR", "0.05"))

# Logging
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE: Path = LOGS_DIR / os.getenv("LOG_FILE", "cdr_pipeline.log")

# Email notifications
SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.office365.com")
SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
NOTIFICATION_EMAIL: str = os.getenv("NOTIFICATION_EMAIL", "")


def validate_config() -> bool:
    \"\"\"Validate that required configuration is present.\"\"\"
    required_fabric_vars = [
        FABRIC_WORKSPACE_ID,
        FABRIC_LAKEHOUSE_ID,
    ]
    
    if not all(required_fabric_vars):
        print(" Warning: Fabric configuration incomplete. Set environment variables.")
        return False
    
    return True


if __name__ == "__main__":
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Data Directory: {DATA_DIR}")
    print(f"Configuration Valid: {validate_config()}")
