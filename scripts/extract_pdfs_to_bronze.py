#!/usr/bin/env python3
"""
Quick script to extract PDFs and save to Bronze layer.
Run this if Notebook 01 has issues.
"""

import sys
from pathlib import Path
import pandas as pd
import pdfplumber
import re
from datetime import datetime
import logging

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Paths
PDF_PATH = project_root / "data" / "sample"
BRONZE_PATH = project_root / "data" / "bronze_tables"
BRONZE_PATH.mkdir(parents=True, exist_ok=True)

def extract_kpi_panel(pdf_path: str) -> dict:
    """Extract KPI data from PDF."""
    kpi_data = {
        'confirmed_cases': None,
        'suspected_cases': None,
        'deaths': None,
        'cfr_percent': None,
        'affected_countries': None
    }
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            first_page = pdf.pages[0]
            text = first_page.extract_text()
            
            if not text:
                return kpi_data
            
            lines = text.split('\n')
            for i, line in enumerate(lines):
                if 'Confirmed Cases' in line and 'Suspected Cases' in line:
                    if i + 1 < len(lines):
                        numbers_line = lines[i + 1].strip()
                        numbers = numbers_line.split()
                        if len(numbers) >= 4:
                            try:
                                kpi_data['confirmed_cases'] = int(numbers[0].replace(',', ''))
                                kpi_data['suspected_cases'] = int(numbers[1].replace(',', ''))
                                kpi_data['deaths'] = int(numbers[2].replace(',', ''))
                                kpi_data['cfr_percent'] = float(numbers[3].replace(',', ''))
                            except (ValueError, IndexError) as e:
                                logger.warning(f"Error parsing KPI numbers: {e}")
            
            for i, line in enumerate(lines):
                if 'Affected Countries' in line:
                    if i + 1 < len(lines):
                        numbers_line = lines[i + 1].strip()
                        numbers = numbers_line.split()
                        if len(numbers) >= 1:
                            try:
                                kpi_data['affected_countries'] = int(numbers[0])
                            except ValueError:
                                pass
                    break
                    
    except Exception as e:
        logger.error(f"Error extracting KPI from {pdf_path}: {e}")
    
    return kpi_data

def extract_country_breakdown(pdf_path: str) -> list:
    """Extract country-level data from PDF."""
    country_data = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"
            
            if "Country-Level Summary:" in full_text:
                country_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*?):\s+(?:Reported\s+)?(\d+)\s+(?:cumulative\s+)?cases?\s+(?:with\s+)?(?:and\s+)?(\d+)\s+deaths?'
                matches = re.finditer(country_pattern, full_text)
                
                for match in matches:
                    country_name = match.group(1).strip()
                    cases = int(match.group(2))
                    deaths = int(match.group(3))
                    
                    country_data.append({
                        'country_name': country_name,
                        'confirmed_cases': cases,
                        'suspected_cases': None,
                        'deaths': deaths
                    })
                    
    except Exception as e:
        logger.warning(f"Error extracting countries from {pdf_path}: {e}")
    
    return country_data

def main():
    """Main extraction function."""
    print("🔄 Starting PDF extraction...\n")
    
    # Find PDFs
    pdf_files = list(PDF_PATH.glob('*.pdf'))
    print(f"📄 Found {len(pdf_files)} PDF files\n")
    
    report_summaries = []
    country_breakdowns = []
    extraction_logs = []
    
    for pdf_path in pdf_files:
        try:
            logger.info(f"Processing: {pdf_path.name}")
            
            # Extract report ID
            filename = pdf_path.stem
            match = re.search(r'(\d{4})_wk(\d{2})', filename)
            
            if match:
                year = int(match.group(1))
                week = int(match.group(2))
                report_id = f"{year}_wk{week:02d}"
            else:
                report_id = filename
                year = None
                week = None
            
            # Extract data
            kpi_data = extract_kpi_panel(str(pdf_path))
            countries = extract_country_breakdown(str(pdf_path))
            
            # Create report summary
            report_summary = {
                'report_id': report_id,
                'epi_year': year,
                'epi_week': week,
                'report_date': None,
                'confirmed_cases': kpi_data.get('confirmed_cases'),
                'suspected_cases': kpi_data.get('suspected_cases'),
                'deaths': kpi_data.get('deaths'),
                'cfr_percent': kpi_data.get('cfr_percent'),
                'affected_countries': kpi_data.get('affected_countries'),
                'source_file': pdf_path.name,
                'extraction_timestamp': datetime.now().isoformat(),
                'country_breakdown_count': len(countries)
            }
            
            report_summaries.append(report_summary)
            
            # Add report_id to country records
            for country in countries:
                country['report_id'] = report_id
                country['epi_year'] = year
                country['epi_week'] = week
                country['extraction_timestamp'] = datetime.now().isoformat()
            
            country_breakdowns.extend(countries)
            
            # Log extraction
            extraction_logs.append({
                'report_id': report_id,
                'file_name': pdf_path.name,
                'file_size_bytes': pdf_path.stat().st_size,
                'page_count': len(pdfplumber.open(str(pdf_path)).pages),
                'extraction_timestamp': datetime.now().isoformat(),
                'kpi_extracted': kpi_data.get('confirmed_cases') is not None,
                'countries_extracted': len(countries),
                'status': 'SUCCESS'
            })
            
            print(f"✅ {report_id}: {kpi_data.get('confirmed_cases', 0):,} cases, {len(countries)} countries")
            
        except Exception as e:
            logger.error(f"Failed to process {pdf_path.name}: {e}")
            extraction_logs.append({
                'report_id': pdf_path.stem,
                'file_name': pdf_path.name,
                'extraction_timestamp': datetime.now().isoformat(),
                'status': 'FAILED',
                'error_message': str(e)
            })
    
    # Create DataFrames
    df_report_summary = pd.DataFrame(report_summaries)
    df_country_weekly = pd.DataFrame(country_breakdowns)
    df_extraction_metadata = pd.DataFrame(extraction_logs)
    
    print(f"\n✅ Extraction complete: {len(report_summaries)} reports, {len(country_breakdowns)} country records\n")
    
    # Save to Parquet
    print("💾 Saving to Bronze layer...\n")
    
    df_report_summary.to_parquet(
        BRONZE_PATH / "report_summary.parquet",
        index=False,
        engine='pyarrow'
    )
    
    df_country_weekly.to_parquet(
        BRONZE_PATH / "country_weekly.parquet",
        index=False,
        engine='pyarrow'
    )
    
    df_extraction_metadata.to_parquet(
        BRONZE_PATH / "extraction_metadata.parquet",
        index=False,
        engine='pyarrow'
    )
    
    print(f"✅ Parquet files saved to: {BRONZE_PATH}")
    print(f"   - report_summary.parquet ({len(df_report_summary)} rows)")
    print(f"   - country_weekly.parquet ({len(df_country_weekly)} rows)")
    print(f"   - extraction_metadata.parquet ({len(df_extraction_metadata)} rows)")
    
    print("\n✅ Bronze layer extraction complete!")

if __name__ == "__main__":
    main()
