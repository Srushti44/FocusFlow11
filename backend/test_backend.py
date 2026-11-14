"""
Test Suite for FocusFlow FastAPI Backend.
Verifies all endpoints, schemas, chunking logic, semantic highlighting,
and deterministic AI fallbacks.
"""

import sys
import os

# Ensure backend can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

SAMPLE_ARTICLE = """Cognitive load theory posits that our working memory has a strictly finite capacity. When human readers encounter modern digital articles filled with animated advertisements and unbroken blocks of dense text, our cognitive architecture suffers from extraneous load.

Extraneous cognitive load is defined as the mental effort required to process the way information is presented, rather than the core information itself. When extraneous load exceeds our working threshold, attention fractures. Neuroimaging studies confirm that 80% of readers experience visual regression when reading on screens.

FocusFlow mitigates extraneous load through structured cognitive chunking and visual calm. By isolating paragraphs into atomic 60 to 90 word units, the reader's visual field remains uncluttered."""


def run_tests():
    print("=" * 65)
    print("FOCUSFLOW FASTAPI BACKEND VERIFICATION")
    print("=" * 65)

    # 1. Health check
    print("\n[1] Testing GET /api/health...")
    r = client.get("/api/health")
    assert r.status_code == 200, f"Health check failed: {r.text}"
    health = r.json()
    print("    Health:", health)
    assert health["status"] == "healthy"
    assert "ai_provider" in health
    print("    --> Health check PASSED.")

    # 2. Chunking endpoint
    print("\n[2] Testing POST /api/chunk with configurable chunk size (60 words)...")
    r = client.post("/api/chunk", json={
        "text": SAMPLE_ARTICLE,
        "chunk_size_words": 60
    })
    assert r.status_code == 200, f"Chunking failed: {r.text}"
    chunk_data = r.json()
    print(f"    Chunks generated: {chunk_data['total_chunks']} | Word count: {chunk_data['word_count']} | Readability: {chunk_data['cognitive_rating']}")
    assert chunk_data["total_chunks"] >= 3
    assert len(chunk_data["chunks"]) == chunk_data["total_chunks"]
    # Verify first chunk doesn't split sentences
    c0 = chunk_data["chunks"][0]["text"]
    assert c0.endswith(".") or c0.endswith("!") or c0.endswith("?"), "Chunk ended with split sentence!"
    print("    --> Chunking test PASSED.")

    # 3. Text explanation endpoint
    print("\n[3] Testing POST /api/explain...")
    r = client.post("/api/explain", json={
        "text": "Extraneous cognitive load is the mental effort required to process the presentation format.",
        "context": "Cognitive Load Theory in digital reading."
    })
    assert r.status_code == 200, f"Explain failed: {r.text}"
    exp_data = r.json()
    print("    Simple explanation:", exp_data["simple_explanation"])
    print("    Analogy:", exp_data.get("analogy"))
    assert "simple_explanation" in exp_data
    assert exp_data["provider"] in ["deterministic_nlp", "gemini", "openai"]
    print("    --> Text explanation test PASSED.")

    # 4. Semantic highlighting endpoint
    print("\n[4] Testing POST /api/highlights...")
    r = client.post("/api/highlights", json={
        "text": SAMPLE_ARTICLE,
        "article_title": "Cognitive Load Theory"
    })
    assert r.status_code == 200, f"Highlights failed: {r.text}"
    hl_data = r.json()
    print(f"    Highlights detected: {hl_data['total_highlights']}")
    categories = [h["category"] for h in hl_data["highlights"]]
    print("    Categories found:", set(categories))
    assert hl_data["total_highlights"] > 0
    # Verify definition was extracted
    assert any(h["category"] == "definition" for h in hl_data["highlights"]), "Definition pattern not detected"
    print("    --> Semantic highlights test PASSED.")

    # 5. Summary endpoint
    print("\n[5] Testing POST /api/summary...")
    r = client.post("/api/summary", json={
        "text": SAMPLE_ARTICLE,
        "title": "Cognitive Load Theory"
    })
    assert r.status_code == 200, f"Summary failed: {r.text}"
    sum_data = r.json()
    print("    TL;DR:", sum_data.get("tldr"))
    print("    Takeaways count:", len(sum_data.get("key_takeaways", [])))
    assert "tldr" in sum_data
    assert len(sum_data["key_takeaways"]) > 0
    print("    --> Summary test PASSED.")

    # 6. Quiz endpoint
    print("\n[6] Testing POST /api/quiz...")
    r = client.post("/api/quiz", json={
        "text": SAMPLE_ARTICLE,
        "title": "Cognitive Load Theory"
    })
    assert r.status_code == 200, f"Quiz failed: {r.text}"
    quiz_data = r.json()
    assert len(quiz_data) >= 1
    print(f"    Quiz questions generated: {len(quiz_data)}")
    print("    Q1:", quiz_data[0]["question"])
    print("    --> Quiz test PASSED.")

    # 7. Flashcards endpoint
    print("\n[7] Testing POST /api/flashcards...")
    r = client.post("/api/flashcards", json={
        "text": SAMPLE_ARTICLE,
        "title": "Cognitive Load Theory"
    })
    assert r.status_code == 200, f"Flashcards failed: {r.text}"
    fc_data = r.json()
    assert len(fc_data) >= 1
    print(f"    Flashcards generated: {len(fc_data)}")
    print("    Card 1 front:", fc_data[0]["front"])
    print("    --> Flashcards test PASSED.")

    # 8. List articles (seed data)
    print("\n[8] Testing GET /api/articles...")
    r = client.get("/api/articles")
    assert r.status_code == 200
    articles = r.json()
    print(f"    Articles available in library: {len(articles)}")
    assert len(articles) >= 1
    art_id = articles[0]["id"]
    print(f"    Testing GET /api/articles/{art_id}...")
    r_art = client.get(f"/api/articles/{art_id}")
    assert r_art.status_code == 200
    print("    Article title:", r_art.json()["title"])
    print("    --> Articles retrieval PASSED.")

    print("\n" + "=" * 65)
    print("ALL 8 BACKEND TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 65)
    return True


if __name__ == "__main__":
    success = run_tests()
    if not success:
        sys.exit(1)
