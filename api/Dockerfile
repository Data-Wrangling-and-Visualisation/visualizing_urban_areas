# Use the official Python image as the base image
FROM python:3.11-slim


# install curl (and clean up apt lists)
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*


# Set the working directory inside the container
WORKDIR /app

# Create data directory and set permissions
RUN mkdir -p /app/data && chmod 777 /app/data

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the container
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8000

# Command to run the FastAPI application
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]