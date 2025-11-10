import pytest
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Test configuration
TEST_DATA_DIR = Path(__file__).parent / "test_data"
TEST_CACHE_DIR = TEST_DATA_DIR / "cache"
TEST_OUTPUT_DIR = TEST_DATA_DIR / "outputs"

# Create test directories
TEST_DATA_DIR.mkdir(exist_ok=True)
TEST_CACHE_DIR.mkdir(exist_ok=True)
TEST_OUTPUT_DIR.mkdir(exist_ok=True)

@pytest.fixture
def test_data_dir():
    return TEST_DATA_DIR

@pytest.fixture
def test_cache_dir():
    return TEST_CACHE_DIR

@pytest.fixture
def test_output_dir():
    return TEST_OUTPUT_DIR

@pytest.fixture
def sample_raster_metadata():
    return {
        'country': 'KEN',
        'sex': 'M',
        'age_group': '0_4',
        'crs': 'EPSG:4326',
        'width': 100,
        'height': 100,
        'bounds': None
    }

@pytest.fixture
def sample_district_data():
    return {
        'district_id': 'KEN.1.1_1',
        'district': 'Nairobi',
        'region': 'Nairobi',
        'population': 450000,
        'pixel_count': 1000
    }