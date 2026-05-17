# Backend Dockerfile for University Front Door Agent
# Lab 06: Deploy with azd - SOLUTION
#
# This Dockerfile containerizes the FastAPI backend application
# for deployment to Azure Container Apps.

FROM python:3.12-slim

WORKDIR /app

# Install system dependencies needed for the application
# curl is required for health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
# This ensures dependencies are only reinstalled when requirements.txt changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create a non-root user for security (CIS Docker Benchmark recommendation)
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

# Expose the FastAPI port
EXPOSE 8000

# Health check endpoint for container orchestration
# Azure Container Apps uses this to determine container health
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Start the FastAPI application with uvicorn
# --host 0.0.0.0 allows connections from outside the container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
