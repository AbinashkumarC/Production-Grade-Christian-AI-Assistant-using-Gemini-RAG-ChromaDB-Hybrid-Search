"""
Safety & Moderation Layer
--------------------------
Two-stage filtering:
  Stage 1 – Fast rule-based pre-filter  (regex / keyword lists)
  Stage 2 – LLM-based semantic check    (for nuanced adversarial prompts)
"""

import re
from enum import Enum
from dataclasses import dataclass


class SafetyLevel(Enum):
    SAFE        = "safe"
    WARNING     = "warning"   # allow but add disclaimer
    BLOCKED     = "blocked"   # refuse entirely


@dataclass
class SafetyResult:
    level:   SafetyLevel
    reason:  str
    message: str          # User-facing explanation when blocked/warned


# ── Keyword / pattern lists ───────────────────────────────────────────────────

_BLOCK_PATTERNS = [
    # Scripture manipulation
    r"rewrite\s+(the\s+)?bible",
    r"rewrite\s+.{0,40}verse",
    r"modify\s+scripture",
    r"change\s+(the\s+)?bible",
    r"edit\s+(the\s+)?scripture",
    r"make\s+(the\s+)?bible\s+say",
    r"bible\s+support\s+.{0,30}(ideology|political|agenda)",
    # Hate / extremism
    r"(god|jesus|christ|bible)\s+hate[sd]?\s+\w+",
    r"religious\s+(violence|terrorism|war|genocide)",
    r"kill\s+(all\s+)?(non.christian|infidel|heretic)",
    r"(christian|religious)\s+supremac",
    r"exterminate",
    # Blasphemy / heresy intent
    r"(satan|devil|lucifer)\s+is\s+(better|greater|superior|right)",
    r"jesus\s+(was\s+)?(fake|fraud|lie|evil|bad)",
    # Exploitation of religion
    r"use\s+(the\s+)?bible\s+to\s+(justify|support)\s+(abuse|harm|violence|control)",
    r"manipulat.{0,20}(faith|believer|christian)",
]

_WARN_PATTERNS = [
    r"prove\s+(god|jesus)\s+(doesn.t\s+exist|is\s+not\s+real)",
    r"(was|is)\s+jesus\s+(just\s+a\s+)?human",
    r"bible\s+(is\s+)?(wrong|false|fake|myth)",
    r"(sex|sexual|porn|nude|naked).{0,30}(jesus|mary|saint|church|religious)",
    r"why\s+(does|did|do)\s+god\s+(allow|permit|cause).{0,30}(evil|suffering|murder)",
]

_IMAGE_BLOCK_PATTERNS = [
    r"(weapon|gun|sword|knife|bomb).{0,30}(jesus|christ|god|mary|saint)",
    r"(jesus|christ|god|mary|saint).{0,30}(weapon|gun|sword|bomb|violence)",
    r"nude|naked|sexual|porn",
    r"(jesus|christ).{0,20}(evil|dark|demonic|satan)",
    r"(cross|church).{0,20}burn",
    r"mock.{0,20}(jesus|christ|god|bible)",
    r"(jesus|christ|god).{0,20}(political|campaign|vote|party)",
]


def _matches(text: str, patterns: list[str]) -> str | None:
    """Return the first matching pattern or None."""
    lower = text.lower()
    for p in patterns:
        if re.search(p, lower):
            return p
    return None


# ── Stage 1: Rule-based ───────────────────────────────────────────────────────

def check_text_safety(user_input: str) -> SafetyResult:
    """
    Rule-based safety check for chat input.
    Returns SafetyResult with level SAFE / WARNING / BLOCKED.
    """
    matched = _matches(user_input, _BLOCK_PATTERNS)
    if matched:
        return SafetyResult(
            level=SafetyLevel.BLOCKED,
            reason=f"Matched block pattern: {matched}",
            message=(
                "I'm unable to help with that request. This assistant is designed "
                "to support faith, learning, and edification — not to manipulate, "
                "distort, or weaponize scripture. Please ask something else."
            ),
        )

    matched = _matches(user_input, _WARN_PATTERNS)
    if matched:
        return SafetyResult(
            level=SafetyLevel.WARNING,
            reason=f"Matched warning pattern: {matched}",
            message=(
                "This is a sensitive theological topic. I'll do my best to answer "
                "thoughtfully and respectfully."
            ),
        )

    return SafetyResult(
        level=SafetyLevel.SAFE,
        reason="No unsafe patterns detected",
        message="",
    )


def check_image_safety(prompt: str) -> SafetyResult:
    """
    Rule-based safety check for image generation prompts.
    """
    matched = _matches(prompt, _IMAGE_BLOCK_PATTERNS)
    if matched:
        return SafetyResult(
            level=SafetyLevel.BLOCKED,
            reason=f"Image block pattern: {matched}",
            message=(
                "That image prompt violates content guidelines. "
                "Please request reverent, appropriate Christian imagery — "
                "such as biblical scenes, landscapes, crosses, doves, or saints."
            ),
        )
    return SafetyResult(
        level=SafetyLevel.SAFE,
        reason="Image prompt appears safe",
        message="",
    )


def check_fake_verse(user_input: str) -> dict:
    """
    Detect if the user is asserting a specific Bible verse in their message.
    Returns { "has_verse_claim": bool, "references": list[str] }
    so the chat engine can verify them via bible_rag.
    """
    pattern = re.compile(
        r'\b(\d\s)?([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\s(\d+):(\d+)\b'
    )
    matches = pattern.findall(user_input)
    refs = []
    for num, book, chap, verse in matches:
        ref = f"{num.strip()+' ' if num.strip() else ''}{book} {chap}:{verse}"
        refs.append(ref)
    return {"has_verse_claim": len(refs) > 0, "references": refs}


def build_safety_note(result: SafetyResult) -> str:
    """Format a visible safety note for the UI."""
    if result.level == SafetyLevel.WARNING:
        return f"⚠️ **Sensitive Topic Notice:** {result.message}"
    if result.level == SafetyLevel.BLOCKED:
        return f"🚫 **Request Blocked:** {result.message}"
    return ""
