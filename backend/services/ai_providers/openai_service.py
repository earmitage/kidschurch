"""
OpenAI GPT and DALL·E implementation
"""

import os
import json
import re
from .base import AIServiceBase, QUIZ_GENERATION_CONFIG, COLORING_IMAGE_CONFIG, CROSSWORD_CONFIG, PAMPHLET_CONTENT_CONFIG, build_quiz_user_prompt, build_coloring_prompt, build_crossword_words_prompt, build_pamphlet_content_prompt
from utils.tracking import track_llm_call


class OpenAIService(AIServiceBase):
    """OpenAI GPT and DALL·E implementation"""
    
    def __init__(self):
        self.provider_name = "OpenAI"
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        self._client = None
        
        if self.api_key:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
            except ImportError:
                print("⚠️  OpenAI package not installed. Run: pip install openai")
    
    def is_enabled(self) -> bool:
        return self._client is not None and self.api_key is not None
    
    @track_llm_call('generate_coloring_image')
    def generate_coloring_image(self, prompt: str, theme: str) -> str:
        """Generate image using DALL·E 3"""
        if not self.is_enabled():
            raise Exception("OpenAI service is not properly configured")
        
        try:
            full_prompt = build_coloring_prompt(prompt, theme)
            
            response = self._client.images.generate(
                model="dall-e-3",
                prompt=full_prompt,
                size=COLORING_IMAGE_CONFIG['size'],
                quality=COLORING_IMAGE_CONFIG['quality'],
                n=1,
            )
            
            return response.data[0].url
            
        except Exception as e:
            raise Exception(f"Failed to generate image with OpenAI: {str(e)}")
    
    @track_llm_call('generate_quiz_questions')
    def generate_quiz_questions(self, theme: str, num_questions: int = 10) -> list:
        """Generate quiz questions using OpenAI GPT"""
        if not self.is_enabled():
            raise Exception("OpenAI service is not properly configured")
        
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": QUIZ_GENERATION_CONFIG['system_prompt']},
                    {"role": "user", "content": build_quiz_user_prompt(theme, num_questions)}
                ],
                temperature=QUIZ_GENERATION_CONFIG['temperature'],
                max_tokens=QUIZ_GENERATION_CONFIG['max_tokens']
            )
            
            text = response.choices[0].message.content
            return self._parse_quiz_response(text, num_questions)
            
        except Exception as e:
            raise Exception(f"Failed to generate questions with OpenAI: {str(e)}")
    
    @track_llm_call('generate_crossword_words')
    def generate_crossword_words(self, theme: str, num_words: int = 8) -> list:
        """Generate crossword words using OpenAI GPT"""
        if not self.is_enabled():
            raise Exception("OpenAI service is not properly configured")
        
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": CROSSWORD_CONFIG['system_prompt']},
                    {"role": "user", "content": build_crossword_words_prompt(theme, num_words)}
                ],
                temperature=CROSSWORD_CONFIG['temperature'],
                max_tokens=CROSSWORD_CONFIG['max_tokens']
            )
            
            text = response.choices[0].message.content
            return self._parse_crossword_words_response(text, num_words)
            
        except Exception as e:
            raise Exception(f"Failed to generate crossword words with OpenAI: {str(e)}")
    
    @track_llm_call('generate_pamphlet_content')
    def generate_pamphlet_content(self, theme: str) -> dict:
        """Generate all pamphlet content in one LLM call, then generate coloring images"""
        if not self.is_enabled():
            raise Exception("OpenAI service is not properly configured")
        
        try:
            # Build the combined prompt
            full_prompt = (
                f"{PAMPHLET_CONTENT_CONFIG['system_prompt']}\n\n"
                f"{build_pamphlet_content_prompt(theme)}"
            )
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": PAMPHLET_CONTENT_CONFIG['system_prompt']},
                    {"role": "user", "content": build_pamphlet_content_prompt(theme)}
                ],
                temperature=PAMPHLET_CONTENT_CONFIG['temperature'],
                max_tokens=PAMPHLET_CONTENT_CONFIG['max_tokens']
            )
            
            text = response.choices[0].message.content
            
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
                    error_msg = f"OpenAI image generation failed: {str(e)}"
                    print(f"⚠️  {error_msg}")
                    content['coloringTextImageUrl'] = None
                    content['coloringSceneImageUrl'] = None
                    content['coloringImageError'] = error_msg
            else:
                content['coloringTextImageUrl'] = None
                content['coloringSceneImageUrl'] = None
            
            return content
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse pamphlet content JSON from OpenAI: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to generate pamphlet content with OpenAI: {str(e)}")

