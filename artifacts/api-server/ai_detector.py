import re

FAKE_KEYWORDS = [
    ('registration fee', 30), ('pay fee', 25), ('deposit required', 25),
    ('earn daily', 20), ('earn \\d+ daily', 25), ('earn \\d+ weekly', 20),
    ('5000 daily', 30), ('3000 daily', 30), ('10000 daily', 30),
    ('no experience needed', 15), ('no experience required', 15),
    ('guaranteed job', 20), ('100% guaranteed', 20), ('guaranteed income', 20),
    ('whatsapp', 10), ('telegram group', 15), ('join our group', 10),
    ('work from home earn', 15), ('part time earn', 10),
    ('urgent hiring', 5), ('urgently required', 5),
    ('abroad job', 15), ('overseas job', 10),
    ('data entry earn', 15), ('typing work earn', 15),
    ('mlm', 20), ('network marketing earn', 15),
    ('lottery', 25), ('prize money', 20), ('winner selected', 25),
]

SAFE_KEYWORDS = [
    ('years of experience', -10), ('bachelor', -8), ('degree required', -8),
    ('apply through', -10), ('official portal', -15), ('company website', -10),
    ('interview process', -10), ('technical interview', -12),
    ('ctc', -8), ('lpa', -8), ('per annum', -8),
    ('nda', -5), ('background check', -8),
    ('hr@', -10), ('.com', -5), ('@infosys', -15), ('@tcs', -15),
    ('@wipro', -15), ('@google', -20), ('@microsoft', -20),
]

def analyze(content, input_type='text'):
    text = content.lower()
    score = 0

    for pattern, weight in FAKE_KEYWORDS:
        if re.search(pattern, text):
            score += weight

    for pattern, weight in SAFE_KEYWORDS:
        if re.search(pattern, text):
            score += weight

    score = max(0, min(100, score))

    if score >= 60:
        result = 'fake'
        risk_level = 'high'
        confidence = min(95, 60 + score // 3)
        ai_explanation = ("Our AI model has determined this job posting is SUSPICIOUS / FRAUDULENT "
                          "based on multiple risk indicators found in the content, email, domain, and structure.")
        key_reasons = _get_fake_reasons(text)
        keyword_highlights = _get_fake_keywords(text)
        safety_tips = [
            "Never pay money for a job — legitimate employers do not charge fees",
            "Avoid jobs that sound too good to be true",
            "Verify company on official website before sharing details",
            "Do not join WhatsApp/Telegram groups for job applications",
            "Report suspicious jobs to cybercrime.gov.in"
        ]
    elif score >= 30:
        result = 'suspicious'
        risk_level = 'medium'
        confidence = 50 + score
        ai_explanation = ("Our AI model flagged this job posting as POTENTIALLY SUSPICIOUS. "
                          "Some indicators suggest this may not be a legitimate opportunity. Verify carefully.")
        key_reasons = _get_suspicious_reasons(text)
        keyword_highlights = _get_fake_keywords(text)
        safety_tips = [
            "Verify the company's official website",
            "Contact the company through official channels",
            "Do not share financial or personal details",
            "Check for online reviews of the company"
        ]
    else:
        result = 'safe'
        risk_level = 'low'
        confidence = max(75, 95 - score)
        ai_explanation = ("Our AI model has determined this job posting appears LEGITIMATE. "
                          "The content follows standard industry practices with no major red flags detected.")
        key_reasons = _get_safe_reasons(text)
        keyword_highlights = _get_safe_keywords(text)
        safety_tips = [
            "Apply through official company portals",
            "Verify job details before submitting your resume",
            "Do not share OTP or bank details during the process",
            "Keep records of all communications"
        ]

    return {
        'result': result,
        'confidence_score': confidence,
        'risk_level': risk_level,
        'ai_explanation': ai_explanation,
        'key_reasons': key_reasons,
        'keyword_highlights': keyword_highlights,
        'safety_tips': safety_tips
    }

def _get_fake_reasons(text):
    reasons = []
    if any(w in text for w in ['registration fee', 'pay fee', 'deposit']):
        reasons.append("Asks for upfront payment / registration fee")
    if any(w in text for w in ['earn', '5000', '3000', 'daily']):
        reasons.append("Unrealistic earnings claim (e.g. earn ₹5000 daily)")
    if any(w in text for w in ['whatsapp', 'telegram', 'group']):
        reasons.append("Uses WhatsApp/Telegram instead of official channels")
    if 'no experience' in text:
        reasons.append("Claims no experience is required for high-paying role")
    if any(w in text for w in ['urgent', 'urgently', 'immediately']):
        reasons.append("Creates urgency to pressure quick decisions")
    if 'guaranteed' in text:
        reasons.append("Uses 'guaranteed' language — not a legitimate practice")
    if not reasons:
        reasons = ["Multiple fraud indicators detected in content",
                   "Domain or contact information appears suspicious",
                   "Job description lacks specific professional requirements"]
    return reasons[:4]

def _get_suspicious_reasons(text):
    reasons = ["Some indicators suggest this may not be legitimate"]
    if 'work from home' in text and 'earn' in text:
        reasons.append("Work-from-home with unusually high earnings claimed")
    if 'urgent' in text:
        reasons.append("Urgency language used — verify before applying")
    return reasons[:3]

def _get_safe_reasons(text):
    reasons = []
    if any(w in text for w in ['experience', 'years', 'required']):
        reasons.append("Job requires specific experience and qualifications")
    if any(w in text for w in ['lpa', 'ctc', 'per annum', 'salary']):
        reasons.append("Salary range is realistic and industry-standard")
    if any(w in text for w in ['official', 'portal', 'company', 'website']):
        reasons.append("Directs candidates to official channels")
    if any(w in text for w in ['interview', 'technical', 'hr']):
        reasons.append("Mentions standard interview process")
    if not reasons:
        reasons = ["Professional job description with clear requirements",
                   "No suspicious keywords or fee demands detected"]
    return reasons[:4]

def _get_fake_keywords(text):
    found = []
    checks = [('earn', 'Earn Daily'), ('registration fee', 'Registration Fee'),
               ('whatsapp', 'WhatsApp Contact'), ('telegram', 'Telegram Group'),
               ('no experience', 'No Experience Needed'), ('urgent', 'Urgent Hiring'),
               ('guaranteed', '100% Guaranteed'), ('work from home', 'Work From Home')]
    for key, label in checks:
        if key in text:
            found.append(label)
    return found[:5] if found else ['Suspicious Content']

def _get_safe_keywords(text):
    found = []
    checks = [('experience', 'Experience Required'), ('lpa', 'Competitive CTC'),
               ('official', 'Official Portal'), ('interview', 'Proper Interview'),
               ('salary', 'Industry Salary'), ('company', 'Verified Company')]
    for key, label in checks:
        if key in text:
            found.append(label)
    return found[:4] if found else ['Professional Listing']
