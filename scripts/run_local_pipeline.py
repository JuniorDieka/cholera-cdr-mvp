#!/usr/bin/env python3
"""
Local Pipeline Orchestrator - Simulates Fabric Data Pipeline
Executes all notebooks in sequence for end-to-end testing.

Usage:
    python scripts/run_local_pipeline.py
    python scripts/run_local_pipeline.py --notebooks 01 02 03  # Run specific notebooks
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime
import argparse
import json

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

# Notebook execution order
NOTEBOOKS = [
    {
        "id": "01",
        "name": "01_pdf_extraction.ipynb",
        "description": "PDF Extraction - Bronze Layer",
        "estimated_time": "2-3 minutes"
    },
    {
        "id": "02",
        "name": "02_silver_transformation.ipynb",
        "description": "Silver Transformation - Data Cleansing",
        "estimated_time": "1-2 minutes"
    },
    {
        "id": "03",
        "name": "03_gold_dimensional_model.ipynb",
        "description": "Gold Dimensional Model - Star Schema",
        "estimated_time": "1-2 minutes"
    },
    {
        "id": "04",
        "name": "04_epi_analytics.ipynb",
        "description": "Epidemiological Analytics",
        "estimated_time": "1-2 minutes"
    },
    {
        "id": "05",
        "name": "05_ml_forecasting.ipynb",
        "description": "ML Forecasting - Prophet",
        "estimated_time": "2-3 minutes"
    }
]


def print_banner(text: str, char: str = "="):
    """Print a formatted banner."""
    width = 80
    print("\n" + char * width)
    print(f"{text:^{width}}")
    print(char * width + "\n")


def run_notebook(notebook_path: Path) -> dict:
    """
    Execute a Jupyter notebook and return results.
    
    Args:
        notebook_path: Path to notebook file
        
    Returns:
        Dictionary with execution results
    """
    result = {
        "notebook": notebook_path.name,
        "status": "PENDING",
        "start_time": None,
        "end_time": None,
        "duration_seconds": None,
        "error": None
    }
    
    try:
        result["start_time"] = datetime.now()
        
        print(f"📓 Executing: {notebook_path.name}")
        print(f"   Path: {notebook_path}")
        
        # Execute notebook using nbconvert
        cmd = [
            "jupyter", "nbconvert",
            "--to", "notebook",
            "--execute",
            str(notebook_path),
            "--output", str(notebook_path),
            "--ExecutePreprocessor.timeout=600"  # 10 minute timeout
        ]
        
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )
        
        result["end_time"] = datetime.now()
        result["duration_seconds"] = (result["end_time"] - result["start_time"]).total_seconds()
        
        if process.returncode == 0:
            result["status"] = "SUCCESS"
            print(f"   ✅ Completed in {result['duration_seconds']:.1f}s\n")
        else:
            result["status"] = "FAILED"
            result["error"] = process.stderr
            print(f"   ❌ Failed after {result['duration_seconds']:.1f}s")
            print(f"   Error: {process.stderr[:200]}...\n")
            
    except Exception as e:
        result["status"] = "ERROR"
        result["error"] = str(e)
        result["end_time"] = datetime.now()
        if result["start_time"]:
            result["duration_seconds"] = (result["end_time"] - result["start_time"]).total_seconds()
        print(f"   ❌ Exception: {e}\n")
    
    return result


def generate_report(results: list, output_file: Path = None):
    """
    Generate execution report.
    
    Args:
        results: List of execution results
        output_file: Optional path to save report
    """
    print_banner("PIPELINE EXECUTION REPORT", "=")
    
    total_duration = sum(r["duration_seconds"] for r in results if r["duration_seconds"])
    success_count = sum(1 for r in results if r["status"] == "SUCCESS")
    failed_count = sum(1 for r in results if r["status"] == "FAILED")
    error_count = sum(1 for r in results if r["status"] == "ERROR")
    
    print(f"📊 Summary:")
    print(f"   Total Notebooks: {len(results)}")
    print(f"   ✅ Successful: {success_count}")
    print(f"   ❌ Failed: {failed_count}")
    print(f"   ⚠️  Errors: {error_count}")
    print(f"   ⏱️  Total Duration: {total_duration:.1f}s ({total_duration/60:.1f} minutes)")
    
    print(f"\n📋 Detailed Results:")
    for i, result in enumerate(results, 1):
        status_icon = "✅" if result["status"] == "SUCCESS" else "❌"
        duration = f"{result['duration_seconds']:.1f}s" if result["duration_seconds"] else "N/A"
        print(f"   {i}. {status_icon} {result['notebook']} - {result['status']} ({duration})")
        if result["error"]:
            print(f"      Error: {result['error'][:100]}...")
    
    # Save report to file if requested
    if output_file:
        report_data = {
            "execution_date": datetime.now().isoformat(),
            "total_notebooks": len(results),
            "successful": success_count,
            "failed": failed_count,
            "errors": error_count,
            "total_duration_seconds": total_duration,
            "results": results
        }
        
        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"\n📄 Report saved to: {output_file}")
    
    print("\n" + "=" * 80 + "\n")
    
    return success_count == len(results)


def main():
    """Main pipeline orchestrator."""
    parser = argparse.ArgumentParser(description="Run Cholera CDR data pipeline locally")
    parser.add_argument(
        "--notebooks",
        nargs="+",
        help="Specific notebook IDs to run (e.g., 01 02 03)",
        default=None
    )
    parser.add_argument(
        "--report",
        type=str,
        help="Path to save execution report (JSON)",
        default=None
    )
    
    args = parser.parse_args()
    
    print_banner("CHOLERA CDR MVP - LOCAL PIPELINE EXECUTION", "=")
    print(f"🚀 Starting pipeline execution at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Project Root: {PROJECT_ROOT}")
    print(f"📓 Notebooks Directory: {NOTEBOOKS_DIR}\n")
    
    # Determine which notebooks to run
    if args.notebooks:
        notebooks_to_run = [nb for nb in NOTEBOOKS if nb["id"] in args.notebooks]
        print(f"🎯 Running selected notebooks: {', '.join(args.notebooks)}\n")
    else:
        notebooks_to_run = NOTEBOOKS
        print(f"🎯 Running all {len(NOTEBOOKS)} notebooks\n")
    
    if not notebooks_to_run:
        print("❌ No notebooks found to execute!")
        sys.exit(1)
    
    # Display execution plan
    print("📋 Execution Plan:")
    for i, nb in enumerate(notebooks_to_run, 1):
        print(f"   {i}. {nb['name']} - {nb['description']}")
        print(f"      Estimated time: {nb['estimated_time']}")
    print()
    
    # Execute notebooks
    results = []
    
    for i, notebook in enumerate(notebooks_to_run, 1):
        print_banner(f"STEP {i}/{len(notebooks_to_run)}: {notebook['description']}", "-")
        
        notebook_path = NOTEBOOKS_DIR / notebook["name"]
        
        if not notebook_path.exists():
            print(f"❌ Notebook not found: {notebook_path}")
            results.append({
                "notebook": notebook["name"],
                "status": "NOT_FOUND",
                "error": f"File not found: {notebook_path}"
            })
            continue
        
        result = run_notebook(notebook_path)
        results.append(result)
        
        # Stop on failure unless --continue flag is set
        if result["status"] != "SUCCESS":
            print(f"\n⚠️  Notebook {notebook['name']} failed. Stopping pipeline.")
            break
    
    # Generate report
    report_path = Path(args.report) if args.report else PROJECT_ROOT / "pipeline_report.json"
    all_success = generate_report(results, report_path)
    
    # Exit with appropriate code
    if all_success:
        print("✅ Pipeline completed successfully!")
        sys.exit(0)
    else:
        print("❌ Pipeline completed with errors!")
        sys.exit(1)


if __name__ == "__main__":
    main()
