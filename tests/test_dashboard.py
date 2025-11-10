import pytest
import pandas as pd
import streamlit as st
from unittest.mock import Mock, patch, MagicMock

from dashboard.filters import create_filters
from dashboard.charts import (
    create_choropleth_map,
    create_age_sex_pyramid,
    create_population_summary_chart,
    create_empty_figure
)
from dashboard.text_blocks import get_public_health_insights

class TestDashboardFilters:
    
    @pytest.fixture
    def sample_data(self):
        return pd.DataFrame({
            'country': ['KEN', 'KEN', 'UGA', 'UGA'],
            'district': ['Nairobi', 'Mombasa', 'Kampala', 'Gulu'],
            'age_group': ['0-4', '5-9', '0-4', '5-9'],
            'sex': ['M', 'F', 'M', 'F'],
            'population': [1000, 900, 800, 700]
        })

    @patch('streamlit.sidebar.selectbox')
    @patch('streamlit.sidebar.multiselect')
    def test_create_filters(self, mock_multiselect, mock_selectbox, sample_data):
        # Mock the filter responses
        mock_selectbox.side_effect = ["All", "All"]
        mock_multiselect.return_value = ['0-4', '5-9']
        
        country, age_groups, sex = create_filters(sample_data)
        
        assert country == "All"
        assert age_groups == ['0-4', '5-9']
        assert sex == "All"

    @patch('streamlit.sidebar.selectbox')
    @patch('streamlit.sidebar.multiselect')
    def test_create_filters_specific_country(self, mock_multiselect, mock_selectbox, sample_data):
        mock_selectbox.side_effect = ["KEN", "Male"]
        mock_multiselect.return_value = ['0-4']
        
        country, age_groups, sex = create_filters(sample_data)
        
        assert country == "KEN"
        assert age_groups == ['0-4']
        assert sex == "M"

class TestDashboardCharts:
    
    @pytest.fixture
    def sample_chart_data(self):
        return pd.DataFrame({
            'country': ['KEN', 'KEN', 'KEN', 'KEN'],
            'district': ['Nairobi', 'Nairobi', 'Mombasa', 'Mombasa'],
            'age_group': ['0-4', '5-9', '0-4', '5-9'],
            'sex': ['M', 'F', 'M', 'F'],
            'population': [1000, 900, 800, 700]
        })

    def test_create_choropleth_map(self, sample_chart_data):
        fig = create_choropleth_map(sample_chart_data, "All")
        
        # Should return a Plotly figure
        assert hasattr(fig, 'data')
        assert hasattr(fig, 'layout')

    def test_create_choropleth_map_specific_country(self, sample_chart_data):
        fig = create_choropleth_map(sample_chart_data, "KEN")
        
        assert hasattr(fig, 'data')
        assert hasattr(fig, 'layout')

    def test_create_age_sex_pyramid(self, sample_chart_data):
        fig = create_age_sex_pyramid(sample_chart_data)
        
        assert hasattr(fig, 'data')
        assert hasattr(fig, 'layout')
        # Should have two traces (male and female)
        assert len(fig.data) == 2

    def test_create_age_sex_pyramid_empty_data(self):
        empty_data = pd.DataFrame()
        fig = create_age_sex_pyramid(empty_data)
        
        assert hasattr(fig, 'layout')
        # Should handle empty data gracefully

    def test_create_population_summary_chart(self, sample_chart_data):
        fig = create_population_summary_chart(sample_chart_data)
        
        assert hasattr(fig, 'data')
        assert hasattr(fig, 'layout')

    def test_create_population_summary_chart_empty(self):
        empty_data = pd.DataFrame()
        fig = create_population_summary_chart(empty_data)
        
        assert hasattr(fig, 'layout')

    def test_create_empty_figure(self):
        message = "Test message"
        fig = create_empty_figure(message)
        
        assert hasattr(fig, 'layout')
        # Should contain the message in annotations
        annotations = fig.layout.annotations
        assert len(annotations) > 0
        assert annotations[0].text == message

class TestPublicHealthInsights:
    
    @pytest.fixture
    def sample_insight_data(self):
        return pd.DataFrame({
            'country': ['KEN'] * 8,
            'district': ['Nairobi'] * 8,
            'age_group': ['0-4', '5-9', '10-14', '15-19', '20-24', '25-29', '60-64', '80+'],
            'sex': ['M', 'F', 'M', 'F', 'M', 'F', 'M', 'F'],
            'population': [500, 480, 400, 380, 350, 340, 100, 80]  # High youth population
        })

    def test_get_public_health_insights(self, sample_insight_data):
        insights = get_public_health_insights(sample_insight_data, "KEN", ['0-4', '5-9'], "All")
        
        assert isinstance(insights, str)
        assert len(insights) > 0
        # Should contain key sections
        assert "Population Overview" in insights
        assert "Key Demographic Indicators" in insights
        assert "Service Planning Considerations" in insights

    def test_get_public_health_insights_empty_data(self):
        empty_data = pd.DataFrame()
        insights = get_public_health_insights(empty_data, "All", [], "All")
        
        assert "No data available" in insights

    def test_get_public_health_insights_high_youth(self):
        # Data with high youth population
        data = pd.DataFrame({
            'country': ['KEN'] * 4,
            'district': ['Nairobi'] * 4,
            'age_group': ['0-4', '5-9', '10-14', '15-19'],
            'sex': ['M', 'F', 'M', 'F'],
            'population': [1000, 950, 800, 750]  # Very high youth numbers
        })
        
        insights = get_public_health_insights(data, "KEN", ['0-4', '5-9', '10-14'], "All")
        
        # Should mention youth population
        assert "Youth" in insights or "young" in insights.lower()

    def test_get_public_health_insights_elderly(self):
        # Data with significant elderly population
        data = pd.DataFrame({
            'country': ['KEN'] * 6,
            'district': ['Nairobi'] * 6,
            'age_group': ['60-64', '65-69', '70-74', '75-79', '80+', '20-24'],
            'sex': ['M', 'F', 'M', 'F', 'M', 'F'],
            'population': [300, 280, 200, 180, 100, 50]  # High elderly relative to working age
        })
        
        insights = get_public_health_insights(data, "KEN", ['60-64', '65-69', '70-74', '75-79', '80+'], "All")
        
        # Should mention elderly population
        assert "Elderly" in insights or "aging" in insights.lower()

if __name__ == '__main__':
    pytest.main([__file__, '-v'])