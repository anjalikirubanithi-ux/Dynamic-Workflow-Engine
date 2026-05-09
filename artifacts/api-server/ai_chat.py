import re
import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3"

# ── Knowledge base for fallback responses ──────────────────────────────────
KB = {
    'registration_fee': {
        'triggers': ['registration fee', 'joining fee', 'advance fee', 'deposit', 'pay to join', 'pay first'],
        'response': (
            "🚨 <strong>Red Flag: Advance/Registration Fee</strong><br><br>"
            "Legitimate employers <strong>NEVER</strong> ask candidates to pay money to get hired. "
            "Any job requiring registration fees, training fees, security deposits, or advance payments "
            "is almost certainly a <strong>scam</strong>.<br><br>"
            "<strong>What to do:</strong><br>"
            "• Do not pay any amount<br>"
            "• Block and report the contact<br>"
            "• File a complaint at <a href='https://cybercrime.gov.in' target='_blank'>cybercrime.gov.in</a>"
        )
    },
    'daily_earnings': {
        'triggers': ['earn daily', '5000 daily', '3000 daily', 'earn per day', 'daily income', 'earn 1000', 'earn 2000'],
        'response': (
            "💰 <strong>Red Flag: Unrealistic Daily Earnings</strong><br><br>"
            "Promises of ₹3,000–₹10,000 per day from simple tasks like data entry, "
            "typing, or clicking links are <strong>common scam patterns</strong>.<br><br>"
            "Real salaries are paid monthly. High-paying legitimate jobs require "
            "specific qualifications and a proper interview process.<br><br>"
            "<strong>Reality check:</strong> A ₹5,000/day job = ₹1.5 lakh/month — "
            "that's an executive-level salary, not for unskilled work."
        )
    },
    'whatsapp_telegram': {
        'triggers': ['whatsapp', 'telegram', 'join group', 'contact on whatsapp'],
        'response': (
            "📱 <strong>Red Flag: WhatsApp/Telegram-Only Contact</strong><br><br>"
            "Legitimate companies use official email, company career portals, or "
            "LinkedIn for hiring — <strong>not</strong> WhatsApp or Telegram groups.<br><br>"
            "Scammers prefer these platforms because:<br>"
            "• Messages can be deleted easily<br>"
            "• Harder to trace the fraudster<br>"
            "• Easy to add victims to group chats<br><br>"
            "<strong>Rule:</strong> If a recruiter only wants to communicate on WhatsApp/Telegram, walk away."
        )
    },
    'why_fake': {
        'triggers': ['why fake', 'why flagged', 'why marked', 'why suspicious', 'reason for fake', 'explain result'],
        'response': (
            "🔍 <strong>Why Was This Job Flagged?</strong><br><br>"
            "Our AI model analyzed the content using a combination of:<br>"
            "• <strong>ML Model</strong>: Trained on thousands of real/fake job postings using TF-IDF + Logistic Regression<br>"
            "• <strong>Fraud Score Engine</strong>: Keyword patterns, urgency signals, fee demands<br>"
            "• <strong>Domain & Contact Analysis</strong>: Suspicious URLs, generic contacts<br><br>"
            "A fraud score of 66+ = Fake, 36–65 = Suspicious, 0–35 = Safe.<br><br>"
            "Check the <strong>Key Reasons</strong> section above for the specific triggers found."
        )
    },
    'safe_job': {
        'triggers': ['why safe', 'is it safe', 'can i trust', 'should i apply', 'is it legitimate'],
        'response': (
            "✅ <strong>Job Appears Legitimate — Here's How to Stay Safe</strong><br><br>"
            "Our AI scored this job as safe, but always take precautions:<br><br>"
            "1. <strong>Verify the company</strong> on MCA21 portal (mca.gov.in)<br>"
            "2. <strong>Apply only</strong> through the official company careers page<br>"
            "3. <strong>Never share</strong> Aadhaar, PAN, or bank details before a formal offer<br>"
            "4. <strong>Meet in person</strong> at a real company office before accepting<br>"
            "5. <strong>Get the offer in writing</strong> on company letterhead with seal"
        )
    },
    'common_scams': {
        'triggers': ['common scam', 'types of fraud', 'scam indicators', 'how to identify', 'what to look for'],
        'response': (
            "🛡️ <strong>Common Job Scam Indicators</strong><br><br>"
            "<strong>1. Advance Fee Scams</strong> — Pay to get the job<br>"
            "<strong>2. Data Entry Scams</strong> — Earn ₹500/page typing at home<br>"
            "<strong>3. Overseas Job Fraud</strong> — Visa + processing fee required<br>"
            "<strong>4. WhatsApp Interview Scams</strong> — Hired instantly via chat<br>"
            "<strong>5. Government Job Scams</strong> — Fake vacancies requiring payment<br>"
            "<strong>6. MLM/Network Marketing</strong> — Join and recruit others<br>"
            "<strong>7. Lottery/Prize Scams</strong> — You won a job lottery<br><br>"
            "<strong>Golden Rule:</strong> If it sounds too good to be true, it always is."
        )
    },
    'report': {
        'triggers': ['how to report', 'report cybercrime', 'where to report', 'file complaint'],
        'response': (
            "📋 <strong>How to Report Job Fraud in India</strong><br><br>"
            "<strong>Official Channels:</strong><br>"
            "• <a href='https://cybercrime.gov.in' target='_blank'>cybercrime.gov.in</a> — National Cybercrime Reporting Portal<br>"
            "• Cybercrime helpline: <strong>1930</strong><br>"
            "• Local police cybercrime cell<br>"
            "• Report on JobGuard using the 'Report Cybercrime' button<br><br>"
            "<strong>Keep as evidence:</strong><br>"
            "• Screenshots of conversations<br>"
            "• Phone numbers used by the scammer<br>"
            "• Bank transaction details (if you paid)<br>"
            "• URLs and email addresses"
        )
    },
    'protect': {
        'triggers': ['how to protect', 'stay safe', 'avoid scam', 'tips', 'safety advice'],
        'response': (
            "🛡️ <strong>How to Protect Yourself from Job Scams</strong><br><br>"
            "✅ Always apply through official company websites<br>"
            "✅ Verify company on MCA21 portal before sharing documents<br>"
            "✅ Never pay any fee to get a job<br>"
            "✅ Do not join WhatsApp/Telegram groups for hiring<br>"
            "✅ Be suspicious of unusually high salaries for unskilled work<br>"
            "✅ Video call with HR to verify identity before proceeding<br>"
            "✅ Check company email domain (not @gmail.com)<br>"
            "✅ Search the company name + 'scam' on Google<br>"
            "✅ Trust your instincts — if it feels wrong, walk away"
        )
    },
    'ml_model': {
        'triggers': ['how does ai work', 'how does model work', 'machine learning', 'ml model', 'how does it detect'],
        'response': (
            "🤖 <strong>How JobGuard AI Works</strong><br><br>"
            "Our fraud detection uses a <strong>hybrid AI architecture</strong>:<br><br>"
            "<strong>1. ML Model (scikit-learn)</strong><br>"
            "• TF-IDF vectorization of job text<br>"
            "• Logistic Regression classifier trained on labeled data<br>"
            "• Outputs a fraud probability score (0–100)<br><br>"
            "<strong>2. Rules Engine</strong><br>"
            "• Pattern matching for known scam phrases<br>"
            "• Urgency detection, fee keywords, contact method analysis<br><br>"
            "<strong>3. Blended Score</strong><br>"
            "• Final score = 65% ML + 35% Rules<br>"
            "• Score ≥ 66 → Fake | 36–65 → Suspicious | 0–35 → Safe"
        )
    },
}

FALLBACK_RESPONSE = (
    "🤔 I'm not sure about that specific question, but I can help with:<br><br>"
    "• <strong>Ask:</strong> 'Why was this job flagged?'<br>"
    "• <strong>Ask:</strong> 'Is it safe to apply?'<br>"
    "• <strong>Ask:</strong> 'What are common job scams?'<br>"
    "• <strong>Ask:</strong> 'How to protect myself?'<br>"
    "• <strong>Ask:</strong> 'How to report cybercrime?'<br><br>"
    "I'm here to help you stay safe while job hunting! 🛡️"
)

def chat(message, context='', analysis=None):
    """Try Ollama first, fall back to knowledge base."""
    # Try Ollama
    try:
        ollama_resp = _ask_ollama(message, context, analysis)
        if ollama_resp:
            return ollama_resp
    except Exception:
        pass

    # Knowledge base fallback
    return _kb_response(message, context, analysis)

def _ask_ollama(message, context, analysis):
    system_prompt = (
        "You are JobGuard AI Assistant, an expert in job fraud detection in India. "
        "Help users understand job fraud, analyze suspicious postings, and stay safe. "
        "Be concise (max 150 words), use bullet points, and be direct. "
        "Format responses in HTML with <br> for line breaks and <strong> for emphasis."
    )
    if analysis:
        context = (
            f"Job Analysis Result: {analysis.get('result','unknown').upper()}, "
            f"Fraud Score: {analysis.get('fraud_score', 'N/A')}/100, "
            f"Risk Level: {analysis.get('risk_level','unknown')}"
        )
    prompt = f"{system_prompt}\n\nContext: {context}\n\nUser: {message}"

    resp = requests.post(OLLAMA_URL, json={
        'model': OLLAMA_MODEL,
        'prompt': prompt,
        'stream': False,
        'options': {'num_predict': 200}
    }, timeout=8)

    if resp.status_code == 200:
        data = resp.json()
        return data.get('response', '').strip()
    return None

def _kb_response(message, context, analysis):
    msg_lower = message.lower()

    # Check each category
    for category, data in KB.items():
        for trigger in data['triggers']:
            if trigger in msg_lower:
                return data['response']

    # Context-aware responses
    if analysis:
        result = analysis.get('result', '')
        score = analysis.get('fraud_score', 50)
        if any(w in msg_lower for w in ['explain', 'tell me', 'why', 'what', 'how']):
            if result == 'fake':
                return KB['why_fake']['response']
            elif result == 'safe':
                return KB['safe_job']['response']

    # Greeting
    if any(w in msg_lower for w in ['hello', 'hi', 'hey', 'help', 'start']):
        return (
            "👋 <strong>Hello! I'm JobGuard AI Assistant.</strong><br><br>"
            "I can help you:<br>"
            "• Understand why a job was flagged as fake<br>"
            "• Identify red flags in job postings<br>"
            "• Learn how to protect yourself from scams<br>"
            "• Know how to report cybercrime<br><br>"
            "What would you like to know? 🛡️"
        )

    return FALLBACK_RESPONSE

def generate_briefing(stats, recent_analyses):
    """Generate a personalized AI safety briefing for the dashboard."""
    total = stats.get('total', 0)
    fake = stats.get('fake', 0)
    safe = stats.get('safe', 0)

    if total == 0:
        return (
            "👋 <strong>Welcome to JobGuard AI!</strong> You haven't analyzed any jobs yet. "
            "Use the <strong>Analyze Job</strong> feature to check if a job is real or fake before applying."
        )

    fake_pct = round(fake / total * 100) if total > 0 else 0

    if fake_pct >= 60:
        tone = (
            f"⚠️ <strong>High Risk Alert:</strong> {fake_pct}% of the jobs you've analyzed are fake. "
            "Be extra cautious. Avoid jobs offering unrealistic salaries or asking for fees."
        )
    elif fake_pct >= 30:
        tone = (
            f"🟡 <strong>Stay Alert:</strong> {fake_pct}% of your analyzed jobs showed fraud indicators. "
            "Always verify companies before applying."
        )
    else:
        tone = (
            f"✅ <strong>Looking Good:</strong> Most jobs you've analyzed appear legitimate. "
            "Keep using JobGuard to stay protected."
        )

    # Check for patterns in recent analyses
    recent_types = [a.get('input_type', '') for a in recent_analyses]
    tips = []
    if 'url' not in recent_types:
        tips.append("Try the <strong>URL Analysis</strong> feature to scan job links directly")
    if fake > 0:
        tips.append("Report fake jobs via the <strong>Cybercrime Report</strong> section")
    tips.append("Always apply through official company career portals")

    tip_html = '<br>'.join(f"• {t}" for t in tips[:2])
    return f"{tone}<br><br><strong>Tips:</strong><br>{tip_html}"
