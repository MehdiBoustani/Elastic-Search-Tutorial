from elasticsearch import Elasticsearch
from elasticsearch import helpers
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connect to Elasticsearch
es = Elasticsearch("http://localhost:9200")

# Create the index with mappings
index_name = "apod"

mappings = {
    "mappings": {
        "properties": {
            "date": {"type": "date"},
            "title": {"type": "text"},
            "explanation": {"type": "text"},
            "image_url": {"type": "keyword"},
            "authors": {"type": "text"}
        }
    }
}

def create_index():
    try:
        # Delete index if it exists
        if es.indices.exists(index=index_name):
            es.indices.delete(index=index_name)
            logger.info(f"Deleted existing index: {index_name}")
        
        # Create index with mappings
        es.indices.create(index=index_name, body=mappings)
        logger.info(f"Created index: {index_name}")
        
        # Read data from JSON file
        with open('data/apod.json', 'r') as f:
            data = json.load(f)
            
        # Prepare the actions for bulk import
        actions = [
            {
                "_index": index_name,
                "_id": doc["title"],  # Using title as document ID
                "_source": doc
            }
            for doc in data
        ]
        
        # Bulk import the data
        helpers.bulk(es, actions)
        logger.info(f"Successfully bulk imported {len(data)} documents")
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    create_index() 