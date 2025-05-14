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
    mode = request.form.get('mode', '')

    try:
        if request.method == 'POST':
            query = request.form.get('query', '')
            date_from = request.form.get('date_from')
            date_to = request.form.get('date_to')

            if not es.indices.exists(index="apod"):
                error = "The 'apod' index does not exist. Please create it first."
                logger.error(error)
                return render_template('index.html', results=[], query=query, error=error)

            if mode == "simple":
                body = {
                    "query": {
                        "match": {
                            "title": query
                        }
                    }
                }

            elif mode == "fuzzy":
                body = {
                    "query": {
                        "fuzzy": {
                            "title": {
                                "value": query,
                                "fuzziness": "AUTO"
                            }
                        }
                    }
                }

            elif mode == "filter":
                if not date_from or not date_to:
                    raise ValueError("Both start and end dates must be provided.")
                body = {
                    "query": {
                        "range": {
                            "date": {
                                "gte": date_from,
                                "lte": date_to
                            }
                        }
                    }
                }

            elif mode == "combined":
                if not query or not date_from or not date_to:
                    raise ValueError("Query and both dates must be provided for combined search.")
                body = {
                    "query": {
                        "bool": {
                            "should": [
                                {"match": {"title": query}},
                                {"fuzzy": {"title": {"value": query, "fuzziness": "AUTO"}}}
                            ],
                            "filter": [
                                {"range": {"date": {"gte": date_from, "lte": date_to}}}
                            ],
                            "minimum_should_match": 1
                        }
                    }
                }

            else:
                raise ValueError("Invalid search mode.")

            logger.info(f"Running {mode} search for query: {query}")
            response = es.search(index="apod", size=100, body=body)
            results = [hit["_source"] for hit in response["hits"]["hits"]]
            logger.info(f"Found {len(results)} results")

    except Exception as e:
        error = f"An error occurred: {str(e)}"
        logger.error(error)

    return render_template('index.html', results=results, query=query, error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
