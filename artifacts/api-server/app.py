from flask import Flask, render_template, request, session, redirect, url_for, jsonify, flash, get_flashed_messages
from werkzeug.security import generate_password_hash, check_password_hash
import database as db
import ai_detector
import url_scraper
import ai_chat
import os
import base64
import io
import secrets
import time
from functools import wraps

# In-memory reset tokens: {token: {'email': ..., 'expires': ...}}
_reset_tokens = {}

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.environ.get('SESSION_SECRET', os.environ.get('SECRET_KEY', 'jobguard-ai-secret-2025'))

# ── Auth decorators ────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if not session.get('is_admin'):
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated

# ── Auth ──────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    error = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        user = db.get_user_by_email(email)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['full_name'] = user['full_name']
            session['email'] = user['email']
            session['is_admin'] = user['role'] == 'admin'
            session['_login_success'] = f"Welcome back, {user['full_name'].split()[0]}! 👋"
            return redirect(url_for('dashboard'))
        error = 'Invalid email or password'
    success = None
    return render_template('login.html', error=error, success=success)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    error = None
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        if not full_name or not email or not password:
            error = 'All fields are required'
        elif password != confirm:
            error = 'Passwords do not match'
        elif len(password) < 6:
            error = 'Password must be at least 6 characters'
        elif db.get_user_by_email(email):
            error = 'Email already registered'
        else:
            user_id = db.create_user(full_name, email, generate_password_hash(password))
            session['user_id'] = user_id
            session['full_name'] = full_name
            session['email'] = email
            session['is_admin'] = False
            session['_login_success'] = f"Account created! Welcome to JobGuard AI, {full_name.split()[0]}! 🎉"
            return redirect(url_for('dashboard'))
    return render_template('register.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ── Forgot / Reset Password ────────────────────────────────────────────────
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    error = None
    success = None
    token = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user = db.get_user_by_email(email)
        if user:
            # Generate a secure token valid for 30 minutes
            tok = secrets.token_urlsafe(32)
            _reset_tokens[tok] = {'email': email, 'expires': time.time() + 1800}
            # Clean up old tokens
            expired = [k for k, v in _reset_tokens.items() if v['expires'] < time.time()]
            for k in expired:
                del _reset_tokens[k]
            token = tok
            success = f"Reset link generated for {email}. Click the button below to set your new password."
        else:
            error = 'No account found with that email address.'
    return render_template('forgot_password.html', error=error, success=success, token=token)

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    entry = _reset_tokens.get(token)
    if not entry or entry['expires'] < time.time():
        return render_template('reset_password.html', token=token,
                               error='This reset link has expired or is invalid. Please request a new one.')
    error = None
    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        if len(password) < 6:
            error = 'Password must be at least 6 characters.'
        elif password != confirm:
            error = 'Passwords do not match.'
        else:
            db.update_user_password(entry['email'], generate_password_hash(password))
            del _reset_tokens[token]
            return redirect('/login?reset=1')
    return render_template('reset_password.html', token=token, error=error)

# ── Dashboard ─────────────────────────────────────────────────────────────
@app.route('/dashboard')
@login_required
def dashboard():
    stats = db.get_user_stats(session['user_id'])
    recent = db.get_recent_analyses(session['user_id'], limit=5)
    chart_data = db.get_chart_data(session['user_id'])
    login_msg = session.pop('_login_success', None)
    return render_template('dashboard.html', stats=stats, recent=recent, chart_data=chart_data, login_success=login_msg)

@app.route('/api/ai-briefing')
@login_required
def api_ai_briefing():
    stats = db.get_user_stats(session['user_id'])
    recent = db.get_recent_analyses(session['user_id'], limit=5)
    briefing = ai_chat.generate_briefing(stats, recent)
    return jsonify({'briefing': briefing})

# ── Analyze ───────────────────────────────────────────────────────────────
@app.route('/analyze')
@login_required
def analyze():
    return render_template('analyze.html')

@app.route('/api/analyze', methods=['POST'])
@login_required
def api_analyze():
    data = request.get_json(force=True, silent=True) or {}
    input_type = data.get('input_type', 'text')
    content = data.get('content', '').strip()
    job_title = data.get('job_title', '').strip()
    if not content:
        return jsonify({'error': 'Content is required'}), 400
    try:
        result = ai_detector.analyze(content, input_type)
        analysis_id = db.save_analysis(
            user_id=session['user_id'],
            input_type=input_type,
            content=content,
            job_title=job_title,
            result=result
        )
        return jsonify({'id': analysis_id, 'result': result})
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/api/scrape-url', methods=['POST'])
@login_required
def api_scrape_url():
    data = request.get_json(force=True, silent=True) or {}
    url = data.get('url', '').strip()
    if not url:
        return jsonify({'success': False, 'error': 'URL is required'}), 400
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    result = url_scraper.scrape_with_status(url)
    return jsonify(result)

@app.route('/api/ocr', methods=['POST'])
@login_required
def api_ocr():
    data = request.get_json(force=True, silent=True) or {}
    image_b64 = data.get('image', '')
    if not image_b64:
        return jsonify({'success': False, 'error': 'No image provided'}), 400
    try:
        import pytesseract
        from PIL import Image
        img_bytes = base64.b64decode(image_b64.split(',')[-1])
        img = Image.open(io.BytesIO(img_bytes))
        text = pytesseract.image_to_string(img)
        if text.strip():
            return jsonify({'success': True, 'text': text.strip()})
        return jsonify({'success': False, 'error': 'No text found in image'})
    except ImportError:
        return jsonify({'success': False, 'error': 'OCR engine not installed on server', 'fallback': True})
    except Exception as e:
        return jsonify({'success': False, 'error': f'OCR failed: {str(e)}'})

# ── AI Chat ───────────────────────────────────────────────────────────────
@app.route('/api/chat', methods=['POST'])
@login_required
def api_chat():
    data = request.get_json(force=True, silent=True) or {}
    message = data.get('message', '').strip()
    context = data.get('context', '')
    analysis = data.get('analysis')
    if not message:
        return jsonify({'error': 'Message required'}), 400
    response = ai_chat.chat(message, context, analysis)
    return jsonify({'response': response})

# ── Result ────────────────────────────────────────────────────────────────
@app.route('/result/<int:analysis_id>')
@login_required
def result(analysis_id):
    analysis = db.get_analysis(analysis_id, session['user_id'])
    if not analysis:
        return redirect(url_for('analyze'))
    return render_template('result.html', analysis=analysis)

@app.route('/api/feedback/<int:analysis_id>', methods=['POST'])
@login_required
def api_feedback(analysis_id):
    data = request.get_json(force=True, silent=True) or {}
    is_correct = data.get('is_correct', True)
    db.save_feedback(analysis_id, session['user_id'], is_correct)
    return jsonify({'message': 'Thank you for your feedback!'})

# ── History / Insights ────────────────────────────────────────────────────
@app.route('/history')
@login_required
def history():
    analyses = db.get_all_analyses(session['user_id'])
    return render_template('history.html', analyses=analyses)

@app.route('/insights')
@login_required
def insights():
    stats = db.get_user_stats(session['user_id'])
    ins = db.get_insights_data(session['user_id'])
    analyses = db.get_all_analyses(session['user_id'])
    return render_template('insights.html', stats=stats, ins=ins, analyses=analyses)

# ── Job Portal ────────────────────────────────────────────────────────────
@app.route('/jobs')
@login_required
def jobs():
    search = request.args.get('search', '')
    status_filter = request.args.get('status', 'all')
    job_list = db.get_jobs(search, status_filter)
    return render_template('jobs.html', jobs=job_list, search=search, status_filter=status_filter)

@app.route('/jobs/<int:job_id>')
@login_required
def job_detail(job_id):
    job = db.get_job(job_id)
    if not job:
        return redirect(url_for('jobs'))
    is_saved = db.is_job_saved(job_id, session['user_id'])
    already_applied = db.already_applied(job_id, session['user_id'])
    return render_template('job_detail.html', job=job, is_saved=is_saved, already_applied=already_applied)

@app.route('/api/jobs/<int:job_id>/apply', methods=['POST'])
@login_required
def api_apply(job_id):
    try:
        import uuid, os
        data = {
            'full_name': request.form.get('full_name', '').strip(),
            'email': request.form.get('email', '').strip(),
            'phone': request.form.get('phone', '').strip(),
            'resume_filename': ''
        }
        if not data['full_name'] or not data['email'] or not data['phone']:
            return jsonify({'error': 'Name, email, and phone are required'}), 400
        resume_file = request.files.get('resume')
        if resume_file and resume_file.filename:
            ext = os.path.splitext(resume_file.filename)[1].lower()
            if ext not in ['.pdf', '.doc', '.docx']:
                return jsonify({'error': 'Only PDF, DOC, and DOCX files are allowed'}), 400
            safe_name = f"{uuid.uuid4().hex}{ext}"
            uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads')
            os.makedirs(uploads_dir, exist_ok=True)
            resume_file.save(os.path.join(uploads_dir, safe_name))
            data['resume_filename'] = resume_file.filename
        app_id = db.apply_for_job(job_id, session['user_id'], data)
        return jsonify({'application_id': app_id, 'message': 'Application submitted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/jobs/<int:job_id>/save', methods=['POST'])
@login_required
def api_save_job(job_id):
    saved = db.toggle_save_job(job_id, session['user_id'])
    return jsonify({'saved': saved})

@app.route('/my-applications')
@login_required
def my_applications():
    applications = db.get_applications(session['user_id'])
    saved_jobs = db.get_saved_jobs(session['user_id'])
    return render_template('my_applications.html', applications=applications, saved_jobs=saved_jobs)

# ── Cybercrime Report ──────────────────────────────────────────────────────
@app.route('/report')
@login_required
def report_page():
    return render_template('cybercrime.html')

@app.route('/api/report', methods=['POST'])
@login_required
def api_report():
    data = request.get_json(force=True, silent=True) or {}
    report_id = db.create_report(session['user_id'], data)
    return jsonify({'report_id': report_id, 'message': 'Report submitted to cybercrime portal'})

# ── Profile ───────────────────────────────────────────────────────────────
@app.route('/profile')
@login_required
def profile():
    user = db.get_user(session['user_id'])
    stats = db.get_user_stats(session['user_id'])
    return render_template('profile.html', user=user, stats=stats)

@app.route('/api/profile', methods=['POST'])
@login_required
def api_update_profile():
    data = request.get_json(force=True, silent=True) or {}
    db.update_user(session['user_id'], data)
    if data.get('full_name'):
        session['full_name'] = data['full_name']
    return jsonify({'message': 'Profile updated successfully'})

# ── Admin — Overview ──────────────────────────────────────────────────────
@app.route('/admin')
@admin_required
def admin_overview():
    stats = db.get_admin_stats()
    analytics = db.get_platform_analytics()
    return render_template('admin_overview.html', stats=stats, analytics=analytics)

@app.route('/admin/analytics')
@admin_required
def admin_analytics():
    stats = db.get_admin_stats()
    analytics = db.get_platform_analytics()
    return render_template('admin_analytics.html', stats=stats, analytics=analytics)

@app.route('/admin/feedback')
@admin_required
def admin_feedback():
    feedback_stats = db.get_admin_feedback_stats()
    reports = db.get_all_reports()
    return render_template('admin_feedback.html', feedback_stats=feedback_stats, reports=reports)

@app.route('/api/admin/reports/<int:report_id>/action', methods=['POST'])
@admin_required
def api_admin_report_action(report_id):
    data = request.get_json(force=True, silent=True) or {}
    status = data.get('status', 'reviewed')
    db.update_report_status(report_id, status)
    db.log_admin_action(session['user_id'], f'report_{status}', f'report:{report_id}')
    return jsonify({'message': f'Report marked as {status}'})

# ── Admin — User Management ───────────────────────────────────────────────
@app.route('/admin/users')
@admin_required
def admin_users():
    users = db.get_all_users()
    return render_template('admin_users.html', users=users)

@app.route('/api/admin/users/<int:user_id>/status', methods=['POST'])
@admin_required
def api_admin_user_status(user_id):
    data = request.get_json(force=True, silent=True) or {}
    status = data.get('status', 'Active')
    db.update_user_status(user_id, status)
    db.log_admin_action(session['user_id'], f'user_{status.lower()}', f'user:{user_id}')
    return jsonify({'message': f'User status set to {status}'})

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def api_admin_delete_user(user_id):
    if user_id == session['user_id']:
        return jsonify({'error': 'Cannot delete your own account'}), 400
    db.delete_user(user_id)
    db.log_admin_action(session['user_id'], 'user_deleted', f'user:{user_id}')
    return jsonify({'message': 'User deleted'})

# ── Admin — Job Management ────────────────────────────────────────────────
@app.route('/admin/jobs')
@admin_required
def admin_jobs_page():
    all_jobs = db.get_jobs()
    return render_template('admin_jobs.html', jobs=all_jobs)

@app.route('/api/admin/jobs', methods=['POST'])
@admin_required
def api_admin_add_job():
    data = request.get_json()
    if not data.get('title') or not data.get('company'):
        return jsonify({'error': 'Title and company are required'}), 400
    # Auto-score the job description using AI
    if data.get('description'):
        detection = ai_detector.analyze(data['description'])
        if 'ai_score' not in data or not data['ai_score']:
            if detection['result'] == 'safe':
                data['ai_score'] = detection['confidence_score']
            else:
                data['ai_score'] = 100 - detection['confidence_score']
        if 'verification_status' not in data or not data['verification_status']:
            data['verification_status'] = 'verified' if detection['result'] == 'safe' else 'suspicious'
    job_id = db.add_job(data)
    db.log_admin_action(session['user_id'], 'job_added', f'job:{job_id}')
    return jsonify({'job_id': job_id, 'message': 'Job added successfully'})

@app.route('/api/admin/jobs/<int:job_id>', methods=['PUT', 'DELETE'])
@admin_required
def api_admin_job(job_id):
    if request.method == 'DELETE':
        db.delete_job(job_id)
        db.log_admin_action(session['user_id'], 'job_deleted', f'job:{job_id}')
        return jsonify({'message': 'Job deleted'})
    data = request.get_json(force=True, silent=True) or {}
    db.update_job(job_id, data)
    db.log_admin_action(session['user_id'], 'job_updated', f'job:{job_id}')
    return jsonify({'message': 'Job updated successfully'})

# ── Health ─────────────────────────────────────────────────────────────────
@app.route('/api/healthz')
def healthz():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    db.init_db()
    db.seed_data()
    # Pre-train the ML model at startup
    try:
        ai_detector.get_model()
        print("ML model ready")
    except Exception as e:
        print(f"ML model warning: {e}")
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
