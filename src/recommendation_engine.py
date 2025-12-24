"""
Recommendation Engine
Provides context-aware recommendations for food, places, and activities
Uses local timing, crowd patterns, budget, and weather considerations
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, time
from enum import Enum

from .context_loader import ContextLoader, ContextCategory

class RecommendationType(Enum):
    FOOD = "food"
    TRANSPORT = "transport"
    ACTIVITY = "activity"
    SAFETY = "safety"

@dataclass
class Recommendation:
    title: str
    description: str
    reasoning: str
    confidence: float
    timing_advice: Optional[str] = None
    budget_info: Optional[str] = None
    crowd_level: Optional[str] = None
    weather_consideration: Optional[str] = None

@dataclass
class RecommendationRequest:
    type: RecommendationType
    current_time: datetime
    location: Optional[str] = None
    budget_level: Optional[str] = None  # 'low', 'medium', 'high'
    weather_condition: Optional[str] = None
    crowd_tolerance: Optional[str] = None  # 'avoid', 'okay', 'prefer'
    specific_preferences: Optional[List[str]] = None

class RecommendationEngine:
    def __init__(self, context_loader: ContextLoader):
        self.context_loader = context_loader
        self.context_data = context_loader.structured_data
        
    def get_recommendations(self, request: RecommendationRequest) -> List[Recommendation]:
        """Get recommendations based on request parameters"""
        
        if request.type == RecommendationType.FOOD:
            return self._get_food_recommendations(request)
        elif request.type == RecommendationType.TRANSPORT:
            return self._get_transport_recommendations(request)
        elif request.type == RecommendationType.ACTIVITY:
            return self._get_activity_recommendations(request)
        elif request.type == RecommendationType.SAFETY:
            return self._get_safety_recommendations(request)
        else:
            return []
    
    def _get_food_recommendations(self, request: RecommendationRequest) -> List[Recommendation]:
        """Generate food recommendations based on context and constraints"""
        recommendations = []
        
        if 'food' not in self.context_data:
            return [Recommendation(
                title="No Food Information",
                description="Food information is not present in the local context file.",
                reasoning="Missing local food data",
                confidence=0.0
            )]
        
        food_data = self.context_data['food']
        current_hour = request.current_time.hour
        time_period = self._get_time_period(current_hour)
        
        # Time-based recommendations
        if 'timings' in food_data:
            for timing_key, foods in food_data['timings'].items():
                if time_period.lower() in timing_key.lower():
                    recommendations.append(Recommendation(
                        title=f"Perfect for {time_period}",
                        description=foods,
                        reasoning=f"Based on local timing patterns for {timing_key}",
                        confidence=0.9,
                        timing_advice=f"Best time for these foods: {timing_key}"
                    ))
        
        # Location-based recommendations
        if request.location and 'areas' in food_data:
            for area, area_info in food_data['areas'].items():
                if request.location.lower() in area.lower() or area.lower() in request.location.lower():
                    crowd_advice = self._get_crowd_advice(area_info.get('timing', ''), request.current_time)
                    
                    recommendations.append(Recommendation(
                        title=f"Local Favorite at {area}",
                        description=area_info['foods'],
                        reasoning=f"Popular area mentioned in local context",
                        confidence=0.8,
                        timing_advice=area_info.get('timing'),
                        crowd_level=crowd_advice
                    ))
        
        # Budget-aware recommendations
        if request.budget_level and 'pricing' in self.context_data:
            pricing_data = self.context_data['pricing']
            budget_recs = self._filter_by_budget(pricing_data, request.budget_level)
            recommendations.extend(budget_recs)
        
        # Weather-based adjustments
        if request.weather_condition:
            weather_recs = self._adjust_for_weather(recommendations, request.weather_condition)
            recommendations = weather_recs
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _get_transport_recommendations(self, request: RecommendationRequest) -> List[Recommendation]:
        """Generate transport recommendations"""
        recommendations = []
        
        if 'transport' not in self.context_data:
            return [Recommendation(
                title="No Transport Information",
                description="Transport information is not present in the local context file.",
                reasoning="Missing local transport data",
                confidence=0.0
            )]
        
        current_hour = request.current_time.hour
        is_peak = self._is_peak_hour(current_hour)
        
        # Peak hour recommendations
        if is_peak:
            recommendations.append(Recommendation(
                title="Peak Hour Transport Strategy",
                description="Local trains are fastest but extremely crowded. Auto-rickshaws will be slower due to traffic.",
                reasoning="Current time falls within peak hours (8-11 AM, 6-9 PM)",
                confidence=0.9,
                timing_advice="Consider delaying travel by 30-60 minutes if possible",
                crowd_level="Very High"
            ))
        else:
            recommendations.append(Recommendation(
                title="Off-Peak Travel Advantage",
                description="Good time to travel - trains are manageable and roads are clearer.",
                reasoning="Current time is outside peak hours",
                confidence=0.8,
                timing_advice="Optimal travel time",
                crowd_level="Moderate"
            ))
        
        # Mode-specific recommendations
        transport_data = self.context_data['transport']
        
        # Local train advice
        if 'local_trains' in transport_data or any('train' in str(v).lower() for v in transport_data.values()):
            recommendations.append(Recommendation(
                title="Local Train Etiquette",
                description="Stand on left, let people exit first. Ladies compartment in first 4 coaches.",
                reasoning="Based on local train culture and rules",
                confidence=1.0,
                timing_advice="Peak: 8-11 AM, 6-9 PM (extremely crowded)"
            ))
        
        # Auto-rickshaw advice
        recommendations.append(Recommendation(
            title="Auto-Rickshaw Tips",
            description="Insist on meter during day. Night charges are 1.5x after midnight.",
            reasoning="Standard local auto-rickshaw practices",
            confidence=0.9,
            budget_info="Meter rate + night surcharge if applicable"
        ))
        
        return recommendations
    
    def _get_activity_recommendations(self, request: RecommendationRequest) -> List[Recommendation]:
        """Generate activity recommendations"""
        recommendations = []
        
        current_hour = request.current_time.hour
        
        # Time-based activity suggestions
        if 16 <= current_hour <= 20:  # Evening
            recommendations.append(Recommendation(
                title="Evening Street Food Tour",
                description="Perfect time for Bhel Puri, Sev Puri, and Cutting Chai at local spots",
                reasoning="Evening is peak time for street food according to local patterns",
                confidence=0.8,
                timing_advice="4-8 PM is ideal for street food",
                crowd_level="High but manageable"
            ))
        
        # Weather-based activities
        if request.weather_condition:
            if 'rain' in request.weather_condition.lower():
                recommendations.append(Recommendation(
                    title="Monsoon Activity Adjustment",
                    description="Indoor activities recommended. If going out, carry umbrella and avoid low-lying areas.",
                    reasoning="Monsoon weather requires special precautions in local context",
                    confidence=0.9,
                    weather_consideration="Heavy rains and flooding possible"
                ))
        
        return recommendations
    
    def _get_safety_recommendations(self, request: RecommendationRequest) -> List[Recommendation]:
        """Generate safety recommendations"""
        recommendations = []
        
        if 'safety' not in self.context_data:
            return [Recommendation(
                title="No Safety Information",
                description="Safety information is not present in the local context file.",
                reasoning="Missing local safety data",
                confidence=0.0
            )]
        
        safety_data = self.context_data['safety']
        current_hour = request.current_time.hour
        
        # Time-based safety advice
        if current_hour >= 22 or current_hour <= 5:  # Late night/early morning
            recommendations.append(Recommendation(
                title="Late Night Safety",
                description="Stick to main roads and well-lit areas. Use trusted transport options.",
                reasoning="Late night hours require extra caution",
                confidence=0.9,
                timing_advice="Extra caution needed during late night hours"
            ))
        
        # General safety recommendations from context
        for safety_item in safety_data:
            if isinstance(safety_item, str):
                # Parse safety advice
                if ':' in safety_item:
                    situation, advice = safety_item.split(':', 1)
                    recommendations.append(Recommendation(
                        title=f"Safety: {situation.strip()}",
                        description=advice.strip(),
                        reasoning="Based on local safety guidelines",
                        confidence=0.8
                    ))
        
        return recommendations
    
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
    
    def _is_peak_hour(self, hour: int) -> bool:
        """Check if current hour is peak time"""
        return (8 <= hour <= 11) or (18 <= hour <= 21)
    
    def _get_crowd_advice(self, timing_info: str, current_time: datetime) -> str:
        """Generate crowd level advice based on timing"""
        current_hour = current_time.hour
        
        # Parse timing info for crowd patterns
        if 'evening' in timing_info.lower() and 16 <= current_hour <= 20:
            return "High - Peak evening crowd"
        elif 'morning' in timing_info.lower() and 8 <= current_hour <= 10:
            return "High - Morning rush"
        elif self._is_peak_hour(current_hour):
            return "Moderate to High"
        else:
            return "Low to Moderate"
    
    def _filter_by_budget(self, pricing_data: Dict[str, Any], budget_level: str) -> List[Recommendation]:
        """Filter recommendations by budget level"""
        recommendations = []
        
        budget_ranges = {
            'low': (0, 50),
            'medium': (50, 150),
            'high': (150, float('inf'))
        }
        
        min_budget, max_budget = budget_ranges.get(budget_level, (0, float('inf')))
        
        for category, items in pricing_data.items():
            if isinstance(items, dict):
                suitable_items = []
                for item, price_str in items.items():
                    import re
        # Extract numeric price (simplified)
                    price_match = re.search(r'₹(\d+)', price_str)
                    if price_match:
                        price = int(price_match.group(1))
                        if min_budget <= price <= max_budget:
                            suitable_items.append(f"{item} ({price_str})")
                
                if suitable_items:
                    recommendations.append(Recommendation(
                        title=f"Budget-Friendly {category.title()}",
                        description=", ".join(suitable_items),
                        reasoning=f"Items matching {budget_level} budget range",
                        confidence=0.7,
                        budget_info=f"Within {budget_level} budget range"
                    ))
        
        return recommendations
    
    def _adjust_for_weather(self, recommendations: List[Recommendation], weather_condition: str) -> List[Recommendation]:
        """Adjust recommendations based on weather"""
        adjusted_recs = []
        
        for rec in recommendations:
            adjusted_rec = rec
            
            if 'rain' in weather_condition.lower():
                # Add weather considerations for rainy weather
                adjusted_rec.weather_consideration = "Monsoon: Check for covered areas, carry umbrella"
                if 'outdoor' in rec.description.lower():
                    adjusted_rec.confidence *= 0.7  # Reduce confidence for outdoor activities
            elif 'hot' in weather_condition.lower():
                adjusted_rec.weather_consideration = "Hot weather: Stay hydrated, prefer AC venues"
            
            adjusted_recs.append(adjusted_rec)
        
        return adjusted_recs
    
    def get_festival_aware_recommendations(self, request: RecommendationRequest, 
                                        festival_name: Optional[str] = None) -> List[Recommendation]:
        """Get recommendations that consider ongoing festivals"""
        recommendations = []
        
        if 'festivals' not in self.context_data:
            return self.get_recommendations(request)
        
        festival_data = self.context_data['festivals']
        
        # Check if there's festival impact information
        if festival_name or 'festival' in str(festival_data).lower():
            recommendations.append(Recommendation(
                title="Festival Impact Advisory",
                description="Expect 2x normal travel time, crowded areas, and special festival foods available.",
                reasoning="Festival period affects normal patterns",
                confidence=0.9,
                timing_advice="Plan extra travel time",
                crowd_level="Very High",
                budget_info="Festival pricing may apply"
            ))
        
        # Add regular recommendations with festival adjustments
        regular_recs = self.get_recommendations(request)
        for rec in regular_recs:
            if festival_name:
                rec.description += f" (Note: {festival_name} celebrations may affect availability and crowds)"
                rec.confidence *= 0.8  # Slightly reduce confidence due to festival uncertainty
        
        recommendations.extend(regular_recs)
        return recommendations