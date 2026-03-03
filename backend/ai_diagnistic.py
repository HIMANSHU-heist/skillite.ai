# ai_diagnostic.py
# Purpose: Student chi AI-powered diagnostic interview ghene

import os
from groq import Groq  # Groq = Free OpenAI alternative
from dotenv import load_dotenv

load_dotenv()  # .env file madhe API key read karto

# ─── Groq client initialize ───────────────────────────────
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ─── System Prompt: AI la samajvto ki to kaay ahe ────────
SYSTEM_PROMPT = """
You are SKILLITE-AI, an intelligent skill diagnostic assistant.
Your job is to interview students and identify their:
1. Current knowledge level (Beginner/Intermediate/Advanced)
2. Skill gaps in their target domain
3. Learning style preferences

Rules:
- Ask ONE question at a time
- Be encouraging, not intimidating
- After 5 questions, provide a skill assessment summary
- Format final assessment as JSON with keys: 
  level, gaps, strengths, recommended_path
"""

# ─── Conversation History Store ──────────────────────────
# Logic: AI la previous messages yaad rahat nahit by default
# Mhanun aapan history list madhe save karto
conversation_history = []

def chat_with_ai(user_message: str) -> str:
    """
    Student chya message la AI response deto.
    
    Args:
        user_message: Student ne jo type kela
    
    Returns:
        AI cha response string
    """
    
    # Step 1: User message history madhe add karo
    conversation_history.append({
        "role": "user",
        "content": user_message
    })
    
    # Step 2: Groq API la call karo with full history
    # (Full history pathvato mhanun AI la context milto)
    response = client.chat.completions.create(
        model="llama3-8b-8192",   # Free Llama 3 model
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            *conversation_history   # * = list unpack karto
        ],
        temperature=0.7,  # 0 = robotic, 1 = creative
        max_tokens=500    # Response length limit
    )
    
    # Step 3: Response extract karo
    ai_message = response.choices[0].message.content
    
    # Step 4: AI response pan history madhe save karo
    conversation_history.append({
        "role": "assistant", 
        "content": ai_message
    })
    
    return ai_message

def reset_conversation():
    """New student sathi conversation clear karo"""
    conversation_history.clear()

# ─── Test: Direct script run kelyas ──────────────────────
if __name__ == "__main__":
    print("🎯 SKILLITE-AI Diagnostic Started!")
    print("Type 'quit' to exit, 'reset' for new session\n")
    
    # AI la pahili greeting pathav
    opening = chat_with_ai(
        "Hello, I want to assess my skills for a career in AI/Data Science"
    )
    print(f"AI: {opening}\n")
    
    # Simple terminal chatbot loop
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() == 'quit':
            break
        elif user_input.lower() == 'reset':
            reset_conversation()
            print("✅ Conversation reset!\n")
            continue
        elif not user_input:
            continue
            
        response = chat_with_ai(user_input)
        print(f"\nAI: {response}\n")