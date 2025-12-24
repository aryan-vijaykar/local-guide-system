# The Local Guide System - Architecture Diagram

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           THE LOCAL GUIDE SYSTEM                            │
│                     (Context-Driven Local Intelligence)                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │ Interactive CLI │  │   Debug Mode    │  │     Sample Queries          │  │
│  │   main.py       │  │  (Step-by-step) │  │    (Demonstration)          │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        LOCAL GUIDE SYSTEM CORE                              │
│                         (local_guide_system.py)                             │
│                                                                             │
│  • Query Processing Orchestration                                          │
│  • Response Generation & Enhancement                                       │
│  • Component Integration                                                   │
│  • Confidence Assessment                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    ▼                   ▼                   ▼
┌─────────────────────────┐  ┌─────────────────────────┐  ┌─────────────────────────┐
│    CONTEXT LOADER       │  │  LOCAL REASONING ENGINE │  │   SLANG INTERPRETER     │
│  (context_loader.py)    │  │ (local_reasoning_engine │  │  (slang_interpreter.py) │
│                         │  │         .py)            │  │                         │
│ • Parse product.md      │  │                         │  │ • Local→Standard        │
│ • Structure data        │  │ • Intent Detection      │  │ • Standard→Local        │
│ • Category tagging      │  │ • Context-based Logic   │  │ • Mixed Language        │
│ • Search & retrieval    │  │ • Time-aware reasoning  │  │ • Cultural Context      │
│                         │  │ • Local pattern apply   │  │                         │
└─────────────────────────┘  └─────────────────────────┘  └─────────────────────────┘
            │                            │                            │
            ▼                            ▼                            ▼
┌─────────────────────────┐  ┌─────────────────────────┐  ┌─────────────────────────┐
│  RECOMMENDATION ENGINE  │  │   CONFIDENCE SCORER     │  │      DATA FLOW          │
│ (recommendation_engine  │  │  (confidence_scorer.py) │  │                         │
│        .py)             │  │                         │  │ Query → Analysis →      │
│                         │  │ • Multi-factor scoring  │  │ Context → Reasoning →   │
│ • Food recommendations  │  │ • Missing info detect   │  │ Response → Confidence   │
│ • Transport advice      │  │ • Clarification logic   │  │                         │
│ • Activity suggestions  │  │ • Quality assessment    │  │                         │
│ • Safety guidance       │  │                         │  │                         │
└─────────────────────────┘  └─────────────────────────┘  └─────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            PRODUCT.MD CONTEXT                               │
│                        (Single Source of Truth)                            │
│                                                                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐    │
│  │    Slang    │ │    Food     │ │  Transport  │ │      Culture        │    │
│  │ Dictionary  │ │   Timings   │ │   Patterns  │ │   Do's & Don'ts     │    │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────────────┘    │
│                                                                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐    │
│  │   Weather   │ │  Festivals  │ │   Pricing   │ │       Safety        │    │
│  │  Patterns   │ │   Impact    │ │ Expectations│ │      Guidelines     │    │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Architecture

```
USER QUERY
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    QUERY PREPROCESSING                          │
│                                                                 │
│  1. Slang Detection & Translation                              │
│  2. Intent Analysis (food/transport/culture/slang)            │
│  3. Time/Location Context Extraction                          │
│  4. Keyword Identification                                     │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│                   CONTEXT RETRIEVAL                            │
│                                                                 │
│  1. Search product.md for relevant sections                   │
│  2. Category-based filtering                                  │
│  3. Relevance scoring                                         │
│  4. Context item ranking                                      │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│                   LOCAL REASONING                              │
│                                                                 │
│  1. Apply local logic patterns                                │
│  2. Time-aware decision making                                │
│  3. Context-specific inference                                │
│  4. Cultural sensitivity check                                │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│                 RESPONSE GENERATION                            │
│                                                                 │
│  1. Generate base response                                     │
│  2. Add local personality                                     │
│  3. Include recommendations                                   │
│  4. Provide cultural context                                  │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│                 CONFIDENCE ASSESSMENT                          │
│                                                                 │
│  1. Multi-factor confidence scoring                           │
│  2. Missing information detection                             │
│  3. Clarification need assessment                             │
│  4. Quality validation                                        │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
ENHANCED LOCAL RESPONSE
```

## Component Interaction Matrix

| Component | Context Loader | Reasoning Engine | Slang Interpreter | Recommendation Engine | Confidence Scorer |
|-----------|---------------|------------------|-------------------|----------------------|-------------------|
| **Context Loader** | - | Provides context data | Provides slang dict | Provides structured data | N/A |
| **Reasoning Engine** | Uses context search | - | Uses for translation | Triggers recommendations | Provides reasoning result |
| **Slang Interpreter** | Uses slang data | Provides translations | - | N/A | N/A |
| **Recommendation Engine** | Uses context categories | Triggered by reasoning | N/A | - | N/A |
| **Confidence Scorer** | N/A | Scores reasoning quality | N/A | N/A | - |

## Key Design Principles

### 1. Context-First Architecture
- **Single Source of Truth**: All knowledge comes from product.md
- **No Global Knowledge**: System explicitly avoids internet/general knowledge
- **Structured Context**: Raw text converted to searchable, categorized data

### 2. Local Reasoning Logic
- **Time-Aware**: Decisions based on local timing patterns
- **Culture-Sensitive**: Respects local customs and etiquette
- **Pattern-Based**: Uses local logic patterns, not generic rules

### 3. Confidence-Driven Responses
- **Multi-Factor Scoring**: Context availability, relevance, completeness
- **Transparent Uncertainty**: Explicitly states when information is missing
- **Clarification Logic**: Asks specific questions when confidence is low

### 4. Modular Design
- **Separation of Concerns**: Each component has a specific responsibility
- **Loose Coupling**: Components interact through well-defined interfaces
- **Extensibility**: Easy to add new features or modify existing ones

## Technical Implementation Details

### Context Loading Strategy
```python
product.md → Markdown Parser → Section Extractor → 
Category Tagger → Structured Data → Search Index
```

### Query Processing Pipeline
```python
Raw Query → Slang Detection → Intent Analysis → 
Context Retrieval → Local Reasoning → Response Generation → 
Confidence Scoring → Enhanced Response
```

### Confidence Scoring Formula
```
Overall Confidence = 
  (Context Availability × 0.30) +
  (Query Specificity × 0.20) +
  (Context Relevance × 0.25) +
  (Information Completeness × 0.15) +
  (Response Quality × 0.10)
```

## Scalability Considerations

### Adding New Cities
1. Create new product.md for the city
2. Initialize LocalGuideSystem with new context file
3. All components automatically adapt to new local context

### Extending Functionality
1. Add new intent types in reasoning engine
2. Create new recommendation categories
3. Extend confidence scoring factors
4. Add new slang interpretation patterns

### Performance Optimization
1. Context caching for frequently accessed data
2. Lazy loading of context sections
3. Response caching for common queries
4. Batch processing for multiple queries