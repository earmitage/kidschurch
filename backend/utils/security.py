"""
Security utilities for input validation and sanitization
"""

import re
from typing import Optional


def validate_theme(theme: str, max_length: int = 255) -> Optional[str]:
    """
    Validate and sanitize theme input
    
    Args:
        theme: Theme string to validate
        max_length: Maximum allowed length
        
    Returns:
        Sanitized theme or None if invalid
    """
    if not theme or not isinstance(theme, str):
        return None
    
    # Remove leading/trailing whitespace
    theme = theme.strip()
    
    # Check length
    if len(theme) == 0 or len(theme) > max_length:
        return None
    
    # Remove dangerous characters but allow basic punctuation
    # Allow letters, numbers, spaces, hyphens, apostrophes
    theme = re.sub(r'[^\w\s\-\']', '', theme)
    
    return theme if theme else None


def validate_church_name(church_name: str, max_length: int = 255) -> Optional[str]:
    """
    Validate and sanitize church name input
    
    Args:
        church_name: Church name string to validate
        max_length: Maximum allowed length
        
    Returns:
        Sanitized church name or None if invalid
    """
    if not church_name or not isinstance(church_name, str):
        return None
    
    # Remove leading/trailing whitespace
    church_name = church_name.strip()
    
    # Check length
    if len(church_name) == 0 or len(church_name) > max_length:
        return None
    
    # Remove dangerous characters but allow basic punctuation
    church_name = re.sub(r'[^\w\s\-\'\.]', '', church_name)
    
    return church_name if church_name else None


def validate_prompt(prompt: str, max_length: int = 500) -> Optional[str]:
    """
    Validate and sanitize prompt input
    
    Args:
        prompt: Prompt string to validate
        max_length: Maximum allowed length
        
    Returns:
        Sanitized prompt or None if invalid
    """
    if not prompt or not isinstance(prompt, str):
        return None
    
    # Remove leading/trailing whitespace
    prompt = prompt.strip()
    
    # Check length
    if len(prompt) == 0 or len(prompt) > max_length:
        return None
    
    # Basic sanitization - remove null bytes and control characters
    prompt = prompt.replace('\x00', '').replace('\r', '')
    prompt = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', prompt)
    
    return prompt if prompt else None


def validate_int(value: any, min_value: int = 1, max_value: int = 100) -> Optional[int]:
    """
    Validate integer input with min/max bounds
    
    Args:
        value: Value to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        
    Returns:
        Validated integer or None if invalid
    """
    try:
        int_value = int(value)
        if min_value <= int_value <= max_value:
            return int_value
    except (ValueError, TypeError):
        pass
    return None


def validate_file_extension(filename: str, allowed_extensions: set = None) -> bool:
    """
    Validate file extension
    
    Args:
        filename: Filename to check
        allowed_extensions: Set of allowed extensions (default: {'pdf'})
        
    Returns:
        True if extension is allowed, False otherwise
    """
    if allowed_extensions is None:
        allowed_extensions = {'pdf'}
    
    if not filename:
        return False
    
    # Get extension
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    
    return ext in allowed_extensions


def sanitize_string(value: str, max_length: int = 500) -> Optional[str]:
    """
    General string sanitization
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string or None if invalid
    """
    if not value or not isinstance(value, str):
        return None
    
    # Remove leading/trailing whitespace
    value = value.strip()
    
    # Check length
    if len(value) == 0 or len(value) > max_length:
        return None
    
    # Remove null bytes and control characters
    value = value.replace('\x00', '')
    value = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', value)
    
    return value if value else None


