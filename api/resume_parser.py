import re
from datetime import datetime
from collections import defaultdict
from dateutil import parser
import os
import json
from typing import List, Tuple, Optional, Dict
import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException
from .resources import (supported_country_phonecodes, common_job_titles, career_objective_titles as cot,
                        education_section_titles as est, experience_section_titles as exst, skills_section_titles as sst,
                        certifications_section_titles as cst, other_boundary_section_titles as ost,
                        years_of_experience_map, degree_keywords, institution_keywords)
import unicodedata

class SmartPhoneExtractor:
    def __init__(self, supported_regions=None):
        self.supported_regions = supported_regions or  supported_country_phonecodes.keys()

    def extract_phone_numbers(self, text):
        """
        Extracts valid phone numbers from free text using phonenumbers.
        - Tries Nigerian format first
        - Falls back to other supported regions
        - Preserves unmatched numbers as raw
        """
        # Step 1: Extract digit-rich candidates (>=9 digits)
        candidates = candidates = re.findall(r'(?:\+?\d[\d\s().-]{8,}\d)', text) 
        cleaned_candidates= [re.sub(r'[^\d+]', '', c) for c in candidates] # remove non-digit characters except '+'
        
        if not cleaned_candidates:
            return []

        found_numbers = []

        for raw in cleaned_candidates:
            parsed_number = None

            # Step 2: Try Nigeria first
            try:
                number_obj = phonenumbers.parse(raw, 'NG')
                if phonenumbers.is_valid_number(number_obj):
                    parsed_number = phonenumbers.format_number(number_obj, phonenumbers.PhoneNumberFormat.E164)
            except NumberParseException:
                pass

            # Step 3: If Nigeria failed, try other supported regions
            if not parsed_number:
                for region in self.supported_regions:
                    try:
                        number_obj = phonenumbers.parse(raw, region)
                        if phonenumbers.is_valid_number(number_obj):
                            parsed_number = phonenumbers.format_number(number_obj, phonenumbers.PhoneNumberFormat.E164)
                            break
                    except NumberParseException:
                        continue

            # Step 4: Fallback to raw
            found_numbers.append(parsed_number or raw)

        return list(set(found_numbers))  # remove duplicates


class ResumeParser:
    def __init__(self, resume_text):
        self.resume_text = resume_text
        self.errors = []
        self.sectional_scores = {
            'contact': 20,
            'education': 20,
            'experience': 20,
            'skills': 20,
            'certifications': 20,
            'career_objective': 0
        }
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
        
    def _subtract_section_scores(self, section, score):
        """
        Subtracts a score from the sectional scores for a given section.
        If the section does not exist, it does nothing.
        """
        if section in self.sectional_scores:
            self.sectional_scores[section] -= score
            if self.sectional_scores[section] < 0:
                self.sectional_scores[section] = 0
    def get_ats_score(self):
        """
        Returns the total score based on the sectional scores.
        The total score is the sum of all sectional scores.
        """
        return sum(self.sectional_scores.values())
    
    def normalize_unicode(self, text):
        return unicodedata.normalize("NFKC", text)
    
    def _identify_sectionsxxx(self):
        """Identify major sections in the resume using common headings"""
        section_patterns = {
            'contact': r'(contact|personal)\s*(info|information|details)?',
            'education': r'education|academic\s*background|qualifications',
            'experience': r'experience|work\s*history|employment\s*history|professional\s*experience',
            'skills': r'skills|technical\s*skills|competencies|key\s*skills',
            'certifications': r'\b(certification(s)?|license(s)?|certificate(s)?|training(s)?)\b',
            'summary': (
                r'summary|profile|objective|about|introduction|career\s*summary|'
                r'career\s*objective|professional\s*summary|professional\s*objective'
            ),
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
    
    def _identify_sections(self):
        """Extracts section texts from the resume based on common headings."""
        sections = {
            'contact': self.extract_contact_section(),
            'education': self.extract_education_section(),
            'experience': self.extract_experience_section(),
            'skills': self.extract_skills_section(),
            'certifications': self.extract_certifications_section(),
            'career_objective': self.extract_career_objective_section()
        }
        
        # Clean up empty sections
        return {k: v for k, v in sections.items() if v}
    
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
    
    def extract_phone_numbers(self, text, default_country_code='234'):
        """
        Extract phone numbers from text with various international formats
        
        Supports:
        - International: +234 123 456 7890
        - US/CAN: (123) 456-7890, 123-456-7890, 123.456.7890
        - With extensions: 123-456-7890 x1234
        - Without separators: 1234567890
        """

        # Match international and US/CAN formats with optional extension
        pattern = r'''
            (?:
                (?:\+|00)?(\d{1,3})?       # Optional country code (e.g., +234, 1)
                [\s\-\.()]*                # Optional separators
            )?
            (\d{3})                        # Area code or first chunk
            [\s\-\.()]*
            (\d{3})                        # Second chunk
            [\s\-\.()]*
            (\d{4})                        # Third chunk
            (?:\s*(?:ext|x|\#)\s*(\d{1,5}))?  # Optional extension
        '''


        matches = re.findall(pattern, text, re.VERBOSE)
        phone_numbers = []

        for country_code, part1, part2, part3, extension in matches:
            digits = part1 + part2 + part3

            if not country_code:
                if digits.startswith('0'):
                    digits = digits[1:]
                    country_code = default_country_code
                else:
                    # Assume US/Canada (country code 1) if not specified
                    country_code = '1'

            full_number = f"+{country_code}{digits}"
            if extension:
                full_number += f" x{extension}"

            if re.fullmatch(r'\+\d{10,15}(?: x\d{1,5})?', full_number):
                phone_numbers.append(full_number)

        return list(set(phone_numbers)) # Remove duplicates and return unique phone numbers
    
    def parse_metadata(self):
        """Extract personal/contact information"""
        contact_text = self.sections.get('contact', '')
        if not contact_text:
            # self.errors.append('Contact Section: Your contact information such as name, email, and phone number should be in the first few lines of your resume before the Career Summary, Work Experience, Education, and Skills sections.')
            # self._subtract_section_scores('contact', 20)
            return {}
        
        # Email extraction (unchanged)
        emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', contact_text)
        if emails:
            self.parsed_data['metadata']['email'] = emails[0]
        else:
            self.errors.append('Contact Section - email: Ensure your email is correctly formatted: e.g yourname@yourdomain.com. For best practice, email should be within the first three lines in your resume, usually below your name.')
            self._subtract_section_scores('contact', 6)
        
        # Phone extraction 
        phone_extractor = SmartPhoneExtractor(supported_regions=supported_country_phonecodes.keys())
        phones = phone_extractor.extract_phone_numbers(contact_text)
        if phones:
            valid_numbers = [number for number in phones if re.fullmatch(r'\+\d{10,15}(?: x\d{1,5})?', number)]
            self.parsed_data['metadata']['phone'] = valid_numbers[0] if valid_numbers else None
        if not self.parsed_data['metadata'].get('phone'):
            self.errors.append('Contact Section - phone: Ensure your phone number is correctly formatted. For best practice, phone number should be within the first three lines in your resume, usually below your name. Use international format: e.g +2341234567890 or 1234567890.')
            self._subtract_section_scores('contact', 6)
        
        
        # Name extraction - ATS-style rule-based
        name_pattern = re.compile(
            r'''
            ^                                                           # Start of line
            (?:
                (?:                                                     # A name part can be:
                    [A-ZÀ-ÖØ-Ý]{2,}                                      # 2+ uppercase letters (e.g., AKINRINOLA)
                    | [A-ZÀ-ÖØ-Ý][a-zà-öø-ÿ'’\-]+                        # Proper-case name (e.g., Olamide)
                    | [A-Z]\.?                                           # Single-letter initial with optional dot (e.g., J. or J)
                )
                \s+
            ){1,3}                                                       # 2 to 4 parts total
            (?:                                                          # Optional last name part (4th)
                [A-ZÀ-ÖØ-Ý]{2,}
                | [A-ZÀ-ÖØ-Ý][a-zà-öø-ÿ'’\-]+
                | [A-Z]\.?
            )
            (?:\s+(?:Jr\.?|Sr\.?|II|III|IV|V))?                          # Optional suffix
            $                                                           # End of line
            ''',
            re.VERBOSE
        )
        
        if not self.parsed_data['metadata'].get('name'):
            # Strategy 1: First line that looks like a name
            first_lines = [self.normalize_unicode(line.strip()) for line in contact_text.split('\n') if line.strip()]
            for line in first_lines[:3]:
                line_lower = line.lower()
                if (
                    re.fullmatch(name_pattern, line)
                    and not any(skill in line_lower for skill in self.known_skills['all'])
                    and not any(title.lower() in line_lower for title in common_job_titles)
                ):
                    self.parsed_data['metadata']['name'] = line.strip()
                    break
            
            # Strategy 2: Before email/phone (common resume format)
            if not self.parsed_data['metadata'].get('name') and emails:
                pre_email_text = contact_text.split(emails[0])[0]
                lines = [line.strip() for line in pre_email_text.split('\n') if line.strip()]
                if lines:
                    # ensure line does not contain numbers
                    if (
                        re.fullmatch(name_pattern, line)
                        and not any(char.isdigit() for char in line)
                        and not any(skill in line_lower for skill in self.known_skills['all'])
                        and not any(title.lower() in line_lower for title in common_job_titles)
                    ):
                        self.parsed_data['metadata']['name'] = lines[-1].strip()
            
        if not self.parsed_data['metadata'].get('name'):
            self.errors.append('Contact Section - name: Ensure your name is clearly stated at the top of your resume. It should be the first line before your contact information. Name should be in all uppercase letters or proper case and should be bolded or larger than the rest of the text (e.g: Chisom Ayokunle Hamzat, Chisom A. Hamzat, C. A. Hamzat, or CHISOM HAMZAT). Avoid Abbreviations or using initials.')
            self._subtract_section_scores('contact', 8)
        
        # Location extraction - hybrid approach
        if not self.parsed_data['metadata'].get('location'):
            # Strategy 1: Common city/state/country patterns
            # location_pattern = r'\b(?:[A-Z][a-z]+\s*,\s*)?(?:[A-Z]{2}|\b[A-Z][a-z]+\b)(?:\s*\d{5})?\b'
            location_pattern = r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*(?:,\s*[A-Z][a-z]+(?:\s[A-Z][a-z]+)*){0,2}\b'
            contact_lines = [line.strip() for line in contact_text.split('\n') if line.strip()]
            if contact_lines:
                for line in contact_lines[:5]:
                    line_lower = line.lower()
                    if (
                        re.search(location_pattern, line)
                        and not any(skill in line_lower for skill in self.known_skills['all'])
                        and not any(title.lower() in line_lower for title in common_job_titles)
                    ):
                        matched = re.findall(location_pattern, line)
                        if matched:
                            self.parsed_data['metadata']['location'] = matched[0].strip()
                            print(f'Possible location found: {self.parsed_data["metadata"]["location"]}')
                            break
            
            # Strategy 2: After "Location:" or "Address:" markers
            if not self.parsed_data['metadata'].get('location'):
                for marker in ['location:', 'address:', 'based in']:
                    if marker in contact_text.lower():
                        marker_pos = contact_text.lower().find(marker)
                        possible_loc = contact_text[marker_pos + len(marker):].strip().split('\n')[0]
                        if possible_loc:
                            self.parsed_data['metadata']['location'] = possible_loc.strip(',. ')
                            # print(f'Possible location found: {self.parsed_data["metadata"]["location"]}')
                            break
        if not self.parsed_data['metadata'].get('location'):
            self.errors.append('Contact Section - address: Ensure your location is clearly stated. It should be in the format: City, State/Province, Country (e.g: Lagos, Nigeria). Location should be within the first five lines in your resume, usually below your name.')
            # self._subtract_section_scores('contact', 6)
        
        return self.parsed_data['metadata']

    def parse_education(self):
        """ description"""
        edu_text = self.sections.get('education', '')
        def normalize_doc_text(text: str) -> str:
            """
            Clean and standardize document line text for better parsing.
            - Replaces tabs and multiple spaces with single space.
            - Normalizes date range dashes (e.g., em dash, en dash, etc.).
            - Strips extra spaces around dashes.
            - Standardizes month abbreviations.
            """
            if not text:
                return ""

            # Replace tabs with space
            text = text.replace('\t', ' ')

            # Replace different dash types with regular dash
            text = re.sub(r'[\u2012\u2013\u2014\u2015–—]', '-', text)  # en-dash, em-dash, etc.

            # Remove multiple spaces and spaces around dashes
            text = re.sub(r'\s*-\s*', ' - ', text)  # normalize spacing around dash
            text = re.sub(r'\s+', ' ', text).strip()  # collapse multiple spaces

            # Optionally standardize months (e.g., Sept -> Sep)
            month_map = {
                'Sept': 'Sep',
                'January': 'Jan', 'February': 'Feb', 'March': 'Mar', 'April': 'Apr',
                'June': 'Jun', 'July': 'Jul', 'August': 'Aug', 'October': 'Oct',
                'November': 'Nov', 'December': 'Dec'
            }
            for full, abbr in month_map.items():
                text = re.sub(rf'\b{full}\b', abbr, text, flags=re.IGNORECASE)

            return text

        def is_degree_line(line: str) -> bool:
            """Check if a line is likely a degree line using a curated list of degree keywords."""
            pattern = r'\b(?:' + '|'.join(degree_keywords) + r')\b'
            return bool(re.search(pattern, line, re.I))

        def is_institution_line(line: str) -> bool:
            """Check if a line is likely an institution line."""
            pattern = r'\b(?:' + '|'.join(institution_keywords) + r')\b'
            return bool(re.search(pattern, line, re.I))

        def is_one_line_education(line: str) -> bool:
            """Check if a line is a one-line education entry."""
            institution_pattern = r'\b(?:' + '|'.join(institution_keywords) + r')\b'
            degree_pattern = r'\b(?:' + '|'.join(degree_keywords) + r')\b'
            return bool(re.search(institution_pattern, line, re.I) and re.search(degree_pattern, line, re.I))

        def identify_format(first_line: str) -> str:
            """
                Identify the format of the education entry based on the first line.

                Returns:
                    One of: 'degree_first', 'institution_first', 'one_line'
            """
            if is_one_line_education(first_line):
                return 'one_line'
            elif is_institution_line(first_line):
                return 'institution_first'
            elif is_degree_line(first_line):
                return 'degree_first'
            return ''

        def parse_education_format_single_line(entries: List[Dict[str, str]]) -> List[Dict[str, Optional[str]]]:
            """
            Parses education entries from a list of dicts with possible keys 'main_line' and 'description_line'.
            Handles common single-line formats with possible order reversals (degree, field, institution, date).
            Returns a list of structured dictionaries with keys: degree, field, institution, location, dates, description.
            """
            date_pattern = re.compile(
                r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)?\.?\s?\d{4}(?:\s?[-–to]+\s?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)?\.?\s?\d{4})?',
                re.IGNORECASE
            )

            def extract_date(text: str) -> Tuple[str, Optional[str]]:
                match = date_pattern.search(text)
                if match:
                    return text.replace(match.group(), '').strip(" ,–-"), match.group().strip()
                return text, None

            def extract_degree_and_field(text: str) -> (Tuple[Optional[str], Optional[str]]):
                for degree in sorted(degree_keywords, key=len, reverse=True):
                    pattern = rf'({degree})\s*(in)?\s*([\w &/-]+)'
                    match = re.search(pattern, text)  # case sensitive to avoid false positives
                    if match:
                        degree_found = match.group(1)
                        field = match.group(3).strip()
                        return degree_found, field
                return None, None

            def extract_institution_and_location(text: str) -> Tuple[Optional[str], Optional[str]]:
                for keyword in institution_keywords:
                    if keyword.lower() in text.lower():
                        parts = text.split(',')
                        institution = parts[0].strip()
                        location = ','.join(parts[1:]).strip() if len(parts) > 1 else ''
                        return institution, location
                return None, None

            results = []

            for entry in entries:
                main_line = entry.get("main_line", "").strip()
                description_line = entry.get("description_line", "").strip()
                #print(f'main line: {main_line}')

                if not main_line:
                    continue

                line, date = extract_date(main_line)
            
                # Try normal order: degree + field + institution
                degree, field = extract_degree_and_field(line)
                line_without_degree = line
                #print(f'degree, field: {degree}, {field}')
                
                if degree and field:
                    degree_field_text = f"{degree} in {field}" if "in" not in degree else f"{degree} {field}"
                    line_without_degree = line.replace(degree_field_text, '').strip(", ")
                    #print(f'line without degree: {line_without_degree}')

                institution, location = extract_institution_and_location(line_without_degree)

                # If parsing fails, try alternative order (e.g., institution first)
                if not (degree and field):
                    institution_guess, _ = extract_institution_and_location(line)
                    if institution_guess:
                        degree, field = extract_degree_and_field(line)

                # Skip if still missing essential info
                if not degree or not institution:
                    continue

                if not location:
                    # self.errors.append('Education Section: State your institution location along with it in this format: University of Ibadan, Oyo State Nigeria. The institution name and location should appear on the same line, separated only by a single comma.')
                    self.errors.append('Education Section - location: State your institution locattion after your institution name, separating them by a comma (e.g BSc in Computer Science, University of Ibadan, Oyo State Nigeria - Jun 2012).')
                    self._subtract_section_scores('education', round(4/len(entries), 2))
                if not date:
                    # self.errors.append('Education Section: Ensure you provide the date of graduation or duration of attendance for each education entry. This should be in the format: Jan 2020 - Dec 2020 or Jan 2020. It can be at the far right of the institution line or the degree line if using multi-line format (e.g: B.Sc in Computer Science      Jan 2020 - Dec 2020, Federal University of Owerri, Imo State Nigeria    Nov 2018), or separated by a dash from the main content in a single line format (e.g: B.Sc in Computer Science, Federal University of Owerri, Imo State Nigeria - Jan 2020 - Dec 2020).')
                    self.errors.append('Education Section - date: Ensure you provide the date of graduation or duration of attendance for each education entry. This should be in the format: Jan 2020 - Dec 2020 or Jan 2020. Note the date format (Month Year or you can use just the year). You can write the month name in full or just the first three letters (January or Jan). It should be separated by a dash from the main content (e.g: BSc in Computer Science, Federal University of Owerri, Imo State Nigeria - Jan 2020 - Dec 2020).')
                    self._subtract_section_scores('education', round(4/len(entries), 2))
                # if not description_line:
                #     self.errors.append('Education Section: You can use an extra line to provide additional information about your education, such as your Class of graduation or CGPA or something about your school project.')
                #     # self._subtract_section_scores('education', round(4/len(entries), 2))
                if not field:
                    self.errors.append('Education Section - field: Ensure you provide the field of study for each education entry. This should be in the format: BSc in Computer Science, MSc in Software Engineering, etc where the degree and the field are separated by the text "in".')
                    self._subtract_section_scores('education', round(4/len(entries), 2))
                # if not degree:
                #     self.errors.append('Education Section - degree: Ensure you provide the degree for each education entry. For best practice in a single-line format, write the degree name in full (e.g Bachelor of Science) or use non-punctuated abbreviations (e.g BSc, note the case formatting). Degree should be separated from the field by the text "in" (e.g BSc in Computer Science, Master of Science in Software Engineering).')
                #     self._subtract_section_scores('education', round(4/len(entries), 2))
                # if not institution:
                #     self.errors.append('Education Section - institution: Ensure you provide the institution name for each education entry. For a single-line format, the institution name should be clearly stated and separated from the degree and field by a comma (e.g BSc in Computer Science, University of Lagos, Lagos State Nigeria - Jun 2022) or (University of Lagos, Lagos State Nigeria, BSc in Computer Science - Jun 2022).')
                #     self._subtract_section_scores('education', round(4/len(entries), 2))
                results.append({
                    'degree': degree or '',
                    'field': field or '',
                    'institution': institution or '',
                    'location': location or '',
                    'date': date or '',
                    'description': description_line or ''
                })

            return results

        def extract_education_data(entries: List[Dict[str, str]]) -> List[Dict[str, str]]:
            """Description"""
            def extract_date(text: str) -> Tuple[str, Optional[str]]:
                """
                Extracts and removes the date portion from the line if present.
                Returns a tuple of (cleaned_text, extracted_date).
                """
                text = normalize_doc_text(text)
                date_regex = r'((?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|' \
                            r'May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|' \
                            r'Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)?\.?\s*\d{4}' \
                            r'(?:\s*(?:–|-|to)\s*(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|' \
                            r'Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|' \
                            r'Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)?\.?\s*\d{4})?)'

                match = re.search(date_regex, text, re.IGNORECASE)
                if match:
                    date = match.group(0).strip('–- ').strip()
                    # Replace only the matched substring
                    text_without_date = re.sub(re.escape(match.group(0)), '', text, count=1)
                    text_without_date = re.sub(r'[\s,–-]+$', '', text_without_date).strip()
                    return text_without_date, date

                return text.strip(), None

            def extract_field_and_degree(text: str) -> Tuple[str, str]:
                # Try to split on ' in ' first
                parts = re.split(r'\s+in\s+', text, flags=re.I)
                if len(parts) >= 2:
                    degree = parts[0].strip()
                    field = parts[1].strip()
                else:
                    degree = text.strip()
                    field = ""
                return field, degree
        
            def extract_institution_and_location(line: str) -> Tuple[str, Optional[str]]:
                """Extracts the institution and optional location."""
                if ',' in line:
                    parts = [p.strip() for p in line.split(',', 1)]
                    return parts[0], parts[1]
                return line.strip(), None

            result = []

            for entry in entries:
                degree_line = entry.get("degree_line", "").strip()
                institution_line = entry.get("institution_line", "").strip()

                # Skip if required fields are missing
                if not degree_line or not institution_line:
                    #result.append({})
                    continue

                degree_line_without_date, date = extract_date(degree_line)
                if not date:
                    institution_line, date = extract_date(institution_line)
                    
                field, degree = extract_field_and_degree(degree_line_without_date)
                institution_line_without_date = institution_line
                institution, location = extract_institution_and_location(institution_line_without_date)
                description = entry.get("description_line", "").strip()

                # if not institution:
                #     self.errors.append('Education Section - institution: Ensure you provide the institution name for each education entry. The institution name should be stated alongside its location and separated from each other by a comma (e.g University of Abuja, Abuja Nigeria). This should be on the first line if the degree is on the second line or on the second line if the degree is on the first line.')
                #     self._subtract_section_scores('education', round(4/len(entries), 2))
                if not location:
                    self.errors.append('Education Section - location: Ensure you provide the location of your institution. The institution location should be clearly stated and separated from the institution name by a comma (e.g University of Abuja, Abuja Nigeria). This should be on the first line if the degree is on the second line or on the second line if the degree is on the first line.')
                    self._subtract_section_scores('education', round(4/len(entries), 2))
                # if not degree:
                #     self.errors.append('Education Section - degree: Ensure you provide the degree for each education entry. For best practice, write the degree name in full (e.g Bachelor of Science) or non-punctuated abbreviations (e.g BSc, note the case formatting). Degree should be separated from the field by the text "in" (e.g BSc in Computer Science, Master of Science in Software Engineering). This should be on the first line if the institution is on the second line or on the second line if the institution is on the first line.')
                #     self._subtract_section_scores('education', round(4/len(entries), 2))
                if not field:
                    self.errors.append('Education Section - field: Ensure you provide the field of study for each education entry. This should be in the format: BSc in Computer Science, MSc in Software Engineering, etc Where the degree and the field are separated by the text "in". This should be on the first line if the institution is on the second line or on the second line if the institution is on the first line.')
                    self._subtract_section_scores('education', round(4/len(entries), 2))
                if not date:
                    self.errors.append('Education Section - date: Ensure you provide the date of graduation or duration of attendance for each education entry. This should be in the format: Jan 2020 - Dec 2020 or Jan 2020. Note the date format (Month Year or you can use just the year). You can write the month name in full or just the first three letters (January or Jan). The date should be on the far right of the either the Institution line or the degree line (e.g: BSc in Computer Science         Jan 2020 - Dec 2020) or (University of Lagos, Lagos State Nigeria         Dec 2020).')
                    self._subtract_section_scores('education', round(4/len(entries), 2))
                
                result.append({
                    "field": field,
                    "degree": degree,
                    "institution": institution,
                    "date": date if date else "",
                    "location": location if location else "", 
                    "description": description
                })

            return result

        def make_unique_dicts(lst):
            seen = set()
            result = []
            for d in lst:
                key = tuple(sorted(d.items()))
                if key not in seen:
                    seen.add(key)
                    result.append(d)
            return result
        
        if not edu_text:
            # self.errors.append('Education Section: Your education history should be clearly stated in the Education section of your resume. Ensure it is well-formatted with degrees, institutions, and dates.')
            # self._subtract_section_scores('education', 20)
            return []
        
        lines = [line.strip() for line in edu_text.splitlines() if line.strip()]
        
        if not lines:
            self.errors.append("Education Section - content: Your education should be clearly stated in the Education section of your resume. Ensure it is well-formatted with degrees, institutions, and dates. Follow either a single line format (Degree in Field, Instition, Location, Graduation date. e.g Bachelor of Science in Computer Science, University of Lagos, Lagos State Nigeria, Jan 2020) or a multi-line format (Degree in Field and Graduation date on the first line, Institution and Location on the second line, optional third line to state your class of graduation or CGPA. e.g Bachelor of Science in Computer Science Aug 2020 (on the first line); University of Lagos, Lagos State Nigeria (on the second line); Graduated with First Class Honours (optional, on the third line)). Maintain the same order for all your education entries.")
            self._subtract_section_scores('education', 20)
            return []
        
        entries = []
        #print(f'Lines: {lines}')
        mr = {}
        discript = []
        indx = 0
        entry_complete = False
        
        format_type = identify_format(lines[0])
        if not format_type:
            self.errors.append('Education Section - format: Your education data should follow a clear format. Ensure each entry has a degree, institution, and date. Use one of the following formats: Degree First line (e.g., B.Sc in Computer Science) and institution second line, Institution First line (e.g., University of Lagos, B.Sc in Computer Science) and degree on the second line, or One Line (e.g., B.Sc in Computer Science, University of Lagos, 2020). Use an extra 3rd or second line to provide a extra information like your Class of graduation or CGPA etc.')
            self._subtract_section_scores('education', 20)
            return []
        
        # Group lines into entries based on the detected format
        if format_type == 'degree_first' or format_type == 'institution_first':
            while indx < len(lines):
                # print(f'Lines[{indx}]: {lines[indx]}')
                if 'degree_line' in mr and 'institution_line' in mr:
                    if not entry_complete and not is_degree_line(lines[indx]) and not is_institution_line(lines[indx]):
                        #print(f'description line: {lines[indx]}')
                        mr['description_line'] = lines[indx].strip()
                        entry_complete = True
                    elif is_degree_line(lines[indx]) or is_institution_line(lines[indx]):
                        entry_complete = True
                
                if entry_complete:
                    entries.append(mr)
                    if not 'description_line' in mr:
                        self.errors.append('Education Section - description: You can use an extra line to provide additional information about your education, such as your Class of graduation or CGPA or something about your school project.')
                    mr = {}
                    entry_complete = False
                
                if is_degree_line(lines[indx]):
                    # print(f'degree line: {lines[indx]}')
                    mr['degree_line'] = lines[indx].strip()
                elif is_institution_line(lines[indx]):
                    # print(f'institution line: {lines[indx]}')
                    mr['institution_line'] = lines[indx].strip()
                
                if indx == len(lines) - 1 and ('degree_line' in mr and 'institution_line' in mr):
                    # If we reach the end and have a partial entry, add it
                    entries.append(mr)
                    if not 'description_line' in mr:
                        self.errors.append('Education Section - description: You can use an extra line to provide additional information about your education, such as your Class of graduation or CGPA or something about your school project.')
                indx += 1
        else: #treat as single line format
            #print(format_type)
            while indx < len(lines):
                if "main_line" in mr:
                    if not entry_complete and not is_degree_line(lines[indx]):
                        mr['description_line'] = lines[indx].strip()
                        entry_complete = True
                    elif is_degree_line(lines[indx]) or is_institution_line(lines[indx]):
                        entry_complete = True
                if entry_complete:
                    entries.append(mr)
                    if not 'description_line' in mr:
                        self.errors.append('Education Section - description: You can use an extra line to provide additional information about your education, such as your Class of graduation or CGPA or something about your school project.')
                    mr = {}
                    entry_complete = False
                if is_degree_line(lines[indx]) or is_institution_line(lines[indx]):
                    #print(f'degree line: {lines[indx]}')
                    mr['main_line'] = normalize_doc_text(lines[indx].strip())
                
                if indx == len(lines) - 1 and 'main_line' in mr:
                    # If we reach the end and have a partial entry, add it
                    entries.append(mr)
                    if not 'description_line' in mr:
                        self.errors.append('Education Section - description: You can use an extra line to provide additional information about your education, such as your Class of graduation or CGPA or something about your school project.')
                indx += 1
        
        if not entries:
            self.errors.append('Education Section - format: Your education history should be presented following a consistent format. Ensure it is well-formatted with degrees, institutions, and dates. Follow either a single line format (Degree in Field, Instition, Location, Graduation date. e.g Bachelor of Science in Computer Science, University of Lagos, Lagos State Nigeria, Jan 2020) or a multi-line format (Degree in Field and Graduation date on the first line, Institution and Location on the second line, optional third line to state your class of graduation or CGPA. e.g Bachelor of Science in Computer Science Aug 2020 (on the first line); University of Lagos, Lagos State Nigeria (on the second line); Graduated with First Class Honours (optional, on the third line)). Maintain the same order for all your education entries.')
            self._subtract_section_scores('education', 20)
            return []
        
        #print(f'Entries: {entries}')
        if format_type == "one_line":
            education_data = parse_education_format_single_line(entries)
        else:
            education_data = extract_education_data(entries)
        # print(f'Education data: {education_data}')
        if not education_data:
            self.errors.append('Education Section - format: Your education history should be presented following a consistent format. Ensure it is well-formatted with degrees, institutions, and dates. Follow either a single line format (Degree in Field, Instition, Location, Graduation date. e.g Bachelor of Science in Computer Science, University of Lagos, Lagos State Nigeria, Jan 2020) or a multi-line format (Degree in Field and Graduation date on the first line, Institution and Location on the second line, optional third line to state your class of graduation or CGPA. e.g Bachelor of Science in Computer Science Aug 2020 (on the first line); University of Lagos, Lagos State Nigeria (on the second line); Graduated with First Class Honours (optional, on the third line)). Maintain the same order for all your education entries.')
            self._subtract_section_scores('education', 20)
            return []
        # Normalize the education data
        for entry in education_data:
            for key, value in entry.items():
                if isinstance(value, str):
                    entry[key] = self.normalize_unicode(value)

        self.parsed_data['education'] = make_unique_dicts(education_data)
        return self.parsed_data['education']

    def parse_educationxxx(self):
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
        """Parse date string into a datetime object from various common formats"""
        date_str = date_str.strip()

        # List of possible formats
        formats = ['%B %Y', '%b %Y', '%Y-%m', '%Y']

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        return None  # If no format matched

    def _calculate_experience_years(self, date_ranges):
        """Calculate total years of experience from date ranges"""
        total_days = 0
        today = datetime.now()
        
        for date_range in date_ranges:
            dates = re.split(r'\s*(?:-|–|to)\s*', date_range, maxsplit=1)
            if len(dates) == 2:
                start_date = self._parse_date(dates[0].strip())
                end_text = dates[1].strip().lower()
                end_date = today if end_text in ['present', 'current'] else self._parse_date(dates[1].strip())
                
                if start_date and end_date and end_date > start_date:
                    total_days += (end_date - start_date).days

        return round(total_days / 365)  # Convert to years

    def extract_skills_section(self) -> str | None:
        """Extract the skills section text from the resume text."""
        section_boundaries = [title for title in ost + est + exst + cst + cot]  # all section titles excluding skills
        lines = [line.strip() for line in self.resume_text.splitlines() if line.strip()]

        def looks_like_header(line: str) -> bool:
            norm_line = ResumeParser.normalize_line(line)
            for title in sst:  # sst = skills section titles
                if norm_line == title.lower():
                    return True
            return False

        def looks_like_boundary(line: str) -> bool:
            norm_line = ResumeParser.normalize_line(line)
            for title in section_boundaries:
                if norm_line == title.lower():
                    return True
            return False

        # Search for skills section header
        for i, line in enumerate(lines):
            # Case 1: Skills on the same line, like "Skills: Python, SQL"
            for title in sst:
                if line.lower().startswith(title.lower() + ":"):
                    return line.split(":", 1)[1].strip() or None

            # Case 2: Standalone header
            if looks_like_header(line):
                start_idx = i

                # Find end of section
                end_idx = len(lines)
                for j in range(start_idx + 1, len(lines)):
                    if looks_like_boundary(lines[j]):
                        end_idx = j
                        break

                # return "\n".join(lines[start_idx + 1:end_idx]).strip() or None
                base_text = "\n".join(lines[start_idx + 1:end_idx]).strip()
                if not base_text:
                    self.errors.append("Skills Section: Your skills should be listed in the Skills section of your resume. Mark them with a header like 'Skills' or 'Technical Skills'. You use simple rounded bullet point for eack skill. You can group your skills or list them as is (e.g., Python, SQL, Java; or groups like this- Programming: Python, Dart, C++).")
                    self._subtract_section_scores('skills', 20)
                return base_text
            
        # If no skills section found
        self.errors.append("Skills Section - title: Your skills should be listed in the Skills section of your resume. Mark them with a header like 'Skills' or 'Technical Skills'. You can use simple rounded bullet point for each skill. You can group your skills or list them as is (e.g., Python, SQL, Java; or groups like this - Programming: Python, Dart, C++).")
        self._subtract_section_scores('skills', 20)
        return None

    def extract_education_section(self) -> str | None:
        """ Extract the education section text from the resume text. """
        section_boundaries = [title for title in ost + sst + exst + cst + cot]  # exclude est itself
        lines = [line.strip() for line in self.resume_text.splitlines() if line.strip()]

        def looks_like_header(line: str) -> bool:
            norm_line = ResumeParser.normalize_line(line)
            for title in est:  # est = education section titles
                # if title in line or title.upper() in line:
                if norm_line == title.lower():
                    return True
            return False

        def looks_like_boundary(line: str) -> bool:
            norm_line = ResumeParser.normalize_line(line)
            for title in section_boundaries:
                # if title in line or title.upper() in line:
                if norm_line == title.lower():
                    return True
            return False

        # Find the start of the education section
        start_idx = None
        for i, line in enumerate(lines):
            if looks_like_header(line):
                start_idx = i
                break

        if start_idx is None:
            self.errors.append("Education Section - Title: Your resume should contain a clearly marked education section. Mark this off with a clearly stated title like: Education, Academic Background, or Academic Qualifications. Should be written in all upper case letters or proper case.")
            self._subtract_section_scores('education', 20)
            return None

        # Find the end (next known section header)
        end_idx = len(lines)
        for i in range(start_idx + 1, len(lines)):
            if looks_like_boundary(lines[i]):
                end_idx = i
                break

        # Return content below the header
        base_text = "\n".join(lines[start_idx + 1:end_idx]).strip()
        if not base_text:
            self.errors.append("Education Section - content: Your education should be clearly stated in the Education section of your resume. Ensure it is well-formatted with degrees, institutions, and dates. Follow either a single line format (Degree in Field, Instition, Location, Graduation date. e.g Bachelor of Science in Computer Science, University of Lagos, Lagos State Nigeria, Jan 2020) or a multi-line format (Degree in Field and Graduation date on the first line, Institution and Location on the second line, optional third line to state your class of graduation or CGPA. e.g Bachelor of Science in Computer Science Aug 2020 (on the first line); University of Lagos, Lagos State Nigeria (on the second line); Graduated with First Class Honours (optional, on the third line)). Maintain the same order for all your education entries.")
            self._subtract_section_scores('education', 20)
        return base_text
        
    def extract_certifications_section(self) -> str | None:
        """ Extract the certifications section text from the resume text. """
        section_boundaries = [title for title in ost + sst + exst + est + cot]  # exclude cst itself
        lines = [line.strip() for line in self.resume_text.splitlines() if line.strip()]

        def looks_like_header(line: str) -> bool:
            norm_line = ResumeParser.normalize_line(line)
            for title in cst:  # cst = certification section titles
                # if title in line or title.upper() in line:
                if norm_line == title.lower():
                    return True
            return False

        def looks_like_boundary(line: str) -> bool:
            norm_line = ResumeParser.normalize_line(line)
            for title in section_boundaries:
                # if title in line or title.upper() in line:
                if norm_line == title.lower():
                    return True
            return False

        # Find the start of the certifications section
        start_idx = None
        for i, line in enumerate(lines):
            if looks_like_header(line):
                start_idx = i
                break

        if start_idx is None:
            self.errors.append("Certifications Section - title: Your certifications should be clearly stated in the Certifications section of your resume. Mark this off with a clearly stated title like: Certifications, Professional Certifications, or Professional Qualifications. Should be written in all upper case letters or proper case.")
            self._subtract_section_scores('certifications', 20)
            return None

        # Find the end (next known section header)
        end_idx = len(lines)
        for i in range(start_idx + 1, len(lines)):
            if looks_like_boundary(lines[i]):
                end_idx = i
                break

        # Return content below the header
        base_text = "\n".join(lines[start_idx + 1:end_idx]).strip() or None
        if not base_text:
            self.errors.append("Certifications Section - content: Your certifications should be clearly stated in the Certifications section of your resume. Mark this off with a clearly stated title like: Certifications, Professional Certifications, or Professional Qualifications. Should be written in all upper case letters or proper case.")
            self._subtract_section_scores('certifications', 20)
        return base_text

    def extract_contact_section(self) -> str | None:
        """ Extract the contact section text from the resume text. """
        # Combine all possible section headers (excluding contact)
        section_boundaries = ost + sst + exst + est + cst + cot

        lines = [line.strip() for line in self.resume_text.splitlines() if line.strip()]

        def looks_like_boundary(line: str) -> bool:
            normal_line = ResumeParser.normalize_line(line)
            for title in section_boundaries:
                # if title in line or title.upper() in line:
                if normal_line == title.lower():
                    return True
            return False

        end_idx = len(lines)
        for i, line in enumerate(lines):
            if looks_like_boundary(line):
                end_idx = i
                break

        base_text = "\n".join(lines[:end_idx]).strip() or None
        if not base_text:
            self.errors.append("Contact Section - extraction: Your contact information such as your name, email, phone number should all be in the first few lines of your resume before Career Summary, Work Experience, Education, or Skills sections.")
            self._subtract_section_scores('contact', 20)
        return base_text

    def extract_career_objective_section(self) -> str | None:
        section_boundaries = [title for title in ost + exst + sst + est + cst]

        lines = [line.strip() for line in self.resume_text.splitlines() if line.strip()]

        def looks_like_header(line: str) -> bool:
            normal_line = ResumeParser.normalize_line(line)
            for title in cot:
                # if title.title() in line or title.upper() in line:
                if normal_line == title.lower():
                    return True
            return False

        def looks_like_boundary(line: str) -> bool:
            normal_line = ResumeParser.normalize_line(line)
            for title in section_boundaries:
                # if title.title() in line or title.upper() in line:
                if normal_line == title.lower():
                    return True
            return False

        # Find the start of the objective section
        start_idx = None
        for i, line in enumerate(lines):
            if looks_like_header(line):
                start_idx = i
                break

        if start_idx is None:
            self.errors.append("Career Objective/Summary Section - title: Your career objective should be clearly stated in the first few lines of your resume before Work Experience, Education, or Skills sections. Mark this off with a clearly stated title like: Career Objective, SUMMARY, or Career Profile or just Objective. Should be written in all upper case letters or proper case.")
            return None

        # Find the end (next known section header)
        end_idx = len(lines)
        for i in range(start_idx + 1, len(lines)):
            if looks_like_boundary(lines[i]):
                end_idx = i
                break

        # Return content below the header
        # return "\n".join(lines[start_idx + 1:end_idx]).strip() or None
        base_text = "\n".join(lines[start_idx + 1:end_idx]).strip() or None
        if not base_text:
            self.errors.append("Career Objective/Summary Section - extraction: Your career objective should be clearly stated in the first few lines of your resume before Work Experience, Education, or Skills sections. Mark this off with a clearly stated title like: Career Objective, SUMMARY, or Career Profile or just Objective. Should be written in all upper case letters or proper case.")
            self._subtract_section_scores('career_objective', 20)
        return base_text

    def extract_experience_section(self) -> str | None:
        """Extract the experience section text from the resume text."""
        section_boundaries = [title for title in ost + sst + est + cst + cot]

        lines = [line.strip() for line in self.resume_text.splitlines() if line.strip()]

        def looks_like_header(line: str) -> bool:
            normal_line = ResumeParser.normalize_line(line)
            for title in exst:
                # if title.title() in line or title.upper() in line:
                if normal_line == title.lower():
                    return True
            return False

        def looks_like_boundary(line: str) -> bool:
            normal_line = ResumeParser.normalize_line(line)
            for title in section_boundaries:
                # if title.title() in line or title.upper() in line:
                if normal_line == title.lower():
                    return True
            return False

        # Find the start of the experience section
        start_idx = None
        for i, line in enumerate(lines):
            if looks_like_header(line):
                start_idx = i
                break

        if start_idx is None:
            self.errors.append("Experience Section - title: Your work experience should be clearly stated within your resume. Mark this off with a clearly stated title like: Work Experience, Professional Experience, Employment History, or Career History. Should be written in all upper case letters or proper case. If you have no work experience, you can provide your internship or volunteer experience.")
            self._subtract_section_scores('experience', 20)
            return None

        # Find the end (next known section header)
        end_idx = len(lines)
        for i in range(start_idx + 1, len(lines)):
            if looks_like_boundary(lines[i]):
                end_idx = i
                break

        # Return content below the header
        # return "\n".join(lines[start_idx + 1:end_idx]).strip() or None
        base_text = "\n".join(lines[start_idx + 1:end_idx]).strip() or None
        if not base_text:
            self.errors.append("Experience Section - content: Provide some infomation about your work history. If you have no work experience, you can provide your internship or volunteer experience. Ensure it is well-formatted with job titles, company names, locations, and dates. Follow a consistent format for all entries.")
            self._subtract_section_scores('experience', 20)
        return base_text
    
    def parse_experience(self):
        """Extract number of years of work experience from resume text"""
        years_of_experience = ''
        years = 0
        def extract_years_of_experience_from_summary_text(text: str) -> int | None:
            if not text:
                return None
            
            patterns = [
                r'\b(\d{1,2})\+?\s+(?:years|yrs?)\b',
                r'\bover\s+(\d{1,2})\s+(?:years|yrs?)\b',
                r'\bmore than\s+(\d{1,2})\s+(?:years|yrs?)\b',
                r'\b(?:with|have|has)\s+(\d{1,2})\s+(?:years|yrs?)\b',
                r'\b(' + '|'.join(years_of_experience_map.keys()) + r')\s+(?:years|yrs?)\b',
                r'\b(?:\w+\s+)?\((\d{1,2})\)\s+(?:years|yrs?)\b',
            ]

            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    value = match.group(1).lower()
                    if value.isdigit():
                        return int(value)
                    elif value in years_of_experience_map:
                        return years_of_experience_map[value]

            return None
        
        def extract_experience_durations(text: str) -> List[str]:
            if not text:
                return []

            lines = [line.strip() for line in text.splitlines() if line.strip()]

            # Separator: hyphen, en dash, em dash, or "to" (case-insensitive, with optional spaces)
            sep = r'[-–—]|to'

            # Month variants (short and full)
            month = r'(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'

            # Patterns
            date_patterns = [
                # Month YYYY to Month YYYY
                rf'{month}\s+\d{{4}}\s*(?:{sep})\s*{month}\s+\d{{4}}',
                # Month YYYY to Present/Current/Ongoing
                rf'{month}\s+\d{{4}}\s*(?:{sep})\s*(Present|Current|Ongoing)',
                # MM/YYYY to MM/YYYY
                rf'\d{{2}}/\d{{4}}\s*(?:{sep})\s*\d{{2}}/\d{{4}}',
                # YYYY to YYYY
                rf'\b\d{{4}}\s*(?:{sep})\s*\d{{4}}\b',
                # YYYY to Present/Current/Ongoing
                rf'\b\d{{4}}\s*(?:{sep})\s*(Present|Current|Ongoing|Till date|Till now|Till Present)\b'
            ]

            combined_pattern = re.compile(rf"({'|'.join(date_patterns)})$", re.IGNORECASE)

            matched_durations = []
            for line in lines:
                match = combined_pattern.search(line)
                if match:
                    matched_durations.append(match.group(1).strip())

            return matched_durations
        
        def split_date_ranges(durations: List[str]) -> List[str]:
            if not durations:
                return []

            # Match common separators: hyphen, en dash, em dash, or "to" (with optional spaces)
            separator_pattern = re.compile(r'\s*(?:to|[-–—])\s*', flags=re.IGNORECASE)

            # Flat list to collect all individual date components
            split_dates = []
            
            for duration in durations:
                parts = separator_pattern.split(duration)
                # Keep only non-empty trimmed parts
                for part in parts:
                    clean_part = part.strip()
                    if clean_part:
                        split_dates.append(clean_part)

            return split_dates

        def get_date_range_bounds(date_strings: List[str]) -> tuple[datetime, datetime]:
            present_keywords = {'present', 'current', 'till date', 'till now', 'now'}
            parsed_dates = []

            for date_str in date_strings:
                normalized = date_str.strip().lower()

                # Replace present/current-like terms with today's date
                if normalized in present_keywords:
                    parsed_dates.append(datetime.today())
                else:
                    try:
                        parsed = parser.parse(date_str, default=datetime(1900, 1, 1))
                        parsed_dates.append(parsed)
                    except Exception:
                        pass  # Ignore unparseable entries

            if not parsed_dates:
                return None, None

            return min(parsed_dates), max(parsed_dates)
        
        def calculate_total_experience_from_bounds(bounds: list[tuple[datetime, datetime]]) -> str:
            total_months = 0

            for start, end in bounds:
                if start > end:
                    start, end = end, start
                delta_months = (end.year - start.year) * 12 + (end.month - start.month)
                total_months += max(delta_months, 0)

            total_years = total_months // 12
            remaining_months = total_months % 12

            if total_years and remaining_months:
                return f"{total_years} Years {remaining_months} Months of Professional Experience"
            elif total_years:
                return f"{total_years} Years of Professional Experience"
            elif remaining_months:
                return f"{remaining_months} Months of Professional Experience"
            else:
                return "Less than a month of Professional Experience"
        
        # Strategy 1: Search in the career objective section
        career_objective = self.sections.get('career_objective', '')

        if career_objective:
            # Check for explicit experience mentions
            years = extract_years_of_experience_from_summary_text(career_objective)
            if years is not None:
                # number_of_years = f"{years} Years of Professional Experience"
                years_of_experience = f"{years} Years of Professional Experience"
            else:
                self.errors.append("Career Objective Section - content: It is a good practice to summarize your years of experience in your career summary section. Use ATS-friendly formats like '5+ years of experience' or '3-5 years of experience' summarize your total career experience in years.")
        
        # if not years or years <= 0:
        # Strategy 2: Search in the experience section
        deduction = 10
        if not years or years <= 0:
            deduction = 20
        experience_section = self.sections.get('experience', '')
        if experience_section:
            # Extract experience durations from the section
            durations = extract_experience_durations(experience_section)
            # print(f'Extracted durations: {durations}')
            if durations:
                # print(f'Extracted durations: {durations}')
                split_dates = split_date_ranges(durations)
                if split_dates:
                    # print(f'Split dates: {split_dates}')
                    bounds = get_date_range_bounds(split_dates)
                    if bounds[0] and bounds[1]:
                        # print(f'Bounds: {bounds}')
                        # number_of_years = calculate_total_experience_from_bounds([bounds])
                        if not years or years <= 0:
                            years_of_experience = calculate_total_experience_from_bounds([bounds])
                    else:
                        self.errors.append("Experience Section - experience duration: Ensure you provide clear date ranges for your work experience in the format: 'Jan 2021 - Aug 2024' or '2021 - 2024'.")
                        self._subtract_section_scores('experience', deduction)
            else:
                self.errors.append("Experience Section - experience duration: Your work experience should be clearly stated within your resume. Ensure it is well-formatted with job titles, company names, locations, and most importantly, the duration of the experience. Follow a consistent format for all entries. Duration of the experience should be a date range (start date - end date). For best practice, use month and year to represent the date, or just year (e.g Jun 2021 - Aug 2024 or 2021 - 2024). You can represent month name in full or just the first three letters as seen earlier, no punctuations. ATS algorithms will usually look for the dates on the same line where you provide the company name, or the job title line. If you have no work experience, you can provide your internship or volunteer experience.")
                self._subtract_section_scores('experience', deduction)
        
        if years_of_experience:
            self.parsed_data['experience'] = years_of_experience
            self.parsed_data['experience_duration'] = years_of_experience
            return years_of_experience
        else:
            self.parsed_data['experience'] = 'Less than a month of Professional Experience'
            self.parsed_data['experience_duration'] = 'Less than a month of Professional Experience'
            return 'Less than a month of Professional Experience'
  
    def parse_experiencexxx(self):
        """Extract work experience duration from entire resume text"""
        exp_text = self.sections.get('experience', '') or self.resume_text
        # First try explicit duration patterns (e.g., "5+ years", "3-5 years")
        range_pattern = r'(?P<min_years>\d+)\s*(?:\+|\–|-)\s*(?P<max_years>\d+)?\s*(?:year|yr)s?'
        range_match = re.search(range_pattern, exp_text, re.IGNORECASE)
        
        if range_match:
            min_years = range_match.group('min_years')
            max_years = range_match.group('max_years') or min_years
            self.parsed_data['experience_duration'] = f"{min_years}-{max_years} years experience"
            self.parsed_data['experience'] = self.parsed_data['experience_duration']
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
            
            self.parsed_data['experience'] = self.parsed_data['experience_duration']
            #print(f'Experience duration (level match): {self.parsed_data["experience_duration"]}')
            return self.parsed_data['experience_duration']
        
        # Fall back to date range calculation (your existing implementation)
        # date_ranges = re.findall(
        #     r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}'
        #     r'\s*(?:-|–|to)\s*'
        #     r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?[a-z]* \d{4}|present|current',
        #     exp_text,
        #     re.IGNORECASE
        # )

        date_ranges = re.findall(
            r'(?:'
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}'  # e.g., Jan 2021
            r'|'
            r'\d{4}-\d{2}'  # e.g., 2021-06
            r')'
            r'\s*(?:-|–|to)\s*'
            r'(?:'
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?[a-z]* \d{4}'  # e.g., Mar 2022
            r'|'
            r'\d{4}-\d{2}'  # e.g., 2022-03
            r'|'
            r'present|current'
            r')',
            exp_text,
            re.IGNORECASE
        )
        
        if date_ranges:
            total_years = self._calculate_experience_years(date_ranges)
            if total_years > 0:
                self.parsed_data['experience_duration'] = f"{total_years} years experience"
                self.parsed_data['experience'] = self.parsed_data['experience_duration']
                return self.parsed_data['experience_duration']
            else:
                self.parsed_data['experience_duration'] = 'Less than 1 year experience'
                self.parsed_data['experience'] = self.parsed_data['experience_duration']
                return self.parsed_data['experience_duration']
        
        self.parsed_data['experience_duration'] = None
        #print('No experience duration found')
        return None
    
    def parse_skills(self):
        """Extract skills from resume text"""
        skills_text = self.sections.get('skills', '')
        known_skills = self.known_skills['all']  # Use all known skills
        found_skills = set()

        if not skills_text:
            # self.errors.append("Skills Section: Your skills should be listed in the Skills section of your resume. Mark them with a header like 'Skills' or 'Technical Skills'. You use simple rounded bullet point for each skill. You can group your skills or list them as is (e.g., Python, SQL, Java; or groups like this- Programming: Python, Dart, C++).")
            # self._subtract_section_scores('skills', 20)
            return []
        
        def extract_skills_list_from_one_line_text(skills_text: str) -> Optional[list[str]]:
            """
            Processes multi-line text and extracts a clean list of skills from each line
            formatted like: 'GroupName: item1, item2, item3'.
            Accepts colon, dash, en-dash, or em-dash as group-item separators.
            Splits skill items using common delimiters: comma, semicolon, bullet, pipe, etc.
            Returns a flat list of all extracted skills, or None if none found.
            """
            if not skills_text or len(skills_text) > 5000:
                return None

            skills = []

            # Process each line separately
            for line in skills_text.splitlines():
                line = line.strip()
                if not line:
                    continue

                # Match line like "GroupName: item1, item2" or "GroupName - item1; item2"
                # match = re.match(r"^[\w\s]+[:\-–—]\s*(.+)", line)
                match = re.match(r"^[\w\s]+[:\-–—]\s+(.+)", line)
                if not match:
                    continue

                skills_part = match.group(1)

                # Split the skill list using common delimiters
                items = re.split(r"[,\u2022;\|\u2023\u25AA\u25CF\u2024\u2027\-•·]+", skills_part)
                cleaned = [item.strip() for item in items if item.strip()]
                skills.extend(cleaned)

            return skills or None

        def extract_skills_from_multiline_text(skills_text: str) -> list[str] | None:
            """
            Extracts a clean list of skills from a multiline skills section.
            Handles grouped and ungrouped formats, with optional bullets.
            Groups: Start with 'Label:' followed by lines that continue the group.
            Ungrouped: Just a list of skills, one per line.
            Items in each line can be separated by common delimiters.
            Lines not matching known ATS-friendly formats are ignored.
            """

            if not skills_text:
                return None

            lines = [line.strip() for line in skills_text.splitlines() if line.strip()]
            skill_items = []
            current_group_lines = []

            def remove_bullet(line: str) -> str:
                return re.sub(r"^[\u2022\-\u25CF\*]+ ", "", line).strip()

            def split_skills(line: str) -> list[str]:
                # Split on common delimiters
                return [s.strip() for s in re.split(r"[,\u2022;\|\u2023\u25AA\u25CF\u2024\u2027–—•·]+", line) if s.strip()]

            for line in lines:
                line = remove_bullet(line)

                # New skill group (e.g., "Technical Skills:")
                if re.match(r"^[\w\s]+:\s*$", line):
                    # Process previous group if it exists
                    if current_group_lines:
                        for group_line in current_group_lines:
                            skill_items.extend(split_skills(group_line))
                        current_group_lines = []

                # Group continuation or ungrouped line
                else:
                    current_group_lines.append(line)

            # Process the last buffered group or list
            if current_group_lines:
                for group_line in current_group_lines:
                    skill_items.extend(split_skills(group_line))

            return skill_items or None

        # 1. First extract all the skills listed in the skills text following standard formats
        skills_list = extract_skills_list_from_one_line_text(skills_text)
        if skills_list:
            # add to found_skills
            # print(f'Extracted skills from one-line text: {skills_list}')
            found_skills.update(skill.title() for skill in skills_list)

        skills_list = extract_skills_from_multiline_text(skills_text) # if not skills_list else skills_list
        if skills_list:
            # print(f'Extracted skills from multiline text: {skills_list}')
            # add to found_skills
            found_skills.update(skill.title() for skill in skills_list)
        
        if not found_skills:
            self.errors.append("Skills Section: Use bullet points to present your skills in the Skills section of your resume. You can group your skills or list them as is (e.g., Python, SQL, Java; or groups like this- Programming: Python, Dart, C++). When listing in groups, ensure the group name is separated from the skills by a colon (:), dash (-), en-dash (–), or em-dash (—) wisth a space after the separator. Use common delimiters like comma, semicolon, bullet point, pipe, etc., to separate individual skills within the group.")
            self._subtract_section_scores('skills', 20)
            return []
        
        # 2. Then search other parts of the resume for known skills
        resume_text = self.resume_text.lower().replace(skills_text, '')  # Exclude skills section text

        for skill in known_skills:
            # Create a regex pattern that matches the whole word
            pattern = r'(?<!\w)' + re.escape(skill.lower()) + r'(?!\w)'
            if re.search(pattern, resume_text, re.IGNORECASE):
                found_skills.add(skill.title())
        
        # Return sorted skills, case-insensitive
        self.parsed_data['skills'] = sorted(found_skills, key=lambda x: x.lower())
        # print(f'Parsed skills: {self.parsed_data["skills"]}')
        return self.parsed_data['skills']
    
    def parse_skillsxxx(self):
        skills_text = self.sections.get('skills', '')
        resume_text = self.resume_text.lower()
        known_skills = self.known_skills['all']  # Use all known skills
        found_skills = set()
        
        # 1. First parse the skills section (more structured data)
        if skills_text:
            # print(f'Skills section text: {skills_text}')
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
        # print(f'Found skills in section 1: {found_skills}')

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
    
    def parse_certifications(self) -> List[Dict[str, Optional[str]]]:
        """
            Extracts certification information from raw text following a standardized format.
            Handles multiple formats including:
            - Single-line: "Certification Name - Issuer, Date"
            - Multi-line: "Certification Name - Issuer\nDate"
            - No-date: "Certification Name - Issuer"
            
            Returns:
                List of dictionaries with keys: 'name', 'issuer', 'date' (optional)
        """
        if 'certifications' not in self.sections:
            return []
        
        cert_text = self.sections['certifications'].strip()
        # print(f'Certifications section text: {cert_text}')
        if not cert_text:
            return []
        
        def normalize_text(text: str) -> str:
            """Normalize text for consistent parsing"""
            # Standardize dashes and spacing
            text = re.sub(r'[\u2012\u2013\u2014\u2015–—]', ' - ', text)  # All dash types to hyphen
            text = re.sub(r'\s+', ' ', text).strip()  # Collapse whitespace
            return text
        
        def extract_date(text: str, lone=False) -> Tuple[str, Optional[str]]: 
            """Extract and remove date from text if present.
            
            If lone is True, expect the text to contain only the date. Otherwise, return None as date.
            """
            date_patterns = [
                r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4})',  # Month Year
                r'(\d{1,2}/\d{4})',  # MM/YYYY
                r'(\b\d{4}\b)',  # YYYY
                r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\s*(?:-|to)\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4})'  # Date range
            ]

            for pattern in date_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    date = match.group(1)

                    if lone:
                        # Normalize input and match to ensure date is the only content
                        if re.fullmatch(r'\s*' + re.escape(date) + r'\s*', text, re.IGNORECASE):
                            return '', date
                        else:
                            return text, None
                    else:
                        cleaned_text = re.sub(re.escape(date), '', text).strip(' ,-')
                        return cleaned_text, date

            return text, None
        
        def parse_certification_line(line: str) -> Dict[str, Optional[str]]:
            """Parse a single certification line into components"""
            line = normalize_text(line)
            cert = {'name': None, 'issuer': None, 'date': None}
            
            # First extract date if present
            line_without_date, date = extract_date(line)
            if date:
                cert['date'] = date
            
            # Split into name and issuer
            # parts = re.split(r'\s+-\s+', line_without_date, maxsplit=1)
            parts = re.split(r'\s*(?:–|-|\||,)\s*', line_without_date, maxsplit=1) # Handle various separators
            if len(parts) == 2:
                cert['name'] = parts[0].strip()
                cert['issuer'] = parts[1].strip()
            else:
                cert['name'] = line_without_date.strip()
            
            return cert
        
        def identify_format(lines: List[str]) -> str:
            """Identify the certification format pattern"""
            if not lines:
                return 'unknown'
            
            # Check for multi-line format (date on second line)
            if len(lines) >= 2:
                _, first_date = extract_date(lines[0], lone=True)
                _, second_date = extract_date(lines[1], lone=True)
                if not first_date and second_date:
                    return 'multi-line'
            
            # Default to single-line format
            return 'single-line'
        
        # Process the certifications
        lines = [line.strip() for line in cert_text.split('\n') if line.strip()]
        format_type = identify_format(lines)
        # print(f'Identified format type: {format_type}')
        certifications = []
        
        if format_type == 'multi-line':
            # Process pairs of lines (certification line + date line)
            i = 0
            while i < len(lines) - 1:
                cert_line = lines[i]
                date_line = lines[i + 1]
                
                cert = parse_certification_line(cert_line)
                _, date = extract_date(date_line)
                if date:
                    cert['date'] = date
                
                if cert['name']:  # Only add if we have at least a name
                    certifications.append(cert)
                else:
                    self.errors.append("Certifications Section - name: List your certifications in single or double lines. For single line, the certificate name be followed by the issuer name. These two should be separated by a comma (,), pipe (|) or hyphen (-). For double line, the first line should contain the certificate name and issuer name separated by a comma (,) or pipe (|), then the date of issue, separated by a hyphen (-). For double line: the certificate and issuer on the first line, the date on the second line.")
                    self._subtract_section_scores('certifications', round(20 / len(lines), 2))
                i += 2
        else:
            # Process each line independently
            for line in lines:
                cert = parse_certification_line(line)
                # print(f'Parsed certification: {cert}')
                if cert['name']:  # Only add if we have at least a name
                    certifications.append(cert)
                else:
                    self.errors.append("Certifications Section - name: List your certifications in single or double lines. For single line, the certificate name be followed by the issuer name. These two should be separated by a comma (,), pipe (|) or hyphen (-). For double line, the first line should contain the certificate name and issuer name separated by a comma (,) or pipe (|), then the date of issue, separated by a hyphen (-). For double line: the certificate and issuer on the first line, the date on the second line.")
                    self._subtract_section_scores('certifications', round(20 / len(lines), 2))
        
        if not certifications:
            # self.errors.append("Certifications Section: List your certifications in single or double lines. For single line, the certificate name be followed by the issuer name. These two should be separated by a comma (,) or pipe (|) or hyphen (-). For double line, the first line should contain the certificate name and issuer name separated by a comma (,) or pipe (|), then the date of issue, separated by a hyphen (-). For double line: the certificate and issuer on the first line, the date on the second line.")
            # self._subtract_section_scores('certifications', 20)
            return []
        
        # Remove duplicates while preserving order
        seen = set()
        unique_certs = []
        for cert in certifications:
            key = (cert['name'], cert.get('issuer'), cert.get('date'))
            if key not in seen:
                seen.add(key)
                unique_certs.append(cert)
        
        for certs in unique_certs:
            if not certs.get('name'):
                self.errors.append("Certifications Section - name: List your certifications in single or double lines. For single line, the certificate name be followed by the issuer name. These two should be separated by a comma (,), a pipe (|) or hyphen (-). For double line, the first line should contain the certificate name and issuer name separated by a comma (,) or pipe (|), then the date of issue, separated by a hyphen (-). For double line: the certificate and issuer on the first line, the date on the second line.")
                self._subtract_section_scores('certifications', round(20 / len(unique_certs), 2))
            if not certs.get('issuer'):
                self.errors.append("Certifications Section - issuer: State the name of your certificate issuer immediately after the certificate name. These two should be separated by a comma (,), pipe (|) or hyphen (-). (e.g 'AWS Certified Cloud Practitioner – Amazon Web Services').")
                self._subtract_section_scores('certifications', round(10 / len(unique_certs), 2))
            if not certs.get('date'):
                self.errors.append("Certifications Section - date: State the date of issue of your certificate. This should be on the first line, separated by a hyphen (-) from the other content. Or on the second line alone. (e.g 'AWS Certified Cloud Practitioner – Amazon Web Services - Jul 2023').")
                self._subtract_section_scores('certifications', round(10 / len(unique_certs), 2))
        
        self.parsed_data['certifications'] = unique_certs
        return self.parsed_data['certifications']
    
    def parse_certificationsxxx(self):
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
        self.parsed_data['ats_score'] = self.get_ats_score()
        self.parsed_data['errors'] = self.errors
        return self.parsed_data
    
    # static methods
    @staticmethod
    def normalize_line(line: str) -> str:
        # Remove common prefixes and suffixes (like bullets, colons) and normalize casing
        return re.sub(r"^[•\-–\*\s]*|[:\-\s]*$", "", line.strip()).lower()