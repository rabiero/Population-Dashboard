#!/usr/bin/env python3
"""
WorldPop Data Pipeline - Main Execution Script
"""

import logging
from pathlib import Path
import argparse
import time

from data_pipeline.config import OUTPUT_DIR
from data_pipeline.load_rasters import RasterLoader
from data_pipeline.extract_metadata import create_metadata_summary, export_metadata_to_csv
from data_pipeline.summarize_by_district import DistrictSummarizer
from data_pipeline.utils import setup_logging, save_json, save_dataframe

def run_pipeline(countries=None, age_groups=None, sex_options=None, use_cache=True):
    """
    Run the complete data pipeline
    
    Args:
        countries: List of country codes to process
        age_groups: List of age groups to process
        sex_options: List of sex options to process
        use_cache: Whether to use cached files
    
    Returns:
        dict: Pipeline results
    """
    start_time = time.time()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting WorldPop data pipeline")
    
    # Initialize components
    raster_loader = RasterLoader()
    district_summarizer = DistrictSummarizer()
    
    # Step 1: Load raster data
    logger.info("Step 1: Loading raster data")
    raster_data = raster_loader.batch_load_rasters(
        countries=countries,
        age_groups=age_groups,
        sex_options=sex_options
    )
    
    # Step 2: Extract and save metadata
    logger.info("Step 2: Extracting metadata")
    metadata_summary = create_metadata_summary(raster_data)
    save_json(metadata_summary, OUTPUT_DIR / "metadata_summary.json")
    
    export_metadata_to_csv(
        raster_data, 
        OUTPUT_DIR / "raster_metadata.csv"
    )
    
    # Step 3: Summarize by districts
    logger.info("Step 3: Summarizing by districts")
    district_summaries = district_summarizer.batch_summarize_rasters(raster_data)
    
    # Step 4: Create combined summary
    logger.info("Step 4: Creating combined summary")
    combined_summary = district_summarizer.create_combined_summary(district_summaries)
    save_dataframe(combined_summary, OUTPUT_DIR / "combined_population_summary.csv")
    
    # Step 5: Calculate demographic indicators
    logger.info("Step 5: Calculating demographic indicators")
    demographic_indicators = district_summarizer.calculate_demographic_indicators(combined_summary)
    save_dataframe(demographic_indicators, OUTPUT_DIR / "demographic_indicators.csv")
    
    # Save final results
    results = {
        'raster_data': {k: v for k, v in raster_data.items() if any(v.values())},
        'district_summaries': district_summaries,
        'combined_summary': combined_summary.to_dict('records'),
        'demographic_indicators': demographic_indicators.to_dict('records'),
        'metadata_summary': metadata_summary,
        'execution_time': time.time() - start_time
    }
    
    save_json(results, OUTPUT_DIR / "pipeline_results.json")
    
    logger.info(f"Pipeline completed in {time.time() - start_time:.2f} seconds")
    logger.info(f"Results saved to {OUTPUT_DIR}")
    
    return results

def main():
    """Command line interface for the pipeline"""
    parser = argparse.ArgumentParser(description='WorldPop Data Pipeline')
    parser.add_argument('--countries', nargs='+', default=['KEN', 'UGA'],
                       help='Countries to process (default: KEN UGA)')
    parser.add_argument('--age-groups', nargs='+', 
                       help='Age groups to process (default: all)')
    parser.add_argument('--sex-options', nargs='+', default=['M', 'F'],
                       help='Sex options to process (default: M F)')
    parser.add_argument('--no-cache', action='store_true',
                       help='Disable cache')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level=log_level)
    
    try:
        results = run_pipeline(
            countries=args.countries,
            age_groups=args.age_groups,
            sex_options=args.sex_options,
            use_cache=not args.no_cache
        )
        
        # Print summary
        print("\nPipeline Summary:")
        print(f"Countries processed: {results['metadata_summary']['countries']}")
        print(f"Total rasters loaded: {results['metadata_summary']['total_rasters']}")
        print(f"Failed rasters: {len(results['metadata_summary']['failed_rasters'])}")
        print(f"Execution time: {results['execution_time']:.2f} seconds")
        
    except Exception as e:
        logging.error(f"Pipeline failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()