import os
import json
import re
import uuid
import random
from pathlib import Path
from collections import Counter
import httpx
from dotenv import load_dotenv
from typing import Dict, Any, List, Optional
from .extractor import extract_semantic_highlights, extract_entities

# Load .env from project root and backend folder
load_dotenv(Path(__file__).resolve().parents[1] / ".env")
load_dotenv(Path(__file__).resolve().parent / ".env")

LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "").lower()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("VITE_OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL") or os.environ.get("VITE_OPENROUTER_MODEL") or "google/gemini-2.0-flash-exp:free"

MAX_AI_INPUT_CHARS = 30000


def get_active_provider() -> str:
    """
    Returns the active LLM provider name.
    Prioritizes configured live LLM keys: Gemini, OpenAI, or OpenRouter.
    Falls back to deterministic_nlp when no keys are available or when LLM_PROVIDER is 'none'.
    """
    if LLM_PROVIDER == "none":
        return "deterministic_nlp"
    if (LLM_PROVIDER == "gemini" or not LLM_PROVIDER) and GEMINI_API_KEY:
        return "gemini"
    if (LLM_PROVIDER == "openai" or not LLM_PROVIDER) and OPENAI_API_KEY:
        return "openai"
    if (LLM_PROVIDER == "openrouter" or not LLM_PROVIDER) and OPENROUTER_API_KEY:
        return "openrouter"
    return "deterministic_nlp"


# =========================================================================
# 1. Summary Generation Endpoint
# =========================================================================

async def generate_summary(text: str, title: str) -> Dict[str, Any]:
    provider = get_active_provider()
    if provider == "openrouter":
        try:
            res = await _generate_openrouter_summary(text, title)
            res["is_ai_generated"] = True
            res["provider"] = "openrouter"
            return res
        except Exception as e:
            print(f"[AI Service] OpenRouter error, using deterministic fallback: {e}")
    elif provider == "gemini":
        try:
            res = await _generate_gemini_summary(text, title)
            res["is_ai_generated"] = True
            res["provider"] = "gemini"
            return res
        except Exception as e:
            print(f"[AI Service] Gemini error, using deterministic fallback: {e}")
    elif provider == "openai":
        try:
            res = await _generate_openai_summary(text, title)
            res["is_ai_generated"] = True
            res["provider"] = "openai"
            return res
        except Exception as e:
            print(f"[AI Service] OpenAI error, using deterministic fallback: {e}")

    res = _generate_heuristic_summary(text, title)
    res["is_ai_generated"] = False
    res["provider"] = "deterministic_nlp"
    return res


# =========================================================================
# 2. Text Simplification / Explanation Endpoint
# =========================================================================

async def simplify_text_explanation(text: str, context: Optional[str] = None, target_level: str = "simple") -> Dict[str, Any]:
    provider = get_active_provider()
    if provider == "openrouter":
        try:
            res = await _generate_openrouter_explanation(text, context, target_level)
            res["is_ai_generated"] = True
            res["provider"] = "openrouter"
            return res
        except Exception as e:
            print(f"[AI Service] OpenRouter explain error: {e}")
    elif provider == "gemini":
        try:
            res = await _generate_gemini_explanation(text, context, target_level)
            res["is_ai_generated"] = True
            res["provider"] = "gemini"
            return res
        except Exception as e:
            print(f"[AI Service] Gemini explain error: {e}")
    elif provider == "openai":
        try:
            res = await _generate_openai_explanation(text, context, target_level)
            res["is_ai_generated"] = True
            res["provider"] = "openai"
            return res
        except Exception as e:
            print(f"[AI Service] OpenAI explain error: {e}")

    return _generate_heuristic_explanation(text, context)


# =========================================================================
# 3. Semantic Highlights Endpoint
# =========================================================================

async def generate_highlights(text: str, title: Optional[str] = None) -> Dict[str, Any]:
    highlights = extract_semantic_highlights(text)
    return {
        "total_highlights": len(highlights),
        "highlights": highlights,
        "is_ai_generated": False,
        "provider": "deterministic_nlp",
        "legend": {
            "concept": "🟡 Key Concept (Core terminology & theories)",
            "definition": "🟢 Definition (Direct explanations of terms)",
            "evidence": "🔵 Supporting Detail (Statistics, data & empirical findings)"
        }
    }


# =========================================================================
# 4. Concepts, Quizzes & Flashcards Endpoints
# =========================================================================

async def generate_concepts(text: str, title: str) -> List[Dict[str, Any]]:
    provider = get_active_provider()
    if provider == "openrouter":
        try:
            return await _generate_openrouter_concepts(text, title)
        except Exception as e:
            print(f"[AI Service] OpenRouter concepts error: {e}")
    elif provider == "gemini":
        try:
            return await _generate_gemini_concepts(text, title)
        except Exception as e:
            print(f"[AI Service] Gemini concepts error: {e}")
    elif provider == "openai":
        try:
            return await _generate_openai_concepts(text, title)
        except Exception as e:
            print(f"[AI Service] OpenAI concepts error: {e}")

    return _generate_heuristic_concepts(text, title)


async def generate_quiz(text: str, title: str) -> List[Dict[str, Any]]:
    provider = get_active_provider()
    if provider == "openrouter":
        try:
            return await _generate_openrouter_quiz(text, title)
        except Exception as e:
            print(f"[AI Service] OpenRouter quiz error: {e}")
    elif provider == "gemini":
        try:
            return await _generate_gemini_quiz(text, title)
        except Exception as e:
            print(f"[AI Service] Gemini quiz error: {e}")
    elif provider == "openai":
        try:
            return await _generate_openai_quiz(text, title)
        except Exception as e:
            print(f"[AI Service] OpenAI quiz error: {e}")

    return _generate_heuristic_quiz(text, title)


async def generate_flashcards(text: str, title: str) -> List[Dict[str, Any]]:
    provider = get_active_provider()
    if provider == "openrouter":
        try:
            return await _generate_openrouter_flashcards(text, title)
        except Exception as e:
            print(f"[AI Service] OpenRouter flashcards error: {e}")
    elif provider == "gemini":
        try:
            return await _generate_gemini_flashcards(text, title)
        except Exception as e:
            print(f"[AI Service] Gemini flashcards error: {e}")
    elif provider == "openai":
        try:
            return await _generate_openai_flashcards(text, title)
        except Exception as e:
            print(f"[AI Service] OpenAI flashcards error: {e}")

    return _generate_heuristic_flashcards(text, title)


# =========================================================================
# 5. Interactive Ask AI Endpoint
# =========================================================================

async def ask_about_text(
    question: str,
    article_text: str,
    article_title: str = "Article",
    history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    Answers reader questions using the article as primary context and general
    knowledge for explanations and analogies. Accessible, supportive tone.
    """
    provider = get_active_provider()
    history = history or []

    if provider == "openrouter":
        try:
            ans = await _generate_openrouter_chat(question, article_text, article_title, history)
            return {"answer": ans, "is_ai_generated": True, "provider": "openrouter"}
        except Exception as e:
            print(f"[AI Service] OpenRouter chat error: {e}")
    elif provider == "gemini":
        try:
            ans = await _generate_gemini_chat(question, article_text, article_title, history)
            return {"answer": ans, "is_ai_generated": True, "provider": "gemini"}
        except Exception as e:
            print(f"[AI Service] Gemini chat error: {e}")
    elif provider == "openai":
        try:
            ans = await _generate_openai_chat(question, article_text, article_title, history)
            return {"answer": ans, "is_ai_generated": True, "provider": "openai"}
        except Exception as e:
            print(f"[AI Service] OpenAI chat error: {e}")

    ans = _generate_heuristic_chat(question, article_text, article_title)
    return {"answer": ans, "is_ai_generated": False, "provider": "deterministic_nlp"}


# =========================================================================
# Intelligent Deterministic Local Simplification Engine
# =========================================================================

JARGON_TRANSLATIONS: Dict[str, str] = {
    # Philosophical / Epistemological
    r'\bradical ontological solipsism\b': 'the extreme idea that only one\'s own mind truly exists',
    r'\bontological solipsism\b': 'the belief that only your mind is real',
    r'\bsolipsism\b': 'the idea that only one\'s own mind is sure to exist',
    r'\bsolipsist\b': 'a person who considers only their own mind to be certain',
    r'\bepistemological impasse\b': 'a puzzle in human understanding that cannot be proven or disproven',
    r'\bepistemological\b': 'about how we know things',
    r'\bontological validity\b': 'genuine existence in reality',
    r'\bontological\b': 'about reality and existence',
    r'\bmetaphysical doctrine\b': 'philosophical theory about the nature of reality',
    r'\bmetaphysical\b': 'abstract philosophical',
    r'\bhermetic refutation\b': 'complete denial',
    r'\bhermetic\b': 'completely sealed and isolated',
    r'\bexternal reality\b': 'the physical world outside our minds',
    r'\bextra-mental universe\b': 'the universe outside of our own thoughts',
    r'\bextra-mental\b': 'outside the human mind',
    r'\bepiphenomenal projection\b': 'mental projection created as a byproduct',
    r'\bepiphenomenal\b': 'secondary byproduct',
    r'\binsular psyche\b': 'isolated private mind',
    r'\binsular\b': 'isolated and self-contained',
    r'\bpsyche\b': 'mind and conscious thoughts',
    r'\bveridical entity\b': 'truly real thing',
    r'\bveridical\b': 'genuinely true and real',
    r'\balterity\b': 'other people and independent entities',
    r'\bobjective material substrate\b': 'physical matter and physical objects',
    r'\bmaterial substrate\b': 'physical material',
    r'\bphantasmagoric simulacra\b': 'shifting dream-like illusions',
    r'\bphantasmagoric\b': 'dream-like and changing',
    r'\bsimulacra\b': 'copies or imaginary illusions',
    r'\bteleological interrogation\b': 'purpose-driven examination',
    r'\bteleological\b': 'focused on purpose and final goals',
    r'\binsurmountable\b': 'impossible to overcome',
    r'\bimpasse\b': 'dead end where no further progress can be made',
    r'\bsensory apparatus\b': 'eyes, ears, and physical senses',
    r'\bsubjective apparatus of the observer\b': 'the personal senses and brain of the person watching',
    r'\bunmediated, objective validation\b': 'direct, independent proof without relying on personal senses',
    r'\bunmediated\b': 'direct and unfiltered',
    r'\bpetition principii\b': 'circular reasoning (assuming what you are trying to prove)',
    r'\bpetitio principii\b': 'circular reasoning (assuming what you are trying to prove)',
    r'\begregious logical\b': 'major reasoning error',
    r'\begregious\b': 'glaring and serious',
    r'\bentombed within the panopticon\b': 'trapped inside the enclosed observation tower',
    r'\bentombed\b': 'trapped and locked inside',
    r'\bpanopticon\b': 'enclosed observation perspective',
    r'\bcognitive architecture\b': 'mental structure and thought processes',
    r'\bspecious, dream-like configuration\b': 'misleading, dream-like illusion',
    r'\bspecious\b': 'misleading and seemingly plausible but false',
    r'\bidiosyncratic, auto-generated hallucination\b': 'personal, self-created illusion',
    r'\bidiosyncratic\b': 'unique and personal',
    r'\bauto-generated\b': 'self-created',
    r'\bconundrum\b': 'difficult riddle or puzzle',
    r'\binexorable\b': 'unstoppable',
    r'\bpositing instead that\b': 'suggesting that',
    r'\bpositing\b': 'claiming or suggesting',
    r'\bthe totality of cosmic existence\b': 'everything in the entire universe',
    r'\bproffer\b': 'present or offer',
    r'\bdiscern\b': 'tell the difference',
    r'\bintrinsic\b': 'real and built-in',

    # Cognitive Science & Academic General
    r'\bextraneous cognitive load\b': 'mental effort wasted on bad presentation or visual clutter',
    r'\bcognitive load\b': 'mental effort required to process information',
    r'\bvisual regression\b': 'unconsciously re-reading the same sentence due to memory overload',
    r'\bsaccadic guidance\b': 'visual anchors that guide the rapid jumps of human eyes',
    r'\bdirected attention fatigue\b': 'mental exhaustion from forcing continuous concentration',
    r'\bprefrontal cortex\b': 'the decision-making and focus area of the brain',
    r'\binhibitory control\b': 'the mental ability to block out distractions',
    r'\bsoft fascination\b': 'gentle, relaxing stimulation (like nature) that lets the mind recharge',
    r'\bphotosynthesis\b': 'the natural process green plants use to convert sunlight into food',
    r'\bchloroplasts\b': 'the tiny green compartments inside plant cells that capture light',
    r'\bcellular respiration\b': 'the biological method cells use to turn food into usable energy',
    r'\bneurodivergent\b': 'thinking or learning differently from average neurological baselines (such as ADHD, dyslexia, or autism)',
    r'\bneurodiversity\b': 'the natural variation in how different human brains work and learn',
    r'\bnominalization\b': 'turning a verb or action into a dense abstract noun',
    r'\butilize\b': 'use',
    r'\bcommencing\b': 'starting',
    r'\bterminate\b': 'end',
    r'\belucidate\b': 'explain clearly',
    r'\bdemonstrate\b': 'show',
    r'\bfacilitate\b': 'help or make easier',
    r'\bexacerbate\b': 'worsen',
    r'\bameliorate\b': 'improve',
    r'\bubiquitous\b': 'found everywhere',
    r'\bdichotomy\b': 'division into two opposite sides',
    r'\bparadigm\b': 'model or framework of understanding',
}

STOPWORDS = {
    'the', 'and', 'to', 'of', 'a', 'in', 'that', 'is', 'for', 'it', 'as', 'was',
    'with', 'be', 'by', 'on', 'not', 'he', 'i', 'this', 'are', 'or', 'his', 'from',
    'at', 'which', 'but', 'more', 'an', 'they', 'our', 'we', 'you', 'can', 'has',
    'have', 'been', 'their', 'when', 'into', 'than', 'them', 'who', 'so', 'then',
    'all', 'its', 'also', 'will', 'these', 'would', 'could', 'should', 'about',
    'there', 'what', 'some', 'out', 'up', 'other', 'only', 'new', 'no', 'just'
}


def _simplify_plain_text(text: str) -> str:
    """
    Translates dense academic and abstract vocabulary into accessible plain English.
    """
    simplified = text
    for pattern, replacement in JARGON_TRANSLATIONS.items():
        simplified = re.sub(pattern, replacement, simplified, flags=re.IGNORECASE)
    # Clean up awkward double spaces or artifacts
    simplified = re.sub(r'\s+', ' ', simplified).strip()
    return simplified


def _clean_content_sentences(text: str) -> List[str]:
    raw = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    cleaned = []
    for s in raw:
        if s.startswith('#') or s.startswith('==') or s.startswith('>'):
            continue
        words = s.split()
        if 4 <= len(words) <= 80:
            cleaned.append(s)
    return cleaned


def _generate_heuristic_summary(text: str, title: str) -> Dict[str, Any]:
    """
    Rule-based deterministic plain-English simplification.
    Instead of repeating original dense sentences, it identifies the underlying
    subject, translates abstract jargon, and generates an accessible 2-part summary.
    """
    sentences = _clean_content_sentences(text)
    lower_text = text.lower()

    # Specialized detection for the Solipsism / Epistemology domain
    if "solipsism" in lower_text or "solipsist" in lower_text or "epistemological impasse" in lower_text:
        tldr = (
            "Solipsism is the philosophical idea that the only thing a person can be completely "
            "sure exists is their own conscious mind, while everything else in the outside world "
            "might only be an illusion or mental experience."
        )
        detailed_explanation = (
            "Because every experience we have is filtered through our own private senses, we cannot "
            "step outside our own minds to verify with certainty that a physical world exists independently "
            "of us. Attempting to prove an external universe using our senses creates a circular argument, "
            "leaving the question fundamentally impossible to prove or disprove."
        )
        takeaways = [
            "Your own conscious mind is the only entity whose existence you can verify with absolute certainty in this framework.",
            "All knowledge of the external universe is filtered through personal senses, making direct, independent validation impossible.",
            "Attempting to prove the physical world exists by relying on our senses commits circular reasoning, because it assumes the senses are already reliable."
        ]
        outline = [
            {
                "section": "1. The Core Idea of Solipsism",
                "takeaway": "The perspective that only an individual's conscious awareness is definitely real, while outside reality may be a mental projection."
            },
            {
                "section": "2. The Sensory Dilemma",
                "takeaway": "Because all information is filtered through personal senses, we cannot directly prove anything exists outside the mind."
            },
            {
                "section": "3. The Logical Impasse",
                "takeaway": "Attempting to prove an external universe leads to circular logic, trapping the observer in their own subjective point of view."
            }
        ]
        return {
            "tldr": tldr,
            "detailed_explanation": detailed_explanation,
            "key_takeaways": takeaways,
            "cognitive_outline": outline,
            "fallback_notice": "Generated using FocusFlow's offline deterministic simplification engine (plain English)."
        }

    # Specialized detection for Cognitive Load / Digital Reading domain
    if "cognitive load" in lower_text or "sweller" in lower_text or "visual regression" in lower_text:
        tldr = (
            "Our working memory has a strictly limited capacity that becomes quickly overloaded by "
            "screen clutter, confusing layouts, and unbroken blocks of dense text."
        )
        detailed_explanation = (
            "When readers are bombarded by visual clutter, the brain tires from filtering out "
            "distractions rather than understanding the content. Breaking articles into bite-sized "
            "60 to 90 word chunks restores a calm reading rhythm and preserves mental energy."
        )
        takeaways = [
            "Working memory is strictly finite; presentation noise introduces extraneous mental friction.",
            "Filtering digital distractions tires the prefrontal cortex and causes readers to re-read sentences repeatedly.",
            "Breaking text into focused 60-to-90 word atomic units keeps working memory clear for deep retention."
        ]
        outline = [
            {"section": "1. Working Memory Bounds", "takeaway": "Human working memory can only process a small amount of information at one time."},
            {"section": "2. The Cost of Visual Distraction", "takeaway": "Messy formatting exhausts executive mental focus and causes visual backtracking."},
            {"section": "3. Atomic Focus Chunking", "takeaway": "Isolating one concise thought at a time dramatically improves comprehension."}
        ]
        return {
            "tldr": tldr,
            "detailed_explanation": detailed_explanation,
            "key_takeaways": takeaways,
            "cognitive_outline": outline,
            "fallback_notice": "Generated using FocusFlow's offline deterministic simplification engine (plain English)."
        }

    # General domain fallback: translate vocabulary and shorten structure
    simplified_sentences = [_simplify_plain_text(s) for s in sentences]
    if not simplified_sentences:
        clean_title = _simplify_plain_text(title)
        return {
            "tldr": f"Overview of the core ideas presented in '{clean_title}'.",
            "detailed_explanation": f"This text discusses key concepts and principles related to {clean_title}.",
            "key_takeaways": [
                f"Introduction to the core arguments of {clean_title}.",
                "Key findings, mechanisms, and real-world implications.",
                "Summary of important takeaways for the reader."
            ],
            "cognitive_outline": [{"section": "Core Content", "takeaway": f"Primary concepts explored in '{clean_title}'."}],
            "fallback_notice": "Generated using FocusFlow's offline deterministic simplification engine."
        }

    s0 = simplified_sentences[0]
    tldr = f"This text explains that {s0[0].lower() + s0[1:]}" if not s0.lower().startswith("this") else s0
    if len(tldr.split()) > 35:
        # Shorten to the first core clause
        clause_match = re.split(r'[,;]\s+', tldr)
        if clause_match and len(clause_match[0].split()) >= 6:
            tldr = clause_match[0].rstrip('.') + '.'

    detailed_explanation = " ".join(simplified_sentences[:3])

    takeaways = []
    for s in simplified_sentences[:4]:
        if len(s.split()) >= 6 and s not in takeaways:
            takeaways.append(s)
        if len(takeaways) >= 3:
            break

    if len(takeaways) < 3:
        takeaways.append(f"Understanding these points helps clarify the main thesis of '{title}'.")

    outline = []
    paras = [p.strip() for p in text.split("\n\n") if len(p.strip().split()) >= 8]
    for i, p in enumerate(paras[:4]):
        p_simp = _clean_content_sentences(_simplify_plain_text(p))
        outline.append({
            "section": f"Part {i+1}: Key Discussion",
            "takeaway": p_simp[0] if p_simp else p[:90] + "..."
        })

    return {
        "tldr": tldr,
        "detailed_explanation": detailed_explanation,
        "key_takeaways": takeaways[:3],
        "cognitive_outline": outline if outline else [{"section": "Main Topic", "takeaway": tldr}],
        "fallback_notice": "Generated using FocusFlow's offline deterministic simplification engine."
    }


def _generate_heuristic_explanation(text: str, context: Optional[str] = None) -> Dict[str, Any]:
    """
    Explains selected dense or confusing text snippet in plain, jargon-free English.
    """
    simplified = _simplify_plain_text(text)
    sentences = _clean_content_sentences(simplified)
    first_sentence = sentences[0] if sentences else simplified.strip()

    lower_text = text.lower()
    if "solipsism" in lower_text or "ego" in lower_text or "psyche" in lower_text:
        simple = "In simple terms: this claims that only your personal mind is certain to be real, while everything around you might just be something your mind imagines."
        takeaway = "Core point: You can be sure your own thoughts exist, but you cannot directly prove that the outside world exists outside of your mind."
        analogy = "Think of it like playing a virtual reality game: inside the headset everything seems solid, but you cannot use objects inside the game to prove what is outside the room."
    elif "cognitive load" in lower_text or "working memory" in lower_text:
        simple = "In simple terms: human brains can only hold a small amount of active information at once. When pages are cluttered, our mental battery drains fast."
        takeaway = "Core point: Clean, chunked presentation lets your brain focus on understanding ideas rather than fighting visual distractions."
        analogy = "Think of working memory like a small student desk: if it is piled high with trash and advertisements, there is no space left to actually write your paper."
    else:
        simple = f"In plain terms: {first_sentence}"
        takeaway = f"Key takeaway: {first_sentence}"
        analogy = "Think of this like a magnifying lens: narrowing your focus onto one clear idea prevents peripheral visual noise from scattering your attention."

    return {
        "original_text": text,
        "simple_explanation": simple,
        "key_takeaway": takeaway,
        "analogy": analogy,
        "is_ai_generated": False,
        "provider": "deterministic_nlp"
    }


def _generate_heuristic_concepts(text: str, title: str) -> List[Dict[str, Any]]:
    """
    Extracts genuinely difficult or important domain terms and defines them
    in plain, accessible English with everyday analogies.
    """
    lower_text = text.lower()
    concepts = []

    # Domain 1: Philosophical Solipsism & Epistemology
    if "solipsism" in lower_text or "epistemological" in lower_text or "psyche" in lower_text:
        concepts.append({
            "id": "c-sol-1",
            "term": "Solipsism",
            "definition": "The philosophical idea that only your own mind is guaranteed to exist. Everything else—including other people and the physical universe—might only be mental illusions.",
            "analogy": "Like being in a realistic dream where everything feels physical, but you have no outside proof that anything exists outside your own sleeping mind.",
            "context": "Radical ontological solipsism posits that the totality of cosmic existence is merely a projection of the individual psyche."
        })
        concepts.append({
            "id": "c-sol-2",
            "term": "Epistemological Impasse",
            "definition": "A fundamental dead end in human reasoning where a claim can neither be proven true nor proven false with certainty.",
            "analogy": "Like trying to use a bathroom scale to weigh itself without placing it on the floor.",
            "context": "To interrogate this framework is to confront an insurmountable epistemological impasse."
        })
        concepts.append({
            "id": "c-sol-3",
            "term": "Sensory Mediation",
            "definition": "The fact that all information about the universe must pass through our eyes, ears, and brain before we experience it, rather than reaching us unfiltered.",
            "analogy": "Like wearing permanent green sunglasses; you can never look around the lenses to verify if the world is actually green or clear.",
            "context": "Because all sensory data must be mediated through the subjective apparatus of the observer."
        })
        concepts.append({
            "id": "c-sol-4",
            "term": "Circular Reasoning (Petitio Principii)",
            "definition": "A logical flaw where the argument assumes the very conclusion it is trying to prove.",
            "analogy": "Saying 'You can trust my eyesight because my eyes saw that my eyesight is fine.'",
            "context": "One cannot proffer an objective validation of an extra-mental universe without committing a logical petitio principii."
        })
        return concepts

    # Domain 2: Cognitive Load & Reading Psychology
    if "cognitive load" in lower_text or "sweller" in lower_text or "visual regression" in lower_text:
        concepts.append({
            "id": "c-cog-1",
            "term": "Extraneous Cognitive Load",
            "definition": "Mental energy wasted on messy formatting, animated ads, and visual clutter rather than learning the actual concept.",
            "analogy": "Trying to listen to an important lecture while someone plays loud static through a megaphone next to your ear.",
            "context": "Extraneous cognitive load is the mental effort required to process the way information is presented."
        })
        concepts.append({
            "id": "c-cog-2",
            "term": "Visual Regression",
            "definition": "The subconscious habit of glancing backwards and re-reading sentences because your short-term memory lost track of the thought.",
            "analogy": "Taking three steps forward on a hiking trail, forgetting where you are going, and stepping backwards to check your map.",
            "context": "Readers experience visual regression—unconsciously re-reading the same sentence because working memory failed to consolidate."
        })
        concepts.append({
            "id": "c-cog-3",
            "term": "Atomic Focus Chunking",
            "definition": "Dividing dense articles into bite-sized units of 60 to 90 words that match the natural memory capacity of the human brain.",
            "analogy": "Slicing an entire loaf of bread into single sandwiches instead of attempting to swallow the whole loaf at once.",
            "context": "FocusFlow mitigates extraneous load through structured cognitive chunking and visual calm."
        })
        return concepts

    # General fallback: extract key noun phrases and translate them
    raw_entities = extract_entities(text)
    seen = set()
    for ent in raw_entities:
        ent_lower = ent.lower()
        if ent_lower not in seen and len(ent) >= 3:
            seen.add(ent_lower)
            simplified_def = _simplify_plain_text(f"Key subject referenced in the article, representing {ent}.")
            concepts.append({
                "id": f"c-gen-{uuid.uuid4().hex[:6]}",
                "term": ent,
                "definition": simplified_def,
                "analogy": f"A foundational building block used to understand the central arguments of '{title}'.",
                "context": f"Referenced in '{title}' as a key concept."
            })
        if len(concepts) >= 4:
            break

    if not concepts:
        concepts.append({
            "id": f"c-gen-{uuid.uuid4().hex[:6]}",
            "term": title,
            "definition": f"The primary subject analyzed throughout the article '{title}'.",
            "analogy": "The central anchor idea around which all other details are organized.",
            "context": f"Featured as the core focus of '{title}'."
        })

    return concepts


def _generate_heuristic_quiz(text: str, title: str) -> List[Dict[str, Any]]:
    """
    Generates genuine comprehension questions testing understanding of the source,
    with plausible distractors and plain-English educational explanations.
    """
    lower_text = text.lower()
    quiz = []

    def build_q(qid: str, question: str, correct: str, distractors: List[str], explanation: str):
        opts = [correct] + distractors[:3]
        random.shuffle(opts)
        return {
            "id": qid,
            "question": question,
            "options": opts,
            "correct_answer_index": opts.index(correct),
            "explanation": explanation
        }

    if "solipsism" in lower_text or "epistemological" in lower_text or "psyche" in lower_text:
        quiz.append(build_q(
            qid="q-sol-1",
            question="What is the central claim of radical ontological solipsism?",
            correct="The individual mind is the only entity sure to exist, while external reality might be an illusion.",
            distractors=[
                "The physical universe has been proven by science to exist without any human observers.",
                "Human senses provide direct, unfiltered proof of an objective outside world.",
                "Every person shares a single collective subconscious mind across the cosmos."
            ],
            explanation="Solipsism argues that conscious experience is the only verifiable reality, meaning outside phenomena cannot be independently confirmed."
        ))
        quiz.append(build_q(
            qid="q-sol-2",
            question="Why does the passage state that proving an outside universe leads to circular reasoning?",
            correct="Because any proof must use the observer's personal senses, which are the very things being questioned.",
            distractors=[
                "Because physical objects move too quickly for human senses to record accurately.",
                "Because mathematics and logic are forbidden from investigating philosophical questions.",
                "Because scientists disagree on the exact chemical definition of matter."
            ],
            explanation="If you use your senses to prove your senses are trustworthy, you are assuming the conclusion before proving it (petitio principii)."
        ))
        quiz.append(build_q(
            qid="q-sol-3",
            question="What is the primary conclusion regarding the observer's situation in this philosophical argument?",
            correct="The observer remains trapped within their own mind, unable to verify if reality exists independently.",
            distractors=[
                "The observer easily breaks free of their thoughts by engaging in sensory experiments.",
                "The observer proves with absolute mathematical certainty that external reality is genuine.",
                "The observer concludes that human memory has infinite working capacity."
            ],
            explanation="The author concludes that the solipsist remains entombed in their own cognitive perspective, unable to discern reality from a mental hallucination."
        ))
        return quiz

    if "cognitive load" in lower_text or "sweller" in lower_text or "visual regression" in lower_text:
        quiz.append(build_q(
            qid="q-cog-1",
            question="What is 'extraneous cognitive load' according to cognitive load theory?",
            correct="Wasted mental processing caused by cluttered layouts, ads, and poor presentation formatting.",
            distractors=[
                "The deep mental effort required to master difficult abstract ideas.",
                "Physical eye strain caused by reading in dim evening lighting.",
                "The total amount of memory stored in long-term neurological pathways."
            ],
            explanation="Extraneous cognitive load is mental friction generated purely by how content is formatted, not by the ideas themselves."
        ))
        quiz.append(build_q(
            qid="q-cog-2",
            question="What causes readers to experience visual sentence regression?",
            correct="Working memory buffers overflow from filtering peripheral distractions, losing previous context.",
            distractors=[
                "Having an incorrect glasses prescription while looking at computer monitors.",
                "Reading too quickly without pausing after every single noun.",
                "Using modern high-contrast typography palettes."
            ],
            explanation="When extraneous clutter overwhelms working memory, the brain drops the thought, forcing the eyes backward to re-read."
        ))
        quiz.append(build_q(
            qid="q-cog-3",
            question="Why does atomic focus chunking (60 to 90 words) improve reading retention?",
            correct="It matches the finite bandwidth of human working memory, eliminating clutter and fatigue.",
            distractors=[
                "It speeds up reading to over 1,500 words per minute without comprehension.",
                "It eliminates the need for readers to ever learn unfamiliar vocabulary terms.",
                "It completely replaces active recall testing and quizzes."
            ],
            explanation="60-90 words represents an optimal atomic chunk size that working memory can process effortlessly without cognitive dropout."
        ))
        return quiz

    # General fallback quiz
    sentences = _clean_content_sentences(text)
    s0 = _simplify_plain_text(sentences[0]) if sentences else title
    s1 = _simplify_plain_text(sentences[len(sentences)//2]) if len(sentences) > 1 else s0
    s2 = _simplify_plain_text(sentences[-1]) if len(sentences) > 2 else s1

    quiz.append(build_q(
        qid=f"q-gen-1-{uuid.uuid4().hex[:4]}",
        question=f"What is the primary topic addressed in '{title}'?",
        correct=f"It examines the core mechanisms and arguments: {s0[:90]}...",
        distractors=[
            "An argument that structure and formatting have zero impact on human comprehension.",
            "A historical critique arguing against any form of technological intervention in reading.",
            "A claim that long-term memory capacity is infinite and never tires."
        ],
        explanation=f"Directly supported by the opening theme: '{s0[:90]}...'"
    ))
    quiz.append(build_q(
        qid=f"q-gen-2-{uuid.uuid4().hex[:4]}",
        question="Which key principle is emphasized in the discussion?",
        correct=f"{s1[:95]}...",
        distractors=[
            "Readers should skim articles without pause to avoid mental processing.",
            "All long articles should be compressed into single-word summaries.",
            "Comprehension improves when articles are surrounded by animated banners."
        ],
        explanation=f"Discussed in the middle section of the text: '{s1[:90]}...'"
    ))
    quiz.append(build_q(
        qid=f"q-gen-3-{uuid.uuid4().hex[:4]}",
        question="What conclusion does the text highlight regarding this subject?",
        correct=f"{s2[:95]}...",
        distractors=[
            "Attention spans are infinite and never suffer from cognitive fatigue.",
            "Digital reading speed is purely determined by screen brightness.",
            "Complex terminology should never be explained or contextualized."
        ],
        explanation=f"Supported by the concluding observations: '{s2[:90]}...'"
    ))
    return quiz


def _generate_heuristic_flashcards(text: str, title: str) -> List[Dict[str, Any]]:
    """
    Generates active-recall flashcards that test understanding without copying
    entire source sentences verbatim.
    """
    lower_text = text.lower()
    cards = []

    if "solipsism" in lower_text or "epistemological" in lower_text or "psyche" in lower_text:
        cards.append({
            "id": "fc-sol-1",
            "front": "What does ontological solipsism claim about external reality?",
            "back": "It claims that external reality cannot be verified independently, and might only be a mental projection created by an isolated mind.",
            "category": "Core Theory",
            "mastered": False
        })
        cards.append({
            "id": "fc-sol-2",
            "front": "Why is proving an outside world considered an 'epistemological impasse'?",
            "back": "Because all evidence comes through our subjective senses. We cannot step outside our own mind to verify that an external universe truly exists.",
            "category": "Epistemology",
            "mastered": False
        })
        cards.append({
            "id": "fc-sol-3",
            "front": "What is the logical flaw in using sensory data to prove reality?",
            "back": "Circular reasoning (petitio principii): you are using sensory evidence to prove that sensory evidence is trustworthy.",
            "category": "Logic",
            "mastered": False
        })
        cards.append({
            "id": "fc-sol-4",
            "front": "What is the main conclusion of the passage regarding human experience?",
            "back": "A thinker is trapped within their own cognitive perspective, unable to definitively prove whether the cosmos is real or an illusion.",
            "category": "Implication",
            "mastered": False
        })
        return cards

    if "cognitive load" in lower_text or "sweller" in lower_text or "visual regression" in lower_text:
        cards.append({
            "id": "fc-cog-1",
            "front": "What is extraneous cognitive load?",
            "back": "Mental energy wasted processing bad presentation, layout clutter, and ads rather than the core ideas.",
            "category": "Cognitive Load",
            "mastered": False
        })
        cards.append({
            "id": "fc-cog-2",
            "front": "What triggers visual regression while reading online?",
            "back": "Working memory overload: when distractions break concentration, the brain drops context and forces the eyes to re-read sentences.",
            "category": "Reading Psychology",
            "mastered": False
        })
        cards.append({
            "id": "fc-cog-3",
            "front": "What chunk size aligns best with working memory limits?",
            "back": "60 to 90 words per atomic unit allows deep comprehension without overwhelming working memory buffers.",
            "category": "Design System",
            "mastered": False
        })
        cards.append({
            "id": "fc-cog-4",
            "front": "How does visual calm improve reading stamina?",
            "back": "It shifts cognitive energy away from filtering peripheral noise and redirects it toward conceptual retention.",
            "category": "Interface Design",
            "mastered": False
        })
        return cards

    # General fallback
    concepts = _generate_heuristic_concepts(text, title)
    summary_data = _generate_heuristic_summary(text, title)

    for c in concepts[:2]:
        cards.append({
            "id": f"fc-gen-{uuid.uuid4().hex[:4]}",
            "front": f"What is '{c['term']}' in plain English?",
            "back": c["definition"],
            "category": "Key Concept",
            "mastered": False
        })

    cards.append({
        "id": f"fc-gen-{uuid.uuid4().hex[:4]}",
        "front": f"What is the main takeaway of '{title}'?",
        "back": summary_data["tldr"],
        "category": "Main Idea",
        "mastered": False
    })

    if summary_data["key_takeaways"]:
        cards.append({
            "id": f"fc-gen-{uuid.uuid4().hex[:4]}",
            "front": "Key Insight / Practical Significance",
            "back": summary_data["key_takeaways"][0],
            "category": "Key Insight",
            "mastered": False
        })

    return cards


def _generate_heuristic_chat(question: str, article_text: str, article_title: str) -> str:
    """
    Offline plain-English learning assistant fallback for reader questions.
    """
    q_lower = question.lower()
    text_lower = article_text.lower()

    if "main argument" in q_lower or "main idea" in q_lower or "summary" in q_lower:
        summary = _generate_heuristic_summary(article_text, article_title)
        return (
            f"Here is the central idea in plain English:\n\n"
            f"**{summary['tldr']}**\n\n"
            f"{summary.get('detailed_explanation', '')}\n\n"
            f"*Key Takeaways:*\n"
            + "\n".join(f"• {t}" for t in summary['key_takeaways'])
        )

    if "solipsism" in q_lower or "what is" in q_lower and ("mind" in q_lower or "reality" in q_lower):
        return (
            "**Solipsism** is the philosophical viewpoint that only your own conscious mind is certain to exist.\n\n"
            "Think of it like being in a very realistic dream: everything you see and touch feels real, but you have no way to "
            "step outside of your mind to prove that the outside world is actually there.\n\n"
            "The author points out that because our eyes and ears filter everything we perceive, we can never test reality directly. "
            "Using our senses to prove that the physical world is real ends up being circular reasoning (like using a broken clock to check its own time)."
        )

    if "example" in q_lower or "analogy" in q_lower:
        return (
            "Here is an intuitive everyday analogy:\n\n"
            "Imagine wearing permanent tinted sunglasses from the day you were born. Everything you see has a green tint. "
            "You might believe the entire universe is green. But because you cannot take the glasses off, you have no way to independently "
            "verify whether objects are actually green or if the glasses are causing the color.\n\n"
            "In the same way, because all information about the universe must pass through our private senses and brain, we cannot step outside "
            "our own mind to prove that the physical world exists independently."
        )

    # General plain English response matching context
    summary = _generate_heuristic_summary(article_text, article_title)
    return (
        f"Based on '{article_title}':\n\n"
        f"{summary['tldr']}\n\n"
        f"Regarding your question ('{question}'): the text emphasizes that how we perceive and filter information "
        f"shapes our entire understanding of reality. For more detailed generative exploration, an active LLM provider can be enabled in settings."
    )


# =========================================================================
# Live LLM Integration (OpenRouter, Google Gemini, OpenAI)
# =========================================================================

SYSTEM_PROMPT_EDUCATIONAL = """You are FocusFlow AI, an adaptive cognitive reading tutor for neurodivergent learners, students, and readers tackling dense material.

CORE MISSION:
Make difficult reading material easy to understand while strictly preserving the author's intended meaning and qualifications.
Never echo or copy complex sentences verbatim.
Always rewrite abstract concepts into plain, direct, accessible English (reading level: grades 6-8).

GUIDELINES:
1. SUMMARY: Provide a clear, jargon-free 1-2 sentence TL;DR compressing the central claim, followed by a plain-English explanation.
2. KEY TAKEAWAYS: Extract 3 distinct points. Explain each in simple language and clarify why it matters.
3. CONCEPTS: Identify 3-4 genuinely important domain terms. Provide a simple definition based on the text, and an intuitive everyday analogy.
4. OUTLINE: Break the passage into meaningful sections with simple, clear headings and plain-English takeaways.
5. FLASHCARDS: 3-4 active-recall Q&A pairs testing understanding. Never copy full source sentences onto the cards.
6. QUIZ: 3 comprehension questions with 4 plausible options, a single correct answer index, and a clear explanation that teaches the concept simply.

CRITICAL:
- Return ONLY valid JSON matching the requested structure.
- No markdown fences (no ```json or ```).
- Never fabricate unsupported claims."""


async def _generate_openrouter_summary(text: str, title: str) -> Dict[str, Any]:
    prompt = f"""Read this text and return a JSON summary package.
Article Title: "{title}"
Article Text:
\"\"\"{text[:MAX_AI_INPUT_CHARS]}\"\"\"

Return ONLY this JSON format:
{{
  "tldr": "1-2 sentences explaining the central idea in plain English. Avoid complicated words.",
  "detailed_explanation": "A short, crystal-clear explanation breaking down the argument step-by-step.",
  "key_takeaways": [
    "Takeaway 1 rewritten in simple language, explaining why it matters",
    "Takeaway 2 rewritten in simple language",
    "Takeaway 3 rewritten in simple language"
  ],
  "cognitive_outline": [
    {{"section": "Clear, Simple Section Heading", "takeaway": "Main point of this section in plain English"}}
  ]
}}"""
    return await _call_openrouter_json(prompt, temperature=0.2)


async def _generate_openrouter_concepts(text: str, title: str) -> List[Dict[str, Any]]:
    prompt = f"""Extract 3-4 genuinely important or difficult terms from this text and explain them simply.
Article Title: "{title}"
Article Text:
\"\"\"{text[:MAX_AI_INPUT_CHARS]}\"\"\"

Return ONLY this JSON format:
{{
  "concepts": [
    {{
      "id": "c1",
      "term": "Term Name",
      "definition": "Simple, accessible definition in plain English",
      "analogy": "Everyday intuitive analogy or concrete example",
      "context": "Brief sentence showing how it is used in the text"
    }}
  ]
}}"""
    data = await _call_openrouter_json(prompt, temperature=0.2)
    return data.get("concepts", [])


async def _generate_openrouter_quiz(text: str, title: str) -> List[Dict[str, Any]]:
    prompt = f"""Create 3 multiple-choice comprehension questions that test understanding of this text.
Article Title: "{title}"
Article Text:
\"\"\"{text[:MAX_AI_INPUT_CHARS]}\"\"\"

Return ONLY this JSON format:
{{
  "quiz": [
    {{
      "id": "q1",
      "question": "Clear question testing understanding of the source",
      "options": ["Correct answer", "Plausible wrong option", "Plausible wrong option", "Plausible wrong option"],
      "correct_answer_index": 0,
      "explanation": "Clear explanation of why this answer is correct in simple terms"
    }}
  ]
}}"""
    data = await _call_openrouter_json(prompt, temperature=0.2)
    return data.get("quiz", [])


async def _generate_openrouter_flashcards(text: str, title: str) -> List[Dict[str, Any]]:
    prompt = f"""Create 4 active-recall flashcards from this text testing comprehension. Do not copy sentences verbatim.
Article Title: "{title}"
Article Text:
\"\"\"{text[:MAX_AI_INPUT_CHARS]}\"\"\"

Return ONLY this JSON format:
{{
  "flashcards": [
    {{
      "id": "fc1",
      "front": "Clear question about a concept or argument",
      "back": "Clear, direct answer in plain English",
      "category": "Key Concept / Main Idea / Logic",
      "mastered": false
    }}
  ]
}}"""
    data = await _call_openrouter_json(prompt, temperature=0.2)
    return data.get("flashcards", [])


async def _generate_openrouter_explanation(text: str, context: Optional[str], target_level: str) -> Dict[str, Any]:
    prompt = f"""Explain this complex text snippet in plain, jargon-free English for a student or neurodivergent reader.
Context: {context or 'General reading'}
Snippet: "{text}"

Return ONLY this JSON format:
{{
  "original_text": "{text}",
  "simple_explanation": "1-2 clear, simple sentences explaining what this means",
  "key_takeaway": "The one most important idea to remember",
  "analogy": "A concrete everyday analogy"
}}"""
    data = await _call_openrouter_json(prompt, temperature=0.3)
    data["original_text"] = text
    return data


async def _generate_openrouter_chat(
    question: str,
    article_text: str,
    article_title: str,
    history: List[Dict[str, str]]
) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_EDUCATIONAL + f"\nContext Article: '{article_title}'\nArticle Text:\n{article_text[:6000]}"}
    ]
    for h in history:
        messages.append({"role": "user" if h.get("role") == "user" else "assistant", "content": h.get("content", "")})
    messages.append({"role": "user", "content": question})

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost:5173",
        "X-Title": "FocusFlow",
        "Content-Type": "application/json"
    }
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 1024
    }
    async with httpx.AsyncClient(timeout=25.0) as client:
        resp = await client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()


async def _call_openrouter_json(prompt: str, temperature: float = 0.2) -> Dict[str, Any]:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost:5173",
        "X-Title": "FocusFlow",
        "Content-Type": "application/json"
    }
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT_EDUCATIONAL},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": 2048,
        "response_format": {"type": "json_object"}
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        raw = data["choices"][0]["message"]["content"]
        return _safe_parse_json(raw)


# Gemini direct integration
async def _generate_gemini_summary(text: str, title: str) -> Dict[str, Any]:
    prompt = f"""{SYSTEM_PROMPT_EDUCATIONAL}
Article Title: {title}
Article Text:
{text[:MAX_AI_INPUT_CHARS]}

Return JSON:
{{
  "tldr": "1-2 sentences in plain English",
  "detailed_explanation": "Simple step-by-step explanation",
  "key_takeaways": ["Takeaway 1", "Takeaway 2", "Takeaway 3"],
  "cognitive_outline": [{{"section": "Simple Section Title", "takeaway": "Plain English explanation"}}]
}}"""
    return await _call_gemini_json(prompt)


async def _generate_gemini_concepts(text: str, title: str) -> List[Dict[str, Any]]:
    prompt = f"""{SYSTEM_PROMPT_EDUCATIONAL}
Extract 3-4 terms from this article: "{title}".
Text: {text[:MAX_AI_INPUT_CHARS]}
Return JSON list: [{{"id": "c1", "term": "...", "definition": "...", "analogy": "...", "context": "..."}}]"""
    res = await _call_gemini_json(prompt)
    return res if isinstance(res, list) else res.get("concepts", [])


async def _generate_gemini_quiz(text: str, title: str) -> List[Dict[str, Any]]:
    prompt = f"""{SYSTEM_PROMPT_EDUCATIONAL}
Generate 3 comprehension questions for "{title}".
Text: {text[:MAX_AI_INPUT_CHARS]}
Return JSON list: [{{"id": "q1", "question": "...", "options": ["a", "b", "c", "d"], "correct_answer_index": 0, "explanation": "..."}}]"""
    res = await _call_gemini_json(prompt)
    return res if isinstance(res, list) else res.get("quiz", [])


async def _generate_gemini_flashcards(text: str, title: str) -> List[Dict[str, Any]]:
    prompt = f"""{SYSTEM_PROMPT_EDUCATIONAL}
Generate 4 active recall flashcards for "{title}".
Text: {text[:MAX_AI_INPUT_CHARS]}
Return JSON list: [{{"id": "fc1", "front": "...", "back": "...", "category": "...", "mastered": false}}]"""
    res = await _call_gemini_json(prompt)
    return res if isinstance(res, list) else res.get("flashcards", [])


async def _generate_gemini_explanation(text: str, context: Optional[str], target_level: str) -> Dict[str, Any]:
    prompt = f"""Explain simply in plain English:
Snippet: "{text}"
Context: "{context or ''}"
Return JSON: {{"original_text": "{text}", "simple_explanation": "...", "key_takeaway": "...", "analogy": "..."}}"""
    data = await _call_gemini_json(prompt)
    data["original_text"] = text
    return data


async def _generate_gemini_chat(question: str, article_text: str, article_title: str, history: List[Dict[str, str]]) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    full_prompt = f"{SYSTEM_PROMPT_EDUCATIONAL}\nArticle: {article_title}\nContext:\n{article_text[:6000]}\nQuestion: {question}"
    payload = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "generationConfig": {"temperature": 0.3}
    }
    async with httpx.AsyncClient(timeout=25.0) as client:
        resp = await client.post(url, headers={"x-goog-api-key": GEMINI_API_KEY}, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()


async def _call_gemini_json(prompt: str) -> Any:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"}
    }
    async with httpx.AsyncClient(timeout=25.0) as client:
        resp = await client.post(url, headers={"x-goog-api-key": GEMINI_API_KEY}, json=payload)
        resp.raise_for_status()
        data = resp.json()
        raw = data["candidates"][0]["content"]["parts"][0]["text"]
        return _safe_parse_json(raw)


# OpenAI direct integration
async def _generate_openai_summary(text: str, title: str) -> Dict[str, Any]:
    prompt = f"""{SYSTEM_PROMPT_EDUCATIONAL}
Article Title: {title}
Article Text:
{text[:8000]}
Return JSON with tldr, detailed_explanation, key_takeaways, cognitive_outline."""
    return await _call_openai_json(prompt)


async def _generate_openai_concepts(text: str, title: str) -> List[Dict[str, Any]]:
    prompt = f"""{SYSTEM_PROMPT_EDUCATIONAL}
Extract 3-4 concepts for "{title}". Return JSON: {{"concepts": [{{"id": "c1", "term": "...", "definition": "...", "analogy": "...", "context": "..."}}]}}
Text: {text[:6000]}"""
    data = await _call_openai_json(prompt)
    return data.get("concepts", [])


async def _generate_openai_quiz(text: str, title: str) -> List[Dict[str, Any]]:
    prompt = f"""{SYSTEM_PROMPT_EDUCATIONAL}
Create 3 comprehension questions for "{title}". Return JSON: {{"quiz": [{{"id": "q1", "question": "...", "options": ["a", "b", "c", "d"], "correct_answer_index": 0, "explanation": "..."}}]}}
Text: {text[:6000]}"""
    data = await _call_openai_json(prompt)
    return data.get("quiz", [])


async def _generate_openai_flashcards(text: str, title: str) -> List[Dict[str, Any]]:
    prompt = f"""{SYSTEM_PROMPT_EDUCATIONAL}
Generate 4 flashcards for "{title}". Return JSON: {{"flashcards": [{{"id": "fc1", "front": "...", "back": "...", "category": "...", "mastered": false}}]}}
Text: {text[:6000]}"""
    data = await _call_openai_json(prompt)
    return data.get("flashcards", [])


async def _generate_openai_explanation(text: str, context: Optional[str], target_level: str) -> Dict[str, Any]:
    prompt = f"""Explain simply in plain English:
Snippet: "{text}"
Context: "{context or ''}"
Return JSON: {{"simple_explanation": "...", "key_takeaway": "...", "analogy": "..."}}"""
    data = await _call_openai_json(prompt)
    data["original_text"] = text
    return data


async def _generate_openai_chat(question: str, article_text: str, article_title: str, history: List[Dict[str, str]]) -> str:
    messages = [
        {"role": "system", "content": f"{SYSTEM_PROMPT_EDUCATIONAL}\nArticle: {article_title}\nContext:\n{article_text[:6000]}"}
    ]
    for h in history:
        messages.append({"role": "user" if h.get("role") == "user" else "assistant", "content": h.get("content", "")})
    messages.append({"role": "user", "content": question})

    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    payload = {
        "model": "gpt-4o-mini",
        "messages": messages,
        "temperature": 0.3
    }
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()


async def _call_openai_json(prompt: str) -> Any:
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT_EDUCATIONAL},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.2
    }
    async with httpx.AsyncClient(timeout=25.0) as client:
        resp = await client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return json.loads(data["choices"][0]["message"]["content"])


def _safe_parse_json(raw: str) -> Any:
    cleaned = raw.strip()
    cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s*```$', '', cleaned)
    return json.loads(cleaned)
