import pytest
import rasterio
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import tempfile
from pathlib import Path

from data_pipeline.load_rasters import RasterLoader
from data_pipeline.config import COUNTRIES, AGE_GROUPS, SEX_OPTIONS

class TestRasterLoader:
    
    def test_initialization(self, test_cache_dir):
        loader = RasterLoader(cache_dir=test_cache_dir)
        assert loader.cache_dir == test_cache_dir
        
    def test_get_raster_url(self):
        loader = RasterLoader()
        url = loader.get_raster_url('KEN', 'M', '0_4')
        expected_url = "https://data.worldpop.org/GIS/AgeSex_structures/Global_2015_2030_2025/1km_ua/constrained/KEN/v1.0/M_0_4.tif"
        assert url == expected_url
        
    def test_get_raster_url_uganda(self):
        loader = RasterLoader()
        url = loader.get_raster_url('UGA', 'F', '15_19')
        expected_url = "https://data.worldpop.org/GIS/AgeSex_structures/Global_2015_2030_2025/1km_ua/constrained/UGA/v1.0/F_15_19.tif"
        assert url == expected_url

    @patch('data_pipeline.load_rasters.download_file')
    @patch('data_pipeline.load_rasters.get_cached_file')
    def test_load_raster_success(self, mock_get_cached, mock_download, test_cache_dir):
        # Mock cached file
        mock_get_cached.return_value = None
        
        # Create a temporary raster file for testing
        with tempfile.NamedTemporaryFile(suffix='.tif', delete=False) as tmp_file:
            # Create a simple raster
            with rasterio.open(
                tmp_file.name,
                'w',
                driver='GTiff',
                height=10,
                width=10,
                count=1,
                dtype='float32',
                crs='EPSG:4326',
                transform=rasterio.Affine(1.0, 0.0, 0.0, 0.0, -1.0, 0.0),
            ) as dst:
                data = np.ones((10, 10), dtype='float32')
                dst.write(data, 1)
            
            mock_download.return_value = Path(tmp_file.name)
            
            loader = RasterLoader(cache_dir=test_cache_dir)
            data, profile, bounds = loader.load_raster('KEN', 'M', '0_4')
            
            assert data is not None
            assert isinstance(data, np.ndarray)
            assert data.shape == (10, 10)
            assert profile['crs'] == 'EPSG:4326'
            assert profile['width'] == 10
            assert profile['height'] == 10
            
            # Clean up
            Path(tmp_file.name).unlink()

    @patch('data_pipeline.load_rasters.download_file')
    def test_load_raster_failure(self, mock_download, test_cache_dir):
        mock_download.side_effect = Exception("Download failed")
        
        loader = RasterLoader(cache_dir=test_cache_dir)
        data, profile, bounds = loader.load_raster('KEN', 'M', '0_4')
        
        assert data is None
        assert profile is None
        assert bounds is None

    @patch('data_pipeline.load_rasters.RasterLoader.load_raster')
    def test_batch_load_rasters(self, mock_load_raster, test_cache_dir):
        # Mock successful raster loading
        mock_load_raster.return_value = (
            np.ones((10, 10), dtype='float32'),
            {'crs': 'EPSG:4326', 'width': 10, 'height': 10},
            None
        )
        
        loader = RasterLoader(cache_dir=test_cache_dir)
        results = loader.batch_load_rasters(
            countries=['KEN'],
            age_groups=['0_4'],
            sex_options=['M']
        )
        
        assert 'KEN' in results
        assert 'M' in results['KEN']
        assert '0_4' in results['KEN']['M']
        assert results['KEN']['M']['0_4']['data'] is not None
        assert mock_load_raster.call_count == 1

    def test_batch_load_rasters_empty(self, test_cache_dir):
        loader = RasterLoader(cache_dir=test_cache_dir)
        results = loader.batch_load_rasters(countries=[])
        
        assert results == {}

    @patch('data_pipeline.load_rasters.download_file')
    def test_get_raster_metadata(self, mock_download, test_cache_dir):
        # Create a temporary raster file for testing
        with tempfile.NamedTemporaryFile(suffix='.tif', delete=False) as tmp_file:
            with rasterio.open(
                tmp_file.name,
                'w',
                driver='GTiff',
                height=100,
                width=100,
                count=1,
                dtype='float32',
                crs='EPSG:4326',
                transform=rasterio.Affine(0.01, 0.0, 30.0, 0.0, -0.01, 0.0),
                nodata=-9999
            ) as dst:
                data = np.ones((100, 100), dtype='float32')
                dst.write(data, 1)
            
            mock_download.return_value = Path(tmp_file.name)
            
            loader = RasterLoader(cache_dir=test_cache_dir)
            metadata = loader.get_raster_metadata('KEN', 'M', '0_4')
            
            assert metadata is not None
            assert metadata['country'] == 'KEN'
            assert metadata['sex'] == 'M'
            assert metadata['age_group'] == '0_4'
            assert metadata['crs'] == 'EPSG:4326'
            assert metadata['width'] == 100
            assert metadata['height'] == 100
            assert metadata['nodata'] == -9999
            
            # Clean up
            Path(tmp_file.name).unlink()

if __name__ == '__main__':
    pytest.main([__file__, '-v'])