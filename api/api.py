from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from typing import List, Optional
import os
from dotenv import load_dotenv
import logging
import time
from urllib3.exceptions import NewConnectionError, MaxRetryError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (you can restrict this to specific domains)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

def create_elasticsearch_client(max_retries=5, retry_delay=5):
    """Create Elasticsearch client with retry logic."""
    es_host = os.getenv('ELASTICSEARCH_URL', 'http://localhost:9200')
    logger.info(f"Attempting to connect to Elasticsearch at {es_host}")
    
    for attempt in range(max_retries):
        try:
            
            es = Elasticsearch(
                es_host,
                request_timeout=30,
                verify_certs=False,
                ssl_show_warn=False,
                headers= {
                    'Accept': "application/json",
                    'Content-Type': "application/json"
                }
            )
            if not es.ping():
                logger.error("Failed to connect to Elasticsearch")
                raise Exception("Failed to connect to Elasticsearch")
            return es
        except Exception as e:
            logger.error(f"Failed to connect to Elasticsearch: {str(e)}")
            import requests
            response = requests.get(es_host)
            logger.error(f"Elasticsearch response: {response.status_code}")
            raise

# Initialize Elasticsearch client with retry logic
try:
    es = create_elasticsearch_client()
except Exception as e:
    logger.error(f"Failed to initialize Elasticsearch client: {str(e)}")
    raise HTTPException(status_code=500, detail=f"Failed to connect to Elasticsearch: {str(e)}")

@app.get("/cities")
async def get_cities():
    """Get list of all available cities with their coordinates."""
    try:
        # Use terms aggregation to get unique cities
        max_cities=10000
        body = {
        "size": 0,
        "aggs": {
            "by_city": {
                "terms": {
                    "field": "city",
                    "size": max_cities
                },
                "aggs": {
                    "sample_loc": {
                        "top_hits": {
                            "size": 1,
                            "_source": ["location"]
                        }
                    }
                }
            }
            }
        }
        
        response = es.search(index="urban_areas", body=body)
        buckets = response["aggregations"]["by_city"]["buckets"]
        cities = []
        for bucket in buckets:
            cities.append({
                "name": bucket['key'],
                "lat": bucket['sample_loc']['hits']['hits'][0]['_source']['location']['lat'],
                "lon": bucket['sample_loc']['hits']['hits'][0]['_source']['location']['lon']
            })
            logger.info(f"Found {len(cities)} cities")
        return {"cities": cities}
    except Exception as e:
        logger.error(f"Error fetching cities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/city/{city_name}/pois")
async def get_city_pois(city_name: str):
    """Get all POIs for a specific city."""
    try:
        query = {
            "query": {
                "term": {
                    "city": {
                        "value": city_name
                    }
                }
            }
        }
        logger.info(f"Fetching POIs for city {city_name}")
        docs = scan(
            client=es,
            index="urban_areas",
            query=query,
            _source_includes=["name", "location", "categories", "timestamp", "metadata", "custom_tags"]
        )
        pois = [hit["_source"] for hit in docs]
        
        return {"pois": pois}
    except Exception as e:
        logger.error(f"Error fetching POIs for city {city_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/nearby")
async def get_nearby_pois(
    lat: float,
    lon: float,
    distance: Optional[str] = "1km",
    size: Optional[int] = 100
):
    """Get POIs near a specific location."""
    try:
        query = {
            "query": {
                "bool": {
                    "must": {
                        "match_all": {}
                    },
                    "filter": {
                        "geo_distance": {
                            "distance": distance,
                            "location": {
                                "lat": lat,
                                "lon": lon
                            }
                        }
                    }
                }
            },
            "size": size,
            "sort": [
                {
                    "_geo_distance": {
                        "location": {
                            "lat": lat,
                            "lon": lon
                        },
                        "order": "asc",
                        "unit": "m"
                    }
                }
            ]
        }
        
        response = es.search(index="urban_areas", body=query)
        pois = [hit["_source"] for hit in response["hits"]["hits"]]
        
        return {"pois": pois}
    except Exception as e:
        logger.error(f"Error fetching nearby POIs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check if Elasticsearch is responding
        if es.ping():
            return {"status": "healthy", "elasticsearch": "connected"}
        else:
            return {"status": "unhealthy", "elasticsearch": "not connected"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}
