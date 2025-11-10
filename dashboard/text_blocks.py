import pandas as pd
import streamlit as st

def get_public_health_insights(data, selected_country, selected_age_groups, selected_sex):
    """
    Generate public health insights based on the filtered data
    
    Returns:
        Formatted insights with Streamlit components
    """
    if data.empty:
        st.warning("No data available for the selected filters. Please adjust your selection.")
        return
    
    # Calculate key metrics
    total_population = data['population'].sum()
    
    # Age group calculations
    child_population = data[data['age_group'].isin(['0-4', '5-9', '10-14'])]['population'].sum()
    working_age_population = data[data['age_group'].isin(['15-19', '20-24', '25-29', '30-34', '35-39', '40-44', '45-49', '50-54', '55-59'])]['population'].sum()
    elderly_population = data[data['age_group'].isin(['60-64', '65-69', '70-74', '75-79', '80+'])]['population'].sum()
    
    child_percentage = (child_population / total_population * 100) if total_population > 0 else 0
    working_age_percentage = (working_age_population / total_population * 100) if total_population > 0 else 0
    elderly_percentage = (elderly_population / total_population * 100) if total_population > 0 else 0
    
    # Sex ratio
    male_population = data[data['sex'] == 'M']['population'].sum()
    female_population = data[data['sex'] == 'F']['population'].sum()
    sex_ratio = (male_population / female_population) if female_population > 0 else 0
    
    # Create organized layout
    _create_population_overview(selected_country, total_population)
    _create_key_findings(child_percentage, working_age_percentage, elderly_percentage, sex_ratio)
    _create_demographic_indicators(child_percentage, working_age_percentage, elderly_percentage, sex_ratio)
    _create_service_recommendations(child_percentage, working_age_percentage, elderly_percentage, selected_age_groups)

def _create_population_overview(selected_country, total_population):
    """Create population overview section"""
    st.subheader("📋 Population Overview")
    
    country_text = selected_country if selected_country != "All" else "Kenya and Uganda"
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write(f"**Region:** {country_text}")
        st.write(f"**Total Population:** {total_population:,}")
    with col2:
        if total_population > 0:
            st.metric("Population Size", f"{total_population:,}")

def _create_key_findings(child_percentage, working_age_percentage, elderly_percentage, sex_ratio):
    """Create key findings section with visual indicators"""
    st.subheader("🔍 Key Findings")
    
    # Create columns for key insights
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if child_percentage > 30:
            st.success("👶 **Youthful Population**")
            st.write("High proportion of children indicates need for expanded educational and child health services.")
        elif child_percentage < 20:
            st.info("👴 **Aging Population**")
            st.write("Lower youth proportion suggests transitioning demographics with implications for healthcare.")
    
    with col2:
        if working_age_percentage > 60:
            st.success("💼 **Strong Workforce**")
            st.write("Large working-age population presents economic opportunities but requires employment planning.")
        elif working_age_percentage < 50:
            st.warning("👥 **Workforce Challenges**")
            st.write("Smaller working-age population may indicate economic or migration challenges.")
    
    with col3:
        if elderly_percentage > 10:
            st.info("🏥 **Aging Society**")
            st.write("Significant elderly population highlights need for geriatric healthcare services.")
        if sex_ratio > 1.05:
            st.warning("⚖️ **Gender Imbalance**")
            st.write("Male-dominant ratio may indicate specific social or migration patterns.")

def _create_demographic_indicators(child_percentage, working_age_percentage, elderly_percentage, sex_ratio):
    """Create demographic indicators section with metrics"""
    st.subheader("📊 Demographic Indicators")
    
    # Create metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Child Population (0-14)",
            f"{child_percentage:.1f}%",
            help="Percentage of population aged 0-14 years"
        )
    
    with col2:
        st.metric(
            "Working Age (15-59)",
            f"{working_age_percentage:.1f}%",
            help="Percentage of population aged 15-59 years"
        )
    
    with col3:
        st.metric(
            "Elderly Population (60+)",
            f"{elderly_percentage:.1f}%",
            help="Percentage of population aged 60+ years"
        )
    
    with col4:
        st.metric(
            "Sex Ratio (M/F)",
            f"{sex_ratio:.2f}",
            help="Ratio of males to females in the population"
        )
    
    # Add age pyramid explanation
    st.info("💡 **Age Structure Interpretation:**")
    if child_percentage > 40:
        st.write("• **Expansive Pyramid**: High birth rates, young population")
        st.write("• **Implications**: High dependency ratio, need for child services")
    elif elderly_percentage > 15:
        st.write("• **Constrictive Pyramid**: Aging population, lower birth rates")
        st.write("• **Implications**: Healthcare for elderly, pension systems")
    else:
        st.write("• **Stationary Pyramid**: Balanced age distribution")
        st.write("• **Implications**: Stable workforce, balanced service needs")

def _create_service_recommendations(child_percentage, working_age_percentage, elderly_percentage, selected_age_groups):
    """Create service planning recommendations section"""
    st.subheader("🏛️ Service Planning Recommendations")
    
    # Education and Child Services
    if child_percentage > 25:
        with st.expander("🎓 Education and Child Services", expanded=True):
            st.write("**Priority Actions:**")
            st.write("• Expand primary school infrastructure and teaching capacity")
            st.write("• Strengthen early childhood development programs")
            st.write("• Enhance vocational training for adolescents")
            
            st.write("**Health Services:**")
            st.write("• Scale up immunization coverage and outreach programs")
            st.write("• Improve maternal and child healthcare facilities")
            st.write("• Implement school-based health and nutrition programs")
    
    # Healthcare and Social Services
    with st.expander("🏥 Healthcare and Social Services"):
        st.write("**Primary Healthcare:**")
        st.write("• Strengthen community health worker programs")
        st.write("• Expand access to essential medicines and services")
        
        if elderly_percentage > 8:
            st.write("**Geriatric Care:**")
            st.write("• Develop specialized elderly healthcare services")
            st.write("• Establish community-based elderly support programs")
        
        st.write("**Reproductive Health:**")
        st.write("• Enhance family planning and reproductive health services")
        st.write("• Improve adolescent-friendly health services")
    
    # Economic Development
    if working_age_percentage > 55:
        with st.expander("💼 Economic Development and Employment"):
            st.write("**Workforce Development:**")
            st.write("• Create vocational training and skills development programs")
            st.write("• Support entrepreneurship and small business development")
            
            st.write("**Employment Strategies:**")
            st.write("• Develop job creation initiatives in key sectors")
            st.write("• Enhance labor market information systems")
    
    # Infrastructure and Social Protection
    with st.expander("🏗️ Infrastructure and Social Protection"):
        st.write("**Social Protection:**")
        st.write("• Strengthen social safety nets for vulnerable populations")
        st.write("• Implement targeted support for children and elderly")
        
        st.write("**Community Infrastructure:**")
        st.write("• Improve water, sanitation, and hygiene facilities")
        st.write("• Develop community centers and public spaces")
    
    # Special Programs
    if selected_age_groups and any(age in ['0-4', '5-9'] for age in selected_age_groups):
        with st.expander("👶 Early Childhood Development"):
            st.write("**Early Intervention:**")
            st.write("• Scale up integrated early childhood development programs")
            st.write("• Improve access to quality preschool education")
            st.write("• Strengthen parenting education and support")
    
    if selected_age_groups and any(age in ['15-19', '20-24'] for age in selected_age_groups):
        with st.expander("🎯 Youth and Adolescent Programs"):
            st.write("**Youth Development:**")
            st.write("• Establish youth centers and recreational facilities")
            st.write("• Implement comprehensive sexuality education")
            st.write("• Create youth employment and entrepreneurship programs")

def get_quick_insights(data):
    """Generate quick insights for dashboard overview"""
    if data.empty:
        return "No data available"
    
    total_population = data['population'].sum()
    child_population = data[data['age_group'].isin(['0-4', '5-9', '10-14'])]['population'].sum()
    child_percentage = (child_population / total_population * 100) if total_population > 0 else 0
    
    insights = []
    
    if child_percentage > 35:
        insights.append("High youth population - focus on education and child health")
    elif child_percentage < 20:
        insights.append("Aging population - prioritize elderly care services")
    
    if len(insights) == 0:
        insights.append("Balanced population structure - comprehensive planning needed")
    
    return " | ".join(insights)