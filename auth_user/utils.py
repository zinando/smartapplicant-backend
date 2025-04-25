from api.models import GeneralData
from api.resources import technical_keywords
from api.utils import calculate_keyword_coverage, match_job_field
from api.ai import get_basic_improvement_suggestion

def get_suggestions_for_resume(parsed_data: dict, kw_data: dict):
    """Returns suggestions for improving the resume based on parsed data and keywords."""
    # Calculate metadata score (0-100)
    meta_fields = ['name', 'email', 'phone']
    meta_score = int(sum(1 for field in meta_fields if parsed_data.get(field)) / len(meta_fields) * 100)
    
    # Calculate experience score (check both existence and content)
    experience_score = 100 if parsed_data.get('experience') else 0
    
    # Calculate skill match score (0-100)
    skill_score = 0
    if kw_data:  # Prevent division by zero
        skill_score = int(sum(kw_data.values()) / len(kw_data))
    
    # Calculate certification score
    certification_score = 100 if parsed_data.get('certificates') else 0
    
    # Calculate education score (placeholder - implement your logic)
    education_score = 100 if parsed_data.get('education') else 0
    
    metrics = {
        'metadata': meta_score,
        'education': education_score,
        'skills': skill_score,
        'experience': experience_score,
        'certifications': certification_score
    }
    print(metrics)
    return get_basic_improvement_suggestion(metrics)

def compare_ats_score(resume_score):
    """This function compares the ATS score of the resume with that of other user's resumes."""
    # update general stat data
    gen_obj, created = GeneralData.objects.get_or_create(
        id = 1,
        defaults= {
            "ats_score": [resume_score],
            "premium_users": 0,
            "registered_users": 1,
            "currently_online": 0
        }
    )
    score = 100
    ats_scores = set()
    if not created:
        # check if ats score is empty
        if gen_obj.ats_score:
            ats_scores = set(gen_obj.ats_score.copy())
            lower_scores = [x for x in ats_scores if x < resume_score]
            if not lower_scores:
                score = 0
            else:
                score = int(len(lower_scores)/len(ats_scores)*100)
    ats_scores.add(resume_score)
    gen_obj.ats_score = list(ats_scores)
    gen_obj.save()
    return score

def get_keyword_coverage(resume_text, job_title=''):
    """This function takes a resume text and a job description and returns the keyword coverage of the resume."""

    field_matcher = match_job_field(job_title, technical_keywords)
    kw_data = calculate_keyword_coverage(resume_text, field_matcher['expected_keywords'])
    return kw_data

def get_resume_score_rating(ats_score):
    """This function takes an ATS score and returns a rating based on the score."""
    if ats_score >= 90:
        return "Excellent"
    elif ats_score >= 75:
        return "Good"
    elif ats_score >= 50:
        return "Average"
    else:
        return "Poor"

def add_user_resume_data(user, resume_data):
    """This function takes a user and resume data and adds the resume data to the user's profile."""
    try:
        # Check if user resume data is null or empty
        if not user.resume_data:
            resume_data['id'] = 1
            user.resume_data = [resume_data]
            user.save()
            return True
        # Check if resume data already exists
        for data in user.resume_data:
            if 'id' in resume_data and data['id'] == resume_data['id']:
                return False
        # Add new resume data
        resume_data['id'] = len(user.resume_data) + 1
        user.resume_data.append(resume_data)
        user.save()
        return True

    except Exception as e:
        print(f"Error adding resume data: {e}")
        return False
    
def update_user_resume_data_id(user):
    """This function takes a user and assigns a new id to all the resume data."""
    if not user.resume_data:
        user.resume_data = None
        user.save()
        
    else:
        for i, data in enumerate(user.resume_data):
            data['id'] = i + 1
        user.save()
    