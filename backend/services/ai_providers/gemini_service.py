"""
Google Gemini implementation
"""

import os
import json
import re
import requests
import base64
from .base import AIServiceBase, QUIZ_GENERATION_CONFIG, CROSSWORD_CONFIG, PAMPHLET_CONTENT_CONFIG, build_quiz_user_prompt, build_crossword_words_prompt, build_pamphlet_content_prompt
from utils.tracking import track_llm_call


class GeminiService(AIServiceBase):
    """Google Gemini implementation"""
    
    def __init__(self):
        self.provider_name = "Google Gemini"
        self.api_key = os.getenv('GOOGLE_API_KEY')
        self.model = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')
        self._client = None
        self._image_model = os.getenv('GEMINI_IMAGE_MODEL', 'gemini-2.0-flash-exp')  # Default, will try gemini-2.5-flash-image if available
        
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._client = genai.GenerativeModel(self.model)
                print(f"✅ Gemini client initialized with API key")
            except ImportError:
                print("⚠️  Google Generative AI package not installed. Run: pip install google-generativeai")

    
    def is_enabled(self) -> bool:
        return self._client is not None and self.api_key is not None
    
    @track_llm_call('generate_coloring_image')
    def generate_coloring_image(self, prompt: str, theme: str) -> str:
        """Generate image using Gemini REST API with API key authentication"""
        if not self.is_enabled():
            raise Exception("Gemini service is not properly configured")
        
        if not self.api_key:
            raise Exception("GOOGLE_API_KEY not set. Image generation requires an API key.")
        
        from .base import build_coloring_prompt
        
        # Build the full prompt
        full_prompt = build_coloring_prompt(prompt, theme)
        
        # Use Gemini REST API with API key
        # gemini-2.0-flash-preview-image-generation does NOT support aspectRatio
        # gemini-2.5-flash-image DOES support aspectRatio (but may require Vertex AI)
        image_model = os.getenv('GEMINI_IMAGE_MODEL', 'gemini-2.0-flash-preview-image-generation')
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{image_model}:generateContent"
        
        # Prepare request payload
        # Image generation models require both TEXT and IMAGE in responseModalities
        generation_config = {
            "temperature": 0.7,
            "maxOutputTokens": 2048,
            "responseModalities": ["TEXT", "IMAGE"]  # Required for image generation models
        }
        
        # Only include imageConfig with aspectRatio for models that support it
        # gemini-2.0-flash-preview-image-generation does NOT support aspectRatio
        # gemini-2.5-flash-image DOES support aspectRatio
        # Check if model is 2.5-flash-image (not preview version)
        supports_aspect_ratio = (
            "2.5" in image_model and "flash-image" in image_model and "preview" not in image_model
        )
        if supports_aspect_ratio:
            generation_config["imageConfig"] = {
                "aspectRatio": "1:1"  # Square format for coloring pages
            }
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": full_prompt
                }]
            }],
            "generationConfig": generation_config
        }
        
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }
        
        try:
            response = requests.post(api_url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            
            # Extract image data from response
            if 'candidates' not in result or not result['candidates']:
                raise Exception("No candidates in response")
            
            candidate = result['candidates'][0]
            if 'content' not in candidate or 'parts' not in candidate['content']:
                raise Exception("No content parts in response")
            
            image_data = None
            for part in candidate['content']['parts']:
                # Check for inline_data with image
                if 'inlineData' in part:
                    inline_data = part['inlineData']
                    if 'data' in inline_data:
                        # Decode base64 image data
                        image_data = base64.b64decode(inline_data['data'])
                        if image_data:
                            break
            
            if not image_data:
                raise Exception("No image data found in response. The model may not support image generation via REST API.")
            
            # Convert image data to base64 data URI for frontend
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            mime_type = "image/png"  # Gemini typically returns PNG
            data_uri = f"data:{mime_type};base64,{image_base64}"
            
            return data_uri
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            if e.response.status_code == 404:
                raise Exception(
                    f"Gemini image model '{image_model}' not found or not available via REST API.\n"
                    "This model may only be available via Vertex AI.\n"
                    f"Original error: {error_msg}"
                )
            raise Exception(f"Failed to generate image with Gemini: {error_msg}")
        except Exception as e:
            error_msg = str(e)
            raise Exception(f"Failed to generate image with Gemini: {error_msg}")
    
    @track_llm_call('generate_quiz_questions')
    def generate_quiz_questions(self, theme: str, num_questions: int = 10) -> list:
        """Generate quiz questions using Google Gemini"""
        if not self.is_enabled():
            raise Exception("Gemini service is not properly configured")
        
        try:
            # Gemini doesn't have separate system/user, combine them
            full_prompt = (
                f"{QUIZ_GENERATION_CONFIG['system_prompt']}\n\n"
                f"{build_quiz_user_prompt(theme, num_questions)}"
            )
            
            response = self._client.generate_content(
                full_prompt,
                generation_config={
                    'temperature': QUIZ_GENERATION_CONFIG['temperature'],
                    'max_output_tokens': QUIZ_GENERATION_CONFIG['max_tokens'],
                }
            )
            
            text = response.text
            return self._parse_quiz_response(text, num_questions)
            
        except Exception as e:
            raise Exception(f"Failed to generate questions with Gemini: {str(e)}")
    
    @track_llm_call('generate_crossword_words')
    def generate_crossword_words(self, theme: str, num_words: int = 8) -> list:
        """Generate crossword words using Google Gemini"""
        if not self.is_enabled():
            raise Exception("Gemini service is not properly configured")
        
        try:
            # Gemini doesn't have separate system/user, combine them
            full_prompt = (
                f"{CROSSWORD_CONFIG['system_prompt']}\n\n"
                f"{build_crossword_words_prompt(theme, num_words)}"
            )
            
            response = self._client.generate_content(
                full_prompt,
                generation_config={
                    'temperature': CROSSWORD_CONFIG['temperature'],
                    'max_output_tokens': CROSSWORD_CONFIG['max_tokens'],
                }
            )
            
            text = response.text
            return self._parse_crossword_words_response(text, num_words)
            
        except Exception as e:
            raise Exception(f"Failed to generate crossword words with Gemini: {str(e)}")
    
    def generate_crossword(self, theme: str) -> dict:
        """Generate a complete crossword puzzle with grid and clues using Gemini"""
        if not self.is_enabled():
            raise Exception("Gemini service is not properly configured")
        
        prompt = f'''You are creating a crossword puzzle for 5-year-old children about the biblical theme "{theme}".

REQUIREMENTS:
- Generate exactly 8 words (3-8 letters each)
- Words must intersect and share letters
- All words must be related to the theme
- Use simple, kid-friendly clues
- Grid must be 10x10 cells maximum

Return ONLY valid JSON in this format:
{{
  "title": "{theme} Crossword",
  "grid": [["A","R","K","",""],["","","N","",""],["","","O","",""],["","","A","",""],["","","H","",""]],
  "words": [
    {{ "number": 1, "direction": "across", "row": 0, "col": 0, "clue": "What Noah built", "answer": "ARK" }},
    {{ "number": 2, "direction": "down", "row": 0, "col": 2, "clue": "Who built the boat", "answer": "NOAH" }}
  ]
}}

CRITICAL: The grid must exactly match where the words are placed. Use "" for empty cells.'''

        try:
            response = self._client.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.2,
                    'max_output_tokens': 2500,
                }
            )
            
            text = response.text
            
            # Extract JSON from markdown code blocks if present
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
            if json_match:
                text = json_match.group(1)
            else:
                # Try to find JSON object directly
                json_match = re.search(r'\{.*\}', text, re.DOTALL)
                if json_match:
                    text = json_match.group(0)
            
            puzzle = json.loads(text)
            return puzzle
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse crossword JSON from Gemini: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to generate crossword with Gemini: {str(e)}")
    
    @track_llm_call('generate_pamphlet_content')
    def generate_pamphlet_content(self, theme: str) -> dict:
        """Generate all pamphlet content in one LLM call, then generate coloring images"""
        if not self.is_enabled():
            raise Exception("Gemini service is not properly configured")
        
        try:
            # Build the combined prompt
            full_prompt = (
                f"{PAMPHLET_CONTENT_CONFIG['system_prompt']}\n\n"
                f"{build_pamphlet_content_prompt(theme)}"
            )
            
            response = self._client.generate_content(
                full_prompt,
                generation_config={
                    'temperature': PAMPHLET_CONTENT_CONFIG['temperature'],
                    'max_output_tokens': PAMPHLET_CONTENT_CONFIG['max_tokens'],
                }
            )
            
            text = response.text
            
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
                    # Generate both images in parallel using threading
                    import concurrent.futures
                    
                    def generate_text_image():
                        return self.generate_coloring_image(
                            content['coloringTextPrompt'], theme
                        )
                    
                    def generate_scene_image():
                        return self.generate_coloring_image(
                            content['coloringScenePrompt'], theme
                        )
                    
                    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                        text_future = executor.submit(generate_text_image)
                        scene_future = executor.submit(generate_scene_image)
                        
                        content['coloringTextImageUrl'] = text_future.result()
                        content['coloringSceneImageUrl'] = scene_future.result()
                        
                except Exception as e:
                    error_msg = f"Gemini image generation failed: {str(e)}"
                    print(f"⚠️  {error_msg}")
                    content['coloringTextImageUrl'] = None
                    content['coloringSceneImageUrl'] = None
                    content['coloringImageError'] = error_msg
            else:
                content['coloringTextImageUrl'] = None
                content['coloringSceneImageUrl'] = None
            
            return content
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse pamphlet content JSON from Gemini: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to generate pamphlet content with Gemini: {str(e)}")

