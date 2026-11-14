import re
import uuid
import httpx
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Tuple
from urllib.parse import urlparse

def count_syllables(word: str) -> int:
    word = word.lower().strip(".:;?!'\"")
    if not word:
        return 0
    if len(word) <= 3:
        return 1
    word = re.sub(r'(?:[^laeiouy]|ed|es|e)$', '', word)
    word = re.sub(r'^y', '', word)
    matches = re.findall(r'[aeiouy]{1,2}', word)
    return max(1, len(matches))

def calculate_readability(text: str) -> Tuple[float, str]:
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    words = [w for w in re.findall(r'\b[A-Za-z]+\b', text)]
    if not sentences or not words:
        return 70.0, "Standard"
    
    total_words = len(words)
    total_sentences = max(1, len(sentences))
    total_syllables = sum(count_syllables(w) for w in words)

    # Flesch Reading Ease Formula
    score = 206.835 - (1.015 * (total_words / total_sentences)) - (84.6 * (total_syllables / total_words))
    score = max(0.0, min(100.0, round(score, 1)))

    if score >= 70:
        rating = "Accessible"
    elif score >= 50:
        rating = "Standard"
    else:
        rating = "Dense / Academic"
    
    return score, rating

def extract_entities(text: str) -> List[str]:
    # Extract capitalized terms, prominent acronyms, or numbers
    acronyms = set(re.findall(r'\b[A-Z]{2,6}\b', text))
    proper_nouns = set(re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text))
    stopwords = {
        "The", "This", "That", "When", "Where", "Why", "How", "There", "Here",
        "With", "After", "Before", "While", "In", "On", "At", "For", "To",
        "From", "And", "Or", "But", "If", "What", "Because", "However", "Therefore"
    }
    filtered = [w for w in (proper_nouns | acronyms) if w not in stopwords and len(w) > 2]
    return list(filtered)[:5]

def extract_semantic_highlights(text: str) -> List[Dict[str, Any]]:
    """
    Deterministic semantic highlight extractor.
    Identifies:
    1. Key Concepts: Terminology & capitalized constructs
    2. Definitions: Sentences containing 'is defined as', 'refers to', 'is a', etc.
    3. Supporting Details: Statistics, percentages, years, numbers, and citations
    """
    highlights = []
    seen_spans = set()

    # 1. Definitions (Regex matching definition patterns)
    def_patterns = [
        r'([A-Z][a-zA-Z\s]{2,30})\s+(?:is defined as|refers to|represents|means)\s+([^.!?]+[.!?])',
        r'([A-Z][a-zA-Z\s]{2,30})\s+(?:is\s+a\s+[a-z\s]+(?:that|which|designed to))\s+([^.!?]+[.!?])'
    ]
    for pattern in def_patterns:
        for match in re.finditer(pattern, text):
            start = match.start()
            end = match.end()
            span_key = (start, end)
            if span_key not in seen_spans:
                seen_spans.add(span_key)
                highlights.append({
                    "id": f"hl-def-{uuid.uuid4().hex[:6]}",
                    "category": "definition",
                    "text": match.group(0).strip(),
                    "start_char": start,
                    "end_char": end,
                    "label": "Definition",
                    "explanation": f"Defines '{match.group(1).strip()}'"
                })

    # 2. Supporting Details / Empirical Data (percentages, statistics, time spans, studies)
    evidence_patterns = [
        r'\b(?:\d+(?:\.\d+)?%|\$\d+(?:\.\d+)?|\d+\s*(?:percent|million|billion|thousand|users|seconds|minutes|words|participants))\b',
        r'\b(?:in\s+the\s+late\s+\d{4}s|in\s+\d{4}|from\s+\d{4}\s+to\s+\d{4})\b',
        r'(?:studies|research|neuroimaging|data)\s+(?:show|confirm|demonstrate|indicate|reveal)[^.!?]+'
    ]
    for pattern in evidence_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            start = match.start()
            end = match.end()
            # Avoid duplicate overlapping spans
            if not any(s <= start and end <= e for (s, e) in seen_spans):
                seen_spans.add((start, end))
                highlights.append({
                    "id": f"hl-evi-{uuid.uuid4().hex[:6]}",
                    "category": "evidence",
                    "text": match.group(0).strip(),
                    "start_char": start,
                    "end_char": end,
                    "label": "Supporting Detail / Data",
                    "explanation": "Empirical data, metric, or study reference"
                })

    # 3. Key Concepts (Important terminology)
    concept_candidates = extract_entities(text)
    for concept in concept_candidates:
        if len(concept) < 4:
            continue
        # Find matches of the whole word
        for match in re.finditer(r'\b' + re.escape(concept) + r'\b', text):
            start = match.start()
            end = match.end()
            if not any(s <= start and end <= e for (s, e) in seen_spans):
                seen_spans.add((start, end))
                highlights.append({
                    "id": f"hl-con-{uuid.uuid4().hex[:6]}",
                    "category": "concept",
                    "text": match.group(0),
                    "start_char": start,
                    "end_char": end,
                    "label": "Key Concept",
                    "explanation": f"Core term: {concept}"
                })
                break # Only highlight first 1-2 occurrences to prevent clutter

    # Sort by appearance in text
    highlights.sort(key=lambda x: x["start_char"])
    return highlights

def predict_cognitive_difficulty_safely(text: str) -> str:
    """
    Uses the trained ACLI ML model if loaded and ready;
    otherwise falls back gracefully to deterministic word-count heuristic.
    """
    try:
        from .ml.service import get_inference_service
        service = get_inference_service()
        if service.is_ready():
            res = service.predict(text)
            if res.get("status") == "success":
                return res.get("predicted_difficulty", "Medium")
    except Exception:
        pass

    c_words = len(text.split())
    return "Hard" if c_words > 90 else ("Easy" if c_words < 45 else "Medium")


def split_into_cognitive_chunks(text: str, max_words_per_chunk: int = 80) -> List[Dict[str, Any]]:
    """
    Splits text into atomic reading chunks respecting:
    - Paragraph breaks (\n\n)
    - Headings (##, ###)
    - Sentence boundaries (never splits within a sentence)
    - Configurable target chunk size (max_words_per_chunk)
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    chunk_index = 0
    seen_chunk_texts = set()

    for para in paragraphs:
        # Preserve standalone headings as concise thematic intro chunks
        if para.startswith("#") or para.startswith("==") or (len(para.split()) < 8 and para.isupper()):
            c_words = len(para.split())
            norm_para = re.sub(r'\s+', ' ', para).lower().strip()
            if norm_para not in seen_chunk_texts:
                seen_chunk_texts.add(norm_para)
                chunks.append({
                    "id": f"chunk-{uuid.uuid4().hex[:8]}",
                    "index": chunk_index,
                    "text": para,
                    "key_takeaway": para.lstrip("#").strip(),
                    "word_count": c_words,
                    "estimated_seconds": max(5, round((c_words / 200) * 60)),
                    "entities": extract_entities(para),
                    "cognitive_difficulty": "easy"
                })
                chunk_index += 1
            continue

        # Split paragraph into complete sentences using regex lookbehind
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', para) if s.strip()]
        if not sentences:
            continue

        current_sentences = []
        current_words = 0

        for sentence in sentences:
            words = sentence.split()
            word_count = len(words)

            # Check if adding this sentence exceeds target chunk size
            if current_words + word_count > (max_words_per_chunk + 15) and current_sentences:
                # Flush current chunk
                chunk_text = " ".join(current_sentences)
                norm_chunk = re.sub(r'\s+', ' ', chunk_text).lower().strip()
                if norm_chunk not in seen_chunk_texts:
                    seen_chunk_texts.add(norm_chunk)
                    c_words = len(chunk_text.split())
                    chunks.append({
                        "id": f"chunk-{uuid.uuid4().hex[:8]}",
                        "index": chunk_index,
                        "text": chunk_text,
                        "key_takeaway": current_sentences[0] if current_sentences else chunk_text[:60] + "...",
                        "word_count": c_words,
                        "estimated_seconds": max(10, round((c_words / 200) * 60)),
                        "entities": extract_entities(chunk_text),
                        "cognitive_difficulty": predict_cognitive_difficulty_safely(chunk_text)
                    })
                    chunk_index += 1
                current_sentences = [sentence]
                current_words = word_count
            else:
                current_sentences.append(sentence)
                current_words += word_count

        if current_sentences:
            chunk_text = " ".join(current_sentences)
            norm_chunk = re.sub(r'\s+', ' ', chunk_text).lower().strip()
            if norm_chunk not in seen_chunk_texts:
                seen_chunk_texts.add(norm_chunk)
                c_words = len(chunk_text.split())
                chunks.append({
                    "id": f"chunk-{uuid.uuid4().hex[:8]}",
                    "index": chunk_index,
                    "text": chunk_text,
                    "key_takeaway": current_sentences[0] if current_sentences else chunk_text[:60] + "...",
                    "word_count": c_words,
                    "estimated_seconds": max(10, round((c_words / 200) * 60)),
                    "entities": extract_entities(chunk_text),
                    "cognitive_difficulty": predict_cognitive_difficulty_safely(chunk_text)
                })
                chunk_index += 1

    return chunks

async def fetch_article_from_url(url: str, chunk_size_words: int = 80) -> Dict[str, Any]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) FocusFlowReader/1.0"
    }
    async with httpx.AsyncClient(follow_redirects=True, timeout=12.0) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        html = response.text
    return parse_html_to_article(html, url=url, chunk_size_words=chunk_size_words)

def parse_html_to_article(html: str, url: str = None, fallback_title: str = None, chunk_size_words: int = 80) -> Dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")

    # Remove script, style, nav, footer, ads, header tags
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "svg", "form", "iframe"]):
        tag.decompose()

    # Extract title
    title = ""
    if soup.find("h1"):
        title = soup.find("h1").get_text(strip=True)
    elif soup.title:
        title = soup.title.get_text(strip=True)
    if not title and fallback_title:
        title = fallback_title
    if not title:
        title = "Extracted Article"

    # Extract Author / Byline
    author = "Web Author"
    author_meta = soup.find("meta", {"name": re.compile(r"author|creator|byline", re.I)})
    if author_meta and author_meta.get("content"):
        author = author_meta["content"]
    else:
        author_elem = soup.find(class_=re.compile(r"author|byline|writer", re.I))
        if author_elem:
            author = author_elem.get_text(strip=True)[:50]

    # Extract body content paragraphs
    paragraphs = []
    seen_paragraphs = set()
    main_container = soup.find("article") or soup.find("main") or soup.find(id=re.compile(r"content|article|main", re.I)) or soup.body
    if main_container:
        for elem in main_container.find_all(["p", "h2", "h3", "blockquote"]):
            # Skip paragraph tag if it's already inside a blockquote to prevent duplication
            if elem.name == "p" and elem.find_parent("blockquote"):
                continue
            text = elem.get_text(separator=" ", strip=True)
            norm = re.sub(r'\s+', ' ', text).lower().strip()
            if len(text.split()) > 4 and norm not in seen_paragraphs:
                seen_paragraphs.add(norm)
                paragraphs.append(text)
    
    full_text = "\n\n".join(paragraphs) if paragraphs else (soup.get_text(separator="\n\n", strip=True) if soup.body else "")

    domain = urlparse(url).netloc if url else "Pasted Source"
    domain = domain.replace("www.", "") if domain else "Source"

    return process_raw_text(full_text, title=title, author=author, source_url=url, domain=domain, chunk_size_words=chunk_size_words)

def process_raw_text(
    text: str,
    title: str = "Focus Article",
    author: str = "Unknown Author",
    source_url: str = None,
    domain: str = "Direct Entry",
    chunk_size_words: int = 80
) -> Dict[str, Any]:
    # Clean redundant whitespace
    text = re.sub(r'\r\n|\r', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    
    words = text.split()
    word_count = len(words)
    reading_time = max(1, round(word_count / 200))

    score, rating = calculate_readability(text)
    chunks = split_into_cognitive_chunks(text, max_words_per_chunk=chunk_size_words)
    highlights = extract_semantic_highlights(text)

    article_id = f"art-{uuid.uuid4().hex[:10]}"

    return {
        "id": article_id,
        "title": title,
        "author": author,
        "source_url": source_url,
        "domain": domain,
        "raw_content": text,
        "reading_time_minutes": reading_time,
        "word_count": word_count,
        "flesch_score": score,
        "cognitive_rating": rating,
        "chunks": chunks,
        "highlights": highlights,
        "progress_percent": 0,
        "current_chunk_index": 0,
        "is_favorite": False,
        "is_completed": False
    }
