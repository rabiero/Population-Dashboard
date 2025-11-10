import pytest
import pandas as pd
from unittest.mock import Mock, patch

from data_pipeline.extract_metadata import (
    parse_filename,
    extract_country_from_url,
    validate_metadata,
    create_metadata_summary,
    export_metadata_to_csv
)

class TestMetadataExtraction:
    
    def test_parse_filename_valid(self):
        filename = "M_0_4.tif"
        metadata = parse_filename(filename)
        
        assert metadata is not None
        assert metadata['sex'] == 'M'
        assert metadata['age_start'] == 0
        assert metadata['age_end'] == '4'
        assert metadata['age_group'] == '0_4'
        assert metadata['filename'] == 'M_0_4.tif'

    def test_parse_filename_plus_age(self):
        filename = "F_80_plus.tif"
        metadata = parse_filename(filename)
        
        assert metadata is not None
        assert metadata['sex'] == 'F'
        assert metadata['age_start'] == 80
        assert metadata['age_end'] == 'plus'
        assert metadata['age_group'] == '80+'

    def test_parse_filename_with_path(self):
        filename = "/path/to/data/F_15_19.tif"
        metadata = parse_filename(filename)
        
        assert metadata is not None
        assert metadata['sex'] == 'F'
        assert metadata['age_group'] == '15_19'

    def test_parse_filename_invalid(self):
        filename = "invalid_filename.txt"
        metadata = parse_filename(filename)
        
        assert metadata is None

    def test_extract_country_from_url_kenya(self):
        url = "https://data.worldpop.org/GIS/AgeSex_structures/Global_2015_2030_2025/1km_ua/constrained/KEN/v1.0/M_0_4.tif"
        country = extract_country_from_url(url)
        
        assert country == "KEN"

    def test_extract_country_from_url_uganda(self):
        url = "https://data.worldpop.org/GIS/AgeSex_structures/Global_2015_2030_2025/1km_ua/constrained/UGA/v1.0/F_15_19.tif"
        country = extract_country_from_url(url)
        
        assert country == "UGA"

    def test_extract_country_from_url_invalid(self):
        url = "https://example.com/path/file.tif"
        country = extract_country_from_url(url)
        
        assert country is None

    def test_validate_metadata_valid(self):
        metadata = {
            'sex': 'M',
            'age_group': '0_4',
            'age_start': 0
        }
        
        assert validate_metadata(metadata) is True

    def test_validate_metadata_invalid_sex(self):
        metadata = {
            'sex': 'X',  # Invalid sex
            'age_group': '0_4',
            'age_start': 0
        }
        
        assert validate_metadata(metadata) is False

    def test_validate_metadata_missing_field(self):
        metadata = {
            'sex': 'M',
            'age_group': '0_4'
            # Missing age_start
        }
        
        assert validate_metadata(metadata) is False

    def test_validate_metadata_none(self):
        assert validate_metadata(None) is False

    def test_create_metadata_summary(self):
        # Mock raster data structure
        raster_data = {
            'KEN': {
                'M': {
                    '0_4': {
                        'data': Mock(shape=(100, 100)),
                        'profile': {'crs': 'EPSG:4326', 'width': 100, 'height': 100},
                        'bounds': Mock(left=30, bottom=0, right=40, top=10)
                    }
                },
                'F': {
                    '15_19': {
                        'data': None,  # Failed raster
                        'profile': {},
                        'bounds': None
                    }
                }
            }
        }
        
        summary = create_metadata_summary(raster_data)
        
        assert summary['total_rasters'] == 1
        assert 'KEN' in summary['countries']
        assert '0_4' in summary['age_groups']
        assert len(summary['failed_rasters']) == 1
        assert 'KEN' in summary['spatial_info']

    def test_create_metadata_summary_empty(self):
        raster_data = {}
        summary = create_metadata_summary(raster_data)
        
        assert summary['total_rasters'] == 0
        assert summary['countries'] == []
        assert summary['age_groups'] == []
        assert summary['failed_rasters'] == []

    @patch('pandas.DataFrame.to_csv')
    def test_export_metadata_to_csv(self, mock_to_csv, test_output_dir):
        # Mock raster data
        raster_data = {
            'KEN': {
                'M': {
                    '0_4': {
                        'data': Mock(shape=(100, 100)),
                        'profile': {
                            'crs': 'EPSG:4326',
                            'width': 100,
                            'height': 100
                        },
                        'bounds': Mock(left=30, bottom=0, right=40, top=10)
                    }
                }
            }
        }
        
        output_path = test_output_dir / "test_metadata.csv"
        export_metadata_to_csv(raster_data, output_path)
        
        # Verify that to_csv was called
        mock_to_csv.assert_called_once()

    def test_export_metadata_to_csv_empty(self, test_output_dir):
        raster_data = {}
        output_path = test_output_dir / "empty_metadata.csv"
        
        # This should not raise an exception
        export_metadata_to_csv(raster_data, output_path)
        
        # Check that file was created (though it will be empty)
        assert output_path.exists()

if __name__ == '__main__':
    pytest.main([__file__, '-v'])