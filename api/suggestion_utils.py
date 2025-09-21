from django.db import transaction
from .models import JobTitle, Skill, Responsibility
# from .utils import normalize_title
from .ai import get_structured_data_from_gemini
from .serializers import JobTitleSerializer

@transaction.atomic
def add_new_job_title_record(title: str, field_group: str, responsibilities: list, skills: list):
    """
    Add a new JobTitle with responsibilities and skills.
    Responsibilities/skills come as list of dicts:
      {"text": "...", "job_ids": [1, 2, 3]}
    """
    title = title.strip()
    job, created = JobTitle.objects.get_or_create(
        title__iexact=title,
        defaults={"title": title, "field_group": field_group or "Other"}
    )

    summary = {
        "created_job": created,
        "responsibilities_linked": [],
        "skills_linked": []
    }

    # --- Responsibilities ---
    for item in responsibilities:
        r_text = item.get("text", "").strip()
        job_ids = item.get("job_ids", [])
        if not r_text:
            continue

        resp, _ = Responsibility.objects.get_or_create(
            text__iexact=r_text, defaults={"text": r_text}
        )
        # Link to new job
        job.responsibilities.add(resp)
        # Link to other provided job IDs
        if job_ids:
            resp.jobtitle_set.add(*JobTitle.objects.filter(id__in=job_ids))
        summary["responsibilities_linked"].append(r_text)

    # --- Skills ---
    for item in skills:
        s_name = item.get("name", "").strip()
        job_ids = item.get("job_ids", [])
        if not s_name:
            continue

        skill, _ = Skill.objects.get_or_create(
            name__iexact=s_name, defaults={"name": s_name}
        )
        # Link to new job
        job.skills.add(skill)
        # Link to other provided job IDs
        if job_ids:
            skill.jobtitle_set.add(*JobTitle.objects.filter(id__in=job_ids))
        summary["skills_linked"].append(s_name)

    return job, summary


JF = {
	"Technology & Engineering":[
				"Software Engineer","Backend Developer","Frontend Developer","Full Stack Developer","Mobile App Developer","iOS Developer", 
				"Android Developer", "DevOps Engineer","Cloud Engineer","Data Engineer","Machine Learning Engineer","AI Research Scientist", "Database Administrator","Systems Administrator","Network Engineer","Cybersecurity Analyst","Information Security Engineer","QA Engineer", "Automation Engineer","Site Reliability Engineer","Solutions Architect","Embedded Systems Engineer","Hardware Engineer","Electrical Engineer","Electronics Engineer","Mechanical Engineer","Civil Engineer","Chemical Engineer","Biomedical Engineer","Industrial Engineer", "Robotics Engineer","Control Systems Engineer","Structural Engineer","Environmental Engineer","Petroleum Engineer","Mining Engineer","Aerospace Engineer","Marine Engineer","Telecommunications Engineer","Technical Support Specialist"
			],
	"Creative & Design":[
				"Graphic Designer", "UI/UX Designer", "Product Designer", "Visual Designer", "Web Designer", 
				"Interior Designer", "Fashion Designer", "Industrial Designer", "Game Designer", "Animator", 
				"3D Modeler", "Illustrator", "Art Director", "Creative Director", "Brand Designer", 
				"Exhibition Designer", "Jewelry Designer", "Set Designer", "Package Designer", 
				"Motion Graphics Designer", "Storyboard Artist", "Concept Artist", "Multimedia Artist", 
				"Textile Designer", "Furniture Designer", "Landscape Designer", "Sound Designer", 
				"Lighting Designer", "Architectural Designer", "Digital Painter", "Handcraft Artist", 
				"Photographer", "Videographer", "Film Editor", "Copywriter", "Creative Writer", 
				"Content Designer", "Typography Designer", "Print Designer", "Logo Designer"
			],
	"Business & Finance": [
				"Accountant", "Auditor", "Financial Analyst", "Investment Analyst", "Credit Analyst",
				"Budget Analyst", "Tax Consultant", "Payroll Specialist", "Bookkeeper", "Chief Financial Officer (CFO)",
				"Financial Planner", "Treasurer", "Risk Manager", "Compliance Officer", "Actuary",
				"Loan Officer", "Bank Teller", "Mortgage Advisor", "Financial Controller", "Cost Estimator",
				"Business Analyst", "Management Consultant", "Strategy Consultant", "Operations Analyst", "Procurement Specialist",
				"Project Manager", "Contract Manager", "Sales Analyst", "Revenue Manager", "Pricing Analyst",
				"Investor Relations Specialist", "Insurance Underwriter", "Insurance Broker", "Hedge Fund Manager", "Venture Capital Analyst",
				"Private Equity Analyst", "Treasury Analyst", "Corporate Development Manager", "Business Development Manager", "Entrepreneur"
			],
	"Healthcare & Medical": [
				"General Practitioner (GP)", "Surgeon", "Pediatrician", "Oncologist", "Cardiologist",
				"Neurologist", "Dermatologist", "Psychiatrist", "Radiologist", "Anesthesiologist",
				"Obstetrician/Gynecologist (OB/GYN)", "Endocrinologist", "Nephrologist", "Orthopedic Surgeon", "Pathologist",
				"Emergency Medicine Physician", "Dentist", "Dental Hygienist", "Pharmacist", "Pharmacy Technician",
				"Registered Nurse (RN)", "Licensed Practical Nurse (LPN)", "Nurse Practitioner", "Midwife", "Physician Assistant",
				"Occupational Therapist", "Physical Therapist", "Respiratory Therapist", "Speech-Language Pathologist", "Radiology Technician",
				"Medical Laboratory Technician", "Medical Assistant", "Surgical Technologist", "Paramedic", "Home Health Aide",
				"Caregiver", "Nutritionist", "Dietitian", "Clinical Psychologist", "Mental Health Counselor"
			],
	"Education & Training": [
				"Primary School Teacher", "Secondary School Teacher", "Special Education Teacher", "Preschool Teacher", "Kindergarten Teacher",
				"College Professor", "University Lecturer", "Adjunct Professor", "Teaching Assistant", "Substitute Teacher",
				"Curriculum Developer", "Instructional Designer", "Education Administrator", "School Principal", "Vice Principal",
				"Academic Advisor", "Guidance Counselor", "Career Counselor", "Corporate Trainer", "Technical Trainer",
				"Online Course Instructor", "E-learning Specialist", "Education Consultant", "Tutor", "Private Language Teacher",
				"Teacher Aide", "Education Policy Analyst", "Educational Psychologist", "Adult Education Instructor", "Literacy Coach",
				"Library Media Specialist", "Teacher Mentor", "Instructional Coordinator", "Vocational Education Teacher", "Workshop Facilitator",
				"After-School Program Coordinator", "Early Childhood Educator", "Education Researcher", "STEM Instructor", "Training Manager"
			],
	"Legal & Government": [
				"Lawyer", "Attorney", "Corporate Counsel", "Public Defender", "Prosecutor",
				"Judge", "Magistrate", "Paralegal", "Legal Assistant", "Legal Secretary",
				"Compliance Officer", "Contract Manager", "Arbitrator", "Mediator", "Notary Public",
				"Policy Analyst", "Legislative Aide", "Legislator", "Senator", "Member of Parliament",
				"Governor", "Mayor", "City Councilor", "Government Affairs Specialist", "Political Advisor",
				"Intelligence Analyst", "Immigration Officer", "Customs Officer", "Tax Inspector", "Licensing Officer",
				"Social Benefits Officer", "Regulatory Affairs Specialist", "Diplomat", "Foreign Service Officer", "Consular Officer",
				"Election Officer", "Court Clerk", "Bailiff", "Police Inspector", "Detective"
			],
	"Science & Research": [
				"Research Scientist", "Laboratory Technician", "Biologist", "Microbiologist", "Geneticist",
				"Chemist", "Biochemist", "Physicist", "Astronomer", "Astrophysicist",
				"Geologist", "Geophysicist", "Meteorologist", "Oceanographer", "Ecologist",
				"Environmental Scientist", "Climate Scientist", "Hydrologist", "Toxicologist", "Pharmacologist",
				"Data Scientist", "Bioinformatician", "Epidemiologist", "Public Health Researcher", "Clinical Research Associate",
				"Research Assistant", "Research Fellow", "Anthropologist", "Archaeologist", "Sociologist",
				"Psychologist (Research)", "Political Scientist", "Economist", "Statistician", "Mathematician",
				"Operations Research Analyst", "Food Scientist", "Materials Scientist", "Nanotechnologist", "Robotics Researcher"
			],
	"Sales & Marketing": [
				"Sales Representative", "Account Executive", "Business Development Manager", "Territory Sales Manager", "Regional Sales Manager",
				"Inside Sales Representative", "Outside Sales Representative", "Key Account Manager", "Channel Sales Manager", "Enterprise Sales Executive",
				"Sales Operations Specialist", "Sales Consultant", "Sales Engineer", "Customer Success Manager", "Retail Sales Associate",
				"Sales Supervisor", "Sales Director", "Vice President of Sales", "Head of Sales", "Sales Administrator",
				"Marketing Manager", "Digital Marketing Specialist", "Content Marketing Manager", "SEO Specialist", "SEM Specialist",
				"Email Marketing Specialist", "Social Media Manager", "Brand Manager", "Product Marketing Manager", "Marketing Coordinator",
				"Marketing Analyst", "Growth Marketing Manager", "Advertising Manager", "Media Planner", "Public Relations Specialist",
				"Event Marketing Manager", "Affiliate Marketing Manager", "Partnerships Manager", "Field Marketing Manager", "Influencer Marketing Specialist"
			],
	"Skilled Trades & Technical Services": [
				"Electrician", "Plumber", "Carpenter", "Welder", "Machinist",
				"HVAC Technician", "Automotive Mechanic", "Aircraft Mechanic", "Elevator Technician", "Locksmith",
				"Boilermaker", "Pipefitter", "Sheet Metal Worker", "Roofer", "Glazier",
				"Insulation Installer", "Heavy Equipment Operator", "Diesel Mechanic", "Motorcycle Mechanic", "Industrial Maintenance Technician",
				"Millwright", "Control Systems Technician", "Instrumentation Technician", "Textile Technician", "Printing Technician",
				"Tool and Die Maker", "Furniture Maker", "Cabinet Maker", "Jeweler", "Watch Repairer",
				"Musical Instrument Repairer", "Sign Maker", "Stone Mason", "Bricklayer", "Concrete Finisher",
				"Scaffolder", "Blacksmith", "Gunsmith", "Fabricator", "Upholsterer"
			],
	"Media & Communications": [
				"Journalist", "News Anchor", "Radio Host", "Television Presenter", "Reporter",
				"Editor", "Copywriter", "Content Writer", "Technical Writer", "Grant Writer",
				"Public Relations Specialist", "Communications Officer", "Corporate Spokesperson", "Speechwriter", "Media Planner",
				"Advertising Copywriter", "Broadcast Technician", "Camera Operator", "Video Editor", "Film Director",
				"Producer", "Screenwriter", "Podcaster", "Social Media Manager", "Digital Content Creator",
				"Community Manager", "Influencer Marketing Specialist", "Brand Strategist", "Media Buyer", "Photojournalist",
				"Photographer", "Videographer", "Animator", "Motion Graphics Designer", "Sound Engineer",
				"Voice-over Artist", "Event Announcer", "Media Relations Specialist", "Publishing Editor", "Columnist"
			],
	"Hospitality & Tourism": [
				"Hotel Manager", "Resort Manager", "Front Desk Agent", "Concierge", "Guest Relations Manager",
				"Housekeeping Supervisor", "Event Planner", "Wedding Coordinator", "Conference Services Manager", "Travel Agent",
				"Tour Guide", "Adventure Tour Leader", "Cruise Director", "Flight Attendant", "Airline Customer Service Agent",
				"Restaurant Manager", "Executive Chef", "Sous Chef", "Pastry Chef", "Caterer",
				"Food and Beverage Manager", "Bartender", "Sommelier", "Banquet Server", "Barista",
				"Casino Dealer", "Casino Host", "Theme Park Manager", "Recreation Coordinator", "Spa Manager",
				"Wellness Retreat Coordinator", "Tourism Development Officer", "Destination Marketing Manager", "Hospitality Trainer", "Front Office Supervisor",
				"Reservations Agent", "Ticketing Agent", "Travel Consultant", "Sustainable Tourism Specialist", "Luxury Travel Advisor"
			],
	"Transportation & Logistics": [
				"Logistics Manager", "Supply Chain Analyst", "Freight Forwarder", "Customs Broker", "Warehouse Manager",
				"Inventory Controller", "Procurement Specialist", "Distribution Manager", "Fleet Manager", "Operations Planner",
				"Transportation Coordinator", "Dispatch Supervisor", "Route Planner", "Logistics Coordinator", "Port Operations Manager",
				"Air Cargo Agent", "Shipping Coordinator", "Rail Operations Manager", "Truck Driver", "Bus Driver",
				"Delivery Driver", "Courier", "Forklift Operator", "Crane Operator", "Material Handler",
				"Supply Chain Manager", "Import/Export Specialist", "Maritime Logistics Coordinator", "Aviation Logistics Specialist", "Cargo Handler",
				"Warehouse Associate", "Inventory Clerk", "Freight Dispatcher", "Supply Planner", "Distribution Center Supervisor",
				"Last Mile Delivery Specialist", "E-commerce Fulfillment Specialist", "Logistics Analyst", "Transport Safety Officer", "Logistics Engineer"
			],
	"Construction & Real Estate": [
				"Construction Manager", "Project Manager", "Site Supervisor", "Civil Engineer", "Structural Engineer",
				"Quantity Surveyor", "Building Inspector", "Architect", "Landscape Architect", "Urban Planner",
				"Real Estate Agent", "Real Estate Broker", "Property Manager", "Leasing Consultant", "Real Estate Analyst",
				"Facilities Manager", "Estimator", "Health and Safety Officer", "Building Services Engineer", "Foreman",
				"Construction Laborer", "Mason", "Carpenter", "Electrician", "Plumber",
				"Roofer", "Glazier", "Painter and Decorator", "Tiler", "Concrete Worker",
				"Heavy Equipment Operator", "Surveyor", "Drafter", "Interior Designer", "Real Estate Developer",
				"Mortgage Broker", "Real Estate Appraiser", "Housing Officer", "Site Planner", "Project Architect"
			],
	"Agriculture & Environment": [
				"Agricultural Scientist", "Agronomist", "Soil Scientist", "Horticulturist", "Viticulturist",
				"Forester", "Conservation Scientist", "Environmental Scientist", "Ecologist", "Wildlife Biologist",
				"Fisheries Scientist", "Aquaculture Specialist", "Marine Biologist", "Sustainability Specialist", "Climate Analyst",
				"Environmental Engineer", "Water Resource Specialist", "Irrigation Engineer", "Agricultural Engineer", "Farm Manager",
				"Crop Farmer", "Dairy Farmer", "Poultry Farmer", "Livestock Farmer", "Organic Farmer",
				"Beekeeper", "Rancher", "Agricultural Technician", "Greenhouse Manager", "Soil Conservationist",
				"Environmental Consultant", "Recycling Coordinator", "Waste Management Specialist", "Renewable Energy Technician", "Environmental Health Officer",
				"Tree Surgeon (Arborist)", "Park Ranger", "Hydrologist", "Natural Resource Manager", "Sustainability Consultant"
			],
	"Human Resources & Administration": [
				"Human Resources Manager", "HR Business Partner", "HR Generalist", "HR Specialist", "HR Coordinator",
				"HR Administrator", "Recruiter", "Talent Acquisition Specialist", "Head of Talent", "Campus Recruiter",
				"Compensation and Benefits Manager", "Payroll Specialist", "Employee Relations Specialist", "Labor Relations Specialist", "Training and Development Manager",
				"Learning and Development Specialist", "Organizational Development Specialist", "Diversity and Inclusion Manager", "Workforce Planning Analyst", "HRIS Specialist",
				"Office Administrator", "Administrative Assistant", "Executive Assistant", "Personal Assistant", "Office Manager",
				"Front Desk Receptionist", "Clerical Officer", "Records Management Officer", "Data Entry Clerk", "Administrative Coordinator",
				"Program Administrator", "Operations Administrator", "Facilities Coordinator", "Virtual Assistant", "Scheduling Coordinator",
				"Compliance Administrator", "Contract Administrator", "Procurement Administrator", "Business Support Officer", "Administrative Services Manager"
			],
	"Security & Protective Services": [
				"Security Guard", "Security Officer", "Corporate Security Specialist", "Loss Prevention Officer", "Surveillance Officer",
				"Police Officer", "Detective", "Criminal Investigator", "Traffic Police Officer", "Border Patrol Agent",
				"Corrections Officer", "Prison Guard", "Probation Officer", "Parole Officer", "Customs Inspector",
				"Immigration Officer", "Firefighter", "Fire Inspector", "Fire Investigator", "Emergency Management Specialist",
				"Private Investigator", "Bodyguard", "Personal Protection Officer", "Event Security Officer", "Campus Security Officer",
				"Security Systems Technician", "Alarm Monitoring Specialist", "Fraud Investigator", "Forensic Analyst", "Cybercrime Investigator",
				"K9 Handler", "Military Police Officer", "Coast Guard Officer", "Disaster Response Specialist", "Rescue Diver",
				"Airport Security Screener", "Transportation Security Officer", "Nuclear Security Officer", "Critical Infrastructure Protection Specialist", "Security Operations Manager"
			],
	"Social & Community Services": [
				"Social Worker", "Community Service Worker", "Case Manager", "Family Support Worker", "Child Protection Officer",
				"School Social Worker", "Substance Abuse Counselor", "Rehabilitation Counselor", "Crisis Intervention Specialist", "Homeless Shelter Worker",
				"Probation and Parole Officer", "Youth Worker", "Disability Support Worker", "Mental Health Support Worker", "Community Outreach Coordinator",
				"Volunteer Coordinator", "Program Coordinator", "Nonprofit Program Manager", "Community Development Officer", "Advocacy Specialist",
				"Elderly Care Coordinator", "Housing Support Specialist", "Refugee Support Worker", "Immigration Services Officer", "Public Health Social Worker",
				"Domestic Violence Advocate", "Victim Support Specialist", "Family Therapist", "Marriage Counselor", "Addiction Specialist",
				"Faith-based Community Worker", "Charity Worker", "NGO Field Officer", "Crisis Hotline Operator", "Human Services Assistant",
				"Occupational Therapist Assistant", "Youth Mentor", "Reentry Support Specialist", "Employment Counselor", "Life Coach"
			],
	"Retail & Customer Service": [
				"Retail Sales Associate", "Cashier", "Store Supervisor", "Assistant Store Manager", "Store Manager",
				"Retail Buyer", "Merchandiser", "Visual Merchandiser", "Inventory Clerk", "Stock Associate",
				"Customer Service Representative", "Call Center Agent", "Technical Support Representative", "Help Desk Specialist", "Client Relations Specialist",
				"Customer Success Manager", "Account Manager", "Key Account Specialist", "Front Desk Associate", "Guest Services Associate",
				"E-commerce Specialist", "Retail Operations Manager", "Sales Floor Associate", "Checkout Operator", "Personal Shopper",
				"Retail Consultant", "Fashion Sales Associate", "Electronics Sales Associate", "Pharmacy Sales Assistant", "Grocery Clerk",
				"Service Desk Agent", "Customer Support Analyst", "Client Support Specialist", "Reservations Agent", "Warranty Specialist",
				"Returns and Exchanges Clerk", "Customer Experience Manager", "Consumer Care Specialist", "POS System Operator", "Customer Loyalty Specialist"
			],
	"Arts, Culture & Entertainment": [
				"Actor", "Theater Performer", "Film Actor", "Stage Actor", "Voice Actor",
				"Musician", "Singer", "Songwriter", "Composer", "Conductor",
				"Dancer", "Choreographer", "Ballet Dancer", "Contemporary Dancer", "Dance Instructor",
				"Visual Artist", "Painter", "Sculptor", "Illustrator", "Muralist",
				"Photographer", "Cinematographer", "Videographer", "Film Director", "Film Producer",
				"Screenwriter", "Playwright", "Poet", "Author", "Novelist",
				"Art Curator", "Museum Curator", "Archivist", "Art Historian", "Cultural Anthropologist",
				"Fashion Designer", "Costume Designer", "Set Designer", "Lighting Designer", "Sound Designer"
			],
	"Other": [
				"Entrepreneur", "Startup Founder", "Business Owner", "Freelancer", "Consultant",
				"Research Assistant", "Project Coordinator", "Program Manager", "Operations Analyst", "Strategy Consultant",
				"Data Entry Operator", "Virtual Assistant", "Remote Worker", "Innovation Specialist", "Think Tank Researcher",
				"Policy Analyst", "Market Research Analyst", "Sustainability Officer", "Corporate Trainer", "Quality Assurance Specialist",
				"Technical Writer", "Grant Writer", "Patent Examiner", "Ethics Officer", "Compliance Officer",
				"Lobbyist", "Risk Manager", "Change Management Specialist", "Business Continuity Planner", "Knowledge Manager",
				"Product Manager", "Scrum Master", "Agile Coach", "E-learning Specialist", "Instructional Designer",
				"International Development Specialist", "Peacekeeping Officer", "Aid Worker", "Futurist", "General Laborer"
			]
}
def populate_job_titles():
    for field_group, titles in JF.items():
        for title in titles:
            try:
                JobTitle.objects.get_or_create(title=title, field_group=field_group)
            except Exception as e:
                print(f"Error creating job title '{title}': {e}")

datas = job_titles = job_titles = [
    {
        "jt": "General Practitioner (GP)",
        "field_group": "HealthCare & Medical",
        "skills": [
            "Patient Examination",
            "Diagnosis",
            "Treatment Planning",
            "Prescription Writing",
            "Preventive Medicine",
            "Chronic Disease Management",
            "Patient Education",
            "Basic Surgical Procedures",
            "Electronic Medical Records (EMR)",
            "Communication"
        ],
        "suggestions": [
            "Conducted patient consultations and physical examinations.",
            "Diagnosed and treated a wide range of medical conditions.",
            "Prescribed medications and monitored treatment outcomes.",
            "Referred patients to specialists when necessary.",
            "Provided preventive care and health education.",
            "Monitored chronic conditions such as diabetes and hypertension.",
            "Maintained accurate patient records in EMR systems.",
            "Performed minor surgical and medical procedures.",
            "Delivered comprehensive care for individuals and families.",
            "Collaborated with healthcare professionals to ensure continuity of care."
        ]
    },
    {
        "jt": "Surgeon",
        "field_group": "HealthCare & Medical",
        "skills": [
            "Surgical Procedures",
            "Preoperative Planning",
            "Postoperative Care",
            "Anatomy Knowledge",
            "Aseptic Techniques",
            "Surgical Instruments Handling",
            "Patient Assessment",
            "Critical Thinking",
            "Team Collaboration",
            "Decision-Making"
        ],
        "suggestions": [
            "Performed surgical operations to treat injuries and diseases.",
            "Assessed patients’ conditions and recommended surgical interventions.",
            "Planned and prepared for surgical procedures.",
            "Ensured sterile conditions and adherence to safety protocols.",
            "Collaborated with anesthesiologists and surgical teams.",
            "Monitored patients during surgery and adjusted techniques as needed.",
            "Provided postoperative care and monitored recovery progress.",
            "Educated patients and families about surgical risks and outcomes.",
            "Maintained detailed surgical and patient care records.",
            "Contributed to research and continuous medical education."
        ]
    },
    {
        "jt": "Pediatrician",
        "field_group": "HealthCare & Medical",
        "skills": [
            "Child Health Assessment",
            "Diagnosis",
            "Immunizations",
            "Growth Monitoring",
            "Chronic Illness Management",
            "Communication",
            "Patient Education",
            "Electronic Medical Records (EMR)",
            "Preventive Care",
            "Critical Thinking"
        ],
        "suggestions": [
            "Diagnosed and treated illnesses and injuries in children.",
            "Conducted routine health check-ups and growth assessments.",
            "Administered immunizations and preventive care.",
            "Provided treatment for chronic conditions in children.",
            "Educated parents on child health, nutrition, and development.",
            "Maintained accurate pediatric health records in EMR systems.",
            "Referred children to specialists when needed.",
            "Monitored developmental milestones and advised parents.",
            "Responded to emergencies in pediatric care.",
            "Collaborated with schools and community health programs."
        ]
    },
    {
        "jt": "Neurologist",
        "field_group": "HealthCare & Medical",
        "skills": [
            "Neurological Examination",
            "Neuroimaging Interpretation",
            "Electroencephalography (EEG)",
            "Diagnosis",
            "Treatment Planning",
            "Patient Care",
            "Critical Thinking",
            "Research",
            "Communication"
        ],
        "suggestions": [
            "Diagnosed and treated neurological disorders such as epilepsy and stroke.",
            "Conducted detailed neurological examinations.",
            "Interpreted MRI, CT scans, and EEG results.",
            "Developed treatment plans for neurological conditions.",
            "Provided patient education on neurological disorders.",
            "Referred patients for surgical or specialized care when necessary.",
            "Participated in neurological research and clinical studies.",
            "Monitored patients’ responses to treatments.",
            "Collaborated with multidisciplinary healthcare teams.",
            "Maintained detailed medical records of neurological cases."
        ]
    },
    {
        "jt": "Dermatologist",
        "field_group": "HealthCare & Medical",
        "skills": [
            "Skin Examination",
            "Dermatological Procedures",
            "Laser Therapy",
            "Cosmetic Dermatology",
            "Diagnosis",
            "Treatment Planning",
            "Patient Care",
            "Communication",
            "Preventive Medicine",
            "Record Keeping"
        ],
        "suggestions": [
            "Diagnosed and treated skin, hair, and nail disorders.",
            "Performed dermatological procedures such as biopsies and excisions.",
            "Administered laser therapy and cosmetic treatments.",
            "Educated patients on skin care and disease prevention.",
            "Prescribed medications for skin-related conditions.",
            "Provided treatment for chronic conditions like eczema and psoriasis.",
            "Documented patient cases and treatment outcomes.",
            "Collaborated with other healthcare providers for holistic care.",
            "Monitored patients for side effects of dermatological treatments.",
            "Participated in dermatology research and clinical advancements."
        ]
    },
    {
        "jt": "Psychiatrist",
        "field_group": "HealthCare & Medical",
        "skills": [
            "Mental Health Assessment",
            "Psychotherapy",
            "Medication Management",
            "Patient Counseling",
            "Crisis Intervention",
            "Diagnosis",
            "Treatment Planning",
            "Communication",
            "Record Keeping",
            "Team Collaboration"
        ],
        "suggestions": [
            "Diagnosed and treated mental health disorders.",
            "Conducted psychiatric evaluations and risk assessments.",
            "Prescribed and managed psychiatric medications.",
            "Provided psychotherapy and counseling sessions.",
            "Responded to mental health crises and emergencies.",
            "Collaborated with psychologists, nurses, and social workers.",
            "Educated patients and families on mental health management.",
            "Maintained confidential patient records and reports.",
            "Developed individualized treatment plans.",
            "Participated in community mental health programs."
        ]
    },
    {
        "jt": "Obstetrician/Gynecologist (OB/GYN)",
        "field_group": "HealthCare & Medical",
        "skills": [
            "Obstetric Care",
            "Gynecological Surgery",
            "Prenatal Care",
            "Labor and Delivery Management",
            "Diagnosis",
            "Reproductive Health",
            "Ultrasound Interpretation",
            "Patient Counseling",
            "Record Keeping",
            "Critical Thinking"
        ],
        "suggestions": [
            "Provided prenatal, labor, and postnatal care to patients.",
            "Performed gynecological surgeries and procedures.",
            "Diagnosed and treated reproductive health conditions.",
            "Assisted in safe deliveries and managed obstetric emergencies.",
            "Conducted ultrasound and diagnostic tests for pregnancy monitoring.",
            "Educated patients on family planning and reproductive health.",
            "Documented patient histories and treatment plans.",
            "Collaborated with nurses and midwives in patient care.",
            "Responded to obstetric and gynecological emergencies.",
            "Participated in maternal health awareness programs."
        ]
    },
    {
        "jt": "Dentist",
        "field_group": "HealthCare & Medical",
        "skills": [
            "Dental Examination",
            "Oral Surgery",
            "Restorative Dentistry",
            "Prosthodontics",
            "Endodontics",
            "Periodontics",
            "Radiology Interpretation",
            "Patient Education",
            "Record Keeping",
            "Team Collaboration"
        ],
        "suggestions": [
            "Performed dental examinations and diagnosed oral health issues.",
            "Conducted restorative procedures such as fillings and crowns.",
            "Performed oral surgeries including extractions.",
            "Educated patients on oral hygiene and preventive care.",
            "Provided treatment for gum diseases and dental infections.",
            "Interpreted dental X-rays and imaging reports.",
            "Designed treatment plans for dental restorations.",
            "Maintained accurate dental patient records.",
            "Collaborated with dental hygienists and assistants.",
            "Monitored patient progress after dental procedures."
        ]
    },
    {
        "jt": "Dental Hygienist",
        "field_group": "HealthCare & Medical",
        "skills": [
            "Oral Health Assessment",
            "Teeth Cleaning",
            "Preventive Dentistry",
            "Patient Education",
            "X-ray Imaging",
            "Infection Control",
            "Record Keeping",
            "Communication"
        ],
        "suggestions": [
            "Performed routine teeth cleaning and scaling procedures.",
            "Conducted oral health assessments and screenings.",
            "Took and processed dental X-rays.",
            "Educated patients on proper oral hygiene practices.",
            "Applied preventive treatments such as fluoride and sealants.",
            "Maintained infection control and sterilization standards.",
            "Documented patient dental records and procedures.",
            "Assisted dentists in complex dental procedures.",
            "Provided advice on nutrition and dental health.",
            "Promoted community dental health awareness."
        ]
    },
    {
        "jt": "Pharmacist",
        "field_group": "HealthCare & Medical",
        "skills": [
            "Pharmaceutical Knowledge",
            "Prescription Dispensing",
            "Drug Interactions",
            "Patient Counseling",
            "Inventory Management",
            "Regulatory Compliance",
            "Pharmacovigilance",
            "Communication",
            "Record Keeping",
            "Critical Thinking"
        ],
        "suggestions": [
            "Dispensed prescribed medications accurately and safely.",
            "Educated patients on proper medication usage and side effects.",
            "Reviewed prescriptions for potential drug interactions.",
            "Maintained pharmacy inventory and ordered supplies.",
            "Ensured compliance with pharmaceutical regulations.",
            "Monitored and reported adverse drug reactions.",
            "Collaborated with doctors and nurses on treatment plans.",
            "Maintained accurate pharmacy records and reports.",
            "Provided immunizations and preventive care services.",
            "Offered guidance on over-the-counter medications."
        ]
    },
    {
        "jt": "Registered Nurse (RN)",
        "field_group": "HealthCare & Medical",
        "skills": [
            "Patient Care",
            "Medication Administration",
            "IV Therapy",
            "Wound Care",
            "Patient Education",
            "Vital Signs Monitoring",
            "Electronic Medical Records (EMR)",
            "Team Collaboration",
            "Critical Thinking",
            "Compassion"
        ],
        "suggestions": [
            "Provided direct patient care in hospitals and clinics.",
            "Administered medications and intravenous therapies.",
            "Monitored patients’ vital signs and progress.",
            "Educated patients and families about health management.",
            "Assisted in medical procedures and emergency care.",
            "Maintained accurate nursing records in EMR systems.",
            "Collaborated with doctors and healthcare professionals.",
            "Performed wound care and dressing changes.",
            "Responded to patient emergencies promptly.",
            "Promoted preventive healthcare practices."
        ]
    },
    {
        "jt": "Licensed Practical Nurse (LPN)",
        "field_group": "HealthCare & Medical",
        "skills": [
            "Basic Patient Care",
            "Medication Administration",
            "Vital Signs Monitoring",
            "Wound Care",
            "Patient Education",
            "Infection Control",
            "Record Keeping",
            "Compassion",
            "Communication"
        ],
        "suggestions": [
            "Assisted patients with daily living activities and care.",
            "Administered prescribed medications under supervision.",
            "Monitored and recorded patient vital signs.",
            "Provided wound care and basic nursing support.",
            "Educated patients and families on health practices.",
            "Maintained clean and safe patient care environments.",
            "Documented nursing observations and care provided.",
            "Collaborated with RNs and physicians in patient care.",
            "Responded to patient needs and concerns promptly.",
            "Ensured adherence to infection control protocols."
        ]
    },
    {
        "jt": "Midwife",
        "field_group": "HealthCare & Medical",
        "skills": [
            "Prenatal Care",
            "Labor and Delivery Management",
            "Postnatal Care",
            "Newborn Care",
            "Patient Education",
            "Emergency Response",
            "Record Keeping",
            "Compassion",
            "Communication"
        ],
        "suggestions": [
            "Provided prenatal care and monitored maternal health.",
            "Assisted in labor and managed normal deliveries.",
            "Cared for mothers and newborns post-delivery.",
            "Educated mothers on breastfeeding and infant care.",
            "Monitored vital signs during pregnancy and delivery.",
            "Responded to obstetric emergencies as required.",
            "Maintained accurate maternal and neonatal records.",
            "Collaborated with obstetricians and healthcare teams.",
            "Promoted reproductive and maternal health awareness.",
            "Supported families emotionally during childbirth."
        ]
    },
    {
        "jt": "Medical Laboratory Technician",
        "field_group": "HealthCare & Medical",
        "skills": [
            "Sample Collection",
            "Laboratory Testing",
            "Microscopy",
            "Clinical Chemistry",
            "Hematology",
            "Microbiology",
            "Record Keeping",
            "Laboratory Safety",
            "Attention to Detail"
        ],
        "suggestions": [
            "Collected and processed patient samples for testing.",
            "Performed laboratory tests in hematology and microbiology.",
            "Operated laboratory equipment and ensured calibration.",
            "Analyzed results and reported findings to physicians.",
            "Maintained accurate laboratory records and documentation.",
            "Ensured compliance with laboratory safety protocols.",
            "Collaborated with healthcare professionals on diagnoses.",
            "Monitored quality control in laboratory procedures.",
            "Prepared reagents and testing solutions.",
            "Supported research and diagnostic laboratory activities."
        ]
    },
    {
        "jt": "Caregiver",
        "field_group": "HealthCare & Medical",
        "skills": [
            "Patient Support",
            "Daily Living Assistance",
            "Compassion",
            "Basic Medical Care",
            "Medication Reminders",
            "Household Support",
            "Record Keeping",
            "Communication",
            "Patience"
        ],
        "suggestions": [
            "Assisted patients with daily living activities.",
            "Provided companionship and emotional support.",
            "Reminded patients to take prescribed medications.",
            "Helped with mobility and personal hygiene tasks.",
            "Prepared meals and assisted with feeding when necessary.",
            "Maintained clean and safe living environments.",
            "Documented patient activities and observations.",
            "Communicated patient needs to healthcare professionals.",
            "Provided basic first aid when required.",
            "Supported families in caring for elderly or disabled members."
        ]
    },
    {
        "jt": "Nutritionist",
        "field_group": "HealthCare & Medical",
        "skills": [
            "Nutritional Assessment",
            "Diet Planning",
            "Patient Education",
            "Health Promotion",
            "Weight Management",
            "Public Health",
            "Communication",
            "Record Keeping"
        ],
        "suggestions": [
            "Assessed patients’ dietary needs and health conditions.",
            "Developed personalized diet and nutrition plans.",
            "Educated individuals and groups on healthy eating habits.",
            "Monitored patients’ progress and adjusted diet plans.",
            "Promoted public health and wellness through nutrition education.",
            "Collaborated with doctors and healthcare teams.",
            "Maintained accurate nutrition counseling records.",
            "Specialized in weight management and chronic disease diets.",
            "Participated in community health awareness programs.",
            "Advised on food safety and proper nutrition practices."
        ]
    },
    {
        "jt": "Dietitian",
        "field_group": "HealthCare & Medical",
        "skills": [
            "Clinical Nutrition",
            "Diet Planning",
            "Medical Nutrition Therapy",
            "Patient Education",
            "Nutritional Assessment",
            "Health Promotion",
            "Record Keeping",
            "Communication"
        ],
        "suggestions": [
            "Provided medical nutrition therapy for patients with health conditions.",
            "Designed diet plans for individuals with specific nutritional needs.",
            "Monitored patients’ responses to dietary interventions.",
            "Educated patients on therapeutic diets and nutrition.",
            "Collaborated with healthcare teams on nutrition care plans.",
            "Maintained accurate dietary and clinical records.",
            "Promoted healthy lifestyle changes through diet education.",
            "Specialized in hospital and clinical nutrition programs.",
            "Advised on nutrition support for chronic diseases.",
            "Participated in health and wellness outreach activities."
        ]
    }
]




@transaction.atomic
def add_sample_suggestions(datas=datas):
    # return
    for data in datas:
        jt = data.get("jt", "").strip()
        skills = data.get("skills", [])
        suggestions = data.get("suggestions", []) or data.get("responsibilities", [])
        # return 

        if not jt:
            print("Job title is required.")
            return

        # Add job title
        job, created = JobTitle.objects.get_or_create(
            title__iexact=jt,
            defaults={"title": jt, "field_group": data.get("field_group", "Other")}
        )

        # # unlink existing responsibilities for backend developer and delete unlinked ones
        # job.responsibilities.clear()
        # Responsibility.objects.filter(jobs=None).delete()


        # Add skills. for each skill, link to job title
        for skill_name in skills:
            skill_name = skill_name.strip()
            if not skill_name:
                continue
            skill, _ = Skill.objects.get_or_create(
                name__iexact=skill_name, defaults={"name": skill_name}
            )
            job.skills.add(skill)
        
        # Add responsibilities. for each suggestion, link to job title
        for resp_text in suggestions:
            resp_text = resp_text.strip()
            if not resp_text:
                continue
            resp, _ = Responsibility.objects.get_or_create(
                text__iexact=resp_text, defaults={"text": resp_text}
            )
            job.responsibilities.add(resp)

def add_sample_skills(skills: list, jt: str):
    """This function adds sample skills to a job title."""
    jt = jt.strip()
    if not jt:
        print("Job title is required.")
        return

    # Add job title
    job, created = JobTitle.objects.get_or_create(
        title__iexact=jt,
        defaults={"title": jt, "field_group": "Other"}
    )

    # Add skills. for each skill, link to job title
    for skill_name in skills:
        skill_name = skill_name.strip()
        if not skill_name:
            continue
        skill, _ = Skill.objects.get_or_create(
            name__iexact=skill_name, defaults={"name": skill_name}
        )
        job.skills.add(skill)

def get_suggestions_for_all_job_titles():
    """ This function returns a dictionary of job titles with their associated responsibilities and skills."""
    JTs = JobTitle.objects.all()
    serialized_JTs = JobTitleSerializer(JTs, many=True).data
    suggestions = {
        jt['title'].lower()
        :
        [resp['text'] for resp in jt['responsibilities']] for jt in serialized_JTs}
    skills = {
        jt['title'].lower()
        :
        [skill['name'] for skill in jt['skills']] for jt in serialized_JTs
    }
    return suggestions, skills

def get_title_suggestions_from_gemini(jt: str):
    """This function gets job title suggestions from Gemini API."""
    field_groups = [choice[0] for choice in JobTitle._meta.get_field("field_group").choices]

    prompt = f"""
                Given a job title input: {jt}

                Tasks:
                1. Validate the title and correct spelling. If invalid, return {{}}.
                2. If valid, classify it into one of these field groups: {', '.join(field_groups)}.
                3. Generate output in JSON format:
                {{
                    "jt": "<corrected job title>",
                    "field_group": "<one of the field groups>",
                    "skills": ["Skill 1", "Skill 2", ...],
                    "responsibilities": [
                        "Conducted patient consultations and physical examinations.",
                        "Diagnosed and treated a wide range of medical conditions.",
                         ...
                    ]
                }}
                4. Provide at least 20 relevant skills and 20 relevant responsibilities suggsetions for a resume builder (fewer only if not possible).
            """
    response = get_structured_data_from_gemini(prompt)
    if response:
        add_sample_suggestions([response])
    return get_suggestions_for_all_job_titles()

def get_skill_suggestion_from_gemini(skill: str, job_title: str):
    """This function gets skill suggestions from Gemini API."""
    prompt = f"""
                Given a skill input: {skill}, and a job title: {job_title}

                Tasks:
                1. Validate the skill and correct spelling. If invalid, return {{}}.
                2. If valid, generate output in JSON format:
                {{
                    "skill": "<corrected skill name>",
                    "related_skills": ["Related Skill 1", "Related Skill 2", ...]
                }}
                3. Provide at least 5 relevant related skills for the job title (fewer only if not possible).
            """
    response = get_structured_data_from_gemini(prompt)
    if response:
        skills = [response.get("skill", "").strip()] if response.get("skill", "").strip() else []
        skills.extend(response.get("related_skills", []))
        add_sample_skills(skills, job_title)
    return get_suggestions_for_all_job_titles()
    