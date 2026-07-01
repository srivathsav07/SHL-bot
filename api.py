from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from bot_logic import get_bot_response

# Create the FastAPI app
app = FastAPI(title="SHL Assessment Bot")

# ===== DATA MODELS (shapes of data that come in/go out) =====

class Message(BaseModel):
    """One message in the conversation"""
    role: str  # "user" or "assistant"
    content: str  # The actual text

class ChatRequest(BaseModel):
    """What the user sends to /chat"""
    messages: List[Message]

class Recommendation(BaseModel):
    """One recommended test"""
    name: str
    url: str
    test_type: str

class ChatResponse(BaseModel):
    """What the bot sends back"""
    reply: str
    recommendations: List[Recommendation] = []
    end_of_conversation: bool = False

# ===== ENDPOINTS =====

@app.get("/health")
def health_check():
    """
    This endpoint is called to check if the bot is alive.
    The grader calls it before starting the conversation.
    """
    return {"status": "ok"}

@app.post("/chat")
def chat(request: ChatRequest):
    """
    This is where the magic happens.
    
    The grader sends:
    - Full conversation history
    
    You send back:
    - Bot reply
    - List of recommended tests (or empty if still asking)
    - Whether conversation is done
    """
    
    # Convert request to list of dicts (easier for bot_logic)
    messages = [
        {"role": m.role, "content": m.content}
        for m in request.messages
    ]
    
    # Get bot's response
    bot_response = get_bot_response(messages)
    
    # Convert recommendations to Recommendation objects
    recs = [
        Recommendation(
            name=r["name"],
            url=r["url"],
            test_type=r["test_type"]
        )
        for r in bot_response["recommendations"]
    ]
    
    # Return in the exact format the grader expects
    return ChatResponse(
        reply=bot_response["reply"],
        recommendations=recs,
        end_of_conversation=bot_response["end_of_conversation"]
    )


# This lets you run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)