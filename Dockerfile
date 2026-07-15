# Start with official Python 3.12 slim image
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements and install dependencies first
# (Docker caches this layer if requirements don't change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Create data directories
RUN mkdir -p data/supplier_drops

# Default command: run the pipeline
CMD ["python", "src/main.py"]
