import logging
import sys
from pathlib import Path
import json
import pandas as pd
from datetime import datetime

def setup_logging(level=logging.INFO):
    """Setup logging configuration"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('pipeline.log')
        ]
    )

def save_json(data, file_path):
    """Save data to JSON file"""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def load_json(file_path):
    """Load data from JSON file"""
    with open(file_path, 'r') as f:
        return json.load(f)

def save_dataframe(df, file_path, format='csv'):
    """Save DataFrame to file"""
    if format == 'csv':
        df.to_csv(file_path, index=False)
    elif format == 'parquet':
        df.to_parquet(file_path, index=False)
    elif format == 'json':
        df.to_json(file_path, orient='records', indent=2)
    else:
        raise ValueError(f"Unsupported format: {format}")

def create_output_filename(base_name, extension, timestamp=True):
    """Create output filename with optional timestamp"""
    if timestamp:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{base_name}_{timestamp_str}.{extension}"
    else:
        return f"{base_name}.{extension}"

def validate_country_code(country_code):
    """Validate country code"""
    valid_codes = ['KEN', 'UGA']
    return country_code.upper() in valid_codes

def validate_age_group(age_group):
    """Validate age group format"""
    # Basic validation - can be enhanced
    return isinstance(age_group, str) and len(age_group) > 0

def format_age_group_display(age_group):
    """Format age group for display"""
    if age_group == '80_plus':
        return '80+'
    else:
        return age_group.replace('_', '-')

def calculate_percentage(numerator, denominator):
    """Calculate percentage safely"""
    if denominator == 0:
        return 0.0
    return (numerator / denominator) * 100

def memory_usage_mb():
    """Get current memory usage in MB"""
    import psutil
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024

def check_disk_space(path, required_gb=1):
    """Check if sufficient disk space is available"""
    import shutil
    total, used, free = shutil.disk_usage(path)
    free_gb = free // (2**30)
    return free_gb >= required_gb

# Import the cache functions for backward compatibility
from .cache_utils import download_file, get_cached_file