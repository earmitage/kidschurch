"""
FastAPI application entry point for Gunicorn
This file is used when running with Gunicorn: gunicorn -c gunicorn.conf.py app:app
Note: FastAPI is ASGI-native, so wsgi.py is optional. Gunicorn with Uvicorn workers
can directly use app:app from app.py
"""

from app import app, database_service, ai_service, pdf_storage_service

print(f"🚀 Church Games Backend (FastAPI)")
print(f"📊 AI Provider: {ai_service.provider_name}")
print(f"💾 Database: {'Enabled' if database_service.is_enabled() else 'Will initialize on first request'}")
print(f"📁 PDF Storage: {pdf_storage_service.storage_path}")

# Export app for Gunicorn
# Note: Gunicorn with Uvicorn workers will use this
if __name__ == '__main__':
    print("⚠️  Run with: ./start.sh or gunicorn -c gunicorn.conf.py app:app")
