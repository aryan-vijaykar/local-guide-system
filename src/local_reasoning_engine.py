"""
Local Reasoning Engine
Uses context-based inference, not global rules
Applies local logic patterns from product.md
"""

from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, time
import re

from .context_loader import ContextLoader, ContextCategory, ContextItem

@dataclass
class ReasoningResult:
    response: str
    confidence: float
    sources_used: List[str]
    reasoning_chain: List[str]
    missing_info: List[str]

class LocalReasoningEngine:
    def __init__(self, context_loader: ContextLoader):
        self.context_loader = context_loader
        self.confidence_threshold = 0.6
        
    def process_query(self, query: str, current_time: Optional[datetime] = None) -> ReasoningResult:
        """Process user query using local context and reasoning"""
        if current_time is None:
            current_time = datetime.now()
            
        # Step 1: Analyze query intent and extract key information
        query_analysis = self._analyze_query(query)
        
        # Step 2: Retrieve relevant context
        relevant_context = self._get_relevant_context(query, query_analysis)
        
        # Step 3: Apply local reasoning
        reasoning_result = self._apply_local_reasoning(
            query, query_analysis, relevant_context, current_time
        )
        
        return reasoning_result
    
    def _analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze query to understand intent and extract key information"""
        query_lower = query.lower()
        
        analysis = {
            'intent': self._detect_intent(query_lower),
            'keywords': self._extract_keywords(query_lower),
            'time_context': self._extract_time_context(query_lower),
            'location_context': self._extract_location_context(query_lower),
            'contains_slang': self._contains_slang(query_lower)
        }
        
        return analysis
    
    def _detect_intent(self, query: str) -> str:
        """Detect the primary intent of the query"""
        intent_patterns = {
            'food_recommendation': ['eat', 'food', 'hungry', 'restaurant', 'street food', 'vada pav', 'bhel'],
            'transport_query': ['reach', 'go to', 'travel', 'auto', 'train', 'bus', 'traffic', 'commute'],
            'slang_translation': ['meaning', 'what does', 'translate', 'bhai', 'scene'],
            'cultural_advice': ['wear', 'appropriate', 'etiquette', 'culture', 'okay to'],
            'timing_query': ['when', 'time', 'hours', 'open', 'close', 'peak'],
            'weather_query': ['weather', 'rain', 'monsoon', 'hot', 'cold'],
            'festival_query': ['festival', 'celebration', 'ganesh', 'diwali', 'navratri'],
            'safety_query': ['safe', 'danger', 'avoid', 'careful', 'security'],
            'pricing_query': ['cost', 'price', 'expensive', 'cheap', 'budget']
        }
        
        for intent, keywords in intent_patterns.items():
            if any(keyword in query for keyword in keywords):
                return intent
        
        return 'general_query'
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract important keywords from query"""
        # Remove common words and extract meaningful terms
        stop_words = {'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but', 'in', 'with', 'to', 'for', 'of', 'as', 'by'}
        words = re.findall(r'\b\w+\b', query.lower())
        return [word for word in words if word not in stop_words and len(word) > 2]
    
    def _extract_time_context(self, query: str) -> Dict[str, Any]:
        """Extract time-related context from query"""
        time_context = {
            'specific_time': None,
            'time_period': None,
            'relative_time': None
        }
        
        # Check for specific times
        time_patterns = [
            r'(\d{1,2}):(\d{2})\s*(am|pm)?',
            r'(\d{1,2})\s*(am|pm)',
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, query)
            if match:
                time_context['specific_time'] = match.group(0)
                break
        
        # Check for time periods
        time_periods = {
            'morning': ['morning', 'am', 'breakfast'],
            'afternoon': ['afternoon', 'lunch', 'noon'],
            'evening': ['evening', 'dinner', 'night'],
            'late_night': ['late night', 'midnight', 'late']
        }
        
        for period, keywords in time_periods.items():
            if any(keyword in query for keyword in keywords):
                time_context['time_period'] = period
                break
        
        # Check for relative time
        relative_patterns = ['now', 'today', 'tonight', 'tomorrow', 'later', 'soon']
        for pattern in relative_patterns:
            if pattern in query:
                time_context['relative_time'] = pattern
                break
        
        return time_context
    
    def _extract_location_context(self, query: str) -> List[str]:
        """Extract location mentions from query"""
        # This would be enhanced with locations from product.md
        locations = []
        
        # Get locations from context
        context_data = self.context_loader.structured_data
        if 'food' in context_data and 'areas' in context_data['food']:
            for area in context_data['food']['areas'].keys():
                if area.lower() in query:
                    locations.append(area)
        
        return locations
    
    def _contains_slang(self, query: str) -> bool:
        """Check if query contains local slang"""
        context_data = self.context_loader.structured_data
        if 'slang' in context_data:
            slang_words = context_data['slang'].keys()
            return any(slang in query for slang in slang_words)
        return False
    
    def _get_relevant_context(self, query: str, query_analysis: Dict[str, Any]) -> List[ContextItem]:
        """Retrieve relevant context based on query and analysis"""
        relevant_context = []
        
        # Get context based on intent
        intent = query_analysis['intent']
        category_mapping = {
            'food_recommendation': ContextCategory.FOOD,
            'transport_query': ContextCategory.TRANSPORT,
            'slang_translation': ContextCategory.SLANG,
            'cultural_advice': ContextCategory.CULTURE,
            'timing_query': ContextCategory.TIMING,
            'weather_query': ContextCategory.WEATHER,
            'festival_query': ContextCategory.FESTIVALS,
            'safety_query': ContextCategory.SAFETY,
            'pricing_query': ContextCategory.COST
        }
        
        if intent in category_mapping:
            category_context = self.context_loader.get_context_by_category(category_mapping[intent])
            relevant_context.extend(category_context)
        
        # Also search for general relevant context
        search_results = self.context_loader.search_context(query)
        relevant_context.extend(search_results)
        
        # Remove duplicates and sort by confidence
        seen_sources = set()
        unique_context = []
        for item in relevant_context:
            if item.source_section not in seen_sources:
                unique_context.append(item)
                seen_sources.add(item.source_section)
        
        return sorted(unique_context, key=lambda x: x.confidence, reverse=True)[:5]  # Top 5 most relevant
    
    def _apply_local_reasoning(self, query: str, query_analysis: Dict[str, Any], 
                             context: List[ContextItem], current_time: datetime) -> ReasoningResult:
        """Apply local reasoning logic based on context"""
        
        intent = query_analysis['intent']
        reasoning_chain = []
        sources_used = []
        missing_info = []
        
        # Apply intent-specific reasoning
        if intent == 'food_recommendation':
            result = self._reason_food_recommendation(query, query_analysis, context, current_time)
        elif intent == 'transport_query':
            result = self._reason_transport_query(query, query_analysis, context, current_time)
        elif intent == 'slang_translation':
            result = self._reason_slang_translation(query, query_analysis, context)
        elif intent == 'cultural_advice':
            result = self._reason_cultural_advice(query, query_analysis, context)
        elif intent == 'timing_query':
            result = self._reason_timing_query(query, query_analysis, context, current_time)
        else:
            result = self._reason_general_query(query, query_analysis, context)
        
        return result
    
    def _reason_food_recommendation(self, query: str, analysis: Dict[str, Any], 
                                  context: List[ContextItem], current_time: datetime) -> ReasoningResult:
        """Reason about food recommendations using local context"""
        reasoning_chain = ["Analyzing food recommendation request"]
        sources_used = []
        missing_info = []
        
        # Get current time period
        current_hour = current_time.hour
        time_period = self._get_time_period(current_hour)
        reasoning_chain.append(f"Current time period: {time_period}")
        
        # Find food context
        food_context = None
        for item in context:
            if item.category == ContextCategory.FOOD:
                food_context = item
                sources_used.append(item.source_section)
                break
        
        if not food_context:
            missing_info.append("Food timing and area information")
            return ReasoningResult(
                response="This information is not present in the local context file.",
                confidence=0.0,
                sources_used=sources_used,
                reasoning_chain=reasoning_chain,
                missing_info=missing_info
            )
        
        # Parse food data
        try:
            food_data = eval(food_context.content) if isinstance(food_context.content, str) else food_context.content
        except:
            food_data = {'timings': {}, 'areas': {}}
        
        response_parts = []
        confidence = 0.8
        
        # Time-based recommendations
        if 'timings' in food_data:
            reasoning_chain.append("Checking time-appropriate food options")
            for timing_key, foods in food_data['timings'].items():
                if time_period.lower() in timing_key.lower():
                    response_parts.append(f"For {time_period}, I'd recommend: {foods}")
                    reasoning_chain.append(f"Found timing match: {timing_key}")
                    break
        
        # Location-based recommendations
        locations = analysis.get('location_context', [])
        if locations and 'areas' in food_data:
            reasoning_chain.append(f"Checking recommendations for mentioned locations: {locations}")
            for location in locations:
                if location in food_data['areas']:
                    area_info = food_data['areas'][location]
                    response_parts.append(f"At {location}: {area_info['foods']} ({area_info['timing']})")
                    reasoning_chain.append(f"Found location-specific info for {location}")
        
        # Add hygiene tips if available
        if 'hygiene_tips' in food_data and food_data['hygiene_tips']:
            response_parts.append("Local tip: Look for crowded stalls (high turnover = fresh food)")
            reasoning_chain.append("Added local hygiene wisdom")
        
        if not response_parts:
            missing_info.append("Specific timing or location information for current context")
            confidence = 0.3
            response = "I need more specific information about timing or location preferences to give you the best local recommendations."
        else:
            response = " ".join(response_parts)
        
        return ReasoningResult(
            response=response,
            confidence=confidence,
            sources_used=sources_used,
            reasoning_chain=reasoning_chain,
            missing_info=missing_info
        )
    
    def _reason_transport_query(self, query: str, analysis: Dict[str, Any], 
                              context: List[ContextItem], current_time: datetime) -> ReasoningResult:
        """Reason about transport queries using local patterns"""
        reasoning_chain = ["Analyzing transport query"]
        sources_used = []
        missing_info = []
        
        # Check for timing patterns
        timing_context = None
        transport_context = None
        
        for item in context:
            if item.category == ContextCategory.TIMING:
                timing_context = item
                sources_used.append(item.source_section)
            elif item.category == ContextCategory.TRANSPORT:
                transport_context = item
                sources_used.append(item.source_section)
        
        if not transport_context:
            missing_info.append("Transport timing and pattern information")
            return ReasoningResult(
                response="This information is not present in the local context file.",
                confidence=0.0,
                sources_used=sources_used,
                reasoning_chain=reasoning_chain,
                missing_info=missing_info
            )
        
        current_hour = current_time.hour
        response_parts = []
        confidence = 0.7
        
        # Check if it's peak hours
        is_peak = (8 <= current_hour <= 11) or (18 <= current_hour <= 21)
        reasoning_chain.append(f"Current hour: {current_hour}, Peak time: {is_peak}")
        
        if is_peak:
            response_parts.append("You're traveling during peak hours.")
            if "after 7 pm roads are jammed" in str(timing_context.content if timing_context else ""):
                response_parts.append("Roads are typically jammed after 7 PM - plan for extra travel time.")
                reasoning_chain.append("Applied local timing pattern: post-7PM traffic")
        
        # Add transport mode advice
        if 'auto' in query.lower():
            response_parts.append("For auto-rickshaw: insist on meter during day, expect 1.5x rate after midnight.")
            reasoning_chain.append("Added auto-rickshaw specific advice")
        elif 'train' in query.lower() or 'local' in query.lower():
            response_parts.append("Local train is fastest but most crowded during peak hours. Stand on left, let people exit first.")
            reasoning_chain.append("Added local train etiquette")
        
        response = " ".join(response_parts) if response_parts else "I need more specific transport information from the local context."
        
        return ReasoningResult(
            response=response,
            confidence=confidence,
            sources_used=sources_used,
            reasoning_chain=reasoning_chain,
            missing_info=missing_info
        )
    
    def _reason_slang_translation(self, query: str, analysis: Dict[str, Any], 
                                context: List[ContextItem]) -> ReasoningResult:
        """Translate local slang using context"""
        reasoning_chain = ["Analyzing slang translation request"]
        sources_used = []
        missing_info = []
        
        # Find slang context
        slang_context = None
        for item in context:
            if item.category == ContextCategory.SLANG:
                slang_context = item
                sources_used.append(item.source_section)
                break
        
        if not slang_context:
            missing_info.append("Local slang dictionary")
            return ReasoningResult(
                response="This information is not present in the local context file.",
                confidence=0.0,
                sources_used=sources_used,
                reasoning_chain=reasoning_chain,
                missing_info=missing_info
            )
        
        # Parse slang data
        try:
            slang_data = eval(slang_context.content) if isinstance(slang_context.content, str) else slang_context.content
        except:
            slang_data = {}
        
        # Extract slang words from query
        query_words = query.lower().split()
        translations = []
        
        for word in query_words:
            if word in slang_data:
                translations.append(f"'{word}' means '{slang_data[word]}'")
                reasoning_chain.append(f"Found translation for: {word}")
        
        if translations:
            response = "Local slang translation: " + ", ".join(translations)
            confidence = 0.9
        else:
            # Check if query contains slang we don't know
            missing_info.append("Translation for specific slang terms in query")
            response = "I don't have the translation for those specific slang terms in my local context."
            confidence = 0.2
        
        return ReasoningResult(
            response=response,
            confidence=confidence,
            sources_used=sources_used,
            reasoning_chain=reasoning_chain,
            missing_info=missing_info
        )
    
    def _reason_cultural_advice(self, query: str, analysis: Dict[str, Any], 
                              context: List[ContextItem]) -> ReasoningResult:
        """Provide cultural advice based on local context"""
        reasoning_chain = ["Analyzing cultural advice request"]
        sources_used = []
        missing_info = []
        
        # Find cultural context
        culture_context = None
        for item in context:
            if item.category == ContextCategory.CULTURE:
                culture_context = item
                sources_used.append(item.source_section)
                break
        
        if not culture_context:
            missing_info.append("Cultural do's and don'ts information")
            return ReasoningResult(
                response="This information is not present in the local context file.",
                confidence=0.0,
                sources_used=sources_used,
                reasoning_chain=reasoning_chain,
                missing_info=missing_info
            )
        
        # Parse cultural data
        culture_data = eval(culture_context.content) if isinstance(culture_context.content, str) else culture_context.content
        
        response_parts = []
        confidence = 0.8
        
        # Check query against do's and don'ts
        query_lower = query.lower()
        
        if 'dos' in culture_data:
            for do_item in culture_data['dos']:
                if any(keyword in query_lower for keyword in ['wear', 'dress', 'clothes', 'shorts']):
                    if 'revealing clothes' in do_item.lower():
                        response_parts.append(f"Cultural advice: {do_item}")
                        reasoning_chain.append("Found relevant cultural guidance about clothing")
        
        if 'donts' in culture_data:
            for dont_item in culture_data['donts']:
                # Match query context with don'ts
                if any(keyword in query_lower for keyword in dont_item.lower().split()):
                    response_parts.append(f"Important: {dont_item}")
                    reasoning_chain.append(f"Found relevant cultural restriction: {dont_item}")
        
        if response_parts:
            response = " ".join(response_parts)
        else:
            missing_info.append("Specific cultural guidance for the situation mentioned")
            response = "I don't have specific cultural guidance for that situation in my local context."
            confidence = 0.3
        
        return ReasoningResult(
            response=response,
            confidence=confidence,
            sources_used=sources_used,
            reasoning_chain=reasoning_chain,
            missing_info=missing_info
        )
    
    def _reason_timing_query(self, query: str, analysis: Dict[str, Any], 
                           context: List[ContextItem], current_time: datetime) -> ReasoningResult:
        """Answer timing-related queries"""
        reasoning_chain = ["Analyzing timing query"]
        sources_used = []
        missing_info = []
        
        # This would use timing patterns from context
        response = "I need specific timing information from the local context to answer this accurately."
        confidence = 0.3
        
        return ReasoningResult(
            response=response,
            confidence=confidence,
            sources_used=sources_used,
            reasoning_chain=reasoning_chain,
            missing_info=["Specific timing patterns for the queried activity"]
        )
    
    def _reason_general_query(self, query: str, analysis: Dict[str, Any], 
                            context: List[ContextItem]) -> ReasoningResult:
        """Handle general queries using available context"""
        reasoning_chain = ["Analyzing general query"]
        sources_used = []
        
        if context:
            # Use the most relevant context item
            best_context = context[0]
            sources_used.append(best_context.source_section)
            
            response = f"Based on local context: {str(best_context.content)[:200]}..."
            confidence = best_context.confidence
        else:
            response = "This information is not present in the local context file."
            confidence = 0.0
        
        return ReasoningResult(
            response=response,
            confidence=confidence,
            sources_used=sources_used,
            reasoning_chain=reasoning_chain,
            missing_info=["Relevant local information for this query"]
        )
    
    def _get_time_period(self, hour: int) -> str:
        """Convert hour to time period"""
        if 6 <= hour < 10:
            return "morning"
        elif 10 <= hour < 15:
            return "afternoon"
        elif 15 <= hour < 20:
            return "evening"
        else:
            return "night"