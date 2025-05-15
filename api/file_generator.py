from docx import Document
from docx.text.paragraph import Paragraph
from docx.oxml.ns import qn
from io import BytesIO
from .ai import call_gemini
import json
from docx.oxml import OxmlElement
import os
# from auth_user.serializers import UserSerializer
# from django.contrib.auth import get_user_model

from docx.oxml import OxmlElement
from docx.text.paragraph import Paragraph

def insert_paragraph_after(paragraph: Paragraph, text='', style=None):
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
        new_run = new_paragraph.add_run(text)
    if style:
        new_paragraph.style = style

    return new_paragraph


class ResumeGenerator:
    template_path = "templates/general.docx"
    output_path = "templates/processed.docx"
    user_data = {
        "name": "John Doe",
        "professional_title": "Software Engineer",
        "city": "Ibadan",
        "state": "Oyo",
        "country": "Nigeria",
        "phone": "+234 123 456 7890",
        "email": "jondoe@gmail.com",
        "objective": "To leverage my skills in software development to contribute to innovative projects.",
        "skills": ["Python", "JavaScript"],
        "certification": {"cert_name": "AWS Certified Solutions Architect", "cert_issuer": "Amazon", "issue_date": "2023-01", "cert_expiry": "2025-03 or Never"},
        "experience": {"company": "Tech Company", "position": "Software Engineer", "experience_duration": "2022-01 to 2023-01", "descriptions": ["Developed web applications using Python and Django.", "Collaborated with cross-functional teams to define, design, and ship new features."], "achievements": ["Increased application performance by 20%.", "Led a team of 5 developers to deliver a project ahead of schedule."]}, 
        "education": {"degree": "B.Sc in Computer Science", "institution": "University of Ibadan", "graduation_date": "2022-11"},
    }

    def __init__(self, resume_data=None, filename=None):
        self.filename = filename
        self.resume_data = resume_data
        prompt = self.__generate_prompt()
        self.user_data = self.__promptGemini(prompt)
    
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
                for item in items:
                    # Insert bullet paragraph after the anchor
                    insert_paragraph_after(para, item, style='List Bullet')
                break
    
    def __select_template(self):
        """Select the appropriate template based on user data."""
        
        if self.resume_data.get("certifications"):
            self.template_path = "templates/general_certification.docx"
        return self.template_path
    
    def populate_template(self):
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

            for para in doc.paragraphs:
                para_text = para.text  # Full paragraph text
                
                for key, value in self.user_data.items():
                    if isinstance(value, str):
                        placeholder = f"{{{{{key}}}}}"
                        if placeholder in para_text:
                            para_text = para_text.replace(placeholder, value)

                    elif isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            if isinstance(sub_value, str):
                                placeholder = f"{{{{{sub_key}}}}}"
                                if placeholder in para_text:
                                    para_text = para_text.replace(placeholder, sub_value)
                
                # Update paragraph runs to reflect changes
                if para.text != para_text:
                    # Remove all existing runs
                    while para.runs:
                        para._element.remove(para.runs[0]._element)

                    # Add new run with replaced text
                    para.add_run(para_text)

            # Handle lists (like SKILLS_LIST, CERTIFICATIONS_LIST)
            list_fields = {
                "{{skills_list}}": self.user_data.get("skills", []),
                "{{certifications_list}}": self.user_data.get("certifications", []),
                "{{achievements}}": self.user_data.get("experience", {}).get("achievements", []),
            }

            for anchor, items in list_fields.items():
                if isinstance(items, list):
                    self._insert_bullets(doc, anchor, items)

            # Return in-memory file object
            output_stream = BytesIO()
            doc.save(output_stream)
            # doc.save(self.output_path)
            output_stream.seek(0)

            # Save to disk or cloud (example: local file system)
            save_path = os.path.join('generated_docs', self.filename)
            with open(save_path, 'wb') as f:
                f.write(output_stream.read())
            return self.filename
        except Exception as e:
            print("Error populating template:", e)
            return ''
