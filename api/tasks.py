from celery import shared_task
import time
from .utils import *
from .file_generator import ResumeGenerator

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
def async_generate_resume(resume_data: dict = {}, filename: str = ''):
    """Simulate resume generation"""
    generator = ResumeGenerator(resume_data, filename)
    file_name = generator.populate_template()
    return file_name
