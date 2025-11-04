FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    make \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY scripts/requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy monitoring scripts
COPY scripts/monitor.py ./
COPY scripts/metrics_server.py ./
COPY configs/monitor.yaml ./

# Create data directory
RUN mkdir -p /app/data

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:9100/api/health || exit 1

# Expose metrics port
EXPOSE 9100

# Start monitoring service
CMD ["python3", "-u", "metrics_server.py"]
