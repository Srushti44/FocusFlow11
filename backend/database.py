import sqlite3
import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "focusflow.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS articles (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        author TEXT,
        source_url TEXT,
        domain TEXT,
        raw_content TEXT,
        reading_time_minutes INTEGER DEFAULT 5,
        word_count INTEGER DEFAULT 0,
        flesch_score REAL DEFAULT 65.0,
        cognitive_rating TEXT DEFAULT 'Standard',
        chunks_json TEXT NOT NULL,
        summary_json TEXT,
        concepts_json TEXT,
        quiz_json TEXT,
        flashcards_json TEXT,
        progress_percent INTEGER DEFAULT 0,
        current_chunk_index INTEGER DEFAULT 0,
        is_favorite INTEGER DEFAULT 0,
        is_completed INTEGER DEFAULT 0,
        created_at TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        id TEXT PRIMARY KEY,
        settings_json TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reading_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        article_id TEXT NOT NULL,
        seconds_read INTEGER NOT NULL,
        chunks_read INTEGER NOT NULL,
        timestamp TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

def save_article(article_dict: Dict[str, Any]):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR REPLACE INTO articles (
        id, title, author, source_url, domain, raw_content,
        reading_time_minutes, word_count, flesch_score, cognitive_rating,
        chunks_json, summary_json, concepts_json, quiz_json, flashcards_json,
        progress_percent, current_chunk_index, is_favorite, is_completed, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        article_dict["id"],
        article_dict["title"],
        article_dict.get("author", "Unknown Author"),
        article_dict.get("source_url"),
        article_dict.get("domain", "Web"),
        article_dict.get("raw_content", ""),
        article_dict.get("reading_time_minutes", 5),
        article_dict.get("word_count", 0),
        article_dict.get("flesch_score", 65.0),
        article_dict.get("cognitive_rating", "Standard"),
        json.dumps(article_dict.get("chunks", [])),
        json.dumps(article_dict.get("summary")),
        json.dumps(article_dict.get("concepts", [])),
        json.dumps(article_dict.get("quiz", [])),
        json.dumps(article_dict.get("flashcards", [])),
        article_dict.get("progress_percent", 0),
        article_dict.get("current_chunk_index", 0),
        1 if article_dict.get("is_favorite") else 0,
        1 if article_dict.get("is_completed") else 0,
        article_dict.get("created_at", datetime.now().isoformat())
    ))

    conn.commit()
    conn.close()

def get_articles_list() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, title, author, domain, reading_time_minutes, word_count, 
           progress_percent, current_chunk_index, is_favorite, is_completed,
           chunks_json, created_at
    FROM articles
    ORDER BY created_at DESC
    """)
    rows = cursor.fetchall()
    results = []
    for r in rows:
        chunks = json.loads(r["chunks_json"]) if r["chunks_json"] else []
        results.append({
            "id": r["id"],
            "title": r["title"],
            "author": r["author"],
            "domain": r["domain"],
            "reading_time_minutes": r["reading_time_minutes"],
            "word_count": r["word_count"],
            "progress_percent": r["progress_percent"],
            "current_chunk_index": r["current_chunk_index"],
            "is_favorite": bool(r["is_favorite"]),
            "is_completed": bool(r["is_completed"]),
            "total_chunks": len(chunks),
            "created_at": r["created_at"],
        })
    conn.close()
    return results

def get_article(article_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM articles WHERE id = ?", (article_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    
    article = {
        "id": row["id"],
        "title": row["title"],
        "author": row["author"],
        "source_url": row["source_url"],
        "domain": row["domain"],
        "raw_content": row["raw_content"],
        "reading_time_minutes": row["reading_time_minutes"],
        "word_count": row["word_count"],
        "flesch_score": row["flesch_score"],
        "cognitive_rating": row["cognitive_rating"],
        "chunks": json.loads(row["chunks_json"]) if row["chunks_json"] else [],
        "summary": json.loads(row["summary_json"]) if row["summary_json"] else None,
        "concepts": json.loads(row["concepts_json"]) if row["concepts_json"] else [],
        "quiz": json.loads(row["quiz_json"]) if row["quiz_json"] else [],
        "flashcards": json.loads(row["flashcards_json"]) if row["flashcards_json"] else [],
        "progress_percent": row["progress_percent"],
        "current_chunk_index": row["current_chunk_index"],
        "is_favorite": bool(row["is_favorite"]),
        "is_completed": bool(row["is_completed"]),
        "created_at": row["created_at"],
    }
    conn.close()
    return article

def update_article_progress(article_id: str, progress_percent: int, current_chunk_index: int, is_completed: Optional[bool] = None):
    conn = get_connection()
    cursor = conn.cursor()
    if is_completed is not None:
        cursor.execute("""
        UPDATE articles
        SET progress_percent = ?, current_chunk_index = ?, is_completed = ?
        WHERE id = ?
        """, (progress_percent, current_chunk_index, 1 if is_completed else 0, article_id))
    else:
        cursor.execute("""
        UPDATE articles
        SET progress_percent = ?, current_chunk_index = ?
        WHERE id = ?
        """, (progress_percent, current_chunk_index, article_id))
    conn.commit()
    conn.close()

def toggle_article_favorite(article_id: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT is_favorite FROM articles WHERE id = ?", (article_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False
    new_val = 0 if row["is_favorite"] else 1
    cursor.execute("UPDATE articles SET is_favorite = ? WHERE id = ?", (new_val, article_id))
    conn.commit()
    conn.close()
    return bool(new_val)

def delete_article(article_id: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM articles WHERE id = ?", (article_id,))
    cursor.execute("DELETE FROM reading_sessions WHERE article_id = ?", (article_id,))
    conn.commit()
    conn.close()
    return True

def get_settings() -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT settings_json FROM settings WHERE id = 'default'")
    row = cursor.fetchone()
    conn.close()
    if row and row["settings_json"]:
        return json.loads(row["settings_json"])
    return {
        "font_family": "lexend",
        "font_size": 18,
        "line_spacing": 1.8,
        "letter_spacing": 0.5,
        "content_width": 720,
        "bionic_reading": False,
        "focus_ruler": False,
        "chunk_mode": True,
        "tts_speed": 1.0,
        "theme": "warm",
        "reduced_motion": False,
        "high_contrast": True
    }

def save_settings(settings_dict: Dict[str, Any]):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO settings (id, settings_json) VALUES ('default', ?)
    """, (json.dumps(settings_dict),))
    conn.commit()
    conn.close()

def log_reading_session(article_id: str, seconds_read: int, chunks_read: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO reading_sessions (article_id, seconds_read, chunks_read, timestamp)
    VALUES (?, ?, ?, ?)
    """, (article_id, seconds_read, chunks_read, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_reading_stats() -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total_articles, SUM(is_completed) as completed_count FROM articles")
    art_row = cursor.fetchone()
    cursor.execute("SELECT SUM(seconds_read) as total_seconds, SUM(chunks_read) as total_chunks FROM reading_sessions")
    sess_row = cursor.fetchone()
    conn.close()

    total_articles = art_row["total_articles"] if art_row else 0
    completed_articles = art_row["completed_count"] if art_row and art_row["completed_count"] else 0
    total_seconds = sess_row["total_seconds"] if sess_row and sess_row["total_seconds"] else 0
    total_chunks = sess_row["total_chunks"] if sess_row and sess_row["total_chunks"] else 0

    return {
        "total_articles": total_articles,
        "completed_articles": completed_articles,
        "total_minutes_focused": round(total_seconds / 60),
        "total_chunks_read": total_chunks,
        "streak_days": 4, # sample motivational streak
    }
