# Visualizing Urban Areas: Smart Residential Real Estate Analysis

## Project Overview
The project goal is divide the city into meaningful districts taking into account nearby restaurants, business centers, residential buildings etc. Look at the intersections of these neighborhoods and show for what purposes which place in the city to choose. Also, we will include the weather conditions like air pollution. All this information will be useful for different purposes of living(travelling, working travel, future living etc). 

## Features
- Interactive city map visualization
- Neighborhood analysis:
  - Real estate class classification
  - What is in the area of neighborhood(houses, theatr etc.)
  - Environmental factors (for example, air pollution)
  - Transportation accessibility
- Recommendation for purpose of neighborhood
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
- **Upper Class**: Penthouses, large apartments in skyscrapers
- **Middle Class**: Hotels, apartments in towers, proximity to sports centers and highways
- **Lower Class**: Areas near schools, public transportation, supermarkets, outside city center, parking

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
   - Openrouteservice
   - Airbnb dataset processing
    
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

## Getting Started

### Installation

1. **Clone the Repository**
   ```bash
   git clone [[repository-url]](https://github.com/Data-Wrangling-and-Visualisation/visualizing_urban_areas)
   cd visualizing_urban_areas
   ```

2. **Set Up Python Environment**
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Set Up Frontend**
   ```bash
   cd front
   npm install
   ```

### Running the Project

1. **Backend**
   ```bash
   # Start FastAPI server
   uvicorn app.main:app --reload
   ```

2. **Frontend**
   ```bash
   cd front
   npm run dev
   ```

3. **Application**
   - Frontend: http://localhost:3000
   - API Documentation: http://localhost:8000/docs

### Data Collection and Processing

1. **Airbnb Dataset**
   ```bash
   python scripts/airbnb_preprocessing.py
   ```

2. **Google Maps Data**
   ```bash
   python scripts/DataCollector.py
   ```

3. **Process and Store Data**
   ```bash
   scripts/data_preparation.sh
   ```

4. **Get city coordinates**
   ```bash
   python scripts/city_coordinates.py
   ```

5. **To elasticsearch**
   ```bash
   python scripts/index_clusters_to_elasticsearch.py
   python scripts/index_to_elasticsearch.py
   python scripts/scraping.py
   ```
