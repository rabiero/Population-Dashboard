import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import sys

# Add parent directory to path to import pipeline modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dashboard.filters import create_filters
from dashboard.charts import (
    create_choropleth_map,
    create_age_sex_pyramid,
    create_population_summary_chart
)
from dashboard.text_blocks import get_public_health_insights

def setup_page():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="WorldPop Population Dashboard",
        page_icon="🌍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🌍 WorldPop 2025 Population Dashboard")
    st.markdown("""
    Interactive visualization of age- and sex-structured population data for Kenya and Uganda.
    Explore population patterns to inform public health planning and resource allocation.
    """)

def load_sample_data():
    """
    Load sample aggregated data for demonstration.
    In a full implementation, this would come from the data pipeline.
    """
    # Sample data structure matching what the pipeline would produce
    # 5 districts × 6 age groups × 2 sexes = 60 records per country
    
    # Kenya data
    kenya_districts = ['Nairobi', 'Mombasa', 'Kisumu', 'Nakuru', 'Eldoret']
    kenya_age_groups = ['0-4', '5-9', '10-14', '15-19', '20-24', '25-29']
    kenya_sexes = ['M', 'F']
    
    # Create Kenya data with exactly 60 records
    kenya_data = []
    for district in kenya_districts:
        for age_group in kenya_age_groups:
            for sex in kenya_sexes:
                # Generate sample population data
                if district == 'Nairobi':
                    base_pop = 400000 if sex == 'M' else 380000
                elif district == 'Mombasa':
                    base_pop = 150000 if sex == 'M' else 145000
                elif district == 'Kisumu':
                    base_pop = 100000 if sex == 'M' else 95000
                elif district == 'Nakuru':
                    base_pop = 120000 if sex == 'M' else 115000
                else:  # Eldoret
                    base_pop = 70000 if sex == 'M' else 68000
                
                # Adjust by age group
                age_factor = {
                    '0-4': 1.1, '5-9': 1.0, '10-14': 0.9, 
                    '15-19': 0.8, '20-24': 0.7, '25-29': 0.6
                }[age_group]
                
                population = int(base_pop * age_factor)
                
                kenya_data.append({
                    'district': district,
                    'age_group': age_group,
                    'sex': sex,
                    'population': population,
                    'country': 'KEN'
                })
    
    # Uganda data
    uganda_districts = ['Kampala', 'Gulu', 'Lira', 'Mbale', 'Jinja']
    uganda_age_groups = ['0-4', '5-9', '10-14', '15-19', '20-24', '25-29']
    uganda_sexes = ['M', 'F']
    
    # Create Uganda data with exactly 60 records
    uganda_data = []
    for district in uganda_districts:
        for age_group in uganda_age_groups:
            for sex in uganda_sexes:
                # Generate sample population data
                if district == 'Kampala':
                    base_pop = 350000 if sex == 'M' else 340000
                elif district == 'Gulu':
                    base_pop = 80000 if sex == 'M' else 78000
                elif district == 'Lira':
                    base_pop = 70000 if sex == 'M' else 68000
                elif district == 'Mbale':
                    base_pop = 85000 if sex == 'M' else 83000
                else:  # Jinja
                    base_pop = 75000 if sex == 'M' else 73000
                
                # Adjust by age group
                age_factor = {
                    '0-4': 1.1, '5-9': 1.0, '10-14': 0.9, 
                    '15-19': 0.8, '20-24': 0.7, '25-29': 0.6
                }[age_group]
                
                population = int(base_pop * age_factor)
                
                uganda_data.append({
                    'district': district,
                    'age_group': age_group,
                    'sex': sex,
                    'population': population,
                    'country': 'UGA'
                })
    
    # Create DataFrames
    kenya_df = pd.DataFrame(kenya_data)
    uganda_df = pd.DataFrame(uganda_data)
    
    return {
        'KEN': kenya_df,
        'UGA': uganda_df
    }

def main():
    """Main dashboard application"""
    setup_page()
    
    # Load data
    sample_data = load_sample_data()
    all_data = pd.concat(sample_data.values(), ignore_index=True)
    
    # Create filters in sidebar
    st.sidebar.header("🔍 Filter Data")
    selected_country, selected_age_groups, selected_sex = create_filters(all_data)
    
    # Apply filters
    filtered_data = all_data.copy()
    if selected_country != "All":
        filtered_data = filtered_data[filtered_data['country'] == selected_country]
    if selected_sex != "All":
        filtered_data = filtered_data[filtered_data['sex'] == selected_sex]
    if selected_age_groups:
        filtered_data = filtered_data[filtered_data['age_group'].isin(selected_age_groups)]
    
    # Display public health insights
    st.header("📊 Public Health Insights")
    get_public_health_insights(filtered_data, selected_country, selected_age_groups, selected_sex)
    
    # Key metrics
    st.header("📈 Key Population Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    total_population = filtered_data['population'].sum()
    male_population = filtered_data[filtered_data['sex'] == 'M']['population'].sum()
    female_population = filtered_data[filtered_data['sex'] == 'F']['population'].sum()
    
    with col1:
        st.metric("Total Population", f"{total_population:,}")
    with col2:
        st.metric("Male Population", f"{male_population:,}")
    with col3:
        st.metric("Female Population", f"{female_population:,}")
    with col4:
        if total_population > 0:
            sex_ratio = (male_population / female_population) if female_population > 0 else 0
            st.metric("Sex Ratio (M/F)", f"{sex_ratio:.2f}")
    
    # Charts
    st.header("📊 Population Visualizations")
    
    # Create two columns for charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Population Distribution by District")
        fig_map = create_choropleth_map(filtered_data, selected_country)
        st.plotly_chart(fig_map, use_container_width=True)
    
    with col2:
        st.subheader("Age-Sex Pyramid")
        fig_pyramid = create_age_sex_pyramid(filtered_data)
        st.plotly_chart(fig_pyramid, use_container_width=True)
    
    # Summary chart
    st.subheader("Population Summary")
    fig_summary = create_population_summary_chart(filtered_data)
    st.plotly_chart(fig_summary, use_container_width=True)
    
    # Data table
    st.header("📋 Detailed Data")
    st.dataframe(
        filtered_data.groupby(['country', 'district', 'age_group', 'sex'])['population']
        .sum()
        .reset_index()
        .sort_values('population', ascending=False),
        use_container_width=True
    )

if __name__ == "__main__":
    main()