from celery import shared_task
import time
from .utils import *
from .file_generator import ResumeGenerator
from .suggestion_utils import get_title_suggestions_from_gemini, get_skill_suggestion_from_gemini

@shared_task
def mock_heavy_parsing(file_data, filename):
    """Simulate slow processing (e.g., OCR, AI enhancements)"""
    time.sleep(10)  # Simulate 10s delay
    return {
        'filename': filename,
        'processed': True,
        'mock_data': 'This would be parsed text in reality'
    }

def async_extract_and_score(file_data, filename):
    """Simulate slow processing (e.g., OCR, AI enhancements)"""
    time.sleep(10)  # Simulate 10s delay
    return {
        'filename': filename,
        'processed': True,
        'mock_data': 'This would be parsed text in reality'
    }

@shared_task
def async_match_resume_with_jd(resume_text, job_description, user, job_title):
    """Simulate matching resume with job description"""
    analysis_result = match_resume_with_jd(resume_text, job_description, user, job_title)

    return analysis_result

@shared_task
def async_generate_resume(resume_data: dict = {}, filename: str = '', user_id=0):
    """Simulate resume generation"""
    generator = ResumeGenerator(resume_data, filename, matching=False, user_id=user_id)
    file_name = generator.populate_template()
    return file_name

@shared_task
def async_generate_matching_resume(resume_data: dict = {}, filename: str = '', user_id=0):
    """Simulate resume generation"""
    generator = ResumeGenerator(resume_data, filename, matching=True, user_id=user_id)
    file_name = generator.populate_matching_template(resume_data['template_id'])
    return file_name

@shared_task
def async_process_new_jt_suggestion(new_title: str):
    """Populate job titles in the database"""
    suggestions, skills = get_title_suggestions_from_gemini(new_title)
    return {
        'responsibilities': suggestions,
        'skills': skills
    }

@shared_task
def async_process_new_skill_suggestion(new_skill: str, job_title: str):
    """Populate skills in the database"""
    suggestions, skills = get_skill_suggestion_from_gemini(new_skill, job_title)
    return {
        'responsibilities': suggestions,
        'skills': skills
    }