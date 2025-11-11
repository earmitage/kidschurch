"""
FastAPI Backend for Church Games AI Integration
Provides AI-powered coloring image generation, PDF storage, and usage tracking
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query, Path as PathParam, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from contextlib import asynccontextmanager
import os
import json
import asyncio
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from services.ai_service import AIService
from services.database_service import DatabaseService
from services.pdf_storage_service import PDFStorageService
from utils.errors import APIError
from utils.security import (
    validate_theme, validate_church_name, validate_prompt,
    validate_int, validate_file_extension, sanitize_string
)
from utils.env_validation import validate_and_exit_on_error

# Load environment variables
# Use explicit path to ensure .env is loaded from backend directory
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=str(env_path), override=True)
else:
    # Fallback: try loading from current directory
    load_dotenv(override=True)

# Validate environment variables on startup
# This will exit if critical configuration is missing
validate_and_exit_on_error()

# Initialize services (will be available after app creation)
ai_service = AIService()
database_service = DatabaseService()
pdf_storage_service = PDFStorageService()

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown"""
    # Startup
    # Store main event loop for thread-safe logging
    from utils.tracking import set_main_event_loop
    loop = asyncio.get_running_loop()
    set_main_event_loop(loop)
    
    # Database service prints its own messages, so we just call initialize
    await database_service.initialize()
    
    yield
    
    # Shutdown
    try:
        await database_service.close()
    except Exception as e:
        print(f"⚠️  Error closing database: {e}")

app = FastAPI(
    title="Church Games API",
    description="AI-powered pamphlet generation for kids church",
    version="1.0.0",
    lifespan=lifespan
)

# Initialize rate limiter
# Use IP address for rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS with security best practices
cors_origins_env = os.getenv('CORS_ORIGINS', '*')
is_production = os.getenv('FLASK_ENV', 'development').lower() == 'production'

if cors_origins_env == '*' or not cors_origins_env:
    if is_production:
        print("❌ ERROR: CORS_ORIGINS is set to '*' in production. This is a security risk!")
        print("   Please set CORS_ORIGINS to specific domain(s) in your .env file.")
        print("   Example: CORS_ORIGINS=https://kidschurch.bylwazi.co.za,https://www.kidschurch.bylwazi.co.za")
        import sys
        sys.exit(1)
    else:
        print("⚠️  WARNING: CORS_ORIGINS is set to '*' (allows all origins).")
        print("   This should be restricted to specific domains in production.")
        cors_origins = ['*']
        # Cannot use allow_credentials=True with allow_origins=['*']
        # Browsers reject this combination per CORS spec
        cors_allow_credentials = False
else:
    # Split comma-separated origins and strip whitespace
    cors_origins = [origin.strip() for origin in cors_origins_env.split(',') if origin.strip()]
    cors_allow_credentials = True
    if is_production:
        print(f"✅ CORS configured for production domains: {', '.join(cors_origins)}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=cors_allow_credentials,
    allow_methods=['GET', 'POST', 'DELETE'],
    allow_headers=['Content-Type'],
    max_age=3600,
)


# Request Models
class ThemeRequest(BaseModel):
    theme: str = Field(..., description="Theme for content generation")

class QuizRequest(BaseModel):
    theme: str = Field(..., description="Theme for quiz questions")
    num_questions: int = Field(default=10, ge=1, le=50, description="Number of questions")

class CrosswordWordsRequest(BaseModel):
    theme: str = Field(..., description="Theme for crossword words")
    num_words: int = Field(default=8, ge=3, le=20, description="Number of words")

class ColoringImageRequest(BaseModel):
    prompt: str = Field(..., description="Image generation prompt")
    theme: str = Field(..., description="Theme for the image")

class PamphletMetadata(BaseModel):
    church_name: str
    theme: str
    llm_call_id: Optional[int] = None

# Exception handlers
@app.exception_handler(APIError)
async def api_error_handler(request, exc: APIError):
    """Handle APIError exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            'success': False,
            'error': exc.message
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle general exceptions"""
    return JSONResponse(
        status_code=500,
        content={
            'success': False,
            'error': str(exc)
        }
    )


# Routes
@app.get('/health')
@limiter.limit("1000/minute")  # Health checks should have very high limit
async def health_check(request: Request):
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'message': 'Church Games Backend is running'
    }


@app.post('/api/generate-coloring-image')
@limiter.limit("15/minute")  # AI generation is expensive, limit strictly
async def generate_coloring_image(request: Request, coloring_request: ColoringImageRequest):
    """
    Generate a coloring image using AI
    """
    # Validate and sanitize inputs
    prompt = validate_prompt(coloring_request.prompt)
    theme = validate_theme(coloring_request.theme)
    
    if not prompt:
        raise APIError('Valid prompt is required', 400)
    if not theme:
        raise APIError('Valid theme is required', 400)
    
    # Generate image using AI service
    image_url = ai_service.generate_coloring_image(prompt, theme)
    
    return {
        'success': True,
        'image_url': image_url
    }


@app.post('/api/upload-pdf')
@limiter.limit("20/minute")  # File uploads are moderate cost
async def upload_pdf(
    request: Request,
    pdf: UploadFile = File(...),
    metadata: str = Form('{}')
):
    """
    Upload a generated PDF pamphlet to local storage
    """
    # Validate file extension
    # pdf.filename might be None if not provided in FormData
    filename = pdf.filename or 'pamphlet.pdf'
    if not validate_file_extension(filename):
        raise APIError('Only PDF files are allowed', 400)
    
    # Read file content
    file_content = await pdf.read()
    
    # Validate file size (max 10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    if len(file_content) > MAX_FILE_SIZE:
        raise APIError('File size exceeds maximum allowed size (10MB)', 400)
    if len(file_content) == 0:
        raise APIError('File is empty', 400)
    
    # Parse metadata
    try:
        metadata_dict = json.loads(metadata) if isinstance(metadata, str) else metadata
    except json.JSONDecodeError:
        raise APIError('Invalid metadata JSON format', 400)
    
    # Validate and sanitize metadata fields
    church_name = validate_church_name(metadata_dict.get('church_name'))
    theme = validate_theme(metadata_dict.get('theme'))
    
    if not church_name:
        raise APIError(f'Valid church_name is required in metadata. Got: {metadata_dict.get("church_name")}', 400)
    if not theme:
        raise APIError(f'Valid theme is required in metadata. Got: {metadata_dict.get("theme")}', 400)
    
    metadata_dict['church_name'] = church_name
    metadata_dict['theme'] = theme
    
    # Create a file-like object for pdf_storage_service
    from io import BytesIO
    pdf_file = BytesIO(file_content)
    pdf_file.name = filename
    
    # Save PDF to local filesystem (async)
    file_path, file_name = await pdf_storage_service.save_pdf(pdf_file, metadata_dict)
    
    # Get file size (async)
    file_size = await pdf_storage_service.get_file_size(file_path)
    
    # Save preview image if provided (after PDF is saved so we know the directory)
    preview_image_url = None
    preview_image_path = None
    if metadata_dict.get('preview_image_url'):
        try:
            import aiofiles
            import base64
            preview_url = metadata_dict.get('preview_image_url')
            
            # Handle base64 data URIs (from Gemini) or regular URLs
            if preview_url.startswith('data:'):
                # Extract base64 data from data URI
                # Format: data:image/png;base64,<base64data>
                header, data = preview_url.split(',', 1)
                image_data = base64.b64decode(data)
            else:
                # Download from URL
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get(preview_url) as response:
                        if response.status == 200:
                            image_data = await response.read()
                        else:
                            raise Exception(f"Failed to download image: HTTP {response.status}")
            
            # Save image to same directory as PDF
            # file_path is relative like "church-name/file.pdf"
            preview_filename = f"preview-{file_name.replace('.pdf', '.png')}"
            preview_path = pdf_storage_service.storage_path / file_path.replace(file_name, preview_filename)
            await asyncio.to_thread(preview_path.parent.mkdir, parents=True, exist_ok=True)
            async with aiofiles.open(preview_path, 'wb') as f:
                await f.write(image_data)
            # Store relative path same format as file_path
            preview_image_path = file_path.replace(file_name, preview_filename)
            print(f"✅ Preview image saved: {preview_image_path}")
        except Exception as e:
            print(f"⚠️  Failed to save preview image: {e}")
            import traceback
            traceback.print_exc()
    
    # Add preview image path to metadata
    if preview_image_path:
        metadata_dict['preview_image_path'] = preview_image_path
    
    # Save to database (async) - always save, regardless of preview image
    pamphlet_id = None
    if database_service.is_enabled():
        try:
            pamphlet_id = await database_service.create_pamphlet_record({
                'church_name': metadata_dict.get('church_name'),
                'theme': metadata_dict.get('theme'),
                'file_path': file_path,
                'file_name': file_name,
                'file_size_bytes': file_size or 0,
                'llm_call_id': metadata_dict.get('llm_call_id'),
                'metadata': metadata_dict,
                'preview_image_path': preview_image_path  # Store separately, not in JSON
            })
            if pamphlet_id:
                print(f"✅ Pamphlet saved to database with ID: {pamphlet_id}")
                # Update preview_image_url now that we have the pamphlet_id
                if preview_image_path:
                    preview_image_url = f'/api/pamphlets/{pamphlet_id}/preview'
            else:
                print(f"⚠️  Failed to save pamphlet to database (pamphlet_id is None)")
        except Exception as e:
            print(f"❌ Error saving pamphlet to database: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("⚠️  Database not enabled, skipping database save")
    
    return {
        'success': True,
        'pamphlet_id': pamphlet_id,
        'file_path': file_path,
        'file_name': file_name,
        'download_url': f'/api/pamphlets/{pamphlet_id}/download' if pamphlet_id else None
    }


@app.post('/api/generate-quiz')
@limiter.limit("10/minute")  # AI generation is expensive
async def generate_quiz(request: Request, quiz_request: QuizRequest):
    """
    Generate quiz questions using AI
    """
    # Validate and sanitize inputs
    theme = validate_theme(quiz_request.theme)
    num_questions = validate_int(quiz_request.num_questions, min_value=1, max_value=50)
    
    if not theme:
        raise APIError('Valid theme is required', 400)
    if not num_questions:
        raise APIError('num_questions must be between 1 and 50', 400)
    
    # Generate questions using AI service
    questions = ai_service.generate_quiz_questions(theme, num_questions)
    
    return {
        'success': True,
        'questions': questions
    }


@app.post('/api/generate-crossword-words')
@limiter.limit("10/minute")  # AI generation is expensive
async def generate_crossword_words(request: Request, words_request: CrosswordWordsRequest):
    """
    Generate crossword words using AI
    """
    # Validate and sanitize inputs
    theme = validate_theme(words_request.theme)
    num_words = validate_int(words_request.num_words, min_value=3, max_value=20)
    
    if not theme:
        raise APIError('Valid theme is required', 400)
    if not num_words:
        raise APIError('num_words must be between 3 and 20', 400)
    
    # Generate words using AI service
    words = ai_service.generate_crossword_words(theme, num_words)
    
    return {
        'success': True,
        'words': words
    }


@app.post('/api/generate-crossword')
@limiter.limit("10/minute")  # AI generation is expensive
async def generate_crossword(request: Request, theme_request: ThemeRequest):
    """
    Generate a complete crossword puzzle using AI
    """
    # Validate and sanitize inputs
    theme = validate_theme(theme_request.theme)
    
    if not theme:
        raise APIError('Valid theme is required', 400)
    
    # Generate complete crossword using AI service
    puzzle = ai_service.generate_crossword(theme)
    
    return {
        'success': True,
        **puzzle
    }


@app.post('/api/generate-pamphlet-content')
@limiter.limit("5/minute")  # Most expensive endpoint - generates all content + images
async def generate_pamphlet_content(request: Request, theme_request: ThemeRequest):
    """
    Generate all pamphlet content in one LLM call
    """
    # Validate and sanitize inputs
    theme = validate_theme(theme_request.theme)
    
    if not theme:
        raise APIError('Valid theme is required', 400)
    
    # Generate all content using AI service (sync method)
    # For better performance, we could make this async in the future
    content = ai_service.generate_pamphlet_content(theme)
    
    return {
        'success': True,
        **content
    }


@app.get('/api/config')
@limiter.limit("60/minute")  # Read-only endpoint, more lenient
async def get_config(request: Request):
    """
    Get backend configuration (non-sensitive)
    """
    return {
        'ai_provider': ai_service.provider_name,
        'image_generation_enabled': ai_service.is_enabled(),
        'database_enabled': database_service.is_enabled(),
        'supported_providers': ['openai', 'anthropic', 'gemini']
    }


# ============================================================================
# PDF History API Endpoints
# ============================================================================

@app.get('/api/pamphlets')
@limiter.limit("60/minute")  # Read-only endpoint, more lenient
async def get_pamphlets(
    request: Request,
    church_name: Optional[str] = Query(None, description="Filter by church name"),
    theme: Optional[str] = Query(None, description="Filter by theme"),
    limit: int = Query(20, ge=1, le=100, description="Number of results"),
    offset: int = Query(0, ge=0, le=10000, description="Pagination offset"),
    sort: str = Query('created_at', description="Sort field"),
    order: str = Query('desc', description="Sort order (asc/desc)")
):
    """
    Get list of pamphlets with filters and pagination
    """
    # Validate and sanitize query parameters
    church_name = sanitize_string(church_name) if church_name else None
    theme = sanitize_string(theme) if theme else None
    
    # Validate sort field
    allowed_sort_fields = ['created_at', 'church_name', 'theme', 'file_size_bytes']
    if sort not in allowed_sort_fields:
        sort = 'created_at'
    
    # Validate order
    if order.lower() not in ['asc', 'desc']:
        order = 'desc'
    else:
        order = order.lower()
    
    filters = {
        'church_name': church_name,
        'theme': theme,
        'limit': limit,
        'offset': offset,
        'sort': sort,
        'order': order
    }
    
    # Remove None values
    filters = {k: v for k, v in filters.items() if v is not None}
    
    try:
        pamphlets, total = await database_service.get_pamphlets(filters)
    except Exception as e:
        print(f"❌ Error fetching pamphlets: {e}")
        import traceback
        traceback.print_exc()
        raise APIError(f'Failed to fetch pamphlets: {str(e)}', 500)
    
    return {
        'success': True,
        'pamphlets': pamphlets,
        'total': total,
        'limit': filters.get('limit', 20),
        'offset': filters.get('offset', 0)
    }


@app.get('/api/pamphlets/{pamphlet_id}')
@limiter.limit("60/minute")  # Read-only endpoint
async def get_pamphlet(
    request: Request,
    pamphlet_id: int = PathParam(..., gt=0, description="Pamphlet ID")
):
    """
    Get a single pamphlet by ID
    """
    pamphlet = await database_service.get_pamphlet_by_id(pamphlet_id)
    
    if not pamphlet:
        raise APIError('Pamphlet not found', 404)
    
    return {
        'success': True,
        'pamphlet': pamphlet
    }


@app.get('/api/pamphlets/{pamphlet_id}/preview')
@limiter.limit("60/minute")  # Read-only endpoint
async def get_preview_image(
    request: Request,
    pamphlet_id: int = PathParam(..., gt=0, description="Pamphlet ID")
):
    """
    Get preview image for a pamphlet
    """
    # Get pamphlet record
    pamphlet = await database_service.get_pamphlet_by_id(pamphlet_id)
    
    if not pamphlet:
        raise APIError('Pamphlet not found', 404)
    
    # Get preview image path from column (not from metadata JSON)
    preview_path = pamphlet.get('preview_image_path')
    
    if not preview_path:
        raise APIError('Preview image not found', 404)
    
    # Get file path
    file_path = await pdf_storage_service.get_file_path(preview_path)
    
    if not file_path or not Path(file_path).exists():
        raise APIError('Preview image file not found', 404)
    
    # Return image file
    return FileResponse(
        path=file_path,
        media_type='image/png',
        headers={
            'Cache-Control': 'public, max-age=31536000'  # Cache for 1 year
        }
    )


@app.get('/api/pamphlets/{pamphlet_id}/download')
@limiter.limit("30/minute")  # File downloads, moderate limit
async def download_pamphlet(
    request: Request,
    pamphlet_id: int = PathParam(..., gt=0, description="Pamphlet ID")
):
    """
    Download a PDF pamphlet file
    """
    # Get pamphlet record
    pamphlet = await database_service.get_pamphlet_by_id(pamphlet_id)
    
    if not pamphlet:
        raise APIError('Pamphlet not found', 404)
    
    # Get file path
    file_path = await pdf_storage_service.get_file_path(pamphlet['file_path'])
    
    if not file_path or not Path(file_path).exists():
        raise APIError('PDF file not found', 404)
    
    # Return file using FastAPI's FileResponse
    return FileResponse(
        path=file_path,
        filename=pamphlet['file_name'],
        media_type='application/pdf',
        headers={
            'Content-Disposition': f'attachment; filename="{pamphlet["file_name"]}"'
        }
    )


@app.delete('/api/pamphlets/{pamphlet_id}')
@limiter.limit("20/minute")  # Delete operations, moderate limit
async def delete_pamphlet(
    request: Request,
    pamphlet_id: int = PathParam(..., gt=0, description="Pamphlet ID")
):
    """
    Soft delete a pamphlet
    """
    success = await database_service.delete_pamphlet(pamphlet_id)
    
    if not success:
        raise APIError('Pamphlet not found', 404)
    
    return {
        'success': True,
        'message': 'Pamphlet deleted successfully'
    }


@app.get('/api/usage/stats')
@limiter.limit("30/minute")  # Stats endpoint, moderate limit
async def get_usage_stats(
    request: Request,
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    provider: Optional[str] = Query(None, description="Filter by provider")
):
    """
    Get usage statistics for LLM API calls
    """
    start_date_obj = None
    end_date_obj = None
    
    if start_date:
        try:
            start_date_obj = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        except:
            raise APIError('Invalid start_date format. Use ISO format.', 400)
    
    if end_date:
        try:
            end_date_obj = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except:
            raise APIError('Invalid end_date format. Use ISO format.', 400)
    
    stats = await database_service.get_usage_stats(
        start_date=start_date_obj,
        end_date=end_date_obj,
        provider=provider
    )
    
    return {
        'success': True,
        'stats': stats
    }


if __name__ == '__main__':
    import uvicorn
    
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print(f"🚀 Starting Church Games Backend on port {port}")
    print(f"📊 AI Provider: {ai_service.provider_name}")
    print(f"💾 Database: {'Enabled' if database_service.is_enabled() else 'Will initialize on first request'}")
    print(f"📁 PDF Storage: {pdf_storage_service.storage_path}")
    print(f"\n⚠️  Using Uvicorn development server. For production, use: ./start.sh\n")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=debug,
        log_level="debug" if debug else "info"
    )

