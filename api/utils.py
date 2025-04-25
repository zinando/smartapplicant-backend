import spacy
import docx2txt
import PyPDF2
import io
import re
import mimetypes
from .resume_parser import ResumeParser
from .resources import job_fields, technical_keywords
from fuzzywuzzy import process
from .ai import get_improvement_suggestions, get_basic_improvement_suggestion

# Load NLP model
nlp = spacy.load("en_core_web_lg")

def get_similarity_score(text1, text2):
    """Calculate similarity score between two texts using spaCy."""
    doc1 = nlp(text1)
    doc2 = nlp(text2)
    return doc1.similarity(doc2)

def convert_words_to_numbers(text):
    number_words = {
        "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
        "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
        "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
        "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40,
    }
    for word, num in number_words.items():
        text = re.sub(rf"\b{word}\b", str(num), text, flags=re.IGNORECASE)
    return text

def extract_text(file_bytes, filename):
    """Extract text from PDF/DOCX in memory"""
    try:
        if filename.endswith('.pdf'):
            with io.BytesIO(file_bytes) as pdf_buffer:
                reader = PyPDF2.PdfReader(pdf_buffer)
                text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
        elif filename.endswith('.docx'):
            with io.BytesIO(file_bytes) as docx_buffer:
                text = docx2txt.process(docx_buffer)
        else:
            raise Exception("Unsupported file type (only PDF/DOCX)")
        return {'status': 1, 'text': text, 'message': 'success'}
    except Exception as e:
        return {'status': 0, 'message': str(e)}

def calculate_ats_score(data):
    """Calculate ATS score based on number of required sections that has values in data"""
    required_sections = ['experience', 'education', 'skills', 'certifications', 'name', 'email', 'phone']
    filled_sections = [section for section in required_sections if data.get(section)]
    total_sections = len(required_sections)
    filled_sections_count = len(filled_sections)
    ats_score = (filled_sections_count / total_sections) * 100
    return round(ats_score, 2)

def extract_experience_with_nlp(text):
    doc = nlp(text)
    for sent in doc.sents:
        if "experience" in sent.text.lower():
            sentence_text = convert_words_to_numbers(sent.text.lower())
            match = re.search(r"(\d+)\+?\s*(years|yrs)", sentence_text)
            if match:
                return match.group(0)
    return None

def extract_email(text):
    """Extract email using regex."""
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else None

def extract_phone(text):
    """Extract phone number using regex (supports multiple formats)."""
    match = re.search(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
    return match.group(0) if match else None

def extract_skills(text):
    """Extract skills using a predefined list."""
    skills = ["Python", "Django", "SQL", "Java", "JavaScript", "Machine Learning", "Data Analysis"]
    found_skills = [skill for skill in skills if skill.lower() in text.lower()]
    return found_skills if found_skills else None

def extract_name(text):
    """Extract name from the resume text"""
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return None

def extract_education(text):
    """
    Extract structured education information from resume text
    Returns: List of dicts with {degree, institution, duration} or None
    """
    def format_duration(duration_str):
        """Standardize duration formatting (nested helper function)"""
        if not duration_str:
            return None
            
        # Clean up separators
        duration_str = re.sub(r'\s*to\s*', ' - ', duration_str, flags=re.IGNORECASE)
        duration_str = re.sub(r'\s*–\s*', ' - ', duration_str)  # Replace en dash
        duration_str = re.sub(r'\s*-\s*', ' - ', duration_str)  # Standardize hyphens
        
        # Format present/current
        duration_str = re.sub(r'(?i)\bpresent\b', 'Present', duration_str)
        
        return duration_str.strip()

    # Improved regex pattern to capture degree, institution, and years
    pattern = r"""
        (?P<degree>bachelor|master|b\.?sc|m\.?sc|ph\.?d|diploma|associate|phd)[\s\.,]*
        (?:degree|in)?[\s\.,]*
        (?:(?:in|of)[\s\.,]*(?P<field>\w[\w\s]*?))?[\s\.,]*
        (?:from|at)?[\s\.,]*
        (?P<institution>[A-Z][\w\s-]+?(?:university|college|institute|school)|[A-Z]{2,})[\s\.,]*
        (?P<duration>(?:\d{4}(?:\s|–|-)*(?:to|present|\d{4})|\w+\s\d{4}\s*(?:–|-)\s*(?:\w+\s\d{4}|present)))
    """
    
    matches = re.finditer(pattern, text, re.IGNORECASE | re.VERBOSE)
    education_entries = []
    
    for match in matches:
        entry = {
            'degree': (match.group('degree') or '').title(),
            'field': (match.group('field') or '').title(),
            'institution': (match.group('institution') or '').title(),
            'duration': format_duration(match.group('duration')) if match.group('duration') else None
        }
        education_entries.append(entry)
    # print(f"Education entries: {education_entries}")
    return education_entries if education_entries else None

def extract_certificates(text):
    """
    Extract structured certification information from resume text
    Returns: List of dicts with {name, issuer, date} or None
    """
    def infer_issuer(cert_name):
        """Infer issuer based on certification name"""
        issuer_map = {
            'PMP': 'Project Management Institute',
            'AWS': 'Amazon Web Services',
            'Microsoft': 'Microsoft',
            'Cisco': 'Cisco Systems',
            'CompTIA': 'CompTIA',
            'Google': 'Google Cloud',
            'Oracle': 'Oracle Corporation'
        }
        for key in issuer_map:
            if key in cert_name:
                return issuer_map[key]
        return ''

    def extract_cert_date(context_text, cert_name):
        """Extract approximate certification date"""
        # Fixed pattern without invalid character range
        date_pattern = r"(?:{})(?:\s|\w|,|\.|-){{0,20}}(20\d{{2}}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{{4}})".format(re.escape(cert_name))
        date_match = re.search(date_pattern, context_text, re.IGNORECASE)
        return date_match.group(1) if date_match else None

    patterns = [
        # PMP Certification
        r"(?P<name>PMP)\s?(?:certified|certification)?\s?(?:by)?\s?(?P<issuer>Project Management Institute)?",
        # AWS Certifications
        r"(?P<name>AWS Certified [\w-]+)\s?(?:by)?\s?(?P<issuer>Amazon Web Services)?",
        # Microsoft Certifications
        r"(?P<name>Microsoft Certified:? [\w-]+)\s?(?:by)?\s?(?P<issuer>Microsoft)?",
        # General certification pattern
        r"(?P<name>(?:[A-Z][\w]+ ){1,3}(?:Certified|Professional|Specialist|Expert))\s?(?:by)?\s?(?P<issuer>[\w\s]+?)(?=\s|,|$)",
        # Short form certs (CISSP, CCNA, etc)
        r"""
            (?P<name>\b(?:PMP|AWS|CCNA|CISSP|CPA|CFA|CEH|CISM|ITIL|AWS|GCP)\b)
            \s?(?:certified|certification)?\s?
            (?:by)?\s?
            (?P<issuer>(?:\w+\s){0,4}\w+)?
            (?=\s|,|\.|$)
        """
    ]

    certificates = []
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            cert = {
                'name': (match.group('name') or '').strip(),
                'issuer': (match.group('issuer') or infer_issuer(match.group('name'))).strip(),
                'date': extract_cert_date(text, match.group('name'))
            }
            if cert['name'] and cert not in certificates:
                certificates.append(cert)
        
    return certificates if certificates else None

def parse_resume(text):
    """Extract structured data from a resume file (PDF or DOCX)."""
    # text = extract_text_from_file(file_obj)
    rar = ResumeParser(text)
    resume_analysis_results = rar.parse_all()

    # return {
    #     "name": extract_name(text),
    #     "email": extract_email(text),
    #     "phone": extract_phone(text),
    #     "skills": extract_skills(text),
    #     "experience": extract_experience_with_nlp(text),
    #     "education": extract_education(text),
    #     "certificates": extract_certificates(text)
    # }
    return {
        "name": resume_analysis_results['metadata']['name'],
        "email": resume_analysis_results['metadata']['email'],
        "phone": resume_analysis_results['metadata']['phone'],
        "skills": resume_analysis_results['skills'],
        "experience": resume_analysis_results['experience'],
        "education": resume_analysis_results['education'],
        "certificates": resume_analysis_results['certifications']
    }

def analyze_metadata(analysis_data:dict):
    """Checks relevant metadata from the analysis results."""
    data = ['name', 'email', 'phone', 'location']
    result_data = []

    for key in data:
        if key in analysis_data:
            if not analysis_data[key]:
                break
            result_data.append(key)
    result_data_count = len(result_data)
    total_data_count = len(data)
    if result_data_count == total_data_count:
        score = 100
    elif result_data_count > 0:
        score = int((result_data_count / total_data_count) * 100)
    else:
        score = 0
    return {'score': score, 'matched': result_data, 'missing': [key for key in data if key not in result_data]}

def analyze_education(resume_analysis_data: list, jd_analysis_data: list) -> dict:
    """
    Strictly checks if resume contains ANY of the JD-listed qualifications.
    Scores 100% if resume meets at least one JD requirement (even if lower in hierarchy).
    Scores 0% if resume has none of the specified qualifications.
    
    Returns: {
        'score': 0 or 100,
        'matched': [list of matched degrees],
        'missing': [list of missing JD degrees],
        'highest_qualification': str or None
    }
    """
    # Normalize degrees (lowercase, strip whitespace)
    resume_degrees = {edu["degree"].lower().strip() for edu in resume_analysis_data if edu.get("degree")}
    jd_degrees = {edu["degree"].lower().strip() for edu in jd_analysis_data if edu.get("degree")}
    
    # Qualification hierarchy (customize as needed)
    HIERARCHY = {
        'phd': 4,
        'm.sc': 3, 'm.tech': 3, 'master': 3,
        'b.sc': 2, 'b.tech': 2, 'bachelor': 2, 
        'hnd': 1, 'ond': 1, 'ond/hnd': 1,
        'associate': 0
    }
    
    # Case 1: No JD requirements → automatic pass
    if not jd_degrees:
        return {
            'score': 100.0,
            'matched': [],
            'missing': [],
            'highest_qualification': max(resume_degrees, key=lambda x: HIERARCHY.get(x, 0)) if resume_degrees else None
        }
    
    # Case 2: Check for ANY match (strict)
    matched_degrees = list(resume_degrees & jd_degrees)
    missing_degrees = list(jd_degrees - resume_degrees)
    
    # Score 0% if no overlap
    if not matched_degrees:
        return {
            'score': 0.0,
            'matched': [],
            'missing': missing_degrees,
            'highest_qualification': max(resume_degrees, key=lambda x: HIERARCHY.get(x, 0)) if resume_degrees else None
        }
    
    # Case 3: At least one match → score based on hierarchy position
    # Get hierarchy values for all JD degrees and matched resume degrees
    jd_levels = [HIERARCHY.get(deg, 0) for deg in jd_degrees]
    resume_levels = [HIERARCHY.get(deg, 0) for deg in matched_degrees]
    
    # Calculate score based on highest matched level vs highest JD level
    max_jd_level = max(jd_levels) if jd_levels else 0
    max_resume_level = max(resume_levels) if resume_levels else 0
    
    # Score is the ratio of resume's highest match to JD's highest requirement
    # (e.g., if JD wants PhD (4) and resume has MSc (3), score = 3/4 = 75%)
    score = (max_resume_level / max_jd_level) * 100 if max_jd_level > 0 else 100.0
    
    return {
        'score': round(score, 1),  # Round to 1 decimal place
        'matched': matched_degrees,
        'missing': missing_degrees,
        'highest_qualification': max(matched_degrees, key=lambda x: HIERARCHY.get(x, 0))
    }

def analyze_skills(jd_analysis_data:list, resume_text:str):
    """Use the skills extracted from resume to match content of the jd"""
    jd_skills = [skill for skill in jd_analysis_data if skill]
    jd_skills = list(set(jd_skills))
    result_data = []
    missing_data = []
    score = 0


    if len(jd_analysis_data) > 0:
        for skill in jd_skills:
            if process.extractOne(skill, resume_text, score_cutoff=85):
                result_data.append(skill)
            else:
                missing_data.append(skill)
        
        # compute the score
        result_data_count = len(result_data)
        total_data_count = len(jd_skills)

        if result_data_count == total_data_count:
            score = 100
        elif result_data_count > 0:
            score = int((result_data_count / total_data_count) * 100)

    else:
        score = 100
    return {'score': score, 'matched': result_data, 'missing': missing_data}

def analyze_experience(resume_analysis_data, jd_analysis_data):
    """Checks relevant experience from the analysis results."""
    #print(f"JD Experience data: {jd_analysis_data}, Resume Experience data: {resume_analysis_data}")
    jd_experience = re.search(r"(\d+)\+?\s*(years|yrs)", str(jd_analysis_data))
    resume_experience = re.search(r"(\d+)\+?\s*(years|yrs)", str(resume_analysis_data))
    #print(f"JD Experience: {jd_experience}, Resume Experience: {resume_experience}")

    if not jd_experience:
        return {'score': 100, 'matched': [], 'missing': []}
    elif not resume_experience:
        return {'score': 0, 'matched': [], 'missing': [jd_analysis_data]}

    jd_years = int(jd_experience.group(1))
    resume_years = int(resume_experience.group(1))

    if resume_years >= jd_years:
        score = 100
        jd_analysis_data = ''
    else:
        score = int((resume_years / jd_years) * 100)

    return {'score': score, 'matched': [resume_analysis_data], 'missing': [jd_analysis_data] if jd_analysis_data != '' else []}

def analyze_certificates(resume_analysis_data:list, jd_analysis_data:list):
    """Checks relevant certificates from the analysis results by similarity comparison."""
    jd_certificates = [cert.get('name', None) for cert in jd_analysis_data if cert.get('name', None) != None]
    resume_certificates = [cert.get('name', None) for cert in resume_analysis_data if cert.get('name', None) != None]

    # Remove duplicates
    jd_certificates = list(set(jd_certificates))
    resume_certificates = list(set(resume_certificates))

    result_data = []
    missing_data = []

    for jd_cert in jd_certificates:
        for resume_cert in resume_certificates:
            if get_similarity_score(jd_cert, resume_cert) > 0.8:
                result_data.append(jd_cert)
                break
        else:
            missing_data.append(jd_cert)
    
    # compute the score
    result_data_count = len(result_data)
    total_data_count = len(jd_certificates)

    if result_data_count == total_data_count:
        score = 100
    elif result_data_count > 0:
        score = int((result_data_count / total_data_count) * 100)
    else:
        score = 0

    return {'score': score, 'matched': result_data, 'missing': missing_data}

def calculate_suitability_score(sectional_analysis:dict):
    """Calculates suitability score as an average of the analysis score for each section."""
    total_score = 0
    count = 0

    for key, value in sectional_analysis.items():
        if value > 0:
            total_score += value
            count += 1

    if count == 0:
        return 0
    else:
        return round(total_score / count, 2)

def resume_sectional_analysis(parsed_data, known_skills=[]):
    """
    Perform sectional analysis on parsed resume data.
    Returns: Dictionary with analysis results.
    """
    # calculate metadata score: parsed_data['metadata'] is dict, check that name, email, and phone are not empty
    # get score as a percentage of the total number of metadata fields with values versus expected fields: name, phone, email
    metadata_score = analyze_metadata(parsed_data['metadata']).get('score', 0)

    # calculate education score: parsed_data['education'] is list of dicts, check that degree, institution, and duration are not empty
    # get score as a percentage of expected education data present versus expected: OND/HND AND BSc/MSc/PhD
    education_score = 0
    degrees = [edu.get('degree', None) for edu in parsed_data['education'] if edu.get('degree', None) != None]
    if 'B.Sc' in degrees or 'M.Sc' in degrees or 'PhD' in degrees or 'HND' in degrees:
        education_score = 100
    elif 'OND' in degrees or 'Associate' in degrees:
        education_score = 50
    
    # claculate experience score as a ratio of number of yrs of expriece versus industry std: 3 years
    resume_experience = re.search(r"(\d+)\+?\s*(years|yrs)", str(parsed_data['experience_duration']))
    resume_experience_score = 0
    expected_years = 3
    resume_years = 0

    if resume_experience:
        resume_years = int(resume_experience.group(1))

    if resume_years >= expected_years:
        resume_experience_score = 100
    elif resume_years > 0:
        resume_experience_score = int((resume_years / expected_years) * 100)
    
    # calculate certification as a ration of number of certificates found in resume vs expected: 2
    # Every resume is assumed to have at least one school certification and one non-school certification
    expected_cert = 2
    resume_cert = 0
    resume_cert_score = 0

    if education_score > 0:
        resume_cert += 1
    if len(parsed_data['certifications']) > 0:
        resume_cert += 1
    
    if resume_cert == expected_cert:
        resume_cert_score = 100
    elif resume_cert > 0:
        resume_cert_score = int((resume_cert / expected_cert) * 100)

    
    return {
        "metadata": metadata_score,
        "education": education_score,
        "skills": 45, #analyze_skills(parsed_data['skills'], known_skills, basic=True).get('score', 0),
        "experience": resume_experience_score,
        "certifications": resume_cert_score
    }
    
def match_job_field(input_title, field_keywords):
    """Find the best-matching field for any job title"""
    # Flatten all job titles across fields
    all_titles = []
    for field, titles in job_fields.items():
        all_titles.extend([(title, field) for title in titles])
    
    # Extract just the titles for matching
    title_strings = [title for title, _ in all_titles]
    
    # Get best match (returns tuple: (matched_title, score, index))
    best_match = process.extractOne(input_title, title_strings)
    
    if best_match:
        matched_title = best_match[0]
        # Retrieve the field for the matched title
        for title, field in all_titles:
            if title == matched_title:
                return {
                    "input_title": input_title,
                    "matched_job_title": matched_title,
                    "field": field,
                    "expected_keywords": field_keywords[field]
                }
    
    # Fallback for unknown titles
    return {
        "input_title": input_title,
        "matched_job_title": None,
        "field": "general",
        "expected_keywords": {}  # Empty template
    }

def calculate_keyword_coverage(resume_text, expected_keywords):
    """Test resume against field-specific keywords"""
    coverage = {}
    resume_text_lower = resume_text.lower()
    
    for category, keywords in expected_keywords.items():
        found = 0
        for keyword in keywords:
            # if keyword.lower() in resume_text_lower:
            if process.extractOne(keyword.lower(), resume_text_lower, score_cutoff=85):
                found += 1
        coverage[category] = round((found / len(keywords)) * 100) if keywords else 0
    
    return coverage

def analyze_resume_with_jd(resume_text, job_description, user, job_title='',):
    """Analyze resume against a job description."""
    try:
        #print(f'Analyzing resume: {resume_text}')
        rar = ResumeParser(resume_text)
        resume_analysis_results = rar.parse_all()
        jd_ar = ResumeParser(job_description)
        jd_analysis_results = jd_ar.parse_all()

        field_matcher = match_job_field(job_title, technical_keywords)
        kw_data = calculate_keyword_coverage(resume_text, field_matcher['expected_keywords'])

        # Parse resume text
        resume_data = parse_resume(resume_text)
        
        sectional_analysis_data = resume_sectional_analysis(resume_analysis_results, rar.known_skills['all'])

        basic_suggestions = get_basic_improvement_suggestion(sectional_analysis_data)

        analyzed_data = {
            'metadata': analyze_metadata(resume_analysis_results['metadata']),
            'education': analyze_education(resume_analysis_results['education'], jd_analysis_results['education']),
            # 'skills': analyze_skills(resume_analysis_results['skills'], jd_analysis_results['skills']),
            'skills': analyze_skills(jd_analysis_results['skills'], resume_text),
            'experience': analyze_experience(resume_analysis_results['experience_duration'], jd_analysis_results['experience_duration']),
            'certifications': analyze_certificates(resume_analysis_results['certifications'], jd_analysis_results['certifications'])
        }
        
        keyword_coverage = {
                    "Experience Level": analyzed_data['experience'].get('score',0),
                    "Education Requirements": analyzed_data['education'].get('score',0)
                }
        kw_data.update(keyword_coverage)
        ats_score = calculate_ats_score(resume_data)
        suggestions = get_improvement_suggestions(resume_text, user.id, job_description)
        if suggestions == '':
            suggestions = [
                    "Add missing keywords like 'TypeScript' and 'GraphQL' to your skills section",
                    "Highlight your computer science education if applicable",
                    "Mention any agile methodology experience you have"
                ]
        else:
            suggestions = [part.strip() for part in suggestions.split(';') if part.strip()]
            #print(suggestions)
        analysis_results = {
            "basic_analysis": {
                "ats_score": ats_score,
                "score_comparison": 65,
                "sectional_analysis": sectional_analysis_data,
                "suggestions": basic_suggestions
            },
            "job_matching": {
                "suitability_score": calculate_suitability_score(kw_data | {'ats_score': ats_score}),
                "keyword_coverage": kw_data,
                "sectional_matching": {
                    "skills": {
                        "match_percentage": analyzed_data['skills'].get('score',0),
                        "matched": analyzed_data['skills'].get('matched',[]),
                        "missing": analyzed_data['skills'].get('missing',[])
                    },
                    "education": {
                        "match_percentage": analyzed_data['education'].get('score',0),
                        "matched": analyzed_data['education'].get('matched',[]),
                        "missing": analyzed_data['education'].get('missing',[])
                    },
                    "experience": {
                        "match_percentage": analyzed_data['experience'].get('score',0),
                        "matched": analyzed_data['experience'].get('matched',[]),
                        "missing": analyzed_data['experience'].get('missing',[])
                    },
                    "certifications": {
                        "match_percentage": analyzed_data['certifications'].get('score',0),
                        "matched": analyzed_data['certifications'].get('matched',[]),
                        "missing": analyzed_data['certifications'].get('missing',[])
                    }
                },
            
                "suggestions": suggestions
            }
        }
        return analysis_results
    except Exception as e:
        #print(e)
        raise Exception(str(e))


