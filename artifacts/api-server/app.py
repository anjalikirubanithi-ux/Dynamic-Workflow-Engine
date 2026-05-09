from flask import Flask, render_template, request, session, redirect, url_for, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
import database as db
import ai_detector
import os
from functools import wraps

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.environ.get('SECRET_KEY', 'jobguard-ai-secret-2025')

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
            return redirect(url_for('dashboard'))
        error = 'Invalid email or password'
    return render_template('login.html', error=error)

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
            return redirect(url_for('dashboard'))
    return render_template('register.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    stats = db.get_user_stats(session['user_id'])
    recent = db.get_recent_analyses(session['user_id'], limit=5)
    chart_data = db.get_chart_data(session['user_id'])
    return render_template('dashboard.html', stats=stats, recent=recent, chart_data=chart_data)

@app.route('/analyze')
@login_required
def analyze():
    return render_template('analyze.html')

@app.route('/api/analyze', methods=['POST'])
@login_required
def api_analyze():
    data = request.get_json()
    input_type = data.get('input_type', 'text')
    content = data.get('content', '')
    job_title = data.get('job_title', '')
    if not content:
        return jsonify({'error': 'Content is required'}), 400
    result = ai_detector.analyze(content, input_type)
    analysis_id = db.save_analysis(
        user_id=session['user_id'],
        input_type=input_type,
        content=content,
        job_title=job_title,
        result=result
    )
    return jsonify({'id': analysis_id, 'result': result})

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
    data = request.get_json()
    is_correct = data.get('is_correct', True)
    db.save_feedback(analysis_id, session['user_id'], is_correct)
    return jsonify({'message': 'Thank you for your feedback!'})

@app.route('/api/report', methods=['POST'])
@login_required
def api_report():
    data = request.get_json()
    report_id = db.create_report(session['user_id'], data)
    return jsonify({'report_id': report_id, 'message': 'Report submitted to cybercrime portal'})

@app.route('/history')
@login_required
def history():
    analyses = db.get_all_analyses(session['user_id'])
    return render_template('history.html', analyses=analyses)

@app.route('/insights')
@login_required
def insights():
    stats = db.get_user_stats(session['user_id'])
    chart_data = db.get_chart_data(session['user_id'])
    analyses = db.get_all_analyses(session['user_id'])
    return render_template('insights.html', stats=stats, chart_data=chart_data, analyses=analyses)

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
    data = request.get_json()
    app_id = db.apply_for_job(job_id, session['user_id'], data)
    return jsonify({'application_id': app_id, 'message': 'Application submitted successfully'})

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

@app.route('/report')
@login_required
def report_page():
    return render_template('cybercrime.html')

@app.route('/profile')
@login_required
def profile():
    user = db.get_user(session['user_id'])
    stats = db.get_user_stats(session['user_id'])
    return render_template('profile.html', user=user, stats=stats)

@app.route('/api/profile', methods=['POST'])
@login_required
def api_update_profile():
    data = request.get_json()
    db.update_user(session['user_id'], data)
    if data.get('full_name'):
        session['full_name'] = data['full_name']
    return jsonify({'message': 'Profile updated successfully'})

@app.route('/admin')
@admin_required
def admin_overview():
    stats = db.get_admin_stats()
    return render_template('admin_overview.html', stats=stats)

@app.route('/admin/feedback')
@admin_required
def admin_feedback():
    feedback_stats = db.get_admin_feedback_stats()
    reports = db.get_all_reports()
    return render_template('admin_feedback.html', feedback_stats=feedback_stats, reports=reports)

@app.route('/api/healthz')
def healthz():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    db.init_db()
    db.seed_data()
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
