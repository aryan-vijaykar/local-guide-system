#!/usr/bin/env python3
"""
The Local Guide System - Main Application
Advanced AI prototype that understands local culture through product.md context
"""

import sys
import json
from datetime import datetime
from typing import Dict, Any

from src.local_guide_system import LocalGuideSystem

class LocalGuideApp:
    def __init__(self):
        """Initialize the Local Guide Application"""
        print("🌍 Initializing The Local Guide System...")
        
        try:
            self.guide_system = LocalGuideSystem()
            status = self.guide_system.get_system_status()
            
            if status['initialized']:
                print(f"✅ System initialized successfully!")
                print(f"📍 City: {status['city_name']}")
                print(f"📚 Context sections loaded: {len(status['context_sections_loaded'])}")
                print(f"🗣️  Slang words available: {status['slang_words_count']}")
                print(f"🍽️  Food areas mapped: {status['food_areas_count']}")
                print("-" * 50)
            else:
                print(f"❌ System initialization failed: {status.get('error', 'Unknown error')}")
                print("Please ensure product.md exists and is properly formatted.")
                sys.exit(1)
                
        except Exception as e:
            print(f"❌ Critical error during initialization: {e}")
            sys.exit(1)
    
    def run_interactive_mode(self):
        """Run the system in interactive mode"""
        print("🤖 Local Guide is ready! Ask me anything about the city.")
        print("💡 Try queries like:")
        print("   - 'Bhai, where should I eat tonight?'")
        print("   - 'What does cutting mean?'")
        print("   - 'How long to reach station by auto?'")
        print("   - 'Is it okay to wear shorts here?'")
        print("\n📝 Type 'quit' to exit, 'debug <query>' for debug info")
        print("=" * 50)
        
        while True:
            try:
                user_input = input("\n🗣️  You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Thanks for using The Local Guide! Stay safe, bhai!")
                    break
                
                if user_input.lower().startswith('debug '):
                    query = user_input[6:]  # Remove 'debug ' prefix
                    self._handle_debug_query(query)
                    continue
                
                if user_input.lower() == 'status':
                    self._show_system_status()
                    continue
                
                if user_input.lower().startswith('translate '):
                    text = user_input[10:]  # Remove 'translate ' prefix
                    self._handle_translation(text)
                    continue
                
                if not user_input:
                    print("🤔 Please ask me something!")
                    continue
                
                # Process the query
                response = self.guide_system.process_query(user_input)
                self._display_response(response)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error processing query: {e}")
    
    def _display_response(self, response):
        """Display the system response in a user-friendly format"""
        print(f"\n🤖 Local Guide: {response.response_text}")
        
        # Show slang translation if available
        if response.slang_translation and response.slang_translation.slang_words_found:
            print(f"\n🗣️  Slang Translation:")
            for slang, meaning in response.slang_translation.slang_words_found:
                print(f"   '{slang}' → {meaning}")
            
            if response.slang_translation.cultural_context:
                print(f"   💡 Cultural Context: {response.slang_translation.cultural_context}")
        
        # Show recommendations if available
        if response.recommendations:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(response.recommendations[:3], 1):
                print(f"   {i}. {rec.title}")
                print(f"      {rec.description}")
                if rec.timing_advice:
                    print(f"      ⏰ {rec.timing_advice}")
                if rec.budget_info:
                    print(f"      💰 {rec.budget_info}")
        
        # Show confidence level
        confidence_emoji = {
            "very_high": "🟢",
            "high": "🟢", 
            "medium": "🟡",
            "low": "🟠",
            "very_low": "🔴"
        }
        
        confidence_level = response.confidence_score.level.value if hasattr(response.confidence_score.level, 'value') else str(response.confidence_score.level)
        emoji = confidence_emoji.get(confidence_level, "⚪")
        print(f"\n{emoji} Confidence: {confidence_level.replace('_', ' ').title()} ({response.confidence_score.overall_score:.2f})")
        
        # Show sources used
        if response.sources_used:
            print(f"📚 Sources: {', '.join(response.sources_used)}")
    
    def _handle_debug_query(self, query: str):
        """Handle debug queries to show internal processing"""
        print(f"\n🔍 Debug Analysis for: '{query}'")
        print("=" * 40)
        
        debug_info = self.guide_system.debug_query_processing(query)
        
        if 'error' in debug_info:
            print(f"❌ {debug_info['error']}")
            return
        
        # Query Analysis
        print("1️⃣ Query Analysis:")
        analysis = debug_info['query_analysis']
        print(f"   Intent: {analysis['intent']}")
        print(f"   Keywords: {analysis['keywords']}")
        print(f"   Time Context: {analysis['time_context']}")
        print(f"   Contains Slang: {analysis['contains_slang']}")
        
        # Slang Detection
        print("\n2️⃣ Slang Detection:")
        slang_info = debug_info['slang_detection']
        print(f"   Mixed Language: {slang_info['is_mixed_language']}")
        print(f"   Slang Words Found: {slang_info['slang_words']}")
        
        # Context Retrieval
        print("\n3️⃣ Relevant Context:")
        for i, context in enumerate(debug_info['relevant_context'][:3], 1):
            print(f"   {i}. Category: {context['category']}")
            print(f"      Confidence: {context['confidence']:.2f}")
            print(f"      Source: {context['source']}")
            print(f"      Preview: {context['content_preview']}")
        
        # Reasoning Result
        print("\n4️⃣ Reasoning Result:")
        reasoning = debug_info['reasoning_result']
        print(f"   Response: {reasoning['response'][:100]}...")
        print(f"   Confidence: {reasoning['confidence']:.2f}")
        print(f"   Sources Used: {reasoning['sources_used']}")
        print(f"   Missing Info: {reasoning['missing_info']}")
    
    def _handle_translation(self, text: str):
        """Handle translation requests"""
        print(f"\n🔄 Translation for: '{text}'")
        
        # Detect and translate
        translation = self.guide_system.translate_slang(text, "to_standard")
        
        print(f"📝 Original: {translation.original_text}")
        print(f"📝 Translated: {translation.translated_text}")
        
        if translation.slang_words_found:
            print(f"🗣️  Slang Words:")
            for slang, meaning in translation.slang_words_found:
                print(f"   '{slang}' → {meaning}")
        
        if translation.cultural_context:
            print(f"💡 Cultural Context: {translation.cultural_context}")
        
        print(f"🎯 Confidence: {translation.confidence:.2f}")
    
    def _show_system_status(self):
        """Show detailed system status"""
        status = self.guide_system.get_system_status()
        
        print("\n📊 System Status:")
        print(f"   Initialized: {'✅' if status['initialized'] else '❌'}")
        print(f"   City: {status['city_name']}")
        print(f"   Context Sections: {status['context_sections_loaded']}")
        print(f"   Slang Dictionary Size: {status['slang_words_count']} words")
        print(f"   Food Areas Mapped: {status['food_areas_count']} areas")

def run_sample_queries():
    """Run sample queries to demonstrate the system"""
    print("\n🧪 Running Sample Queries...")
    print("=" * 50)
    
    guide = LocalGuideSystem()
    
    sample_queries = [
        "Bhai, scene kya hai for dinner tonight?",
        "What does cutting mean?",
        "How long to reach Juhu by auto from CST?",
        "Is it okay to wear shorts in Mumbai?",
        "Where can I get good vada pav in the morning?",
        "What's the best time to travel by local train?",
        "Kya scene hai with street food hygiene?",
        "Should I carry cash or cards?",
        "What happens during Ganesh Chaturthi?",
        "How much does bhel puri cost?"
    ]
    
    for i, query in enumerate(sample_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        print("-" * 30)
        
        response = guide.process_query(query)
        print(f"Response: {response.response_text}")
        
        confidence_level = response.confidence_score.level.value if hasattr(response.confidence_score.level, 'value') else str(response.confidence_score.level)
        print(f"Confidence: {confidence_level} ({response.confidence_score.overall_score:.2f})")
        
        if response.slang_translation and response.slang_translation.slang_words_found:
            print(f"Slang Found: {[word for word, _ in response.slang_translation.slang_words_found]}")

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            run_sample_queries()
            return
        elif sys.argv[1] == "help":
            print("🌍 The Local Guide System")
            print("Usage:")
            print("  python main.py          - Interactive mode")
            print("  python main.py test     - Run sample queries")
            print("  python main.py help     - Show this help")
            return
    
    # Run interactive mode
    app = LocalGuideApp()
    app.run_interactive_mode()

if __name__ == "__main__":
    main()