"""Generate synthetic cholera situation report PDFs for testing."""
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime
import random


def generate_sample_cholera_pdf(output_path: str, epi_week: int, year: int):
    """Generate sample cholera SitRep PDF."""
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title = Paragraph(
        f"<b>Cholera Situation Report - Epidemiological Week {epi_week}, {year}</b>", 
        styles['Title']
    )
    story.append(title)
    story.append(Spacer(1, 0.3*inch))
    
    # KPI Panel
    cases = random.randint(800, 2000)
    deaths = int(cases * random.uniform(0.015, 0.03))
    cfr = round((deaths / cases) * 100, 2)
    countries = random.randint(4, 9)
    
    kpi_data = [
        ['Confirmed Cases', 'Suspected Cases', 'Deaths', 'CFR (%)'],
        [str(cases), str(int(cases * 1.4)), str(deaths), str(cfr)],
        ['Affected Countries', 'First Reported', 'Report Date', 'Risk Assessment'],
        [str(countries), '2024-11-15', datetime.now().strftime('%Y-%m-%d'), 'MODERATE']
    ]
    
    kpi_table = Table(kpi_data, colWidths=[2*inch]*4)
    kpi_table.setStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    story.append(kpi_table)
    story.append(Spacer(1, 0.4*inch))
    
    # Update to Event narrative
    narrative_text = f"""
    <b>Update to Event:</b> As of {datetime.now().strftime('%d %B %Y')}, 
    a cumulative total of {cases} confirmed cholera cases and {deaths} deaths 
    (Case Fatality Rate: {cfr}%) have been reported from {countries} countries 
    in the African region. The outbreak continues to spread with varying intensity 
    across affected Member States.
    """
    story.append(Paragraph(narrative_text, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Epi-week update
    new_cases_week = random.randint(80, 250)
    new_deaths_week = random.randint(2, 8)
    epi_text = f"""
    <b>Epidemiological Week {epi_week} Update:</b> During epidemiological week {epi_week}, 
    a total of {new_cases_week} new confirmed cases and {new_deaths_week} new deaths 
    were reported across the region, representing a {random.randint(-15, 25)}% change 
    compared to the previous week.
    """
    story.append(Paragraph(epi_text, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Country breakdown
    country_text = f"""
    <b>Country-Level Summary:</b><br/>
    <b>Zimbabwe:</b> Reported {random.randint(300, 600)} cumulative cases with 
    {random.randint(5, 15)} deaths. Active transmission in 4 provinces.<br/>
    <b>Zambia:</b> {random.randint(200, 400)} cases and {random.randint(3, 10)} deaths. 
    Outbreak concentrated in urban areas.<br/>
    <b>Mozambique:</b> {random.randint(150, 350)} cases reported. Enhanced surveillance 
    systems detecting cases early.
    """
    story.append(Paragraph(country_text, styles['Normal']))
    
    doc.build(story)
    print(f"✅ Generated: {output_path}")


if __name__ == "__main__":
    import os
    os.makedirs("data/sample", exist_ok=True)
    
    for week in [6, 7, 8]:
        output_file = f"data/sample/cholera_sitrep_2025_wk{week:02d}.pdf"
        generate_sample_cholera_pdf(output_file, week, 2025)
    
    print("\n✅ All sample PDFs generated successfully!")