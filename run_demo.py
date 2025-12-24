#!/usr/bin/env python3
"""
Demo Script for The Local Guide System
Shows the system capabilities with realistic scenarios
"""

from src.local_guide_system import LocalGuideSystem
from datetime import datetime

def main():
    print("🌍 The Local Guide System - Demo")
    print("=" * 50)
    
    # Initialize system
    guide = LocalGuideSystem()
    status = guide.get_system_status()
    
    if not status['initialized']:
        print(f"❌ System failed to initialize: {status.get('error', 'Unknown error')}")
        return
    
    print(f"✅ System ready for {status['city_name']}")
    print(f"📚 Loaded {len(status['context_sections_loaded'])} context sections")
    print(f"🗣️  {status['slang_words_count']} slang words available")
    
    # Demo scenarios
    scenarios = [
        {
            "title": "🍽️  Food Recommendation (Evening)",
            "query": "Bhai, where should I eat dinner? I'm near Juhu beach.",
            "time": datetime(2024, 1, 1, 19, 0)
        },
        {
            "title": "🗣️  Slang Translation",
            "query": "What does cutting mean?",
            "time": datetime(2024, 1, 1, 16, 0)
        },
        {
            "title": "🚊 Transport Query (Peak Hour)",
            "query": "How to reach CST station by local train?",
            "time": datetime(2024, 1, 1, 8, 30)
        },
        {
            "title": "👕 Cultural Advice",
            "query": "Is it okay to wear shorts in Mumbai?",
            "time": datetime(2024, 1, 1, 14, 0)
        },
        {
            "title": "🎭 Mixed Language Query",
            "query": "Bhai, scene kya hai for timepass tonight?",
            "time": datetime(2024, 1, 1, 20, 0)
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['title']}")
        print(f"   Query: '{scenario['query']}'")
        print("   " + "-" * 45)
        
        response = guide.process_query(scenario['query'], scenario['time'])
        
        print(f"   🤖 {response.response_text}")
        
        # Show slang translation if available
        if response.slang_translation and response.slang_translation.slang_words_found:
            print(f"   🗣️  Slang: {', '.join([f'{w}→{m}' for w, m in response.slang_translation.slang_words_found])}")
        
        # Show confidence
        confidence_level = response.confidence_score.level.value if hasattr(response.confidence_score.level, 'value') else str(response.confidence_score.level)
        confidence_emoji = {"very_high": "🟢", "high": "🟢", "medium": "🟡", "low": "🟠", "very_low": "🔴"}
        emoji = confidence_emoji.get(confidence_level, "⚪")
        print(f"   {emoji} Confidence: {confidence_level.replace('_', ' ').title()} ({response.confidence_score.overall_score:.2f})")
    
    print(f"\n🎉 Demo completed! The system successfully processed {len(scenarios)} different query types.")
    print("💡 Try running 'python main.py' for interactive mode!")

if __name__ == "__main__":
    main()