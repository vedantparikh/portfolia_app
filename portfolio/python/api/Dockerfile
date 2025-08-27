# Simple Dockerfile for Portfolia API
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create startup script
RUN echo '#!/bin/bash\n\
    echo "Starting Portfolia API..."\n\
    echo "Waiting for database to be ready..."\n\
    \n\
    # Wait for database to be ready\n\
    until python -c "from app.core.database.connection import init_db; import asyncio; asyncio.run(init_db())" 2>/dev/null; do\n\
    echo "Database not ready, waiting..."\n\
    sleep 2\n\
    done\n\
    \n\
    echo "Database is ready!"\n\
    echo "Starting application..."\n\
    \n\
    # Start the application\n\
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload\n\
    ' > /app/start.sh && chmod +x /app/start.sh

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Use startup script
CMD ["/app/start_api.sh"]
