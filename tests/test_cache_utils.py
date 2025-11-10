import pytest
import time
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from data_pipeline.cache_utils import (
    generate_cache_key,
    get_cached_file,
    download_file,
    clear_old_cache,
    get_cache_size
)

class TestCacheUtilities:
    
    def test_generate_cache_key(self):
        url = "https://example.com/data.tif"
        key = generate_cache_key(url)
        
        # Should be consistent
        key2 = generate_cache_key(url)
        assert key == key2
        
        # Should be different for different URLs
        different_url = "https://example.com/other.tif"
        different_key = generate_cache_key(different_url)
        assert key != different_key

    def test_get_cached_file_exists_valid(self, test_cache_dir):
        url = "https://example.com/data.tif"
        cache_key = generate_cache_key(url)
        cache_file = test_cache_dir / f"{cache_key}.tif"
        metadata_file = test_cache_dir / f"{cache_key}.json"
        
        # Create test files
        cache_file.write_text("test data")
        metadata = {
            'url': url,
            'timestamp': time.time() - 100,  # 100 seconds old
            'size': 9
        }
        metadata_file.write_text(json.dumps(metadata))
        
        result = get_cached_file(url, test_cache_dir, max_age=3600)  # 1 hour max age
        
        assert result == cache_file
        
        # Clean up
        cache_file.unlink()
        metadata_file.unlink()

    def test_get_cached_file_expired(self, test_cache_dir):
        url = "https://example.com/data.tif"
        cache_key = generate_cache_key(url)
        cache_file = test_cache_dir / f"{cache_key}.tif"
        metadata_file = test_cache_dir / f"{cache_key}.json"
        
        # Create test files with old timestamp
        cache_file.write_text("test data")
        metadata = {
            'url': url,
            'timestamp': time.time() - 7200,  # 2 hours old
            'size': 9
        }
        metadata_file.write_text(json.dumps(metadata))
        
        result = get_cached_file(url, test_cache_dir, max_age=3600)  # 1 hour max age
        
        assert result is None
        
        # Clean up
        cache_file.unlink()
        metadata_file.unlink()

    def test_get_cached_file_missing_metadata(self, test_cache_dir):
        url = "https://example.com/data.tif"
        cache_key = generate_cache_key(url)
        cache_file = test_cache_dir / f"{cache_key}.tif"
        
        # Create only cache file, no metadata
        cache_file.write_text("test data")
        
        result = get_cached_file(url, test_cache_dir)
        
        assert result is None
        
        # Clean up
        cache_file.unlink()

    def test_get_cached_file_not_exists(self, test_cache_dir):
        url = "https://example.com/nonexistent.tif"
        result = get_cached_file(url, test_cache_dir)
        
        assert result is None

    @patch('requests.get')
    def test_download_file_success(self, mock_get, test_cache_dir):
        # Mock response
        mock_response = Mock()
        mock_response.iter_content.return_value = [b"chunk1", b"chunk2", b"chunk3"]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        url = "https://example.com/data.tif"
        result = download_file(url, test_cache_dir)
        
        assert result is not None
        assert result.exists()
        
        # Verify files were created
        cache_key = generate_cache_key(url)
        cache_file = test_cache_dir / f"{cache_key}.tif"
        metadata_file = test_cache_dir / f"{cache_key}.json"
        
        assert cache_file.exists()
        assert metadata_file.exists()
        
        # Clean up
        cache_file.unlink()
        metadata_file.unlink()

    @patch('requests.get')
    def test_download_file_failure(self, mock_get, test_cache_dir):
        mock_get.side_effect = Exception("Network error")
        
        url = "https://example.com/data.tif"
        
        with pytest.raises(Exception):
            download_file(url, test_cache_dir)
        
        # Verify no files were created
        cache_key = generate_cache_key(url)
        cache_file = test_cache_dir / f"{cache_key}.tif"
        metadata_file = test_cache_dir / f"{cache_key}.json"
        
        assert not cache_file.exists()
        assert not metadata_file.exists()

    def test_clear_old_cache(self, test_cache_dir):
        current_time = time.time()
        
        # Create some test cache files
        files_to_keep = []
        files_to_remove = []
        
        for i in range(3):
            url = f"https://example.com/data{i}.tif"
            cache_key = generate_cache_key(url)
            cache_file = test_cache_dir / f"{cache_key}.tif"
            metadata_file = test_cache_dir / f"{cache_key}.json"
            
            cache_file.write_text("data")
            
            if i < 2:  # First two files are old
                metadata = {
                    'url': url,
                    'timestamp': current_time - 7200,  # 2 hours old
                    'size': 4
                }
                files_to_remove.append((cache_file, metadata_file))
            else:  # Last file is recent
                metadata = {
                    'url': url,
                    'timestamp': current_time - 1800,  # 30 minutes old
                    'size': 4
                }
                files_to_keep.append((cache_file, metadata_file))
            
            metadata_file.write_text(json.dumps(metadata))
        
        # Clear old cache (1 hour max age)
        clear_old_cache(test_cache_dir, max_age=3600)
        
        # Verify old files were removed, recent files kept
        for cache_file, metadata_file in files_to_remove:
            assert not cache_file.exists()
            assert not metadata_file.exists()
        
        for cache_file, metadata_file in files_to_keep:
            assert cache_file.exists()
            assert metadata_file.exists()
            
            # Clean up
            cache_file.unlink()
            metadata_file.unlink()

    def test_get_cache_size(self, test_cache_dir):
        # Create some test files
        file1 = test_cache_dir / "test1.tif"
        file2 = test_cache_dir / "test2.tif"
        
        file1.write_text("x" * 1000)  # 1000 bytes
        file2.write_text("y" * 2000)  # 2000 bytes
        
        total_size = get_cache_size(test_cache_dir)
        
        assert total_size >= 3000  # At least 3000 bytes
        
        # Clean up
        file1.unlink()
        file2.unlink()

    def test_get_cache_size_empty(self, test_cache_dir):
        total_size = get_cache_size(test_cache_dir)
        assert total_size == 0

if __name__ == '__main__':
    pytest.main([__file__, '-v'])