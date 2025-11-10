import rasterio
import numpy as np
import requests
from pathlib import Path
import tempfile
import logging
from .config import WORLDPOP_BASE_URL, COUNTRIES, AGE_GROUPS, SEX_OPTIONS
from .utils import download_file, get_cached_file

logger = logging.getLogger(__name__)

class RasterLoader:
    def __init__(self, cache_dir=None):
        self.cache_dir = cache_dir
        
    def get_raster_url(self, country, sex, age_group):
        """Construct the URL for a specific raster file"""
        filename = f"{sex}_{age_group}.tif"
        url = f"{WORLDPOP_BASE_URL}/{country}/v1.0/{filename}"
        return url
    
    def load_raster(self, country, sex, age_group, use_cache=True):
        """
        Load raster data from WorldPop URL or cache
        
        Args:
            country: Country code (KEN, UGA)
            sex: Sex (M, F)
            age_group: Age group string
            use_cache: Whether to use cached files
            
        Returns:
            tuple: (data array, profile dict) or (None, None) if failed
        """
        url = self.get_raster_url(country, sex, age_group)
        
        try:
            if use_cache and self.cache_dir:
                cached_file = get_cached_file(url, self.cache_dir)
                if cached_file:
                    file_path = cached_file
                else:
                    file_path = download_file(url, self.cache_dir)
            else:
                # Download to temporary file
                with tempfile.NamedTemporaryFile(suffix='.tif', delete=False) as tmp_file:
                    file_path = download_file(url, Path(tmp_file.name).parent)
                    tmp_file.name = str(file_path)
            
            # Read raster data
            with rasterio.open(file_path) as src:
                data = src.read(1)  # Read first band
                profile = src.profile
                bounds = src.bounds
                
            logger.info(f"Successfully loaded raster: {country}_{sex}_{age_group}")
            return data, profile, bounds
            
        except Exception as e:
            logger.error(f"Failed to load raster {country}_{sex}_{age_group}: {str(e)}")
            return None, None, None
    
    def get_raster_metadata(self, country, sex, age_group):
        """Get metadata for a raster without loading full data"""
        url = self.get_raster_url(country, sex, age_group)
        
        try:
            if self.cache_dir:
                cached_file = get_cached_file(url, self.cache_dir)
                if cached_file:
                    file_path = cached_file
                else:
                    file_path = download_file(url, self.cache_dir)
            else:
                with tempfile.NamedTemporaryFile(suffix='.tif', delete=False) as tmp_file:
                    file_path = download_file(url, Path(tmp_file.name).parent)
                    tmp_file.name = str(file_path)
            
            with rasterio.open(file_path) as src:
                metadata = {
                    'country': country,
                    'sex': sex,
                    'age_group': age_group,
                    'crs': src.crs,
                    'transform': src.transform,
                    'width': src.width,
                    'height': src.height,
                    'bounds': src.bounds,
                    'nodata': src.nodata
                }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to get metadata for {country}_{sex}_{age_group}: {str(e)}")
            return None
    
    def batch_load_rasters(self, countries=None, age_groups=None, sex_options=None):
        """
        Load multiple rasters in batch
        
        Args:
            countries: List of country codes
            age_groups: List of age groups
            sex_options: List of sex options
            
        Returns:
            dict: Nested dictionary of raster data
        """
        if countries is None:
            countries = COUNTRIES.keys()
        if age_groups is None:
            age_groups = AGE_GROUPS
        if sex_options is None:
            sex_options = SEX_OPTIONS
            
        results = {}
        
        for country in countries:
            results[country] = {}
            for sex in sex_options:
                results[country][sex] = {}
                for age_group in age_groups:
                    data, profile, bounds = self.load_raster(country, sex, age_group)
                    if data is not None:
                        results[country][sex][age_group] = {
                            'data': data,
                            'profile': profile,
                            'bounds': bounds
                        }
                    else:
                        logger.warning(f"Failed to load {country}_{sex}_{age_group}")
        
        return results