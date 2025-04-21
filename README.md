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

1. **Clone the Repository**
   ```bash
   git clone [[repository-url]](https://github.com/Data-Wrangling-and-Visualisation/visualizing_urban_areas)
   cd visualizing_urban_areas
   ```

2. **Setup .env and scripts/.env with .env.example**

3. **Just run start.sh**
   ```bash
   bash start.sh
   ```
