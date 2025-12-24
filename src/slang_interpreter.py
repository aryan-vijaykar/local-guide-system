"""
Slang & Language Interpreter
Translates local slang to standard English and vice versa
Handles mixed language sentences
"""

import re
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

from .context_loader import ContextLoader

@dataclass
class SlangTranslation:
    original_text: str
    translated_text: str
    slang_words_found: List[Tuple[str, str]]  # (slang_word, meaning)
    confidence: float
    cultural_context: Optional[str] = None

class SlangInterpreter:
    def __init__(self, context_loader: ContextLoader):
        self.context_loader = context_loader
        self.slang_dict = self._load_slang_dictionary()
        
    def _load_slang_dictionary(self) -> Dict[str, str]:
        """Load slang dictionary from context"""
        context_data = self.context_loader.structured_data
        return context_data.get('slang', {})
    
    def translate_to_standard(self, text: str) -> SlangTranslation:
        """Translate local slang to standard English"""
        original_text = text
        translated_text = text
        slang_words_found = []
        
        # Find and replace slang words
        words = re.findall(r'\b\w+\b', text.lower())
        
        for word in words:
            if word in self.slang_dict:
                meaning = self.slang_dict[word]
                slang_words_found.append((word, meaning))
                
                # Replace in translated text (case-insensitive)
                pattern = re.compile(re.escape(word), re.IGNORECASE)
                translated_text = pattern.sub(f"{meaning}", translated_text)
        
        # Calculate confidence based on how many slang words were found
        confidence = min(1.0, len(slang_words_found) * 0.3 + 0.4) if slang_words_found else 0.0
        
        # Add cultural context for common phrases
        cultural_context = self._get_cultural_context(text, slang_words_found)
        
        return SlangTranslation(
            original_text=original_text,
            translated_text=translated_text,
            slang_words_found=slang_words_found,
            confidence=confidence,
            cultural_context=cultural_context
        )
    
    def translate_to_local(self, text: str) -> SlangTranslation:
        """Translate standard English to local slang"""
        original_text = text
        translated_text = text
        slang_words_found = []
        
        # Reverse lookup - find English words that have slang equivalents
        reverse_slang = {v.lower(): k for k, v in self.slang_dict.items()}
        
        # Simple word replacement (can be enhanced with NLP)
        for english_word, slang_word in reverse_slang.items():
            if english_word in text.lower():
                slang_words_found.append((slang_word, english_word))
                pattern = re.compile(re.escape(english_word), re.IGNORECASE)
                translated_text = pattern.sub(slang_word, translated_text)
        
        # Add common local expressions
        translated_text = self._add_local_flavor(translated_text)
        
        confidence = min(1.0, len(slang_words_found) * 0.2 + 0.3) if slang_words_found else 0.2
        
        return SlangTranslation(
            original_text=original_text,
            translated_text=translated_text,
            slang_words_found=slang_words_found,
            confidence=confidence
        )
    
    def interpret_mixed_language(self, text: str) -> SlangTranslation:
        """Handle mixed language sentences (English + local language)"""
        # This is a simplified version - in reality, this would need
        # more sophisticated language detection and translation
        
        # First, translate any slang to standard English
        slang_translation = self.translate_to_standard(text)
        
        # Then handle common mixed language patterns
        mixed_patterns = {
            r'\bbhai\b': 'brother/friend',
            r'\bscene\b': 'plan/situation',
            r'\bkya\b': 'what',
            r'\bhai\b': 'is/are'
        }
        
        interpreted_text = slang_translation.translated_text
        additional_translations = []
        
        for pattern, meaning in mixed_patterns.items():
            if re.search(pattern, text.lower()):
                interpreted_text = re.sub(pattern, f"({meaning})", interpreted_text, flags=re.IGNORECASE)
                additional_translations.append((pattern.strip('\\b'), meaning))
        
        # Combine all found translations
        all_translations = slang_translation.slang_words_found + additional_translations
        
        return SlangTranslation(
            original_text=text,
            translated_text=interpreted_text,
            slang_words_found=all_translations,
            confidence=slang_translation.confidence,
            cultural_context=slang_translation.cultural_context
        )
    
    def _get_cultural_context(self, text: str, slang_words: List[Tuple[str, str]]) -> Optional[str]:
        """Provide cultural context for slang usage"""
        text_lower = text.lower()
        
        cultural_contexts = {
            'bhai': "Used universally in Mumbai to address anyone, regardless of relationship. Shows friendliness.",
            'cutting': "Refers to half a cup of tea. Popular way to have tea at tapris (tea stalls).",
            'scene': "Very common way to ask about plans or situations. Part of Mumbai youth slang.",
            'bindaas': "Represents the carefree Mumbai attitude. Used to describe someone who's cool and relaxed.",
            'jugaad': "Reflects the innovative problem-solving spirit of Mumbai locals.",
            'timepass': "Essential concept in Mumbai culture - casual hanging out without specific purpose."
        }
        
        for slang_word, _ in slang_words:
            if slang_word in cultural_contexts:
                return cultural_contexts[slang_word]
        
        return None
    
    def _add_local_flavor(self, text: str) -> str:
        """Add local expressions to make text sound more local"""
        # Add common Mumbai expressions
        local_additions = {
            r'\bhow are you\b': 'kya scene hai bhai',
            r'\bwhat\'s up\b': 'kya scene hai',
            r'\bokay\b': 'chalta hai',
            r'\bno problem\b': 'koi scene nahi',
            r'\blet\'s go\b': 'chalo bhai'
        }
        
        modified_text = text
        for pattern, replacement in local_additions.items():
            modified_text = re.sub(pattern, replacement, modified_text, flags=re.IGNORECASE)
        
        return modified_text
    
    def get_slang_suggestions(self, context: str) -> List[str]:
        """Suggest appropriate slang based on context"""
        context_lower = context.lower()
        suggestions = []
        
        suggestion_map = {
            'food': ['tapri', 'cutting', 'vada pav', 'bhel'],
            'transport': ['auto', 'local'],
            'greeting': ['bhai', 'scene'],
            'agreement': ['chalta hai', 'bindaas'],
            'casual': ['timepass', 'jugaad']
        }
        
        for category, slang_list in suggestion_map.items():
            if category in context_lower:
                suggestions.extend(slang_list)
        
        return suggestions[:3]  # Return top 3 suggestions
    
    def explain_slang_usage(self, slang_word: str) -> Dict[str, str]:
        """Provide detailed explanation of slang usage"""
        if slang_word.lower() not in self.slang_dict:
            return {
                'error': f"'{slang_word}' not found in local slang dictionary"
            }
        
        meaning = self.slang_dict[slang_word.lower()]
        
        # Usage examples (would be enhanced with more data)
        usage_examples = {
            'bhai': {
                'meaning': meaning,
                'usage': 'Used to address anyone in a friendly manner',
                'example': 'Bhai, kya scene hai? (Brother, what\'s the plan?)',
                'context': 'Universal term of address in Mumbai'
            },
            'scene': {
                'meaning': meaning,
                'usage': 'Used to ask about plans or situations',
                'example': 'Kal ka scene kya hai? (What\'s tomorrow\'s plan?)',
                'context': 'Very common in Mumbai youth conversations'
            },
            'cutting': {
                'meaning': meaning,
                'usage': 'Used when ordering tea at street stalls',
                'example': 'Ek cutting dena (Give me half a cup of tea)',
                'context': 'Specific to Mumbai tea culture'
            }
        }
        
        return usage_examples.get(slang_word.lower(), {
            'meaning': meaning,
            'usage': 'Local slang term',
            'example': f'Example usage of {slang_word}',
            'context': 'Part of local vocabulary'
        })
    
    def detect_language_mix(self, text: str) -> Dict[str, Any]:
        """Detect if text contains mixed languages"""
        # Simple detection based on known patterns
        english_words = set(re.findall(r'\b[a-zA-Z]+\b', text))
        slang_words = set(word for word in english_words if word.lower() in self.slang_dict)
        
        # Common Hindi/local language patterns
        local_patterns = [r'\bkya\b', r'\bhai\b', r'\bka\b', r'\bke\b', r'\bko\b']
        local_matches = sum(1 for pattern in local_patterns if re.search(pattern, text.lower()))
        
        is_mixed = len(slang_words) > 0 or local_matches > 0
        
        return {
            'is_mixed_language': is_mixed,
            'english_words': len(english_words),
            'slang_words': len(slang_words),
            'local_patterns': local_matches,
            'confidence': min(1.0, (len(slang_words) + local_matches) * 0.2)
        }