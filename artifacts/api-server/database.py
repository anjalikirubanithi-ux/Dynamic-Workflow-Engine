import sqlite3
import json
import os
from datetime import datetime, timedelta
import random

DB_PATH = os.path.join(os.path.dirname(__file__), 'jobguard.db')

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            avatar_url TEXT,
            account_status TEXT DEFAULT 'Active',
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            input_type TEXT NOT NULL,
            content TEXT NOT NULL,
            job_title TEXT,
            result TEXT NOT NULL,
            confidence_score INTEGER NOT NULL,
            risk_level TEXT NOT NULL,
            ai_explanation TEXT NOT NULL,
            key_reasons TEXT NOT NULL,
            keyword_highlights TEXT NOT NULL,
            safety_tips TEXT NOT NULL,
            feedback_given INTEGER,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            is_correct INTEGER NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (analysis_id) REFERENCES analyses(id)
        );
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            job_title TEXT NOT NULL,
            description TEXT NOT NULL,
            analysis_id INTEGER,
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT NOT NULL,
            job_type TEXT DEFAULT 'Full-Time',
            salary TEXT,
            posted_days_ago INTEGER DEFAULT 0,
            verification_status TEXT NOT NULL,
            ai_score INTEGER NOT NULL,
            description TEXT NOT NULL,
            why_legitimate TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            resume_filename TEXT,
            status TEXT DEFAULT 'under_review',
            applied_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (job_id) REFERENCES jobs(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS saved_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            saved_at TEXT DEFAULT (datetime('now')),
            UNIQUE(job_id, user_id),
            FOREIGN KEY (job_id) REFERENCES jobs(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    ''')
    conn.commit()
    conn.close()

def seed_data():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] > 0:
        conn.close()
        return

    from werkzeug.security import generate_password_hash

    # Seed users
    c.execute("INSERT INTO users (full_name, email, password_hash, role, account_status, created_at) VALUES (?,?,?,?,?,?)",
              ('Rahul Sharma', 'rahul@gmail.com', generate_password_hash('user123'), 'user', 'Active', '2025-04-01'))
    c.execute("INSERT INTO users (full_name, email, password_hash, role, account_status, created_at) VALUES (?,?,?,?,?,?)",
              ('Admin User', 'admin@jobguard.ai', generate_password_hash('admin123'), 'admin', 'Active', '2025-01-01'))
    user_id = 1

    # Seed jobs
    jobs_data = [
        ('Frontend Developer', 'Infosys', 'Bangalore', 'Full-Time', '₹8-12 LPA', 2, 'verified', 92,
         'We are looking for a skilled Frontend Developer with 2+ years of experience in HTML, CSS, JavaScript and React. Work with our talented team to build amazing products.',
         'Company domain is verified. Professional email & contact. Salary range is industry-standard. No registration fee required.'),
        ('Data Analyst', 'TCS', 'Hyderabad', 'Full-Time', '₹6-10 LPA', 40, 'verified', 88,
         'TCS is hiring Data Analysts with strong skills in Python, SQL and data visualization. Join our growing analytics team.',
         'TCS is a well-known company. Standard hiring process. No upfront fee.'),
        ('Work From Home – Earn 5000 Daily', 'Unknown', 'Work from Home', 'Part-Time', '₹5000/day', 16, 'suspicious', 28,
         'Earn Rs 5000 daily working from home. No experience needed. Join our WhatsApp group for more details. Registration fee Rs 500.',
         None),
        ('UI/UX Designer', 'Wipro', 'Pune', 'Full-Time', '₹7-11 LPA', 1, 'verified', 90,
         'Wipro is seeking a creative UI/UX Designer. You will design user-friendly interfaces for our enterprise clients.',
         'Wipro is a reputed company. Legitimate job description with proper requirements.'),
        ('Urgent Hiring – Earn 3000 Daily', 'XYZ Corp', 'Remote', 'Part-Time', '₹3000/day', 11, 'suspicious', 18,
         'Urgent hiring! Earn 3000 daily from home. No experience needed. Pay registration fee Rs 200 to join. WhatsApp interview.',
         None),
        ('Software Engineer', 'Google India', 'Bangalore', 'Full-Time', '₹30-50 LPA', 3, 'verified', 95,
         'Google is looking for exceptional Software Engineers. Work on world-class products. Strong CS fundamentals required.',
         'Google is a global brand. Standard technical interview process. No fees.'),
        ('Content Writer', 'Freelance', 'Remote', 'Part-Time', '₹20,000/month', 5, 'verified', 78,
         'Looking for a creative content writer with good English skills. Work on blogs, articles and social media content.',
         'Reasonable salary. Clear job description. Direct payment to bank account.'),
        ('Marketing Executive at ABC', 'ABC Pvt Ltd', 'Mumbai', 'Full-Time', '₹4-6 LPA', 10, 'verified', 82,
         'ABC Pvt Ltd is hiring Marketing Executives for our expansion team. Handle B2B sales and marketing campaigns.',
         'Registered company. Standard job requirements. Industry-standard salary.'),
    ]
    for j in jobs_data:
        c.execute("INSERT INTO jobs (title, company, location, job_type, salary, posted_days_ago, verification_status, ai_score, description, why_legitimate) VALUES (?,?,?,?,?,?,?,?,?,?)", j)

    # Seed analyses for user 1
    sample_analyses = [
        ('text', 'Software Developer at XYZ Company. Earn 5000 daily. No experience needed. Pay registration fee Rs 500. Join our Telegram group.', 'Software Developer at XYZ', 'fake', 87, 'high'),
        ('url', 'https://urgentjobs-earn5000daily.blogspot.com', 'Urgent Hiring', 'fake', 91, 'high'),
        ('text', 'Infosys is hiring Frontend Developers. Apply through official portal. 2+ years experience required. CTC 8-12 LPA.', 'Frontend Developer', 'safe', 92, 'low'),
        ('email', 'From: jobs@tcs-careers.com. Dear Candidate, You are shortlisted for Data Analyst role. Interview on 15 May at Hyderabad office.', 'Data Analyst TCS', 'safe', 88, 'low'),
        ('text', 'Pay Registration Fee & Get Job. Guaranteed job in 7 days. Earn 50000 monthly. No interview needed.', 'Registration Fee Job', 'fake', 95, 'high'),
        ('text', 'Marketing Executive at ABC Pvt Ltd. Bangalore. 3-5 years experience. Salary 5-8 LPA. Send CV to hr@abcpvtltd.com', 'Marketing Executive', 'safe', 79, 'low'),
    ]

    dates = []
    for i in range(6):
        d = datetime.now() - timedelta(days=i)
        dates.append(d.strftime('%Y-%m-%d %H:%M:%S'))

    for i, (itype, content, title, verdict, conf, risk) in enumerate(sample_analyses):
        if verdict == 'fake':
            explanation = "Our AI model has determined this job posting is SUSPICIOUS / FRAUDULENT based on multiple risk indicators found in the content."
            reasons = json.dumps(["Contains payment / fee keywords", "Uses urgent and unrealistic promises", "Domain is suspicious or mismatched"])
            keywords = json.dumps(["Registration Fee", "Earn Daily", "No Experience", "Telegram/WhatsApp"])
            tips = json.dumps(["Never pay money for a job", "Avoid jobs that seem too good to be true", "Verify company on official website"])
        else:
            explanation = "Our AI model has determined this job posting appears LEGITIMATE based on standard industry practices and verified indicators."
            reasons = json.dumps(["Professional email domain", "Salary is industry-standard", "Clear job description with requirements"])
            keywords = json.dumps(["Official Portal", "Experience Required", "CTC Package"])
            tips = json.dumps(["Verify company website before applying", "Apply through official channels", "Do not share personal financial details"])

        c.execute("""INSERT INTO analyses (user_id, input_type, content, job_title, result, confidence_score, risk_level,
                     ai_explanation, key_reasons, keyword_highlights, safety_tips, created_at)
                     VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                  (user_id, itype, content, title, verdict, conf, risk,
                   explanation, reasons, keywords, tips, dates[i]))

    # Seed feedback
    c.execute("INSERT INTO feedback (analysis_id, user_id, is_correct, created_at) VALUES (?,?,?,?)", (1, user_id, 1, dates[0]))
    c.execute("INSERT INTO feedback (analysis_id, user_id, is_correct, created_at) VALUES (?,?,?,?)", (2, user_id, 1, dates[1]))
    c.execute("INSERT INTO feedback (analysis_id, user_id, is_correct, created_at) VALUES (?,?,?,?)", (3, user_id, 1, dates[2]))

    # Seed reports
    c.execute("INSERT INTO reports (user_id, job_title, description, analysis_id, status, created_at) VALUES (?,?,?,?,?,?)",
              (user_id, 'Software Developer at XYZ', 'This job asks for registration fee and is clearly fraudulent.', 1, 'pending', dates[0]))
    c.execute("INSERT INTO reports (user_id, job_title, description, analysis_id, status, created_at) VALUES (?,?,?,?,?,?)",
              (user_id, 'Urgent Hiring – Earn 5000 Daily', 'Fake job with suspicious URL and WhatsApp contact.', 2, 'reviewed', dates[1]))

    # Seed application
    c.execute("INSERT INTO applications (job_id, user_id, full_name, email, phone, status, applied_at) VALUES (?,?,?,?,?,?,?)",
              (1, user_id, 'Rahul Sharma', 'rahul@gmail.com', '9876543210', 'under_review', dates[1]))
    c.execute("INSERT INTO applications (job_id, user_id, full_name, email, phone, status, applied_at) VALUES (?,?,?,?,?,?,?)",
              (2, user_id, 'Rahul Sharma', 'rahul@gmail.com', '9876543210', 'shortlisted', dates[2]))
    c.execute("INSERT INTO applications (job_id, user_id, full_name, email, phone, status, applied_at) VALUES (?,?,?,?,?,?,?)",
              (4, user_id, 'Rahul Sharma', 'rahul@gmail.com', '9876543210', 'rejected', dates[3]))

    conn.commit()
    conn.close()

def get_user_by_email(email):
    conn = get_conn()
    user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    conn.close()
    return dict(user) if user else None

def get_user(user_id):
    conn = get_conn()
    user = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None

def create_user(full_name, email, password_hash):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO users (full_name, email, password_hash) VALUES (?,?,?)", (full_name, email, password_hash))
    conn.commit()
    user_id = c.lastrowid
    conn.close()
    return user_id

def update_user(user_id, data):
    conn = get_conn()
    fields = []
    values = []
    if data.get('full_name'):
        fields.append('full_name=?'); values.append(data['full_name'])
    if data.get('email'):
        fields.append('email=?'); values.append(data['email'])
    if fields:
        values.append(user_id)
        conn.execute(f"UPDATE users SET {', '.join(fields)} WHERE id=?", values)
        conn.commit()
    conn.close()

def save_analysis(user_id, input_type, content, job_title, result):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""INSERT INTO analyses (user_id, input_type, content, job_title, result, confidence_score, risk_level,
                 ai_explanation, key_reasons, keyword_highlights, safety_tips)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
              (user_id, input_type, content, job_title,
               result['result'], result['confidence_score'], result['risk_level'],
               result['ai_explanation'],
               json.dumps(result['key_reasons']),
               json.dumps(result['keyword_highlights']),
               json.dumps(result['safety_tips'])))
    conn.commit()
    aid = c.lastrowid
    conn.close()
    return aid

def get_analysis(analysis_id, user_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM analyses WHERE id=? AND user_id=?", (analysis_id, user_id)).fetchone()
    conn.close()
    if not row:
        return None
    a = dict(row)
    a['key_reasons'] = json.loads(a['key_reasons'])
    a['keyword_highlights'] = json.loads(a['keyword_highlights'])
    a['safety_tips'] = json.loads(a['safety_tips'])
    return a

def get_recent_analyses(user_id, limit=5):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM analyses WHERE user_id=? ORDER BY created_at DESC LIMIT ?", (user_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_analyses(user_id):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM analyses WHERE user_id=? ORDER BY created_at DESC", (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_user_stats(user_id):
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) FROM analyses WHERE user_id=?", (user_id,)).fetchone()[0]
    safe = conn.execute("SELECT COUNT(*) FROM analyses WHERE user_id=? AND result='safe'", (user_id,)).fetchone()[0]
    fake = conn.execute("SELECT COUNT(*) FROM analyses WHERE user_id=? AND result='fake'", (user_id,)).fetchone()[0]
    reports = conn.execute("SELECT COUNT(*) FROM reports WHERE user_id=?", (user_id,)).fetchone()[0]
    conn.close()
    return {'total': total, 'safe': safe, 'fake': fake, 'reports': reports}

def get_chart_data(user_id):
    conn = get_conn()
    rows = conn.execute("""
        SELECT date(created_at) as day,
               SUM(CASE WHEN result='safe' THEN 1 ELSE 0 END) as safe,
               SUM(CASE WHEN result='fake' THEN 1 ELSE 0 END) as fake
        FROM analyses WHERE user_id=?
        GROUP BY day ORDER BY day DESC LIMIT 7
    """, (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in reversed(rows)]

def save_feedback(analysis_id, user_id, is_correct):
    conn = get_conn()
    conn.execute("DELETE FROM feedback WHERE analysis_id=? AND user_id=?", (analysis_id, user_id))
    conn.execute("INSERT INTO feedback (analysis_id, user_id, is_correct) VALUES (?,?,?)",
                 (analysis_id, user_id, 1 if is_correct else 0))
    conn.execute("UPDATE analyses SET feedback_given=? WHERE id=?", (1 if is_correct else 0, analysis_id))
    conn.commit()
    conn.close()

def create_report(user_id, data):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO reports (user_id, job_title, description, analysis_id) VALUES (?,?,?,?)",
              (user_id, data.get('job_title', 'Unknown'), data.get('description', ''), data.get('analysis_id')))
    conn.commit()
    rid = c.lastrowid
    conn.close()
    return rid

def get_jobs(search='', status='all'):
    conn = get_conn()
    query = "SELECT * FROM jobs WHERE 1=1"
    params = []
    if search:
        query += " AND (title LIKE ? OR company LIKE ? OR location LIKE ?)"
        params += [f'%{search}%', f'%{search}%', f'%{search}%']
    if status != 'all':
        query += " AND verification_status=?"
        params.append(status)
    query += " ORDER BY id"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_job(job_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def apply_for_job(job_id, user_id, data):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO applications (job_id, user_id, full_name, email, phone, resume_filename) VALUES (?,?,?,?,?,?)",
              (job_id, user_id, data.get('full_name'), data.get('email'), data.get('phone'), data.get('resume_filename')))
    conn.commit()
    aid = c.lastrowid
    conn.close()
    return aid

def already_applied(job_id, user_id):
    conn = get_conn()
    row = conn.execute("SELECT id FROM applications WHERE job_id=? AND user_id=?", (job_id, user_id)).fetchone()
    conn.close()
    return row is not None

def toggle_save_job(job_id, user_id):
    conn = get_conn()
    existing = conn.execute("SELECT id FROM saved_jobs WHERE job_id=? AND user_id=?", (job_id, user_id)).fetchone()
    if existing:
        conn.execute("DELETE FROM saved_jobs WHERE job_id=? AND user_id=?", (job_id, user_id))
        saved = False
    else:
        conn.execute("INSERT OR IGNORE INTO saved_jobs (job_id, user_id) VALUES (?,?)", (job_id, user_id))
        saved = True
    conn.commit()
    conn.close()
    return saved

def is_job_saved(job_id, user_id):
    conn = get_conn()
    row = conn.execute("SELECT id FROM saved_jobs WHERE job_id=? AND user_id=?", (job_id, user_id)).fetchone()
    conn.close()
    return row is not None

def get_applications(user_id):
    conn = get_conn()
    rows = conn.execute("""
        SELECT a.*, j.title as job_title, j.company, j.location, j.verification_status, j.ai_score
        FROM applications a JOIN jobs j ON a.job_id=j.id
        WHERE a.user_id=? ORDER BY a.applied_at DESC
    """, (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_saved_jobs(user_id):
    conn = get_conn()
    rows = conn.execute("""
        SELECT j.*, s.saved_at FROM saved_jobs s JOIN jobs j ON s.job_id=j.id
        WHERE s.user_id=? ORDER BY s.saved_at DESC
    """, (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_admin_stats():
    conn = get_conn()
    users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    analyses = conn.execute("SELECT COUNT(*) FROM analyses").fetchone()[0]
    feedback = conn.execute("SELECT COUNT(*) FROM feedback").fetchone()[0]
    reports = conn.execute("SELECT COUNT(*) FROM reports").fetchone()[0]
    recent = conn.execute("""
        SELECT 'analysis' as type, job_title as description, created_at as time FROM analyses
        UNION ALL
        SELECT 'report' as type, job_title as description, created_at as time FROM reports
        ORDER BY time DESC LIMIT 5
    """).fetchall()
    conn.close()
    return {
        'total_users': users, 'total_analyses': analyses,
        'total_feedback': feedback, 'total_reports': reports,
        'recent_activity': [dict(r) for r in recent]
    }

def get_admin_feedback_stats():
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) FROM feedback").fetchone()[0]
    correct = conn.execute("SELECT COUNT(*) FROM feedback WHERE is_correct=1").fetchone()[0]
    wrong = total - correct
    conn.close()
    return {
        'total': total, 'correct': correct, 'wrong': wrong,
        'correct_pct': round(correct / total * 100, 1) if total > 0 else 0,
        'wrong_pct': round(wrong / total * 100, 1) if total > 0 else 0
    }

def get_all_reports():
    conn = get_conn()
    rows = conn.execute("""
        SELECT r.*, u.full_name as reporter FROM reports r
        JOIN users u ON r.user_id=u.id ORDER BY r.created_at DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]
