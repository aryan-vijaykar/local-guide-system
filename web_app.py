#!/usr/bin/env python3
"""
Web Interface for The Local Guide System
Interactive UI/UX with real-time chat interface
"""

from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import json
import uuid

from src.local_guide_system import LocalGuideSystem

app = Flask(__name__)
app.secret_key = 'local_guide_secret_key_2024'

# Initialize the Local Guide System
guide_system = LocalGuideSystem()

@app.route('/')
def index():
    """Main chat interface"""
    # Initialize session if new user
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        session['chat_history'] = []
    
    # Get system status
    status = guide_system.get_system_status()
    
    return render_template('index.html', 
                         city_name=status.get('city_name', 'Unknown'),
                         slang_count=status.get('slang_words_count', 0),
                         areas_count=status.get('food_areas_count', 0))

@app.route('/chat', methods=['POST'])
def chat():
    """Process chat messages"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        # Process the query
        current_time = datetime.now()
        response = guide_system.process_query(user_message, current_time)
        
        # Format response for web interface
        chat_response = {
            'response': response.response_text,
            'confidence': {
                'score': round(response.confidence_score.overall_score, 2),
                'level': response.confidence_score.level.value if hasattr(response.confidence_score.level, 'value') else str(response.confidence_score.level),
                'emoji': get_confidence_emoji(response.confidence_score.overall_score)
            },
            'slang_translation': None,
            'recommendations': [],
            'cultural_context': response.cultural_context,
            'sources': response.sources_used or [],
            'timestamp': current_time.strftime('%H:%M')
        }
        
        # Add slang translation if available
        if response.slang_translation and response.slang_translation.slang_words_found:
            chat_response['slang_translation'] = {
                'words': [{'slang': word, 'meaning': meaning} 
                         for word, meaning in response.slang_translation.slang_words_found],
                'cultural_context': response.slang_translation.cultural_context
            }
        
        # Add recommendations if available
        if response.recommendations:
            chat_response['recommendations'] = [
                {
                    'title': rec.title,
                    'description': rec.description,
                    'timing': rec.timing_advice,
                    'budget': rec.budget_info,
                    'crowd': rec.crowd_level
                }
                for rec in response.recommendations[:3]  # Limit to 3 recommendations
            ]
        
        # Store in session history
        if 'chat_history' not in session:
            session['chat_history'] = []
        
        session['chat_history'].append({
            'user': user_message,
            'bot': chat_response,
            'timestamp': current_time.isoformat()
        })
        
        # Keep only last 20 messages
        session['chat_history'] = session['chat_history'][-20:]
        session.modified = True
        
        return jsonify(chat_response)
        
    except Exception as e:
        return jsonify({'error': f'System error: {str(e)}'}), 500

@app.route('/translate', methods=['POST'])
def translate():
    """Translate slang text"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        direction = data.get('direction', 'to_standard')  # to_standard or to_local
        
        if not text:
            return jsonify({'error': 'Empty text'}), 400
        
        translation = guide_system.translate_slang(text, direction)
        
        return jsonify({
            'original': translation.original_text,
            'translated': translation.translated_text,
            'slang_words': [{'slang': word, 'meaning': meaning} 
                           for word, meaning in translation.slang_words_found],
            'confidence': round(translation.confidence, 2),
            'cultural_context': translation.cultural_context
        })
        
    except Exception as e:
        return jsonify({'error': f'Translation error: {str(e)}'}), 500

@app.route('/recommendations/<rec_type>')
def get_recommendations(rec_type):
    """Get specific type of recommendations"""
    try:
        # Get query parameters
        location = request.args.get('location')
        budget = request.args.get('budget')
        weather = request.args.get('weather')
        
        recommendations = guide_system.get_recommendations(
            rec_type,
            location=location,
            budget_level=budget,
            weather_condition=weather,
            current_time=datetime.now()
        )
        
        return jsonify([
            {
                'title': rec.title,
                'description': rec.description,
                'reasoning': rec.reasoning,
                'confidence': round(rec.confidence, 2),
                'timing': rec.timing_advice,
                'budget': rec.budget_info,
                'crowd': rec.crowd_level,
                'weather': rec.weather_consideration
            }
            for rec in recommendations
        ])
        
    except Exception as e:
        return jsonify({'error': f'Recommendation error: {str(e)}'}), 500

@app.route('/status')
def system_status():
    """Get system status"""
    status = guide_system.get_system_status()
    return jsonify(status)

@app.route('/debug', methods=['POST'])
def debug_query():
    """Debug query processing"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Empty query'}), 400
        
        debug_info = guide_system.debug_query_processing(query)
        return jsonify(debug_info)
        
    except Exception as e:
        return jsonify({'error': f'Debug error: {str(e)}'}), 500

@app.route('/history')
def chat_history():
    """Get chat history"""
    return jsonify(session.get('chat_history', []))

@app.route('/clear_history', methods=['POST'])
def clear_history():
    """Clear chat history"""
    session['chat_history'] = []
    session.modified = True
    return jsonify({'success': True})

def get_confidence_emoji(score):
    """Get emoji for confidence score"""
    if score >= 0.8:
        return "🟢"
    elif score >= 0.6:
        return "🟢"
    elif score >= 0.4:
        return "🟡"
    elif score >= 0.2:
        return "🟠"
    else:
        return "🔴"

if __name__ == '__main__':
    print("🌍 Starting The Local Guide System Web Interface...")
    print("🚀 Open http://localhost:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)