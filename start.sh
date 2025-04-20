#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print status messages
print_status() {
    echo -e "${GREEN}[STATUS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running in WSL
if [ -f /proc/version ] && grep -q Microsoft /proc/version; then
    print_status "Running in WSL environment"
    # Convert Windows path to WSL path if needed
    if [[ "$PWD" == /mnt/* ]]; then
        print_status "Windows path detected, using as is"
    else
        print_warning "Please run this script from a Windows path (e.g., /mnt/c/...) for better Docker Desktop integration"
    fi
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

print_status "Starting application setup..."

# Stop any running containers
print_status "Stopping any running containers..."
docker-compose down -v

# Build and start the containers
print_status "Building and starting containers..."
docker-compose up --build -d

# Wait for Elasticsearch to be ready
print_status "Waiting for Elasticsearch to be ready..."
until curl -s http://localhost:9200 > /dev/null; do
    print_warning "Elasticsearch is not ready yet. Waiting..."
    sleep 5
done
print_status "Elasticsearch is ready!"

# Wait for API to be ready
print_status "Waiting for API to be ready..."
until curl -s http://localhost:8000/health > /dev/null; do
    print_warning "API is not ready yet. Waiting..."
    sleep 5
done
print_status "API is ready!"

# Run the clustering script
print_status "Running clustering script..."
python3 scripts/clusterize.py
if [ $? -ne 0 ]; then
    print_error "Clustering script failed!"
    exit 1
fi

# Index clusters to Elasticsearch
print_status "Indexing clusters to Elasticsearch..."
python3 scripts/index_clusters_to_elasticsearch.py
if [ $? -ne 0 ]; then
    print_error "Indexing script failed!"
    exit 1
fi

print_status "Application setup complete!"
print_status "You can now access:"
print_status "- Frontend: http://localhost"
print_status "- API: http://localhost:8000"
print_status "- Elasticsearch: http://localhost:9200"

# Keep the script running to show logs
print_status "Showing container logs (press Ctrl+C to stop)..."
docker-compose logs -f 