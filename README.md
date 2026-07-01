# SHL Assessment Recommender Chatbot

A conversational AI-powered chatbot that helps hiring managers find the perfect SHL assessments through natural dialogue. Built with FastAPI, LLM integration, and comprehensive evaluation metrics.

## Overview

Hiring managers and recruiters struggle to find the right assessment from 377+ SHL tests without knowing exact keywords. This chatbot solves that problem by understanding hiring needs through conversation, asking clarifying questions, and recommending real SHL assessments with direct links.

## Features

- Conversational Interface: Natural dialogue-based assessment discovery
- LLM-Powered: Uses OpenRouter API with Anthropic Claude for intelligent understanding
- Clarifying Questions: Asks about role, seniority level, and required skills when input is vague
- Real Recommendations: Returns 1-10 actual SHL tests with verified URLs from the 377-test catalog
- Dynamic Refinement: Updates recommendations when user constraints change mid-conversation
- Assessment Comparison: Compares tests using catalog evidence and metadata
- Zero Hallucination: Every URL and test name verified from the actual SHL catalog
- Evaluation Metrics: Includes Recall@10, groundedness, schema compliance, and behavioral testing
- Stateless API: Full conversation history sent with each request for reliability

## Architecture

The solution consists of three main components:

1. FastAPI Backend (api.py)
   - Exposes GET /health and POST /chat endpoints
   - Handles stateless conversation management
   - Returns structured JSON responses

2. Bot Logic (bot_logic.py)
   - OpenRouter LLM integration for intelligent conversation
   - Fallback to keyword matching for reliability
   - Loads 377 SHL tests into memory at startup
   - Decides when to ask questions vs recommend vs refuse

3. Streamlit UI (app_streamlit.py)
   - Optional local chat interface for testing
   - Styled with SHL brand colors (dark green, medium green, light green)
   - Shows conversation history with formatted recommendations
   - Clickable links to view assessments

## Technical Stack

- Backend: FastAPI, Uvicorn
- LLM: OpenRouter API (Anthropic Claude)
- Frontend: Streamlit (optional)
- Deployment: Render
- Version Control: GitHub
- Language: Python 3.12

## Installation

1. Clone the repository
```bash
git clone https://github.com/srivathsav07/SHL-bot.git
cd shl_bot
```

2. Install dependencies
```bash
pip install --user -r requirements.txt
```

3. Set environment variable
```bash
set OPENROUTER_API_KEY=your-api-key-here
```

## Running Locally

Terminal 1: Start FastAPI backend
```bash
python api.py
```

Expected output:INFO:     Uvicorn running on http://0.0.0.0:8000
                INFO:     Application startup complete.


Terminal 2 (Optional): Start Streamlit UI
```bash
python -m streamlit run app_streamlit.py
```

## Testing

### Test /health endpoint
```bash
curl http://localhost:8000/health
```

Response:
```json
{"status":"ok"}
```

### Test /chat endpoint
Open http://localhost:8000/docs for interactive Swagger UI

Example request:
```json
{
  "messages": [
    {
      "role": "user",
      "content": "I need an assessment for Java developers"
    }
  ]
}
```

### Run evaluation tests
```bash
python evaluation.py
```

This runs 4 conversation traces and measures:
- Schema Compliance: 100% (all responses match required JSON format)
- Recall@10: ~80% (recommended tests match expected tests)
- Groundedness: 100% (all URLs verified from catalog)
- Behavioral: Vague queries, tech keywords, refinements all handled correctly

## Evaluation Methods

The solution includes comprehensive evaluation in evaluation.py:

1. Schema Compliance (Must-Pass)
   - Validates every response matches required JSON format
   - Checks: reply (string), recommendations (array), end_of_conversation (boolean)

2. Recall@10 (Recommendation Relevance)
   - Measures fraction of expected tests appearing in top 10 recommendations
   - Formula: Recall@K = (# relevant tests in top K) / (total relevant tests)
   - Tests against 4 conversation traces covering Java, Python, vague queries, and management

3. Groundedness (Hallucination Prevention)
   - Ensures all recommended URLs actually exist in SHL catalog
   - Measures: % of recommended URLs that are verified catalog URLs
   - Target: 100% (zero hallucinated tests)

4. Behavioral Probes
   - Vague queries receive clarifying questions
   - Tech keywords trigger immediate recommendations
   - Off-topic requests are refused
   - Mid-conversation changes update recommendations

## Bot Behavior

The bot follows this decision logic:

1. Tech keyword detected (java, python, c#, etc.) -> Recommend tests immediately
2. First turn + vague input (no keyword specified) -> Ask clarifying questions
3. User says done/perfect/thanks -> End conversation
4. Default -> Ask for more details (skills, language, etc.)

## API Specification

### POST /chat

Request body:
```json
{
  "messages": [
    {
      "role": "user",
      "content": "I need an assessment for Java developers"
    },
    {
      "role": "assistant",
      "content": "Great! I found 10 assessments..."
    }
  ]
}
```

Response format:
```json
{
  "reply": "Conversational response",
  "recommendations": [
    {
      "name": "Test Name",
      "url": "https://www.shl.com/...",
      "test_type": "Category"
    }
  ],
  "end_of_conversation": false
}
```

## Deployment

The API is deployed on Render at:https://shl-bot.onrender.com

Endpoints:
- Health check: GET https://shl-bot.onrender.com/health
- Chat: POST https://shl-bot.onrender.com/chat
- Swagger UI: https://shl-bot.onrender.com/docs

Note: Free Render tier has cold-start delay of 50 seconds to 2 minutes after 15 minutes of inactivity.

## Challenges and Solutions

Challenge: Infinite loop on first message
- Cause: st.rerun() caused Streamlit to re-execute script
- Solution: Removed st.rerun() and let Streamlit handle refresh naturally
- Result: Single response per user input, no loops

Challenge: Bot asked questions despite tech keyword specified
- Cause: Logic only checked message length, ignored content
- Solution: Added keyword detection before checking vagueness
- Result: Bot recommends immediately for tech-specified requests

Challenge: JSON encoding error loading catalog
- Cause: Default encoding couldn't handle special characters
- Solution: Explicitly used UTF-8 encoding when loading catalog
- Result: All 377 tests load successfully

Challenge: LLM responses not in valid JSON format
- Cause: Some models don't follow JSON instructions consistently
- Solution: Added fallback to keyword matching if LLM returns invalid JSON
- Result: Bot always returns valid JSON response

## Design Choices

1. OpenRouter LLM Integration
   - Chose OpenRouter for free tier availability and Claude access
   - Implemented fallback to keyword matching for reliability
   - Lower temperature (0.3) for consistent JSON output

2. In-Memory Catalog
   - 377 tests fit in memory (approx 5MB)
   - No external database needed for this scale
   - Fast filtering with Python list comprehensions

3. Stateless API Design
   - Every request includes full conversation history
   - No per-conversation state stored on server
   - Enables easy scaling and deployment

4. Keyword Matching Fallback
   - If LLM fails or returns invalid JSON, fallback to simple keyword detection
   - Ensures bot always responds, never crashes
   - Detects: java, python, javascript, c#, c++, ruby, php, go, rust, .net

## AI Tools Used

Claude (Anthropic) was used to help implement this solution:

- Code Writing (60%): FastAPI backend, bot logic, LLM integration, evaluation framework
- Debugging (20%): Infinite loop fix, JSON parsing errors, encoding issues
- Architecture Design (15%): System design, retrieval strategy, fallback pattern
- Documentation (5%): Approach document, code comments

All code was reviewed, tested locally, and modified for understanding. The implementation reflects actual functionality rather than copy-paste code.

## Approach Document

For detailed information on design choices, retrieval setup, prompt design, evaluation methods, and challenges overcome, see APPROACH.pdf in the repository.

## Requirements

- Python 3.10+
- FastAPI 0.104.1
- Uvicorn 0.24.0
- Streamlit 1.28.0
- Requests 2.31.0
- OpenRouter API key (free tier available)

## License

This project was built as part of the SHL AI Intern assessment.

## Contact

GitHub: https://github.com/srivathsav07/SHL-bot
Live API: https://shl-bot.onrender.com