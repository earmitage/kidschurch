"""
Anthropic Claude implementation
"""

import os
import json
import re
from .base import AIServiceBase, QUIZ_GENERATION_CONFIG, CROSSWORD_CONFIG, PAMPHLET_CONTENT_CONFIG, build_quiz_user_prompt, build_crossword_words_prompt, build_pamphlet_content_prompt
from utils.tracking import track_llm_call


class AnthropicService(AIServiceBase):
    """Anthropic Claude implementation"""
    
    def __init__(self):
        self.provider_name = "Anthropic Claude"
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        self.model = os.getenv('ANTHROPIC_MODEL', 'claude-3-haiku-20240307')
        self._client = None
        
        if self.api_key:
            try:
                from anthropic import Anthropic
                self._client = Anthropic(api_key=self.api_key)
            except ImportError:
                print("⚠️  Anthropic package not installed. Run: pip install anthropic")
    
    def is_enabled(self) -> bool:
        return self._client is not None and self.api_key is not None
    
    def generate_coloring_image(self, prompt: str, theme: str) -> str:
        """Not implemented - Anthropic doesn't do image generation"""
        raise NotImplementedError("Image generation not available with Anthropic. Use OpenAI or Stable Diffusion.")
    
    @track_llm_call('generate_quiz_questions')
    def generate_quiz_questions(self, theme: str, num_questions: int = 10) -> list:
        """Generate quiz questions using Anthropic Claude"""
        if not self.is_enabled():
            raise Exception("Anthropic service is not properly configured")
        
        try:
            response = self._client.messages.create(
                model=self.model,
                max_tokens=QUIZ_GENERATION_CONFIG['max_tokens'],
                system=QUIZ_GENERATION_CONFIG['system_prompt'],
                messages=[
                    {"role": "user", "content": build_quiz_user_prompt(theme, num_questions)}
                ]
            )
            
            text = response.content[0].text
            return self._parse_quiz_response(text, num_questions)
            
        except Exception as e:
            raise Exception(f"Failed to generate questions with Anthropic: {str(e)}")
    
    @track_llm_call('generate_crossword_words')
    def generate_crossword_words(self, theme: str, num_words: int = 8) -> list:
        """Generate crossword words using Anthropic Claude"""
        if not self.is_enabled():
            raise Exception("Anthropic service is not properly configured")
        
        try:
            response = self._client.messages.create(
                model=self.model,
                max_tokens=CROSSWORD_CONFIG['max_tokens'],
                system=CROSSWORD_CONFIG['system_prompt'],
                messages=[
                    {"role": "user", "content": build_crossword_words_prompt(theme, num_words)}
                ]
            )
            
            text = response.content[0].text
            return self._parse_crossword_words_response(text, num_words)
            
        except Exception as e:
            raise Exception(f"Failed to generate crossword words with Anthropic: {str(e)}")
    
    @track_llm_call('generate_pamphlet_content')
    def generate_pamphlet_content(self, theme: str) -> dict:
        """Generate all pamphlet content in one LLM call, then generate coloring images"""
        if not self.is_enabled():
            raise Exception("Anthropic service is not properly configured")
        
        try:
            response = self._client.messages.create(
                model=self.model,
                max_tokens=PAMPHLET_CONTENT_CONFIG['max_tokens'],
                system=PAMPHLET_CONTENT_CONFIG['system_prompt'],
                messages=[
                    {"role": "user", "content": build_pamphlet_content_prompt(theme)}
                ]
            )
            
            text = response.content[0].text
            
            # Extract JSON from markdown code blocks if present
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
            if json_match:
                text = json_match.group(1)
            else:
                # Try to find JSON object directly
                json_match = re.search(r'\{.*\}', text, re.DOTALL)
                if json_match:
                    text = json_match.group(0)
            
            content = json.loads(text)
            
            # Generate coloring images if prompts are available
            if 'coloringTextPrompt' in content and 'coloringScenePrompt' in content:
                try:
                    # Use OpenAI for image generation (Anthropic doesn't support it)
                    from .openai_service import OpenAIService
                    image_service = OpenAIService()
                    
                    if image_service.is_enabled():
                        # Generate both images in parallel using threading
                        import concurrent.futures
                        
                        def generate_text_image():
                            return image_service.generate_coloring_image(
                                content['coloringTextPrompt'], theme
                            )
                        
                        def generate_scene_image():
                            return image_service.generate_coloring_image(
                                content['coloringScenePrompt'], theme
                            )
                        
                        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                            text_future = executor.submit(generate_text_image)
                            scene_future = executor.submit(generate_scene_image)
                            
                            content['coloringTextImageUrl'] = text_future.result()
                            content['coloringSceneImageUrl'] = scene_future.result()
                    else:
                        error_msg = "Anthropic does not support image generation. Configure AI_PROVIDER=openai with OPENAI_API_KEY in backend/.env file for image generation."
                        print(f"⚠️  {error_msg}")
                        content['coloringTextImageUrl'] = None
                        content['coloringSceneImageUrl'] = None
                        content['coloringImageError'] = error_msg
                        
                except Exception as e:
                    error_msg = f"Failed to generate coloring images: {str(e)}"
                    print(f"⚠️  {error_msg}")
                    content['coloringTextImageUrl'] = None
                    content['coloringSceneImageUrl'] = None
                    content['coloringImageError'] = error_msg
            else:
                content['coloringTextImageUrl'] = None
                content['coloringSceneImageUrl'] = None
            
            return content
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse pamphlet content JSON from Anthropic: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to generate pamphlet content with Anthropic: {str(e)}")

