# The Local Guide System

An advanced AI prototype that deeply understands local culture, language, habits, food, transportation, and daily life of a specific city through a custom context file.

## Core Principle
This system operates under a strict constraint: it ONLY learns about the city from `product.md` and has NO prior global knowledge.

## Architecture Overview
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   product.md    │───▶│  Context Loader  │───▶│ Structured Data │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
┌─────────────────┐    ┌──────────────────┐             │
│ User Query      │───▶│ Local Reasoning  │◀────────────┘
└─────────────────┘    │     Engine       │
                       └──────────────────┘
                                │
                       ┌──────────────────┐
                       │ Response with    │
                       │ Confidence Score │
                       └──────────────────┘
```

## Features
- Local Slang Translator
- Smart Street Food Guide
- Traffic & Commute Estimator
- Cultural Etiquette Advisor
- Event & Festival Awareness

## Getting Started
1. Create your city's `product.md` file
2. Run the system
3. Ask local questions and get native-level responses