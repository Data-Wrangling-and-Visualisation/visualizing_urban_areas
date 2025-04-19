import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import json
from pathlib import Path
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_elasticsearch_index(es_client, index_name):
    """Create an Elasticsearch index with optimized mappings."""
    mapping = {
        "mappings": {
            "properties": {
                "Name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                "city": {"type": "keyword"},
                "city_lat": {"type": "float"},
                "city_lon": {"type": "float"},
                "location": {"type": "geo_point"},
                "timestamp": {"type": "date"},
                "metadata": {
                    "properties": {
                        "source": {"type": "keyword"},
                        "confidence": {"type": "float"}
                    }
                }
            }
        },
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "refresh_interval": "30s"
        }
    }
    
    try:
        if es_client.indices.exists(index=index_name):
            logger.info(f"Index {index_name} already exists. Deleting...")
            es_client.indices.delete(index=index_name)
        
        es_client.indices.create(index=index_name, body=mapping)
        logger.info(f"Created index {index_name} with optimized mappings")
    except Exception as e:
        logger.error(f"Error creating index: {e}")
        raise

def prepare_document(row):
    """Prepare a document for Elasticsearch indexing."""
    doc = {
        "Name": row.get("Name", ""),
        "city": row.get("city", ""),
        "city_lat": float(row.get("city_lat", 0)),
        "city_lon": float(row.get("city_lon", 0)),
        "location": {
            "lat": float(row.get("Lat", 0)),
            "lon": float(row.get("Lon", 0))
        },
        "timestamp": pd.Timestamp.now().isoformat(),
        "metadata": {
            "source": "scraped_data",
            "confidence": 1.0
        }
    }
    
    # Add any additional fields from the row
    for key, value in row.items():
        if key not in doc and pd.notna(value):
            doc[key] = value
    
    return doc

def index_data_to_elasticsearch(es_client, index_name, data_path, batch_size=1000):
    """Index data to Elasticsearch in batches."""
    try:
        # Read the filtered data
        df = pd.read_csv(data_path)
        logger.info(f"Read {len(df)} records from {data_path}")
        
        # Prepare documents for bulk indexing
        actions = []
        for _, row in df.iterrows():
            doc = prepare_document(row)
            action = {
                "_index": index_name,
                "_source": doc
            }
            actions.append(action)
            
            # Bulk index when batch size is reached
            if len(actions) >= batch_size:
                bulk(es_client, actions)
                logger.info(f"Indexed {len(actions)} documents")
                actions = []
        
        # Index remaining documents
        if actions:
            bulk(es_client, actions)
            logger.info(f"Indexed {len(actions)} remaining documents")
        
        logger.info("Indexing completed successfully")
        
    except Exception as e:
        logger.error(f"Error during indexing: {e}")
        raise

def main():
    load_dotenv()
    
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    data_path = project_root / 'data' / 'scraped_data_filtered.csv'
    
    # Elasticsearch configuration
    es_host = os.getenv('ELASTICSEARCH_URL', 'http://elasticsearch:9200')
    index_name = 'urban_areas'
    
    try:
        # Initialize Elasticsearch client
        es_client = Elasticsearch(es_host)
        
        # Check connection
        if not es_client.ping():
            raise ConnectionError("Could not connect to Elasticsearch")
        
        # Create index with optimized mappings
        create_elasticsearch_index(es_client, index_name)
        
        # Index the data
        index_data_to_elasticsearch(es_client, index_name, data_path)
        
    except Exception as e:
        logger.error(f"Error in main process: {e}")
        raise

if __name__ == "__main__":
    main() 