"""
AI Service router - select and configure AI provider
"""

import os


class AIService:
    """
    Main AI service that routes to the configured provider
    
    Configure via AI_PROVIDER environment variable:
    - 'openai': Use OpenAI GPT (default)
    - 'anthropic': Use Anthropic Claude
    - 'gemini': Use Google Gemini
    
    Uses lazy imports to reduce memory usage - only loads the configured provider.
    """
    
    def __init__(self):
        provider = os.getenv('AI_PROVIDER', 'openai').lower()
        
        # Lazy import - only load the provider that's actually needed
        if provider == 'openai':
            from .ai_providers.openai_service import OpenAIService
            self._service = OpenAIService()
        elif provider == 'anthropic' or provider == 'claude':
            from .ai_providers.anthropic_service import AnthropicService
            self._service = AnthropicService()
        elif provider == 'gemini' or provider == 'google':
            from .ai_providers.gemini_service import GeminiService
            self._service = GeminiService()
        else:
            print(f"❌ Unknown AI provider '{provider}', use 'openai', 'anthropic', or 'gemini'")
            raise ValueError(f"Invalid AI provider: {provider}")
        
        self.provider_name = self._service.provider_name
        print(f"🤖 AI Provider initialized: {self.provider_name}")
        
        if not self._service.is_enabled():
            print(f"⚠️  {self.provider_name} is not properly configured. Check your API keys.")
    
    def generate_coloring_image(self, prompt: str, theme: str) -> str:
        """Generate a coloring image using the configured AI provider"""
        return self._service.generate_coloring_image(prompt, theme)
    
    def generate_quiz_questions(self, theme: str, num_questions: int = 10) -> list:
        """Generate quiz questions using the configured AI provider"""
        return self._service.generate_quiz_questions(theme, num_questions)
    
    def generate_crossword_words(self, theme: str, num_words: int = 8) -> list:
        """Generate crossword words using the configured AI provider"""
        return self._service.generate_crossword_words(theme, num_words)
    
    def generate_crossword(self, theme: str) -> dict:
        """Generate a complete crossword puzzle using the configured AI provider"""
        return self._service.generate_crossword(theme)
    
    def generate_pamphlet_content(self, theme: str) -> dict:
        """Generate all pamphlet content in one LLM call"""
        return self._service.generate_pamphlet_content(theme)
    
    def is_enabled(self) -> bool:
        """Check if AI service is enabled and configured"""
        return self._service.is_enabled()
