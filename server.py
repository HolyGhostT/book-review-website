from flask import Flask, jsonify, request, send_from_directory
import sqlite3
import os
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "bookreview.db"
app = Flask(__name__, static_folder=None)

BOOKS = [
    {"id": 1, "title": "The Alchemist", "author": "Paulo Coelho", "genre": "Fiction"},
    {"id": 2, "title": "Homegoing", "author": "Yaa Gyasi", "genre": "Fiction"},
    {"id": 3, "title": "The Creative Act", "author": "Rick Rubin", "genre": "Personal Growth"},
    {"id": 4, "title": "Atomic Habits", "author": "James Clear", "genre": "Personal Growth"},
    {"id": 5, "title": "Things Fall Apart", "author": "Chinua Achebe", "genre": "Classic"},
    {"id": 6, "title": "Pride and Prejudice", "author": "Jane Austen", "genre": "Classic"},
]

def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
                review_text TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

init_db()

@app.get("/")
def home():
    return send_from_directory(ROOT, "index.html")

@app.get("/<path:filename>")
def static_files(filename):
    target = (ROOT / filename).resolve()
    if ROOT.resolve() not in target.parents or not target.is_file():
        return jsonify({"error": "File not found"}), 404
    return send_from_directory(ROOT, filename)

@app.get("/api/books")
def get_books():
    return jsonify({"books": BOOKS})

@app.get("/api/reviews")
def get_reviews():
    with connect_db() as conn:
        rows = conn.execute(
            "SELECT id, book_id, name, rating, review_text, created_at FROM reviews ORDER BY id DESC"
        ).fetchall()
    reviews = [{
        "id": row["id"], "bookId": row["book_id"], "name": row["name"],
        "rating": row["rating"], "text": row["review_text"],
        "date": datetime.fromisoformat(row["created_at"]).strftime("%d %b %Y")
    } for row in rows]
    return jsonify({"reviews": reviews})

@app.post("/api/reviews")
def add_review():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    text = str(payload.get("text", "")).strip()
    try:
        book_id, rating = int(payload.get("bookId")), int(payload.get("rating"))
    except (TypeError, ValueError):
        return jsonify({"error": "Please select a book and rating."}), 400
    if not name or len(name) > 80:
        return jsonify({"error": "Enter your name (up to 80 characters)."}), 400
    if len(text) < 12 or len(text) > 2000:
        return jsonify({"error": "A review must be between 12 and 2,000 characters."}), 400
    if book_id not in {book["id"] for book in BOOKS}:
        return jsonify({"error": "Please select a valid book."}), 400
    if rating < 1 or rating > 5:
        return jsonify({"error": "Rating must be between 1 and 5."}), 400
    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with connect_db() as conn:
        cursor = conn.execute(
            "INSERT INTO reviews (book_id, name, rating, review_text, created_at) VALUES (?, ?, ?, ?, ?)",
            (book_id, name, rating, text, created_at)
        )
        review_id = cursor.lastrowid
    return jsonify({"message": "Review saved", "review": {
        "id": review_id, "bookId": book_id, "name": name, "rating": rating,
        "text": text, "date": "Just added"
    }}), 201

if __name__ == "__main__":
    init_db()
    print("BookReview is running at http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "10000")), debug=False)
