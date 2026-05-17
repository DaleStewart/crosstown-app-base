# Backend Dockerfile for University Front Door Agent
# Lab 06: Deploy with azd
#
# TODO: Complete this Dockerfile to containerize the backend application
# Reference: https://docs.docker.com/develop/develop-images/dockerfile_best-practices/

# TODO: Use Python 3.11 slim base image
FROM python:3.11-slim

WORKDIR /app

# TODO: Install system dependencies needed for the application
# Hint: You'll need curl for health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# TODO: Copy requirements.txt first for better Docker layer caching
# Then install Python dependencies
COPY requirements.txt .
# TODO: Install requirements with pip (no cache for smaller image)

# TODO: Copy the application code

# TODO: Create a non-root user for security (recommended practice)
# Hint: Use useradd to create 'appuser'

# TODO: Expose the correct port (FastAPI default is 8000)

# TODO: Add a HEALTHCHECK instruction
# The health endpoint is at /api/health
# Suggested intervals: 30s check, 10s timeout, 5s start period, 3 retries

# TODO: Set the CMD to start uvicorn
# Hint: uvicorn app.main:app --host 0.0.0.0 --port 8000
