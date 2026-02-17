# server.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bot import LearningAgent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = None

class UserInput(BaseModel):
    text: str

@app.post("/start")
def start():
    global agent
    agent = LearningAgent()
    return {"reply": agent.start_call(), "end": False}

@app.post("/next")
def next_turn(input: UserInput):
    reply, final = agent.handle_user(input.text)

    if final:
        return {"end": True, "final": final}

    return {"end": False, "reply": reply}
