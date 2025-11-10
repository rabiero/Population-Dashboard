import re
from pathlib import Path
import logging
from .config import COUNTRIES, AGE_GROUPS, SEX_OPTIONS

logger = logging.getLogger(__name__)

def parse_filename(filename):
    """
    Parse WorldPop filename to extract metadata
    
    Args:
        filename: Filename like 'M_0_4.tif' or full URL
        
    Returns:
        dict: Parsed metadata or None if invalid
    """
    # Extract just the filename from path/URL
    basename = Path(filename).name
    
    # Pattern for WorldPop age/sex files
    pattern = r'^([MF])_(\d+)_(\d+|[a-z_]+)\.tif$'
    match = re.match(pattern, basename)
    
    if not match:
        logger.warning(f"Invalid filename format: {basename}")
        return None
    
    sex = match.group(1)
    age_start = match.group(2)
    age_end = match.group(3)
    
    # Handle different age group formats
    if age_end == 'plus':
        age_group = f"{age_start}+"
    else:
        age_group = f"{age_start}_{age_end}"
    
    return {
        'sex': sex,
        'age_start': int(age_start),
        'age_end': age_end,
        'age_group': age_group,
        'filename': basename
    }

def extract_country_from_url(url):
    """
    Extract country code from WorldPop URL
    
    Args:
        url: WorldPop data URL
        
    Returns:
        str: Country code or None
    """
    country_pattern = r'/(KEN|UGA)/'
    match = re.search(country_pattern, url.upper())
    
    if match:
        return match.group(1)
    else:
        logger.warning(f"Could not extract country from URL: {url}")
        return None

def validate_metadata(metadata):
    """
    Validate extracted metadata
    
    Args:
        metadata: Metadata dictionary
        
    Returns:
        bool: True if valid
    """
    if not metadata:
        return False
        
    required_fields = ['sex', 'age_group', 'age_start']
    for field in required_fields:
        if field not in metadata:
            return False
    
    if metadata['sex'] not in SEX_OPTIONS:
        return False
        
    # Validate age group format
    age_group = metadata['age_group']
    if age_group not in AGE_GROUPS and not any(ag in age_group for ag in AGE_GROUPS):
        logger.warning(f"Unrecognized age group: {age_group}")
        return False
    
    return True

def create_metadata_summary(raster_data):
    """
    Create summary of raster metadata
    
    Args:
        raster_data: Dictionary from batch_load_rasters
        
    Returns:
        dict: Summary statistics
    """
    summary = {
        'total_rasters': 0,
        'countries': set(),
        'age_groups': set(),
        'failed_rasters': [],
        'spatial_info': {}
    }
    
    for country, country_data in raster_data.items():
        summary['countries'].add(country)
        
        for sex, sex_data in country_data.items():
            for age_group, raster_info in sex_data.items():
                if raster_info.get('data') is not None:
                    summary['total_rasters'] += 1
                    summary['age_groups'].add(age_group)
                    
                    # Store spatial info from first successful raster
                    if country not in summary['spatial_info']:
                        summary['spatial_info'][country] = {
                            'crs': raster_info.get('profile', {}).get('crs'),
                            'bounds': raster_info.get('bounds'),
                            'shape': raster_info.get('data', {}).shape if hasattr(raster_info.get('data'), 'shape') else None
                        }
                else:
                    summary['failed_rasters'].append(f"{country}_{sex}_{age_group}")
    
    # Convert sets to lists for JSON serialization
    summary['countries'] = list(summary['countries'])
    summary['age_groups'] = list(summary['age_groups'])
    
    return summary

def export_metadata_to_csv(raster_data, output_path):
    """
    Export raster metadata to CSV file
    
    Args:
        raster_data: Dictionary from batch_load_rasters
        output_path: Path for output CSV
    """
    import pandas as pd
    
    records = []
    
    for country, country_data in raster_data.items():
        for sex, sex_data in country_data.items():
            for age_group, raster_info in sex_data.items():
                record = {
                    'country': country,
                    'sex': sex,
                    'age_group': age_group,
                    'data_loaded': raster_info.get('data') is not None,
                    'crs': str(raster_info.get('profile', {}).get('crs', '')),
                    'width': raster_info.get('profile', {}).get('width', 0),
                    'height': raster_info.get('profile', {}).get('height', 0)
                }
                
                if raster_info.get('bounds'):
                    record.update({
                        'left': raster_info['bounds'].left,
                        'bottom': raster_info['bounds'].bottom,
                        'right': raster_info['bounds'].right,
                        'top': raster_info['bounds'].top
                    })
                
                records.append(record)
    
    df = pd.DataFrame(records)
    df.to_csv(output_path, index=False)
    logger.info(f"Metadata exported to {output_path}")