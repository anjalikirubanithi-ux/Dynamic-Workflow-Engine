import os
import re
import json
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'fraud_model.pkl')

TRAINING_DATA = [
    # ── FAKE / SCAM (label=1) ─────────────────────────────────────────────
    # Fee-based scams
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
    # WhatsApp/Telegram scams
    ("contact us on whatsapp for instant job selection no interview required earn daily from home", 1),
    ("join our telegram channel for daily earning jobs no qualification required limited seats", 1),
    ("whatsapp now to get selected immediately no experience no interview 100% job guaranteed", 1),
    ("message on whatsapp 9999999999 for job earning 5000 per day no degree needed", 1),
    ("telegram group link for work from home job earn without investment students welcome", 1),
    ("part time online job whatsapp interview only earn 300 per hour no experience urgent", 1),
    ("join telegram group earn daily by just liking youtube videos no investment needed", 1),
    ("add whatsapp group for amazon product rating job earn 500 per task no experience", 1),
    # Unrealistic salary scams
    ("earn rs 50000 per week from home no experience no investment guaranteed payment daily", 1),
    ("make 1 lakh per month doing simple tasks at home no skills no experience required", 1),
    ("work 2 hours daily earn 30000 per month no experience housewife students retired welcome", 1),
    ("get paid 5000 per day doing simple online tasks from mobile phone no qualification", 1),
    ("earn 2000 per hour working online from anywhere in india no experience investment", 1),
    ("guaranteed 10000 daily income from home based job no interview simple tasks earn", 1),
    ("earn 500 per click per survey per like simple work from home earning daily", 1),
    ("make money fast 20000 weekly online simple job no experience students housewife", 1),
    # Fake government jobs
    ("government of india recruitment 2024 no exam required direct selection pay fee registration", 1),
    ("psu bank government job vacancy 2024 guaranteed selection pay 500 registration immediately", 1),
    ("railway police army government job guaranteed no exam pay processing fee 1000 apply now", 1),
    ("state government job opening direct selection without exam pay registration fee urgent apply", 1),
    ("central government vacancy 2024 no experience required pay advance fee for joining letter", 1),
    # Fake international jobs
    ("canada uk usa job visa free earn 2 lakh monthly processing fee required whatsapp apply", 1),
    ("dubai job urgent hiring earn 1 lakh salary free accommodation visa fee 5000 required", 1),
    ("singapore malaysia job offer free visa earn usd 3000 monthly pay processing fee telegram", 1),
    ("abroad placement agency job offer high salary free visa pay registration advance fee", 1),
    ("international company hiring earn usd 5000 monthly no experience visa fee required apply", 1),
    # Fake pharma/medical jobs
    ("medical representative pharma company earn 50000 monthly no experience pay registration advance", 1),
    ("hospital job vacancy no qualification required earn 3000 daily pay security deposit 500", 1),
    # Fake IT jobs (low quality)
    ("it company hiring no experience needed earn 25000 monthly work from home pay training fee", 1),
    ("software company data entry operator earn 15000 daily no experience pay registration 300", 1),
    ("bpo call center work from home earn 500 per hour no experience whatsapp interview pay fee", 1),
    ("online computer job no experience typing earn 2000 per hour pay advance registration fee", 1),
    # MLM / pyramid scheme
    ("join our business plan earn unlimited income refer friends earn commission mlm binary", 1),
    ("network marketing opportunity earn passive income recruit members get commission daily", 1),
    ("pyramid scheme investment plan earn 10x returns refer 3 people earn 5000 per referral", 1),
    ("direct selling business earn lakhs monthly no investment required recruit train earn", 1),
    ("multi level marketing earn residual income help others join business opportunity", 1),
    # Fake delivery/logistics jobs
    ("delivery boy earn 2000 daily no experience pay 500 security deposit id proof needed urgent", 1),
    ("courier delivery job earn per delivery no experience needed pay uniform deposit 300 apply", 1),
    # Fake acting/modelling
    ("acting modelling job mumbai bollywood no experience earn lakhs telegram casting couch", 1),
    ("film industry work no experience earn 50000 per day audition fee 2000 required urgent", 1),
    ("model actress wanted earn 1 lakh per shoot no experience pay portfolio fee 3000", 1),
    # More generic fake
    ("unlimited earning opportunity join free seminar business plan earn passive income daily", 1),
    ("work smart not hard earn money online from home 10000 weekly no investment no experience", 1),
    ("guaranteed job placement after training pay training fee 5000 100% placement assured", 1),
    ("online tutoring earn 500 per hour no experience pay registration fee 200 start today", 1),
    ("earn through mobile app daily payment 1000 per hour no investment needed join now", 1),
    ("sell products online earn commission no investment needed pay membership fee 1000", 1),
    ("ghar baithe kaam earn 5000 daily no experience no investment whatsapp registration fee", 1),
    ("housewife student retired earn 3000 daily online work pay small registration amount", 1),
    ("work from mobile earn 2000 per day easy tasks no experience pay advance 200 start", 1),
    ("earn extra income weekends evenings no experience needed pay joining fee 500 start", 1),
    ("digital india earn from home data entry typing earn 1000 per hour pay fee online now", 1),
    ("freelance online job earn 5 lakh per month no investment registration fee 1000 only", 1),
    ("home based packaging job earn per piece no experience women students welcome deposit", 1),
    ("candle making papad making home job earn pay advance fee 500 material provided earn", 1),
    ("stock market trading tips earn guaranteed profit pay 2000 for premium signals group", 1),
    ("crypto investment earn 10x returns guaranteed pay bitcoin advance fee join group", 1),
    ("instagram facebook job like comment earn 1000 daily whatsapp interview no experience", 1),
    ("tele calling job earn 800 per hour work from home no experience pay registration fee", 1),
    ("form filling job earn 500 per form no experience pay 300 advance get daily payment", 1),
    ("copy paste job earn 5000 per day no experience needed pay joining fee 100 immediately", 1),

    # ── SAFE / LEGITIMATE (label=0) ──────────────────────────────────────────
    # Software/Tech jobs
    ("software engineer 3 years experience python java required bachelor degree ctc 8 12 lpa apply portal", 0),
    ("data analyst sql python experience required salary 6 10 lpa technical interview official website", 0),
    ("frontend developer react javascript experience 2 years ctc 7 11 lpa work location bangalore office", 0),
    ("ui ux designer figma sketch experience 2 years portfolio required location pune salary 7 lpa", 0),
    ("product manager 5 years experience agile scrum background check required interview process stages", 0),
    ("java backend developer spring boot microservices experience 4 years salary 12 18 lpa apply now", 0),
    ("devops engineer aws docker kubernetes experience required ctc 15 20 lpa bangalore hybrid office", 0),
    ("machine learning engineer tensorflow pytorch phd mtech preferred salary 20 35 lpa apply portal", 0),
    ("python developer flask django rest api 3 years experience ctc 10 16 lpa work from home hybrid", 0),
    ("react native developer mobile app 2 years salary 8 12 lpa apply company portal official", 0),
    ("full stack developer node react mongo 3 years ctc 10 15 lpa apply through linkedin company website", 0),
    ("ios developer swift objective c 4 years experience portfolio required salary 12 20 lpa", 0),
    ("cyber security analyst certified ethical hacker 3 years experience ctc 12 18 lpa", 0),
    ("qa engineer selenium automation testing 2 years experience salary 6 10 lpa apply portal", 0),
    ("network engineer cisco ccna certification 3 years experience salary 5 9 lpa location hyderabad", 0),
    ("android developer kotlin java 3 years experience salary 8 14 lpa apply official careers page", 0),
    ("data engineer spark kafka 4 years experience ctc 14 22 lpa apply through company linkedin", 0),
    ("cloud architect aws azure certification required 7 years experience salary 25 40 lpa", 0),
    ("blockchain developer solidity 2 years experience ctc 15 25 lpa apply email resume required", 0),
    ("embedded systems engineer c firmware 3 years experience salary 8 14 lpa location chennai", 0),
    ("database administrator oracle postgresql 4 years experience salary 10 18 lpa apply career page", 0),
    ("scrum master agile certification 5 years experience salary 15 22 lpa location gurgaon apply", 0),
    ("sap consultant fiori 5 years implementation experience ctc 20 32 lpa apply email", 0),
    ("salesforce developer lwc apex 3 years experience salary 12 20 lpa bangalore hyderabad", 0),
    ("data scientist nlp computer vision 4 years experience phd preferred ctc 22 38 lpa", 0),
    # Non-tech corporate jobs
    ("marketing executive 2 years experience mba preferred salary 4 6 lpa apply hr email resume required", 0),
    ("business analyst 3 years experience sql excel presentation skills ctc 8 14 lpa hyderabad location", 0),
    ("hr executive recruitment experience 2 years salary 3 5 lpa apply career page company website", 0),
    ("content writer 1 year experience good english grammar editing skills monthly salary 20000 25000", 0),
    ("graphic designer adobe photoshop illustrator experience 2 years salary 25000 monthly portfolio", 0),
    ("sales executive 1 year experience communication skills salary 3 5 lpa incentives location mumbai", 0),
    ("customer support executive good communication skills rotational shifts salary 20000 25000 per month", 0),
    ("civil engineer 3 years site experience autocad proficiency salary 4 7 lpa degree required", 0),
    ("accountant tally gst knowledge 2 years experience salary 25000 35000 apply email resume", 0),
    ("project manager pmp certification preferred 7 years experience salary 18 28 lpa location delhi", 0),
    ("digital marketing manager seo sem social media 4 years salary 8 15 lpa apply linkedin", 0),
    ("financial analyst cfa preferred 3 years experience ctc 10 18 lpa apply official website", 0),
    ("operations manager 6 years experience lean six sigma preferred salary 15 25 lpa bangalore", 0),
    ("supply chain manager 5 years experience erp knowledge salary 12 20 lpa pune location", 0),
    ("legal counsel llb 3 years corporate law experience salary 15 25 lpa mumbai apply email", 0),
    ("chartered accountant ca qualification 2 years post qualification salary 10 16 lpa delhi", 0),
    ("procurement officer 3 years experience vendor management salary 6 12 lpa bangalore office", 0),
    ("logistics coordinator 2 years experience transportation knowledge salary 3 6 lpa apply", 0),
    ("brand manager 5 years fmcg experience mba preferred salary 15 22 lpa mumbai apply", 0),
    ("research analyst 2 years experience ms excel financial modeling salary 5 9 lpa apply", 0),
    ("talent acquisition specialist 3 years experience naukri linkedin salary 5 10 lpa apply", 0),
    ("corporate trainer 5 years experience facilitation skills salary 8 15 lpa pan india travel", 0),
    ("public relations manager 5 years experience media relations salary 10 18 lpa delhi apply", 0),
    ("event coordinator 2 years experience project management salary 3 6 lpa bangalore apply", 0),
    # Known company references
    ("tcs hiring software developer 2 years experience java spring boot ctc 6 10 lpa apply tcs portal", 0),
    ("infosys recruitment software engineer fresher btech preferred ctc 3 6 lpa apply infosys careers", 0),
    ("wipro systems engineer 1 year experience ctc 3 5 lpa apply wipro careers portal official", 0),
    ("hcl technologies java developer 3 years experience ctc 8 14 lpa apply hcl official website", 0),
    ("accenture technology analyst fresher btech mca ctc 4 8 lpa apply accenture careers site", 0),
    ("capgemini associate consultant 2 years experience ctc 5 9 lpa apply capgemini careers", 0),
    ("cognizant technology solutions programmer analyst 2 years ctc 6 10 lpa apply cognizant portal", 0),
    ("tech mahindra engineer 2 years experience ctc 5 8 lpa apply tech mahindra careers official", 0),
    ("mindtree senior developer 4 years ctc 12 18 lpa apply mindtree careers linkedin", 0),
    ("mphasis developer 3 years ctc 8 14 lpa apply mphasis official careers website email", 0),
    ("amazon india software development engineer sde 3 years ctc 25 50 lpa apply amazon jobs", 0),
    ("google india software engineer l4 5 years ctc 40 80 lpa apply google careers portal", 0),
    ("microsoft india sde2 5 years experience ctc 35 60 lpa apply microsoft careers site", 0),
    ("flipkart senior engineer 4 years experience ctc 20 40 lpa apply flipkart careers", 0),
    ("zomato product engineer 3 years ctc 15 30 lpa apply zomato careers website officially", 0),
    # Healthcare/Medical
    ("registered nurse rnbsc nursing 2 years hospital experience salary 30000 45000 per month", 0),
    ("pharmacist b pharm m pharm 2 years retail hospital experience salary 20000 35000 apply", 0),
    ("medical officer mbbs 2 years experience salary 80000 per month clinic hospital apply email", 0),
    ("physiotherapist bpt 2 years experience salary 25000 40000 per month hospital location", 0),
    ("radiologist md radiology 3 years experience salary 1 2 lakh per month hospital apply", 0),
    # Education
    ("school teacher bsc bed 2 years experience cbse curriculum salary 25000 40000 per month", 0),
    ("professor assistant lecturer phd preferred mba 5 years industry experience salary 60000", 0),
    ("online tutor mathematics physics 2 years teaching experience salary 30000 per month", 0),
    ("training specialist learning development 3 years experience salary 6 12 lpa bangalore", 0),
    # Manufacturing/Engineering
    ("mechanical engineer btech 2 years manufacturing experience autocad salary 4 8 lpa apply", 0),
    ("electrical engineer 3 years power systems experience salary 5 9 lpa location pune apply", 0),
    ("production supervisor 4 years manufacturing experience salary 4 8 lpa location chennai", 0),
    ("quality engineer six sigma 3 years experience ctc 6 12 lpa apply company email resume", 0),
    ("plant manager 10 years manufacturing experience salary 20 35 lpa apply hr email linkedin", 0),
    # Freelance/Contract (legitimate)
    ("content writer freelance 2 years experience salary 20000 per month flexible remote work", 0),
    ("graphic designer freelance projects portfolio required salary 15000 25000 per month", 0),
    ("web developer contract 6 months react node salary 80000 per month bangalore startup", 0),
    ("data analyst part time contract work 20 hours week salary 30000 per month remote", 0),
    # Internships (legitimate)
    ("software intern btech final year stipend 15000 20000 per month 6 months duration apply", 0),
    ("marketing intern mba 1st year stipend 10000 per month mumbai office location apply email", 0),
    ("data science intern python ml knowledge stipend 12000 per month 3 months bangalore", 0),
    ("finance intern chartered accountant article ship stipend 8000 12000 per month delhi", 0),
    # Suspicious but safe (edge cases)
    ("work from home senior developer 5 years experience salary 20 35 lpa apply official portal", 0),
    ("remote software engineer us timezone 4 years experience ctc 25 45 lpa apply email resume", 0),
    ("night shift customer support salary 25000 35000 per month rotational shifts apply hr", 0),
    ("weekend part time data analyst 10 hours week salary 15000 per month apply linkedin", 0),
    ("urgent hiring frontend developer 3 years react experience ctc 10 18 lpa apply portal", 0),
    ("immediate joining software engineer 2 years experience salary 8 14 lpa apply email now", 0),
    ("walk in interview software developer 3 years experience salary 10 18 lpa venue bangalore", 0),
    ("telephonic interview shortlisted candidates python developer 3 years experience salary", 0),
    ("we are looking for talented engineers immediately ctc 12 20 lpa apply careers page", 0),
    ("hiring for multiple positions software qa devops 3 5 years experience salary 10 25 lpa", 0),
    # Startup jobs
    ("funded startup hiring senior engineer 4 years experience esops ctc 18 30 lpa apply founders", 0),
    ("early stage startup product engineer 3 years equity ctc 12 22 lpa apply email pitch deck", 0),
    ("series a startup growth hacker 3 years experience salary 10 18 lpa equity options apply", 0),
]

_model = None

def load_or_train_model():
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.svm import LinearSVC
        from sklearn.ensemble import VotingClassifier, GradientBoostingClassifier
        from sklearn.calibration import CalibratedClassifierCV
        from sklearn.pipeline import Pipeline, FeatureUnion
        from sklearn.base import BaseEstimator, TransformerMixin
        import joblib

        if os.path.exists(MODEL_PATH):
            try:
                return joblib.load(MODEL_PATH)
            except Exception:
                pass

        texts = [t for t, _ in TRAINING_DATA]
        labels = [l for _, l in TRAINING_DATA]

        # Feature pipeline: unigrams + bigrams + char ngrams
        tfidf_word = TfidfVectorizer(
            ngram_range=(1, 3),
            max_features=3000,
            sublinear_tf=True,
            analyzer='word',
            min_df=1
        )
        tfidf_char = TfidfVectorizer(
            ngram_range=(3, 5),
            max_features=2000,
            sublinear_tf=True,
            analyzer='char_wb',
            min_df=1
        )

        class FeatureCombiner(BaseEstimator, TransformerMixin):
            def __init__(self):
                self.w = tfidf_word
                self.c = tfidf_char
            def fit(self, X, y=None):
                self.w.fit(X, y)
                self.c.fit(X, y)
                return self
            def transform(self, X):
                from scipy.sparse import hstack
                return hstack([self.w.transform(X), self.c.transform(X)])

        from scipy.sparse import hstack
        combiner = FeatureCombiner()
        X = combiner.fit_transform(texts)

        lr = LogisticRegression(
            max_iter=2000, C=3.0,
            class_weight='balanced',
            solver='lbfgs'
        )
        svm = CalibratedClassifierCV(
            LinearSVC(max_iter=2000, C=2.0, class_weight='balanced')
        )

        lr.fit(X, labels)
        svm.fit(X, labels)

        # Store both classifiers and the combiner
        model_bundle = {'combiner': combiner, 'lr': lr, 'svm': svm}

        try:
            joblib.dump(model_bundle, MODEL_PATH)
        except Exception:
            pass
        return model_bundle

    except ImportError:
        return None

def get_model():
    global _model
    if _model is None:
        _model = load_or_train_model()
    return _model

# ── Keyword rules ──────────────────────────────────────────────────────────
FAKE_KEYWORDS = [
    (r'registration fee|joining fee|advance fee|deposit required|pay.*to.*join|pay.*registration', 40),
    (r'earn \d{3,} daily|earn \d{3,} per day|\d{3,} per (day|hour|page|click|task)', 30),
    (r'5000 daily|3000 daily|10000 daily|1 lakh.*monthly.*guaranteed|50000.*weekly', 35),
    (r'no experience (needed|required).*earn|earn.*no experience.*needed', 22),
    (r'whatsapp (me|group|interview|only|number|now)|whatsapp \d{10}', 22),
    (r'telegram (group|channel|join|link)|join.*telegram', 22),
    (r'guaranteed (income|job|salary|profit|placement|selection)|100% (guaranteed|placement|job)', 28),
    (r'mlm|network marketing|binary plan|pyramid scheme|direct selling plan', 30),
    (r'lottery|prize money|winner selected|claim.*fee|lucky winner', 35),
    (r'abroad job.*fee|overseas.*processing fee|visa.*fee.*required|processing fee.*visa', 32),
    (r'zero investment.*earn|no investment.*earn|earn without investment', 20),
    (r'housewife.*earn|student.*earn.*daily|retired.*earn.*daily', 15),
    (r'pay.*training fee|training fee.*required|pay.*get.*job', 30),
    (r'security deposit.*job|pay.*security deposit|deposit.*start (work|job)', 28),
    (r'instant (selection|job|hiring)|immediately (selected|join|start)', 15),
    (r'unlimited (earn|income)|earn unlimited|passive income.*join', 20),
    (r'copy paste (job|work)|form filling job earn|survey.*earn.*daily', 20),
    (r'ghar baithe|ghar se kaam|घर बैठे', 18),
    (r'crypto.*guaranteed|bitcoin.*earn.*guaranteed|forex.*guaranteed profit', 30),
    (r'refer.*earn|earn.*per referral|recruitment commission', 18),
]

SAFE_KEYWORDS = [
    (r'\d+\s*(years?|yrs?)\s*(of\s*)?(experience|exp)', -15),
    (r'(lpa|ctc|per annum|cost to company|salary range|salary:\s*\d)', -12),
    (r'(bachelor|btech|b\.?tech|mtech|m\.?tech|mba|m\.?b\.?a|degree|graduate)\s*(required|preferred|degree)', -12),
    (r'(technical|hr|aptitude|panel|written)\s*(interview|round|test|assessment)', -15),
    (r'(official|company|corporate)\s*(portal|website|page|channel)|apply.*careers.*page', -18),
    (r'(background|reference|police)\s*(check|verification)', -12),
    (r'@(infosys|tcs|wipro|google|microsoft|amazon|hcl|accenture|flipkart|capgemini|cognizant|techm|zomato|swiggy|ola|paytm)\.com', -25),
    (r'(hybrid|on-site|onsite|remote)\s*(work|position|role|option)', -8),
    (r'(portfolio|resume|cv|curriculum vitae)\s*(required|mandatory|needed)', -10),
    (r'(pmp|ccna|aws certified|azure|cfa|ca|llb|mbbs|bpt|bsc nursing|phd)\s*(certification|qualified|preferred|required)?', -12),
    (r'(esop|equity|stock option)', -10),
    (r'(quarterly|annual|performance)\s*(bonus|appraisal|review)', -8),
    (r'(health|medical|dental)\s*(insurance|benefits|cover)', -8),
    (r'notice period|joining (date|immediately|asap)', -5),
    (r'apply (through|via|at|on)\s*(linkedin|naukri|indeed|glassdoor|shine)', -15),
]

def _rule_score(text):
    score = 38
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
    rule = _rule_score(text)

    if model is not None and isinstance(model, dict):
        try:
            X = model['combiner'].transform([text])
            lr_proba = model['lr'].predict_proba(X)[0]
            svm_proba = model['svm'].predict_proba(X)[0]
            # Ensemble: average LR and SVM
            fake_prob = (float(lr_proba[1]) + float(svm_proba[1])) / 2.0
            ml_score = int(fake_prob * 100)
            # Blend: 70% ML ensemble + 30% rules
            fraud_score = int(ml_score * 0.70 + rule * 0.30)
        except Exception:
            fraud_score = rule
    else:
        fraud_score = rule

    fraud_score = max(0, min(100, fraud_score))

    if fraud_score >= 66:
        result = 'fake'
        risk_level = 'high'
        confidence = min(98, 72 + fraud_score // 5)
    elif fraud_score >= 36:
        result = 'suspicious'
        risk_level = 'medium'
        confidence = min(82, 52 + abs(fraud_score - 50))
    else:
        result = 'safe'
        risk_level = 'low'
        confidence = min(98, 72 + (35 - fraud_score))

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
        return (f"Our ML ensemble (Logistic Regression + SVM) assigned a fraud score of {score}/100 — "
                f"classifying this as HIGH RISK / FAKE. Key fraud indicators detected: {kw_str}. "
                "The content strongly matches known job scam patterns in our training dataset.")
    elif result == 'suspicious':
        return (f"Our ML ensemble assigned a fraud score of {score}/100 — SUSPICIOUS patterns detected. "
                f"Some risk indicators found: {kw_str}. "
                "Verify the company through official channels before sharing any personal information.")
    else:
        return (f"Our ML ensemble assigned a fraud score of {score}/100 — this posting appears LEGITIMATE. "
                "The content follows standard professional hiring language with no major fraud indicators. "
                "Always verify through official channels before sharing sensitive information.")

def _get_reasons(text, result):
    tl = text.lower()
    reasons = []
    if re.search(r'registration fee|joining fee|advance fee|pay.*join|deposit', tl):
        reasons.append("Requests advance payment / registration fee — a strong fraud indicator")
    if re.search(r'earn \d+ daily|guaranteed income|\d{3,}/day|earn.*daily', tl):
        reasons.append("Promises unrealistic daily/weekly earnings")
    if re.search(r'whatsapp|telegram group|telegram channel', tl):
        reasons.append("Uses WhatsApp/Telegram instead of official hiring channels")
    if re.search(r'no experience (needed|required)', tl):
        reasons.append("Claims no experience is needed for unusually high pay")
    if re.search(r'urgent(ly)?|immediately|asap|instant', tl):
        reasons.append("Uses urgency language to pressure quick decisions")
    if re.search(r'guaranteed|100%|zero risk', tl):
        reasons.append("Makes unrealistic guarantees — legitimate employers don't do this")
    if re.search(r'mlm|network marketing|pyramid|binary plan|direct selling', tl):
        reasons.append("References MLM / network marketing / pyramid structure")
    if re.search(r'zero investment|no investment.*earn', tl):
        reasons.append("Promises earnings with zero investment — classic scam pattern")
    if re.search(r'lottery|prize|winner|claim fee', tl):
        reasons.append("References lottery/prize — a known phishing/scam tactic")
    if re.search(r'\d+ years.*experience|experience required|experience preferred', tl):
        reasons.append("Specifies clear experience requirements — legitimate practice")
    if re.search(r'lpa|ctc|per annum|salary range', tl):
        reasons.append("States industry-standard salary range (CTC/LPA)")
    if re.search(r'official portal|company website|apply through|careers page', tl):
        reasons.append("Directs to official company portal for applications")
    if re.search(r'technical interview|background check|interview process|written test', tl):
        reasons.append("Mentions structured interview and verification process")
    if re.search(r'btech|mba|degree required|qualification required|phd preferred', tl):
        reasons.append("Requires specific educational qualifications — standard practice")
    if not reasons:
        if result == 'fake':
            reasons = ["Multiple fraud patterns detected by ML model",
                       "Content matches known scam job templates",
                       "Absence of legitimate company/contact information"]
        else:
            reasons = ["Professional job language with specific requirements",
                       "No suspicious keywords or fee demands detected",
                       "Content consistent with legitimate hiring practices"]
    return reasons[:5]

def _get_keywords(text, result):
    tl = text.lower()
    found = []
    checks_fake = [
        ('registration fee', 'Registration Fee'), ('joining fee', 'Joining Fee'),
        ('advance fee', 'Advance Fee'), ('earn daily', 'Earn Daily'),
        ('earn per day', 'Earn Per Day'), ('earn per hour', 'Earn Per Hour'),
        ('whatsapp', 'WhatsApp Contact'), ('telegram', 'Telegram Group'),
        ('no experience', 'No Experience Needed'), ('urgent', 'Urgency Language'),
        ('guaranteed', '100% Guaranteed'), ('mlm', 'MLM/Pyramid'),
        ('lottery', 'Lottery Scam'), ('zero investment', 'Zero Investment'),
        ('no investment', 'No Investment Needed'), ('security deposit', 'Security Deposit'),
        ('processing fee', 'Processing Fee'), ('work from home', 'Suspicious WFH'),
        ('crypto', 'Crypto Scam'), ('forex', 'Forex Trading Scam'),
    ]
    checks_safe = [
        ('experience', 'Experience Required'), ('lpa', 'CTC/LPA Stated'),
        ('ctc', 'CTC Package'), ('official', 'Official Portal'),
        ('interview', 'Interview Process'), ('degree', 'Degree Required'),
        ('background check', 'Background Check'), ('portfolio', 'Portfolio Required'),
        ('linkedin', 'LinkedIn Application'), ('btech', 'Engineering Degree'),
        ('mba', 'MBA Preferred'), ('phd', 'PhD Preferred'),
    ]
    source = checks_fake if result != 'safe' else checks_safe
    for key, label in source:
        if key in tl and label not in found:
            found.append(label)
    return found[:6] if found else (['Suspicious Content'] if result != 'safe' else ['Professional Listing'])

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


def cross_validate():
    """Run cross-validation on training data and print accuracy report."""
    try:
        from sklearn.model_selection import StratifiedKFold, cross_val_score
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.svm import LinearSVC
        from sklearn.pipeline import Pipeline
        import numpy as np

        texts = [t for t, _ in TRAINING_DATA]
        labels = [l for _, l in TRAINING_DATA]

        pipe = Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 3), max_features=3000, sublinear_tf=True)),
            ('clf', LogisticRegression(max_iter=2000, C=3.0, class_weight='balanced'))
        ])

        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        scores = cross_val_score(pipe, texts, labels, cv=cv, scoring='accuracy')
        f1_scores = cross_val_score(pipe, texts, labels, cv=cv, scoring='f1')
        print(f"CV Accuracy: {scores.mean():.3f} ± {scores.std():.3f}")
        print(f"CV F1 Score: {f1_scores.mean():.3f} ± {f1_scores.std():.3f}")
        print(f"Min accuracy: {scores.min():.3f}, Max accuracy: {scores.max():.3f}")
        return scores.mean()
    except Exception as e:
        print(f"Cross-validation error: {e}")
        return None
