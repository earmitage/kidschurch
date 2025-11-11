#!/bin/bash
# Production-style server startup script
# Uses Uvicorn with Gunicorn workers for FastAPI
# Works for both local development and production deployment

cd "$(dirname "$0")"

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Default values
PORT=${PORT:-5001}
WORKERS=${WORKERS:-2}  # Fewer workers for local dev
HOST=${HOST:-0.0.0.0}
LOG_LEVEL=${LOG_LEVEL:-info}

# Adjust workers for local vs production
if [ "${FLASK_ENV}" = "development" ] || [ -z "${FLASK_ENV}" ]; then
    WORKERS=2  # Use fewer workers for local development
    LOG_LEVEL=debug
fi

echo "🚀 Starting Church Games Backend (FastAPI)"
echo "📊 Port: ${PORT}"
echo "👷 Workers: ${WORKERS}"
echo "🌍 Environment: ${FLASK_ENV:-development}"
echo ""

# Use Gunicorn with uvicorn workers for FastAPI
exec gunicorn \
    --config gunicorn.conf.py \
    --bind "${HOST}:${PORT}" \
    --workers "${WORKERS}" \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 120 \
    --log-level "${LOG_LEVEL}" \
    app:app

