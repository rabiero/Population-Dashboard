# WorldPop Population Dashboard

A comprehensive data pipeline and interactive dashboard for analyzing age- and sex-structured population data from WorldPop for Kenya and Uganda. This project transforms complex spatial datasets into actionable insights for public health planning and resource allocation.

## 📋 Project Overview

The WorldPop Population Dashboard provides:

- **Data Pipeline**: Automated processing of WorldPop 2025 raster data
- **District-Level Analysis**: Population summaries using GADM administrative boundaries  
- **Interactive Dashboard**: Filterable visualizations for country, age group, and sex
- **Public Health Insights**: Automated analysis and service planning recommendations

### Key Features

- 🌍 **Multi-country support**: Kenya (KEN) and Uganda (UGA)
- 👥 **Age-sex disaggregation**: 17 age groups, male/female breakdown
- 🗺️ **Spatial analysis**: District-level population mapping
- 📊 **Interactive visualizations**: Choropleth maps, age-sex pyramids, summary charts
- 🏥 **Public health context**: Automated insights and service recommendations

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended for large datasets)
- 2GB free disk space

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd population-dashboard
   ```

2. **Create virtual environment**
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up project structure**
   ```bash
   # Create necessary directories
   mkdir -p assets/gadm outputs cache
   ```

### Running the Dashboard

1. **Start the dashboard**
   ```bash
   streamlit run dashboard/app.py
   ```

2. **Open your browser**
   - Navigate to: `http://localhost:8501`
   - The dashboard will load with sample data

3. **Explore the data**
   - Use sidebar filters for country, age groups, and sex
   - View public health insights and visualizations
   - Analyze population patterns and service recommendations

## 🏗️ Project Structure

```
population-dashboard/
├── dashboard/                 # Streamlit dashboard application
│   ├── app.py               # Main dashboard application
│   ├── filters.py           # UI filter components
│   ├── charts.py            # Plotly visualization functions
│   └── text_blocks.py       # Public health insights generator
├── data_pipeline/           # Data processing modules
│   ├── config.py           # Configuration and constants
│   ├── load_rasters.py     # WorldPop raster data loader
│   ├── extract_metadata.py # Metadata extraction utilities
│   ├── summarize_by_district.py # District-level aggregation
│   ├── cache_utils.py      # Caching system for performance
│   └── utils.py            # Shared utility functions
├── tests/                   # Test suite
│   ├── test_load_rasters.py
│   ├── test_extract_metadata.py
│   ├── test_summarize_by_district.py
│   ├── test_cache_utils.py
│   ├── test_dashboard.py
│   └── run_tests.py
├── assets/                  # Static data files
│   └── gadm/               # GADM administrative boundaries
├── outputs/                 # Generated outputs and results
├── cache/                   # Cached data files
├── run_pipeline.py         # Main pipeline execution script
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 📊 Data Pipeline

### Running the Full Pipeline

The data pipeline processes WorldPop raster data and generates district-level summaries:

```bash
# Run with default settings (both countries, all age groups)
python run_pipeline.py

# Run with specific options
python run_pipeline.py --countries KEN --age-groups 0_4 5_9 --sex-options M --no-cache --verbose
```

### Pipeline Options

- `--countries`: Countries to process (KEN, UGA) - default: both
- `--age-groups`: Specific age groups to process - default: all
- `--sex-options`: Sex options (M, F) - default: both  
- `--no-cache`: Disable caching for fresh data download
- `--verbose`: Enable detailed logging

### Pipeline Outputs

The pipeline generates:

- `outputs/combined_population_summary.csv`: District-level population data
- `outputs/demographic_indicators.csv`: Calculated demographic metrics
- `outputs/metadata_summary.json`: Processing metadata and statistics
- `outputs/raster_metadata.csv`: Raster file information

## 🧪 Testing

### Install Test Dependencies

```bash
pip install pytest pytest-mock pytest-cov
```

### Running Tests

```bash
# Run all tests
python tests/run_tests.py

# Run specific test module
python tests/run_tests.py --module load_rasters

# Run with pytest directly
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=data_pipeline --cov-report=html
```

### Test Coverage

The test suite covers:
- Raster data loading and validation
- Metadata extraction and parsing
- District-level summarization
- Cache system functionality
- Dashboard components and filters

## 🔧 Configuration

### Data Sources

- **WorldPop Data**: Age and sex structured population rasters (2025 projection)
- **GADM Boundaries**: Administrative level 2 boundaries for Kenya and Uganda
- **Spatial Resolution**: 1km unconstrained (1km_ua/constrained/)

### Environment Setup

The project uses configuration in `data_pipeline/config.py`:

- Data URLs and file paths
- Age groups and sex options
- Cache settings (24-hour default)
- Output directories

## 🎯 Usage Guide

### Dashboard Features

1. **Data Filtering**
   - Select country: Kenya, Uganda, or both
   - Choose age groups: 0-4 to 80+ years
   - Filter by sex: Male, Female, or both

2. **Visualizations**
   - **Choropleth Maps**: Population distribution by district
   - **Age-Sex Pyramids**: Population structure analysis
   - **Summary Charts**: Population by age and sex

3. **Public Health Insights**
   - Automated demographic analysis
   - Service planning recommendations
   - Key indicator calculations

### Public Health Applications

- **Education Planning**: Identify areas needing school infrastructure
- **Healthcare Services**: Target maternal-child health programs
- **Economic Development**: Workforce planning and job creation
- **Social Services**: Elderly care and social protection programs

## 🔄 Data Flow

1. **Data Ingestion**: Download WorldPop raster files
2. **Processing**: Extract metadata and validate data
3. **Spatial Analysis**: Aggregate population by districts
4. **Summary Generation**: Calculate demographic indicators
5. **Visualization**: Interactive dashboard with filters

## 🛠️ Development

### Adding New Countries

1. Add country code to `COUNTRIES` in `data_pipeline/config.py`
2. Download corresponding GADM boundaries to `assets/gadm/`
3. Update country-specific configurations

### Extending Age Groups

Modify `AGE_GROUPS` in `data_pipeline/config.py` to include additional age brackets.

### Custom Visualizations

Add new chart functions in `dashboard/charts.py` and integrate into `dashboard/app.py`.

## 📈 Performance Optimization

- **Caching System**: Redundant downloads with 24-hour cache
- **Lazy Loading**: Data loaded on-demand in dashboard
- **Efficient Aggregation**: Optimized spatial operations
- **Memory Management**: Large dataset handling strategies

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is designed for academic and public health applications.

## 🆘 Troubleshooting

### Common Issues

1. **Memory Errors with Large Datasets**
   - Use specific age groups instead of all
   - Process one country at a time
   - Increase system RAM if possible

2. **Network Connectivity for Data Download**
   - Check internet connection
   - Use `--no-cache` to force fresh download
   - Verify WorldPop service availability

3. **Dashboard Loading Issues**
   - Clear browser cache
   - Restart Streamlit server
   - Check port 8501 availability

### Getting Help

- Check the `outputs/pipeline.log` for detailed error information
- Verify all dependencies are installed correctly
- Ensure sufficient disk space for cache and outputs


## 🙏 Acknowledgments

- **WorldPop**: Population data source
- **GADM**: Administrative boundaries
- **Streamlit**: Dashboard framework
- **Plotly**: Visualization library

---

**Note**: This project uses sample data for demonstration. For production use with real WorldPop data, ensure proper data licensing and attribution.# Population-Dashboard
