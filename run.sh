#!/bin/bash

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

mkdir data

python3 scripts/scraping.py

docker-compose up