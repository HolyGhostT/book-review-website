from flask import Flask, jsonify, request, send_from_directory, session
import os
import secrets
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("DATABASE_PATH", str(ROOT / "bookreview.db")))
app = Flask(__name__, static_folder=None)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(32))
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax",
                  SESSION_COOKIE_SECURE=os.environ.get("RENDER", "") == "true")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")

SEED_BOOKS = [
    (1, "The Alchemist", "Paulo Coelho", "Fiction", "A young shepherd follows a dream and discovers what it means to listen to his heart.", 1988, "#d7c39d", "#314331", "✳"),
    (2, "Homegoing", "Yaa Gyasi", "Fiction", "Two half-sisters and the generations that follow them across continents and time.", 2016, "#31513e", "#f6e8c8", "✦"),
    (3, "The Creative Act", "Rick Rubin", "Personal Growth", "A thoughtful look at creativity, attention and making space for meaningful work.", 2023, "#c77751", "#fff0d6", "☼"),
    (4, "Atomic Habits", "James Clear", "Personal Growth", "Practical ideas for building better habits through small, consistent changes.", 2018, "#d7e0d1", "#334734", "◉"),
    (5, "Things Fall Apart", "Chinua Achebe", "Classic", "A landmark novel exploring community, tradition and change in pre-colonial Nigeria.", 1958, "#b65f43", "#fff0d6", "✺"),
    (6, "Pride and Prejudice", "Jane Austen", "Classic", "A novel about first impressions, family, class and the possibility of changing one's mind.", 1813, "#e4d6b9", "#493a32", "❧"),
]

def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect_db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL, author TEXT NOT NULL, genre TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '', year INTEGER,
            color TEXT NOT NULL DEFAULT '#d7c39d', ink TEXT NOT NULL DEFAULT '#314331',
            symbol TEXT NOT NULL DEFAULT '✳', cover_url TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT, book_id INTEGER NOT NULL,
            name TEXT NOT NULL, rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
            review_text TEXT NOT NULL, created_at TEXT NOT NULL
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT NOT NULL,
            subject TEXT NOT NULL, message TEXT NOT NULL, created_at TEXT NOT NULL
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE COLLATE NOCASE,
            created_at TEXT NOT NULL
        )""")
        count = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
        if count == 0:
            now = datetime.now(timezone.utc).isoformat(timespec="seconds")
            conn.executemany("""INSERT INTO books
                (id,title,author,genre,description,year,color,ink,symbol,cover_url,created_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                [(i,t,a,g,d,y,c,ink,s,"",now) for i,t,a,g,d,y,c,ink,s in SEED_BOOKS])

init_db()

@app.get("/")
def home():
    return send_from_directory(ROOT, "index.html")

@app.get("/admin")
def admin_page():
    return send_from_directory(ROOT, "admin.html")

@app.get("/contact")
def contact_page():
    return send_from_directory(ROOT, "contact.html")

@app.get("/<path:filename>")
def static_files(filename):
    target = (ROOT / filename).resolve()
    if ROOT.resolve() not in target.parents or not target.is_file():
        return jsonify({"error": "File not found"}), 404
    return send_from_directory(ROOT, filename)

@app.get("/api/books")
def get_books():
    with connect_db() as conn:
        rows = conn.execute("SELECT * FROM books ORDER BY id DESC").fetchall()
        reviews = conn.execute("SELECT book_id, AVG(rating) AS avg_rating, COUNT(*) AS total FROM reviews GROUP BY book_id").fetchall()
    rating_map = {r["book_id"]: {"rating": round(r["avg_rating"],1), "reviewCount":r["total"]} for r in reviews}
    result=[]
    for row in rows:
        item={k:row[k] for k in ["id","title","author","genre","description","year","color","ink","symbol","cover_url"]}
        item["coverUrl"] = item.pop("cover_url")
        item["desc"] = item["description"]
        item["rating"] = rating_map.get(row["id"],{}).get("rating",0)
        item["reviewCount"] = rating_map.get(row["id"],{}).get("reviewCount",0)
        result.append(item)
    return jsonify({"books":result})

@app.get("/api/reviews")
def get_reviews():
    with connect_db() as conn:
        rows=conn.execute("SELECT id,book_id,name,rating,review_text,created_at FROM reviews ORDER BY id DESC").fetchall()
    return jsonify({"reviews":[{
        "id":r["id"],"bookId":r["book_id"],"name":r["name"],"rating":r["rating"],
        "text":r["review_text"],"date":datetime.fromisoformat(r["created_at"]).strftime("%d %b %Y")
    } for r in rows]})

@app.post("/api/reviews")
def add_review():
    data=request.get_json(silent=True) or {}
    name=str(data.get("name","")).strip(); text=str(data.get("text","")).strip()
    try: book_id=int(data.get("bookId")); rating=int(data.get("rating"))
    except (TypeError,ValueError): return jsonify({"error":"Select a book and rating."}),400
    if not name or len(name)>80: return jsonify({"error":"Enter your name (up to 80 characters)."}),400
    if len(text)<12 or len(text)>2000: return jsonify({"error":"Review must be between 12 and 2,000 characters."}),400
    if not 1<=rating<=5: return jsonify({"error":"Rating must be between 1 and 5."}),400
    with connect_db() as conn:
        if not conn.execute("SELECT id FROM books WHERE id=?",(book_id,)).fetchone():
            return jsonify({"error":"That book is not available."}),404
        cur=conn.execute("INSERT INTO reviews(book_id,name,rating,review_text,created_at) VALUES(?,?,?,?,?)",
            (book_id,name,rating,text,datetime.now(timezone.utc).isoformat(timespec="seconds")))
        review_id=cur.lastrowid
    return jsonify({"review":{"id":review_id,"bookId":book_id,"name":name,"rating":rating,"text":text,"date":"Just added"}}),201

@app.post("/api/newsletter")
def add_subscriber():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    if len(email) > 254 or "@" not in email or email.startswith("@") or email.endswith("@"):
        return jsonify({"error": "Please enter a valid email address."}), 400
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        with connect_db() as conn:
            conn.execute("INSERT INTO subscribers(email, created_at) VALUES(?, ?)", (email, now))
    except sqlite3.IntegrityError:
        return jsonify({"message": "This email is already subscribed."}), 200
    return jsonify({"message": "You're in! Your email has been added to the BookReview newsletter."}), 201

@app.post("/api/messages")
def add_message():
    d=request.get_json(silent=True) or {}
    name=str(d.get("name","")).strip(); email=str(d.get("email","")).strip()
    subject=str(d.get("subject","")).strip(); message=str(d.get("message","")).strip()
    if not name or len(name)>80: return jsonify({"error":"Enter your name (up to 80 characters)."}),400
    if "@" not in email or len(email)>160: return jsonify({"error":"Enter a valid email address."}),400
    if not subject or len(subject)>160: return jsonify({"error":"Enter a subject."}),400
    if len(message)<5 or len(message)>3000: return jsonify({"error":"Message must be between 5 and 3,000 characters."}),400
    with connect_db() as conn:
        cur=conn.execute("INSERT INTO messages(name,email,subject,message,created_at) VALUES(?,?,?,?,?)",
            (name,email,subject,message,datetime.now(timezone.utc).isoformat(timespec="seconds")))
    return jsonify({"message":"Message received","id":cur.lastrowid}),201

def is_admin():
    return bool(session.get("bookreview_admin"))

@app.post("/admin/login")
def admin_login():
    d=request.get_json(silent=True) or {}
    if not ADMIN_PASSWORD:
        return jsonify({"error":"Admin password is not configured in Render Environment settings."}),503
    if not secrets.compare_digest(str(d.get("password","")),ADMIN_PASSWORD):
        return jsonify({"error":"Incorrect password."}),401
    session["bookreview_admin"]=True
    return jsonify({"message":"Signed in"})

@app.post("/admin/logout")
def admin_logout():
    session.clear()
    return jsonify({"message":"Signed out"})

@app.get("/api/admin/summary")
def admin_summary():
    if not is_admin(): return jsonify({"error":"Please sign in."}),401
    with connect_db() as conn:
        books=conn.execute("SELECT * FROM books ORDER BY id DESC").fetchall()
        reviews=conn.execute("""SELECT r.*,b.title AS book_title FROM reviews r LEFT JOIN books b ON b.id=r.book_id ORDER BY r.id DESC""").fetchall()
        messages=conn.execute("SELECT * FROM messages ORDER BY id DESC").fetchall()
        subscribers=conn.execute("SELECT * FROM subscribers ORDER BY id DESC").fetchall()
    return jsonify({
        "books":[{k:b[k] for k in ["id","title","author","genre","description","year","color","ink","symbol","cover_url"]} for b in books],
        "reviews":[{"id":r["id"],"bookId":r["book_id"],"bookTitle":r["book_title"] or "Removed book","name":r["name"],"rating":r["rating"],"text":r["review_text"],"date":r["created_at"]} for r in reviews],
        "messages":[{"id":m["id"],"name":m["name"],"email":m["email"],"subject":m["subject"],"message":m["message"],"date":m["created_at"]} for m in messages],
        "subscribers":[{"id":s["id"],"email":s["email"],"date":s["created_at"]} for s in subscribers],
        "reviewCount":len(reviews),"messageCount":len(messages),"bookCount":len(books),"subscriberCount":len(subscribers)
    })

@app.post("/api/admin/books")
def create_book():
    if not is_admin(): return jsonify({"error":"Please sign in."}),401
    d=request.get_json(silent=True) or {}
    title=str(d.get("title","")).strip(); author=str(d.get("author","")).strip()
    genre=str(d.get("genre","")).strip(); desc=str(d.get("description","")).strip()
    cover=str(d.get("coverUrl","")).strip()
    try: year=int(d.get("year") or 0) or None
    except (TypeError,ValueError): year=None
    if not title or not author or not genre: return jsonify({"error":"Title, author and genre are required."}),400
    if len(title)>180 or len(author)>120 or len(desc)>1200 or len(cover)>1000: return jsonify({"error":"One of the fields is too long."}),400
    now=datetime.now(timezone.utc).isoformat(timespec="seconds")
    with connect_db() as conn:
        cur=conn.execute("""INSERT INTO books(title,author,genre,description,year,color,ink,symbol,cover_url,created_at)
          VALUES(?,?,?,?,?,?,?,?,?,?)""",(title,author,genre,desc,year,str(d.get("color") or "#d7c39d"),str(d.get("ink") or "#314331"),str(d.get("symbol") or "✳"),cover,now))
        book_id=cur.lastrowid
    return jsonify({"message":"Book added","id":book_id}),201

@app.put("/api/admin/books/<int:book_id>")
def update_book(book_id):
    if not is_admin(): return jsonify({"error":"Please sign in."}),401
    d=request.get_json(silent=True) or {}
    title=str(d.get("title","")).strip(); author=str(d.get("author","")).strip(); genre=str(d.get("genre","")).strip()
    desc=str(d.get("description","")).strip(); cover=str(d.get("coverUrl","")).strip()
    try: year=int(d.get("year") or 0) or None
    except (TypeError,ValueError): year=None
    if not title or not author or not genre: return jsonify({"error":"Title, author and genre are required."}),400
    now=datetime.now(timezone.utc).isoformat(timespec="seconds")
    with connect_db() as conn:
        cur=conn.execute("""UPDATE books SET title=?,author=?,genre=?,description=?,year=?,color=?,ink=?,symbol=?,cover_url=? WHERE id=?""",
            (title,author,genre,desc,year,str(d.get("color") or "#d7c39d"),str(d.get("ink") or "#314331"),str(d.get("symbol") or "✳"),cover,book_id))
        if cur.rowcount==0:return jsonify({"error":"Book not found."}),404
    return jsonify({"message":"Book updated"})

@app.delete("/api/admin/books/<int:book_id>")
def delete_book(book_id):
    if not is_admin(): return jsonify({"error":"Please sign in."}),401
    with connect_db() as conn:
        conn.execute("DELETE FROM reviews WHERE book_id=?",(book_id,))
        cur=conn.execute("DELETE FROM books WHERE id=?",(book_id,))
        if cur.rowcount==0:return jsonify({"error":"Book not found."}),404
    return jsonify({"message":"Book deleted"})

@app.delete("/api/admin/reviews/<int:item_id>")
def delete_review(item_id):
    if not is_admin(): return jsonify({"error":"Please sign in."}),401
    with connect_db() as conn: conn.execute("DELETE FROM reviews WHERE id=?",(item_id,))
    return jsonify({"message":"Review deleted"})

@app.delete("/api/admin/messages/<int:item_id>")
def delete_message(item_id):
    if not is_admin(): return jsonify({"error":"Please sign in."}),401
    with connect_db() as conn: conn.execute("DELETE FROM messages WHERE id=?",(item_id,))
    return jsonify({"message":"Message deleted"})

@app.delete("/api/admin/subscribers/<int:item_id>")
def delete_subscriber(item_id):
    if not is_admin(): return jsonify({"error":"Please sign in."}),401
    with connect_db() as conn:
        cur = conn.execute("DELETE FROM subscribers WHERE id=?", (item_id,))
        if cur.rowcount == 0:
            return jsonify({"error":"Subscriber not found."}),404
    return jsonify({"message":"Subscriber removed"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT","10000")), debug=False)
