import os
import re
import json
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'fraud_model.pkl')

TRAINING_DATA = [
    # FAKE (1)
    ("earn 5000 daily registration fee pay now whatsapp group data entry part time no experience", 1),
    ("urgent hiring work from home earn 50000 monthly no experience required pay deposit telegram join", 1),
    ("make money online 3000 daily guaranteed income no qualification needed registration charge advance", 1),
    ("abroad job visa provided earn 1 lakh monthly registration fee required whatsapp interview only", 1),
    ("part time work earn 500 per hour no experience needed join telegram group pay advance fee immediately", 1),
    ("online job data entry earn 2000 daily payment registration certificate required advance fee bank", 1),
    ("urgently required candidates earn 5 lakh monthly zero investment work from home mlm business scheme", 1),
    ("government job guaranteed vacancy pay 2000 registration immediately join whatsapp group", 1),
    ("work at home earn 8000 daily no interview no experience needed send advance fee bank transfer urgent", 1),
    ("lottery winner selected earn prize money claim fee required immediately telegram contact", 1),
    ("mlm network marketing earn unlimited income recruitment commission binary plan pyramid scheme", 1),
    ("overseas job offer 1 lakh monthly salary processing fee required join now whatsapp contact", 1),
    ("data entry typing job earn per page no experience needed pay joining fee advance", 1),
    ("modelling acting job earn lakhs no experience telegram whatsapp instant selection no interview", 1),
    ("earn money survey work home daily payment paypal registration fee 100 rupees advance", 1),
    ("youtube instagram social media manager earn 10000 daily whatsapp apply immediately no experience", 1),
    ("forex trading guaranteed profit investment plan earn daily income join whatsapp group telegram", 1),
    ("urgent need housewife student retired person earn 5000 weekly no investment telegram register now", 1),
    ("amazon flipkart product review earn 3000 daily whatsapp group registration fee required advance", 1),
    ("digital marketing earn 50000 monthly work from home no experience join telegram fee paid advance", 1),
    ("part time job earn 1000 per hour work from home whatsapp me immediately no experience student", 1),
    ("easy job earn 20000 weekly just share links telegram group registration 500 rupees advance fee", 1),
    ("call center job abroad salary 80000 monthly processing visa fee advance payment required urgent", 1),
    ("reseller job earn 3000 per order work from home no investment required just pay registration", 1),
    ("typing job earn 40 per page work from home submit 200 registration fee to start immediately", 1),
    # SAFE (0)
    ("software engineer 3 years experience python java required bachelor degree ctc 8 12 lpa apply portal", 0),
    ("data analyst sql python experience required salary 6 10 lpa technical interview official website", 0),
    ("frontend developer react javascript experience 2 years ctc 7 11 lpa work location bangalore office", 0),
    ("marketing executive 2 years experience mba preferred salary 4 6 lpa apply hr email resume required", 0),
    ("ui ux designer figma sketch experience 2 years portfolio required location pune salary 7 lpa", 0),
    ("product manager 5 years experience agile scrum background check required interview process stages", 0),
    ("content writer 1 year experience good english grammar editing skills monthly salary 20000 25000", 0),
    ("business analyst 3 years experience sql excel presentation skills ctc 8 14 lpa hyderabad location", 0),
    ("hr executive recruitment experience 2 years salary 3 5 lpa apply career page company website", 0),
    ("java backend developer spring boot microservices experience 4 years salary 12 18 lpa apply now", 0),
    ("devops engineer aws docker kubernetes experience required ctc 15 20 lpa bangalore hybrid office", 0),
    ("machine learning engineer tensorflow pytorch phd mtech preferred salary 20 35 lpa apply portal", 0),
    ("graphic designer adobe photoshop illustrator experience 2 years salary 25000 monthly portfolio", 0),
    ("sales executive 1 year experience communication skills salary 3 5 lpa incentives location mumbai", 0),
    ("customer support executive good communication skills rotational shifts salary 20000 25000 per month", 0),
    ("civil engineer 3 years site experience autocad proficiency salary 4 7 lpa degree required", 0),
    ("accountant tally gst knowledge 2 years experience salary 25000 35000 apply email resume", 0),
    ("python developer flask django rest api 3 years experience ctc 10 16 lpa work from home hybrid", 0),
    ("react native developer mobile app 2 years salary 8 12 lpa apply company portal official", 0),
    ("project manager pmp certification preferred 7 years experience salary 18 28 lpa location delhi", 0),
    ("full stack developer node react mongo 3 years ctc 10 15 lpa apply through linkedin company website", 0),
    ("ios developer swift objective c 4 years experience portfolio required salary 12 20 lpa", 0),
    ("cyber security analyst certified ethical hacker 3 years experience ctc 12 18 lpa", 0),
    ("qa engineer selenium automation testing 2 years experience salary 6 10 lpa apply portal", 0),
    ("network engineer cisco ccna certification 3 years experience salary 5 9 lpa location hyderabad", 0),
]

_model = None

def load_or_train_model():
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import Pipeline
        import joblib

        if os.path.exists(MODEL_PATH):
            try:
                return joblib.load(MODEL_PATH)
            except Exception:
                pass

        texts = [t for t, _ in TRAINING_DATA]
        labels = [l for _, l in TRAINING_DATA]
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=1000, sublinear_tf=True)),
            ('clf', LogisticRegression(max_iter=1000, C=2.0, class_weight='balanced'))
        ])
        pipeline.fit(texts, labels)
        try:
            joblib.dump(pipeline, MODEL_PATH)
        except Exception:
            pass
        return pipeline
    except ImportError:
        return None

def get_model():
    global _model
    if _model is None:
        _model = load_or_train_model()
    return _model

# --- keyword fallback ---
FAKE_KEYWORDS = [
    (r'registration fee|joining fee|advance fee|deposit required|pay.*join', 35),
    (r'earn \d+ daily|earn \d+ weekly|\d{3,} per (day|hour|page)', 28),
    (r'5000 daily|3000 daily|10000 daily|1 lakh monthly guaranteed', 32),
    (r'no experience (needed|required).*earn|earn.*no experience', 20),
    (r'whatsapp (me|group|interview|only)|telegram (group|channel|join)', 18),
    (r'guaranteed (income|job|salary|profit)|100% guaranteed', 22),
    (r'urgent(ly)? hiring.*earn|earn.*urgent', 15),
    (r'work from home.*earn \d+|earn \d+.*work from home', 20),
    (r'mlm|network marketing.*earn|binary plan|pyramid', 25),
    (r'lottery|prize money|winner selected|claim.*fee', 30),
    (r'abroad job.*fee|overseas.*processing fee', 28),
]
SAFE_KEYWORDS = [
    (r'\d+\s*(years?|yrs?)\s*(of\s*)?experience', -12),
    (r'(lpa|ctc|per annum|salary range)', -10),
    (r'(bachelor|btech|mtech|mba|degree)\s*(required|preferred)', -10),
    (r'(technical|hr)\s*interview|interview process', -12),
    (r'official (portal|website|channel)|apply.*company website', -15),
    (r'(background|reference)\s*check', -10),
    (r'@(infosys|tcs|wipro|google|microsoft|amazon|hcl|accenture)\.com', -20),
    (r'(hybrid|on-site|remote)\s*(work|position|role)', -5),
]

def _rule_score(text):
    score = 40
    tl = text.lower()
    for pattern, w in FAKE_KEYWORDS:
        if re.search(pattern, tl):
            score += w
    for pattern, w in SAFE_KEYWORDS:
        if re.search(pattern, tl):
            score += w
    return max(0, min(100, score))

def analyze(content, input_type='text'):
    text = content.strip()
    model = get_model()

    if model is not None:
        try:
            proba = model.predict_proba([text])[0]
            fake_prob = float(proba[1])
            fraud_score = int(fake_prob * 100)
            # Blend with rule score for robustness
            rule = _rule_score(text)
            fraud_score = int(fraud_score * 0.65 + rule * 0.35)
        except Exception:
            fraud_score = _rule_score(text)
    else:
        fraud_score = _rule_score(text)

    fraud_score = max(0, min(100, fraud_score))

    if fraud_score >= 66:
        result = 'fake'
        risk_level = 'high'
        confidence = min(97, 70 + fraud_score // 5)
    elif fraud_score >= 36:
        result = 'suspicious'
        risk_level = 'medium'
        confidence = min(80, 50 + abs(fraud_score - 50))
    else:
        result = 'safe'
        risk_level = 'low'
        confidence = min(97, 70 + (35 - fraud_score))

    key_reasons = _get_reasons(text, result)
    keyword_highlights = _get_keywords(text, result)
    safety_tips = _get_tips(result)
    ai_explanation = _get_explanation(result, fraud_score, keyword_highlights)

    return {
        'result': result,
        'fraud_score': fraud_score,
        'confidence_score': confidence,
        'risk_level': risk_level,
        'ai_explanation': ai_explanation,
        'key_reasons': key_reasons,
        'keyword_highlights': keyword_highlights,
        'safety_tips': safety_tips,
    }

def _get_explanation(result, score, keywords):
    kw_str = ', '.join(keywords[:3]) if keywords else 'suspicious patterns'
    if result == 'fake':
        return (f"Our ML model assigned a fraud score of {score}/100 — classifying this as a HIGH RISK / FAKE posting. "
                f"Key fraud indicators detected include: {kw_str}. "
                "The content matches patterns from known scam job postings in our training database.")
    elif result == 'suspicious':
        return (f"Our ML model assigned a fraud score of {score}/100 — this posting shows SUSPICIOUS patterns. "
                f"Some risk indicators were found: {kw_str}. "
                "We recommend verifying the company through official channels before proceeding.")
    else:
        return (f"Our ML model assigned a fraud score of {score}/100 — this posting appears LEGITIMATE. "
                "The content follows standard professional hiring language with no major fraud indicators. "
                "Always verify through official channels before sharing personal information.")

def _get_reasons(text, result):
    tl = text.lower()
    reasons = []
    if re.search(r'registration fee|joining fee|advance fee|pay.*join|deposit', tl):
        reasons.append("Requests advance payment / registration fee — a strong fraud indicator")
    if re.search(r'earn \d+ daily|guaranteed income|\d{3,}/day', tl):
        reasons.append("Promises unrealistic daily/weekly earnings")
    if re.search(r'whatsapp|telegram group', tl):
        reasons.append("Uses WhatsApp/Telegram instead of official hiring channels")
    if re.search(r'no experience (needed|required)', tl):
        reasons.append("Claims no experience is needed for unusually high pay")
    if re.search(r'urgent(ly)?|immediately|asap', tl):
        reasons.append("Uses urgency language to pressure quick decisions")
    if re.search(r'guaranteed|100%', tl):
        reasons.append("Makes unrealistic guarantees — legitimate employers don't do this")
    if re.search(r'mlm|network marketing|pyramid|binary plan', tl):
        reasons.append("References MLM / network marketing structure")
    if re.search(r'\d+ years.*experience|experience required', tl):
        reasons.append("Specifies clear experience requirements — legitimate practice")
    if re.search(r'lpa|ctc|per annum', tl):
        reasons.append("States industry-standard salary range (CTC/LPA)")
    if re.search(r'official portal|company website|apply through', tl):
        reasons.append("Directs to official company portal for applications")
    if re.search(r'technical interview|background check|interview process', tl):
        reasons.append("Mentions structured interview and verification process")
    if not reasons:
        if result == 'fake':
            reasons = ["Multiple fraud patterns detected by ML model",
                       "Content matches known scam job templates",
                       "Absence of legitimate company/contact information"]
        else:
            reasons = ["Professional job language with specific requirements",
                       "No suspicious keywords or fee demands detected",
                       "Content consistent with legitimate hiring practices"]
    return reasons[:4]

def _get_keywords(text, result):
    tl = text.lower()
    found = []
    checks_fake = [
        ('registration fee', 'Registration Fee'), ('joining fee', 'Joining Fee'),
        ('advance fee', 'Advance Fee'), ('earn daily', 'Earn Daily'),
        ('whatsapp', 'WhatsApp Contact'), ('telegram', 'Telegram Group'),
        ('no experience', 'No Experience Needed'), ('urgent', 'Urgency Language'),
        ('guaranteed', '100% Guaranteed'), ('work from home', 'Work From Home'),
        ('mlm', 'MLM/Pyramid'), ('lottery', 'Lottery Scam'),
    ]
    checks_safe = [
        ('experience', 'Experience Required'), ('lpa', 'CTC/LPA Stated'),
        ('official', 'Official Portal'), ('interview', 'Interview Process'),
        ('degree', 'Degree Required'), ('background check', 'Background Check'),
    ]
    source = checks_fake if result != 'safe' else checks_safe
    for key, label in source:
        if key in tl and label not in found:
            found.append(label)
    return found[:5] if found else (['Suspicious Content'] if result != 'safe' else ['Professional Listing'])

def _get_tips(result):
    if result == 'fake':
        return [
            "Never pay money for a job — legitimate employers do not charge fees",
            "Avoid any job that only contacts via WhatsApp or Telegram",
            "Report this job to cybercrime.gov.in immediately",
            "Block the contact and warn others in your network",
            "Verify any company on MCA21 portal before engaging",
        ]
    elif result == 'suspicious':
        return [
            "Verify the company exists on the official MCA21 / ROC portal",
            "Contact the company only through their official website",
            "Never share OTP, Aadhaar, or bank details during recruitment",
            "Check online reviews for the company before applying",
        ]
    else:
        return [
            "Apply only through the company's official careers portal",
            "Do not share financial details until you receive a formal offer",
            "Verify the offer letter format and company seal",
            "Keep records of all communications during the process",
        ]
