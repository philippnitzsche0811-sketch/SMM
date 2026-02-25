FROM python:3.12-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY . .

# Volumes für persistente Daten
RUN mkdir -p /app/temp /app/tokens /app/data

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Port
EXPOSE 8000

# Default command (wird von docker-compose überschrieben)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
