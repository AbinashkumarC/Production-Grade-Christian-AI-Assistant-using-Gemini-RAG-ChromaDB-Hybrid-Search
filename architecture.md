# Architecture Note — Christianity AI Assistant

## Overview

A production-grade AI assistant for Christianity-related queries, combining LLM reasoning, Bible RAG grounding, multimodal image generation, denomination-aware prompting, and a two-stage safety pipeline.

---

## System Architecture

```
User Input
    │
    ▼
┌─────────────────────────────┐
│   Stage 1: Safety Pre-filter│  ← Rule-based (regex/keyword)
│   safety.py                 │    Fast, no API cost
└────────────┬────────────────┘
             │ SAFE / WARNING
             ▼
┌─────────────────────────────┐
│   Bible RAG Pipeline        │  ← ChromaDB + sentence-transformers
│   bible_rag.py              │    KJV corpus, semantic search
│   - Verse retrieval         │    Returns top-5 relevant verses
│   - Fake verse detection    │    Checks user-cited references
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│   Chat Engine               │  ← Anthropic Claude claude-sonnet-4-20250514
│   chat_engine.py            │    System prompt + RAG context injected
│   - Denomination context    │    Sliding window memory (20 turns)
│   - Hallucination guards    │
│   - Conversation memory     │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  Post-response Audit        │  ← verify_cited_verses()
│  bible_rag.py               │    Regex-extracts all verse refs from response
│                             │    Cross-checks against local KJV index
└────────────┬────────────────┘
             │
             ▼
         Response + Citations + Verification Report
```

---

## Key Design Decisions

### 1. Hallucination Prevention (Most Critical)
**Problem**: LLMs confidently fabricate Bible verse references.

**Solution — Three-layer guard:**
1. **RAG context injection**: Top-5 semantically relevant real verses are injected into every prompt. The LLM is guided toward citing verses it has just seen.
2. **User-input verse detection**: Regex extracts any verse reference the user cites; verified against the local KJV index before the LLM sees it. If fake, an explicit alert is injected into the system.
3. **Post-response audit**: All verse references in the model's response are extracted and verified. UI shows a ✅/❌ badge per citation.

**Why this works**: The model never needs to recall a verse from training — it always has real verses provided. Post-audit catches any slip-through.

### 2. Bible RAG Pipeline
- **Corpus**: King James Version (public domain) — ~31,000 verses from `aruljohn/Bible-kjv` on GitHub.
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (local, free, fast).
- **Vector store**: ChromaDB (persistent, local) — no cloud dependency.
- **Chunking**: One verse = one document. Metadata: `{reference, text}`.
- **Retrieval**: Cosine similarity top-5 per query.

**Trade-off**: Single-verse chunking loses pericope context but maximises precision for citation verification.

### 3. Safety Layer — Two-Stage
**Stage 1 (rule-based)**: Regex/keyword pre-filter catches explicit attack patterns (scripture rewrites, hate speech, blasphemous image requests) with zero API cost and ~0ms latency.

**Stage 2 (LLM-based, implicit)**: Claude's own safety training handles nuanced adversarial prompts that slip past Stage 1 (e.g. subtle jailbreaks, euphemistic hate speech).

**Edge cases handled:**
- Scripture rewrite requests → hard block
- Fake verse assertions → alert injection
- Adversarial image prompts → image-specific block filter
- Hateful framing → blocked or redirected gracefully
- Roleplay jailbreaks → system prompt includes explicit instruction

### 4. Denomination-Aware Prompting
Different denominations have fundamentally different epistemologies (what counts as authority):
- **Catholic**: Scripture + Tradition + Magisterium
- **Protestant**: Sola Scriptura
- **Orthodox**: Scripture + Holy Tradition + Church Fathers
- **Pentecostal**: Scripture + ongoing Holy Spirit gifts

The denomination is injected as a **context block** in the system prompt, not as a user message, so it shapes the entire response framing without being forgeable by the user.

### 5. Conversation Memory
- Simple sliding-window buffer: last 20 messages (10 turns).
- RAG context is injected into the user message but **not saved to history** (to avoid token inflation across turns).
- Clean history means the LLM always sees the actual conversation, not noise.

### 6. Image Generation Safety
- Stage 1: Regex blocks explicit policy violations before calling DALL-E.
- Prompt enrichment: User prompt is wrapped in a "Classical Christian art, reverent, warm light" style context.
- Forbidden terms are stripped from the prompt.
- DALL-E 3's own moderation provides a final safety net.

---

## Technology Stack

| Component        | Technology                          | Reason                          |
|------------------|-------------------------------------|---------------------------------|
| LLM              | Anthropic Claude (claude-sonnet-4)  | Strong theological reasoning, safety training |
| Embeddings       | sentence-transformers MiniLM-L6     | Local, fast, good semantic quality |
| Vector DB        | ChromaDB                            | Local-first, easy setup, no cloud dependency |
| Image Gen        | OpenAI DALL-E 3                     | Best policy compliance, quality |
| Frontend         | Streamlit                           | Rapid demo deployment           |
| Bible Corpus     | aruljohn/Bible-kjv (public domain)  | Complete KJV, well-structured JSON |

---

## Evaluation Strategy

See `eval_dataset.json` — 20 test cases across 6 categories:

| Category           | Test Count | Purpose                                      |
|--------------------|-----------|----------------------------------------------|
| hallucination_test | 3         | Verify fake/wrong verse references are caught |
| fake_verse         | 2         | Misquoted or misattributed popular passages  |
| adversarial        | 5         | Jailbreaks, scripture manipulation, hate     |
| adversarial_image  | 2         | Policy-violating image prompts               |
| theological_hard   | 4         | Complex doctrine handled gracefully          |
| denomination_test  | 2         | Denomination-specific accuracy               |
| valid_query        | 2         | Baseline quality check                       |

---

## Limitations & Future Work

- KJV only — future: add NIV, ESV, NAB, LXX corpora
- No audio/speech interface yet
- Denomination detection could be automatic (NLP intent classifier)
- Evaluation runner script could auto-score responses via a judge LLM
- Could add cross-reference linking (topical Bible chains)
