import pandas as pd
import streamlit as st
from typing import Tuple, List, Optional

def get_public_health_insights(data: pd.DataFrame, selected_country: str, 
                             selected_age_groups: List[str], selected_sex: str) -> None:
    """Generate modern, visually appealing public health insights"""
    
    if data.empty:
        st.error("🚫 No data available for current filters")
        st.info("Try adjusting country, age groups, or sex filters")
        return
    
    # Calculate metrics
    metrics = _calculate_demographic_metrics(data)
    
    # Modern layout with tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "🎯 Key Insights", "📊 Metrics", "🏥 Recommendations"])
    
    with tab1:
        _render_population_overview(selected_country, metrics['total_population'])
        _render_quick_glance(metrics)
    
    with tab2:
        _render_key_insights(metrics, selected_age_groups)
    
    with tab3:
        _render_detailed_metrics(metrics)
    
    with tab4:
        _render_actionable_recommendations(metrics, selected_age_groups)

def _calculate_demographic_metrics(data: pd.DataFrame) -> dict:
    """Calculate all demographic metrics"""
    total_population = data['population'].sum()
    
    # Age groups
    child_groups = ['0-4', '5-9', '10-14']
    working_groups = ['15-19', '20-24', '25-29', '30-34', '35-39', '40-44', '45-49', '50-54', '55-59']
    elderly_groups = ['60-64', '65-69', '70-74', '75-79', '80+']
    
    child_pop = data[data['age_group'].isin(child_groups)]['population'].sum()
    working_pop = data[data['age_group'].isin(working_groups)]['population'].sum()
    elderly_pop = data[data['age_group'].isin(elderly_groups)]['population'].sum()
    
    male_pop = data[data['sex'] == 'M']['population'].sum()
    female_pop = data[data['sex'] == 'F']['population'].sum()
    
    return {
        'total_population': total_population,
        'child_percentage': (child_pop / total_population * 100) if total_population > 0 else 0,
        'working_percentage': (working_pop / total_population * 100) if total_population > 0 else 0,
        'elderly_percentage': (elderly_pop / total_population * 100) if total_population > 0 else 0,
        'sex_ratio': (male_pop / female_pop) if female_pop > 0 else 0,
        'male_population': male_pop,
        'female_population': female_pop,
        'dependency_ratio': ((child_pop + elderly_pop) / working_pop) if working_pop > 0 else 0
    }

def _render_population_overview(selected_country: str, total_population: int) -> None:
    """Render modern population overview"""
    st.subheader("🌍 Population Overview")
    
    country_display = "Kenya & Uganda" if selected_country == "All" else selected_country
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; border-radius: 10px; color: white;'>
            <h3 style='margin:0;'>{country_display}</h3>
            <h1 style='margin:10px 0; font-size: 2.5em;'>{total_population:,}</h1>
            <p style='margin:0;'>Total Population</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.metric("Households", f"{(total_population / 4.5):,.0f}", 
                 help="Estimated based on average household size of 4.5")
    
    with col3:
        st.metric("Density", "Medium", "Urban focus", 
                 help="Population concentration level")

def _render_quick_glance(metrics: dict) -> None:
    """Render quick glance indicators"""
    st.subheader("🔍 Quick Glance")
    
    cols = st.columns(4)
    
    # Child population indicator
    with cols[0]:
        child_color = "#FF6B6B" if metrics['child_percentage'] > 35 else "#4ECDC4"
        st.markdown(f"""
        <div style='text-align: center; padding: 15px; background-color: {child_color}20; 
                    border-radius: 10px; border-left: 4px solid {child_color}'>
            <h3 style='margin:0; color: {child_color};'>{metrics['child_percentage']:.1f}%</h3>
            <p style='margin:0; font-size: 0.8em;'>Children (0-14)</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Workforce indicator
    with cols[1]:
        work_color = "#45B7D1" if metrics['working_percentage'] > 60 else "#F7B731"
        st.markdown(f"""
        <div style='text-align: center; padding: 15px; background-color: {work_color}20; 
                    border-radius: 10px; border-left: 4px solid {work_color}'>
            <h3 style='margin:0; color: {work_color};'>{metrics['working_percentage']:.1f}%</h3>
            <p style='margin:0; font-size: 0.8em;'>Workforce (15-59)</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Elderly indicator
    with cols[2]:
        elder_color = "#9966CC" if metrics['elderly_percentage'] > 10 else "#A0A0A0"
        st.markdown(f"""
        <div style='text-align: center; padding: 15px; background-color: {elder_color}20; 
                    border-radius: 10px; border-left: 4px solid {elder_color}'>
            <h3 style='margin:0; color: {elder_color};'>{metrics['elderly_percentage']:.1f}%</h3>
            <p style='margin:0; font-size: 0.8em;'>Elderly (60+)</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Sex ratio indicator
    with cols[3]:
        ratio_color = "#4CAF50" if 0.95 <= metrics['sex_ratio'] <= 1.05 else "#FF9800"
        st.markdown(f"""
        <div style='text-align: center; padding: 15px; background-color: {ratio_color}20; 
                    border-radius: 10px; border-left: 4px solid {ratio_color}'>
            <h3 style='margin:0; color: {ratio_color};'>{metrics['sex_ratio']:.2f}</h3>
            <p style='margin:0; font-size: 0.8em;'>Sex Ratio</p>
        </div>
        """, unsafe_allow_html=True)

def _render_key_insights(metrics: dict, selected_age_groups: List[str]) -> None:
    """Render key insights with modern cards"""
    st.subheader("💡 Key Insights")
    
    insights = []
    
    # Population structure insights
    if metrics['child_percentage'] > 35:
        insights.append(("👶 Youthful Population", 
                        "High youth dependency ratio indicates need for education and child healthcare expansion", 
                        "success"))
    elif metrics['elderly_percentage'] > 12:
        insights.append(("👵 Aging Society", 
                        "Growing elderly population requires geriatric care and social security systems", 
                        "info"))
    
    # Workforce insights
    if metrics['working_percentage'] > 65:
        insights.append(("💼 Demographic Dividend", 
                        "Large working-age population presents economic growth opportunity", 
                        "success"))
    elif metrics['dependency_ratio'] > 0.7:
        insights.append(("⚖️ High Dependency", 
                        "High dependency ratio may strain social services and economic growth", 
                        "warning"))
    
    # Gender insights
    if metrics['sex_ratio'] > 1.1:
        insights.append(("🚹 Gender Imbalance", 
                        "Male-skewed population may indicate migration patterns or social factors", 
                        "warning"))
    elif metrics['sex_ratio'] < 0.9:
        insights.append(("🚺 Female Majority", 
                        "Female-majority population may reflect specific regional characteristics", 
                        "info"))
    
    # Display insights in modern cards
    for title, description, type in insights:
        if type == "success":
            st.success(f"**{title}**\n\n{description}")
        elif type == "warning":
            st.warning(f"**{title}**\n\n{description}")
        elif type == "info":
            st.info(f"**{title}**\n\n{description}")

def _render_detailed_metrics(metrics: dict) -> None:
    """Render detailed metrics with progress bars"""
    st.subheader("📊 Detailed Analysis")
    
    # Age structure progress bars
    st.write("**Age Structure Distribution**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("Children (0-14)")
        st.progress(metrics['child_percentage'] / 100)
        st.caption(f"{metrics['child_percentage']:.1f}%")
    
    with col2:
        st.write("Working Age (15-59)")
        st.progress(metrics['working_percentage'] / 100)
        st.caption(f"{metrics['working_percentage']:.1f}%")
    
    with col3:
        st.write("Elderly (60+)")
        st.progress(metrics['elderly_percentage'] / 100)
        st.caption(f"{metrics['elderly_percentage']:.1f}%")
    
    # Sex distribution
    st.write("**Gender Distribution**")
    sex_col1, sex_col2 = st.columns(2)
    
    with sex_col1:
        male_percent = (metrics['male_population'] / metrics['total_population'] * 100)
        st.metric("Male Population", f"{male_percent:.1f}%", 
                 f"{metrics['male_population']:,} people")
    
    with sex_col2:
        female_percent = (metrics['female_population'] / metrics['total_population'] * 100)
        st.metric("Female Population", f"{female_percent:.1f}%", 
                 f"{metrics['female_population']:,} people")
    
    # Dependency ratio
    st.write("**Dependency Analysis**")
    dep_col1, dep_col2, dep_col3 = st.columns(3)
    
    with dep_col1:
        st.metric("Dependency Ratio", f"{metrics['dependency_ratio']:.2f}",
                 "Dependents per worker")
    
    with dep_col2:
        st.metric("Youth Dependency", f"{(metrics['child_percentage'] / metrics['working_percentage']):.2f}",
                 "Children per worker")
    
    with dep_col3:
        st.metric("Elderly Dependency", f"{(metrics['elderly_percentage'] / metrics['working_percentage']):.2f}",
                 "Elderly per worker")

def _render_actionable_recommendations(metrics: dict, selected_age_groups: List[str]) -> None:
    """Render actionable recommendations"""
    st.subheader("🎯 Actionable Recommendations")
    
    # Priority recommendations based on population structure
    if metrics['child_percentage'] > 30:
        with st.expander("🎓 **HIGH PRIORITY**: Education & Child Services", expanded=True):
            st.write("""
            **Immediate Actions:**
            • Expand primary school infrastructure in high-density areas
            • Scale up early childhood development programs
            • Strengthen teacher training and recruitment
            
            **Healthcare Initiatives:**
            • Enhance immunization coverage to >95%
            • Implement school-based health screening
            • Develop adolescent health clinics
            """)
    
    if metrics['working_percentage'] > 60:
        with st.expander("💼 **MEDIUM PRIORITY**: Economic Development"):
            st.write("""
            **Workforce Development:**
            • Create vocational training centers
            • Support small business incubation
            • Develop digital skills programs
            
            **Employment Strategy:**
            • Partner with private sector for job creation
            • Enhance labor market information systems
            • Promote entrepreneurship among youth
            """)
    
    if metrics['elderly_percentage'] > 8:
        with st.expander("🏥 **MEDIUM PRIORITY**: Elderly Care"):
            st.write("""
            **Healthcare Services:**
            • Establish geriatric care units in hospitals
            • Train community health workers in elderly care
            • Develop chronic disease management programs
            
            **Social Support:**
            • Create community day care centers
            • Implement elderly nutrition programs
            • Strengthen social pension systems
            """)
    
    # Always show these foundational recommendations
    with st.expander("🏛️ **FOUNDATIONAL**: Public Health Infrastructure"):
        st.write("""
        **Essential Services:**
        • Strengthen primary healthcare centers
        • Improve water and sanitation facilities
        • Enhance disease surveillance systems
        
        **Community Programs:**
        • Train community health workers
        • Implement health education campaigns
        • Develop emergency response capacity
        """)
    
    # Specialized programs based on selected age groups
    if selected_age_groups and any(age in ['0-4', '5-9'] for age in selected_age_groups):
        with st.expander("👶 **SPECIALIZED**: Early Childhood Focus"):
            st.write("""
            **Early Intervention:**
            • Scale up integrated management of childhood illnesses
            • Implement growth monitoring programs
            • Strengthen parental education initiatives
            """)