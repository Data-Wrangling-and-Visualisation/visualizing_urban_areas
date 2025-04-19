FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scripts/ ./scripts/
COPY data/ ./data/

CMD ["bash", "./scripts/data_preparation.sh"] 