# BookReview

**Official project title:** Book Review Website for Sharing Reading Experiences  
**Course:** CSC 302, Systems Analysis and Design

BookReview is a student website prototype where readers can explore a catalogue of books and submit reviews.

## Features
- Responsive book catalogue
- Search by title, author, or genre
- Genre filters
- Review form with input validation
- Flask backend and SQLite database for submitted reviews
- Reviews persist when the server restarts

## Run locally on macOS
1. Extract this project folder.
2. Open Terminal and move into the folder. If it is in Downloads, run:
   `cd ~/Downloads/book-review-website`
3. Create a virtual environment:
   `python3 -m venv .venv`
4. Activate it:
   `source .venv/bin/activate`
5. Install Flask:
   `python -m pip install -r requirements.txt`
6. Start the website:
   `python server.py`
7. Open `http://127.0.0.1:5000`.

Keep Terminal open while using the site. Press Control + C to stop the server.

## Database
The server creates `bookreview.db` automatically and uses it to store submitted reviews.

## Current limitations
This is a local academic prototype. It does not yet include user accounts, password login, a hosted service, or a shared online database. The displayed community reviews are sample demonstration content, not verified user submissions. The newsletter form is a front-end demonstration only.

## Main files
- `index.html`: page structure
- `styles.css`: visual design
- `app.js`: search, filters, and review form interactions
- `server.py`: Flask server and API
- `requirements.txt`: Python dependency
