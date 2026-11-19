# Production Dockerfile for Real-Time E-Commerce Platform
FROM python:3.11-slim

# Prevent Python from writing .pyc and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code and assets
COPY src/ ./src/
COPY sql/ ./sql/
COPY dashboard/ ./dashboard/
COPY scripts/ ./scripts/
COPY data/ ./data/
COPY docs/ ./docs/

# Create runtime directories
RUN mkdir -p logs reports data/rejected data/processed

EXPOSE 8501

# Entrypoint script handles DB wait, schema migrations, ETL, and Streamlit launch
CMD ["python", "scripts/docker_entrypoint.py"]
