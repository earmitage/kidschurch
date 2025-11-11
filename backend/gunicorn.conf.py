# Gunicorn Configuration File
# Used for production-style deployment
# Run with: gunicorn -c gunicorn.conf.py app:app

import multiprocessing
import os

# Server socket
bind = f"{os.getenv('HOST', '0.0.0.0')}:{os.getenv('PORT', 5001)}"
backlog = 2048

# Worker processes
# Use fewer workers for local dev, more for production
if os.getenv('FLASK_ENV') == 'development' or not os.getenv('FLASK_ENV'):
    workers = int(os.getenv('WORKERS', 2))  # 2 workers for local dev
else:
    workers = int(os.getenv('WORKERS', multiprocessing.cpu_count() * 2 + 1))  # More for production

worker_class = 'uvicorn.workers.UvicornWorker'  # Required for FastAPI (ASGI)
worker_connections = 1000
timeout = 120
keepalive = 5

# Request body size limit (for file uploads)
# This allows up to 15MB uploads (PDFs can be large)
# Note: If using Nginx as reverse proxy, also configure client_max_body_size there
limit_request_line = 8190
limit_request_fields = 100
limit_request_field_size = 8190

# Logging
accesslog = '-'  # Log to stdout
errorlog = '-'   # Log to stderr
loglevel = os.getenv('LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'church-games-backend'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
# keyfile = None
# certfile = None

