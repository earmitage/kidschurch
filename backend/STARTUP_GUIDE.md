# Backend Startup Guide

## Quick Start

### Local Development (Production-style server)

Use Gunicorn locally to match production environment:

```bash
cd backend
./start.sh
```

Or use Gunicorn directly:

```bash
cd backend
gunicorn -c gunicorn.conf.py app:app
```

### Configuration

The startup script uses `gunicorn.conf.py` for configuration. You can override settings via environment variables:

- `PORT` - Server port (default: 5001)
- `WORKERS` - Number of worker processes (default: 2 for dev, auto for production)
- `HOST` - Bind address (default: 0.0.0.0)
- `LOG_LEVEL` - Logging level (default: info)
- `FLASK_ENV` - Environment (development/production)

### Alternative: Flask Development Server

If you want to use Flask's built-in development server (not recommended for production):

```bash
cd backend
python3 app.py
```

**Note:** This will show a deprecation warning and is not suitable for production.

## Production Deployment

For production, use the same Gunicorn setup:

```bash
# Set production environment
export FLASK_ENV=production
export WORKERS=4  # Adjust based on server CPU cores

# Start server
./start.sh
```

Or use a process manager like systemd (see `PRODUCTION_DEPLOYMENT.md`).

## Key Differences

| Feature | Flask Dev Server | Gunicorn (Production) |
|---------|------------------|------------------------|
| Concurrent Requests | Single-threaded | Multi-worker |
| Performance | Slow | Fast |
| Production Ready | ❌ No | ✅ Yes |
| Async Support | Limited | Full (with gevent) |
| Debug Mode | Automatic | Manual |

## Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Server
PORT=5001
FLASK_ENV=development  # or 'production'
WORKERS=2
HOST=0.0.0.0

# Database
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=your_user
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=kidschurch

# AI Provider
AI_PROVIDER=gemini
GOOGLE_API_KEY=your_key
GEMINI_MODEL=gemini-2.0-flash-exp

# PDF Storage
PDF_STORAGE_DIR=pdfs
```

## Troubleshooting

### 413 Content Too Large Error

If you're getting `413 (Content Too Large)` errors when uploading PDFs, this is likely due to Nginx (or another reverse proxy) blocking the request before it reaches the application.

**Solution for Nginx:**

1. The default `client_max_body_size` in Nginx is 1MB, but PDFs can be up to 10MB.

2. Add or update the following in your Nginx configuration:
   ```nginx
   location /kidschurch-backend/ {
       # ... other settings ...
       
       # CRITICAL: Allow large file uploads (PDFs can be up to 10MB)
       client_max_body_size 15M;
       
       # Increase timeouts for large uploads
       proxy_read_timeout 300s;
       proxy_connect_timeout 75s;
       proxy_send_timeout 300s;
       
       # Buffer settings for large requests
       proxy_buffering off;
       proxy_request_buffering off;
   }
   ```

3. See `nginx.example.conf` for a complete Nginx configuration example.

4. After updating Nginx config:
   ```bash
   sudo nginx -t  # Test configuration
   sudo systemctl reload nginx  # Reload Nginx
   ```

**Note:** The application itself allows up to 10MB uploads (configured in `app.py`), but the reverse proxy must also allow this size.


