import streamlit as st
import pandas as pd

def create_filters(data):
    """
    Create interactive filters for the dashboard
    
    Returns:
        tuple: (selected_country, selected_age_groups, selected_sex)
    """
    # Country filter
    countries = ["All"] + sorted(data['country'].unique().tolist())
    selected_country = st.sidebar.selectbox(
        "Select Country",
        countries,
        index=0,
        help="Filter data by country"
    )
    
    # Age group filter
    age_groups = sorted(data['age_group'].unique().tolist())
    selected_age_groups = st.sidebar.multiselect(
        "Select Age Groups",
        age_groups,
        default=age_groups,
        help="Select one or more age groups to display"
    )
    
    # Sex filter
    sex_options = ["All", "Male", "Female"]
    sex_mapping = {"All": "All", "Male": "M", "Female": "F"}
    
    selected_sex_display = st.sidebar.selectbox(
        "Select Sex",
        sex_options,
        index=0,
        help="Filter data by sex"
    )
    selected_sex = sex_mapping[selected_sex_display]
    
    # Add some informative metrics in sidebar
    st.sidebar.markdown("---")
    st.sidebar.header("ℹ️ Data Summary")
    
    if selected_country != "All":
        country_data = data[data['country'] == selected_country]
        total_country_pop = country_data['population'].sum()
        st.sidebar.metric(f"Total {selected_country} Population", f"{total_country_pop:,}")
    else:
        total_pop = data['population'].sum()
        st.sidebar.metric("Total Population", f"{total_pop:,}")
    
    # Available age groups info
    if selected_age_groups:
        st.sidebar.info(f"Showing {len(selected_age_groups)} age groups")
    
    return selected_country, selected_age_groups, selected_sex