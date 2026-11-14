import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from datetime import datetime

from .database import (
    init_db, save_article, get_articles_list, get_article,
    update_article_progress, toggle_article_favorite, delete_article,
    get_settings, save_settings, log_reading_session, get_reading_stats
)
from .models import (
    Article, ArticleListItem, ExtractRequest, ChunkRequest, ChunkResponse,
    ExplainRequest, ExplainResponse, HighlightsRequest, HighlightsResponse,
    SummaryRequest, QuizRequest, FlashcardsRequest, ProgressUpdateRequest,
    UserSettings, ChatRequest, ChatResponse
)
from .extractor import (
    fetch_article_from_url, parse_html_to_article, process_raw_text,
    split_into_cognitive_chunks, calculate_readability
)
from .ai_service import (
    generate_summary, generate_concepts, generate_quiz, generate_flashcards,
    simplify_text_explanation, generate_highlights, get_active_provider,
    ask_about_text
)
from .ml.router import router as ml_router
from .ml.service import get_inference_service

app = FastAPI(
    title="FocusFlow Cognitive Reading API",
    description="Cognitive accessibility, article chunking, semantic highlighting, and AI retention suite API",
    version="1.2.0"
)

# Enable CORS for Vite frontend, Chrome extension popup, and Side Panel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def seed_sample_articles():
    existing = get_articles_list()
    if existing:
        return

    sample1_text = """Cognitive load theory, originally established by educational psychologist John Sweller in the late 1980s, posits that our working memory has a strictly finite capacity. When human readers encounter modern digital articles filled with animated advertisements, multi-column navigation sidebars, and unbroken blocks of dense text, our cognitive architecture suffers from extraneous load. Extraneous cognitive load is the mental effort required to process the way information is presented, rather than the core information itself.

When extraneous load exceeds our working threshold, attention fractures. Neuroimaging studies confirm that the prefrontal cortex quickly tires when continuously filtering irrelevant stimuli. Readers begin to experience visual regression—unconsciously re-reading the same sentence three or four times because their working memory failed to consolidate the preceding thought into episodic comprehension.

FocusFlow mitigates extraneous load through structured cognitive chunking and visual calm. By isolating paragraphs into atomic 60 to 90 word units, the reader's visual field remains uncluttered. When text is combined with accessible typographic rhythm, such as weighted baseline characters and subtle saccadic guidance anchors, fixation duration decreases significantly. The brain shifts energy away from filtering visual noise and redirects it toward deep conceptual retention."""

    p1 = process_raw_text(
        sample1_text,
        title="[Sample] Cognitive Load Theory and Digital Reading Architecture",
        author="FocusFlow Demo Library",
        source_url="https://nature.cognitive.org/articles/digital-reading-load",
        domain="Sample Content • nature.cognitive.org"
    )
    p1["created_at"] = datetime.now().isoformat()
    p1["summary"] = {
        "tldr": "Working memory possesses a finite capacity that is easily exhausted by digital clutter and dense blocks of text, leading to frequent visual regression.",
        "key_takeaways": [
            "Extraneous cognitive load is caused by poor presentation and visual clutter, not complex ideas.",
            "Visual regression occurs when the prefrontal cortex exhausts its working memory bandwidth.",
            "Segmenting text into 60-90 word atomic focus chunks restores natural reading rhythm."
        ],
        "cognitive_outline": [
            {"section": "1. Working Memory Limits", "takeaway": "Sweller's research demonstrates that extraneous stimuli compete directly with comprehension."},
            {"section": "2. The Prefrontal Cost", "takeaway": "Continual stimulus filtering exhausts executive focus, triggering sentence regression."},
            {"section": "3. The Architectural Solution", "takeaway": "Visual calm and single-chunk isolation allow effortless deep retention."}
        ],
        "is_ai_generated": False,
        "provider": "deterministic_nlp"
    }
    p1["concepts"] = [
        {"id": "c1", "term": "Extraneous Cognitive Load", "definition": "Mental processing wasted on poorly organized layout, visual clutter, or unnecessary distractions.", "context": "The primary barrier FocusFlow eliminates through minimal neo-brutalist interfaces."},
        {"id": "c2", "term": "Visual Regression", "definition": "The subconscious act of glancing backward and re-reading lines due to working memory dropout.", "context": "Mitigated by focus chunking and reading rulers."},
        {"id": "c3", "term": "Saccadic Anchors", "definition": "Typographic visual waypoints that guide the rapid ballistic movements of human eyes across text.", "context": "Utilized in guided bionic highlighting."}
    ]
    p1["quiz"] = [
        {
            "id": "q1",
            "question": "What is 'extraneous cognitive load' as defined in Cognitive Load Theory?",
            "options": [
                "The mental effort required to learn genuinely difficult subject matter.",
                "Mental effort wasted processing poorly designed presentation and visual noise.",
                "Physical eye strain caused by reading in dim lighting.",
                "The total memory stored in long-term neurological pathways."
            ],
            "correct_answer_index": 1,
            "explanation": "Extraneous cognitive load is strictly the friction introduced by how information is formatted and presented, rather than intrinsic difficulty."
        },
        {
            "id": "q2",
            "question": "What causes visual regression when reading on screens?",
            "options": [
                "Poor optical glasses prescription.",
                "Working memory capacity depletion from filtering peripheral distractions.",
                "High screen refresh rates causing optical illusions.",
                "Slow reading speed compared to speech."
            ],
            "correct_answer_index": 1,
            "explanation": "When working memory overflows, the brain cannot synthesize the previous sentence, forcing the eyes backward to reload context."
        },
        {
            "id": "q3",
            "question": "What is the optimal chunk size for digital reading to respect working memory limits?",
            "options": [
                "500 to 1,000 words per unit.",
                "60 to 90 words per atomic unit.",
                "Only single words flashed sequentially.",
                "Exactly one sentence per page."
            ],
            "correct_answer_index": 1,
            "explanation": "60 to 90 words allows complete thematic coherence without overwhelming the finite buffers of working memory."
        }
    ]
    p1["flashcards"] = [
        {"id": "f1", "front": "Extraneous Cognitive Load", "back": "Mental fatigue caused by layout clutter and distractions rather than the content itself.", "category": "Core Theory", "mastered": False},
        {"id": "f2", "front": "Visual Regression", "back": "Subconsciously re-reading lines because working memory dropped previous context.", "category": "Reading Psychology", "mastered": False},
        {"id": "f3", "front": "Atomic Focus Chunking", "back": "Splitting prose into 60-90 word blocks matching working memory boundaries.", "category": "Design System", "mastered": False}
    ]
    save_article(p1)


@app.on_event("startup")
def startup_event():
    init_db()
    seed_sample_articles()
    # Initialize and warm up ACLI ML model in memory
    service = get_inference_service()
    service.load_model()


# =====================================================================
# Core Health & Status Endpoints
# =====================================================================

@app.get("/api/health")
def health_check():
    provider = get_active_provider()
    ml_service = get_inference_service()
    return {
        "status": "healthy",
        "service": "FocusFlow Cognitive Reading API",
        "ai_provider": provider,
        "llm_configured": provider != "deterministic_nlp",
        "database": "sqlite_ready",
        "ml_model_loaded": ml_service.is_ready(),
        "ml_model_version": ml_service.loaded_version,
        "version": "1.3.0"
    }


# Include ACLI MLOps Router under both /api/ml and /ml
app.include_router(ml_router, prefix="/api/ml")
app.include_router(ml_router, prefix="/ml")


# =====================================================================
# Article Management & Extraction
# =====================================================================

@app.get("/api/articles", response_model=List[ArticleListItem])
def list_articles():
    return get_articles_list()


@app.get("/api/articles/{article_id}")
def read_article(article_id: str):
    art = get_article(article_id)
    if not art:
        raise HTTPException(status_code=404, detail="Article not found")
    return art


@app.post("/api/extract")
async def extract_article(req: ExtractRequest):
    if not req.url and not req.html and not req.text:
        raise HTTPException(status_code=400, detail="Provide either a url, html, or text to extract.")
    
    chunk_size = req.chunk_size_words or 80

    if req.url:
        try:
            art_data = await fetch_article_from_url(req.url, chunk_size_words=chunk_size)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to fetch content from URL: {str(e)}")
    elif req.html:
        art_data = parse_html_to_article(req.html, fallback_title=req.title, chunk_size_words=chunk_size)
    else:
        art_data = process_raw_text(
            req.text,
            title=req.title or "Focus Flow Article",
            author=req.author or "Unknown Author",
            chunk_size_words=chunk_size
        )

    art_data["created_at"] = datetime.now().isoformat()

    # Generate initial AI enhancements (graceful fallback)
    try:
        art_data["summary"] = await generate_summary(art_data["raw_content"], art_data["title"])
        art_data["concepts"] = await generate_concepts(art_data["raw_content"], art_data["title"])
        art_data["quiz"] = await generate_quiz(art_data["raw_content"], art_data["title"])
        art_data["flashcards"] = await generate_flashcards(art_data["raw_content"], art_data["title"])
    except Exception as e:
        print(f"[Extract AI Warning] Failed generating extra AI features: {e}")

    save_article(art_data)
    return art_data


@app.post("/api/process")
async def process_article(req: ExtractRequest):
    """
    Dedicated article processing and chunking pipeline.
    Parses content, cleans page clutter, calculates readability,
    splits into cognitive focus chunks, and extracts semantic highlights.
    """
    return await extract_article(req)


# =====================================================================
# Dedicated Focus Chunking Endpoint (Part B & E)
# =====================================================================

@app.post("/api/chunk", response_model=ChunkResponse)
def chunk_text(req: ChunkRequest):
    """
    Splits any supplied text into coherent, atomic reading chunks.
    Respects paragraph and heading boundaries.
    Never splits sentences mid-phrase.
    """
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    
    target_size = req.chunk_size_words or 80
    chunks = split_into_cognitive_chunks(req.text, max_words_per_chunk=target_size)
    words = req.text.split()
    word_count = len(words)
    reading_time = max(1, round(word_count / 200))
    score, rating = calculate_readability(req.text)

    return ChunkResponse(
        total_chunks=len(chunks),
        word_count=word_count,
        reading_time_minutes=reading_time,
        flesch_score=score,
        cognitive_rating=rating,
        chunks=chunks
    )


# =====================================================================
# Text Simplification / Explanation Endpoint (Part E)
# =====================================================================

@app.post("/api/explain", response_model=ExplainResponse)
async def explain_selected_text(req: ExplainRequest):
    """
    Generates a simplified, plain-English explanation and intuitive analogy
    for selected dense or confusing text.
    """
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Selected text cannot be empty.")
    
    result = await simplify_text_explanation(
        text=req.text.strip(),
        context=req.context,
        target_level=req.target_level or "simple"
    )
    return ExplainResponse(**result)


# =====================================================================
# Semantic Highlighting Endpoints (Part D & E)
# =====================================================================

@app.post("/api/highlights", response_model=HighlightsResponse)
async def get_highlights_for_text(req: HighlightsRequest):
    """
    Extracts semantic highlights for supplied text:
    - Key Concepts (core terminology)
    - Definitions (explanations of terms)
    - Supporting Details / Evidence (statistics, dates, empirical proof)
    """
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    
    data = await generate_highlights(req.text, title=req.article_title)
    return HighlightsResponse(**data)


@app.get("/api/articles/{article_id}/highlights", response_model=HighlightsResponse)
async def get_article_highlights(article_id: str):
    art = get_article(article_id)
    if not art:
        raise HTTPException(status_code=404, detail="Article not found")
    
    data = await generate_highlights(art["raw_content"], title=art["title"])
    return HighlightsResponse(**data)


# =====================================================================
# Summaries, Quizzes & Flashcards Endpoints (Part E)
# =====================================================================

@app.post("/api/summary")
async def generate_text_summary(req: SummaryRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    return await generate_summary(req.text, req.title or "Article")


@app.post("/api/quiz")
async def generate_text_quiz(req: QuizRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    return await generate_quiz(req.text, req.title or "Article")


@app.post("/api/flashcards")
async def generate_text_flashcards(req: FlashcardsRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    return await generate_flashcards(req.text, req.title or "Article")


@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_article(req: ChatRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    history_dicts = [{"role": m.role, "content": m.content} for m in req.history]
    res = await ask_about_text(
        question=req.question.strip(),
        article_text=req.article_text,
        article_title=req.article_title or "Article",
        history=history_dicts
    )
    return ChatResponse(**res)


# Article-specific regeneration endpoints
@app.post("/api/articles/{article_id}/ai/summary")
async def regenerate_summary(article_id: str):
    art = get_article(article_id)
    if not art:
        raise HTTPException(status_code=404, detail="Article not found")
    summary = await generate_summary(art["raw_content"], art["title"])
    art["summary"] = summary
    save_article(art)
    return summary


@app.post("/api/articles/{article_id}/ai/quiz")
async def regenerate_quiz(article_id: str):
    art = get_article(article_id)
    if not art:
        raise HTTPException(status_code=404, detail="Article not found")
    quiz = await generate_quiz(art["raw_content"], art["title"])
    art["quiz"] = quiz
    save_article(art)
    return quiz


@app.post("/api/articles/{article_id}/ai/flashcards")
async def regenerate_flashcards(article_id: str):
    art = get_article(article_id)
    if not art:
        raise HTTPException(status_code=404, detail="Article not found")
    flashcards = await generate_flashcards(art["raw_content"], art["title"])
    art["flashcards"] = flashcards
    save_article(art)
    return flashcards


@app.post("/api/articles/{article_id}/ai/concepts")
async def regenerate_concepts(article_id: str):
    art = get_article(article_id)
    if not art:
        raise HTTPException(status_code=404, detail="Article not found")
    concepts = await generate_concepts(art["raw_content"], art["title"])
    art["concepts"] = concepts
    save_article(art)
    return concepts


# =====================================================================
# User Progress, Reading Sessions & Settings
# =====================================================================

@app.put("/api/articles/{article_id}/progress")
def update_progress(article_id: str, req: ProgressUpdateRequest):
    art = get_article(article_id)
    if not art:
        raise HTTPException(status_code=404, detail="Article not found")
    
    update_article_progress(article_id, req.progress_percent, req.current_chunk_index, req.is_completed)
    log_reading_session(article_id, seconds_read=30, chunks_read=1)
    return {"status": "updated", "article_id": article_id}


@app.post("/api/articles/{article_id}/favorite")
def toggle_favorite(article_id: str):
    new_fav = toggle_article_favorite(article_id)
    return {"id": article_id, "is_favorite": new_fav}


@app.delete("/api/articles/{article_id}")
def remove_article(article_id: str):
    success = delete_article(article_id)
    return {"id": article_id, "deleted": success}


@app.get("/api/settings")
def fetch_settings():
    return get_settings()


@app.put("/api/settings")
def update_settings(settings: UserSettings):
    save_settings(settings.model_dump())
    return {"status": "saved"}


@app.get("/api/stats")
def fetch_stats():
    return get_reading_stats()
