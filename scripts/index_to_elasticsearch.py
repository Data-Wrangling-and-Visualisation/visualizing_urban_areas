import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import json
from pathlib import Path
import os
from dotenv import load_dotenv
import logging
import yaml
from tqdm import tqdm
import numpy as np
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logging.getLogger('elasticsearch').setLevel(logging.DEBUG)

def create_elasticsearch_index(es_client, index_name):
    """Create Elasticsearch index with optimized mappings."""
    try:
        # Check if index exists
        if es_client.indices.exists(index=index_name):
            logger.info(f"Index {index_name} already exists. Deleting...")
            es_client.indices.delete(index=index_name)
        
        # Index settings
        settings = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "refresh_interval": "1s"  # Set to 1 second for development
            },
            "mappings": {
                "properties": {
                    "name": {"type": "text"},
                    "city": {"type": "keyword"},
                    "latitude": {"type": "double"},
                    "longitude": {"type": "double"},
                    "location": {"type": "geo_point"},
                    "categories": {"type": "keyword"},
                    "timestamp": {"type": "date"},
                    "metadata": {
                        "type": "object",
                        "properties": {
                            "source": {"type": "keyword"},
                            "confidence": {"type": "float"}
                        }
                    }
                }
            }
        }
        
        # Create index with settings
        es_client.indices.create(index=index_name, body=settings)
        logger.info(f"Created index {index_name} with optimized mappings")
        
    except Exception as e:
        logger.error(f"Error creating index: {e}")
        raise

def prepare_document(row):
    """Prepare a document for indexing."""
    try:
        # Get latitude and longitude
        lat = float(row["Latitude"]) if pd.notna(row.get("Latitude")) else 0.0
        lon = float(row["Longitude"]) if pd.notna(row.get("Longitude")) else 0.0
        
        # Normalize field names and structure
        doc = {
            "name": str(row["Name"]) if pd.notna(row.get("Name")) else "",
            "city": str(row["city"]) if pd.notna(row.get("city")) else "",
            "latitude": lat,
            "longitude": lon,
            "location": {"lat": lat, "lon": lon},  # Added geo_point field
            "categories": str(row["Categories"]) if pd.notna(row.get("Categories")) else "",
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "source": "scraped_data",
                "confidence": 1.0
            }
        }
        
        # Add custom fields if they exist
        if pd.notna(row.get("Custom")):
            if isinstance(row["Custom"], (list, np.ndarray)):
                doc["custom_tags"] = [str(tag) for tag in row["Custom"]]
            else:
                doc["custom_tags"] = [str(row["Custom"])]
        
        return doc
    except Exception as e:
        logger.error(f"Error preparing document: {e}, row: {row}")
        return None

def index_data_to_elasticsearch(es_client, index_name, df):
    """Index data to Elasticsearch using bulk operations."""
    try:
        total_docs = 0
        failed_docs = 0
        
        # Process in batches of 500
        batch_size = 500
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i + batch_size]
            actions = []
            
            for _, row in batch.iterrows():
                try:
                    doc = prepare_document(row)
                    if doc:  # Only add valid documents
                        actions.append({"index": {"_index": index_name}})
                        actions.append(doc)
                except Exception as e:
                    logger.error(f"Error preparing document: {e}")
                    failed_docs += 1
                    continue
            
            if actions:  # Only perform bulk operation if there are valid actions
                try:
                    response = es_client.bulk(operations=actions, refresh=True)
                    if response["errors"]:
                        failed_items = [item for item in response["items"] if "error" in item["index"]]
                        for item in failed_items:
                            logger.error(f"Failed to index document: {item['index']['error']}")
                            failed_docs += 1
                    total_docs += len(actions) // 2  # Divide by 2 because each doc has 2 actions
                except Exception as e:
                    logger.error(f"Bulk indexing error: {e}")
                    failed_docs += len(actions) // 2
        
        logger.info(f"Indexed {total_docs} documents, {failed_docs} failed")
        
        # Force a refresh to ensure all documents are searchable
        es_client.indices.refresh(index=index_name)
        
        # Verify document count
        count = es_client.count(index=index_name)
        logger.info(f"Total documents in index: {count['count']}")
        
        if total_docs - failed_docs != count['count']:
            logger.warning(f"Document count mismatch. Expected {total_docs - failed_docs}, got {count['count']}")
        
    except Exception as e:
        logger.error(f"Error in bulk indexing: {e}")
        raise

def main(df):
    # Get the project root directory and load environment variables
    project_root = Path(__file__).parent.parent
    env_path = project_root / '.env'
    load_dotenv()        
    
    # Elasticsearch configuration
    es_host = os.getenv('ELASTICSEARCH_URL','http://localhost:9200')
    logger.info(f"Using Elasticsearch host: {es_host}")
    if not es_host:
        raise ValueError(f"ELASTICSEARCH_URL environment variable is not set in {env_path}")
    
    logger.info(f"Using Elasticsearch host: {es_host}")
    index_name = 'urban_areas'
    
    try:
        # Initialize Elasticsearch client with proper headers
        es_client = Elasticsearch(
            es_host,
            request_timeout=30,
            verify_certs=False,
            ssl_show_warn=False,
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        )
        
        # Check connection
        try:
            info = es_client.info()
            logger.info(f"Connected to Elasticsearch cluster: {info['cluster_name']}")
        except Exception as e:
            logger.error(f"Connection error details: {str(e)}")
            raise ConnectionError(f"Could not connect to Elasticsearch: {str(e)}")
        
        # Create index with optimized mappings
        create_elasticsearch_index(es_client, index_name)
        
        # Index the data
        index_data_to_elasticsearch(es_client, index_name, df)
        
    except Exception as e:
        logger.error(f"Error in main process: {e}")
        raise

if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    config_path = project_root / 'configs' / 'scraping_config.yaml'
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    bar = tqdm(config['cities'],desc='Indexing cities')
    for city in bar:
        df=pd.read_parquet(f'./data/collected/{city}_pois.zstd')
        main(df)
        bar.set_postfix(city=city)