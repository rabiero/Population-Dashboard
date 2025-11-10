import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "assets"
GADM_DIR = DATA_DIR / "gadm"
OUTPUT_DIR = BASE_DIR / "outputs"

# WorldPop data configuration
WORLDPOP_BASE_URL = "https://data.worldpop.org/GIS/AgeSex_structures/Global_2015_2030_2025/1km_ua/constrained"
COUNTRIES = {
    "KEN": "Kenya",
    "UGA": "Uganda"
}

# Age groups and sex combinations
AGE_GROUPS = [
    "0_4", "5_9", "10_14", "15_19", "20_24", "25_29", 
    "30_34", "35_39", "40_44", "45_49", "50_54", 
    "55_59", "60_64", "65_69", "70_74", "75_79", "80_plus"
]

SEX_OPTIONS = ["M", "F"]

# GADM files
GADM_FILES = {
    "KEN": GADM_DIR / "gadm41_KEN_2.json",
    "UGA": GADM_DIR / "gadm41_UGA_2.json"
}

# Cache configuration
CACHE_DIR = BASE_DIR / "cache"
CACHE_MAX_AGE = 24 * 60 * 60  # 24 hours in seconds

# Create necessary directories
for directory in [OUTPUT_DIR, CACHE_DIR, GADM_DIR]:
    directory.mkdir(parents=True, exist_ok=True)