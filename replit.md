# JobGuard AI

Intelligent job fraud detection web application. Users paste job descriptions, URLs, emails, or image text to get instant AI-powered analysis identifying fake vs safe job postings.

## Run & Operate

- The app runs via the `artifacts/jobguard-ai: web` workflow
- Command: `python /home/runner/workspace/artifacts/api-server/app.py`
- Port: 22547 (proxied to `/` via the shared reverse proxy)
- Demo login: rahul@gmail.com / user123 (user), admin@jobguard.ai / admin123 (admin)

## Stack

- **Frontend**: Vanilla HTML, CSS, JavaScript (Jinja2 templates)
- **Backend**: Python 3.11 + Flask 3.1
- **Database**: SQLite (via sqlite3 built-in)
- **Charts**: Chart.js via CDN
- **Auth**: Flask session-based with werkzeug password hashing
- **AI Detection**: scikit-learn TF-IDF + Logistic Regression (hybrid: 65% ML + 35% rules)
- **URL Scraping**: BeautifulSoup4 + requests
- **OCR**: pytesseract (graceful fallback — Tesseract binary not installed)
- **AI Chat**: Rule-based knowledge base with Ollama fallback hook

## Where things live

- `artifacts/api-server/app.py` — Flask routes (all 20+ pages)
- `artifacts/api-server/database.py` — SQLite setup, CRUD, admin functions
- `artifacts/api-server/ai_detector.py` — scikit-learn ML fraud detection
- `artifacts/api-server/url_scraper.py` — BeautifulSoup URL scraping
- `artifacts/api-server/ai_chat.py` — AI chat with knowledge base fallback
- `artifacts/api-server/templates/` — All Jinja2 HTML templates (17 pages)
- `artifacts/api-server/static/css/style.css` — Complete CSS theme
- `artifacts/api-server/jobguard.db` — SQLite database (auto-created on first run)
- `artifacts/api-server/fraud_model.pkl` — Trained ML model (auto-generated on first run)

## Pages

1. Login / Register (no sidebar)
2. Dashboard (stats + AI briefing + trend charts + recent analyses)
3. Analyze Job (text / URL scrape / image OCR / email tabs)
4. Result (stamp + fraud score + confidence ring + AI explanation + reasons + AI chat widget)
5. History (filterable table with fraud scores + result filter tabs)
6. Insights (charts + distribution breakdown)
7. Job Portal (browse with AI scores + verification badges)
8. Job Detail (apply form + save job)
9. My Applications (applied + saved jobs)
10. Cybercrime Report (report fake jobs)
11. Profile (update name/email + activity stats)
12. Admin Overview (system stats + charts + quick actions)
13. Admin User Management (view/suspend/activate/delete users)
14. Admin Job Management (add/edit/delete jobs with AI auto-scoring)
15. Admin Feedback & Reports (feedback analytics + report moderation with actions)
16. Admin Platform Analytics (fraud trends, verdict breakdown, input type charts, ML model info)

## Fraud Score System (updated)

- **0–35**: Safe (green)
- **36–65**: Suspicious (orange)
- **66–100**: Fake (red)

## Architecture decisions

- Flask serves both HTML pages (server-side rendering) and REST API at `/api/*`
- Session-based auth using Flask's built-in session + werkzeug hashing
- Hybrid AI: scikit-learn ML model (65%) + keyword rules engine (35%)
- ML model trained at startup using TRAINING_DATA in ai_detector.py, saved as fraud_model.pkl
- URL scraping uses BeautifulSoup4 with job-content-aware extraction
- OCR endpoint tries pytesseract; falls back to manual text entry if Tesseract not installed
- AI chat uses rule-based knowledge base; hooks into Ollama if locally running
- SQLite chosen for simplicity and zero-config deployment

## User preferences

- Frontend: plain HTML, CSS, JavaScript (no React, no TypeScript, no Vite)
- Backend: Python Flask
- Database: SQLite
