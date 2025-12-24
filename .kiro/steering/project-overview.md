---
inclusion: always
---

# The Local Guide System - Project Overview

## Core Principle
This system operates under a strict constraint: it ONLY learns about the city from `product.md` and has NO prior global knowledge.

## Architecture Components

### 1. Context Loader (`src/context_loader.py`)
- Parses `product.md` into structured data
- Tags information by categories (slang, food, transport, culture, etc.)
- Provides search and retrieval functionality

### 2. Local Reasoning Engine (`src/local_reasoning_engine.py`)
- Uses context-based inference, not global rules
- Applies local timing patterns (e.g., "after 7 PM roads are jammed")
- Time-aware decision making

### 3. Slang Interpreter (`src/slang_interpreter.py`)
- Translates local slang ↔ standard English
- Handles mixed language sentences
- Provides cultural context for slang usage

### 4. Recommendation Engine (`src/recommendation_engine.py`)
- Smart food recommendations based on time/location
- Transport advice considering peak hours
- Budget and weather-aware suggestions

### 5. Confidence Scorer (`src/confidence_scorer.py`)
- Multi-factor confidence assessment
- Detects missing information
- Triggers clarifying questions when confidence < threshold

## Key Features
- ✅ Local Slang Translation
- ✅ Smart Food Recommendations  
- ✅ Traffic & Transport Intelligence
- ✅ Cultural Sensitivity
- ✅ Confidence-Driven Responses
- ✅ Interactive Web Interface

## Usage Patterns
- CLI: `python main.py`
- Web: `python web_app.py`
- Demo: `python run_demo.py`
- Tests: `python tests/test_system.py`