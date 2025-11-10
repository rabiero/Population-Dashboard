import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def create_choropleth_map(data, selected_country):
    """
    Create a choropleth map showing population distribution by district
    
    Note: This uses sample district data. In production, this would use
    actual GADM GeoJSON boundaries and proper spatial joins.
    """
    # Aggregate data by district
    district_data = data.groupby(['country', 'district'])['population'].sum().reset_index()
    
    # Create sample coordinates for demonstration
    # In production, these would come from GADM GeoJSON files
    sample_coords = {
        'Nairobi': {'lat': -1.286389, 'lon': 36.817223},
        'Mombasa': {'lat': -4.0435, 'lon': 39.6682},
        'Kisumu': {'lat': -0.1022, 'lon': 34.7617},
        'Nakuru': {'lat': -0.3031, 'lon': 36.0800},
        'Eldoret': {'lat': 0.5143, 'lon': 35.2698},
        'Kampala': {'lat': 0.3476, 'lon': 32.5825},
        'Gulu': {'lat': 2.7663, 'lon': 32.3057},
        'Lira': {'lat': 2.2350, 'lon': 32.9097},
        'Mbale': {'lat': 1.0647, 'lon': 34.1794},
        'Jinja': {'lat': 0.4473, 'lon': 33.2026}
    }
    
    # Add coordinates to data
    district_data['lat'] = district_data['district'].map(lambda x: sample_coords.get(x, {}).get('lat', 0))
    district_data['lon'] = district_data['district'].map(lambda x: sample_coords.get(x, {}).get('lon', 0))
    
    # Filter by selected country if applicable
    if selected_country != "All":
        district_data = district_data[district_data['country'] == selected_country]
    
    # Create scatter map
    fig = px.scatter_mapbox(
        district_data,
        lat="lat",
        lon="lon",
        size="population",
        color="population",
        hover_name="district",
        hover_data={"population": True, "country": True},
        color_continuous_scale="Viridis",
        size_max=50,
        zoom=5,
        title="Population Distribution by District"
    )
    
    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r":0,"t":30,"l":0,"b":0},
        height=500
    )
    
    return fig

def create_age_sex_pyramid(data):
    """
    Create an age-sex population pyramid
    """
    if data.empty:
        return create_empty_figure("No data available for selected filters")
    
    # Prepare data for pyramid
    pyramid_data = data.groupby(['age_group', 'sex'])['population'].sum().reset_index()
    
    # Create separate dataframes for males and females
    males = pyramid_data[pyramid_data['sex'] == 'M'].sort_values('age_group')
    females = pyramid_data[pyramid_data['sex'] == 'F'].sort_values('age_group')
    
    # Create pyramid
    fig = go.Figure()
    
    # Add male bars (left side, negative values)
    fig.add_trace(go.Bar(
        y=males['age_group'],
        x=-males['population'],
        name='Male',
        orientation='h',
        marker_color='lightblue',
        hovertemplate='Male: %{x:,}<extra></extra>'
    ))
    
    # Add female bars (right side, positive values)
    fig.add_trace(go.Bar(
        y=females['age_group'],
        x=females['population'],
        name='Female',
        orientation='h',
        marker_color='lightpink',
        hovertemplate='Female: %{x:,}<extra></extra>'
    ))
    
    # Update layout for pyramid appearance
    fig.update_layout(
        title="Age-Sex Population Pyramid",
        barmode='overlay',
        xaxis=dict(
            title="Population",
            tickformat=",",
            tickvals=[-max(pyramid_data['population']), 0, max(pyramid_data['population'])],
            ticktext=[f"{max(pyramid_data['population']):,}", "0", f"{max(pyramid_data['population']):,}"]
        ),
        yaxis=dict(title="Age Group"),
        showlegend=True,
        height=500,
        bargap=0.1
    )
    
    return fig

def create_population_summary_chart(data):
    """
    Create a summary chart showing population by age group and sex
    """
    if data.empty:
        return create_empty_figure("No data available for selected filters")
    
    # Aggregate data
    summary_data = data.groupby(['age_group', 'sex'])['population'].sum().reset_index()
    
    # Create grouped bar chart
    fig = px.bar(
        summary_data,
        x='age_group',
        y='population',
        color='sex',
        barmode='group',
        title="Population by Age Group and Sex",
        labels={'population': 'Population', 'age_group': 'Age Group', 'sex': 'Sex'},
        color_discrete_map={'M': 'lightblue', 'F': 'lightpink'}
    )
    
    fig.update_layout(
        height=400,
        xaxis={'categoryorder': 'category ascending'},
        yaxis={'tickformat': ','}
    )
    
    return fig

def create_empty_figure(message):
    """Create an empty figure with a message"""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=16)
    )
    fig.update_layout(height=400)
    return fig