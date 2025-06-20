from docx import Document
from docx.text.paragraph import Paragraph
from docx.oxml.ns import qn
from io import BytesIO
from .ai import call_gemini
import json
from docx.oxml import OxmlElement
from docx.shared import Inches
from docx.enum.text import WD_TAB_ALIGNMENT
import os
from auth_user.models import MatchedResumeData
from docx.oxml import OxmlElement
from docx.text.paragraph import Paragraph
from .template_layouts import tp_layouts

def insert_paragraph_afterxxx(paragraph: Paragraph, text='', style=None):
    """
    Insert a new paragraph after the given paragraph.

    Args:
        paragraph (Paragraph): The reference paragraph after which the new paragraph will be inserted.
        text (str): The text for the new paragraph.
        style (str): The style to apply (e.g., 'List Bullet').

    Returns:
        Paragraph: The newly inserted paragraph.
    """
    # Get the XML element of the reference paragraph
    p_element = paragraph._p

    # Create a new XML paragraph element <w:p>
    new_p_element = OxmlElement('w:p')

    # Insert the new paragraph element after the reference paragraph element
    p_element.addnext(new_p_element)

    # Wrap the XML element back into a python-docx Paragraph object
    new_paragraph = Paragraph(new_p_element, paragraph._parent)

    # Add text and style
    if text:
        new_paragraph.add_run(text)
    if style:
        new_paragraph.style = style

    return new_paragraph

def insert_paragraph_after(paragraph: Paragraph, text='', style=None):
    """
    Insert a new paragraph after the given paragraph.
    Formats skill categories as bold, followed by comma-separated skills.

    Args:
        paragraph (Paragraph): Reference paragraph
        text (str|dict): String or dict of {category: [skills]}
        style (str): Style to apply

    Returns:
        Paragraph: Newly inserted paragraph
    """
    # Get the XML element of the reference paragraph
    p_element = paragraph._p

    # Create new paragraph element
    new_p_element = OxmlElement('w:p')
    p_element.addnext(new_p_element)
    new_paragraph = Paragraph(new_p_element, paragraph._parent)

    # Handle dictionary of categorized skills
    if isinstance(text, dict):
        content = []
        for category, skills in text.items():
            # Add bold category name
            content.append(f"{category}: ")
            # Add comma-separated skills
            content.append(", ".join(skills))
        
        # Add all content to the paragraph
        run = new_paragraph.add_run("".join(content))
        
        # Make category names bold
        for category in text.keys():
            start = run.text.find(category)
            if start >= 0:
                end = start + len(category)
                run.bold = True  # Make the entire run bold
                break
        
        if style:
            new_paragraph.style = style
        return new_paragraph

    # Original string handling
    if text:
        new_paragraph.add_run(text)
    if style:
        new_paragraph.style = style

    return new_paragraph



class ResumeGenerator:
    template_path = "templates/general.docx"
    output_path = "templates/processed.docx"
    _document = None
    user_data = {
        "name": "John Doe",
        "professional_title": "Software Engineer",
        "city": "Ibadan",
        "state": "Oyo",
        "country": "Nigeria",
        "phone": "+234 123 456 7890",
        "email": "jondoe@gmail.com",
        "git": "https://github.com/jondo",
        'linkedin': "https://linkedin.com/in/jon-do",
        "portfolio": "https://jondo.com",
        "objective": "To leverage my skills in software development to contribute to innovative projects.",
        "skills": ["Python", "JavaScript"],
        "certification": {"cert_name": "AWS Certified Solutions Architect", "cert_issuer": "Amazon", "issue_date": "2023-01", "cert_expiry": "2025-03 or Never"},
        "experience": {"company": "Tech Company", "position": "Software Engineer", "experience_duration": "2022-01 to 2023-01", "descriptions": ["Developed web applications using Python and Django.", "Collaborated with cross-functional teams to define, design, and ship new features."], "achievements": ["Increased application performance by 20%.", "Led a team of 5 developers to deliver a project ahead of schedule."]}, 
        "project": {"title": "Automated Machine Monitoring System", "technologies": "python, pylogix, SQLite", "date": "2023", "description": ["Developed a real-time monitoring app to track PLC machine status and log downtimes.", "Improved maintenance response time by 40%."]},
        "education": {"degree": "B.Sc in Computer Science", "institution": "University of Ibadan", "graduation_date": "2022-11"},
    }

    matching_user_data = {
        "name": "John Doe",
        "professional_title": "Software Engineer",
        "city": "Ibadan",
        "state": "Oyo",
        "country": "Nigeria",
        "git": "https://github.com/jondo",
        'linkedin': "https://linkedin.com/in/jon-do",
        "portfolio": "https://jondo.com",
        "phone": "+234 123 456 7890",
        "email": "jondoe@gmail.com",
        "objective": "To leverage my skills in software development to contribute to innovative projects.",
        "skills": ["Python", "JavaScript"],
        "certifications": [
            {
                "cert_name": "AWS Certified Solutions Architect", 
                "cert_issuer": "Amazon", 
                "issue_date": "2023-01", 
                "cert_expiry": "2025-03 or Never",
                "description": "Demonstrated ability to design distributed systems on AWS"
            }, 
            {
                "cert_name": "Certified data analyst", 
                "cert_issuer": "IBM", 
                "issue_date": "2023-06", 
                "cert_expiry": "2025-03 or Never",
                "description": "Demonstrated ability to design distributed systems on AWS"
            }
        ],
        "experience": [
            {
                "company": "Tech Company", 
                "position": "Software Engineer", 
                "experience_duration": "2022-01 to 2023-01",
                "start_date": "2022-01",
                "end_date": "2023-01", 
                "description": ["Developed web applications using Python and Django.", "Collaborated with cross-functional teams to define, design, and ship new features."], 
                "achievements": ["Increased application performance by 20%.", "Led a team of 5 developers to deliver a project ahead of schedule."]
            }, 
            {...}
        ], 
        "education": [
            {
                "degree": "B.Sc", 
                "institution": "University of Ibadan",
                "field_of_study": "Computer Science",
                "start_date": "2018-10",
                "end_date": "2022-11",
                "description": "Graduated with First Class Honours", 
                "graduation_date": "2022-11"
            }, 
            {...}
        ],
        "subjects": [
            {"title": "Educational Psychology & Classroom Management", "description": "A theory-and-practice course focusing on learner motivation, behavioral analysis, and inclusive education."},
            {"title": "Curriculum Design & Instructional Strategies", "description": "A course on designing effective curricula and employing diverse instructional strategies to enhance learning outcomes."},
            {"title": "Basic Technology", "description": "An introductory course on technology integration in education, covering digital tools and resources."},
            {...}
        ],
        "publications": [
            {"title": "Reforming Procurement Law in Nigeria: A Legislative Framework for Transparency", "source": "Published in the African Journal of Law & Public Policy, Vol. 12, Issue 3", "description": "Explores weaknesses in Nigeria’s Public Procurement Act and proposes amendments for better compliance and oversight.", "date": "2021"},
            {"title": "The Impact of E-Government on Public Service Delivery in Nigeria", "source": "Published in the Journal of Public Administration and Governance, Vol. 10, Issue 2", "description": "Analyzes the effectiveness of e-government initiatives in improving public service delivery in Nigeria.", "date": "2022"},
            {...}
        ],
        "teaching": [
            {"institution": "Federal University of Agriculture, Abeokuta", "role": "course instructor", "subject": "Molecular Genetics (BIO 304)", "description": "Taught 3rd-year undergraduates core concepts of molecular biology and genetic engineering", "date": "2023"},
            {"institution": "University of Ibadan", "role": "Teaching Assistant", "subject": "Introduction to Computer Science (CSC 101)", "description": "Assisted in teaching introductory computer science concepts to first-year students.", "date": "2022"},
            {...}
        ],
        "research": [
            {"title": "Investigating the Effects of Climate Change on Agricultural Productivity in Nigeria", "description": "A comprehensive study analyzing the impact of climate change on crop yields and food security in Nigeria.", "date": "2023"},
            {"title": "The Role of Renewable Energy in Sustainable Development", "description": "Explores how renewable energy sources can contribute to sustainable development goals in developing countries.", "date": "2022"},
            {...}
        ],
        "project": [
            {
                "title": "Automated Machine Monitoring System",
                "technologies": "python, pylogix, SQLite",
                "date": "2023",
                "description": ["Developed a real-time monitoring app to track PLC machine status and log downtimes.", "Improved maintenance response time by 40%."]
            },
            {...}
        ]
    }

    def __init__(self, resume_data=None, filename=None, matching=False, user=None):
        self.filename = filename
        self.resume_data = resume_data
        self.user_object = user
        if not matching:
            prompt = self.__generate_prompt()
            self.user_data = self.__promptGemini(prompt)
        else:
            self.job_description = resume_data['job_description']
            prompt = self.__generate_matching_prompt()
            self.matching_user_data = self.__promptGemini(prompt)
            self.log_matched_resume_data()
            self.deduct_resume_credit()
    
    # method that subtracts resume credit from non-premium users after resume generation
    def deduct_resume_credit(self):
        """Deducts resume credit from non-premium users after resume generation."""
        if self.user_object and not self.user_object.is_premium:
            if self.user_object.resume_credits > 0:
                self.user_object.resume_credits -= 1
                self.user_object.save()
            else:
                raise ValueError("Insufficient resume credits.")
        
    
    def log_matched_resume_data(self):
        """Logs the matched resume data to the database."""
        if not self.matching_user_data:
            return
        
        # Check if user exists
        if not self.user_object:
            raise ValueError("User object is required to log matched resume data.")
        
        # Always save the matched resume data
        MatchedResumeData.objects.create(
            user=self.user_object,
            job_title=self.matching_user_data.get('professional_title', 'Unknown'),
            resume_data=self.matching_user_data
        )
     
    def __generate_prompt(self) -> str:
        if self.resume_data is None:
            return "No resume data provided."
        return f"""
        Use the resume data provided to generate a structured resume data for me. return your response in JSON format structured as indicated below.
        Craft a profesionally-worthy objective statement that is relevant to the job title and industry with ATS-friendly keywords.
        Include industry-relevant soft skills in the skills section. Skills section cannot be empty.
        Of all certifications data provided, return only the most relevant one, well-presented for job applications in the field. Return None if no relevant certification is provided.
        Return the most relevant work experience data provided, well-presented for job applications in the field. Return None if no relevant work experience is provided.
        For the experience, generate 4 quantied achievements based on the experience data provided.
        Return the most relevant education data provided, well-presented for job applications in the field.

        SPECIAL CONSIDERATIONS:

        Work Experience Section:
        * if no end_date is provided, use "Present" as the end date.
        * return a maximum of 4 achievements items.
        * do not use place holders for quantification. use realistic imaginary quantification numbers like 15%, 20%, 30%, etc.

        Skills Section:
        * return a maximum of 4 skills items if certification data was provided, otherwise return 6 skills items only.
        * each item should be a single word or a short phrase not more than 35 characters long.

        The numbers in the the expected format represents the maximum number of characters for each item.
        Please do not include the numbers in your response.

        Resume_data:
        {self.resume_data}

        Expected JSON format:
        {self.user_data}           
        """
    
    def __generate_matching_prompt(self) -> str:
        # print(f"Resume text:\n{self.resume_data['resume_text']}")
        return f"""
        You are a professional resume editor and recruiter. 
        Your task is to re-write a candidate’s resume to make it closely match a specific job description (JD), optimizing it for maximum recruiter appeal and applicant tracking system (ATS) compatibility.

        Instructions:

        Analyze the job description and resume provided.

        Rewrite the resume to:

        Emphasize keywords and phrases found in the JD.

        Reposition and highlight relevant experiences, skills, and achievements.

        Remove irrelevant or unnecessary information that does not contribute to the JD.

        Maintain factual accuracy — do not fabricate sensitive information such as:

            Education

            Certifications

            Work experience

            Technical skills

            Projects

            You may infer and include missing but commonly expected content such as:

                Soft skills

                Summary/objective

                Role-aligned phrasing
        
        SPECIAL CONSIDERATIONS:

        Work Experience Section:
        * if no descriptions are provided, generate a maximum of 3 based on the role
        * if no achievements is provided, generate possible imaginary ones based on the descriptions
        * return a maximum of 4 achievements items.
        * do not use place holders for quantification. use realistic imaginary quantification numbers like 15%, 20%, 30%, etc.

        Education Section:
        * if no descriptions are provided, return imaginary possible one
        * graduation date is the same as end_date
        * the degree value should be the degree abreviation: B.Sc, M.Sc, OND, HND etc

        Certification Section:
        * if no expiry date is provide, return N/A
        * if no issue date is provided, return in-progress
        * if no description is provided, return imaginary one

        Subjects Section:
        * if no description is provided, return imaginary possible one
        * this section is for teachers and educators only, so it should contain subjects they have taught or are qualified to teach.

        Publications Section:
        * if no description is provided, return imaginary possible one

        Teaching Section:
        * if no description is provided, return imaginary possible one
        * this section is for science and research lecturers, so it should contain subjects they have taught or are qualified to teach.
        * it should be different from the subjects section, which is for teachers and educators, and work experience section, which is for general professionals in other fields.
        
        Research Section:
        * if no description is provided, return imaginary possible one
        * this section is for science and research lecturers, so it should contain research they have interest in.  


        Skills Section:
        * each item should be a single word or a short phrase not more than 35 characters long.
        For a ui/ux designer, return skills as a list of dictionaries with the following keys: Design, Prototyping, Research, Project Tools, Soft Skills, Branding, Code. Their respective values should be a list of skills relevant to the key.

        We will use your data to generate a clean, modern, recruiter-friendly resume with clearly labeled sections (e.g., Summary, Skills, Experience, Education).

        If any of the following are missing — job description, resume, or structural format — return an empty string.

        Job Description (JD):
        {self.job_description}

        Resume_data:
        {self.resume_data['resume_text']}

        Expected JSON format:
        {self.matching_user_data}
        """
    
    def __promptGemini(self, prompt: str) -> dict:
        # Placeholder for the actual Gemini API call
        try:
            text = call_gemini(prompt)
            text = text.replace('```json', '')
            text = text.replace('```', '')
            # print(f'Gemini response: {text}')
            response = json.loads(text)
        except Exception as e:
            print(f"Error calling Gemini: {e}")
            response = {}
        
        return response

    def _insert_bullets(self, doc, anchor_text, items):
        for i, para in enumerate(doc.paragraphs):
            if anchor_text in para.text:
                para.text = para.text.replace(anchor_text, "")
                if isinstance(items, dict):
                    for key, value in items.items():
                        mr = {}
                        mr[key] = value
                        # Insert bullet paragraph after the anchor
                        insert_paragraph_after(para, mr, style='List Bullet')
                elif isinstance(items, list):
                    for item in items:
                        # Insert bullet paragraph after the anchor
                        insert_paragraph_after(para, item, style='List Bullet')
                break
    
    def __select_template(self, template_id:str=''):
        """Select the appropriate template based on user data."""

        if template_id:
            self.template_path = f"templates/{template_id}.docx"        
        elif self.resume_data.get("certifications"):
            self.template_path = "templates/general_certification.docx"
        
        if not os.path.exists(self.template_path):
            raise FileNotFoundError(f"{self.template_path} not found")
        
        return self.template_path
    
    def populate_template(self):
        """Populate a Word template with user data and save the result."""
        # Early exit checks
        if not self.user_data:
            print("No user data available.")
            return ''
        if not self.filename:
            print("No filename available.")
            return ''
        # Select template
        self.template_path = self.__select_template()

        try:
            doc = Document(self.template_path)
            placeholder_cache = {}  # Cache for parsed placeholders

            # Process paragraphs
            for para in doc.paragraphs:
                if not para.text:  # Skip empty paragraphs
                    continue
                    
                para_text = para.text
                modified = False
                
                # Check for simple placeholders first
                for key, value in self.user_data.items():
                    if isinstance(value, str):
                        placeholder = f"{{{{{key}}}}}"
                        if placeholder in para_text:
                            para_text = para_text.replace(placeholder, value)
                            modified = True
                    elif isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            if isinstance(sub_value, str):
                                placeholder = f"{{{{{sub_key}}}}}"
                                if placeholder in para_text:
                                    para_text = para_text.replace(placeholder, sub_value)
                                    modified = True
                
                # Update paragraph if modified
                if modified:
                    # Clear existing runs more efficiently
                    para.clear()
                    para.add_run(para_text)

            # Process lists
            list_fields = {
                "{{skills_list}}": self.user_data.get("skills", []),
                "{{certifications_list}}": self.user_data.get("certifications", []),
                "{{achievements}}": self.user_data.get("experience", {}).get("achievements", []),
            }

            for anchor, items in list_fields.items():
                if items:  # Only process if there are items
                    self._insert_bullets(doc, anchor, items)
            
            # Remove unused placeholders
            self._clean_unused_placeholders(doc)

            # Create directory if it doesn't exist
            os.makedirs('generated_docs', exist_ok=True)
            
            # Save directly to file instead of using BytesIO
            save_path = os.path.join('generated_docs', self.filename)
            doc.save(save_path)
            
            return self.filename
            
        except Exception as e:
            print(f"Error populating template: {str(e)}")
            return ''
        
    def populate_matching_template(self, template_id:str):
        """Populate a Word template with user data and save the result."""
        result = ''

        if template_id == 'ats_bold_classic_resume' or 'ats_bold_classic_resume' in template_id:
            result = self.populate_ats_bold_classic_resume()
        
        if result == '':
            raise Exception('Failed to populate resume template')
        
        return result

    def populate_ats_bold_classic_resume(self):
        """ Processes the ATS Bold Classic template (v2.1)
        
            Requirements:
            - Requires experience in reverse-chronological order
            - Skills must be < 25 characters each
        """
        # helper functions
        def process_simple_fields(doc):
            """Process simple key-value pairs in the document."""
            for para in doc.paragraphs:
                if not para.text:
                    continue
                    
                para_text = para.text
                modified = False
                
                for key, value in self.matching_user_data.items():
                    if isinstance(value, str):
                        placeholder = f"{{{{{key}}}}}"
                        if placeholder in para_text:
                            para_text = para_text.replace(placeholder, value)
                            modified = True
                    elif isinstance(value, dict) and not any(k in key.lower() for k in ['education', 'skills', 'experience', 'certification', 'projects']):
                        for sub_key, sub_value in value.items():
                            if isinstance(sub_value, str):
                                placeholder = f"{{{{{sub_key}}}}}"
                                if placeholder in para_text:
                                    para_text = para_text.replace(placeholder, sub_value)
                                    modified = True
                
                if modified:
                    para.clear()
                    para.add_run(para_text)
        
        def process_multi_item_sections(doc):
            """Process sections with perfectly aligned dates at line ends."""
            
            template_id = self.resume_data.get('template_id')
            multi_item_sections = tp_layouts.get(template_id)

            if not multi_item_sections:
                multi_item_sections = tp_layouts['ats_bold_classic_resume']
                
            for section, config in multi_item_sections.items():
                items = self.matching_user_data.get(section, [])
                if not items:
                    continue
                    
                section_paragraphs = []
                
                for item_idx, item in enumerate(items):
                    item_paragraphs = []
                    
                    for line_config in config['item_template']:
                        # Create new paragraph if needed
                        if line_config.get('new_paragraph', True):
                            p = doc.add_paragraph()
                            item_paragraphs.append(p)
                            
                            # Configure tab stops for dated lines
                            if line_config.get('type') == 'dated_line':
                                tab_stops = p.paragraph_format.tab_stops
                                tab_stops.add_tab_stop(Inches(6), WD_TAB_ALIGNMENT.RIGHT)
                            
                            if line_config.get('bullet', False):
                                p.style = 'List Bullet'
                                if line_config.get('indent', 0) > 0:
                                    p.paragraph_format.left_indent = Inches(line_config['indent'])
                                    p.paragraph_format.first_line_indent = Inches(-0.25)  # Proper bullet spacing
                        
                        # Handle dated lines with perfect date alignment
                        if line_config.get('type') == 'dated_line':
                            content = line_config['content']
                            dates = line_config['dates']
                            
                            # Replace placeholders in content
                            for key, value in item.items():
                                if isinstance(value, str):
                                    placeholder = f"{{{{{key}}}}}"
                                    content = content.replace(placeholder, value)
                                    dates = dates.replace(placeholder, value)
                            
                            # Add content and dates with tab separation
                            run = p.add_run(content)
                            if line_config.get('content_bold', False):
                                run.bold = True
                            p.add_run('\t')  # Tab character for alignment
                            p.add_run(dates)
                            continue
                        
                        # Handle list-type descriptions
                        if line_config.get('is_list', False) and 'description' in item and isinstance(item['description'], list):
                            for i, bullet_point in enumerate(item['description']):
                                if i > 0:
                                    p = doc.add_paragraph(style='List Bullet')
                                    p.paragraph_format.left_indent = Inches(line_config.get('indent', 0.5))
                                    p.paragraph_format.first_line_indent = Inches(-0.25)
                                    item_paragraphs.append(p)
                                
                                p.add_run(bullet_point)
                            continue
                        
                        # Handle regular text
                        if 'text' in line_config:
                            line_text = line_config['text']
                            for key, value in item.items():
                                if isinstance(value, str):
                                    placeholder = f"{{{{{key}}}}}"
                                    line_text = line_text.replace(placeholder, value)
                                elif isinstance(value, list):
                                    value = "\n".join(value)
                                    placeholder = f"{{{{{key}}}}}"
                                    line_text = line_text.replace(placeholder, value)
                            
                            run = p.add_run(line_text)
                            if line_config.get('bold', False):
                                run.bold = True
                            if line_config.get('italic', False):
                                run.italic = True
                    
                    # Add separator between items (except after last item)
                    if item_idx < len(items) - 1:
                        separator_para = doc.add_paragraph()
                        separator_para.add_run(config['separator'])
                        item_paragraphs.append(separator_para)
                    
                    section_paragraphs.extend(item_paragraphs)
                
                # Replace placeholder with styled content
                replace_placeholder_with_styled_content(
                    doc,
                    config.get('template_placeholder') or config.get('template_anchor'),
                    section_paragraphs
                )

        def process_bullet_lists(doc):
            """Process simple bullet list sections."""
            list_fields = {
                "{{skills_list}}": self.matching_user_data.get("skills", []),
            }

            for anchor, items in list_fields.items():
                if items:
                    self._insert_bullets(doc, anchor, items)

        def replace_placeholder_with_styled_content(doc, placeholder, new_paragraphs):
            """Replace a placeholder with styled paragraphs."""
            for para in doc.paragraphs:
                if placeholder in para.text:
                    # Get the parent element of the paragraph
                    parent = para._element.getparent()
                    # Get the index of the paragraph in its parent
                    index = parent.index(para._element)
                    
                    # Remove the placeholder paragraph
                    parent.remove(para._element)
                    
                    # Insert the new paragraphs at the same position
                    for new_para in reversed(new_paragraphs):
                        parent.insert(index, new_para._element)
                    
                    break

        # Early exit checks
        if not self.matching_user_data:
            # print("No user data available.")
            return ''
        if not self.filename:
            # print("No filename available.")
            return ''
        # Select template
        self.__select_template(self.resume_data.get('template_id', ''))

        try:
            doc = Document(self.template_path)
            self._document = doc

            # Process simple fields (name, contact info, etc.)
            process_simple_fields(doc)
            # print("Simple fields processed successfully.")
            
            # Process multi-item sections
            process_multi_item_sections(doc)
            # print("Multi-item sections processed successfully.")
            
            # Process bullet lists
            process_bullet_lists(doc)
            # print("Bullet lists processed successfully.")

            # Remove unused placeholders
            self._clean_unused_placeholders(doc)
            # print("Unused placeholders cleaned successfully.")

            # Save the document
            os.makedirs('generated_docs', exist_ok=True)
            save_path = os.path.join('generated_docs', self.filename)
            doc.save(save_path)
            
            return self.filename
            
        except Exception as e:
            print(f"Error populating template: {str(e)}")
            return ''
    
    def _clean_unused_placeholders(self, doc: Document) -> None:
        """
        Remove all unused placeholders and their associated formatting elements.
        Handles three cases:
        1. Simple inline placeholders (remove placeholder only)
        2. Labeled placeholders (remove label + placeholder)
        3. Sectional placeholders (remove section header + divider + placeholder)
        """
        # Define placeholder patterns for each case
        placeholder_groups = {
            'simple': [
                '{{name}}', '{{email}}', '{{phone}}', 
                '{{city}}', '{{state}}', '{{country}}'
            ],
            'labeled': [
                ('Git:', '{{git}}'),
                ('Portfolio:', '{{portfolio}}'),
                ('LinkedIn:', '{{linkedin}}')
            ],
            'sectional': [
                '{{certification_section}}', '{{experience_section}}', '{{education_section}}',
                '{{project_section}}', '{{skils_list}}',
                '{{publication_section}}', '{{objective}}'
            ]
        }

        # Process simple placeholders
        for placeholder in placeholder_groups['simple']:
            self._remove_simple_placeholder(doc, placeholder)

        # Process labeled placeholders
        for label, placeholder in placeholder_groups['labeled']:
            self._remove_labeled_placeholder(doc, label, placeholder)

        # Process sectional placeholders
        for placeholder in placeholder_groups['sectional']:
            self._remove_sectional_placeholder(doc, placeholder)

    def _remove_simple_placeholder(self, doc: Document, placeholder: str) -> None:
        """Remove simple inline placeholders that weren't replaced."""
        for paragraph in doc.paragraphs:
            if placeholder in paragraph.text:
                paragraph.text = paragraph.text.replace(placeholder, "").strip()
                # Remove paragraph if empty
                if not paragraph.text:
                    self._remove_paragraph(paragraph)

    def _remove_labeled_placeholder(self, doc: Document, label: str, placeholder: str) -> None:
        """
        Remove placeholders with preceding labels.
        Example: "Git: {{git}}" -> removes entire line when placeholder exists
        """
        for paragraph in doc.paragraphs:
            if placeholder in paragraph.text and label in paragraph.text:
                # Check if this is the only content in the paragraph
                full_pattern = f"{label} {placeholder}"
                if paragraph.text.strip() == full_pattern:
                    self._remove_paragraph(paragraph)
                else:
                    # Handle cases where label+placeholder are part of larger text
                    paragraph.text = paragraph.text.replace(full_pattern, "").strip()

    def _remove_sectional_placeholder(self, doc: Document, placeholder: str) -> None:
        """
        Remove sectional placeholders and their associated header structure.
        Removes:
        - The paragraph containing the placeholder
        - The divider paragraph immediately above it (index-1)
        - The section header paragraph above that (index-2)
        """
        paragraphs = doc.paragraphs
        to_remove = set()

        for i, paragraph in enumerate(paragraphs):
            if placeholder in paragraph.text:
                # Always remove the placeholder paragraph
                to_remove.add(i)
                
                # Remove divider paragraph (immediately above)
                if i > 0:
                    to_remove.add(i-1)
                    
                    # Remove section header (two above)
                    if i > 1:
                        to_remove.add(i-2)

        # Remove marked paragraphs in reverse order to maintain indices
        for i in sorted(to_remove, reverse=True):
            if i < len(paragraphs):
                self._remove_paragraph(paragraphs[i])

    def _is_horizontal_rule(self, paragraph: Paragraph) -> bool:
        """More reliable horizontal rule detection."""
        text = paragraph.text.strip()
        
        # Check for line characters
        line_chars = {'─', '━', '═', '—', '―', '-', '_', '='}
        if text and all(c in line_chars for c in text):
            return True
            
        # Check for empty paragraph with special formatting
        if not text and paragraph.paragraph_format.space_after == 0:
            return True
            
        return False

    def _remove_paragraph(self, paragraph: Paragraph) -> None:
        """Safely remove a paragraph from the document."""
        p = paragraph._element
        p.getparent().remove(p)
        p._p = p._element = None
