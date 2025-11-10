import streamlit as st
import pandas as pd
from typing import Tuple, List

def create_filters(data: pd.DataFrame) -> Tuple[str, List[str], str]:
    """
    Create modern, interactive filters for the dashboard
    """
    st.sidebar.markdown("""
    <style>
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    .filter-header {
        font-size: 1.2em;
        font-weight: bold;
        color: #1f1f1f;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header with icon
    st.sidebar.markdown('<div class="filter-header">🎛️ Data Filters</div>', unsafe_allow_html=True)
    
    # Country filter with flags
    st.sidebar.markdown("**🌍 Select Country**")
    countries = ["All Countries"] + sorted(data['country'].unique().tolist())
    country_labels = {
        "All Countries": "🌐 All Countries",
        "KEN": "🇰🇪 Kenya",
        "UGA": "🇺🇬 Uganda"
    }
    
    selected_country_display = st.sidebar.selectbox(
        "",
        countries,
        format_func=lambda x: country_labels.get(x, x),
        help="Filter analysis by country"
    )
    selected_country = "All" if selected_country_display == "All Countries" else selected_country_display
    
    st.sidebar.markdown("---")
    
    # Age group filter with modern multi-select
    st.sidebar.markdown("**👥 Age Groups**")
    
    # Group age groups logically
    age_groups = sorted(data['age_group'].unique().tolist())
    child_ages = [age for age in age_groups if age in ['0-4', '5-9', '10-14']]
    youth_ages = [age for age in age_groups if age in ['15-19', '20-24', '25-29']]
    adult_ages = [age for age in age_groups if age in ['30-34', '35-39', '40-44', '45-49']]
    senior_ages = [age for age in age_groups if age in ['50-54', '55-59', '60-64', '65-69', '70-74', '75-79', '80+']]
    
    # Quick select buttons
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("👶 Children", use_container_width=True):
            selected_age_groups = child_ages
        if st.button("💼 Workforce", use_container_width=True):
            selected_age_groups = youth_ages + adult_ages
    with col2:
        if st.button("👵 Elderly", use_container_width=True):
            selected_age_groups = senior_ages
        if st.button("📊 All Ages", use_container_width=True):
            selected_age_groups = age_groups
    
    # Multi-select for fine-grained control
    selected_age_groups = st.sidebar.multiselect(
        "Select specific age groups:",
        age_groups,
        default=age_groups,
        help="Choose one or multiple age groups for analysis"
    )
    
    st.sidebar.markdown("---")
    
    # Sex filter with modern toggle style
    st.sidebar.markdown("**⚧️ Sex**")
    
    sex_options = ["All", "Male", "Female"]
    sex_icons = {"All": "👥", "Male": "👨", "Female": "👩"}
    sex_mapping = {"All": "All", "Male": "M", "Female": "F"}
    
    selected_sex_display = st.sidebar.radio(
        "",
        sex_options,
        format_func=lambda x: f"{sex_icons[x]} {x}",
        horizontal=True
    )
    selected_sex = sex_mapping[selected_sex_display]
    
    st.sidebar.markdown("---")
    
    # Real-time statistics panel
    _render_live_statistics(data, selected_country, selected_age_groups, selected_sex)
    
    return selected_country, selected_age_groups, selected_sex

def _render_live_statistics(data: pd.DataFrame, selected_country: str, 
                          selected_age_groups: List[str], selected_sex: str) -> None:
    """Render live statistics panel in sidebar"""
    st.sidebar.markdown("### 📈 Live Statistics")
    
    # Apply filters to data
    filtered_data = data.copy()
    if selected_country != "All":
        filtered_data = filtered_data[filtered_data['country'] == selected_country]
    if selected_sex != "All":
        filtered_data = filtered_data[filtered_data['sex'] == selected_sex]
    if selected_age_groups:
        filtered_data = filtered_data[filtered_data['age_group'].isin(selected_age_groups)]
    
    # Calculate statistics
    total_population = filtered_data['population'].sum()
    male_population = filtered_data[filtered_data['sex'] == 'M']['population'].sum()
    female_population = filtered_data[filtered_data['sex'] == 'F']['population'].sum()
    avg_age_population = _calculate_average_population(filtered_data)
    
    # Display metrics in modern cards
    st.sidebar.markdown(f"""
    <div style='background: #f0f2f6; padding: 15px; border-radius: 10px; margin: 10px 0;'>
        <div style='font-size: 1.8em; font-weight: bold; color: #1f77b4;'>{total_population:,}</div>
        <div style='font-size: 0.9em; color: #666;'>Total Population</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Gender distribution
    if total_population > 0:
        male_percent = (male_population / total_population) * 100
        female_percent = (female_population / total_population) * 100
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.metric("👨 Male", f"{male_percent:.1f}%")
        with col2:
            st.metric("👩 Female", f"{female_percent:.1f}%")
    
    # Age group count
    st.sidebar.metric("📊 Age Groups", len(selected_age_groups))
    
    # Data quality indicator
    data_coverage = (len(filtered_data) / len(data)) * 100 if len(data) > 0 else 0
    st.sidebar.progress(data_coverage / 100)
    st.sidebar.caption(f"Data coverage: {data_coverage:.1f}%")
    
    # Quick insights
    if total_population > 0:
        if male_population > female_population * 1.1:
            st.sidebar.info("♂️ Male-skewed population")
        elif female_population > male_population * 1.1:
            st.sidebar.info("♀️ Female-majority population")
        else:
            st.sidebar.success("⚖️ Balanced gender distribution")

def _calculate_average_population(data: pd.DataFrame) -> float:
    """Calculate average population per age group"""
    if len(data) == 0:
        return 0
    return data['population'].mean()