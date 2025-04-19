from DataCollector import DataCollector
from city_coordinates import get_city_coordinates
import yaml
import pandas as pd
import json
from tqdm import tqdm
import os
from pathlib import Path
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    
    # Load config from the new location
    config_path = project_root / 'configs' / 'scraping_config.yaml'
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    all_data=[]
    dc=DataCollector()

    for city in tqdm(config['cities'],desc='Processing cities'):
        lat, lon = get_city_coordinates(city)
        if lat is not None and lon is not None:
            data=dc.info_nearby_op(lat,lon,500,city)
            data= data.to_dict(orient='records')
            for i in range(len(data)):
                data[i]['city']=city
                data[i]['city_lat']=lat
                data[i]['city_lon']=lon
                all_data.append(data[i])
