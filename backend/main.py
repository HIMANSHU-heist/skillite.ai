# main.py
# Purpose: FastAPI server - Frontend ani AI madhla bridge

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  
from pydantic import BaseModel  # Data validation sathi
from ai_diagnostic import chat_with_ai, reset_conversation

# ─── FastAPI App Initialize ───────────────────────────────
app = FastAPI(
    title="SKILLITE-AI API",
    description="AI-powered skill diagnostic platform",
    version="1.0.0"
)

# ─── CORS Setup ───────────────────────────────────────────
# CORS = Browser security feature
# React (port 3000) FastAPI (port 8000) la call karto
# Browser blocked karto by default — he allow karto
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_methods=["*"],   # GET, POST, PUT, DELETE sab allow
    allow_headers=["*"],
)

# ─── Request/Response Models ──────────────────────────────
# Pydantic: Automatically validate karto ki correct data aala ka
class ChatRequest(BaseModel):
    message: str      # Required field
    session_id: str = "default"  # Optional, default value

class ChatResponse(BaseModel):
    response: str
    message_count: int

# ─── API Endpoints ────────────────────────────────────────

@app.get("/")
def home():
    """Health check — server running aahe ka verify karo"""
    return {"status": "SKILLITE-AI is running! 🚀"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Main diagnostic chat endpoint.
    Frontend yethun message pathvto, AI response milto.
    """
    # Validation: Empty message nako
    if not request.message.strip():
        raise HTTPException(
            status_code=400, 
            detail="Message cannot be empty"
        )
    
    # AI la message pathav ani response ghey
    ai_response = chat_with_ai(request.message)
    
    return ChatResponse(
        response=ai_response,
        message_count=len([])  # Phase 2 madhe improve karu
    )

@app.post("/reset")
def reset_chat():
    """New diagnostic session start karne sathi"""
    reset_conversation()
    return {"status": "Conversation reset successfully"}

# ─── Server Run ───────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)