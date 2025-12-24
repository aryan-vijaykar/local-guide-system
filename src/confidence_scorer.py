"""
Confidence Scoring Module
Computes confidence scores for responses based on available context
Determines when to ask clarifying questions
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .context_loader import ContextItem, ContextCategory

class ConfidenceLevel(Enum):
    VERY_LOW = "very_low"      # 0.0 - 0.2
    LOW = "low"                # 0.2 - 0.4
    MEDIUM = "medium"          # 0.4 - 0.6
    HIGH = "high"              # 0.6 - 0.8
    VERY_HIGH = "very_high"    # 0.8 - 1.0

@dataclass
class ConfidenceScore:
    overall_score: float
    level: ConfidenceLevel
    factors: Dict[str, float]
    missing_information: List[str]
    recommendation: str
    should_ask_clarification: bool

class ConfidenceScorer:
    def __init__(self, confidence_threshold: float = 0.6):
        self.confidence_threshold = confidence_threshold
        
    def calculate_confidence(self, 
                           query: str,
                           relevant_context: List[ContextItem],
                           query_analysis: Dict[str, Any],
                           response_content: str) -> ConfidenceScore:
        """Calculate overall confidence score for a response"""
        
        factors = {}
        missing_info = []
        
        # Factor 1: Context Availability (30% weight)
        context_score = self._score_context_availability(query, relevant_context)
        factors['context_availability'] = context_score
        
        # Factor 2: Query Specificity (20% weight)
        specificity_score = self._score_query_specificity(query, query_analysis)
        factors['query_specificity'] = specificity_score
        
        # Factor 3: Context Relevance (25% weight)
        relevance_score = self._score_context_relevance(query, relevant_context)
        factors['context_relevance'] = relevance_score
        
        # Factor 4: Information Completeness (15% weight)
        completeness_score, missing = self._score_information_completeness(query_analysis, relevant_context)
        factors['information_completeness'] = completeness_score
        missing_info.extend(missing)
        
        # Factor 5: Response Quality (10% weight)
        response_score = self._score_response_quality(response_content)
        factors['response_quality'] = response_score
        
        # Calculate weighted overall score
        weights = {
            'context_availability': 0.30,
            'query_specificity': 0.20,
            'context_relevance': 0.25,
            'information_completeness': 0.15,
            'response_quality': 0.10
        }
        
        overall_score = sum(factors[factor] * weights[factor] for factor in factors)
        
        # Determine confidence level
        level = self._get_confidence_level(overall_score)
        
        # Determine if clarification is needed
        should_ask_clarification = overall_score < self.confidence_threshold
        
        # Generate recommendation
        recommendation = self._generate_recommendation(overall_score, factors, missing_info)
        
        return ConfidenceScore(
            overall_score=overall_score,
            level=level,
            factors=factors,
            missing_information=missing_info,
            recommendation=recommendation,
            should_ask_clarification=should_ask_clarification
        )
    
    def _score_context_availability(self, query: str, context: List[ContextItem]) -> float:
        """Score based on how much relevant context is available"""
        if not context:
            return 0.0
        
        # Base score for having any context
        base_score = 0.3
        
        # Additional score based on number of relevant context items
        context_bonus = min(0.5, len(context) * 0.1)
        
        # Bonus for high-confidence context items
        confidence_bonus = sum(item.confidence for item in context[:3]) / 3 * 0.2
        
        return min(1.0, base_score + context_bonus + confidence_bonus)
    
    def _score_query_specificity(self, query: str, analysis: Dict[str, Any]) -> float:
        """Score based on how specific and clear the query is"""
        score = 0.0
        
        # Length factor (not too short, not too long)
        query_length = len(query.split())
        if 3 <= query_length <= 20:
            score += 0.3
        elif query_length > 20:
            score += 0.2
        else:
            score += 0.1
        
        # Intent clarity
        if analysis.get('intent') != 'general_query':
            score += 0.3
        
        # Time context specificity
        time_context = analysis.get('time_context', {})
        if time_context.get('specific_time') or time_context.get('time_period'):
            score += 0.2
        
        # Location context specificity
        if analysis.get('location_context'):
            score += 0.2
        
        return min(1.0, score)
    
    def _score_context_relevance(self, query: str, context: List[ContextItem]) -> float:
        """Score based on how relevant the context is to the query"""
        if not context:
            return 0.0
        
        # Average relevance of top context items
        top_context = context[:3]  # Consider top 3 most relevant
        avg_relevance = sum(item.confidence for item in top_context) / len(top_context)
        
        # Bonus for having multiple relevant categories
        categories = set(item.category for item in context)
        category_bonus = min(0.2, len(categories) * 0.05)
        
        return min(1.0, avg_relevance + category_bonus)
    
    def _score_information_completeness(self, analysis: Dict[str, Any], 
                                      context: List[ContextItem]) -> Tuple[float, List[str]]:
        """Score based on completeness of information for the query type"""
        intent = analysis.get('intent', 'general_query')
        missing_info = []
        score = 0.0
        
        # Required information by intent type
        requirements = {
            'food_recommendation': {
                'required_categories': [ContextCategory.FOOD],
                'helpful_categories': [ContextCategory.TIMING, ContextCategory.COST],
                'required_fields': ['timings', 'areas']
            },
            'transport_query': {
                'required_categories': [ContextCategory.TRANSPORT],
                'helpful_categories': [ContextCategory.TIMING, ContextCategory.SAFETY],
                'required_fields': ['peak_hours', 'transport_modes']
            },
            'slang_translation': {
                'required_categories': [ContextCategory.SLANG],
                'helpful_categories': [ContextCategory.CULTURE],
                'required_fields': ['slang_dictionary']
            },
            'cultural_advice': {
                'required_categories': [ContextCategory.CULTURE],
                'helpful_categories': [ContextCategory.SAFETY],
                'required_fields': ['dos', 'donts']
            }
        }
        
        if intent in requirements:
            req = requirements[intent]
            
            # Check for required categories
            available_categories = set(item.category for item in context)
            required_categories = set(req['required_categories'])
            
            if required_categories.issubset(available_categories):
                score += 0.6
            else:
                missing_categories = required_categories - available_categories
                missing_info.extend([f"{cat.value} information" for cat in missing_categories])
            
            # Check for helpful categories
            helpful_categories = set(req.get('helpful_categories', []))
            available_helpful = helpful_categories.intersection(available_categories)
            score += len(available_helpful) / len(helpful_categories) * 0.4 if helpful_categories else 0.4
            
        else:
            # General query - score based on any available context
            score = 0.5 if context else 0.0
        
        return min(1.0, score), missing_info
    
    def _score_response_quality(self, response: str) -> float:
        """Score the quality of the generated response"""
        if not response or response.strip() == "":
            return 0.0
        
        score = 0.0
        
        # Length appropriateness
        response_length = len(response.split())
        if 10 <= response_length <= 100:
            score += 0.4
        elif response_length > 100:
            score += 0.3
        else:
            score += 0.2
        
        # Check for specific local information
        local_indicators = ['local', 'mumbai', 'bhai', 'tapri', 'vada pav', 'auto', 'train']
        local_mentions = sum(1 for indicator in local_indicators if indicator.lower() in response.lower())
        score += min(0.3, local_mentions * 0.1)
        
        # Check for actionable advice
        actionable_words = ['recommend', 'suggest', 'try', 'go to', 'avoid', 'consider']
        actionable_mentions = sum(1 for word in actionable_words if word.lower() in response.lower())
        score += min(0.3, actionable_mentions * 0.1)
        
        return min(1.0, score)
    
    def _get_confidence_level(self, score: float) -> ConfidenceLevel:
        """Convert numeric score to confidence level"""
        if score >= 0.8:
            return ConfidenceLevel.VERY_HIGH
        elif score >= 0.6:
            return ConfidenceLevel.HIGH
        elif score >= 0.4:
            return ConfidenceLevel.MEDIUM
        elif score >= 0.2:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW
    
    def _generate_recommendation(self, score: float, factors: Dict[str, float], 
                               missing_info: List[str]) -> str:
        """Generate recommendation based on confidence analysis"""
        
        if score >= 0.8:
            return "High confidence response. Information is comprehensive and reliable."
        
        elif score >= 0.6:
            return "Good confidence response. Minor information gaps may exist."
        
        elif score >= 0.4:
            recommendations = []
            
            # Identify weak factors
            weak_factors = [factor for factor, value in factors.items() if value < 0.5]
            
            if 'context_availability' in weak_factors:
                recommendations.append("Need more local context information")
            
            if 'query_specificity' in weak_factors:
                recommendations.append("Query could be more specific")
            
            if 'context_relevance' in weak_factors:
                recommendations.append("Available context may not be directly relevant")
            
            if missing_info:
                recommendations.append(f"Missing: {', '.join(missing_info[:3])}")
            
            return "Medium confidence. " + ". ".join(recommendations[:2])
        
        else:
            return "Low confidence. Significant information gaps exist. Consider asking clarifying questions."
    
    def should_request_clarification(self, confidence_score: ConfidenceScore, 
                                   query_analysis: Dict[str, Any]) -> Optional[str]:
        """Determine if clarification should be requested and generate clarifying question"""
        
        if not confidence_score.should_ask_clarification:
            return None
        
        intent = query_analysis.get('intent', 'general_query')
        missing_info = confidence_score.missing_information
        
        # Generate specific clarifying questions based on intent and missing info
        clarification_templates = {
            'food_recommendation': [
                "What time are you planning to eat?",
                "Which area of the city are you in?",
                "What's your budget range?",
                "Are you looking for street food or restaurant food?"
            ],
            'transport_query': [
                "Where are you starting from and going to?",
                "What time do you need to travel?",
                "Do you prefer train, auto, or bus?",
                "Are you okay with crowded transport?"
            ],
            'slang_translation': [
                "Which specific words or phrases need translation?",
                "Are you looking to understand or to speak like a local?"
            ],
            'cultural_advice': [
                "What specific situation or activity are you asking about?",
                "Are you visiting religious places or general areas?"
            ]
        }
        
        if intent in clarification_templates:
            # Select most relevant clarifying question based on missing info
            questions = clarification_templates[intent]
            
            if 'timing' in str(missing_info).lower():
                return next((q for q in questions if 'time' in q.lower()), questions[0])
            elif 'location' in str(missing_info).lower():
                return next((q for q in questions if any(word in q.lower() for word in ['where', 'area'])), questions[0])
            else:
                return questions[0]
        
        return "Could you provide more specific details about what you're looking for?"
    
    def get_confidence_explanation(self, confidence_score: ConfidenceScore) -> str:
        """Generate human-readable explanation of confidence score"""
        
        explanations = []
        
        # Overall assessment
        level_descriptions = {
            ConfidenceLevel.VERY_HIGH: "I'm very confident in this response",
            ConfidenceLevel.HIGH: "I'm quite confident in this response",
            ConfidenceLevel.MEDIUM: "I have moderate confidence in this response",
            ConfidenceLevel.LOW: "I have limited confidence in this response",
            ConfidenceLevel.VERY_LOW: "I have very low confidence in this response"
        }
        
        explanations.append(level_descriptions[confidence_score.level])
        
        # Factor explanations
        if confidence_score.factors['context_availability'] < 0.5:
            explanations.append("limited local context available")
        
        if confidence_score.factors['context_relevance'] < 0.5:
            explanations.append("context may not be directly relevant")
        
        if confidence_score.missing_information:
            missing_str = ", ".join(confidence_score.missing_information[:2])
            explanations.append(f"missing information about {missing_str}")
        
        return " because " + " and ".join(explanations[1:]) if len(explanations) > 1 else explanations[0] + "."