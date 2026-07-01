import json
import os
import requests

CATALOG = None

def load_catalog():
    """Read all SHL tests from the catalog file"""
    global CATALOG
    with open('data/shl_tests.json', 'r', encoding='utf-8') as f:
        CATALOG = json.load(f)
    return CATALOG

CATALOG = load_catalog()

def get_bot_response(messages):
    """Use OpenRouter to recommend SHL assessments"""
    
    # Get API key from environment variable (safe, not hardcoded)
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("WARNING: OPENROUTER_API_KEY not set, using fallback")
        return fallback_recommendation(messages)
    
    # Build catalog summary (first 30 tests for context)
    catalog_summary = json.dumps(CATALOG[:30], indent=2)
    
    system_prompt = f"""You are an SHL Assessment Recommender bot helping hiring managers find the perfect assessment.

CATALOG (30 sample tests from 377 total):
{catalog_summary}

YOUR TASK:
1. Understand the user's hiring need (role, seniority, skills)
2. If the request is vague, ask clarifying questions
3. Once you understand, recommend 1-10 real tests from the catalog
4. Return ONLY valid JSON (no markdown, no extra text, no explanations)

RESPONSE FORMAT (MUST be valid JSON only):
{{"reply": "Your conversational response", "recommendations": [{{"name": "Test Name", "url": "https://www.shl.com/...", "test_type": "Category"}}], "end_of_conversation": false}}

RULES:
- Return ONLY JSON (no markdown, no code blocks, no extra text)
- recommendations array: empty [] if still gathering info, 1-10 items if recommending
- All test names and URLs must come from the catalog above
- end_of_conversation: true only when user is satisfied with recommendations
- Never make up test names or URLs
- Keep replies conversational and helpful
"""
    
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://shl-bot.onrender.com",
                "X-Title": "SHL Assessment Bot"
            },
            json={
                "model": "openrouter/auto",
                "messages": messages,
                "system": system_prompt,
                "max_tokens": 1000,
                "temperature": 0.3  # Lower temperature for consistent JSON output
            },
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"OpenRouter error: {response.status_code} - {response.text}")
            return fallback_recommendation(messages)
        
        result = response.json()
        bot_text = result["choices"][0]["message"]["content"].strip()
        
        # Try to parse JSON response
        try:
            parsed = json.loads(bot_text)
            return parsed
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON from LLM: {str(e)}")
            print(f"LLM response was: {bot_text[:200]}")
            # Fallback to keyword matching if LLM returns invalid JSON
            return fallback_recommendation(messages)
    
    except requests.exceptions.Timeout:
        print("Request timed out")
        return fallback_recommendation(messages)
    except Exception as e:
        print(f"Error calling OpenRouter: {str(e)}")
        return fallback_recommendation(messages)


def fallback_recommendation(messages):
    """Fallback to keyword matching if LLM fails or is unavailable"""
    
    last_user_message = messages[-1]["content"] if messages else ""
    user_turn_count = len([m for m in messages if m["role"] == "user"])
    
    print(f"[FALLBACK] Turn {user_turn_count}, User said: {last_user_message}")
    
    # Check if user mentioned a specific technology
    tech_keywords = ["java", "python", "javascript", "c#", "c++", "ruby", "php", "go", "rust", ".net"]
    mentioned_tech = [tech for tech in tech_keywords if tech in last_user_message.lower()]
    
    # If user mentioned a specific tech, recommend immediately
    if mentioned_tech:
        tech = mentioned_tech[0]
        tech_tests = [t for t in CATALOG if tech in t.get("name", "").lower()]
        
        recommendations = [
            {
                "name": test.get("name", "Unknown"),
                "url": test.get("link", "#"),
                "test_type": test.get("keys", ["K"])[0] if test.get("keys") else "K"
            }
            for test in tech_tests[:10]
        ]
        
        return {
            "reply": f"Great! I found {len(tech_tests)} assessments related to {tech.upper()}. Here are my top picks:",
            "recommendations": recommendations,
            "end_of_conversation": False
        }
    
    # If it's the first turn and message is vague
    elif user_turn_count == 1 and len(last_user_message) < 50:
        return {
            "reply": "Hi! I'd love to help you find the right assessment. To get started, could you tell me:\n\n1. **What role** are you hiring for? (e.g., Java Developer, Python Engineer, Manager)\n2. **What's the seniority level?** (e.g., Junior, Mid, Senior)\n\nOnce I know this, I can recommend the perfect tests!",
            "recommendations": [],
            "end_of_conversation": False
        }
    
    # If user says they're done
    elif any(word in last_user_message.lower() for word in ["done", "perfect", "thanks", "that's it", "goodbye"]):
        return {
            "reply": "Excellent! You're all set with your recommendations. Good luck with your hiring!",
            "recommendations": [],
            "end_of_conversation": True
        }
    
    # Default: ask more questions
    else:
        return {
            "reply": "Thanks for that info! To narrow down further, could you tell me:\n\n- **What skills** matter most? (e.g., problem-solving, communication, technical)\n- **What language** should the test be in?\n\nThis will help me give you more precise recommendations.",
            "recommendations": [],
            "end_of_conversation": False
        }


# Test locally
if __name__ == "__main__":
    test_messages = [
        {"role": "user", "content": "I need an assessment for Java developers"}
    ]
    
    result = get_bot_response(test_messages)
    print("\n[BOT RESPONSE]")
    print(json.dumps(result, indent=2))