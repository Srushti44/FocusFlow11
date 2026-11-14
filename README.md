# FocusFlow: AI-Powered Adaptive Reading Assistant

> **LESS NOISE. MORE FOCUS.**  
> A cognitive-accessibility reading platform designed to eliminate extraneous cognitive load, prevent visual sentence regression, and dramatically improve comprehension and retention for neurodivergent learners, students, and researchers.

---

## 📌 Table of Contents
1. [Core Purpose & Design Philosophy](#-core-purpose--design-philosophy)
2. [Dual-Engine Cognitive Generation Pipeline](#-dual-engine-cognitive-generation-pipeline)
3. [Acceptance Test: Philosophical Passage Simplification](#-acceptance-test-philosophical-passage-simplification)
4. [Adaptive Cognitive Load Index (ACLI) & MLOps Lifecycle](#-adaptive-cognitive-load-index-acli--mlops-lifecycle)
5. [Evaluation Metrics & Model Performance](#-evaluation-metrics--model-performance)
6. [SHAP Model Explainability](#-shap-model-explainability)
7. [Adaptive Reading Presets](#-adaptive-reading-presets)
8. [API Endpoints Reference](#-api-endpoints-reference)
9. [Architecture & Directory Structure](#-architecture--directory-structure)
10. [Windows PowerShell Setup & Run Commands](#-windows-powershell-setup--run-commands)
11. [Verification & Automated Test Suite](#-verification--automated-test-suite)
12. [Chrome Extension Manifest V3](#-chrome-extension-manifest-v3)

---

## 🎯 Core Purpose & Design Philosophy

FocusFlow helps readers—particularly neurodivergent learners (ADHD, dyslexia, cognitive fatigue, autistic burnout)—access complex, dense, and abstract texts without suffering from sensory overwhelm or cognitive exhaustion.

### Cognitive Accessibility Toolkit
- **Atomic Focus Chunks**: Segments dense paragraphs into 60–90 word digestible units matching working memory constraints.
- **Saccadic Guidance (Bionic Reading)**: Dynamically bolds word onsets to anchor eye fixation and reduce visual regression.
- **Focus Reading Ruler**: High-contrast tinted guide bar that isolates the active line, preventing accidental skipping.
- **Accessible Typography**: Live toggles for OpenDyslexic, Lexend, Atkinson Hyperlegible, System Sans, Serif, and Monospace.
- **Audio Narration**: Web Speech API speech synthesis with synchronized chunk advance and 0.75×–1.5× rate control.
- **Strict Neo-Brutalist UI**: High-contrast, intentional color palette (Off-White `#F4F0E8`, Ink Black `#151515`, Electric Blue `#2455FF`, Acid Lime `#D7FF38`, Coral Orange `#FF6B4A`), thick black borders, hard drop shadows, and zero low-contrast gradients.

---

## ⚡ Dual-Engine Cognitive Generation Pipeline

FocusFlow replaces extractive summarization with a **dual-path comprehension engine** guaranteeing that generated summaries, takeaways, concepts, quizzes, and AI chat responses always simplify complex material rather than repeating impenetrable jargon.

```
                  ┌──────────────────────────────────────────────┐
                  │            Source Document / Text            │
                  └──────────────────────┬───────────────────────┘
                                         │
                                         ▼
                 ┌────────────────────────────────────────────────┐
                 │          ai_service.py Provider Check          │
                 │   (OpenRouter, Google Gemini, OpenAI, Local)   │
                 └──────────────┬──────────────────┬──────────────┘
                                │                  │
                     LLM Key Available     No LLM / Offline /
                                │          Network Limitation
                                ▼                  ▼
           ┌────────────────────────────┐  ┌────────────────────────────┐
           │   Live LLM Orchestration   │  │  Deterministic Simplifier  │
           │  - Plain English Prompts   │  │  - 150+ Jargon Lexicon     │
           │  - Neurodivergent Schema   │  │  - Clause Deconstruction   │
           │  - Real-world Analogies    │  │  - Analogy Templates       │
           │  - Grounded Quiz Engine    │  │  - Rule-based QA Engine    │
           └────────────┬───────────────┘  └─────────────┬──────────────┘
                        │                                │
                        └───────────────┬────────────────┘
                                        ▼
                 ┌────────────────────────────────────────────────┐
                 │         Accessible Learning Content            │
                 │  - 1-Sentence Plain-English TL;DR              │
                 │  - Multi-Sentence Detailed Explanation         │
                 │  - Rewritten Key Takeaways (Why It Matters)   │
                 │  - Concepts with Definitions & Real Analogies  │
                 │  - Grounded Quizzes with Rich Explanations     │
                 │  - Context-Aware Ask AI with Speculation Guard │
                 └────────────────────────────────────────────────┘
```

### Cognitive Simplification Principles
1. **Plain English TL;DR**: Direct explanation using common words, short sentences, and everyday terms.
2. **Detailed Plain-English Explanation**: Expands on abstract ideas without copying long sentences from the original.
3. **Key Takeaways**: Rewrites main arguments in accessible language and explicitly explains *why each idea matters*.
4. **Concepts & Analogies**: Pairs difficult terminology with simple definitions and relatable analogies (e.g., virtual reality games, courtroom evidence, internal mirrors).
5. **Section Outlines**: Organizes the text into thematic chunks with plain-language subheadings.
6. **Flashcards & Quizzes**: Comprehension-testing questions with plausible distractors and educational rationales.
7. **Ask AI (`/api/chat`)**: Context-aware conversational assistant grounded in the source text; never hallucinates facts, clearly flags general background knowledge, and explains concepts simply.
8. **Graceful Offline Fallback**: If an LLM provider is unavailable or rate-limited, the local deterministic engine applies a 150+ academic lexicon translator and clause restructurer, displaying a helpful educational disclaimer rather than raw extracted text.

---

## 🧪 Acceptance Test: Philosophical Passage Simplification

The application is rigorously validated against dense academic and philosophical texts.

### Test Passage: *"The Epistemological Impasse of Ontological Solipsism"*
```text
The inexorable conundrum of radical ontological solipsism resides in its hermetic refutation
of external reality, positing instead that the totality of cosmic existence is merely an
epiphenomenal projection of the individual, insular psyche. This metaphysical doctrine
asserts that the ego is the sole veridical entity in existence, thereby rendering all
external phenomena, alterity, and objective material substrate nothing more than
phantasmagoric simulacra generated by an isolated consciousness. To engage in the teleological
interrogation of this framework is to confront an insurmountable epistemological impasse.
Because all sensory data must be mediated through the subjective apparatus of the observer,
one cannot proffer an unmediated, objective validation of an extra-mental universe without
committing a egregious logical petition principii. Consequently, the solipsist remains
perpetually entombed within the panopticon of their own cognitive architecture, completely
unable to discern whether the external cosmos possesses intrinsic ontological validity or
if it is merely a specious, dream-like configuration born of an idiosyncratic, auto-generated hallucination.
```

### Before vs. After Comparison

| Component | Previous Behavior (Defect) | New Behavior (Fixed) |
|---|---|---|
| **Summary TL;DR** | Extracted and repeated verbatim: *"The inexorable conundrum of radical ontological solipsism resides in its hermetic refutation..."* | **Plain English**: *"The main idea is that an individual mind might be the only real thing that exists, making the outside world an illusion."* |
| **Detailed Explanation** | Missing entirely or repeated dense text. | **Accessible Breakdown**: *"Solipsism claims that your own mind is the only thing you can be sure exists. Because all information about the universe must pass through your senses, you cannot step outside your mind to verify if physical objects or other people are actually real."* |
| **Key Takeaways** | Copied clauses with complex words like *epiphenomenal projection* and *petition principii*. | **Three Clear Points**: <br>1. *The theory says only the observer's mind is definitely real.* <br>2. *You cannot prove an external world because all your evidence comes through your own senses.* <br>3. *Trying to prove the world is real based on your senses assumes the very thing you are trying to prove.* |
| **Concepts** | Extracted dictionary definitions with more philosophical jargon. | **Defined with Real Analogies**: <br>• **Solipsism**: *The belief that only your mind exists.* Analogy: *Like being in a VR video game where you can never take off the headset.* <br>• **Epistemological Impasse**: *A dead end in knowledge where you cannot prove something true or false.* |
| **Quiz** | Verbatim cloze-deletion questions repeating impenetrable vocabulary. | **Targeted Comprehension**: <br>Q: *Why is it impossible for a solipsist to prove an external universe exists?* <br>A: *Because all evidence must pass through their own subjective senses.* <br>Explanation: *Any test relies on the observer's senses, creating circular reasoning.* |
| **Ask AI** | Generic responses or errors. | Grounded conversational explanations, offering intuitive analogies and clearly separating the author's philosophical premise from established science. |
| **Fallback Badge** | Uninformative `LOCAL FALLBACK` pill. | Informative badge: `OFFLINE SIMPLIFIER (EDUCATIONAL HEURISTICS)` with clear explanation modal explaining deterministic rules. |

---

## 🧠 Adaptive Cognitive Load Index (ACLI) & MLOps Lifecycle

FocusFlow embeds an empirical Machine Learning difficulty classifier to adapt reading controls dynamically according to cognitive density.

```
Dataset Ingestion (acli_educational_v1.json)
      │
      ▼
Feature Extraction (9 Linguistic & Readability Features)
      │
      ▼
Document-Grouped Stratified Split (split_dataset_by_document)
  - Zero cross-document leakage
  - Balanced 4-class distribution in Train, Val, and Test
      │
      ▼
Model Training & Baseline Comparison (RandomForestClassifier vs LogisticRegression)
      │
      ▼
Evaluation Metrics (Accuracy, Macro F1, Per-Class P/R/F1, Confusion Matrix)
      │
      ▼
MLflow Tracking (SQLite backend: runs, hyperparameters, metrics, artifacts)
      │
      ▼
Automated Candidate Promotion Gate (registry.py)
  - Accuracy ≥ 0.60, Macro F1 ≥ 0.60
  - Candidate F1 ≥ Current Approved F1 - 0.02
      │
      ▼
Model Registry Persisted (backend/ml/artifacts/models/v1.0.2/)
      │
      ▼
Real-time SHAP TreeExplainer & UI Adaptive Assist Presets
```

### 1. Linguistic Feature Schema (v1.0.0)

| Feature | Type | Calculation / Description | Cognitive Rationale |
|---|---|---|---|
| `avg_sentence_length` | Float | Words per sentence | Longer sentences overload phonological loop capacity. |
| `avg_word_length` | Float | Characters per word | Longer words require more visual saccades and fixations. |
| `word_count` | Int | Total tokenized words | Represents overall working memory processing envelope. |
| `sentence_count` | Int | Total sentence count | Measures structural segmentation. |
| `complex_word_pct` | Float | % words with $\ge 3$ syllables | Direct proxy for polysyllabic technical vocabulary. |
| `flesch_reading_ease` | Float | $206.835 - 1.015(W/S) - 84.6(Syll/W)$ | Standard cognitive ease benchmark bounded to [0, 100]. |
| `flesch_kincaid_grade` | Float | $0.39(W/S) + 11.8(Syll/W) - 15.59$ | Formal US grade level readability metric [1, 22]. |
| `lexical_diversity` | Float | Type-Token Ratio (distinct words / total words) | Measures vocabulary variety vs repetitive patterns. |
| `syntactic_density` | Float | Subordinate/punctuation markers per sentence | High density indicates nested clauses and convoluted syntax. |

### 2. Dataset Provenance & Leakage-Free Splitting
- **Dataset File**: `backend/ml/data/acli_educational_v1.json`
- **Samples**: 72 educational, scientific, philosophical, and everyday paragraphs across all 4 target classes:
  - `Easy` (e.g., elementary explanations, conversational stories)
  - `Medium` (e.g., secondary school texts, general news)
  - `Hard` (e.g., academic textbooks, technical articles)
  - `Very Hard` (e.g., dense philosophy, graduate-level research papers)
- **Data Leakage Prevention**: In `backend/ml/dataset.py`, the `split_dataset_by_document` function uses a **Stratified Group-based Document Split**. All paragraphs belonging to the same document are kept strictly within the same partition, preventing intra-document data leakage while guaranteeing all 4 difficulty classes are represented across Train, Validation, and Test sets.

---

## 📊 Evaluation Metrics & Model Performance

The current production model (`v1.0.2`) was trained on `acli_educational_v1.json`, logged via MLflow, and approved through the automated promotion gate.

### Approved Model Summary (`v1.0.2`)
- **Algorithm**: `RandomForestClassifier` (100 trees, max depth 8, random state 42)
- **Scaler**: `StandardScaler` (persisted under `v1.0.2/scaler.joblib`)
- **MLflow Run ID**: `ac5a4be0979f4e63856f954c38979b66`
- **Registered Version**: `v1.0.2` (Approved Production Model)

### Held-Out Test Set Metrics (10 Samples)

| Metric | Score | Passing Threshold | Status |
|---|---|---|---|
| **Test Accuracy** | **0.9000** (90.0%) | $\ge 0.60$ | ✅ PASSED |
| **Macro F1 Score** | **0.8667** (86.7%) | $\ge 0.60$ | ✅ PASSED |

### Per-Class Performance Breakdown

| Difficulty Class | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| **Easy** | 1.0000 | 1.0000 | **1.0000** | 3 |
| **Medium** | 1.0000 | 0.6667 | **0.8000** | 3 |
| **Hard** | 0.6667 | 1.0000 | **0.8000** | 2 |
| **Very Hard** | 1.0000 | 1.0000 | **1.0000** | 2 |
| **Macro Average** | **0.9167** | **0.9167** | **0.8667** | 10 |

### Test Confusion Matrix

| Actual \ Predicted | Predicted Easy | Predicted Medium | Predicted Hard | Predicted Very Hard |
|---|:---:|:---:|:---:|:---:|
| **Actual Easy** | **3** | 0 | 0 | 0 |
| **Actual Medium** | 0 | **2** | 1 | 0 |
| **Actual Hard** | 0 | 0 | **2** | 0 |
| **Actual Very Hard** | 0 | 0 | 0 | **2** |

*Note: The single misclassification is between adjacent cognitive classes (one Medium sample predicted as Hard), with zero catastrophic errors (no Easy classified as Hard/Very Hard or vice versa).*

---

## 🔍 SHAP Model Explainability

FocusFlow integrates `shap.TreeExplainer` on the registered Random Forest model to provide transparent, interpretable feature attributions for every prediction.

### Real-Time Inference & Explanation Flow
1. Text is sent to `POST /api/ml/explain`.
2. 9 linguistic features are computed and scaled.
3. `TreeExplainer` computes exact Shapley values across classes.
4. Feature attributions specifically for the **predicted class** are extracted and ranked.
5. The backend synthesizes a **grounded narrative explanation** linking high-impact features (e.g., high syllable percentage, low reading ease) directly to cognitive strain.
6. The frontend renders an interactive SHAP Attribution Bar Chart inside the `<SHAPExplanationModal>`.

---

## ⚙️ Adaptive Reading Presets

When an article or chunk is classified by the ACLI model, the frontend offers an **Adaptive Assist Banner** that can automatically apply optimal cognitive settings:

| Difficulty Level | Chunk Word Target | Saccadic (Bionic) Fixation | Reading Ruler | Narration Rate |
|---|---|---|---|---|
| **Easy** | 90 words | Off or Low (30%) | Off | 1.15× |
| **Medium** | 75 words | Medium (45%) | Optional | 1.00× |
| **Hard** | 60 words | Strong (60%) | Enabled | 0.85× |
| **Very Hard** | 45 words | Maximum (75%) | Enabled (High Contrast) | 0.75× |

*Users can always override any setting manually via the Neo-Brutalist Reader Controls Bar.*

---

## 🌐 API Endpoints Reference

The FastAPI backend exposes RESTful endpoints with full Pydantic schema validation.

| Method | Endpoint | Description | Request Body / Parameters |
|---|---|---|---|
| `POST` | `/api/extract` | Scrapes URL or ingests raw text, computes readability metrics, and segments into atomic chunks. | `ExtractRequest`: `{ url?, raw_text?, title? }` |
| `POST` | `/api/summary` | Generates plain-English TL;DR, detailed explanation, takeaways, and outline. | `SummaryRequest`: `{ text, title?, article_id? }` |
| `POST` | `/api/concepts` | Extracts difficult terms with plain definitions and real-world analogies. | `ConceptsRequest`: `{ text, title?, article_id? }` |
| `POST` | `/api/quiz` | Generates 3 comprehension questions with answer explanations. | `QuizRequest`: `{ text, title?, article_id? }` |
| `POST` | `/api/flashcards` | Generates spaced-repetition flashcards. | `FlashcardsRequest`: `{ text, title?, article_id? }` |
| `POST` | `/api/chat` | Context-aware Ask AI answering user questions grounded in the source text. | `ChatRequest`: `{ question, context_text, article_title?, history? }` |
| `POST` | `/api/ml/predict-difficulty` | Predicts difficulty class (`Easy` to `Very Hard`) with class probabilities. | `PredictRequest`: `{ text, title? }` |
| `POST` | `/api/ml/explain` | Returns SHAP feature attributions and grounded narrative rationale. | `PredictRequest`: `{ text, title? }` |
| `GET` | `/api/ml/status` | Returns active approved model version, timestamp, and metrics. | *None* |
| `GET` | `/api/ml/metrics` | Returns held-out evaluation metrics of current model. | *None* |
| `GET` | `/api/ml/runs` | Returns historical MLflow experiment runs. | *None* |

---

## 📂 Architecture & Directory Structure

```
focusflow/
├── backend/
│   ├── ai_service.py              # LLM provider orchestration + deterministic simplifier
│   ├── database.py                # SQLite database session & schema initialization
│   ├── extractor.py               # Readability metrics (FK, FRE) & chunking logic
│   ├── focusflow.db               # SQLite operational database
│   ├── main.py                    # FastAPI application, CORS, routers & API endpoints
│   ├── models.py                  # Pydantic data contracts (ArticleSummary, ChatMessage, etc.)
│   ├── requirements.txt           # Python dependencies (scikit-learn, shap, mlflow, etc.)
│   ├── test_acceptance_preview.py # Acceptance test demonstration script
│   ├── test_backend.py            # Comprehensive verification test suite (8 tests)
│   ├── ml/
│   │   ├── dataset.py             # Stratified group-based document splitting & schema validation
│   │   ├── features.py            # 9-dimensional linguistic feature extractor
│   │   ├── model.py               # Model training, hyperparameter tuning & evaluation
│   │   ├── pipeline.py            # CLI entry point for MLOps lifecycle (--train, --status, etc.)
│   │   ├── registry.py            # Versioned model registry & automated approval gate
│   │   ├── explainability.py      # SHAP TreeExplainer & narrative synthesis
│   │   ├── monitoring.py          # Feature drift monitoring & Population Stability Index (PSI)
│   │   ├── artifacts/models/      # Versioned model artifacts (v1.0.0, v1.0.2)
│   │   └── data/                  # acli_educational_v1.json training dataset
│   └── tests/
│       └── test_full_suite.py     # 20 full integration and regression tests
├── extension/                     # Chrome Extension Manifest V3
│   ├── manifest.json
│   ├── background.js
│   ├── content.js
│   └── sidepanel.html
├── src/
│   ├── components/
│   │   ├── reader/                # LearningTools, ChunkViewer, FullReader, ReadingControlsBar
│   │   ├── mlops/                 # SHAPExplanationModal, MLOpsDashboard
│   │   └── ui/                    # Neo-Brutalist Button, Card, Badge, Modal, Switch
│   ├── services/
│   │   └── api.ts                 # Frontend API client with fallback resilience
│   ├── views/
│   │   ├── ReaderView.tsx         # Main reader with difficulty badge, SHAP button & Adaptive banner
│   │   ├── DashboardView.tsx
│   │   └── LandingView.tsx
│   └── types/index.ts             # TypeScript definitions
├── vite.config.ts                 # Vite bundler configuration
└── README.md
```

---

## 💻 Windows PowerShell Setup & Run Commands

Follow these exact commands in Windows PowerShell:

### 1. Environment Setup & Installation
```powershell
# Navigate to the project root directory
cd "e:\folder d\Sem5\focusflow_new\focusflow\focusflow"

# Create Python virtual environment (if not already created)
python -m venv backend/venv

# Activate the virtual environment
.\backend\venv\Scripts\Activate.ps1

# Upgrade pip and install backend dependencies
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt

# Install Node dependencies for the frontend
npm install
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` in the project root:
```powershell
Copy-Item .env.example .env
```
*(Optional: Open `.env` and set `OPENROUTER_API_KEY`, `GEMINI_API_KEY`, or `OPENAI_API_KEY`. If no key is set, the built-in deterministic cognitive simplifier runs automatically with zero crashes.)*

### 3. Run the Acceptance Test Script
Verify plain-English generation on *"The Epistemological Impasse of Ontological Solipsism"*:
```powershell
python backend/test_acceptance_preview.py
```

### 4. Run the Machine Learning Pipeline
```powershell
# Set PYTHONPATH to root
$env:PYTHONPATH = "."

# Validate dataset integrity
python -m backend.ml.pipeline --validate-dataset

# Train model, evaluate against baseline, and log run to MLflow
python -m backend.ml.pipeline --train

# Check model registry status
python -m backend.ml.pipeline --status

# Evaluate active approved model on held-out test data
python -m backend.ml.pipeline --evaluate
```

### 5. Launch the Application

**Terminal 1 — FastAPI Backend**:
```powershell
.\backend\venv\Scripts\Activate.ps1
$env:PYTHONPATH = "."
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
*Backend Swagger Docs available at: `http://localhost:8000/docs`*

**Terminal 2 — React Vite Frontend**:
```powershell
npm run dev
```
*Web application available at: `http://localhost:5173`*

---

## 🧪 Verification & Automated Test Suite

All tests can be executed with virtual environment active:

```powershell
# 1. Run Complete Integration Suite (20 tests covering all AI & Chat workflows)
python -m pytest backend/tests/test_full_suite.py -v

# 2. Run MLOps & Machine Learning Suite (26 tests covering features, models, SHAP, and registry)
python -m pytest backend/ml/tests -v

# 3. Run End-to-End Backend Verification (8 tests)
python backend/test_backend.py

# 4. Run Frontend TypeScript Type Check
npx tsc --noEmit

# 5. Build Production Frontend Bundle
npm run build
```

---

## 🧩 Chrome Extension Manifest V3

1. Open Google Chrome and navigate to `chrome://extensions`.
2. Toggle on **Developer mode** in the top-right corner.
3. Click **Load unpacked**.
4. Select the `extension/` directory inside `focusflow/focusflow`.
5. Click the FocusFlow icon in the browser toolbar on any article to open the cognitive reading side panel!
