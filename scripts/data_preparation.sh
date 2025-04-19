#!/bin/bash

echo "Scraping data..."
python3 scripts/scraping.py
echo "Filtering unnamed entities..."
python3 scripts/filter_unnamed.py
echo "Indexing data to Elasticsearch..."
python3 scripts/index_to_elasticsearch.py
echo "Data preparation complete."
