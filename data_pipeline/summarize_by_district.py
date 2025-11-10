import geopandas as gpd
import pandas as pd
import numpy as np
from rasterio.mask import mask
from rasterio.features import geometry_mask
import logging
from .config import GADM_FILES, COUNTRIES
from .utils import reproject_geometry

logger = logging.getLogger(__name__)

class DistrictSummarizer:
    def __init__(self):
        self.admin_boundaries = {}
        self.load_admin_boundaries()
    
    def load_admin_boundaries(self):
        """Load GADM administrative boundaries"""
        for country, file_path in GADM_FILES.items():
            try:
                gdf = gpd.read_file(file_path)
                # Standardize column names
                gdf = gdf.rename(columns={
                    'NAME_1': 'region',
                    'NAME_2': 'district',
                    'GID_2': 'district_id'
                })
                self.admin_boundaries[country] = gdf
                logger.info(f"Loaded admin boundaries for {country}: {len(gdf)} districts")
            except Exception as e:
                logger.error(f"Failed to load admin boundaries for {country}: {str(e)}")
    
    def summarize_raster_by_districts(self, raster_data, profile, country):
        """
        Summarize raster data by administrative districts
        
        Args:
            raster_data: 2D numpy array
            profile: Raster profile with CRS and transform
            country: Country code
            
        Returns:
            GeoDataFrame: District summaries with population totals
        """
        if country not in self.admin_boundaries:
            logger.error(f"No admin boundaries loaded for {country}")
            return None
        
        districts_gdf = self.admin_boundaries[country]
        
        # Ensure same CRS
        if districts_gdf.crs != profile['crs']:
            districts_gdf = districts_gdf.to_crs(profile['crs'])
        
        results = []
        
        for idx, district in districts_gdf.iterrows():
            try:
                # Create mask for district
                geom = [district.geometry]
                district_mask = geometry_mask(
                    geom, 
                    out_shape=(profile['height'], profile['width']),
                    transform=profile['transform'],
                    invert=True
                )
                
                # Extract data within district
                district_data = raster_data[district_mask]
                
                # Remove nodata values
                if profile.get('nodata') is not None:
                    valid_data = district_data[district_data != profile['nodata']]
                else:
                    valid_data = district_data
                
                # Calculate total population
                total_population = np.sum(valid_data) if len(valid_data) > 0 else 0
                
                results.append({
                    'district_id': district['district_id'],
                    'district': district['district'],
                    'region': district.get('region', ''),
                    'population': total_population,
                    'pixel_count': len(valid_data)
                })
                
            except Exception as e:
                logger.warning(f"Failed to process district {district['district']}: {str(e)}")
                continue
        
        result_gdf = gpd.GeoDataFrame(results, geometry=districts_gdf.geometry)
        return result_gdf
    
    def batch_summarize_rasters(self, raster_data):
        """
        Summarize all rasters by districts
        
        Args:
            raster_data: Dictionary from batch_load_rasters
            
        Returns:
            dict: Nested dictionary of district summaries
        """
        summaries = {}
        
        for country, country_data in raster_data.items():
            summaries[country] = {}
            
            for sex, sex_data in country_data.items():
                summaries[country][sex] = {}
                
                for age_group, raster_info in sex_data.items():
                    if raster_info.get('data') is not None:
                        logger.info(f"Summarizing {country}_{sex}_{age_group}")
                        
                        district_summary = self.summarize_raster_by_districts(
                            raster_info['data'],
                            raster_info['profile'],
                            country
                        )
                        
                        if district_summary is not None:
                            summaries[country][sex][age_group] = district_summary
                        else:
                            logger.warning(f"Failed to summarize {country}_{sex}_{age_group}")
                    else:
                        logger.warning(f"Skipping {country}_{sex}_{age_group} - no data")
        
        return summaries
    
    def create_combined_summary(self, summaries):
        """
        Create combined summary table from all district summaries
        
        Args:
            summaries: Dictionary from batch_summarize_rasters
            
        Returns:
            DataFrame: Combined summary with country, district, age, sex
        """
        all_records = []
        
        for country, country_data in summaries.items():
            for sex, sex_data in country_data.items():
                for age_group, district_gdf in sex_data.items():
                    if district_gdf is not None:
                        for idx, row in district_gdf.iterrows():
                            record = {
                                'country': country,
                                'sex': sex,
                                'age_group': age_group,
                                'district_id': row['district_id'],
                                'district': row['district'],
                                'region': row.get('region', ''),
                                'population': row['population']
                            }
                            all_records.append(record)
        
        return pd.DataFrame(all_records)
    
    def calculate_demographic_indicators(self, combined_summary):
        """
        Calculate key demographic indicators
        
        Args:
            combined_summary: DataFrame from create_combined_summary
            
        Returns:
            DataFrame: District-level demographic indicators
        """
        # Group by district and calculate indicators
        district_totals = combined_summary.groupby(['country', 'district_id', 'district']).agg({
            'population': 'sum'
        }).reset_index()
        
        # Age structure calculations
        age_bins = {
            'children': ['0_4', '5_9', '10_14'],
            'working_age': ['15_19', '20_24', '25_29', '30_34', '35_39', '40_44', '45_49', '50_54', '55_59'],
            'elderly': ['60_64', '65_69', '70_74', '75_79', '80_plus']
        }
        
        indicators = []
        
        for (country, district_id, district), group in combined_summary.groupby(['country', 'district_id', 'district']):
            total_pop = group['population'].sum()
            
            if total_pop > 0:
                # Age structure
                children_pop = group[group['age_group'].isin(age_bins['children'])]['population'].sum()
                working_pop = group[group['age_group'].isin(age_bins['working_age'])]['population'].sum()
                elderly_pop = group[group['age_group'].isin(age_bins['elderly'])]['population'].sum()
                
                # Sex ratio
                male_pop = group[group['sex'] == 'M']['population'].sum()
                female_pop = group[group['sex'] == 'F']['population'].sum()
                sex_ratio = male_pop / female_pop if female_pop > 0 else 0
                
                indicators.append({
                    'country': country,
                    'district_id': district_id,
                    'district': district,
                    'total_population': total_pop,
                    'child_percentage': (children_pop / total_pop) * 100,
                    'working_age_percentage': (working_pop / total_pop) * 100,
                    'elderly_percentage': (elderly_pop / total_pop) * 100,
                    'sex_ratio': sex_ratio,
                    'male_population': male_pop,
                    'female_population': female_pop
                })
        
        return pd.DataFrame(indicators)