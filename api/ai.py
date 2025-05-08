from dotenv import load_dotenv
import os
import json
import requests

# Load environment variables
load_dotenv()

# context = {}

def call_gemini(prompt: str) -> str:
    """Call Gemini API directly using requests and return the model's response."""
    api_key = os.getenv("GEMENAI_API_KEY")
    if not api_key:
        raise ValueError("GEMENAI_API_KEY not set in environment variables.")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    headers = {
        "Content-Type": "application/json",
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()  # Raise error for 4xx/5xx responses
        data = response.json()

        return data['candidates'][0]['content']['parts'][0]['text']
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return ""
    except (KeyError, IndexError) as parse_err:
        print(f"Error parsing Gemini response: {parse_err}")
        print(response.text)
        return ""

def save_context(text, response, user_id):
    mr ={}
    mr['User'] = text
    mr['Response'] = response
    context[user_id] = mr

    # save context to a file as json
    with open('context.json', 'w') as f:
        f.write(json.dumps(context))

def get_context(user_id):
    # read context from a file
    # if the file does not exist, return an empty string
    try:
        with open('context.json', 'r') as f:
            data = json.loads(f.read())
            context = data[user_id]
    except:
        return ''
    prompt = ''
    for convo in context:
        prompt += f"I said this: {convo['User']}\nAnd you responded with this: {convo['Response']}\n\n"
    return prompt


def get_improvement_suggestions(resume_text:str, user_id:int, job_description:str=''):
    """This method will route resume text and jd to ai and seek ai suggestions on how to improve the resume."""
    starter = "I want you to send me structured response ONLY because this is automated."
    starter += "separate your responses for each point with a semicolon (;)."
    starter += "Remember to be very brief, professional, but hitting the most relevant points."

    prompt = '' # get_context(user_id)
    prompt = prompt.replace(job_description, 'JD')
    prompt = prompt.replace(resume_text, 'RESUME')
    text = prompt

    text += 'Analyze my resume versus the job i want to apply for.\n'
    text += 'Give me structured advice on how to improve my resume versus the job description\n'
    text += 'Let your analysis center on the following topics requirements: Education, Skills, Certifications, Personal Information, and Experience.\n'
    text += 'Be silent where my resume feels strong. Point out missing specific requirement items and how i should add them to my resume.\n\n'
    text += 'My Resume:\n'
    text += resume_text + '\n\n'
    text += 'Job Description:\n'
    text += job_description + '\n\n'
    text += starter

    response = ''

    try:
        formatted_text = prompt + f'Let\'s continue from here: \n{text}'
        query = gen_model.generate_content(formatted_text)
        response = query.text
        #save_context(text, response, user_id)
    except Exception as e:
        print(e)
    #print(f'AI RESPONSE: {response}')
    return response

def get_basic_improvement_suggestion(analysis_result:dict):
    """This method uses the analysis result to provide improvement solution, referencing AI help when necessary."""
    # Map each key in the analysis result to how that point is analyzed
    how_it_works = {
        "metadata": "Here the app expects to extract at least three common personal information: name, phone number, and email. The scoring is based on the number of these three the app is able to extract, expressed as a percentage.",
        "skills": "",
        "education": "The app expects to extract a diploma or a bachelors education info from the resume. Diploma gives 50% while bachelors give 100%.",
        "experience": "The app expects to get at least 3 years experience information. The score is expressed as a percentage of number of experience versus 3 years if not over 3 years.",
        "certifications": "The app expects to find at least one education certification (Diploma, bachelor, etc) and any non-school certification (OSHA, etc)"
    }

    suggestions = {
        "education": 
                    """
                    Add a 'Education' section with degrees (e.g., 'B.Sc Computer Science'). Use standard abbreviations (B.Sc, M.Sc, PhD).
                    Format as: 'University Name – Location – YYYY-YYYY'. Avoid bullets or icons in this section.
                    Include dates for each degree (e.g., '2015-2019'). Use full years or 'Present' if ongoing.
                    Specify fields (e.g., 'B.Sc in Data Science'). Align with job description keywords.
                    """,
        "metadata": 
                    """
                    Add a professional email (e.g., name@gmail.com) in the header. Avoid unformatted or placeholder emails.
                    Include a phone number with country code (e.g., +1 123-456-7890). Place it near your email.
                    Ensure your full name is the first line of your resume. Avoid nicknames or icons interfering with text.
                    Add your city/country (e.g., 'San Francisco, CA'). Use standard abbreviations for states/countries.
                    """,
        "skills": 
                    """
                    Create a dedicated 'Skills' section. List 6-12 key skills in bullet points (e.g., 'Python, SQL, AWS').
                    Replace generic terms (e.g., 'Microsoft Office') with specific tools (e.g., 'Excel VLOOKUP, PowerPoint').
                    Move technical skills higher in your resume. Group them by type (e.g., 'Programming: Python, R, Java').
                    Add 3-5 keywords from the job description (e.g., 'Tableau' if listed in requirements).
                    Use commas or bullets to separate skills. Avoid icons, tables, or images for critical skills.
                    """,
        "certifications": 
                    """
                    Add a 'Certifications' section. Format as: 'AWS Certified Cloud Practitioner (AWS) - 2023'.
                    Include issuing organization and year (e.g., 'Google Data Analytics Certificate (Google) - 2024').
                    Move certifications to a dedicated section. Avoid mixing with education/experience.
                    Use consistent formatting: 'Cert Name (Issuer) - Year'. Avoid bullets/icons in this section.
                    Remove expired certifications unless highly relevant. Add 'In Progress' for current studies.
                    """,
        "experience": 
                    """
                    Add a professional summary and summarize your total experience in it (e.g., '5+ years experience as a Software Developer').
                    Format employment dates clearly: 'Jan 2020 - Present' or 'Mar 2018 - Dec 2022' for each role.
                    Specify level in your summary (e.g., 'Senior Product Manager with 8+ years experience').
                    Label contract roles clearly and include total duration (e.g., '2-year contract at Google').
                    Briefly note gaps (e.g., 'Career break: 2020-2021'). Use years (not months) for clarity.
                    """,
    }

    suggestion_list = []

    for point, score in analysis_result.items():
        if score < 100:
            suggestion_list.append(suggestions[point])
    
    return suggestion_list

def match_resume_to_jd_with_ai(resume_text:str, job_description:str):
    """This method will route resume text and jd to ai and seek structured response on how the resume matches the jd."""
    prompt = """
    I want you to analyze my resume and the job description I want to apply for.
    I want you to grade various sections of the resume against the job details. Follow the format below.

    {
        "keyword_coverage": {
             "Technical Skills": rate how well the resume uses technical skills, esp with resp to the jd. from 1 to 100, integer only,
             "Tools and Concepts": rate how well the resume uses tools and concepts, esp with resp to the jd. from 1 to 100, integer only,
             "Soft Skills": rate how well the resume uses soft skills, esp with resp to the jd. from 1 to 100, integer only,
            "Experience Level": rate the experience level in the resume vs the required in the jd. resume/jd. whole number. if no exoerience is required, give 100%, if experience is required but non provided, give 0,
            "Education Requirements": rate the education level in the resume vs the required in the jd. e.g if required is BSc but resume has HND, gvive 50. if HND/BSc is required but resume has OND/associate, give zero. If required is BSc in Law but resume has BSc in Engineering, give zero. whole number. if no education is required, give 100%, if education is required but non provided, give 0,            
        },
        "sectional_matching": {
            "skills": {
                "match_percentage": how many percent of the skills in the job description are present in the resume,
                "matched": an array of skills that are present in both the resume and the job description,
                "missing": an array of skills that are present in the job description but not in the resume
            },
            "education": {
                "match_percentage": please give zero if the education is not relevant to the job requirement, i.e if the field is not related to required fields. How many percent of the education requirements in the job description are present in the resume. If resume has the target degree, give 100%,
                "matched": an array of education items that are present in both the resume and the job description,
                "missing": an array of education items that are present in the job description but not in the resume
            },
            "experience": {
                "match_percentage": quantify the years of experience in the resume against the required years of experience in the job description. If no experience is required, give 100%, 
                "matched": an array of experience items that are present resume,
                "missing": an array of experience items that are present in the job description but not in the resume
            },
            "certifications": {
                "match_percentage": how many percent of the certifications in the job description are present in the resume, IF NO CERTIFICATION IS REQUIRED, give 100%,
                "matched": an array of certifications that are present in both the resume and the job description,
                "missing": an array of certifications that are present in the job description but not in the resume
            }
        },
    
        "suggestions": [
        For each of the above sections, if the score is below 100%, give PRACTICAL suggestions on how i can improve on it. Separate each section suggestion with a comma.
        ],
        suitability_score: give an average score based on all the sections above.
    }

    I want your response to come in JSON format. Please DO NOT INCLUDE TRIPLE BACKTICKS in your response. Because i will parse the response as is with son.loads function.
    I want you to be very brief and professional.
    Return empty string if no resume or jd is provided.
    
    
    """
    prompt += "My Resume:\n"
    prompt += f"{resume_text}\n"

    prompt += "Job Description:\n"
    prompt += f"{job_description}"
 
    response = ''

    try:
        text = call_gemini(prompt)
        text = text.replace('```json', '')
        text = text.replace('```', '')
        response = json.loads(text)
    except Exception as e:
        response = ''
    
    return response