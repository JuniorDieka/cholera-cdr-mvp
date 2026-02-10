"""PDF extraction module for cholera situation reports."""
import re
from pathlib import Path
from typing import Dict, Any, Optional
import pdfplumber


def extract_kpi_panel(pdf_path: str) -> Dict[str, Any]:
    """
    Extract KPI panel data from PDF first page.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Dictionary with extracted KPI metrics
    """
    kpi_data = {}
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[0]
            text = page.extract_text()
            
            # Extract confirmed cases
            confirmed_match = re.search(
                r'Confirmed Cases[:\s]+(\d+(?:,\d{3})*)', 
                text, 
                re.IGNORECASE
            )
            if confirmed_match:
                kpi_data['confirmed_cases'] = int(
                    confirmed_match.group(1).replace(',', '')
                )
            
            # Extract suspected cases
            suspected_match = re.search(
                r'Suspected Cases[:\s]+(\d+(?:,\d{3})*)', 
                text, 
                re.IGNORECASE
            )
            if suspected_match:
                kpi_data['suspected_cases'] = int(
                    suspected_match.group(1).replace(',', '')
                )
            
            # Extract deaths
            deaths_match = re.search(
                r'Deaths[:\s]+(\d+(?:,\d{3})*)', 
                text, 
                re.IGNORECASE
            )
            if deaths_match:
                kpi_data['deaths'] = int(
                    deaths_match.group(1).replace(',', '')
                )
            
            # Extract CFR
            cfr_match = re.search(
                r'CFR[:\s\(]+(\d+\.?\d*)%?\)', 
                text, 
                re.IGNORECASE
            )
            if cfr_match:
                kpi_data['cfr_percent'] = float(cfr_match.group(1))
            
            # Extract affected countries
            countries_match = re.search(
                r'Affected Countries[:\s]+(\d+)', 
                text, 
                re.IGNORECASE
            )
            if countries_match:
                kpi_data['affected_countries'] = int(countries_match.group(1))
                
    except Exception as e:
        print(f" Error extracting KPI panel: {e}")
        
    return kpi_data


def extract_narrative(pdf_path: str) -> Dict[str, str]:
    """
    Extract narrative sections from PDF.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Dictionary with narrative texts
    """
    narratives = {}
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            for page in pdf.pages:
                full_text += page.extract_text() + "\n"
            
            # Extract "Update to Event"
            update_match = re.search(
                r'Update to Event:(.*?)(?=Epidemiological Week|\Z)', 
                full_text, 
                re.DOTALL | re.IGNORECASE
            )
            if update_match:
                narratives['update_to_event'] = update_match.group(1).strip()
            
            # Extract Epi Week summary
            epi_week_match = re.search(
                r'Epidemiological Week \d+ Update:(.*?)(?=Country|\Z)', 
                full_text, 
                re.DOTALL | re.IGNORECASE
            )
            if epi_week_match:
                narratives['epi_week_summary'] = epi_week_match.group(1).strip()
                
    except Exception as e:
        print(f" Error extracting narratives: {e}")
        
    return narratives


if __name__ == "__main__":
    # Test extraction with sample data
    sample_pdf = Path("data/sample/cholera_sitrep_2025_wk06.pdf")
    if sample_pdf.exists():
        print("Testing PDF extraction...")
        kpi = extract_kpi_panel(str(sample_pdf))
        print(f"Extracted KPI: {kpi}")
    else:
        print(" Sample PDF not found. Run generate_sample_data.py first.")
