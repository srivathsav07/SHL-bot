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
    
    # Get API key
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        api_key = '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'
    
    # Build catalog summary (first 20 tests)
    catalog_summary = json.dumps(CATALOG[:20], indent=2)
    
    system_prompt = f"""You are an SHL Assessment Recommender bot.

CATALOG (20 sample tests):
{catalog_summary}

TASK:
1. Understand user's hiring need
2. If vague, ask clarifying questions
3. Recommend 1-10 real tests from catalog
4. Return ONLY valid JSON (no markdown, no extra text)

RESPONSE FORMAT (MUST be valid JSON only):
{{"reply": "Your response", "recommendations": [{{"name": "test name", "url": "https://...", "test_type": "type"}}], "end_of_conversation": false}}

Rules:
- ONLY return JSON
- recommendations array: empty if gathering info, 1-10 if recommending
- All URLs must be from catalog above
- end_of_conversation: true only when user satisfied
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
                "temperature": 0.3  # Lower temp for more consistent JSON
            },
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"OpenRouter error: {response.status_code} - {response.text}")
            return {
                "reply": "I'm having trouble connecting. Please try again.",
                "recommendations": [],
                "end_of_conversation": False
            }
        
        result = response.json()
        bot_text = result["choices"][0]["message"]["content"].strip()
        
        # Try to parse JSON response
        try:
            parsed = json.loads(bot_text)
            return parsed
        except json.JSONDecodeError:
            print(f"Failed to parse JSON: {bot_text}")
            # Fallback to keyword matching
            return fallback_recommendation(messages)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return fallback_recommendation(messages)


def fallback_recommendation(messages):
    """Fallback to keyword matching if LLM fails"""
    last_user_message = messages[-1]["content"] if messages else ""
    user_turn_count = len([m for m in messages if m["role"] == "user"])
    
    tech_keywords = ["java", "python", "javascript", "c#", "c++", "ruby", "php", "go", "rust", ".net"]
    mentioned_tech = [tech for tech in tech_keywords if tech in last_user_message.lower()]
    
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
    
    elif user_turn_count == 1:
        return {
            "reply": "Hi! I'd love to help. Could you tell me: 1. What role are you hiring for? 2. What's the seniority level?",
            "recommendations": [],
            "end_of_conversation": False
        }
    
    else:
        return {
            "reply": "Thanks for that info! Could you tell me what skills matter most?",
            "recommendations": [],
            "end_of_conversation": False
        }


if __name__ == "__main__":
    test_messages = [
        {"role": "user", "content": "I need an assessment for Java developers"}
    ]
    
    result = get_bot_response(test_messages)
    print("\n[BOT RESPONSE]")
    print(json.dumps(result, indent=2))