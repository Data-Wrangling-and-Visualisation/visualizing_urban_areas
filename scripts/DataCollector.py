import requests
import pandas as pd
from dotenv import load_dotenv
import os
from tqdm import tqdm
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("datacollector.log"),
        logging.StreamHandler()
    ]
)

load_dotenv()

class DataCollector:
    def __init__(self):
        logging.info("Initializing DataCollector class.")
        self.osm_mapping = {
            # AMENITY MAPPINGS
            'amenity': {
                # Nature
                'bbq': 'Nature', 'bench': 'Nature',
                # Ethnic
                'theatre': 'Ethnic', 'place_of_worship': 'Ethnic',
                # Tourist
                'cinema': 'Tourist', 'fountain': 'Tourist', 'stage': 'Tourist',
                'theater': 'Tourist', 'marketplace': 'Tourist', 'public_bath': 'Tourist',
                # Cafe street
                'cafe': 'Cafe street', 'fast_food': 'Cafe street', 'restaurant': 'Cafe street',
                # Nightlife
                'bar': 'Nightlife', 'biergarten': 'Nightlife', 'brothel': 'Nightlife',
                'casino': 'Nightlife', 'gambling': 'Nightlife', 'nightclub': 'Nightlife',
                'stripclub': 'Nightlife',
                # Elite r.e.
                'lounge': 'Elite r.e.',
                # Lower r.e.
                'prison': 'Lower r.e.', 'grave_yard': 'Lower r.e.'
            },
            
            # BUILDING MAPPINGS (handled differently as they need additional tag checks)
            'building': {
                # University
                'dormitory': 'University', 'college': 'University',
                'school': 'University', 'university': 'University',
                # Ethnic
                'religious': 'Ethnic', 'cathedral': 'Ethnic',
                'church': 'Ethnic', 'monastery': 'Ethnic',
                # Tourist
                'museum': 'Tourist', 'public': 'Tourist',
                'stadium': 'Tourist', 'grandstand': 'Tourist',
                'ship': 'Tourist', 'tower': 'Tourist',
                # Business center (handled in info_nearby_op)
                'office': 'Business center',
                # Elite r.e. (handled in info_nearby_op)
                'hotel': 'Elite r.e.',
                # Upper r.e. (handled in info_nearby_op)
                'apartments': 'Upper r.e.', 'commercial': 'Upper r.e.',
                'government': 'Upper r.e.',
                # Middle r.e. (handled in info_nearby_op)
                'residential': 'Middle r.e.', 'retail': 'Middle r.e.',
                'supermarket': 'Middle r.e.', 'civic': 'Middle r.e.',
                'parking': 'Middle r.e.', 'garages': 'Middle r.e.',
                # Lower r.e. (handled in info_nearby_op)
                'static_caravan': 'Lower r.e.', 'warehouse': 'Lower r.e.',
                'ruins': 'Lower r.e.',
                # cottage settlement
                'bungalow': 'cottage settlement', 'cabin': 'cottage settlement',
                'detached': 'cottage settlement', 'annexe': 'cottage settlement',
                'farm': 'cottage settlement', 'ger': 'cottage settlement',
                'house': 'cottage settlement', 'semidetached_house': 'cottage settlement',
                'terrace': 'cottage settlement'
            },
            
            # CLUB MAPPINGS
            'club': {
                # All tourist
                '*': 'Tourist'
            },
            
            # EDUCATION MAPPINGS
            'education': {
                # All university
                '*': 'University'
            },
            
            # HIGHWAY MAPPINGS
            'highway': {
                'living_street': 'Middle r.e.',
                'tertiary': 'cottage settlement',
                'residential': 'cottage settlement'
            },
            
            # LANDCOVER MAPPINGS
            'landcover': {
                # All nature
                '*': 'Nature'
            },
            
            # HISTORIC MAPPINGS
            'historic': {
                # All tourist
                '*': 'Tourist'
            },
            
            # LANDUSE MAPPINGS
            'landuse': {
                # All nature
                '*': 'Nature'
            },
            
            # LEISURE MAPPINGS
            'leisure': {
                'water_park': ['Nature', 'Tourist'],
                'stadium': ['Nature', 'Tourist'],
                'park': ['Nature', 'Tourist'],
                'picnic_table': ['Nature', 'Tourist'],
                'firepit': ['Nature', 'Tourist'],
                'beach_resort': ['Nature', 'Tourist'],
                'swimming_area': ['Nature', 'Tourist'],
                'outdoor_seating': 'Cafe street'
            },
            
            # MAN_MADE MAPPINGS
            'man_made': {
                'advertising': 'Tourist',
                'obelisk': 'Tourist',
                # All others are Lower r.e.
                '*': 'Lower r.e.'
            },
            
            # NATURAL MAPPINGS
            'natural': {
                # All nature
                '*': 'Nature'
            },
            
            # OFFICE MAPPINGS
            'office': {
                # All business center
                '*': 'Business center'
            },
            
            # SHOP MAPPINGS
            'shop': {
                # Downtown
                'boutique': 'Downtown', 'jewelry': 'Downtown',
                'leather': 'Downtown', 'shoes': 'Downtown',
                'watches': 'Downtown', 'perfumery': 'Downtown',
                # Cafe street
                'butcher': 'Cafe street', 'chocolate': 'Cafe street',
                'coffee': 'Cafe street', 'seafood': 'Cafe street',
                'alcohol': 'Cafe street',
                # Elite r.e.
                'boutique': 'Elite r.e.',
                # Upper r.e.
                'beauty': 'Upper r.e.', 'hairdresser': 'Upper r.e.',
                'massage': 'Upper r.e.',
                # Middle r.e.
                'bakery': 'Middle r.e.', 'convenience': 'Middle r.e.',
                'dairy': 'Middle r.e.', 'supermarket': 'Middle r.e.',
                'wholesale': 'Middle r.e.', 'mall': 'Middle r.e.',
                'chemist': 'Middle r.e.', 'doityourself': 'Middle r.e.',
                # Lower r.e.
                'second_hand': 'Lower r.e.', 'variety_store': 'Lower r.e.',
                'trade': 'Lower r.e.'
            },
            
            # TOURISM MAPPINGS
            'tourism': {
                'hotel': 'Upper r.e.',
                'hostel': 'Middle r.e.',
                'motel': 'Middle r.e.',
                # All others are Tourist
                '*': 'Tourist'
            },
            
            # WATERWAY MAPPINGS
            'waterway': {
                # All nature
                '*': 'Nature'
            }
        }

    def _get_mapped_category(self, osm_type, osm_value, tags=None):
        """Helper method to get the mapped category based on OSM type and value"""
        logging.debug(f"Getting mapped category for osm_type: {osm_type}, osm_value: {osm_value}, tags: {tags}")
        if osm_type not in self.osm_mapping:
            logging.warning(f"OSM type '{osm_type}' not found in mappings.")
            return None

        mapping = self.osm_mapping[osm_type]

        # Handle wildcard mappings
        if '*' in mapping and osm_value not in mapping:
            logging.debug(f"Using wildcard mapping for osm_type: {osm_type}, osm_value: {osm_value}")
            return mapping['*']

        # Handle specific value mappings
        if osm_value in mapping:
            logging.debug(f"Found specific mapping for osm_value: {osm_value}")
            return mapping[osm_value]

        # For building types that need additional tag checks
        if osm_type == 'building':
            if tags:
                # Check for Business center (office with specific material/height)
                if osm_value == 'office':
                    material = tags.get('building:material', '').lower()
                    height = float(tags.get('height', 0))
                    if material in ('glass', 'mirrored-glass') or height > 20:
                        return 'Business center'
                
                # Check for Elite r.e. (hotel or levels >20, specific material/height)
                if osm_value == 'hotel':
                    levels = int(tags.get('levels', 0))
                    material = tags.get('building:material', '').lower()
                    height = float(tags.get('height', 0))
                    if (levels > 20 or height > 60) or material in ('glass', 'mirrored-glass'):
                        return 'Elite r.e.'
                
                # Check for Upper class residential (tall residential buildings)
                if osm_value == 'residential':
                    levels = int(tags.get('levels', 0))
                    height = float(tags.get('height', 0))
                    if levels >= 10 or height >= 30:
                        return 'Upper'
                # Check for Middle class residential (medium height residential)
                    if 5 <= levels < 10 or 15 <= height < 30:
                        return 'Middle'
                # Check for Lower class residential (small residential)
                    if levels < 5 or height < 15:
                        return 'Lower'
                
                # Check for Cottage settlement (detached houses with landuse tags)
                if osm_value == 'house' and tags.get('detached', 'no') == 'yes':
                    landuse = tags.get('landuse', '').lower()
                    if landuse in ('residential', 'village', 'farmyard'):
                        return 'Cottage settlement'

        return None

    def info_nearby_op(self, latitude, longitude, radius, city=None):
        """Use Overpass API to search for POIs within circle
           https://wiki.openstreetmap.org/wiki/Overture_categories
           @params: city - use to read cached city data"""
        overpass_url = "https://overpass-api.de/api/interpreter"

        overpass_query = f"""
        [out:json];
        (
            node["amenity"](around:{radius},{latitude},{longitude});
            node["shop"](around:{radius},{latitude},{longitude});
            node["tourism"](around:{radius},{latitude},{longitude});
            node["building"](around:{radius},{latitude},{longitude});
            node["club"](around:{radius},{latitude},{longitude});
            node["education"](around:{radius},{latitude},{longitude});
            node["highway"](around:{radius},{latitude},{longitude});
            node["landcover"](around:{radius},{latitude},{longitude});
            node["historic"](around:{radius},{latitude},{longitude});
            node["landuse"](around:{radius},{latitude},{longitude});
            node["leisure"](around:{radius},{latitude},{longitude});
            node["man_made"](around:{radius},{latitude},{longitude});
            node["natural"](around:{radius},{latitude},{longitude});
            node["office"](around:{radius},{latitude},{longitude});
            node["place"](around:{radius},{latitude},{longitude});
            node["public_transport"](around:{radius},{latitude},{longitude});
            node["waterway"](around:{radius},{latitude},{longitude});
            node["attraction"](around:{radius},{latitude},{longitude});
            node["playground"](around:{radius},{latitude},{longitude});
            node["healthcare"](around:{radius},{latitude},{longitude});
        );
        out body;
        >;
        out skel qt;
        """
        
        if city!=None:
            try:
                df=pd.read_csv(f'./data/{city}.csv')
                print("Found city cached")
                return df
            except Exception:
                print(f"City {city} not found in cached. Collecting data from API")
        info_nearby = []
        try:
            response = requests.get(overpass_url, params={'data': overpass_query})
            if response.status_code == 200:
                logging.info("Successfully received response from Overpass API.")
                data = response.json()
                for element in data['elements']:
                    if element['type'] == 'node':
                        tags = element.get('tags', {})
                        name = tags.get('name', 'Unnamed')
                        lat = element.get('lat')
                        lon = element.get('lon')
                        
                        # Search for city name for later caching
                        # Check for place=city, place=town, or place=* tags
                        if city==None:
                            place_type = tags.get('place')
                            if place_type in ['city', 'town', 'village', 'hamlet']:
                                city = tags.get('name')
                            # Check for addr:city
                            if 'addr:city' in tags and not city:
                                city = tags['addr:city']
                        
                        mapped_categories = []
                        poi_type = None

                        # Check all possible OSM tag types
                        for osm_type in self.osm_mapping.keys():
                            if osm_type in tags:
                                osm_value = tags[osm_type]
                                mapped = self._get_mapped_category(osm_type, osm_value, tags)
                                if mapped:
                                    if isinstance(mapped, list):
                                        mapped_categories.extend(mapped)
                                    else:
                                        mapped_categories.append(mapped)
                                poi_type = f"{osm_type}:{osm_value}"

                        if mapped_categories:
                            info_nearby.append({
                                'Name': name,
                                'Latitude': float(lat),
                                'Longitude': float(lon),
                                'Categories': poi_type, #osm category
                                'Custom': list(set(mapped_categories))  # Remove duplicates
                            })
            else:
                logging.error(f"Error: Received status code {response.status_code} from Overpass API.")
        except Exception as e:
            print(f"Error during Overpass query: {e}")

        if city!=None:
            print("City found in POI descriptions or passed by you. Saving city data for later usage")
            pd.DataFrame(info_nearby).to_csv(f'./data/{city}.csv', index=False)
        else:
            print("City not found. Next time API will be called")
        return pd.DataFrame(info_nearby)
    
    def info_nearby_ors(self, latitude, longitude, step_lat, step_long):
        """Use OpenRouteService to search for POI within rectangle."""
        logging.info(f"Querying OpenRouteService for POIs in rectangle starting at ({latitude}, {longitude}).")
        left_top_point = [latitude, longitude][::-1]  # Longitude, Latitude
        right_bottom_point = [left_top_point[0] + step_long, left_top_point[1] + step_lat]

        body = {
            "request": "pois",
            "geometry": {
                "bbox": [left_top_point, right_bottom_point],
                "geojson": {"type": "Point", "coordinates": left_top_point},
                "buffer": 200
            }
        }
        try:
            key = os.environ['ors_sercret']
        except KeyError:
            logging.error("ORS secret key not found in environment variables.")
            return []

        headers = {
            'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
            'Authorization': key,
            'Content-Type': 'application/json; charset=utf-8'
        }

        try:
            response = requests.post('https://api.openrouteservice.org/pois', json=body, headers=headers)
            logging.info(f"OpenRouteService response: {response.status_code} {response.reason}")
            response_data = response.json()

            info_nearby = []
            for item in response_data.get('features', []):
                
                name = item['properties'].get('osm_tags',{}).get('name', 'Unnamed')
                coordinates = item['geometry'].get('coordinates', None)
                categories = item['properties'].get('category_ids', None)

                info_nearby.append({
                    'name': name,
                    'coordinates': coordinates,
                    'categories': categories
                })

            return info_nearby
        except Exception as e:
            logging.exception(f"Error during OpenRouteService query: {e}")
            return []