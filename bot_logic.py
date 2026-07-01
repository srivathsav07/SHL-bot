import json

# Load catalog once (at the top, so it's fast)
def load_catalog():
    """Read all SHL tests from the catalog file"""
    with open('data/shl_tests.json', 'r', encoding='utf-8') as f:
        return json.load(f)

CATALOG = load_catalog()

def get_bot_response(messages):
    """
    This function is the BRAIN of the bot.
    
    Input: List of all messages so far
    Output: What the bot should say + which tests to recommend
    """
    
    # Get the most recent user message
    last_user_message = messages[-1]["content"] if messages else ""
    
    # Count how many times the user has spoken (to know which turn we're on)
    user_turn_count = len([m for m in messages if m["role"] == "user"])
    
    print(f"[DEBUG] Turn {user_turn_count}, User said: {last_user_message}")
    
    # ===== DECISION LOGIC =====
    
    # Check if user mentioned a specific technology or role
    tech_keywords = ["java", "python", "javascript", "c#", "c++", "ruby", "php", "go", "rust", ".net"]
    mentioned_tech = [tech for tech in tech_keywords if tech in last_user_message.lower()]
    
    # If user mentioned a specific tech, recommend immediately
    if mentioned_tech:
        tech = mentioned_tech[0]
        # Filter catalog for tech-related tests
        tech_tests = [t for t in CATALOG if tech in t.get("name", "").lower()]
        
        reply_text = (
            f"Great! I found {len(tech_tests)} assessments related to {tech.upper()}. "
            f"Here are my top picks:"
        )
        
        # Build recommendations (max 10)
        recommendations = []
        for test in tech_tests[:10]:
            recommendations.append({
                "name": test.get("name", "Unknown"),
                "url": test.get("link", "#"),
                "test_type": test.get("keys", ["K"])[0] if test.get("keys") else "K"
            })
        
        end_conversation = False
    
    # If it's the first turn and message is vague (no tech, no role mentioned)
    elif user_turn_count == 1 and len(last_user_message) < 50:
        reply_text = (
            "Hi! I'd love to help you find the right assessment. To get started, could you tell me:\n\n"
            "1. **What role** are you hiring for? (e.g., Java Developer, Python Engineer, Manager)\n"
            "2. **What's the seniority level?** (e.g., Junior, Mid, Senior)\n\n"
            "Once I know this, I can recommend the perfect tests!"
        )
        recommendations = []
        end_conversation = False
    
    # If user says they're done
    elif any(word in last_user_message.lower() for word in ["done", "perfect", "thanks", "that's it", "goodbye"]):
        reply_text = "Excellent! You're all set with your recommendations. Good luck with your hiring!"
        recommendations = []
        end_conversation = True
    
    # Default: ask more questions
    else:
        reply_text = (
            "Thanks for that info! To narrow down further, could you tell me:\n\n"
            "- **What skills** matter most? (e.g., problem-solving, communication, technical)\n"
            "- **What language** should the test be in?\n\n"
            "This will help me give you more precise recommendations."
        )
        recommendations = []
        end_conversation = False
    
    # Return everything in the format your API expects
    return {
        "reply": reply_text,
        "recommendations": recommendations,
        "end_of_conversation": end_conversation
    }