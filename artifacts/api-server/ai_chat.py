import requests
import json
import re

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

# ── Smart knowledge-base fallback (works without Ollama) ───────────────────

KB = [
    # Warning signs
    (r'warning sign|red flag|scam sign|fake sign|how.*know.*fake|identify.*fake|spot.*scam',
     "🚨 <strong>Top Job Scam Warning Signs:</strong><br>"
     "• Asked to pay any fee (registration, training, deposit)<br>"
     "• WhatsApp/Telegram-only hiring — no official email<br>"
     "• Unrealistic salary: ₹5000/day, ₹1 lakh/month for basic tasks<br>"
     "• 'No experience, no interview, instant selection'<br>"
     "• Overseas job with free visa + processing fee required<br><br>"
     "<strong>Tip:</strong> Legitimate employers <em>never</em> ask you to pay to get hired."),

    # Fee scams
    (r'registration fee|joining fee|advance fee|pay.*fee|asked.*pay|deposit',
     "🚫 <strong>Fee-Based Scam — Very Common!</strong><br>"
     "Any job asking you to pay a fee upfront is almost certainly a scam.<br><br>"
     "• Registration/joining fee<br>"
     "• Training fee<br>"
     "• Security deposit<br>"
     "• Visa/processing fee<br><br>"
     "<strong>Rule:</strong> Real companies pay <em>you</em> — you never pay them. Report at <strong>cybercrime.gov.in</strong>."),

    # Verify company
    (r'verify.*company|check.*company|real.*company|company.*real|how.*confirm|is.*legitimate',
     "🔍 <strong>How to Verify a Company:</strong><br>"
     "• Search company name on <strong>LinkedIn</strong> — check employee count & reviews<br>"
     "• Look up on <strong>MCA (mca.gov.in)</strong> for official registration<br>"
     "• Check <strong>Glassdoor</strong> for real employee reviews<br>"
     "• Visit only <strong>official company website</strong> — not third-party links<br>"
     "• Call the company's official landline to confirm the job opening<br><br>"
     "<strong>Tip:</strong> Never trust recruiters who only contact via WhatsApp/Telegram."),

    # Report cybercrime
    (r'report.*cybercrime|report.*crime|report.*fraud|report.*scam|cyber.*crime|1930|cybercrime\.gov',
     "📋 <strong>How to Report Job Fraud in India:</strong><br>"
     "• <strong>Online:</strong> cybercrime.gov.in → File complaint under 'Online Financial Fraud'<br>"
     "• <strong>Helpline:</strong> Call <strong>1930</strong> (Cyber Crime Helpline, 24/7)<br>"
     "• <strong>Police:</strong> File FIR at local cyber cell<br>"
     "• <strong>NCCRP:</strong> National Cyber Crime Reporting Portal<br><br>"
     "<strong>Tip:</strong> Screenshot all fraudulent messages and save the scammer's number before reporting."),

    # WhatsApp/Telegram hiring
    (r'whatsapp.*job|telegram.*job|whatsapp.*hiring|job.*whatsapp|job.*telegram',
     "⚠️ <strong>WhatsApp/Telegram-Only Jobs are Scams!</strong><br>"
     "Legitimate companies use:<br>"
     "• Official company email (@companyname.com)<br>"
     "• LinkedIn, Naukri, Indeed portals<br>"
     "• Company website careers page<br><br>"
     "They do <strong>NOT</strong> recruit via anonymous WhatsApp groups, Telegram channels, or random DMs.<br><br>"
     "<strong>Action:</strong> Block and report such numbers immediately."),

    # Government job scams
    (r'government job|ssc|upsc|railway|post office|government.*vacancy|fake.*government',
     "🏛️ <strong>Fake Government Job Scams:</strong><br>"
     "Real government jobs in India:<br>"
     "• Are advertised on <strong>official websites only</strong> (ssc.nic.in, upsc.gov.in, etc.)<br>"
     "• <strong>Never</strong> require advance/registration fees<br>"
     "• Have proper exam dates, admit cards, and official notifications<br><br>"
     "Scam signs: 'Guaranteed selection without exam', 'Pay ₹500 for joining letter'<br><br>"
     "<strong>Tip:</strong> Always verify on the official .gov.in domain."),

    # Overseas job scams
    (r'abroad|overseas|foreign.*job|dubai|canada|uk.*job|usa.*job|singapore.*job|visa.*fee',
     "✈️ <strong>Overseas Job Scam Alert:</strong><br>"
     "Genuine international employers:<br>"
     "• Work through <strong>NASSCOM/MEA-approved</strong> recruitment agencies<br>"
     "• Never ask for visa/processing fees upfront<br>"
     "• Provide verifiable job offer letters on company letterhead<br><br>"
     "Red flags: Free visa + processing fee, WhatsApp-only contact, salary too high for role<br><br>"
     "<strong>Tip:</strong> Check agency registration at <strong>mea.gov.in</strong> before paying anything."),

    # MLM/pyramid
    (r'mlm|network marketing|pyramid|binary plan|direct sell|refer.*earn|downline',
     "🔺 <strong>MLM / Pyramid Scheme Warning:</strong><br>"
     "These are disguised as 'business opportunities' but are NOT jobs.<br>"
     "• You earn mainly by <strong>recruiting others</strong>, not selling products<br>"
     "• Requires paying to join / buying inventory<br>"
     "• Income depends on how many people you recruit<br><br>"
     "These are often illegal in India under the Prize Chits & Money Circulation Schemes Act.<br><br>"
     "<strong>Tip:</strong> Report to your state's economic offences wing."),

    # How JobGuard works
    (r'how.*work|how.*jobguard|how.*detect|how.*model|ml model|algorithm|fraud score.*mean|what.*score',
     "🤖 <strong>How JobGuard AI Works:</strong><br>"
     "JobGuard uses a <strong>hybrid detection system</strong>:<br>"
     "• <strong>ML Engine (70%):</strong> TF-IDF + Logistic Regression + SVM ensemble trained on 270+ job samples<br>"
     "• <strong>Rules Engine (30%):</strong> 20+ keyword patterns for scam signals<br>"
     "• <strong>Domain Trust:</strong> Bonus for LinkedIn, Naukri, Glassdoor URLs<br><br>"
     "<strong>Fraud Score:</strong> 0–35 = Safe ✅ | 36–65 = Suspicious ⚠️ | 66–100 = Fake 🚫"),

    # Safe job tips
    (r'safe.*job|stay safe|protect.*myself|safety tip|job hunting safe|how.*apply safe',
     "🛡️ <strong>Safe Job Hunting Tips:</strong><br>"
     "• Only apply via <strong>official portals</strong>: LinkedIn, Naukri, Indeed, company websites<br>"
     "• <strong>Never pay</strong> any fee to get hired<br>"
     "• <strong>Verify</strong> the company on LinkedIn before sharing personal info<br>"
     "• Use <strong>JobGuard AI</strong> to scan suspicious job postings<br>"
     "• <strong>Trust your instincts</strong> — if it sounds too good, it probably is<br><br>"
     "<strong>Tip:</strong> A legitimate offer will always wait for you to verify it."),

    # Salary unrealistic
    (r'unrealistic salary|too good|earn.*daily|earn.*lakh|5000 per day|guaranteed income|earn.*without',
     "💰 <strong>Unrealistic Salary = Big Red Flag:</strong><br>"
     "Typical legitimate salaries in India:<br>"
     "• Fresher IT: ₹3–6 LPA | Experienced: ₹8–20+ LPA<br>"
     "• Data Entry/BPO: ₹15,000–25,000/month<br>"
     "• 'Earn ₹5000/day doing simple tasks' — <strong>always a scam</strong><br><br>"
     "No legitimate employer offers ₹50,000/week for zero-skill work.<br><br>"
     "<strong>Tip:</strong> Research typical salaries on <strong>Glassdoor</strong> or <strong>AmbitionBox</strong>."),

    # What to do after being scammed
    (r'already.*paid|got scammed|lost money|cheated|what.*do.*now|i was scammed',
     "🆘 <strong>If You Were Scammed — Act Immediately:</strong><br>"
     "1. <strong>Call 1930</strong> (Cyber Crime Helpline) right now<br>"
     "2. File complaint at <strong>cybercrime.gov.in</strong><br>"
     "3. <strong>Block</strong> all contact with the scammer<br>"
     "4. <strong>Contact your bank</strong> to reverse the transaction if recent<br>"
     "5. Collect evidence: screenshots, transaction IDs, phone numbers<br><br>"
     "<strong>Quick action (within 24hrs)</strong> increases chances of money recovery."),

    # Result explanation
    (r'why.*fake|why.*suspicious|why.*flagged|explain.*result|what.*mean.*result|reason.*fake',
     "📊 <strong>Understanding Your Result:</strong><br>"
     "JobGuard flags jobs based on:<br>"
     "• <strong>Fee demands</strong> — registration, training, deposit (+40 pts)<br>"
     "• <strong>WhatsApp/Telegram hiring</strong> — no official channel (+20 pts)<br>"
     "• <strong>Unrealistic earnings</strong> — ₹5000/day, guaranteed income (+28 pts)<br>"
     "• <strong>MLM/pyramid language</strong> — refer & earn, downline (+32 pts)<br><br>"
     "Safe signals like 'years experience', 'CTC', 'official portal' reduce the score.<br><br>"
     "<strong>Tip:</strong> Check the 'Key Reasons' section on the result page for specifics."),
]

def _kb_response(message):
    msg_lower = message.lower()
    for pattern, response in KB:
        if re.search(pattern, msg_lower):
            return response
    # Generic fallback
    return (
        "🛡️ <strong>JobGuard AI Assistant</strong><br><br>"
        "I can help you with:<br>"
        "• <strong>Warning signs</strong> of fake jobs<br>"
        "• <strong>Verifying</strong> a company's legitimacy<br>"
        "• <strong>Reporting</strong> cybercrime (cybercrime.gov.in | 1930)<br>"
        "• Understanding your <strong>fraud score result</strong><br>"
        "• <strong>Safe job hunting</strong> tips<br><br>"
        "Try asking: <em>'What are the warning signs of a fake job?'</em> or <em>'How do I verify a company?'</em>"
    )

def chat(message, context='', analysis=None):
    context_parts = []
    if analysis:
        context_parts.append(
            f"Current Analysis — Result: {analysis.get('result','unknown').upper()}, "
            f"Fraud Score: {analysis.get('fraud_score','N/A')}/100, "
            f"Risk Level: {analysis.get('risk_level','unknown').upper()}"
        )
    if context:
        context_parts.append(f"Additional context: {context}")

    full_context = '\n'.join(context_parts)
    context_block = ('Context:\n' + full_context + '\n\n') if full_context else ''
    prompt = f"{SYSTEM_PROMPT}\n\n{context_block}User question: {message}\n\nRespond in HTML format:"

    # Try Ollama first
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
            timeout=12
        )
        if resp.status_code == 200:
            data = resp.json()
            response_text = data.get('response', '').strip()
            if response_text:
                return response_text
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        pass
    except Exception:
        pass

    # Ollama unavailable — use smart knowledge-base fallback
    return _kb_response(message)


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
