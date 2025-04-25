from celery import shared_task
import time
from .utils import extract_text, calculate_ats_score

@shared_task
def mock_heavy_parsing(file_data, filename):
    """Simulate slow processing (e.g., OCR, AI enhancements)"""
    time.sleep(10)  # Simulate 10s delay
    return {
        'filename': filename,
        'processed': True,
        'mock_data': 'This would be parsed text in reality'
    }

@shared_task
def async_extract_and_score(file_bytes, filename):
    text = extract_text(file_bytes, filename)
    return {
        'text': text,
        'ats_score': calculate_ats_score(text)
    }