import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3"

SYSTEM_PROMPT = """You are JobGuard AI Assistant — an expert in job fraud detection, cybercrime awareness, and safe job hunting in India.

Your role:
- Help users understand whether a job posting is fake or legitimate
- Explain fraud indicators found in job postings
- Guide users on how to protect themselves from job scams
- Answer questions about the JobGuard AI analysis results
- Provide advice on reporting cybercrime related to job fraud

Key facts you know:
- Fraud Score 0–35 = SAFE (green), 36–65 = SUSPICIOUS (orange), 66–100 = FAKE (red)
- JobGuard uses ML (TF-IDF + Logistic Regression + SVM ensemble) + keyword rules engine
- Common job scams in India: advance/registration fee, WhatsApp/Telegram-only hiring, guaranteed daily income, MLM/pyramid schemes, fake government jobs, overseas job fraud
- Legitimate employers NEVER ask candidates to pay money to get hired
- Official cybercrime portal: cybercrime.gov.in, helpline: 1930

Response rules:
- Be concise (max 120 words per response)
- Use HTML formatting: <strong> for emphasis, <br> for line breaks, bullet points with •
- Be direct and helpful
- If asked something unrelated to jobs/fraud/career, politely redirect to your expertise
- Always end with a helpful action tip when relevant"""

OLLAMA_UNAVAILABLE_MSG = (
    "⚠️ <strong>AI Assistant Offline</strong><br><br>"
    "The Ollama AI engine is not running. To enable the full AI chat:<br><br>"
    "1. Install Ollama from <strong>ollama.com</strong><br>"
    "2. Run: <code>ollama pull llama3</code><br>"
    "3. Start: <code>ollama serve</code><br><br>"
    "Once Ollama is running, the AI assistant will respond intelligently to all your questions about job fraud, safety tips, and analysis results."
)

def chat(message, context='', analysis=None):
    context_parts = []
    if analysis:
        context_parts.append(
            f"Current Analysis — Result: {analysis.get('result','unknown').upper()}, "
            f"Fraud Score: {analysis.get('fraud_score','N/A')}/100, "
            f"Risk Level: {analysis.get('risk_level','unknown').upper()}, "
            f"Key Reasons: {', '.join(analysis.get('key_reasons', [])[:3])}"
        )
    if context:
        context_parts.append(f"Additional context: {context}")

    full_context = '\n'.join(context_parts)
    context_block = ('Context:\n' + full_context + '\n\n') if full_context else ''
    prompt = f"{SYSTEM_PROMPT}\n\n{context_block}User question: {message}\n\nRespond in HTML format:"

    try:
        resp = requests.post(
            OLLAMA_URL,
            json={
                'model': OLLAMA_MODEL,
                'prompt': prompt,
                'stream': False,
                'options': {
                    'num_predict': 250,
                    'temperature': 0.7,
                    'top_p': 0.9,
                }
            },
            timeout=15
        )
        if resp.status_code == 200:
            data = resp.json()
            response_text = data.get('response', '').strip()
            if response_text:
                return response_text
        return OLLAMA_UNAVAILABLE_MSG
    except requests.exceptions.ConnectionError:
        return OLLAMA_UNAVAILABLE_MSG
    except requests.exceptions.Timeout:
        return (
            "⏳ <strong>AI response timed out.</strong><br><br>"
            "The Ollama model is taking too long. Try asking a shorter question, "
            "or check that Ollama is running properly with <code>ollama serve</code>."
        )
    except Exception as e:
        return OLLAMA_UNAVAILABLE_MSG


def generate_briefing(stats, recent_analyses):
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

    recent_types = [a.get('input_type', '') for a in recent_analyses]
    tips = []
    if 'url' not in recent_types:
        tips.append("Try the <strong>URL Analysis</strong> feature to scan job links directly")
    if fake > 0:
        tips.append("Report fake jobs via the <strong>Cybercrime Report</strong> section")
    tips.append("Always apply through official company career portals")

    tip_html = '<br>'.join(f"• {t}" for t in tips[:2])
    return f"{tone}<br><br><strong>Tips:</strong><br>{tip_html}"
