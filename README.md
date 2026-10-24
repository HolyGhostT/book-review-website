# BookReview
**Official project title:** Book Review Website for Sharing Reading Experiences  
**Course:** CSC 302: Systems Analysis and Design

## Project purpose
BookReview is a student group-project prototype for exploring a small book catalogue, sharing reader reviews and sending contact messages.

## Main functions
- Browse, search and filter the catalogue
- Submit a review with a rating
- Contact the project team through a form
- Administrator sign-in
- Add, edit and remove books
- View and remove submitted reviews
- View contact messages and open an email reply

## Run locally
Requires Python 3.10 or later.
1. `python3 -m venv .venv`
2. `source .venv/bin/activate`
3. `python -m pip install -r requirements.txt`
4. Set `ADMIN_PASSWORD` and `FLASK_SECRET_KEY` in your local environment.
5. `python server.py`
6. Open `http://127.0.0.1:10000`.

## Render configuration
Build command: `pip install -r requirements.txt`  
Start command: `gunicorn server:app`

In Render → service → Environment, set:
- `ADMIN_PASSWORD`: a strong private password
- `FLASK_SECRET_KEY`: a long random secret

Do not commit secrets to GitHub.

## Honest scope and limitations
- The book-cover field currently accepts a URL, not a file upload from a computer.
- This prototype does not include visitor accounts or verified identities.
- The current database uses SQLite. On Render's free web service, local files are not guaranteed to persist through restarts/redeploys. A persistent hosted database should be configured before using this for ongoing public activity.
- The source files have been reviewed for key frontend/backend field compatibility and Python syntax. The full hosted application still needs manual end-to-end testing after deployment.

## Suggested group testing
Record each result only after actually performing the test:
1. Open homepage on desktop and phone.
2. Search for a known title and filter by genre.
3. Submit a review and check that it appears.
4. Sign in to `/admin` with the configured password.
5. Add a book, edit it, and check it appears on the public catalogue.
6. Delete a test review and verify it is removed.
7. Submit a contact message and confirm it appears in the dashboard.
8. Sign out and verify the admin data endpoints require login.
