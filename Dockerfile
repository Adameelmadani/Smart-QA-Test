FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Generate domain packs
RUN cd backend && python domain_packs_generator.py

# Create directories
RUN mkdir -p backend/uploads backend/exports

EXPOSE 8000

WORKDIR /app/backend

CMD ["python", "main.py"]
