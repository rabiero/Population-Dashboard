"""Basic tests for summarization module (smoke tests)."""
from data_pipeline import summarize_by_district


def test_summarize_callable():
    assert hasattr(summarize_by_district, "summarize_raster_by_gadm") or hasattr(summarize_by_district, "summarize_raster_by_gadm")
