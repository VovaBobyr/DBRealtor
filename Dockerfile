FROM python:3.12-slim

WORKDIR /app

# Install system deps needed by asyncpg (libpq) and psycopg2 (for alembic)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (layer caching)
COPY pyproject.toml .
RUN pip install --no-cache-dir ".[dev]" 2>/dev/null || pip install --no-cache-dir .

# Copy source
COPY src/ src/
COPY db/ db/
COPY alembic.ini .

# Default: run the scraper (override with CMD for migrations etc.)
CMD ["python", "-m", "src.scraper"]
