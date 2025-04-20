# Visualizing Urban Areas: Smart Residential Real Estate Analysis

## Project Overview
This project aims to create an intelligent system for analyzing and visualizing urban areas to help users make informed decisions about residential real estate choices. By combining data from Airbnb listings and Google Maps API, we provide insights into different city districts based on various factors including amenities, transportation, and environmental conditions.

## Features
- Interactive city map visualization with district classification
- Comprehensive neighborhood analysis including:
  - Residential real estate types
  - Nearby amenities and facilities
  - Environmental factors (air pollution, etc.)
  - Transportation accessibility
- Smart property recommendations based on user preferences
- Multi-city support with dynamic data collection

## Dataset Sources
1. **Airbnb Dataset**
   - Property descriptions (name, summary, neighborhood)
   - Ordinal features (bathrooms, bedrooms, capacity, review scores)
   - Continuous features (price, square footage, review frequency)
   - Location data (transit information, coordinates)
   - Additional information (photos, host profiles, reviews)

2. **Google Maps API**
   - Neighborhood characteristics
   - Points of interest
   - Transportation routes
   - Environmental data

## Residential Real Estate Classification
### Property Types
- **Elite Class**: Penthouses, large apartments in skyscrapers
- **Upper Class**: Hotels, apartments in towers, proximity to sports centers and highways
- **Middle Class**: Areas near schools, public transportation, supermarkets, outside city center

### Area Types
- Downtown (skyscrapers, luxury shopping)
- University (student housing, colleges)
- Nature (parks, water bodies, recreational areas)
- Ethnic (cultural and religious centers)
- Tourist (landmarks, museums, events)
- Tech Hub (coworking spaces, tech offices)
- Industrial (railways, highways, factories)
- Dining (cafes, restaurants, bakeries)
- Business (office towers)
- Nightlife (bars, clubs, entertainment)

## Technical Architecture
1. **Data Collection**
   - Google Maps API integration
   - Airbnb dataset processing
   - Hadoop-based cloud storage

2. **Data Processing**
   - Data cleaning and preprocessing (Pandas)
   - Exploratory data analysis (IPython, Matplotlib/Seaborn)
   - Clustering and classification algorithms

3. **Backend**
   - FastAPI RESTful API
   - JSON data delivery
   - Multi-city support

4. **Frontend**
   - Interactive map visualization (D3.js)
   - User-friendly interface
   - Dynamic data updates

## Project Timeline
1. **Week 1**: Project setup, dataset gathering, cloud storage preparation
2. **Week 2**: Residential real estate type definition and refinement
3. **Week 3**: Data clustering and validation
4. **Week 4**: Neighborhood data integration and verification
5. **Week 5**: Google Maps API data collection pipeline
6. **Week 6**: Dataset integration and pipeline testing
7. **Week 7**: FastAPI backend development and testing
8. **Week 8**: Deployment and documentation

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Node.js 14.x or higher
- Docker and Docker Compose
- Google Maps API key
- Hadoop cluster access (or local setup)

### Installation

1. **Clone the Repository**
   ```bash
   git clone [repository-url]
   cd visualizing_urban_areas
   ```

2. **Set Up Python Environment**
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install Python dependencies
   pip install -r requirements.txt
   ```

3. **Set Up Frontend**
   ```bash
   cd frontend
   npm install
   ```

4. **Configure Environment Variables**
   Create a `.env` file in the root directory with the following variables:
   ```
   GOOGLE_MAPS_API_KEY=your_api_key_here
   AIRBNB_DATASET_PATH=path_to_airbnb_dataset
   HADOOP_CONNECTION_STRING=your_hadoop_connection_string
   ```

### Running the Project

1. **Start Backend Services**
   ```bash
   # Start FastAPI server
   uvicorn app.main:app --reload
   ```

2. **Start Frontend Development Server**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Access the Application**
   - Frontend: http://localhost:3000
   - API Documentation: http://localhost:8000/docs

### Data Collection and Processing

1. **Prepare Airbnb Dataset**
   ```bash
   python scripts/prepare_airbnb_data.py
   ```

2. **Collect Google Maps Data**
   ```bash
   python scripts/collect_google_maps_data.py
   ```

3. **Process and Store Data**
   ```bash
   python scripts/process_and_store_data.py
   ```

### Development Workflow

1. **Data Analysis**
   - Use Jupyter notebooks in the `notebooks/` directory for exploratory data analysis
   - Run clustering algorithms to classify areas
   - Validate results using the validation scripts

2. **API Development**
   - Add new endpoints in `app/routers/`
   - Update data models in `app/models/`
   - Test API endpoints using the interactive docs

3. **Frontend Development**
   - Add new components in `frontend/src/components/`
   - Update map visualizations in `frontend/src/visualizations/`
   - Test UI changes using the development server

### Testing

1. **Run Python Tests**
   ```bash
   pytest tests/
   ```

2. **Run Frontend Tests**
   ```bash
   cd frontend
   npm test
   ```

### Troubleshooting

Common issues and solutions:
1. **API Key Issues**
   - Ensure your Google Maps API key has the necessary permissions
   - Check if the key is properly set in the `.env` file

2. **Data Processing Errors**
   - Verify the Airbnb dataset path is correct
   - Check Hadoop connection settings
   - Ensure all required Python packages are installed

3. **Frontend Build Issues**
   - Clear node_modules and reinstall dependencies
   - Check for version conflicts in package.json

## Dependencies
- Python 3.x
- FastAPI
- Pandas
- D3.js
- Google Maps API
- Hadoop
- Matplotlib/Seaborn
