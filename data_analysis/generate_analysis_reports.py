#!/usr/bin/env python
"""
Generate the item outliers and display name variants reports
with the new naming convention.
"""
import sys
import os
from pathlib import Path

# Add parent directory to path so we can import our modules
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from data_analysis.analyzer import DataAnalyzer
from data_analysis.reporter import DataReporter, AnalysisReporter
from utils.logger import logger

def main():
    """Generate reports with the new naming convention."""
    # Get the project root directory
    root_dir = Path(__file__).parent.parent
    
    # Create an analyzer instance
    analyzer = DataAnalyzer(root_dir=str(root_dir), version_id="1_2", logger=logger)
    
    # Create the reports directory if it doesn't exist
    reports_dir = root_dir / "data_analysis" / "reports"
    reports_dir.mkdir(exist_ok=True, parents=True)
    
    # Create a reporter instance
    reporter = DataReporter(reports_dir=reports_dir, logger=logger)
    
    # Run the analyses
    print("Analyzing processed items...")
    processed_items = analyzer.analyze_processed_items()
    
    print("Analyzing item outliers...")
    item_outliers = analyzer.analyze_item_outliers()
    
    print("Analyzing display name variants...")
    display_name_variants = analyzer.analyze_display_name_variants()
    
    # Set the analysis results in the reporter
    reporter.analysis_results = {
        "processed_items": processed_items,
        "item_outliers": item_outliers,
        "display_name_variants": display_name_variants
    }
    
    # Generate the reports
    print("Generating reports...")
    analysis_reporter = AnalysisReporter(logger=logger)
    processed_items_report = analysis_reporter.generate_processed_items_report(processed_items)
    analysis_reporter.save_reports_to_files({"s06_processed_items": processed_items_report}, reports_dir)
    
    item_outliers_path = reporter.generate_item_outliers_report()
    display_name_variants_path = reporter.generate_display_name_variants_report()
    
    print(f"Generated processed items report: {reports_dir / 's06_processed_items_report.txt'}")
    print(f"Generated item outliers report: {item_outliers_path}")
    print(f"Generated display name variants report: {display_name_variants_path}")

if __name__ == "__main__":
    main()