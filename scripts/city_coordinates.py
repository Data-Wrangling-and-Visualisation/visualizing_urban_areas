from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

def get_city_coordinates(city_name, county_name=None):
    """
    Get the latitude and longitude coordinates for a city.
    
    Args:
        city_name (str): Name of the city
        county_name (str, optional): Name of the county. Defaults to None.
    
    Returns:
        tuple: (latitude, longitude) if successful, (None, None) if failed
    """
    geolocator = Nominatim(user_agent="city_coordinates_app")
    
    # Construct the query
    query = f"{city_name}"
    if county_name:
        query += f", {county_name}"
    
    try:
        location = geolocator.geocode(query)
        if location:
            return location.latitude, location.longitude
        return None, None
    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        print(f"Error occurred: {e}")
        return None, None

def main():
    # Example usage
    city = input("Enter city name: ")
    county = input("Enter county name (optional, press Enter to skip): ")
    
    lat, lon = get_city_coordinates(city, county if county else None)
    
    if lat and lon:
        print(f"\nCoordinates for {city}{f', {county}' if county else ''}:")
        print(f"Latitude: {lat}")
        print(f"Longitude: {lon}")
    else:
        print(f"\nCould not find coordinates for {city}{f', {county}' if county else ''}")

if __name__ == "__main__":
    main() 