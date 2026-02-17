🤖 AI Cold Call Simulation Agent

An AI-powered B2B cold call simulator that behaves like a real human sales representative using Groq LLaMA 3.1-8B.

It qualifies prospects, detects business relevance, and produces a structured outcome — all within 40-60 seconds, just like real cold calls.

🎯 Overview

This project simulates real-world cold calls to:

✅ Sound human (not scripted)
✅ Qualify decision makers
✅ Detect business relevance
✅ End unsuitable calls quickly
✅ Keep calls short and realistic
✅ Produce structured qualification outcome

🏗️ Architecture Overview
Frontend (React + Vite)
        │
        │ REST API
        ▼
FastAPI Backend (server.py)
        │
        ▼
LearningAgent (bot.py)
        │
        ▼
Groq LLM API (LLaMA 3.1-8B)

🔄 Call Flow

1️⃣ User clicks Start Call

2️⃣ Backend creates LearningAgent

3️⃣ Agent asks opening question

4️⃣ User replies via /next

5️⃣ Agent:

Applies ⚡ Fast rule checks

Uses 🧠 LLM for reasoning

Maintains 🧾 short memory

6️⃣ Agent either:

✔ Continues conversation
❌ Ends call
📊 Returns qualification summary

🧩 Component Breakdown
🎨 Frontend (React + Vite)

• Chat-style UI
• Calls /start and /next
• Displays replies and final results

⚙️ FastAPI Backend

• Handles HTTP endpoints
• Maintains active agent instance
• Returns structured JSON

🧠 LearningAgent (Core Brain)

Handles:

• Conversation state
• Regex-based early exits
• LLM reasoning
• Call timing logic
• Final structured summary

🚀 Groq LLM

Model: llama-3.1-8b-instant

Used for:

• Natural human conversation
• Business reasoning
• Qualification decisions
• Polite call termination

💡 Key Design Decisions
⚡ Hybrid Logic (Rules + LLM)

Why not pure LLM?

❌ Expensive
❌ Unpredictable

Solution:

✔ Regex → Fast exits
✔ LLM → Human reasoning

Benefits:

• Faster
• Cheaper
• Stable

🧾 Short Conversation Memory

Only last 5-6 turns sent to LLM

Why:

• Lower cost
• Faster response
• Clean context

📦 Strict JSON Output

LLM forced to return:

{
"action": "continue | end",
"reply": "text"
}


Why:

• Prevent crashes
• Stable backend
• No hallucinated formats

🛡️ Safe Fallback Protection

If LLM fails:

✔ System DOES NOT crash
✔ Safe default reply provided

Production-ready safety.

⏱️ Call Duration Control

Cold calls must be short.

System exits if:

• Not owner
• Not interested
• Non-IT business
• Busy

🧠 Stateful Agent (Stateless API)

API → Stateless
Agent → Stateful (in memory)

Simple & efficient for simulation.

⚖️ Tradeoffs
🧠 In-Memory Agent

❌ Lost if server restarts

✔ Simpler
✔ Faster

Production → Redis recommended

⚡ Regex Early Signals

❌ Not perfect

✔ Very fast
✔ Efficient

LLM handles complex reasoning.

💰 LLM Cost Optimization

LLM used only when needed.

Not every message → LLM call.

✂ Short Responses

Default: Max 3 sentences

Realistic cold-call behavior.

🔓 No Authentication

Open API for demo.

Production → Add Auth Layer

🧠 Qualification Logic Summary

Agent exits if:

❌ Not owner
❌ Not interested
❌ Non-IT business

Agent continues if:

✔ IT / Cloud business
✔ Decision maker
✔ Shows interest

Final output:

📊 Structured qualification result

🚀 How To Run
Backend Setup
py -3.11 -m venv .venv

.venv\Scripts\activate

pip install -r requirements.txt

python -m uvicorn server:app --reload

Frontend Setup
cd frontend

npm install

npm run dev

🧰 Tech Stack
Backend

🐍 Python 3.11
⚡ FastAPI
🚀 Groq API
🧠 LLaMA 3.1

Frontend

⚛ React
⚡ Vite
🌐 Axios

LLM

🧠 llama-3.1-8b-instant
⚡ Ultra-fast inference

🔮 Future Improvements

🚀 Redis session storage

📊 Call analytics dashboard

📞 Voice integration (Twilio)

📅 Callback scheduling

📈 Qualification scoring

💰 Cost tracking

👥 Multi-call simulation

🎥 Demo Purpose

This project demonstrates:

✔ AI agent design
✔ Production-safe LLM usage
✔ Hybrid AI architecture
✔ Real-world sales simulation

👨‍💻 Author

Ashhar Raza

Full Stack Developer | AI | Backend | Cloud

⭐ If you like this project

Give it a ⭐ on GitHub