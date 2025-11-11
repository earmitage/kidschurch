"""
Error handling utilities
Security: Don't expose sensitive information in error messages
Works with both Flask and FastAPI
"""


class APIError(Exception):
    """Custom API error class"""
    
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

