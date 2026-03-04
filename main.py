from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "llama-3.1-8b-instant"

# Store conversation state (basic memory)
user_sessions = {}


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_message = data.get("message")
    session_id = data.get("session_id", "default")

    # Initialize session if not exists
    if session_id not in user_sessions:
        user_sessions[session_id] = {
            "stage": "ask_details",
            "answers": []
        }

    session = user_sessions[session_id]

    # Stage 1: Ask Details First
    if session["stage"] == "ask_details":
        session["answers"].append(user_message)

        if len(session["answers"]) < 1:
            reply = """
Hi 👋 Before I create your personalized roadmap, answer these:

1. What is your current field or education?
2. What is your career goal?
3. What skills do you already have?
4. How many hours per day can you study?
5. Do you prefer free or paid courses?

Reply in one message with all answers.
"""
            return JSONResponse({"reply": reply})

        else:
            session["stage"] = "generate_plan"

    # Stage 2: Generate Plan Based on Answers
    if session["stage"] == "generate_plan":

        combined_answers = "\n".join(session["answers"])

        prompt = f"""
You are an expert AI Career Mentor for Indian students.

Student Details:
{combined_answers}

Now create a COMPLETE personalized career roadmap.

Response must include:

1. 🔎 Skill Gap Analysis
2. 🛣 Step-by-Step Learning Roadmap (Beginner → Advanced)
3. 🎓 Best Udemy Courses (with exact course names)
4. 🎓 Best Coursera Courses (with exact course names)
5. 📺 3 YouTube search suggestions
6. 💡 3 Practical Project Ideas
7. 📅 3 Month Action Plan
8. 💰 Expected Career Opportunities in India

Keep response clean, structured and powerful.
"""

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL_NAME,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7
            }
        )

        result = response.json()

        if "choices" not in result:
            return JSONResponse({"reply": "⚠ API Error. Check GROQ API key."})

        ai_reply = result["choices"][0]["message"]["content"]

        # Reset session after plan generation
        user_sessions.pop(session_id)

        return JSONResponse({"reply": ai_reply})