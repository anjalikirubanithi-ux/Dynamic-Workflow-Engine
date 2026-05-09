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
- **AI Detection**: Rule-based keyword scoring engine

## Where things live

- `artifacts/api-server/app.py` — Flask routes (all 18 pages)
- `artifacts/api-server/database.py` — SQLite setup, CRUD, seeding
- `artifacts/api-server/ai_detector.py` — Rule-based fraud detection logic
- `artifacts/api-server/templates/` — All Jinja2 HTML templates (15 pages)
- `artifacts/api-server/static/css/style.css` — Complete CSS theme
- `artifacts/api-server/jobguard.db` — SQLite database (auto-created on first run)

## Pages

1. Login / Register (no sidebar)
2. Dashboard (stats cards + trend chart + recent analyses)
3. Analyze Job (text / URL / image OCR / email tabs)
4. Result (stamp + confidence ring + reasons + feedback)
5. History (filterable table of all analyses)
6. Insights (charts + distribution breakdown)
7. Job Portal (browse with AI scores + verification badges)
8. Job Detail (apply form + save job)
9. My Applications (applied + saved jobs)
10. Cybercrime Report (report fake jobs)
11. Profile (update name/email + activity stats)
12. Admin Overview (system-wide stats — admin only)
13. Admin Feedback & Reports (feedback analytics — admin only)

## Architecture decisions

- Flask serves both HTML pages (server-side rendering) and REST API at `/api/*`
- Session-based auth using Flask's built-in session + werkzeug hashing
- Rule-based AI detector scores content 0–100 based on keyword patterns; score ≥ 60 = fake, ≥ 30 = suspicious
- SQLite chosen for simplicity and zero-config deployment
- Chart.js loaded from CDN to avoid build steps

## User preferences

- Frontend: plain HTML, CSS, JavaScript (no React, no TypeScript, no Vite)
- Backend: Python Flask
- Database: SQLite
