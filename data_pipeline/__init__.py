"""
WorldPop Data Pipeline

A modular pipeline for processing WorldPop age- and sex-structured population data
for Kenya and Uganda, with district-level summarization and dashboard integration.
"""

__version__ = "1.0.0"
__author__ = "WorldPop Dashboard Team"

from .config import *
from .load_rasters import RasterLoader
from .extract_metadata import *
from .summarize_by_district import DistrictSummarizer
from .utils import setup_logging