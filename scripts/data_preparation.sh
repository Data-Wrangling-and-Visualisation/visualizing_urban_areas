echo "Scraping data..."
python scripts/scraping.py
echo "Clustering data..."
python scripts/clustering.py
echo "Indexing data to Elasticsearch..."
python scripts/index_to_elasticsearch.py
echo "Data preparation complete."
