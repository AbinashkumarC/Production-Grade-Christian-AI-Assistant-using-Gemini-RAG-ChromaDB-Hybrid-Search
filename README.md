# ✝️ Christian AI Assistant — Production-Grade RAG + Gemini AI System

A production-ready Christianity-focused AI Assistant powered by **Google Gemini**, **Retrieval-Augmented Generation (RAG)**, **Hybrid Search**, **ChromaDB**, and **Safety Guardrails**.

This system delivers:

* Biblically grounded answers
* Context-aware theological discussions
* Citation-verified scripture retrieval
* Multi-denominational response adaptation
* Safe and moderated AI interactions
* AI-generated Christian artwork

---

# 🚀 Features

## ✝️ Bible-Aware RAG System

* Downloads and processes the **King James Version (KJV)** Bible
* Creates semantic embeddings
* Stores vector representations in **ChromaDB**
* Retrieves scripture passages using similarity search
* Verifies verse citations before response generation

---

## 🤖 Gemini-Powered Conversational AI

Uses Google Gemini for:

* Contextual theological conversations
* Scripture interpretation
* Memory-aware dialogue
* Christian counseling-style interactions
* Hallucination reduction with retrieval grounding

---

## 🔍 Hybrid Retrieval Architecture

Combines:

* Semantic vector search
* Keyword matching
* Citation verification
* Context ranking

This improves:

* Retrieval accuracy
* Theological consistency
* Verse relevance
* Reduced hallucinations

---

## 🛡️ Multi-Layer Safety System

Includes:

* Regex-based pre-filtering
* Prompt injection protection
* LLM-based moderation
* Unsafe theological response detection
* Hallucination guardrails

---

## ⛪ Denomination-Aware Responses

Supports multiple Christian traditions:

* Catholic
* Protestant
* Orthodox
* Baptist
* Pentecostal
* Non-denominational

Each denomination injects customized system prompts for contextualized responses.

---

## 🎨 Christian AI Image Generation

Integrated DALL·E image generation for:

* Bible scenes
* Christian artwork
* Inspirational imagery
* Church visual concepts

Safety layers prevent harmful or unsafe image prompts.

---

# 🧠 System Architecture

```text
                    ┌────────────────────┐
                    │    User Query      │
                    └─────────┬──────────┘
                              │
                              ▼
                 ┌────────────────────────┐
                 │  Safety Pre-Filtering  │
                 │ Regex + LLM Moderation │
                 └─────────┬──────────────┘
                           │
                           ▼
                ┌─────────────────────────┐
                │ Denomination Handler    │
                │ System Prompt Injection │
                └─────────┬───────────────┘
                          │
                          ▼
                ┌─────────────────────────┐
                │ Hybrid Retrieval Layer  │
                │ Semantic + Keyword      │
                └─────────┬───────────────┘
                          │
          ┌───────────────┴────────────────┐
          ▼                                ▼
┌──────────────────┐           ┌──────────────────┐
│   ChromaDB       │           │  Bible Corpus    │
│ Vector Database  │           │ KJV Scripture DB │
└────────┬─────────┘           └────────┬─────────┘
         │                               │
         └──────────────┬────────────────┘
                        ▼
             ┌─────────────────────┐
             │  Gemini LLM Engine  │
             │ Grounded Generation │
             └─────────┬───────────┘
                       │
                       ▼
            ┌────────────────────────┐
            │ Citation Verification  │
            │ Hallucination Guard    │
            └─────────┬──────────────┘
                      │
                      ▼
              ┌─────────────────┐
              │ Final Response  │
              └─────────────────┘
```

---

# 🏗️ Tech Stack

| Component        | Technology            |
| ---------------- | --------------------- |
| Frontend UI      | Streamlit             |
| LLM              | Google Gemini         |
| Vector Database  | ChromaDB              |
| Embeddings       | Gemini Embeddings     |
| Retrieval        | Hybrid Search         |
| Image Generation | DALL·E 3              |
| Moderation       | Regex + LLM Safety    |
| Memory           | Conversational Memory |
| Language         | Python                |
| Deployment       | Docker / Cloud Ready  |

---

# 📂 Project Structure

```text
project/
│
├── app.py
├── bible_rag.py
├── chat_engine.py
├── denomination_handler.py
├── safety.py
├── image_gen.py
├── eval_dataset.json
├── architecture.md
├── requirements.txt
├── .env.example
└── README.md
```

---

# ⚙️ How the RAG Pipeline Works

## Step 1 — Bible Processing

The KJV Bible is downloaded and chunked into searchable scripture passages.

---

## Step 2 — Embedding Generation

Each scripture chunk is converted into vector embeddings using Gemini embedding models.

---

## Step 3 — Vector Storage

Embeddings are stored in ChromaDB for fast semantic retrieval.

---

## Step 4 — Hybrid Search

When a user asks a question:

* Semantic similarity search retrieves relevant verses
* Keyword matching improves precision
* Results are ranked and filtered

---

## Step 5 — Grounded Generation

Retrieved scripture context is injected into Gemini prompts.

This prevents:

* Hallucinations
* Unsupported theology
* Fabricated Bible references

---

## Step 6 — Citation Verification

All scripture references are validated before returning the final response.

---

# 🔐 Safety Architecture

## Stage 1 — Regex Safety Filters

Blocks:

* Harmful prompts
* Prompt injection attempts
* Toxic content
* Unsafe theological manipulation

---

## Stage 2 — LLM Moderation

Secondary moderation verifies:

* Context safety
* Theological grounding
* Response integrity

---

# 📊 Evaluation Dataset

The project includes:

* Adversarial prompts
* Hallucination tests
* Scripture verification tests
* Denomination consistency checks
* Safety validation cases

Evaluation file:

```text
eval_dataset.json
```

---

# 🖼️ Example Queries

```text
"What does the Bible say about forgiveness?"

"Explain Romans 8:28"

"Generate an image of Noah's Ark"

"How do Catholics and Protestants interpret baptism differently?"
```

---

# 📦 Installation

## 1. Clone Repository

```bash
git clone https://github.com/your-username/christian-ai-assistant.git
cd christian-ai-assistant
```

---

## 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create `.env`

```env
GEMINI_API_KEY=your_key
OPENAI_API_KEY=your_key
```

---

## 5. Run Application

```bash
streamlit run app.py
```

---

# 🐳 Docker Deployment

```bash
docker build -t christian-ai .
docker run -p 8501:8501 christian-ai
```

---

# 📈 Future Improvements

* Multi-Bible translation support
* Voice interaction
* Church knowledge graphs
* Fine-tuned theological models
* Long-term memory
* Multi-agent theological debate system

---

# 🤝 Contributing

Pull requests are welcome.

For major changes:

1. Fork repository
2. Create feature branch
3. Commit changes
4. Open pull request

---

# 📜 License

MIT License

---

# 🙏 Acknowledgements

* Google Gemini
* ChromaDB
* Streamlit
* OpenAI
* Christian theological resources

---

# ⭐ If You Like This Project

## 👨‍💻 Author

<table>
  <tr>
    <td align="center">
      <strong>Abinashkumar C</strong><br><br>
      <a href="mailto:abinashkumarc752@gmail.com">📧 abinashkumarc752@gmail.com</a><br><br>
      <a href="https://github.com/AbinashkumarC">🐙 GitHub</a> &nbsp;|&nbsp;
      <a href="https://www.linkedin.com/in/abinashkumar-c-b7222b251/">💼 LinkedIn</a> &nbsp;|&nbsp;
      <a href="https://chimerical-sunshine-442277.netlify.app/">🌐 Portfolio</a>
    </td>
  </tr>
</table>

Feel free to reach out for questions, collaboration, or feedback about this project.

Please star the repository and share it with the community.
