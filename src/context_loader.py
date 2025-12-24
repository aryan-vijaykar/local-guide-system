"""
Context Loader Module
Parses product.md and converts raw text into structured internal knowledge
"""

import re
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

class ContextCategory(Enum):
    SLANG = "slang"
    FOOD = "food"
    TRANSPORT = "transport"
    SAFETY = "safety"
    TIMING = "timing"
    COST = "cost"
    CULTURE = "culture"
    WEATHER = "weather"
    FESTIVALS = "festivals"

@dataclass
class ContextItem:
    content: str
    category: ContextCategory
    confidence: float
    source_section: str

class ContextLoader:
    def __init__(self, product_md_path: str = "product.md"):
        self.product_md_path = product_md_path
        self.structured_data = {}
        self.raw_content = ""
        
    def load_context(self) -> Dict[str, Any]:
        """Load and parse the product.md file"""
        try:
            with open(self.product_md_path, 'r', encoding='utf-8') as file:
                self.raw_content = file.read()
        except FileNotFoundError:
            raise Exception(f"product.md not found at {self.product_md_path}")
        
        return self._parse_content()
    
    def _parse_content(self) -> Dict[str, Any]:
        """Parse the markdown content into structured data"""
        sections = self._extract_sections()
        
        structured_data = {
            'city_info': self._extract_city_info(sections),
            'slang': self._extract_slang(sections),
            'food': self._extract_food_info(sections),
            'transport': self._extract_transport_info(sections),
            'culture': self._extract_cultural_info(sections),
            'weather': self._extract_weather_info(sections),
            'festivals': self._extract_festival_info(sections),
            'pricing': self._extract_pricing_info(sections),
            'safety': self._extract_safety_info(sections),
            'timing_patterns': self._extract_timing_patterns(sections)
        }
        
        self.structured_data = structured_data
        return structured_data
    
    def _extract_sections(self) -> Dict[str, str]:
        """Extract sections from markdown"""
        sections = {}
        current_section = None
        current_content = []
        
        for line in self.raw_content.split('\n'):
            if line.startswith('## '):
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                current_section = line[3:].strip()
                current_content = []
            else:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def _extract_city_info(self, sections: Dict[str, str]) -> Dict[str, str]:
        """Extract basic city information"""
        city_info = {}
        if 'City Information' in sections:
            content = sections['City Information']
            # Extract city name
            city_match = re.search(r'\*\*City Name:\*\* (.+)', content)
            if city_match:
                city_info['name'] = city_match.group(1)
            
            # Extract local name
            local_match = re.search(r'\*\*Local Name:\*\* (.+)', content)
            if local_match:
                city_info['local_name'] = local_match.group(1)
        
        return city_info
    
    def _extract_slang(self, sections: Dict[str, str]) -> Dict[str, str]:
        """Extract slang and phrases"""
        slang_dict = {}
        if 'Common Slang & Phrases' in sections:
            content = sections['Common Slang & Phrases']
            # Match pattern: - **word** - meaning
            matches = re.findall(r'- \*\*(.+?)\*\* - (.+)', content)
            for word, meaning in matches:
                slang_dict[word.lower()] = meaning
        
        return slang_dict
    
    def _extract_food_info(self, sections: Dict[str, str]) -> Dict[str, Any]:
        """Extract food and street vendor information"""
        food_info = {
            'timings': {},
            'areas': {},
            'hygiene_tips': []
        }
        
        if 'Local Food & Street Vendors' in sections:
            content = sections['Local Food & Street Vendors']
            
            # Extract timing patterns
            timing_matches = re.findall(r'- \*\*(.+?):\*\* (.+)', content)
            for time_period, foods in timing_matches:
                food_info['timings'][time_period.lower()] = foods
            
            # Extract area information
            area_matches = re.findall(r'- \*\*(.+?):\*\* (.+?) \((.+?)\)', content)
            for area, foods, timing in area_matches:
                food_info['areas'][area] = {
                    'foods': foods,
                    'timing': timing
                }
        
        return food_info
    
    def _extract_transport_info(self, sections: Dict[str, str]) -> Dict[str, Any]:
        """Extract transport habits and patterns"""
        transport_info = {
            'local_trains': {},
            'auto_rickshaws': {},
            'buses': {}
        }
        
        if 'Transport Habits' in sections:
            content = sections['Transport Habits']
            # This would be expanded based on the specific format in product.md
            # For now, storing raw content by subsection
            subsections = content.split('### ')
            for subsection in subsections[1:]:  # Skip first empty element
                lines = subsection.split('\n')
                section_name = lines[0].lower().replace(' ', '_')
                section_content = '\n'.join(lines[1:])
                transport_info[section_name] = section_content
        
        return transport_info
    
    def _extract_cultural_info(self, sections: Dict[str, str]) -> Dict[str, List[str]]:
        """Extract cultural do's and don'ts"""
        culture_info = {
            'dos': [],
            'donts': []
        }
        
        if "Cultural Do's and Don'ts" in sections:
            content = sections["Cultural Do's and Don'ts"]
            
            # Extract do's
            dos_section = re.search(r"### Do's\n(.*?)### Don'ts", content, re.DOTALL)
            if dos_section:
                dos_text = dos_section.group(1)
                culture_info['dos'] = [line.strip('- ') for line in dos_text.split('\n') if line.strip().startswith('-')]
            
            # Extract don'ts
            donts_section = re.search(r"### Don'ts\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
            if donts_section:
                donts_text = donts_section.group(1)
                culture_info['donts'] = [line.strip('- ') for line in donts_text.split('\n') if line.strip().startswith('-')]
        
        return culture_info
    
    def _extract_weather_info(self, sections: Dict[str, str]) -> Dict[str, str]:
        """Extract weather patterns"""
        weather_info = {}
        if 'Weather Patterns' in sections:
            content = sections['Weather Patterns']
            # Extract seasonal information
            seasons = re.findall(r'### (.+?)\n(.*?)(?=\n###|\Z)', content, re.DOTALL)
            for season, description in seasons:
                weather_info[season.lower()] = description.strip()
        
        return weather_info
    
    def _extract_festival_info(self, sections: Dict[str, str]) -> Dict[str, Any]:
        """Extract festival and event information"""
        festival_info = {
            'major_festivals': {},
            'impact': {}
        }
        
        if 'Festivals & Events' in sections:
            content = sections['Festivals & Events']
            # This would be expanded based on specific format
            festival_info['raw_content'] = content
        
        return festival_info
    
    def _extract_pricing_info(self, sections: Dict[str, str]) -> Dict[str, Dict[str, str]]:
        """Extract local pricing expectations"""
        pricing_info = {}
        if 'Local Pricing Expectations' in sections:
            content = sections['Local Pricing Expectations']
            
            # Extract categories and prices
            categories = re.findall(r'### (.+?)\n(.*?)(?=\n###|\Z)', content, re.DOTALL)
            for category, prices_text in categories:
                category_prices = {}
                price_matches = re.findall(r'- (.+?): (.+)', prices_text)
                for item, price in price_matches:
                    category_prices[item] = price
                pricing_info[category.lower()] = category_prices
        
        return pricing_info
    
    def _extract_safety_info(self, sections: Dict[str, str]) -> List[str]:
        """Extract safety notes"""
        safety_info = []
        if 'Safety Notes' in sections:
            content = sections['Safety Notes']
            safety_matches = re.findall(r'- \*\*(.+?):\*\* (.+)', content)
            for situation, advice in safety_matches:
                safety_info.append(f"{situation}: {advice}")
        
        return safety_info
    
    def _extract_timing_patterns(self, sections: Dict[str, str]) -> Dict[str, str]:
        """Extract local logic and timing patterns"""
        timing_patterns = {}
        if 'Local Logic Patterns' in sections:
            content = sections['Local Logic Patterns']
            patterns = re.findall(r'- "(.+?)"', content)
            for i, pattern in enumerate(patterns):
                timing_patterns[f'pattern_{i+1}'] = pattern
        
        return timing_patterns
    
    def get_context_by_category(self, category: ContextCategory) -> List[ContextItem]:
        """Get all context items for a specific category"""
        items = []
        
        category_mapping = {
            ContextCategory.SLANG: ['slang'],
            ContextCategory.FOOD: ['food'],
            ContextCategory.TRANSPORT: ['transport'],
            ContextCategory.CULTURE: ['culture'],
            ContextCategory.WEATHER: ['weather'],
            ContextCategory.FESTIVALS: ['festivals'],
            ContextCategory.COST: ['pricing'],
            ContextCategory.SAFETY: ['safety'],
            ContextCategory.TIMING: ['timing_patterns']
        }
        
        for section in category_mapping.get(category, []):
            if section in self.structured_data:
                content = self.structured_data[section]
                items.append(ContextItem(
                    content=str(content),
                    category=category,
                    confidence=1.0,
                    source_section=section
                ))
        
        return items
    
    def search_context(self, query: str) -> List[ContextItem]:
        """Search for relevant context based on query"""
        results = []
        query_lower = query.lower()
        
        # Search through all structured data
        for section_name, section_data in self.structured_data.items():
            if self._contains_relevant_info(str(section_data).lower(), query_lower):
                # Determine category based on section name
                category = self._get_category_from_section(section_name)
                results.append(ContextItem(
                    content=str(section_data),
                    category=category,
                    confidence=self._calculate_relevance_score(str(section_data).lower(), query_lower),
                    source_section=section_name
                ))
        
        # Sort by confidence score
        results.sort(key=lambda x: x.confidence, reverse=True)
        return results
    
    def _contains_relevant_info(self, content: str, query: str) -> bool:
        """Check if content contains relevant information for query"""
        query_words = query.split()
        content_words = content.split()
        
        # Simple keyword matching - can be improved with NLP
        matches = sum(1 for word in query_words if word in content_words)
        return matches > 0
    
    def _calculate_relevance_score(self, content: str, query: str) -> float:
        """Calculate relevance score between content and query"""
        query_words = set(query.split())
        content_words = set(content.split())
        
        if not query_words:
            return 0.0
        
        intersection = query_words.intersection(content_words)
        return len(intersection) / len(query_words)
    
    def _get_category_from_section(self, section_name: str) -> ContextCategory:
        """Map section name to context category"""
        mapping = {
            'slang': ContextCategory.SLANG,
            'food': ContextCategory.FOOD,
            'transport': ContextCategory.TRANSPORT,
            'culture': ContextCategory.CULTURE,
            'weather': ContextCategory.WEATHER,
            'festivals': ContextCategory.FESTIVALS,
            'pricing': ContextCategory.COST,
            'safety': ContextCategory.SAFETY,
            'timing_patterns': ContextCategory.TIMING
        }
        return mapping.get(section_name, ContextCategory.CULTURE)