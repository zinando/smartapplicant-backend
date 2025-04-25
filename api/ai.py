import google.generativeai as genai
from dotenv import load_dotenv
import os
import requests
import json

# Load environment variables
load_dotenv()

context = {}

# Initialize Generative AI API
genai.configure(api_key=os.getenv("GEMENAI-API-KEY"))
gen_model = genai.GenerativeModel("gemini-1.5-flash")

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

    prompt = get_context(user_id)
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
        save_context(text, response, user_id)
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