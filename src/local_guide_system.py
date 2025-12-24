"""
Main Local Guide System
Orchestrates all components to provide intelligent local assistance
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json

from .context_loader import ContextLoader
from .local_reasoning_engine import LocalReasoningEngine, ReasoningResult
from .slang_interpreter import SlangInterpreter, SlangTranslation
from .recommendation_engine import RecommendationEngine, RecommendationRequest, RecommendationType
from .confidence_scorer import ConfidenceScorer, ConfidenceScore

@dataclass
class LocalGuideResponse:
    response_text: str
    confidence_score: ConfidenceScore
    slang_translation: Optional[SlangTranslation] = None
    recommendations: Optional[List[Any]] = None
    cultural_context: Optional[str] = None
    sources_used: Optional[List[str]] = None
    reasoning_chain: Optional[List[str]] = None

class LocalGuideSystem:
    def __init__(self, product_md_path: str = "product.md"):
        """Initialize the Local Guide System"""
        
        # Initialize core components
        self.context_loader = ContextLoader(product_md_path)
        self.reasoning_engine = LocalReasoningEngine(self.context_loader)
        self.slang_interpreter = SlangInterpreter(self.context_loader)
        self.recommendation_engine = RecommendationEngine(self.context_loader)
        self.confidence_scorer = ConfidenceScorer()
        
        # Load context data
        try:
            self.context_data = self.context_loader.load_context()
            self.city_name = self.context_data.get('city_info', {}).get('name', 'Unknown City')
            self.is_initialized = True
        except Exception as e:
            self.is_initialized = False
            self.initialization_error = str(e)
    
    def process_query(self, query: str, current_time: Optional[datetime] = None) -> LocalGuideResponse:
        """Main method to process user queries"""
        
        if not self.is_initialized:
            return LocalGuideResponse(
                response_text=f"System initialization failed: {self.initialization_error}",
                confidence_score=ConfidenceScore(
                    overall_score=0.0,
                    level="very_low",
                    factors={},
                    missing_information=["product.md file"],
                    recommendation="Check if product.md exists and is properly formatted",
                    should_ask_clarification=False
                )
            )
        
        if current_time is None:
            current_time = datetime.now()
        
        # Step 1: Check if query contains slang and translate if needed
        slang_translation = None
        processed_query = query
        
        if self.slang_interpreter.detect_language_mix(query)['is_mixed_language']:
            slang_translation = self.slang_interpreter.interpret_mixed_language(query)
            processed_query = slang_translation.translated_text
        
        # Step 2: Process query through reasoning engine
        reasoning_result = self.reasoning_engine.process_query(processed_query, current_time)
        
        # Step 3: Calculate confidence score
        query_analysis = self.reasoning_engine._analyze_query(processed_query)
        relevant_context = self.reasoning_engine._get_relevant_context(processed_query, query_analysis)
        
        confidence_score = self.confidence_scorer.calculate_confidence(
            processed_query, relevant_context, query_analysis, reasoning_result.response
        )
        
        # Step 4: Generate recommendations if appropriate
        recommendations = None
        if self._should_generate_recommendations(query_analysis, confidence_score):
            recommendations = self._generate_contextual_recommendations(
                query_analysis, current_time, reasoning_result
            )
        
        # Step 5: Add cultural context if relevant
        cultural_context = self._get_cultural_context(query, slang_translation)
        
        # Step 6: Enhance response with local personality
        enhanced_response = self._enhance_response_personality(
            reasoning_result.response, query_analysis, slang_translation
        )
        
        # Step 7: Handle low confidence scenarios
        if confidence_score.should_ask_clarification:
            clarifying_question = self.confidence_scorer.should_request_clarification(
                confidence_score, query_analysis
            )
            if clarifying_question:
                enhanced_response += f"\n\n{clarifying_question}"
        
        return LocalGuideResponse(
            response_text=enhanced_response,
            confidence_score=confidence_score,
            slang_translation=slang_translation,
            recommendations=recommendations,
            cultural_context=cultural_context,
            sources_used=reasoning_result.sources_used,
            reasoning_chain=reasoning_result.reasoning_chain
        )
    
    def translate_slang(self, text: str, direction: str = "to_standard") -> SlangTranslation:
        """Translate slang text"""
        if direction == "to_standard":
            return self.slang_interpreter.translate_to_standard(text)
        elif direction == "to_local":
            return self.slang_interpreter.translate_to_local(text)
        else:
            return self.slang_interpreter.interpret_mixed_language(text)
    
    def get_recommendations(self, recommendation_type: str, **kwargs) -> List[Any]:
        """Get specific type of recommendations"""
        
        current_time = kwargs.get('current_time', datetime.now())
        
        request = RecommendationRequest(
            type=RecommendationType(recommendation_type),
            current_time=current_time,
            location=kwargs.get('location'),
            budget_level=kwargs.get('budget_level'),
            weather_condition=kwargs.get('weather_condition'),
            crowd_tolerance=kwargs.get('crowd_tolerance'),
            specific_preferences=kwargs.get('specific_preferences')
        )
        
        return self.recommendation_engine.get_recommendations(request)
    
    def explain_cultural_context(self, topic: str) -> str:
        """Explain cultural context for a specific topic"""
        
        if 'culture' not in self.context_data:
            return "Cultural information is not present in the local context file."
        
        culture_data = self.context_data['culture']
        
        # Search for relevant cultural information
        topic_lower = topic.lower()
        explanations = []
        
        if 'dos' in culture_data:
            for do_item in culture_data['dos']:
                if any(word in do_item.lower() for word in topic_lower.split()):
                    explanations.append(f"Do: {do_item}")
        
        if 'donts' in culture_data:
            for dont_item in culture_data['donts']:
                if any(word in dont_item.lower() for word in topic_lower.split()):
                    explanations.append(f"Don't: {dont_item}")
        
        if explanations:
            return f"Cultural context for '{topic}':\n" + "\n".join(explanations)
        else:
            return f"No specific cultural information found for '{topic}' in the local context."
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status and loaded context information"""
        
        status = {
            'initialized': self.is_initialized,
            'city_name': getattr(self, 'city_name', 'Unknown'),
            'context_sections_loaded': list(self.context_data.keys()) if self.is_initialized else [],
            'slang_words_count': len(self.context_data.get('slang', {})) if self.is_initialized else 0,
            'food_areas_count': len(self.context_data.get('food', {}).get('areas', {})) if self.is_initialized else 0
        }
        
        if not self.is_initialized:
            status['error'] = getattr(self, 'initialization_error', 'Unknown error')
        
        return status
    
    def _should_generate_recommendations(self, query_analysis: Dict[str, Any], 
                                       confidence_score: ConfidenceScore) -> bool:
        """Determine if recommendations should be generated"""
        
        intent = query_analysis.get('intent', 'general_query')
        recommendation_intents = [
            'food_recommendation', 'transport_query', 'activity_query'
        ]
        
        return (intent in recommendation_intents and 
                confidence_score.overall_score > 0.3)
    
    def _generate_contextual_recommendations(self, query_analysis: Dict[str, Any], 
                                           current_time: datetime,
                                           reasoning_result: ReasoningResult) -> List[Any]:
        """Generate contextual recommendations based on query"""
        
        intent = query_analysis.get('intent', 'general_query')
        
        if intent == 'food_recommendation':
            request = RecommendationRequest(
                type=RecommendationType.FOOD,
                current_time=current_time,
                location=query_analysis.get('location_context', [None])[0] if query_analysis.get('location_context') else None
            )
            return self.recommendation_engine.get_recommendations(request)
        
        elif intent == 'transport_query':
            request = RecommendationRequest(
                type=RecommendationType.TRANSPORT,
                current_time=current_time
            )
            return self.recommendation_engine.get_recommendations(request)
        
        return []
    
    def _get_cultural_context(self, original_query: str, 
                            slang_translation: Optional[SlangTranslation]) -> Optional[str]:
        """Extract relevant cultural context"""
        
        if slang_translation and slang_translation.cultural_context:
            return slang_translation.cultural_context
        
        # Check if query relates to cultural topics
        cultural_keywords = ['wear', 'dress', 'appropriate', 'culture', 'etiquette', 'respect']
        if any(keyword in original_query.lower() for keyword in cultural_keywords):
            return "Cultural sensitivity is important in local interactions. Check local customs and dress codes."
        
        return None
    
    def _enhance_response_personality(self, response: str, query_analysis: Dict[str, Any], 
                                    slang_translation: Optional[SlangTranslation]) -> str:
        """Add local personality and warmth to responses"""
        
        if not response or "not present in the local context file" in response:
            return response
        
        # Add local greeting based on time
        current_hour = datetime.now().hour
        if 6 <= current_hour < 12:
            greeting_prefix = ""
        elif 12 <= current_hour < 17:
            greeting_prefix = ""
        else:
            greeting_prefix = ""
        
        # Add local expressions for friendliness
        local_expressions = {
            'food_recommendation': "Here's what I'd suggest, bhai: ",
            'transport_query': "For getting around: ",
            'slang_translation': "Local translation: ",
            'cultural_advice': "Cultural tip: "
        }
        
        intent = query_analysis.get('intent', 'general_query')
        if intent in local_expressions and not response.startswith(local_expressions[intent]):
            response = local_expressions[intent] + response
        
        # Add confidence indicator in local style
        if "I'd recommend" not in response and "suggest" not in response:
            if intent == 'food_recommendation':
                response = response.replace("For", "I'd suggest for")
        
        return greeting_prefix + response
    
    def debug_query_processing(self, query: str) -> Dict[str, Any]:
        """Debug method to see internal processing steps"""
        
        if not self.is_initialized:
            return {'error': 'System not initialized'}
        
        # Step-by-step processing for debugging
        debug_info = {}
        
        # 1. Query analysis
        query_analysis = self.reasoning_engine._analyze_query(query)
        debug_info['query_analysis'] = query_analysis
        
        # 2. Slang detection
        slang_detection = self.slang_interpreter.detect_language_mix(query)
        debug_info['slang_detection'] = slang_detection
        
        # 3. Context retrieval
        relevant_context = self.reasoning_engine._get_relevant_context(query, query_analysis)
        debug_info['relevant_context'] = [
            {
                'category': item.category.value,
                'confidence': item.confidence,
                'source': item.source_section,
                'content_preview': str(item.content)[:100] + "..."
            }
            for item in relevant_context
        ]
        
        # 4. Reasoning process
        reasoning_result = self.reasoning_engine.process_query(query)
        debug_info['reasoning_result'] = {
            'response': reasoning_result.response,
            'confidence': reasoning_result.confidence,
            'sources_used': reasoning_result.sources_used,
            'reasoning_chain': reasoning_result.reasoning_chain,
            'missing_info': reasoning_result.missing_info
        }
        
        return debug_info