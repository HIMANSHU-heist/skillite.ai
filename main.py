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

# Conversation memory
sessions = {}


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_message = data.get("message")
    session_id = data.get("session_id", "default")

    if session_id not in sessions:
        sessions[session_id] = {
            "stage": "profiling",
            "answers": []
        }

    session = sessions[session_id]

    # STAGE 1: PROFILING MODE
    if session["stage"] == "profiling":

        session["answers"].append(user_message)

        # After 4-5 answers, move to confirmation
        if len(session["answers"]) >= 4:
            session["stage"] = "confirm"

            return JSONResponse({
                "reply": "मेरे पास अब आपकी पर्याप्त जानकारी है। क्या मैं अब आपका पर्सनल AI करियर रोडमैप तैयार करूं? (हाँ / नहीं)"
            })

        # Ask next intelligent question dynamically
        prompt = f"""
आप एक प्रोफेशनल करियर मेंटर हैं।

अब तक छात्र ने यह जानकारी दी है:
{session["answers"]}

अब अगला सबसे ज़रूरी सवाल हिंदी में पूछिए।
एक बार में सिर्फ एक सवाल।
रोडमैप अभी मत दीजिए।
"""

    # STAGE 2: CONFIRMATION MODE
    elif session["stage"] == "confirm":

        if "हाँ" in user_message or "haan" in user_message.lower():
            session["stage"] = "roadmap"

            combined_answers = "\n".join(session["answers"])

            prompt = f"""
आप एक प्रोफेशनल AI करियर स्ट्रैटेजिस्ट हैं।

छात्र की जानकारी:
{combined_answers}

अब एक पूरा डिटेल्ड पर्सनल रोडमैप हिंदी में तैयार करें।

रोडमैप में शामिल करें:

1. स्किल गैप एनालिसिस
2. 6 महीने का स्टेप-बाय-स्टेप प्लान
3. 3 प्रोजेक्ट आइडिया
4. कोर्स सुझाव
5. भारत में जॉब अवसर
6. सैलरी रेंज

साफ, स्ट्रक्चर्ड और प्रोफेशनल तरीके से लिखें।
"""
        else:
            session["stage"] = "profiling"

            return JSONResponse({
                "reply": "ठीक है, मैं आपसे कुछ और सवाल पूछता हूँ ताकि बेहतर रोडमैप बना सकूँ।"
            })

    # STAGE 3: NORMAL CHAT AFTER ROADMAP
    else:
        prompt = f"""
आप एक AI करियर मेंटर हैं।

छात्र ने रोडमैप के बाद यह पूछा:
{user_message}

उसे स्पष्ट और प्रोफेशनल हिंदी में जवाब दें।
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
    ai_reply = result["choices"][0]["message"]["content"]

    return JSONResponse({"reply": ai_reply})
