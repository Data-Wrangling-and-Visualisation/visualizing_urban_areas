"""
Script to index cluster shapes from clusterize.py to Elasticsearch.
The script reads the cluster shapes from parquet file and indexes them to Elasticsearch
with proper geo_shape mapping for visualization and analysis.
"""

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
import pyarrow.parquet as pq
import pyarrow.compute as pc

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logging.getLogger('elasticsearch').setLevel(logging.DEBUG)

def create_elasticsearch_index(es_client, index_name):
    """Create Elasticsearch index with optimized mappings for cluster shapes."""
    try:
        # Check if index exists
        if es_client.indices.exists(index=index_name):
            logger.info(f"Index {index_name} already exists. Deleting...")
            es_client.indices.delete(index=index_name)
        
        # Index settings with geo_shape mapping
        settings = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "refresh_interval": "1s"
            },
            "mappings": {
                "properties": {
                    "group": {"type": "keyword"},
                    "cluster_number": {"type": "integer"},
                    "shape": {
                        "type": "geo_shape"
                    },
                    "city": {"type": "keyword"},
                    "timestamp": {"type": "date"},
                    "metadata": {
                        "type": "object",
                        "properties": {
                            "num_points": {"type": "integer"},
                            "area_km2": {"type": "float"}
                        }
                    }
                }
            }
        }
        
        # Create index with settings
        es_client.indices.create(index=index_name, body=settings)
        logger.info(f"Created index {index_name} with geo_shape mapping")
        
    except Exception as e:
        logger.error(f"Error creating index: {e}")
        raise

def calculate_area_km2(coordinates):
    """Calculate approximate area of a polygon in square kilometers."""
    try:
        # Convert coordinates to numpy array
        coords = np.array(coordinates)
        
        # Calculate area using shoelace formula
        x = coords[:, 0]
        y = coords[:, 1]
        area = 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))
        
        # Convert to square kilometers (approximate conversion)
        # This is a rough approximation as we're using lat/lon coordinates
        area_km2 = area * 111.32 * 111.32  # 1 degree ≈ 111.32 km
        return area_km2
    except Exception as e:
        logger.error(f"Error calculating area: {e}")
        return 0.0

def prepare_cluster_document(group, cluster_num, coordinates, city):
    """Prepare a cluster document for indexing."""
    try:
        # Format coordinates for geo_shape
        # Elasticsearch expects coordinates in [lon, lat] format
        formatted_coords = [[float(lon), float(lat)] for lat, lon in coordinates]
        
        # Create polygon shape
        shape = {
            "type": "polygon",
            "coordinates": [formatted_coords]  # Note: coordinates must be closed (first and last point same)
        }
        
        # Calculate area
        area_km2 = calculate_area_km2(coordinates)
        
        doc = {
            "group": group,
            "cluster_number": cluster_num,
            "shape": shape,
            "city": city,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "num_points": len(coordinates),
                "area_km2": area_km2
            }
        }
        
        return doc
    except Exception as e:
        logger.error(f"Error preparing cluster document: {e}")
        return None

def index_clusters_to_elasticsearch(es_client, index_name, clusters_path, city):
    """Index cluster shapes to Elasticsearch using bulk operations."""
    try:
        # Read clusters from parquet
        table = pq.read_table(clusters_path)
        
        # Process in batches
        batch_size = 100
        total_docs = 0
        failed_docs = 0
        
        # Get unique groups
        groups = set(table.select(['group']).to_pydict()['group'])
        
        for group in tqdm(groups, desc=f"Indexing clusters for {city}"):
            # Filter table for current group
            expr = pc.field("group") == group
            group_table = table.filter(expr)
            
            # Process each cluster in the group
            for i in range(len(group_table)):
                try:
                    row = group_table.slice(i, 1)
                    cluster_num = row['cluster_number'][0].as_py()
                    coordinates = row['coordinates'][0].as_py()
                    
                    # Prepare document
                    doc = prepare_cluster_document(group, cluster_num, coordinates, city)
                    if doc:
                        # Index document
                        es_client.index(
                            index=index_name,
                            body=doc,
                            refresh=True
                        )
                        total_docs += 1
                except Exception as e:
                    logger.error(f"Error processing cluster: {e}")
                    failed_docs += 1
                    continue
        
        logger.info(f"Indexed {total_docs} cluster shapes, {failed_docs} failed")
        
        # Force a refresh to ensure all documents are searchable
        es_client.indices.refresh(index=index_name)
        
        # Verify document count
        count = es_client.count(index=index_name)
        logger.info(f"Total cluster shapes in index: {count['count']}")
        
    except Exception as e:
        logger.error(f"Error in bulk indexing: {e}")
        raise

def main():
    # Get the project root directory and load environment variables
    project_root = Path(__file__).parent.parent
    env_path = project_root / '.env'
    if not env_path.exists():
        # Try one level up if not found
        env_path = project_root.parent / '.env'
    load_dotenv(env_path)
    
    # Elasticsearch configuration
    es_host = os.getenv('ELASTICSEARCH_URL', None)
    
    if not es_host:
        raise ValueError(f"ELASTICSEARCH_URL environment variable is not set in {env_path}")
    
    logger.info(f"Using Elasticsearch host: {es_host}")
    index_name = 'urban_clusters'
    
    try:
        # Initialize Elasticsearch client with more detailed options
        es_client = Elasticsearch(
            es_host,
            request_timeout=60,  # Increased timeout
            verify_certs=False,
            ssl_show_warn=False,
            retry_on_timeout=True,
            max_retries=3,
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            # Add basic auth if needed
            # basic_auth=('username', 'password')
        )
        
        # Check connection with more detailed error handling
        try:
            # Try a simple ping first
            if not es_client.ping():
                raise ConnectionError("Could not ping Elasticsearch server")
            
            # Then get cluster info
            info = es_client.info()
            logger.info(f"Connected to Elasticsearch cluster: {info['cluster_name']}")
            logger.info(f"Cluster version: {info['version']['number']}")
            
        except Exception as e:
            logger.error(f"Connection error details: {str(e)}")
            logger.error(f"Trying to connect to: {es_host}")
            # Try to get more detailed error information
            try:
                import requests
                response = requests.get(es_host, timeout=5)
                logger.error(f"HTTP Response: {response.status_code}")
                logger.error(f"Response content: {response.text}")
            except requests.exceptions.RequestException as re:
                logger.error(f"HTTP Request error: {str(re)}")
            raise ConnectionError(f"Could not connect to Elasticsearch: {str(e)}")
        
        # Create index with geo_shape mapping
        create_elasticsearch_index(es_client, index_name)
        
        # Load clustering config to get city
        with open('./configs/clustering.yaml', 'r') as f:
            config = yaml.safe_load(f)
            city = config['general_parameters']['city']
        
        # Index the clusters
        clusters_path = './data/processed/clusters.zstd'
        index_clusters_to_elasticsearch(es_client, index_name, clusters_path, city)
        
    except Exception as e:
        logger.error(f"Error in main process: {e}")
        raise

if __name__ == "__main__":
    main() 