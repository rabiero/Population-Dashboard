import pytest
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
from unittest.mock import Mock, patch, MagicMock

from data_pipeline.summarize_by_district import DistrictSummarizer

class TestDistrictSummarizer:
    
    @pytest.fixture
    def sample_districts_gdf(self):
        """Create a sample GeoDataFrame for testing"""
        polygons = [
            Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
            Polygon([(1, 0), (2, 0), (2, 1), (1, 1)])
        ]
        
        gdf = gpd.GeoDataFrame({
            'district_id': ['DIST_1', 'DIST_2'],
            'district': ['District 1', 'District 2'],
            'region': ['Region A', 'Region B'],
            'geometry': polygons
        }, crs='EPSG:4326')
        
        return gdf

    @pytest.fixture
    def sample_raster_data(self):
        """Create sample raster data for testing"""
        # Create a 10x10 raster with some data
        data = np.zeros((10, 10), dtype='float32')
        # Add some population in specific areas
        data[2:5, 2:5] = 100  # District 1 area
        data[6:9, 6:9] = 200  # District 2 area
        return data

    @pytest.fixture
    def sample_raster_profile(self):
        """Create sample raster profile"""
        return {
            'crs': 'EPSG:4326',
            'transform': Mock(a=0.1, b=0.0, c=0.0, d=0.0, e=-0.1, f=0.0),
            'width': 10,
            'height': 10,
            'nodata': -9999
        }

    def test_initialization(self):
        summarizer = DistrictSummarizer()
        assert hasattr(summarizer, 'admin_boundaries')
        assert isinstance(summarizer.admin_boundaries, dict)

    @patch('geopandas.read_file')
    def test_load_admin_boundaries_success(self, mock_read_file, sample_districts_gdf):
        mock_read_file.return_value = sample_districts_gdf
        
        summarizer = DistrictSummarizer()
        
        # Verify that boundaries are loaded
        assert 'KEN' in summarizer.admin_boundaries
        assert 'UGA' in summarizer.admin_boundaries
        # Mock will return the same data for both, but in real case they would be different

    @patch('geopandas.read_file')
    def test_load_admin_boundaries_failure(self, mock_read_file):
        mock_read_file.side_effect = Exception("File not found")
        
        # Should not raise exception, just log error
        summarizer = DistrictSummarizer()
        assert summarizer.admin_boundaries == {}

    @patch('rasterio.features.geometry_mask')
    def test_summarize_raster_by_districts(self, mock_geometry_mask, 
                                         sample_districts_gdf,
                                         sample_raster_data,
                                         sample_raster_profile):
        # Mock the geometry mask
        mock_geometry_mask.side_effect = [
            # First district mask
            np.array([
                [False, False, False, False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False, False, False, False],
                [False, False, True,  True,  True,  False, False, False, False, False],
                [False, False, True,  True,  True,  False, False, False, False, False],
                [False, False, True,  True,  True,  False, False, False, False, False],
                [False, False, False, False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False, False, False, False]
            ]),
            # Second district mask
            np.array([
                [False, False, False, False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False, False, False, False],
                [False, False, False, False, False, False, True,  True,  True,  False],
                [False, False, False, False, False, False, True,  True,  True,  False],
                [False, False, False, False, False, False, True,  True,  True,  False],
                [False, False, False, False, False, False, False, False, False, False]
            ])
        ]
        
        summarizer = DistrictSummarizer()
        summarizer.admin_boundaries = {'TEST': sample_districts_gdf}
        
        result = summarizer.summarize_raster_by_districts(
            sample_raster_data, sample_raster_profile, 'TEST'
        )
        
        assert result is not None
        assert len(result) == 2
        assert 'district_id' in result.columns
        assert 'population' in result.columns
        assert 'pixel_count' in result.columns
        
        # Check that populations are calculated correctly
        populations = result['population'].values
        assert populations[0] == 900  # 3x3 area with 100 each = 900
        assert populations[1] == 1800  # 3x3 area with 200 each = 1800

    def test_summarize_raster_no_boundaries(self, sample_raster_data, sample_raster_profile):
        summarizer = DistrictSummarizer()
        summarizer.admin_boundaries = {}  # No boundaries loaded
        
        result = summarizer.summarize_raster_by_districts(
            sample_raster_data, sample_raster_profile, 'TEST'
        )
        
        assert result is None

    @patch.object(DistrictSummarizer, 'summarize_raster_by_districts')
    def test_batch_summarize_rasters(self, mock_summarize, sample_districts_gdf):
        # Mock the summarize method to return sample data
        mock_summarize.return_value = sample_districts_gdf
        
        # Mock raster data
        raster_data = {
            'KEN': {
                'M': {
                    '0_4': {
                        'data': np.ones((10, 10)),
                        'profile': {'crs': 'EPSG:4326'},
                        'bounds': None
                    }
                }
            }
        }
        
        summarizer = DistrictSummarizer()
        summarizer.admin_boundaries = {'KEN': sample_districts_gdf}
        
        results = summarizer.batch_summarize_rasters(raster_data)
        
        assert 'KEN' in results
        assert 'M' in results['KEN']
        assert '0_4' in results['KEN']['M']
        assert mock_summarize.called

    def test_create_combined_summary(self):
        # Create sample district summaries
        summaries = {
            'KEN': {
                'M': {
                    '0_4': gpd.GeoDataFrame({
                        'district_id': ['KEN.1.1', 'KEN.1.2'],
                        'district': ['Nairobi', 'Mombasa'],
                        'region': ['Nairobi', 'Coast'],
                        'population': [1000, 500],
                        'geometry': [None, None]
                    })
                },
                'F': {
                    '15_19': gpd.GeoDataFrame({
                        'district_id': ['KEN.1.1', 'KEN.1.2'],
                        'district': ['Nairobi', 'Mombasa'],
                        'region': ['Nairobi', 'Coast'],
                        'population': [800, 400],
                        'geometry': [None, None]
                    })
                }
            }
        }
        
        summarizer = DistrictSummarizer()
        combined = summarizer.create_combined_summary(summaries)
        
        assert isinstance(combined, pd.DataFrame)
        assert len(combined) == 4  # 2 districts × 2 age/sex combinations
        assert 'country' in combined.columns
        assert 'sex' in combined.columns
        assert 'age_group' in combined.columns
        assert 'population' in combined.columns

    def test_create_combined_summary_empty(self):
        summarizer = DistrictSummarizer()
        combined = summarizer.create_combined_summary({})
        
        assert isinstance(combined, pd.DataFrame)
        assert len(combined) == 0

    def test_calculate_demographic_indicators(self):
        # Create sample combined summary
        combined_summary = pd.DataFrame({
            'country': ['KEN', 'KEN', 'KEN', 'KEN'],
            'district_id': ['D1', 'D1', 'D1', 'D1'],
            'district': ['Test District', 'Test District', 'Test District', 'Test District'],
            'sex': ['M', 'F', 'M', 'F'],
            'age_group': ['0_4', '0_4', '15_19', '15_19'],
            'population': [100, 90, 200, 180]
        })
        
        summarizer = DistrictSummarizer()
        indicators = summarizer.calculate_demographic_indicators(combined_summary)
        
        assert isinstance(indicators, pd.DataFrame)
        assert 'total_population' in indicators.columns
        assert 'child_percentage' in indicators.columns
        assert 'working_age_percentage' in indicators.columns
        assert 'elderly_percentage' in indicators.columns
        assert 'sex_ratio' in indicators.columns
        
        # Check calculations
        total_pop = 100 + 90 + 200 + 180  # 570
        child_pop = 100 + 90  # 190
        working_pop = 200 + 180  # 380
        
        assert indicators.iloc[0]['total_population'] == total_pop
        assert indicators.iloc[0]['child_percentage'] == pytest.approx((child_pop / total_pop) * 100)
        assert indicators.iloc[0]['working_age_percentage'] == pytest.approx((working_pop / total_pop) * 100)

    def test_calculate_demographic_indicators_empty(self):
        summarizer = DistrictSummarizer()
        empty_summary = pd.DataFrame()
        
        indicators = summarizer.calculate_demographic_indicators(empty_summary)
        
        assert isinstance(indicators, pd.DataFrame)
        assert len(indicators) == 0

if __name__ == '__main__':
    pytest.main([__file__, '-v'])