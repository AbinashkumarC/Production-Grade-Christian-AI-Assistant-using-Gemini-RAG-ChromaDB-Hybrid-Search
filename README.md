# ✝️ Christianity AI Assistant

A production-grade AI assistant for Christianity — scripture-grounded, denomination-aware, and hallucination-safe.  
**100% free to run** using the Google Gemini free tier.

---

## 🚀 Quick Start

### 1. Get your FREE Gemini API key
1. Go to → **https://aistudio.google.com/apikey**
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the key (starts with `AIza...`)

### 2. Clone & install
```bash
git clone https://github.com/yourusername/christianity-ai-assistant.git
cd christianity-ai-assistant
pip install -r requirements.txt
```

### 3. Add your API key
```bash
cp .env.example .env
```
Open `.env` and replace `your_gemini_api_key_here` with your actual key:
```
GEMINI_API_KEY=AIzaSy...your_key_here
```

### 4. Run
```bash
streamlit run app.py
```

> **First run**: Downloads the KJV Bible (~2MB) and builds the ChromaDB index (~31,000 verses). Takes ~2-3 minutes. All future runs are instant.

---

## Features

| Feature | Details |
|---|---|
| 💬 Chat | Scripture-grounded answers via Bible RAG pipeline |
| 📖 Verse verification | Every cited verse cross-checked against KJV corpus |
| 🔍 Hallucination guard | Fake verse detection in user input AND model output |
| ✝️ Denomination-aware | 6 modes: Catholic, Protestant, Orthodox, Baptist, Pentecostal, General |
| 🎨 Image generation | Gemini Imagen 3 + text fallback if unavailable |
| 🛡️ Safety layer | Two-stage: rule-based pre-filter + LLM moderation |
| 🧪 Eval suite | 20 test cases: adversarial, hallucination, theological edge cases |

---

## Free Tier Limits (Gemini)

| Model | Free Limit |
|---|---|
| Gemini 1.5 Flash (chat) | 15 req/min · 1,500 req/day |
| Imagen 3 (images) | Available on free tier (region-dependent) |

More than enough for demos and interviews.

---

## Project Structure

```
christianity-ai-assistant/
├── app.py                    # Streamlit UI (Chat / Image / Eval tabs)
├── chat_engine.py            # Gemini LLM + RAG + memory
├── bible_rag.py              # KJV corpus + ChromaDB + verse verification
├── safety.py                 # Two-stage moderation layer
├── denomination_handler.py   # 6 denomination profiles
├── image_gen.py              # Imagen 3 + text fallback
├── eval_dataset.json         # 20 evaluation test cases
├── architecture.md           # Design decisions document
├── requirements.txt
└── .env.example
```

---

## Architecture

See [architecture.md](architecture.md) for full design decisions.

```
User Input
    ↓
Safety Pre-filter (rule-based, instant)
    ↓
Bible RAG (ChromaDB semantic search → top 5 real verses)
    ↓
Fake Verse Detector (check user-cited refs against KJV)
    ↓
Gemini 1.5 Flash (with system prompt + RAG context)
    ↓
Post-response Verse Audit (verify every cited reference)
    ↓
Response + Citations + Verification badges
```

---

## License
MIT
