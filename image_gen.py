"""
Christian Image Generation — Gemini Version
---------------------------------------------
Uses Google Imagen 3 via the Gemini API (free tier).
Falls back gracefully with a detailed text description if
Imagen is unavailable in the user's region.
"""

import os
import io
import base64
from safety import check_image_safety, SafetyLevel


# ── Prompt enrichment ────────────────────────────────────────────────────────

_STYLE_SUFFIX = (
    ", classical Christian artwork, oil painting style, "
    "reverent and spiritually uplifting, warm golden light, "
    "Renaissance art tradition, highly detailed"
)

_FORBIDDEN_TERMS = [
    "violence", "blood", "war", "weapon", "gun", "knife", "bomb",
    "nude", "naked", "sexual", "horror", "demon", "satan",
    "burning cross", "political",
]


def _sanitise_prompt(prompt: str) -> str:
    cleaned = prompt
    for term in _FORBIDDEN_TERMS:
        cleaned = cleaned.replace(term, "")
    return cleaned.strip()


def build_image_prompt(user_prompt: str) -> str:
    sanitised = _sanitise_prompt(user_prompt)
    return f"Christian religious artwork: {sanitised}{_STYLE_SUFFIX}"


# ── Generation ───────────────────────────────────────────────────────────────

def generate_christian_image(user_prompt: str) -> dict:
    """
    Generate a Christian image via Gemini Imagen 3.
    Falls back to text description if Imagen is unavailable.

    Returns:
        {
          "success":      bool,
          "url":          str | None,       # URL if available
          "image_bytes":  bytes | None,     # Raw bytes if returned directly
          "blocked":      bool,
          "fallback":     bool,             # True if text fallback used
          "message":      str
        }
    """
    # Safety check first
    safety = check_image_safety(user_prompt)
    if safety.level == SafetyLevel.BLOCKED:
        return {
            "success":     False,
            "url":         None,
            "image_bytes": None,
            "blocked":     True,
            "fallback":    False,
            "message":     safety.message,
        }

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {
            "success":     False,
            "url":         None,
            "image_bytes": None,
            "blocked":     False,
            "fallback":    False,
            "message":     "GEMINI_API_KEY not configured. Add it to your .env file.",
        }

    final_prompt = build_image_prompt(user_prompt)

    # ── Try Imagen 3 ──────────────────────────────────────────────────────────
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)

        imagen_model = genai.ImageGenerationModel("imagen-3.0-generate-002")
        result = imagen_model.generate_images(
            prompt=final_prompt,
            number_of_images=1,
            aspect_ratio="1:1",
        )

        if result.images:
            img = result.images[0]
            # Imagen returns PIL image or raw bytes depending on SDK version
            if hasattr(img, "_pil_image") and img._pil_image:
                buf = io.BytesIO()
                img._pil_image.save(buf, format="PNG")
                return {
                    "success":     True,
                    "url":         None,
                    "image_bytes": buf.getvalue(),
                    "blocked":     False,
                    "fallback":    False,
                    "message":     "Image generated with Imagen 3.",
                }
            elif hasattr(img, "image") and img.image:
                return {
                    "success":     True,
                    "url":         None,
                    "image_bytes": img.image,
                    "blocked":     False,
                    "fallback":    False,
                    "message":     "Image generated with Imagen 3.",
                }

    except Exception as imagen_error:
        # Imagen not available — fall back to text description
        pass

    # ── Fallback: Gemini text describes the image ─────────────────────────────
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)

        text_model = genai.GenerativeModel("gemini-2.5-flash-image")
        fallback_prompt = (
            f"Describe in vivid, poetic detail what a classical Christian painting "
            f"of the following scene would look like. Be very descriptive about "
            f"colors, light, composition, facial expressions, and spiritual atmosphere. "
            f"Scene: {user_prompt}"
        )
        response = text_model.generate_content(fallback_prompt)
        return {
            "success":     True,
            "url":         None,
            "image_bytes": None,
            "blocked":     False,
            "fallback":    True,
            "message":     response.text,
        }

    except Exception as e:
        return {
            "success":     False,
            "url":         None,
            "image_bytes": None,
            "blocked":     False,
            "fallback":    False,
            "message":     f"Image generation failed: {str(e)}",
        }


# ── Suggested prompts ────────────────────────────────────────────────────────

SAMPLE_IMAGE_PROMPTS = [
    "The Good Shepherd carrying a lamb",
    "The Last Supper scene in Renaissance style",
    "A dove descending over calm water at sunrise",
    "The Sermon on the Mount with crowd",
    "A glowing cross on a hill at sunset",
    "Mary and the infant Jesus in the stable",
    "The resurrection of Jesus with rays of light",
    "Daniel in the lions' den, peaceful and praying",
    "Noah's ark on calm waters under a rainbow",
    "Jesus walking on water reaching out to Peter",
]
