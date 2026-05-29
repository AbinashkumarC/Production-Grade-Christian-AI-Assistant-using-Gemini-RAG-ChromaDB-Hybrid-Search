"""
Chat Engine — Gemini Version
------------------------------
Uses Google Gemini 1.5 Flash (free tier) as the LLM backbone.
Ties together:
  - Gemini for chat/reasoning
  - Bible RAG for verse grounding
  - Safety layer (pre & post)
  - Denomination-aware system prompt
  - Conversation memory (sliding window)
"""

import os
import google.generativeai as genai
from bible_rag import (
    retrieve_verses,
    verify_cited_verses,
    format_citation_context,
)
from safety import (
    check_text_safety,
    check_fake_verse,
    SafetyLevel,
    SafetyResult,
)
from denomination_handler import build_denomination_system_snippet


# ── Gemini client setup ───────────────────────────────────────────────────────

def _get_model():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set in .env file.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(
        model_name="gemini-3-flash-preview",
        generation_config=genai.GenerationConfig(
            max_output_tokens=1024,
            temperature=0.7,
        ),
    )


# ── System prompt factory ─────────────────────────────────────────────────────

_BASE_SYSTEM = """You are a Christian AI assistant — warm, knowledgeable, and pastorally sensitive.

CORE RESPONSIBILITIES:
1. Answer questions about Christianity, theology, and the Bible accurately.
2. Always ground your answers in actual scripture. Only cite Bible verses that truly exist.
3. If you are not certain a verse exists, say: "I believe this is from [Book], but please verify the exact reference."
4. Never fabricate, paraphrase as quotes, or attribute non-existent verses to the Bible.
5. Maintain a respectful, edifying, pastoral tone throughout.

HALLUCINATION PREVENTION RULES:
- Before citing a verse, be confident it exists. If uncertain, describe the theme without a specific reference.
- When a user quotes a fake verse, gently correct them: "That verse doesn't appear in the Bible. You may be thinking of..."
- Never say "As the Bible says in [fake reference]..."

DIFFICULT QUESTIONS:
- For contested theological questions, present the mainstream views clearly.
- Acknowledge denominational differences where they exist.
- For questions about suffering, evil, or doubt — respond with empathy before theology.

THINGS YOU WILL NEVER DO:
- Rewrite, modify, or "improve" scripture for any purpose.
- Agree that scripture supports harmful ideologies.
- Produce offensive, heretical, or hateful content.
- Mock any Christian denomination or other faith tradition.
- Claim to be human or deny being an AI.

RESPONSE FORMAT:
- Conversational and warm, not academic or preachy.
- Cite scripture as: "As Paul writes in Romans 8:28..." or "[Book chapter:verse] says..."
- Keep responses concise unless a deep dive is requested.
- Conclude theological answers with practical application where helpful.
"""


def build_system_prompt(denomination: str) -> str:
    denom_snippet = build_denomination_system_snippet(denomination)
    return f"{_BASE_SYSTEM}\n\n{denom_snippet}"


# ── Chat engine ───────────────────────────────────────────────────────────────

class ChristianChatEngine:
    def __init__(self, max_history: int = 20):
        self.max_history = max_history
        # Each entry: {"role": "user"|"model", "parts": [text]}
        self.history: list[dict] = []

    def _trim_history(self):
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

    def chat(
        self,
        user_message: str,
        denomination: str = "General / Ecumenical",
        include_rag: bool = True,
    ) -> dict:
        """
        Send a message and receive a grounded, safe response.
        Returns dict with response, safety info, verse citations.
        """

        # ── Stage 1: Pre-filter ───────────────────────────────────────────────
        safety: SafetyResult = check_text_safety(user_message)
        if safety.level == SafetyLevel.BLOCKED:
            return {
                "response":       safety.message,
                "safety_blocked": True,
                "safety_warning": False,
                "safety_message": safety.message,
                "verses_used":    [],
                "verse_checks":   [],
            }

        # ── Stage 2: RAG retrieval ────────────────────────────────────────────
        verses_used = []
        rag_context = ""
        if include_rag:
            try:
                verses_used = retrieve_verses(user_message, top_k=5)
                rag_context = "\n\n" + format_citation_context(verses_used) + "\n"
            except Exception:
                rag_context = ""

        # ── Stage 3: Fake-verse detection in user input ───────────────────────
        verse_check_input = check_fake_verse(user_message)
        pre_verse_checks  = []
        if verse_check_input["has_verse_claim"]:
            from bible_rag import verse_exists
            for ref in verse_check_input["references"]:
                actual = verse_exists(ref)
                pre_verse_checks.append({
                    "reference": ref,
                    "valid":     actual is not None,
                    "text":      actual,
                })

        # ── Stage 4: Build prompt ─────────────────────────────────────────────
        system_prompt = build_system_prompt(denomination)

        fake_verse_alert = ""
        fake_refs = [v for v in pre_verse_checks if not v["valid"]]
        if fake_refs:
            refs_str = ", ".join(r["reference"] for r in fake_refs)
            fake_verse_alert = (
                f"\n\n⚠️ SYSTEM ALERT: The user referenced verse(s) that do NOT "
                f"exist in the Bible: {refs_str}. "
                f"Politely correct them and help them find the real verse."
            )

        augmented_message = user_message + rag_context + fake_verse_alert

        # ── Stage 5: Gemini call ──────────────────────────────────────────────
        try:
            model = _get_model()

            # Build full prompt with system instructions prepended
            full_system = (
                f"{system_prompt}\n\n"
                f"---\nCONVERSATION STARTS BELOW\n---\n"
            )

            # Convert history to Gemini format
            gemini_history = []
            for msg in self.history:
                gemini_history.append({
                    "role":  msg["role"],
                    "parts": msg["parts"],
                })

            chat_session = model.start_chat(history=gemini_history)

            # First turn: inject system prompt once if history is empty
            if not self.history:
                full_first_message = full_system + augmented_message
            else:
                full_first_message = augmented_message

            response = chat_session.send_message(full_first_message)
            assistant_text = response.text

        except Exception as e:
            return {
                "response":       f"⚠️ Error calling Gemini API: {str(e)}\n\nPlease check your GEMINI_API_KEY in the .env file.",
                "safety_blocked": False,
                "safety_warning": False,
                "safety_message": "",
                "verses_used":    verses_used,
                "verse_checks":   [],
            }

        # Save to history (Gemini uses "user" / "model" roles)
        self.history.append({"role": "user",  "parts": [user_message]})
        self.history.append({"role": "model", "parts": [assistant_text]})
        self._trim_history()

        # ── Stage 6: Post-response verse verification ─────────────────────────
        post_verse_checks = verify_cited_verses(assistant_text)

        return {
            "response":       assistant_text,
            "safety_blocked": False,
            "safety_warning": safety.level == SafetyLevel.WARNING,
            "safety_message": safety.message if safety.level == SafetyLevel.WARNING else "",
            "verses_used":    verses_used,
            "verse_checks":   pre_verse_checks + post_verse_checks,
        }

    def clear_history(self):
        self.history = []
