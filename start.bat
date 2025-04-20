@echo off
setlocal enabledelayedexpansion

:: Colors for output (Windows doesn't support ANSI colors in batch files)
set "GREEN=[STATUS] "
set "YELLOW=[WARNING] "
set "RED=[ERROR] "

:: Function to print status messages
call :print_status "Starting application setup..."

:: Check if Docker is running
docker info >nul 2>&1
if %ERRORLEVEL% neq 0 (
    call :print_error "Docker is not running. Please start Docker and try again."
    exit /b 1
)

:: Stop any running containers
call :print_status "Stopping any running containers..."
docker-compose down -v

:: Build and start the containers
call :print_status "Building and starting containers..."
docker-compose up --build -d

:: Wait for Elasticsearch to be ready
call :print_status "Waiting for Elasticsearch to be ready..."
:wait_elasticsearch
curl -s http://localhost:9200 >nul 2>&1
if %ERRORLEVEL% neq 0 (
    call :print_warning "Elasticsearch is not ready yet. Waiting..."
    timeout /t 5 >nul
    goto wait_elasticsearch
)
call :print_status "Elasticsearch is ready!"

:: Wait for API to be ready
call :print_status "Waiting for API to be ready..."
:wait_api
curl -s http://localhost:8000/health >nul 2>&1
if %ERRORLEVEL% neq 0 (
    call :print_warning "API is not ready yet. Waiting..."
    timeout /t 5 >nul
    goto wait_api
)
call :print_status "API is ready!"

:: Run the clustering script
call :print_status "Running clustering script..."
python scripts/clusterize.py
if %ERRORLEVEL% neq 0 (
    call :print_error "Clustering script failed!"
    exit /b 1
)

:: Index clusters to Elasticsearch
call :print_status "Indexing clusters to Elasticsearch..."
python scripts/index_clusters_to_elasticsearch.py
if %ERRORLEVEL% neq 0 (
    call :print_error "Indexing script failed!"
    exit /b 1
)

call :print_status "Application setup complete!"
call :print_status "You can now access:"
call :print_status "- Frontend: http://localhost"
call :print_status "- API: http://localhost:8000"
call :print_status "- Elasticsearch: http://localhost:9200"

:: Show container logs
call :print_status "Showing container logs (press Ctrl+C to stop)..."
docker-compose logs -f

exit /b 0

:print_status
echo %GREEN%%~1
exit /b 0

:print_warning
echo %YELLOW%%~1
exit /b 0

:print_error
echo %RED%%~1
exit /b 0 