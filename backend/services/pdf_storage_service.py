"""
Local PDF Storage Service
Handles async file operations for saving and retrieving PDFs
"""

import os
import asyncio
import aiofiles
from datetime import datetime
from typing import Tuple, Optional
from pathlib import Path


class PDFStorageService:
    """
    Async PDF storage service for local filesystem
    
    Environment variables:
    - PDF_STORAGE_DIR (default: pdfs) - Relative to backend directory
    - PDF_STORAGE_PATH (optional) - Full path to storage directory
    """
    
    def __init__(self):
        # Determine storage directory
        storage_dir = os.getenv('PDF_STORAGE_DIR', 'pdfs')
        storage_path = os.getenv('PDF_STORAGE_PATH')
        
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            # Relative to backend directory
            backend_dir = Path(__file__).parent.parent
            self.storage_path = backend_dir / storage_dir
        
        # Ensure storage directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ PDF storage initialized: {self.storage_path}")
    
    def _sanitize_filename(self, name: str) -> str:
        """Sanitize filename to prevent directory traversal"""
        # Remove path separators and dangerous characters
        sanitized = name.replace('/', '-').replace('\\', '-').replace('..', '-')
        # Remove other potentially dangerous characters
        sanitized = ''.join(c for c in sanitized if c.isalnum() or c in (' ', '-', '_', '.'))
        return sanitized.strip()
    
    async def save_pdf(self, pdf_file, metadata: dict = None) -> Tuple[str, str]:
        """
        Save PDF file to local filesystem
        
        Args:
            pdf_file: Flask FileStorage object or file-like object
            metadata: Dictionary with church_name, theme, etc.
            
        Returns:
            Tuple of (file_path, file_name)
            
        Raises:
            Exception: If save fails
        """
        try:
            # Generate directory name from church name
            church_name = metadata.get('church_name', 'unknown') if metadata else 'unknown'
            theme = metadata.get('theme', 'generic') if metadata else 'generic'
            
            # Sanitize names
            church_dir = self._sanitize_filename(church_name.lower())
            theme_name = self._sanitize_filename(theme.lower())
            
            # Create church directory
            church_path = self.storage_path / church_dir
            await asyncio.to_thread(church_path.mkdir, parents=True, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            file_name = f"{theme_name}-{timestamp}.pdf"
            
            # Full file path
            file_path = church_path / file_name
            
            # Read file content
            if hasattr(pdf_file, 'read'):
                # FileStorage object
                pdf_file.seek(0)
                content = pdf_file.read()
            else:
                # Already bytes or file path
                content = pdf_file if isinstance(pdf_file, bytes) else await aiofiles.open(pdf_file, 'rb').read()
            
            # Write file asynchronously
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)
            
            # Return relative path from storage root and filename
            relative_path = f"{church_dir}/{file_name}"
            return str(relative_path), file_name
            
        except Exception as e:
            raise Exception(f"Failed to save PDF: {str(e)}")
    
    async def get_file_path(self, relative_path: str) -> Optional[Path]:
        """
        Get full file path from relative path
        
        Args:
            relative_path: Relative path from storage root (e.g., 'church-name/file.pdf')
            
        Returns:
            Full Path object, or None if invalid
        """
        try:
            # Prevent directory traversal
            if '..' in relative_path or '/' not in relative_path:
                return None
            
            full_path = self.storage_path / relative_path
            
            # Ensure path is within storage directory
            if not str(full_path.resolve()).startswith(str(self.storage_path.resolve())):
                return None
            
            # Check if file exists
            if not await asyncio.to_thread(full_path.exists):
                return None
            
            return full_path
        except Exception as e:
            print(f"⚠️  Failed to get file path: {e}")
            return None
    
    async def get_file_size(self, relative_path: str) -> Optional[int]:
        """Get file size in bytes"""
        file_path = await self.get_file_path(relative_path)
        if file_path:
            def _get_size(p: Path) -> int:
                return p.stat().st_size
            return await asyncio.to_thread(_get_size, file_path)
        return None
    
    async def delete_file(self, relative_path: str) -> bool:
        """Delete a PDF file"""
        try:
            file_path = await self.get_file_path(relative_path)
            if file_path:
                await asyncio.to_thread(file_path.unlink)
                return True
            return False
        except Exception as e:
            print(f"⚠️  Failed to delete file: {e}")
            return False
    
    async def read_file(self, relative_path: str) -> Optional[bytes]:
        """Read PDF file content"""
        try:
            file_path = await self.get_file_path(relative_path)
            if file_path:
                async with aiofiles.open(file_path, 'rb') as f:
                    return await f.read()
            return None
        except Exception as e:
            print(f"⚠️  Failed to read file: {e}")
            return None

