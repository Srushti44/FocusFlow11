from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Chunk(BaseModel):
    id: str
    index: int
    text: str
    key_takeaway: Optional[str] = None
    word_count: int
    estimated_seconds: int
    entities: List[str] = Field(default_factory=list)
    cognitive_difficulty: str = "medium"  # "easy", "medium", "dense"

class QuizQuestion(BaseModel):
    id: str
    question: str
    options: List[str]
    correct_answer_index: int
    explanation: str

class Flashcard(BaseModel):
    id: str
    front: str
    back: str
    category: str = "Core Concept"
    mastered: bool = False

class KeyConcept(BaseModel):
    id: str
    term: str
    definition: str
    analogy: Optional[str] = None
    context: Optional[str] = None

class ArticleSummary(BaseModel):
    tldr: str
    detailed_explanation: Optional[str] = None
    key_takeaways: List[str] = Field(default_factory=list)
    cognitive_outline: List[Dict[str, str]] = Field(default_factory=list)
    is_ai_generated: bool = False
    provider: str = "deterministic_nlp"
    fallback_notice: Optional[str] = None

class SemanticHighlight(BaseModel):
    id: str
    category: str  # "concept", "definition", "evidence"
    text: str
    start_char: int
    end_char: int
    label: str
    explanation: Optional[str] = None

class Article(BaseModel):
    id: str
    title: str
    author: Optional[str] = "Unknown Author"
    source_url: Optional[str] = None
    domain: Optional[str] = "Web Source"
    raw_content: Optional[str] = ""
    reading_time_minutes: int = 5
    word_count: int = 0
    flesch_score: float = 65.0
    cognitive_rating: str = "Standard" # "Accessible", "Standard", "Dense / Academic"
    chunks: List[Chunk] = Field(default_factory=list)
    summary: Optional[ArticleSummary] = None
    concepts: List[KeyConcept] = Field(default_factory=list)
    quiz: List[QuizQuestion] = Field(default_factory=list)
    flashcards: List[Flashcard] = Field(default_factory=list)
    highlights: List[SemanticHighlight] = Field(default_factory=list)
    progress_percent: int = 0
    current_chunk_index: int = 0
    is_favorite: bool = False
    is_completed: bool = False
    created_at: str

class ArticleListItem(BaseModel):
    id: str
    title: str
    author: Optional[str] = "Unknown Author"
    domain: Optional[str] = "Web Source"
    reading_time_minutes: int
    word_count: int
    progress_percent: int
    current_chunk_index: int
    is_favorite: bool
    is_completed: bool
    total_chunks: int
    created_at: str

class ExtractRequest(BaseModel):
    url: Optional[str] = None
    html: Optional[str] = None
    text: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    chunk_size_words: Optional[int] = 80

class ChunkRequest(BaseModel):
    text: str = Field(..., max_length=150000, description="Raw article text to segment")
    chunk_size_words: Optional[int] = Field(80, ge=30, le=200, description="Target word count per chunk")
    preserve_headings: Optional[bool] = True

class ChunkResponse(BaseModel):
    total_chunks: int
    word_count: int
    reading_time_minutes: int
    flesch_score: float
    cognitive_rating: str
    chunks: List[Chunk]

class ExplainRequest(BaseModel):
    text: str = Field(..., max_length=5000, description="Selected text snippet to simplify")
    context: Optional[str] = Field(None, max_length=10000, description="Surrounding paragraph for context")
    target_level: Optional[str] = Field("simple", description="Simple, analogy, or executive")

class ExplainResponse(BaseModel):
    original_text: str
    simple_explanation: str
    key_takeaway: str
    analogy: Optional[str] = None
    is_ai_generated: bool = False
    provider: str = "deterministic_nlp"

class HighlightsRequest(BaseModel):
    text: str = Field(..., max_length=150000)
    article_title: Optional[str] = None

class HighlightsResponse(BaseModel):
    total_highlights: int
    highlights: List[SemanticHighlight]
    legend: Dict[str, str] = {
        "concept": "🟡 Key Concept (Core terminology & theories)",
        "definition": "🟢 Definition (Direct explanations of terms)",
        "evidence": "🔵 Supporting Detail (Statistics, data & empirical findings)"
    }
    is_ai_generated: bool = False
    provider: str = "deterministic_nlp"

class SummaryRequest(BaseModel):
    text: str = Field(..., max_length=150000)
    title: Optional[str] = "Article"

class QuizRequest(BaseModel):
    text: str = Field(..., max_length=150000)
    title: Optional[str] = "Article"

class FlashcardsRequest(BaseModel):
    text: str = Field(..., max_length=150000)
    title: Optional[str] = "Article"

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    question: str = Field(..., max_length=2000)
    article_text: str = Field(..., max_length=150000)
    article_title: Optional[str] = "Article"
    history: List[ChatMessage] = Field(default_factory=list)

class ChatResponse(BaseModel):
    answer: str
    is_ai_generated: bool = False
    provider: str = "deterministic_nlp"

class ProgressUpdateRequest(BaseModel):
    progress_percent: int
    current_chunk_index: int
    is_completed: Optional[bool] = None

class UserSettings(BaseModel):
    font_family: str = "lexend" # "lexend", "atkinson", "dyslexic", "sans", "serif", "mono"
    font_size: int = 18         # in px (14 - 28)
    line_spacing: float = 1.8   # 1.4 to 2.4
    letter_spacing: float = 0.5 # in px (0 to 3)
    content_width: int = 720    # in px (500 to 900)
    bionic_reading: bool = False
    focus_ruler: bool = False
    chunk_mode: bool = True     # True = Chunk-by-chunk, False = Full Flow
    chunk_size_words: int = 80  # 40 to 140
    enable_semantic_highlights: bool = True
    focus_mode: bool = False    # Zen reading mode (hides chrome)
    tts_speed: float = 1.0
    theme: str = "warm"         # "warm", "white", "dark", "slate"
    reduced_motion: bool = False
    high_contrast: bool = True
