from pydantic import BaseModel, ValidationError
from typing import List

class Experience(BaseModel):
    job_title: str
    company: str
    start_date: str
    end_date: str
    responsibilities: List[str]

class Education(BaseModel):
    degree: str
    school: str
    start_date: str
    end_date: str

class Resume(BaseModel):
    name: str
    email: str
    phone: str
    summary: str
    skills: List[str]
    experience: List[Experience]
    education: List[Education]

def validate_resume(data: dict) -> Resume:
    try:
        return Resume(**data)
    except ValidationError as e:
        print("⚠️ Resume data failed validation:", e)
        return None
