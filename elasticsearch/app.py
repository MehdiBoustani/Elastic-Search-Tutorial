from flask import Flask, render_template, request
from elasticsearch import Elasticsearch
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
es = Elasticsearch("http://elasticsearch:9200")

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    query = ""
    error = None
    
    if request.method == 'POST':
        try:
            query = request.form['query']
            logger.info(f"Searching for query: {query}")
            
            # Check if index exists
            if not es.indices.exists(index="apod"):
                error = "The 'apod' index does not exist. Please create it first."
                logger.error(error)
                return render_template('index.html', results=results, query=query, error=error)
            
            response = es.search(index="apod", body={
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["title", "explanation"],
                        "fuzziness": "AUTO"
                    }
                }
            })
            results = [hit["_source"] for hit in response["hits"]["hits"]]
            logger.info(f"Found {len(results)} results")
            
        except Exception as e:
            error = f"An error occurred: {str(e)}"
            logger.error(error)
            
    return render_template('index.html', results=results, query=query, error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
