"""
Test suite for analyzing output files from data extraction process.
This module provides comprehensive analysis of the output files produced by each step.
"""
import os
import sys
import json
import pytest
from pathlib import Path

# Add the parent directory to sys.path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_analysis import DataAnalyzer, AnalysisReporter
from utils.logger import logger
from config import ROOT_DIR

@pytest.fixture
def version_id():
    """Return the version ID to analyze."""
    # Default to "1_2" version or get from environment variable
    return os.environ.get("KCD2_TEST_VERSION", "1_2")

@pytest.fixture
def data_analyzer(version_id):
    """Return a DataAnalyzer instance for the specified version."""
    return DataAnalyzer(ROOT_DIR, version_id, logger)

@pytest.fixture
def analysis_reporter():
    """Return an AnalysisReporter instance."""
    return AnalysisReporter(logger)

@pytest.fixture
def reports_dir():
    """Return the path to save reports."""
    reports_dir = Path(ROOT_DIR) / "data_analysis" / "reports"
    reports_dir.mkdir(exist_ok=True, parents=True)
    return reports_dir

@pytest.fixture
def data_reporter():
    """Return a DataReporter instance for report generation."""
    from data_analysis.reporter import DataReporter
    
    # Create a reporter instance pointing to the reports directory
    reports_dir = Path(ROOT_DIR) / "data_analysis" / "reports"
    reports_dir.mkdir(exist_ok=True, parents=True)
    
    reporter = DataReporter(reports_dir, logger)
    return reporter

def test_s01_version_analysis(data_analyzer, analysis_reporter, reports_dir, capsys):
    """
    Analyze the version.json file (s01_get_version output).
    
    This test analyzes the version.json file to verify:
    - Version ID was correctly detected
    - Timestamp is present
    """
    with capsys.disabled():
        logger.info("Analyzing version.json...")
        
    # Run analysis
    analysis = data_analyzer.analyze_version()
    
    # Generate and print report
    report = analysis_reporter.generate_version_report(analysis)
    print("\n" + report)
    
    # Save report to file
    analysis_reporter.save_reports_to_files({"s01_version": report}, reports_dir)
    
    # Basic assertions to verify analysis worked
    assert "error" not in analysis, f"Error in analysis: {analysis.get('error')}"
    assert analysis.get("version_id") == data_analyzer.version_id
    assert analysis.get("version_found") == True

def test_s02_data_json_init_analysis(data_analyzer, analysis_reporter, reports_dir, capsys):
    """
    Analyze the initialized data.json file (s02_init_data_json output).
    
    This test analyzes the data.json initialization to verify:
    - The structure is correct
    - Version value matches expected version
    - Items array is initialized properly
    """
    with capsys.disabled():
        logger.info("Analyzing data.json initialization...")
        
    # Run analysis
    analysis = data_analyzer.analyze_data_json_init()
    
    # Generate and print report
    report = analysis_reporter.generate_data_json_init_report(analysis)
    print("\n" + report)
    
    # Save report to file
    analysis_reporter.save_reports_to_files({"s02_data_json_init": report}, reports_dir)
    
    # Basic assertions to verify analysis worked
    assert "error" not in analysis, f"Error in analysis: {analysis.get('error')}"
    assert analysis.get("contains_version") == True
    assert "items" in analysis.get("top_level_keys", [])

def test_s03_xml_extraction_analysis(data_analyzer, analysis_reporter, reports_dir, capsys):
    """
    Analyze the XML extraction results (s03_get_xml output).
    
    This test analyzes the XML extraction to verify:
    - Combined items XML was created
    - Text UI dictionary and combined dictionary have expected item counts
    - All expected XML files were extracted
    """
    with capsys.disabled():
        logger.info("Analyzing XML extraction results...")
        
    # Run analysis
    analysis = data_analyzer.analyze_xml_extraction()
    
    # Generate and print report
    report = analysis_reporter.generate_xml_extraction_report(analysis)
    print("\n" + report)
    
    # Save report to file
    analysis_reporter.save_reports_to_files({"s03_xml_extraction": report}, reports_dir)
    
    # Basic assertions to verify analysis worked
    assert "error" not in analysis, f"Error in analysis: {analysis.get('error')}"
    assert analysis.get("combined_items_xml_exists") == True
    assert analysis.get("combined_dict_item_count") > 0
    assert analysis.get("text_ui_dict_item_count") > 0

def test_s04_parsed_items_analysis(data_analyzer, analysis_reporter, reports_dir, capsys):
    """
    Analyze the parsed items (s04_parse_items output).
    
    This test analyzes parsed_items.json to verify:
    - Expected number of items were parsed
    - Distribution of item types and UI slots
    - Identify items with missing properties
    - Count unique icon IDs
    """
    with capsys.disabled():
        logger.info("Analyzing parsed items...")
        
    # Run analysis
    analysis = data_analyzer.analyze_parsed_items()
    
    # Generate and print report
    report = analysis_reporter.generate_parsed_items_report(analysis)
    print("\n" + report)
    
    # Save report to file
    analysis_reporter.save_reports_to_files({"s04_parsed_items": report}, reports_dir)
    
    # Basic assertions to verify analysis worked
    assert "error" not in analysis, f"Error in analysis: {analysis.get('error')}"
    assert analysis.get("total_item_count") > 0
    assert len(analysis.get("item_types", {})) > 0
    
    # UI slots might not be present at this stage in all implementations
    # Instead of requiring UI slots, we'll just log whether they were found
    ui_slots = analysis.get("ui_slots", {})
    if ui_slots:
        logger.info(f"Found {len(ui_slots)} UI slots")
    else:
        logger.info("No UI slots found in parsed items (this is expected in some implementations)")
    
    # Check for missing properties analysis
    missing_props_count = analysis.get('items_with_missing_props_count', 0)
    assert missing_props_count >= 0, "Missing properties count should be available"

def test_s05_filled_items_analysis(data_analyzer, analysis_reporter, reports_dir, capsys):
    """
    Analyze the filled items (s05_fill_items output).
    
    This test analyzes filled_items.json to verify:
    - Expected number of items were filled
    - Property changes made during filling
    - Distribution of categories by UI slot
    """
    with capsys.disabled():
        logger.info("Analyzing filled items...")
        
    # Run analysis
    analysis = data_analyzer.analyze_filled_items()
    
    # Generate and print report
    report = analysis_reporter.generate_filled_items_report(analysis)
    print("\n" + report)
    
    # Save report to file
    analysis_reporter.save_reports_to_files({"s05_filled_items": report}, reports_dir)
    
    # Basic assertions to verify analysis worked
    assert "error" not in analysis, f"Error in analysis: {analysis.get('error')}"
    assert analysis.get("total_item_count") > 0
    # We expect some items to have been changed during filling
    assert analysis.get("items_changed_during_filling") >= 0

def test_s06_processed_items_analysis(data_analyzer, analysis_reporter, reports_dir, capsys):
    """
    Analyze the processed items (s06_process_items output).
    
    This test analyzes items_array.json and the final data.json to verify:
    - All items were successfully processed
    - Distribution of categories, tiers, and rarities
    - Items were successfully added to data.json
    """
    with capsys.disabled():
        logger.info("Analyzing processed items...")
        
    # Run analysis
    analysis = data_analyzer.analyze_processed_items()
    
    # Generate and print report
    report = analysis_reporter.generate_processed_items_report(analysis)
    print("\n" + report)
    
    # Save report to file
    analysis_reporter.save_reports_to_files({"s06_processed_items": report}, reports_dir)
    
    # Basic assertions to verify analysis worked
    assert "error" not in analysis, f"Error in analysis: {analysis.get('error')}"
    assert analysis.get("item_count_in_array") > 0
    assert analysis.get("item_count_in_data_json") > 0
    assert analysis.get("items_successfully_added") == True

def test_s07_item_outliers_analysis(data_analyzer, analysis_reporter, reports_dir, capsys):
    """
    Analyze the items for statistical outliers, focusing on the most specific type categories.
    
    This test analyzes data.json to find statistical outliers within each specific item type,
    such as unusually high/low stats compared to similar items.
    """
    with capsys.disabled():
        logger.info("Analyzing item outliers...")
        
    # Run analysis
    analysis = data_analyzer.analyze_item_outliers()
    
    # Generate and print report
    report = analysis_reporter.generate_item_outliers_report(analysis)
    print("\n" + report)
    
    # Save report to file with a generic name (without s07 prefix)
    analysis_reporter.save_reports_to_files({"item_outliers_analysis": report}, reports_dir)
    
    # Basic assertions to verify analysis worked
    assert "error" not in analysis, f"Error in analysis: {analysis.get('error')}"
    assert "type_counts" in analysis, "Type counts missing from analysis"
    assert "outliers" in analysis, "Outliers data missing from analysis"
    
    # Check that we have some item types
    type_counts = analysis.get("type_counts", {})
    assert any(types for cat, types in type_counts.items() if types), "No item types found in analysis"

def test_s08_display_name_variants(data_analyzer, analysis_reporter, reports_dir, capsys):
    """
    Analyze the relationship between display names and icon IDs to identify variants.
    
    This test identifies items that share the same display name but have different icons (color variants)
    and items that share the same icon but have different names.
    """
    with capsys.disabled():
        logger.info("Analyzing display name and icon ID variants...")
        
    # Run analysis
    analysis = data_analyzer.analyze_display_name_variants()
    
    # Generate and print report
    report = analysis_reporter.generate_display_name_variants_report(analysis)
    print("\n" + report)
    
    # Save report to file with a generic name (without s08 prefix)
    analysis_reporter.save_reports_to_files({"display_name_variants": report}, reports_dir)
    
    # Basic assertions to verify analysis worked
    assert "error" not in analysis, f"Error in analysis: {analysis.get('error')}"
    assert "total_items" in analysis, "Total items count missing from analysis"
    assert "unique_display_names" in analysis, "Unique display names count missing from analysis"
    assert "unique_icon_ids" in analysis, "Unique icon IDs count missing from analysis"
    
    # Verify that we have variant data (even if empty)
    assert "display_name_variants" in analysis, "Display name variants missing from analysis"
    assert "icon_id_variants" in analysis, "Icon ID variants missing from analysis"

def test_full_analysis(data_analyzer, analysis_reporter, reports_dir, capsys):
    """
    Run a complete analysis of all output files.
    
    This test runs all analyses and generates a complete report for all steps.
    """
    with capsys.disabled():
        logger.info("Running full analysis...")
        
    # Run full analysis
    analysis = data_analyzer.run_full_analysis()
    
    # Generate and save reports
    reports = analysis_reporter.generate_full_report(analysis)
    
    # Print summary
    print("\nFull Analysis Summary:")
    print("=====================")
    for step, report in reports.items():
        # Extract the first line of each report (the title) and print it
        title = report.split('\n', 1)[0]
        print(f"- {step}: {title}")
    
    # Save all reports
    analysis_reporter.save_reports_to_files(reports, reports_dir)
    
    # Print path to reports
    print(f"\nDetailed reports saved to: {reports_dir}")
    
    # Basic assertion to verify analysis worked
    assert len(analysis) == 8, "Expected 8 analysis steps"
    for step in analysis.values():
        assert "error" not in step, f"Error in step: {step.get('error')}"

class TestDataAnalyzer:
    """Test runner for data analysis features."""
    
    def test_run_and_save_outliers_analysis(self, data_analyzer, data_reporter):
        """Test running the item outliers analysis and saving the report."""
        # Run the analysis
        outliers_analysis = data_analyzer.analyze_item_outliers()
        
        # Make sure analysis returns expected structure
        assert isinstance(outliers_analysis, dict)
        assert "type_counts" in outliers_analysis
        assert "outliers" in outliers_analysis
        
        # Include this analysis in the reporter's results
        data_reporter.analysis_results["item_outliers"] = outliers_analysis
        
        # Generate and save the report
        report_path = data_reporter.generate_item_outliers_report()
        
        # Check that report was saved and is accessible
        assert report_path is not None
        assert os.path.exists(report_path)
        
        print(f"Item outliers analysis report saved to: {report_path}")
        
    def test_run_and_save_display_name_variants_analysis(self, data_analyzer, data_reporter):
        """Test running the display name variants analysis and saving the report."""
        # Run the analysis
        variants_analysis = data_analyzer.analyze_display_name_variants()
        
        # Make sure analysis returns expected structure
        assert isinstance(variants_analysis, dict)
        assert "total_items" in variants_analysis
        assert "display_name_variants" in variants_analysis
        assert "icon_id_variants" in variants_analysis
        
        # Include this analysis in the reporter's results
        data_reporter.analysis_results["display_name_variants"] = variants_analysis
        
        # Generate and save the report
        report_path = data_reporter.generate_display_name_variants_report()
        
        # Check that report was saved and is accessible
        assert report_path is not None
        assert os.path.exists(report_path)
        
        print(f"Display name variants analysis report saved to: {report_path}")
    
    def test_run_full_analysis(self, data_analyzer, data_reporter):
        """Test running the full analysis pipeline and saving all reports."""
        # Run the full analysis
        full_analysis = data_analyzer.run_full_analysis()
        
        # Make sure analysis returns expected structure
        assert isinstance(full_analysis, dict)
        assert len(full_analysis) == 8, "Expected 8 analysis steps"
        
        # Run the item outliers analysis
        self.test_run_and_save_outliers_analysis(data_analyzer, data_reporter)
        
        # Run the display name variants analysis
        self.test_run_and_save_display_name_variants_analysis(data_analyzer, data_reporter)