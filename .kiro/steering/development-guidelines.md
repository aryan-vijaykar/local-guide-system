---
inclusion: always
---

# Development Guidelines for The Local Guide System

## Code Standards

### Context-First Development
- All responses must cite sources from `product.md`
- Never use global knowledge or assumptions
- When information is missing, explicitly state "This information is not present in the local context file"

### Module Responsibilities
- **Context Loader**: Only parses and structures `product.md` data
- **Reasoning Engine**: Applies local logic patterns, never generic rules
- **Slang Interpreter**: Uses only slang dictionary from context
- **Recommendation Engine**: Time/location/budget aware using local data
- **Confidence Scorer**: Multi-factor assessment with transparency

### Error Handling
- Graceful degradation when context is missing
- Clear error messages referencing specific missing information
- Confidence scores should reflect data availability

### Testing Approach
- Test with Mumbai-specific queries
- Verify context-only responses
- Check confidence scoring accuracy
- Validate slang translation correctness

### Performance Guidelines
- Cache parsed context data
- Efficient context search algorithms
- Minimal response latency for web interface
- Memory-efficient data structures

## Local Logic Patterns
- Peak hours: 8-11 AM, 6-9 PM
- Evening food recommendations: 4-8 PM
- Monsoon considerations: Add 30-50% travel time
- Festival impacts: 2x normal travel time
- Cultural sensitivity: Religious area dress codes