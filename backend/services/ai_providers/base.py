"""
Base AI service interface and shared utilities
"""

from abc import ABC, abstractmethod
from typing import Optional

# Centralized prompts and configuration
QUIZ_GENERATION_CONFIG = {
    'system_prompt': (
        "You are creating fun, age-appropriate quiz questions for 5-year-old children "
        "learning about Bible stories. Keep questions simple, clear, and engaging. "
        "Answers should be short single words or very short phrases in ALL CAPS."
    ),
    'format_instruction': 'Format each question exactly as: Question here?\nAnswer in ALL CAPS\n\n',
    'temperature': 0.8,
    'max_tokens': 500
}

COLORING_IMAGE_CONFIG = {
    'system_description': (
        'Black and white line art, no shading, '
        'clean outline drawing suitable for children\'s coloring book. '
        'Friendly, smiling, age-appropriate.'
    ),
    'size': '1024x1024',
    'quality': 'standard'
}

CROSSWORD_CONFIG = {
    'system_prompt': (
        "You are creating a word list for a crossword puzzle for 5-year-old children "
        "learning about Bible stories. Generate simple, age-appropriate words related to the theme. "
        "Words should be 3-8 letters long, uppercase, and represent key characters, objects, or concepts from the story."
    ),
    'format_instruction': 'Return ONLY the words as a comma-separated list in ALL CAPS. No numbers, no explanations, no extra text. Just the words separated by commas.',
    'temperature': 0.7,
    'max_tokens': 300
}

PAMPHLET_CONTENT_CONFIG = {
    'system_prompt': (
        "You are creating educational content for a kids church pamphlet for 5-year-old children "
        "learning about Bible stories. Generate simple, age-appropriate, theme-based content. "
        "All content must be biblical, kid-friendly, and match the theme provided."
    ),
    'temperature': 0.7,
    'max_tokens': 2000
}


def build_quiz_user_prompt(theme: str, num_questions: int) -> str:
    """Build the user prompt for quiz generation"""
    return (
        f"Generate {num_questions} fun quiz questions for 5-year-olds about the biblical theme '{theme}'. "
        f"{QUIZ_GENERATION_CONFIG['format_instruction']}"
        f"Keep questions very simple, age-appropriate, and fun. Focus on basic facts and characters from the {theme} story."
    )


def build_coloring_prompt(prompt: str, theme: str) -> str:
    """Build the prompt for coloring image generation"""
    return (
        f"Simple, cute, biblical {theme.lower()} cartoon character "
        f"for kids to color. {COLORING_IMAGE_CONFIG['system_description']} "
        f"Focus on: {prompt}"
    )


def build_crossword_words_prompt(theme: str, num_words: int) -> str:
    """Build the prompt for crossword word generation"""
    return (
        f"Generate EXACTLY {num_words} simple words for a crossword puzzle about the biblical theme '{theme}'. "
        f"{CROSSWORD_CONFIG['format_instruction']} "
        f"Focus on key characters, objects, and concepts from the {theme} story. "
        f"Make sure to return exactly {num_words} words."
    )


def build_pamphlet_content_prompt(theme: str) -> str:
    """Build the prompt for comprehensive pamphlet content generation"""
    return f'''Generate complete pamphlet content for a kids church activity pamphlet about the biblical theme "{theme}".

Return ALL content in this exact JSON format:
{{
  "quizQuestions": [
    {{"q": "Question here for 5-year-olds?", "a": "SHORT ANSWER IN CAPS"}},
    {{"q": "Another simple question?", "a": "ANSWER IN CAPS"}}
  ],
  "wordList": ["WORD1", "WORD2", "WORD3", "WORD4", "WORD5", "WORD6", "WORD7", "WORD8"],
  "missingLetterWords": [
    {{"word": "W _ R D", "missing": "O"}},
    {{"word": "L O _ E", "missing": "V"}}
  ],
  "wordCompletionPhrase": "A simple 5-8 word phrase for kids to complete",
  "mazeGoal": "A fun goal description for the maze challenge",
  "coloringText": "ARK",
  "coloringTextPrompt": "large decorative coloring book style text ARK with biblical patterns, black and white line art, bold thick letters suitable for children to color",
  "coloringScenePrompt": "cartoon scene of Noah's ark floating on calm water with elephants, giraffes, and birds visible on the ark, simple line art, black and white, suitable for children's coloring book"
}}

REQUIREMENTS:
- Generate exactly 5 quiz questions with simple, short answers for 5-year-olds
- Generate exactly 8 words (3-8 letters, UPPERCASE) for word search and crossword
- Generate exactly 5 missing letter words: format as "L E T T E _ S" with spaces between letters, one middle letter as _
- Generate one kid-friendly phrase (5-8 words) for word completion
- Generate one fun maze goal description (10-15 words)
- Generate one theme-appropriate word or short phrase (1-3 words, UPPERCASE) for coloringText (e.g., "ARK", "NOAH", "CREATION", "GOD", "JESUS", "LOVE", "SHEPHERD")
- Generate detailed coloringTextPrompt: "large decorative coloring book style text [coloringText] with [theme] patterns, black and white line art, bold thick letters suitable for children to color"
- Generate detailed coloringScenePrompt: theme-specific cartoon scene description (e.g., "Noah's ark floating on water with animals", "sun in sky, ocean, trees, animals", "shepherd with staff, sheep in field"). Must be simple line art, black and white, suitable for children's coloring book
- All content must match the "{theme}" theme
- Make sure all words and phrases are biblical and appropriate for children
'''


class AIServiceBase(ABC):
    """Base class for AI services - defines the interface"""
    
    @abstractmethod
    def generate_coloring_image(self, prompt: str, theme: str) -> str:
        """
        Generate a coloring image URL
        
        Args:
            prompt: Text description of the image
            theme: Biblical theme context
            
        Returns:
            URL to the generated image
            
        Raises:
            NotImplementedError: If provider not implemented
        """
        pass
    
    @abstractmethod
    def generate_quiz_questions(self, theme: str, num_questions: int = 10) -> list:
        """
        Generate quiz questions for kids
        
        Args:
            theme: Biblical theme context
            num_questions: Number of questions to generate
            
        Returns:
            List of dicts with 'q' (question) and 'a' (answer) keys
            
        Raises:
            NotImplementedError: If provider not implemented
        """
        pass
    
    @abstractmethod
    def generate_crossword_words(self, theme: str, num_words: int = 8) -> list:
        """
        Generate words for a crossword puzzle
        
        Args:
            theme: Biblical theme context
            num_words: Number of words to generate
            
        Returns:
            List of uppercase words (strings)
            
        Raises:
            NotImplementedError: If provider not implemented
        """
        pass
    
    def generate_crossword(self, theme: str) -> dict:
        """
        Generate a complete crossword puzzle with grid and clues
        
        Args:
            theme: Biblical theme context
            
        Returns:
            Dict with 'title', 'grid', and 'words' keys
            
        Raises:
            NotImplementedError: If provider not implemented
        """
        raise NotImplementedError("generate_crossword not implemented for this provider")
    
    def generate_pamphlet_content(self, theme: str) -> dict:
        """
        Generate all pamphlet content in one call
        
        Args:
            theme: Biblical theme context
            
        Returns:
            Dict with quizQuestions, wordList, missingLetterWords, wordCompletionPhrase, mazeGoal
            
        Raises:
            NotImplementedError: If provider not implemented
        """
        raise NotImplementedError("generate_pamphlet_content not implemented for this provider")
    
    @abstractmethod
    def is_enabled(self) -> bool:
        """Check if this AI service is properly configured"""
        pass
    
    def _parse_quiz_response(self, text: str, num_questions: int = 10) -> list:
        """
        Parse quiz questions from AI response
        Expects format: Question?\nANSWER\n\n
        """
        questions = []
        
        for block in text.split('\n\n'):
            if not block.strip():
                continue
            lines = [line.strip() for line in block.split('\n') if line.strip()]
            if len(lines) >= 2:
                questions.append({
                    'q': lines[0].rstrip('?'),
                    'a': lines[1].upper().strip()
                })
        
        return questions[:num_questions]
    
    def _parse_crossword_words_response(self, text: str, num_words: int = 8) -> list:
        """
        Parse crossword words from AI response
        Expects format: WORD1, WORD2, WORD3, ...
        """
        # Extract first line (usually contains the comma-separated words)
        first_line = text.split('\n')[0].strip()
        
        # Remove any unwanted characters and split by comma
        words = [word.strip().upper() for word in first_line.split(',')]
        
        # Filter out invalid words (too short, too long, or contains spaces)
        valid_words = [w for w in words if len(w) >= 3 and len(w) <= 10 and ' ' not in w and w.isalpha()]
        
        # If we got fewer valid words than requested, try parsing from entire text
        if len(valid_words) < num_words:
            # Try finding all uppercase words in the response
            import re
            all_uppercase_words = re.findall(r'\b[A-Z]{3,10}\b', text)
            valid_words = list(dict.fromkeys(all_uppercase_words))  # Remove duplicates
        
        return valid_words[:num_words]

