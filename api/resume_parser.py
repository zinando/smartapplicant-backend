import re
from datetime import datetime
from collections import defaultdict
import spacy
import os
import json



# Load English language model for NLP
nlp = spacy.load("en_core_web_md")

class ResumeParser:
    def __init__(self, resume_text):
        self.resume_text = resume_text
        self.sections = self._identify_sections()
        self.parsed_data = {
            'metadata': {},
            'education': [],
            'experience': [],
            'experience_duration': None,
            'skills': [],
            'certifications': []
        }
        self.known_skills = self._load_known_skills()
        
    def _identify_sections(self):
        """Identify major sections in the resume using common headings"""
        section_patterns = {
            'contact': r'(contact|personal)\s*(info|information|details)?',
            'education': r'education|academic\s*background|qualifications',
            'experience': r'experience|work\s*history|employment\s*history|professional\s*experience',
            'skills': r'skills|technical\s*skills|competencies|key\s*skills',
            'certifications': r'certifications|licenses|certificates|training',
            'summary': r'summary|profile|objective|about'
        }
        sections = defaultdict(str)
        current_section = None
        lines = self.resume_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line matches any section header
            matched = False
            for section, pattern in section_patterns.items():
                if re.search(pattern, line, re.IGNORECASE):
                    current_section = section
                    matched = True
                    break
                    
            if not matched and current_section:
                sections[current_section] += line + '\n'
        return sections
    
    def _load_known_skills(self):
        """Load all skill data from JSON files and return combined dictionary."""
        # Define file paths for each skill category
        #base_path = os.path.dirname(__file__)
        ts_filepath = os.path.join('data', 'ts.json')
        soft_filepath = os.path.join('data', 'ss.json')
        domain_filepath = os.path.join('data', 'dss.json')
        tools_filepath = os.path.join('data', 'ts.json')
        cert_filepath = os.path.join('data', 'cm.json')
        
        # Initialize dictionary to hold the data
        skills_dict = {'ts': [], 'soft': [], 'domain': [], 'tools': [], 'cert': [], 'all': []}
        
        # Load JSON data
        def load_json_file(file_path):
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return []
        
        # Load data for each category
        skills_dict['ts'] = load_json_file(ts_filepath)
        skills_dict['soft'] = load_json_file(soft_filepath)
        skills_dict['domain'] = load_json_file(domain_filepath)
        skills_dict['tools'] = load_json_file(tools_filepath)
        skills_dict['cert'] = load_json_file(cert_filepath)
        
        # Combine all skills into 'all'
        all_skills = set()
        all_skills.update(skills_dict['ts'])
        all_skills.update(skills_dict['soft'])
        all_skills.update(skills_dict['domain'])
        all_skills.update(skills_dict['tools'])
        all_skills.update(skills_dict['cert'])
        
        skills_dict['all'] = list(all_skills)  # Convert set back to list
        
        return skills_dict
    
    def extract_phone_numbers(self, text):
        """
        Extract phone numbers from text with various international formats
        
        Supports:
        - International: +1 (123) 456-7890
        - US/CAN: (123) 456-7890, 123-456-7890, 123.456.7890
        - With extensions: 123-456-7890 x1234
        - Without separators: 1234567890
        """
        phone_pattern = r'''
            (?:\+?(\d{1,3})[-.\s(]*)??    # Optional country code
            (?:\(?(\d{3})\)?[-.\s]*)??    # Optional area code with parentheses
            (\d{3})[-.\s]*                 # Exchange code
            (\d{4})                        # Subscriber number
            (?:\s*(?:ext|x|\#)\s*(\d+))?    # Optional extension
        '''
        # phone_pattern = r'''
        #     (?:\+?(\d{1,3})[-. (]*)?     # Optional country code
        #     (\d{3})[-. )]*                # Area code
        #     (\d{3})[-. ]*                 # Exchange
        #     (\d{4})                       # Subscriber number
        #     (?: *x(\d+))?                 # Optional extension
        #     \b                            # Word boundary
        # '''
        
        matches = re.findall(phone_pattern, text, re.VERBOSE)
        phone_numbers = []
        
        for match in matches:
            country_code, area_code, exchange, subscriber, extension = match
            
            # Format the number
            phone_parts = []
            if country_code:
                phone_parts.append(f"+{country_code}")
            
            if area_code and exchange and subscriber:
                main_number = f"({area_code}) {exchange}-{subscriber}"
                phone_parts.append(main_number)
            
            if extension:
                phone_parts.append(f"x{extension}")
            
            if phone_parts:
                phone_numbers.append(' '.join(phone_parts))
        
        return phone_numbers
    
    def parse_metadata(self):
        """Extract personal/contact information"""
        contact_text = self.sections.get('contact', '') or self.resume_text[:1000]
        
        # Email extraction
        emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', contact_text)
        if emails:
            self.parsed_data['metadata']['email'] = emails[0]
        
        # Phone extraction (international formats)
        # phones = re.findall(r'(?:(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})(?: *x(\d+))?\b', contact_text)
        phones = self.extract_phone_numbers(contact_text)
        if phones:
            self.parsed_data['metadata']['phone'] = ''.join(phones[0])
        
        # Name extraction (first line or before contact info)
        doc = nlp(contact_text.split('\n')[0])
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                self.parsed_data['metadata']['name'] = ent.text
                break
        
        # Location extraction
        doc = nlp(contact_text)
        for ent in doc.ents:
            if ent.label_ == "GPE":
                self.parsed_data['metadata']['location'] = ent.text
                break
                
        return self.parsed_data['metadata']
    

    def parse_education(self):
        """Extract education history with degrees and institutions"""
        edu_text = self.resume_text #self.sections.get('education', '')


        if not edu_text:
            return []
        
        def make_unique_dicts(lst):
            seen = set()
            result = []
            for d in lst:
                key = tuple(sorted(d.items()))
                if key not in seen:
                    seen.add(key)
                    result.append(d)
            return result
        
        education = []
        current_entry = {}
        lines = [line.strip() for line in edu_text.split('\n') if line.strip()]
        
        # Degree standardization mapping
        DEGREE_STANDARDIZATION = {
            # New combined OND/HND pattern
            r'\b(ond|ordinary national diploma)\s*/\s*(hnd|higher national diploma)\b': 'OND/HND',
            r'\b(hnd|higher national diploma)\s*/\s*(ond|ordinary national diploma)\b': 'OND/HND',
            
            # Original separate OND patterns (keep these)
            r'\b(national diploma|ordinary national diploma|nd|ond)\b': 'OND',
            
            # Original separate HND patterns (keep these)
            r'\b(higher national diploma|hnd)\b': 'HND',
            
            # Bachelor variants (B.Sc/B.Eng)
            r'\b(b\.?\s?sc|bachelor of science|bs)(\s*/\s*)?(b\.?\s?eng|bachelor of engineering|beng)?\b': 'B.Sc',
            r'\b(b\.?\s?a|bachelor of arts|ba)\b': 'B.Sc',
            r'\b(b\.?\s?eng|bachelor of engineering|beng)(\s*/\s*)?(b\.?\s?sc|bachelor of science|bsc)?\b': 'B.Sc',
            r'\b(b\.?\s?tech|bachelor of technology)\b': 'B.Tech',
            
            # Master variants
            r'\b(m\.?\s?sc|master of science|ms|msc)\b': 'M.Sc',
            r'\b(m\.?\s?a|master of arts|ma)\b': 'M.Sc',
            r'\b(m\.?\s?eng|master of engineering|meng)\b': 'M.Sc',
            r'\b(m\.?\s?tech|master of technology)\b': 'M.Tech',

            # PhD variants
            r'\b(ph\.?\s?d|phd|doctorate|d\.?\s?phil)\b': 'PhD',

            # Associate variants
            r'\b(associate|a\.?\s?a|a\.?\s?s|aa|as)\b': 'Associate',
        }

        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Pattern for institution line (contains place and dates)
            institution_match = re.search(
                r'^(?P<institution>[^-–]+?)\s*[-–]\s*(?P<location>[^0-9]+?)\s*'
                r'(?P<dates>'
                r'(\d{4}\s*[-–]\s*(present|current))|'  # e.g., "2015–Present"
                r'(\d{4}\s*[-–]\s*\d{4})|'             # e.g., "2015-2019"
                r'(\w{3,9}\s\d{4}\s*[-–]\s*(present|current))|'  # e.g., "Sept 2020–Present"
                r'(\w{3,9}\s\d{4}\s*[-–]\s*\w{3,9}\s\d{4})|'    # e.g., "Jan 2018–Dec 2022"
                r'(\d{1,2}/\d{4}\s*[-–]\s*(present|current))|'   # e.g., "10/2015–Present"
                r'(\d{1,2}/\d{4}\s*[-–]\s*\d{1,2}/\d{4})'       # e.g., "08/2017-05/2021"
                r')',
                line,
                re.IGNORECASE
            )
            
            if institution_match:
                if current_entry:  # Save previous entry
                    education.append(current_entry)
                    current_entry = {}
                
                current_entry['institution'] = institution_match.group('institution').strip()
                current_entry['location'] = institution_match.group('location').strip()
                current_entry['dates'] = institution_match.group('dates').strip()
                
                # Check next line for degree information
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    degree_match = re.search(
                        r'(?P<degree>'
                        # National Diploma variants (strict word boundaries)
                        r'(?<!\w)(?:national[-\s]?diploma|ordinary[-\s]?national[-\s]?diploma|n\.?d|o\.?n\.?d)(?!\w)(\s*/\s*(?:h\.?n\.?d|higher[-\s]?national[-\s]?diploma))?(?!\w)|'
                        # Higher National Diploma variants
                        r'(?<!\w)(?:higher[-\s]?national[-\s]?diploma|h\.?n\.?d)(?!\w)(\s*/\s*(?:o\.?n\.?d|n\.?d))?(?!\w)|'
                        # Bachelor variants
                        r'(?<!\w)(?:b\.?\s?sc(?:ience)?|bachelor[-\s]?(?:of[-\s]?)?science|b\.?s)(?!\w)(\s*/\s*(?:b\.?\s?eng(?:ineering)?|bachelor[-\s]?(?:of[-\s]?)?engineering|b\.?eng))?(?!\w)|'
                        r'(?<!\w)(?:b\.?\s?a(?:rts)?|bachelor[-\s]?(?:of[-\s]?)?arts|b\.?a)(?!\w)|'
                        r'(?<!\w)(?:b\.?\s?eng(?:ineering)?|bachelor[-\s]?(?:of[-\s]?)?engineering|b\.?eng)(?!\w)(\s*/\s*(?:b\.?\s?sc(?:ience)?|bachelor[-\s]?(?:of[-\s]?)?science|b\.?s))?(?!\w)|'
                        # Master variants
                        r'(?<!\w)(?:m\.?\s?sc(?:ience)?|master[-\s]?(?:of[-\s]?)?science|m\.?s|msc)(?!\w)|'
                        r'(?<!\w)(?:m\.?\s?a(?:rts)?|master[-\s]?(?:of[-\s]?)?arts|m\.?a)(?!\w)|'
                        r'(?<!\w)(?:m\.?\s?eng(?:ineering)?|master[-\s]?(?:of[-\s]?)?engineering|m\.?eng)(?!\w)|'
                        # PhD variants
                        r'(?<!\w)(?:ph\.?\s?d|doctorate|d\.?\s?phil|phd)(?!\w)|'
                        # Associate variants (strict to avoid "maintenance tech")
                        r'(?<!\w)(?:associate(?:\sdegree)?|a\.?\s?a|a\.?\s?s|aa|as)(?!\w)'
                        r')'
                        r'(?:\s+(?:in|of)\s+(?P<field>[^\n]+))?',
                        next_line,
                        re.IGNORECASE
                    )
                    if degree_match:
                        raw_degree = degree_match.group('degree').strip()
                        # Standardize the degree name
                        for pattern, standardized in DEGREE_STANDARDIZATION.items():
                            if re.search(pattern, raw_degree, re.IGNORECASE):
                                if standardized == 'OND/HND':
                                    education.extend([{'degree': 'OND'},{'degree': 'HND'}])
                                else:
                                    current_entry['degree'] = standardized
                                break
                        else:
                            current_entry['degree'] = raw_degree  # fallback to original if no match
                        
                        if degree_match.group('field'):
                            current_entry['field'] = degree_match.group('field').strip()
                        i += 1  # Skip the degree line
            else:
                # Check for standalone degree lines
                degree_match = re.search(
                    r'(?P<degree>'
                    # National Diploma variants (strict word boundaries)
                    r'(?<!\w)(?:national[-\s]?diploma|ordinary[-\s]?national[-\s]?diploma|n\.?d|o\.?n\.?d)(?!\w)(\s*/\s*(?:h\.?n\.?d|higher[-\s]?national[-\s]?diploma))?(?!\w)|'
                    # Higher National Diploma variants
                    r'(?<!\w)(?:higher[-\s]?national[-\s]?diploma|h\.?n\.?d)(?!\w)(\s*/\s*(?:o\.?n\.?d|n\.?d))?(?!\w)|'
                    # Bachelor variants
                    r'(?<!\w)(?:b\.?\s?sc(?:ience)?|bachelor[-\s]?(?:of[-\s]?)?science|b\.?s)(?!\w)(\s*/\s*(?:b\.?\s?eng(?:ineering)?|bachelor[-\s]?(?:of[-\s]?)?engineering|b\.?eng))?(?!\w)|'
                    r'(?<!\w)(?:b\.?\s?a(?:rts)?|bachelor[-\s]?(?:of[-\s]?)?arts|b\.?a)(?!\w)|'
                    r'(?<!\w)(?:b\.?\s?eng(?:ineering)?|bachelor[-\s]?(?:of[-\s]?)?engineering|b\.?eng)(?!\w)(\s*/\s*(?:b\.?\s?sc(?:ience)?|bachelor[-\s]?(?:of[-\s]?)?science|b\.?s))?(?!\w)|'
                    # Master variants
                    r'(?<!\w)(?:m\.?\s?sc(?:ience)?|master[-\s]?(?:of[-\s]?)?science|m\.?s|msc)(?!\w)|'
                    r'(?<!\w)(?:m\.?\s?a(?:rts)?|master[-\s]?(?:of[-\s]?)?arts|m\.?a)(?!\w)|'
                    r'(?<!\w)(?:m\.?\s?eng(?:ineering)?|master[-\s]?(?:of[-\s]?)?engineering|m\.?eng)(?!\w)|'
                    # PhD variants
                    r'(?<!\w)(?:ph\.?\s?d|doctorate|d\.?\s?phil|phd)(?!\w)|'
                    # Associate variants (strict to avoid "maintenance tech")
                    r'(?<!\w)(?:associate(?:\sdegree)?|a\.?\s?a|a\.?\s?s|aa|as)(?!\w)'
                    r')'
                    r'(?:\s+(?:in|of)\s+(?P<field>[^\n]+))?',
                    line,
                    re.IGNORECASE
                )
                if degree_match and not current_entry.get('degree'):
                    raw_degree = degree_match.group('degree').strip()
                    # print(f'Other degree: {raw_degree}')
                    # Standardize the degree name
                    for pattern, standardized in DEGREE_STANDARDIZATION.items():
                        if re.search(pattern, raw_degree, re.IGNORECASE):
                            if standardized == 'OND/HND':
                                education.extend([{'degree': 'OND'},{'degree': 'HND'}])
                            else:
                                current_entry['degree'] = standardized
                            break
                    else:
                        current_entry['degree'] = raw_degree  # fallback to original if no match
                    
                    if degree_match.group('field'):
                        current_entry['field'] = degree_match.group('field').strip()
                
                elif degree_match:
                    raw_degree = degree_match.group('degree').strip()
                    # print(f'Degree match: {raw_degree}')
                    entry = {}

                    # Standardize the degree name
                    for pattern, standardized in DEGREE_STANDARDIZATION.items():
                        if re.search(pattern, raw_degree, re.IGNORECASE):
                            if standardized == 'OND/HND':
                                education.extend([{'degree': 'OND'},{'degree': 'HND'}])
                            else:
                                entry['degree'] = standardized
                            break
                    else:
                        entry['degree'] = raw_degree  # fallback to original if no match

                    if degree_match.group('field'):
                        entry['field'] = degree_match.group('field').strip()

                    if entry not in education:
                        education.append(entry)
                
                # Check for honors/distinction
                honors_match = re.search(r'\((Distinction|Honors|First Class|Second Class|Upper|Lower)\)', line, re.IGNORECASE)
                if honors_match:
                    current_entry['honors'] = honors_match.group(1)
            
            i += 1
        
        if current_entry:
            education.append(current_entry)
        
        education = make_unique_dicts(education)
        
        self.parsed_data['education'] = education
        # print(f'Education match: {education}')
        return education

    def _parse_date(self, date_str):
        """Parse date string into datetime object"""
        try:
            # Try month-year format first
            if re.match(r'^[A-Za-z]{3,}', date_str):
                return datetime.strptime(date_str, '%b %Y')
            # Try year-only format
            elif re.match(r'^\d{4}$', date_str):
                return datetime.strptime(date_str, '%Y')
        except ValueError:
            return None
        return None


    def _calculate_experience_years(self, date_ranges):
        """Calculate total years of experience from date ranges"""
        total_days = 0
        today = datetime.now()
        
        for date_range in date_ranges:
            dates = re.split(r'\s*(?:-|–|to)\s*', date_range, maxsplit=1)
            if len(dates) == 2:
                start_date = self._parse_date(dates[0])
                end_date = self._parse_date(dates[1]) if dates[1].lower() not in ['present', 'current'] else today
                
                if start_date and end_date:
                    total_days += (end_date - start_date).days
        
        return round(total_days / 365)  # Convert to years

    def parse_experience(self):
        """Extract work experience duration from entire resume text"""
        exp_text = self.resume_text
        
        # First try explicit duration patterns (e.g., "5+ years", "3-5 years")
        range_pattern = r'(?P<min_years>\d+)\s*(?:\+|\–|-)\s*(?P<max_years>\d+)?\s*(?:year|yr)s?'
        range_match = re.search(range_pattern, exp_text, re.IGNORECASE)
        
        if range_match:
            min_years = range_match.group('min_years')
            max_years = range_match.group('max_years') or min_years
            self.parsed_data['experience_duration'] = f"{min_years}-{max_years} years experience"
            #print(f'Experience duration (range match): {self.parsed_data["experience_duration"]}')
            return self.parsed_data['experience_duration']
        
        # Then try experience level descriptions
        level_pattern = r'(?:Entry-Level|Junior):\s*(?P<entry_years>\d+)\s*–\s*\d+\s*years|' \
                    r'(?:Mid-Level|Intermediate):\s*(?P<mid_years>\d+)\s*–\s*\d+\s*years|' \
                    r'(?:Senior-Level|Expert):\s*(?P<senior_years>\d+\+?)\s*years'
        level_match = re.search(level_pattern, exp_text, re.IGNORECASE)
        
        if level_match:
            if level_match.group('senior_years'):
                years = level_match.group('senior_years')
                self.parsed_data['experience_duration'] = f"{years}+ years experience"
            elif level_match.group('mid_years'):
                years = level_match.group('mid_years')
                self.parsed_data['experience_duration'] = f"{years}-5 years experience"
            elif level_match.group('entry_years'):
                years = level_match.group('entry_years')
                self.parsed_data['experience_duration'] = f"{years}-3 years experience"
            
            #print(f'Experience duration (level match): {self.parsed_data["experience_duration"]}')
            return self.parsed_data['experience_duration']
        
        # Fall back to date range calculation (your existing implementation)
        date_ranges = re.findall(
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}'
            r'\s*(?:-|–|to)\s*'
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?[a-z]* \d{4}|present|current',
            exp_text,
            re.IGNORECASE
        )
        
        if date_ranges:
            total_years = self._calculate_experience_years(date_ranges)
            if total_years > 0:
                self.parsed_data['experience_duration'] = f"{total_years} years experience"
                #print(f'Experience duration (date calculation): {self.parsed_data["experience_duration"]}')
                return self.parsed_data['experience_duration']
        
        self.parsed_data['experience_duration'] = None
        #print('No experience duration found')
        return None
    
    def parse_skills(self):
        skills_text = self.sections.get('skills', '')
        resume_text = self.resume_text.lower()
        known_skills = self.known_skills['all']  # Use all known skills
        found_skills = set()
        
        # 1. First parse the skills section (more structured data)
        if skills_text:
            # Handle multiple formats: comma, semicolon, bullet points, newlines
            candidates = re.split(r'[,;•\-•\n\t]', skills_text)
            for candidate in candidates:
                candidate = candidate.strip()
                if candidate:
                    # Check both exact matches and lowercase versions
                    if candidate in known_skills:
                        found_skills.add(candidate)
                    elif candidate.lower() in known_skills:
                        found_skills.add(candidate.lower())

        # 2. Then search entire resume for known skills (more thorough)
        for skill in known_skills:
            # Create a regex pattern that matches the whole word
            pattern = r'(?<!\w)' + re.escape(skill.lower()) + r'(?!\w)'
            if re.search(pattern, resume_text, re.IGNORECASE):
                found_skills.add(skill)

        # 3. Additional check for multi-word skills (if needed)
        for skill in known_skills:
            if ' ' in skill:  # Only for multi-word skills
                pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                if re.search(pattern, resume_text, re.IGNORECASE):
                    found_skills.add(skill)

        self.parsed_data['skills'] = sorted(found_skills, key=lambda x: x.lower())
        return self.parsed_data['skills']
    
    def parse_certifications(self):
        """Extract certifications and licenses"""
        cert_text = self.sections.get('certifications', '')
        if not cert_text:
            return [] 
            
        certifications = []
        lines = cert_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip section headers
            if re.search(r'certificat(?:ions|es)|licenses?|trainings?', line, re.IGNORECASE):
                continue
                
            # Check for common certification patterns
            cert_match = re.search(r'^([A-Za-z0-9 \-]+)(?:\(([A-Za-z]+)\))?(?:\s*-\s*([A-Za-z0-9 ,\-]+))?', line)
            if cert_match:
                cert = {
                    'name': cert_match.group(1).strip(),
                    'issuer': cert_match.group(3).strip() if cert_match.group(3) else None,
                    'date': None
                }
                
                # Check for date in the line
                date_match = re.search(r'(?:20|19)\d{2}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}', line)
                if date_match:
                    cert['date'] = date_match.group(0)
                    
                certifications.append(cert)
                
        self.parsed_data['certifications'] = certifications
        #print(f'Parsed certifications: {certifications}')
        return certifications 
    
    def parse_all(self):
        """Parse all sections of the resume"""
        self.parse_metadata()
        self.parse_education()
        self.parse_experience()
        self.parse_skills()
        self.parse_certifications()
        return self.parsed_data