import hashlib
import time
import json
from pathlib import Path
import requests
import logging
from .config import CACHE_MAX_AGE

logger = logging.getLogger(__name__)

def generate_cache_key(url):
    """Generate cache key from URL"""
    return hashlib.md5(url.encode()).hexdigest()

def get_cached_file(url, cache_dir, max_age=CACHE_MAX_AGE):
    """
    Get cached file if it exists and is not expired
    
    Args:
        url: File URL
        cache_dir: Cache directory
        max_age: Maximum cache age in seconds
        
    Returns:
        Path or None: Path to cached file if valid
    """
    cache_key = generate_cache_key(url)
    cache_file = cache_dir / f"{cache_key}.tif"
    metadata_file = cache_dir / f"{cache_key}.json"
    
    if cache_file.exists() and metadata_file.exists():
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # Check if cache is still valid
            if time.time() - metadata['timestamp'] < max_age:
                logger.debug(f"Using cached file: {cache_file}")
                return cache_file
            else:
                logger.debug(f"Cache expired for: {url}")
        except Exception as e:
            logger.warning(f"Error reading cache metadata: {str(e)}")
    
    return None

def download_file(url, cache_dir, chunk_size=8192):
    """
    Download file and cache it
    
    Args:
        url: File URL
        cache_dir: Cache directory
        chunk_size: Download chunk size
        
    Returns:
        Path: Path to downloaded file
    """
    cache_key = generate_cache_key(url)
    cache_file = cache_dir / f"{cache_key}.tif"
    metadata_file = cache_dir / f"{cache_key}.json"
    
    try:
        logger.info(f"Downloading: {url}")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Download file
        with open(cache_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                f.write(chunk)
        
        # Save metadata
        metadata = {
            'url': url,
            'timestamp': time.time(),
            'size': cache_file.stat().st_size
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f)
        
        logger.info(f"Downloaded and cached: {cache_file}")
        return cache_file
        
    except Exception as e:
        logger.error(f"Failed to download {url}: {str(e)}")
        # Clean up partial download
        if cache_file.exists():
            cache_file.unlink()
        raise

def clear_old_cache(cache_dir, max_age=CACHE_MAX_AGE):
    """
    Clear expired cache files
    
    Args:
        cache_dir: Cache directory
        max_age: Maximum cache age in seconds
    """
    current_time = time.time()
    cleared_count = 0
    
    for cache_file in cache_dir.glob("*.tif"):
        metadata_file = cache_dir / f"{cache_file.stem}.json"
        
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                
                if current_time - metadata['timestamp'] > max_age:
                    cache_file.unlink()
                    metadata_file.unlink()
                    cleared_count += 1
                    
            except Exception as e:
                logger.warning(f"Error processing cache file {cache_file}: {str(e)}")
    
    logger.info(f"Cleared {cleared_count} expired cache files")

def get_cache_size(cache_dir):
    """Get total size of cache directory"""
    total_size = 0
    for file_path in cache_dir.glob("*"):
        if file_path.is_file():
            total_size += file_path.stat().st_size
    return total_size