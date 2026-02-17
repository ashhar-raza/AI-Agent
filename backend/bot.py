import os
import re
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class LearningAgent:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY missing in .env")

        self.client = Groq(api_key=api_key)
        self.model = "llama-3.1-8b-instant"

        self.history = []
        self.last_bot_message = ""
        self.call_active = True

        self.stage = "owner_check"
        self.turn_count = 0
        self.max_turns = 6   # ~40–60 sec cold call

    # ------------------------------------------------
    # QUICK SIGNALS
    # ------------------------------------------------
    def _is_repeat(self, t):
        return bool(re.search(r"\b(repeat|again|sorry|didn't hear)\b", t, re.I))

    def _not_interested(self, t):
        return bool(re.search(
            r"\b(not interested|no thanks|stop calling|don't call)\b",
            t, re.I))

    def _not_owner(self, t):
        return bool(re.search(
            r"\b(not the owner|employee|staff|assistant|receptionist|manager)\b",
            t, re.I))

    def _busy(self, t):
        return bool(re.search(
            r"\b(busy|call later|meeting|not now|later)\b",
            t, re.I))

    def _non_it_business(self, t):
        return bool(re.search(
            r"\b(grocery|kirana|plumber|electrician|salon|restaurant|bakery|shop)\b",
            t, re.I))

    def _owner_confirmation(self, t):
        return bool(re.search(r"\b(yes|speaking|i am|this is the owner)\b", t, re.I))

    # ------------------------------------------------
    # START CALL
    # ------------------------------------------------
    def start_call(self):
        msg = (
            "Hi, this is Ash calling briefly about cloud cost optimization. "
            "Am I speaking with the business owner?"
        )
        self.last_bot_message = msg
        return msg

    # ------------------------------------------------
    # SAFE LLM CALL
    # ------------------------------------------------
    def _llm_response(self, user_text, context):
        conversation = ""
        for h in self.history[-6:]:
            conversation += f"User: {h['user']}\nAgent: {h['assistant']}\n"

        prompt = f"""
You are a calm, professional B2B sales engineer on a short cold call.

Context stage: {context}

Rules:
- Speak naturally like a human.
- Keep replies under 3 sentences unless user asks for details.
- Do NOT sound scripted.
- If qualified, pitch briefly and clearly.
- If not relevant, end politely.
- If user asks questions, answer intelligently.
- Cold call should feel short and respectful.

Conversation:
{conversation}

User just said:
"{user_text}"

Respond in plain natural text only.
"""

        try:
            res = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=150,
            )

            return res.choices[0].message.content.strip()

        except Exception:
            return "Could you briefly tell me what your company does?"

    # ------------------------------------------------
    # MAIN LOGIC
    # ------------------------------------------------
    def handle_user(self, user_text):

        if not self.call_active:
            return None, "Call already ended."

        self.turn_count += 1

        if self.turn_count > self.max_turns:
            self.call_active = False
            return None, self._final(
                "Cold call exceeded time window",
                "Follow up later if needed"
            )

        t = user_text.strip()
        self.history.append({"user": t, "assistant": ""})

        # Repeat
        if self._is_repeat(t):
            return self.last_bot_message, None

        # Not interested
        if self._not_interested(t):
            self.call_active = False
            return None, self._final(
                "Prospect declined",
                "No follow-up required"
            )

        # Busy
        if self._busy(t):
            self.call_active = False
            return None, self._final(
                "Prospect was busy",
                "Call back at a better time"
            )

        # Not owner
        if self.stage == "owner_check" and self._not_owner(t):
            self.call_active = False
            return None, self._final(
                "Spoke to non-decision maker",
                "Reach business owner directly"
            )

        # Owner confirmed
        if self.stage == "owner_check" and self._owner_confirmation(t):
            self.stage = "qualification"
            reply = "Great, thanks. Could you briefly tell me what your organization does?"
            self.last_bot_message = reply
            self.history[-1]["assistant"] = reply
            return reply, None

        # Non-IT business
        if self._non_it_business(t):
            self.call_active = False
            return None, self._final(
                "Business not related to IT/cloud",
                "No opportunity for cloud services"
            )

        # Qualification stage
        if self.stage == "qualification":
            self.stage = "pitch"
            reply = self._llm_response(t, "qualification")
            self.last_bot_message = reply
            self.history[-1]["assistant"] = reply
            return reply, None

        # Pitch / Q&A stage
        if self.stage == "pitch":
            reply = self._llm_response(t, "pitch")
            self.last_bot_message = reply
            self.history[-1]["assistant"] = reply
            return reply, None

        # Default fallback
        reply = self._llm_response(t, "general")
        self.last_bot_message = reply
        self.history[-1]["assistant"] = reply
        return reply, None

    # ------------------------------------------------
    # FINAL SUMMARY
    # ------------------------------------------------
    def _final(self, reason, conversion):
        return (
            "No, not a potential customer\n"
            f"Reasons:\n- {reason}\n"
            f"How we could convert them:\n- {conversion}"
        )
