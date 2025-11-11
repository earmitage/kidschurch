"""
Environment variable validation
Validates required environment variables on startup
"""

import os
import sys
from typing import List, Tuple, Optional


class EnvValidationError(Exception):
    """Raised when environment validation fails"""
    pass


def validate_required_env_vars() -> Tuple[bool, List[str], List[str]]:
    """
    Validate required environment variables
    
    Returns:
        Tuple of (is_valid, list_of_errors, list_of_warnings)
    """
    errors = []
    warnings = []
    
    # Determine environment
    flask_env = os.getenv('FLASK_ENV', 'development').lower()
    is_production = flask_env == 'production'
    
    # Required for all environments
    ai_provider = os.getenv('AI_PROVIDER', '').lower()
    if not ai_provider:
        errors.append("AI_PROVIDER is required (options: 'openai', 'anthropic', 'gemini')")
    elif ai_provider not in ['openai', 'anthropic', 'gemini', 'mock']:
        errors.append(f"AI_PROVIDER '{ai_provider}' is invalid. Must be one of: 'openai', 'anthropic', 'gemini', 'mock'")
    
    # Provider-specific API keys
    if ai_provider == 'openai':
        if not os.getenv('OPENAI_API_KEY'):
            errors.append("OPENAI_API_KEY is required when AI_PROVIDER=openai")
    elif ai_provider == 'anthropic':
        if not os.getenv('ANTHROPIC_API_KEY'):
            errors.append("ANTHROPIC_API_KEY is required when AI_PROVIDER=anthropic")
    elif ai_provider == 'gemini':
        if not os.getenv('GOOGLE_API_KEY'):
            errors.append("GOOGLE_API_KEY is required when AI_PROVIDER=gemini")
    
    # Database configuration (optional but recommended)
    mysql_user = os.getenv('MYSQL_USER')
    mysql_password = os.getenv('MYSQL_PASSWORD')
    if not mysql_user or not mysql_password:
        warnings.append("MYSQL_USER and MYSQL_PASSWORD not set. Database features will be disabled.")
    
    # Production-specific validations
    if is_production:
        # CORS origins should not be wildcard in production
        cors_origins = os.getenv('CORS_ORIGINS', '*')
        if cors_origins == '*' or not cors_origins:
            errors.append("CORS_ORIGINS must be set to specific domain(s) in production (not '*')")
        
        # Port should be explicitly set
        port = os.getenv('PORT')
        if not port:
            warnings.append("PORT not explicitly set. Using default 5001.")
        
        # Workers should be set for production
        workers = os.getenv('WORKERS')
        if not workers:
            warnings.append("WORKERS not set. Using default. Consider setting based on CPU cores.")
    
    # PDF storage path validation
    pdf_storage_path = os.getenv('PDF_STORAGE_PATH')
    if pdf_storage_path:
        from pathlib import Path
        storage_path = Path(pdf_storage_path)
        if not storage_path.exists():
            try:
                storage_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create PDF_STORAGE_PATH '{pdf_storage_path}': {e}")
    
    return len(errors) == 0, errors, warnings


def validate_and_exit_on_error():
    """
    Validate environment variables and exit if critical errors found
    Prints warnings but continues if only warnings
    """
    is_valid, errors, warnings = validate_required_env_vars()
    
    # Print warnings
    if warnings:
        print("⚠️  Environment Configuration Warnings:")
        for warning in warnings:
            print(f"   - {warning}")
        print()
    
    # Print errors and exit if critical
    if not is_valid:
        print("❌ Environment Configuration Errors:")
        for error in errors:
            print(f"   - {error}")
        print()
        print("Please fix the above errors and restart the application.")
        sys.exit(1)
    
    # Success message
    if is_valid and not warnings:
        print("✅ Environment configuration validated successfully")
    elif is_valid:
        print("✅ Environment configuration validated (with warnings)")
    
    return is_valid

