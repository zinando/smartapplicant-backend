job_fields = {
    # Technology
    "technology": [
        "Software Engineer", "Data Scientist", "DevOps Engineer",
        "Frontend Developer", "Machine Learning Engineer", "Systems Administrator", "Backend Developer", "UI/UX Designer",
        "Product Manager", "Data Analyst", "Python Developer"
    ],
    
    # Engineering
    "engineering": [
        "Mechanical Engineer", "Civil Engineer", "Electrical Engineer", "Electrical Maintenance Technician", "Mechanical Maintenance Technician",
        "HVAC Technician", "Automotive Engineer", "Aerospace Engineer"
    ],
    
    # Healthcare
    "healthcare": [
        "Registered Nurse", "Physician", "Medical Technician", "Medical Lab Technician", 
        "Pharmacist", "Surgeon", "Dentist"
    ],
    
    # Business
    "business": [
        "Marketing Manager", "Financial Analyst", "HR Specialist",
        "Sales Executive", "Operations Manager", "Accountant"
    ],
    
    # Hospitality
    "hospitality": [
        "Hotel Manager", "Chef", "Event Planner",
        "Tour Guide", "Sommelier", "Restaurant Manager"
    ]
}

soft_skills_keywords = {
    # Technology/IT
    "technology": [
        "Problem-solving",
        "Collaboration",
        "Adaptability",
        "Attention to detail",
        "Critical thinking",
        "Time management",
        "Creativity",
        "Communication",
        "Teamwork",
        "Leadership"
    ],
    
    # Engineering
    "engineering": [
        "Analytical thinking",
        "Precision",
        "Teamwork",
        "Project management",
        "Technical communication",
        "Safety awareness",
        "Decision-making",
        "Resourcefulness",
        "Quality focus",
        "Process improvement",
        "Cross-disciplinary coordination"
    ],
    
    # Healthcare
    "healthcare": [
        "Empathy",
        "Active listening",
        "Stress management",
        "Compassion",
        "Patience",
        "Cultural sensitivity",
        "Ethical judgment",
        "Team coordination",
        "Crisis management",
        "Professional discretion"
    ],
    
    # Business/Finance
    "business": [
        "Leadership",
        "Negotiation",
        "Strategic planning",
        "Persuasion",
        "Networking",
        "Emotional intelligence",
        "Presentation skills",
        "Conflict resolution",
        "Decision-making",
        "Customer focus"
    ],
    
    # Hospitality
    "hospitality": [
        "Customer service",
        "Multitasking",
        "Cultural awareness",
        "Patience",
        "Problem-solving",
        "Adaptability",
        "Attention to detail",
        "Communication",
        "Teamwork",
        "Creativity"
    ],
    
    # General (fallback)
    "general": [
        "Communication",
        "Teamwork",
        "Time management",
        "Work ethic",
        "Adaptability",
        "Problem-solving",
        "Positive attitude",
        "Professionalism",
        "Punctuality",
        "Initiative"
    ]
}

tools_tech = {
    # Technology/Software Development
    "technology": [
        "Git", "Docker", "Kubernetes", "AWS", "Azure",
        "Jenkins", "Terraform", "Ansible", "Python", "Java",
        "SQL", "NoSQL", "React", "Node.js", "TensorFlow",
        "PyTorch", "JIRA", "Confluence", "VS Code", "IntelliJ",
        "Agile", "CI/CD", "Microservices"
    ],
    
    # Engineering (Mechanical/Electrical/Civil)
    "engineering": [
        "AutoCAD", "SolidWorks", "MATLAB", "ANSYS", "Revit",
        "PLC Systems", "CATIA", "LabVIEW", "Arduino", "Raspberry Pi",
        "CNC Machines", "3D Printing", "HVAC Controls", "PCB Design",
        "SPICE", "ETAP", "HYSYS", "EPANET", "STAAD Pro", "GIS"
    ],
    
    # Healthcare/Medical
    "healthcare": [
        "EPIC EHR", "Cerner", "Meditech", "PACS Systems",
        "HL7 Interfaces", "DICOM", "Practice Management Software",
        "Telemedicine Platforms", "Bioinformatics Tools",
        "Medical Imaging Software", "Lab Information Systems",
        "ePrescribing Systems", "Patient Monitoring Devices",
        "EMR Systems", "CPOE Systems", "Medical Billing Software",
        "Surgical Robotics", "AI Diagnostic Tools", "Pharmacy Systems"
    ],
    
    # Business/Finance
    "business": [
        "Excel", "Tableau", "Power BI", "SAP", "QuickBooks",
        "Salesforce", "HubSpot", "Zoho CRM", "Google Analytics",
        "SQL Databases", "Oracle", "Bloomberg Terminal", "SPSS",
        "Python (Pandas)", "R", "JIRA", "Trello", "Asana",
        "Adobe Creative Suite", "Mailchimp"
    ],
    
    # Hospitality/Tourism
    "hospitality": [
        "Property Management Systems", "POS Systems", "OpenTable",
        "Reservation Software", "Event Management Platforms",
        "Housekeeping Management Tools", "Revenue Management Systems",
        "Customer Loyalty Platforms", "TripAdvisor Management",
        "Food Costing Software", "Beverage Inventory Systems",
        "HRIS Systems", "Digital Menu Platforms", "Guest Feedback Tools",
        "Channel Managers", "Booking Engines", "Tour Operator Software"
    ],
    
    # General (fallback)
    "general": [
        "Microsoft Office", "Google Workspace", "Zoom",
        "Slack", "Teams", "Project Management Software",
        "CRM Systems", "Basic Database Tools", "Social Media Platforms",
        "Cloud Storage Solutions"
    ]
}

technical_keywords = {
    # Technology
    "technology": {
        "Technical Skills": ["programming", "algorithms", "debugging", "system design"],
        "Tools and Concepts": tools_tech['technology'],
        "Soft Skills": soft_skills_keywords['technology']
    },
    
    # Engineering
    "engineering": {
        "Technical Skills": ["CAD", "prototyping", "fluid dynamics", "circuit design"],
        "Tools and Concepts": tools_tech['engineering'],
        "Soft Skills": soft_skills_keywords['engineering']
    },
    
    # Healthcare
    "healthcare": {
        "Clinical Skills": ["patient care", "phlebotomy", "EMR systems"],
       "Tools and Concepts": tools_tech['healthcare'],
        "Soft Skills": soft_skills_keywords['healthcare']
    },
    
    # Business
    "business": {
        "Analytical Skills": ["financial modeling", "market research", "KPI tracking"],
        "Tools and Concepts": tools_tech['business'],
        "Soft Skills": soft_skills_keywords['business']
    },
    
    # Hospitality
    "hospitality": {
        "Service Skills": ["customer service", "event coordination", "menu planning"],
        "Tools and Concepts": tools_tech['hospitality'],
        "Soft Skills": soft_skills_keywords['hospitality']
    }
}

supported_country_phonecodes = {
    # 🌍 Africa
    'NG': {'name': 'Nigeria', 'code': '+234'},
    'GH': {'name': 'Ghana', 'code': '+233'},
    'KE': {'name': 'Kenya', 'code': '+254'},
    'ZA': {'name': 'South Africa', 'code': '+27'},
    'EG': {'name': 'Egypt', 'code': '+20'},
    'MA': {'name': 'Morocco', 'code': '+212'},
    'ET': {'name': 'Ethiopia', 'code': '+251'},
    'TZ': {'name': 'Tanzania', 'code': '+255'},
    'UG': {'name': 'Uganda', 'code': '+256'},
    'SN': {'name': 'Senegal', 'code': '+221'},

    # 🌎 Americas
    'US': {'name': 'United States', 'code': '+1'},
    'CA': {'name': 'Canada', 'code': '+1'},
    'MX': {'name': 'Mexico', 'code': '+52'},
    'BR': {'name': 'Brazil', 'code': '+55'},
    'AR': {'name': 'Argentina', 'code': '+54'},
    'CO': {'name': 'Colombia', 'code': '+57'},
    'CL': {'name': 'Chile', 'code': '+56'},
    'JM': {'name': 'Jamaica', 'code': '+1-876'},
    'TT': {'name': 'Trinidad and Tobago', 'code': '+1-868'},
    'DO': {'name': 'Dominican Republic', 'code': ['+1-809', '+1-829', '+1-849']},

    # 🌍 Europe
    'GB': {'name': 'United Kingdom', 'code': '+44'},
    'DE': {'name': 'Germany', 'code': '+49'},
    'FR': {'name': 'France', 'code': '+33'},
    'IT': {'name': 'Italy', 'code': '+39'},
    'ES': {'name': 'Spain', 'code': '+34'},
    'NL': {'name': 'Netherlands', 'code': '+31'},
    'SE': {'name': 'Sweden', 'code': '+46'},
    'CH': {'name': 'Switzerland', 'code': '+41'},
    'PL': {'name': 'Poland', 'code': '+48'},
    'PT': {'name': 'Portugal', 'code': '+351'},

    # 🌏 Asia
    'CN': {'name': 'China', 'code': '+86'},
    'IN': {'name': 'India', 'code': '+91'},
    'JP': {'name': 'Japan', 'code': '+81'},
    'KR': {'name': 'South Korea', 'code': '+82'},
    'PH': {'name': 'Philippines', 'code': '+63'},
    'TH': {'name': 'Thailand', 'code': '+66'},
    'PK': {'name': 'Pakistan', 'code': '+92'},
    'ID': {'name': 'Indonesia', 'code': '+62'},
    'BD': {'name': 'Bangladesh', 'code': '+880'},
    'VN': {'name': 'Vietnam', 'code': '+84'}
}

common_job_titles = [
    # Executive & Leadership
    "chief executive officer", "ceo", "chief operating officer", "coo", "chief financial officer", "cfo",
    "chief technology officer", "cto", "chief marketing officer", "cmo", "president", "vice president", "vp",
    "managing director", "executive director", "general manager", "head of operations", "director",

    # Administrative
    "administrative assistant", "office manager", "executive assistant", "receptionist", "secretary",

    # Engineering & Technical
    "software engineer", "software developer", "web developer", "backend developer", "frontend developer",
    "full stack developer", "mobile developer", "devops engineer", "qa engineer", "data engineer", "machine learning engineer",
    "systems engineer", "embedded engineer", "cloud engineer", "network engineer", "site reliability engineer", "technical support engineer",

    # Data & Analytics
    "data analyst", "data scientist", "business analyst", "data architect", "bi analyst", "research analyst",

    # IT & Infrastructure
    "it support specialist", "systems administrator", "network administrator", "it manager", "database administrator",

    # Product & Project Management
    "product manager", "product owner", "project manager", "scrum master", "program manager", "business analyst",

    # Design & UX
    "graphic designer", "ui designer", "ux designer", "product designer", "visual designer", "creative director",

    # Marketing & Sales
    "marketing manager", "digital marketing specialist", "seo specialist", "social media manager",
    "content marketer", "copywriter", "brand manager", "sales representative", "account manager",
    "business development manager", "growth manager", "customer success manager",

    # Finance & Accounting
    "accountant", "financial analyst", "auditor", "controller", "bookkeeper", "finance manager",

    # Human Resources
    "hr manager", "hr specialist", "recruiter", "talent acquisition specialist", "people operations manager",

    # Legal
    "lawyer", "attorney", "legal counsel", "legal assistant", "paralegal", "compliance officer",

    # Education
    "teacher", "professor", "instructor", "tutor", "academic advisor", "curriculum designer",

    # Healthcare
    "nurse", "doctor", "physician", "pharmacist", "medical assistant", "dentist", "therapist", "caregiver",

    # Manufacturing & Operations
    "machine operator", "plant manager", "production supervisor", "maintenance technician",
    "quality assurance inspector", "supply chain manager", "logistics coordinator", "warehouse manager",
    "forklift operator", "assembly line worker", "production planner", "inventory specialist", "engineering technician",
    "mechanical engineer", "mechanical technician", "electrical engineer", "electrical technician", "civil engineer", "industrial engineer", "process engineer", "production engineer",
    "operations manager", "manufacturing engineer", "quality control engineer", "project engineer", "field service engineer",
    "construction manager", "site engineer", "safety officer", "environmental engineer", "materials engineer",
    "production technician", "machinist", "welding technician", "fabrication technician", "assembly technician",

    # Others
    "freelancer", "consultant", "intern", "volunteer", "contractor", "entrepreneur", "founder"
]

career_objective_titles = [
    "Objective",
    "Career Objective",
    "Professional Objective",
    "Career Summary",
    "Professional Summary",
    "Summary",
    "Summary of Qualifications",
    "Personal Statement",
    "Profile",
    "Professional Profile",
    "Career Profile",
    "Executive Summary",
    "About Me",
    "Highlights",
    "Personal Overview",
    "Professional Overview",
    "Career Highlights",
    "Background Summary",
    "Introductory Statement",
    "Candidate Summary",
    "Overview"
]

experience_section_titles = [
    "Experience",
    "Work Experience",
    "Professional Experience",
    "Employment History",
    "Career History",
    "Relevant Experience",
    "Work History",
    "Professional Background",
    "Project Experience",
    "Industry Experience",
    "Job Experience",
    "Employment Experience"
]

skills_section_titles = [
    "Skills",
    "Technical Skills",
    "Professional Skills",
    "Key Skills",
    "Core Competencies",
    "Competencies",
    "Areas of Expertise",
    "Skill Set",
    "Relevant Skills",
    "Summary of Skills",
    "Capabilities",
    "Technologies"
]

certifications_section_titles = [
    "Certifications",
    "Licenses and Certifications",
    "Professional Certifications",
    "Credentials",
    "Licenses",
    "Certification",
    "Achievements and Certifications",
    "Qualifications"
]

education_section_titles = [
    "Education",
    "Academic Background",
    "Academic Qualifications",
    "Educational Background",
    "Educational Qualifications",
    "Academic History",
    "Training and Education",
    "Education and Training",
    "Degrees",
    "Formal Education"
]

other_boundary_section_titles = [
    "Projects",
    "Personal Projects",
    "Volunteer Experience",
    "Volunteer Work",
    "Publications",
    "Awards",
    "Achievements",
    "Honors",
    "Interests",
    "Languages",
    "Professional Development",
    "Training",
    "Courses",
    "References",
    "Additional Information",
    "Portfolio",
    "Extracurricular Activities",
    "Affiliations",
    "Memberships",
    "Internships",
    "Summary of Qualifications",
    "Professional Affiliations", "Professional Memberships", "Professional Associations", "Professional Involvement",
    "Professional Involvement", "Professional Engagements", "Professional Networks", "Professional Connections", "Professional Relationships"
    "Hobbies", "Hobby"
]

years_of_experience_map = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
        'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14,
        'fifteen': 15, 'sixteen': 16, 'seventeen': 17, 'eighteen': 18,
        'nineteen': 19, 'twenty': 20, 'twenty-one': 21, 'twenty-two': 22,
        'twenty-three': 23, 'twenty-four': 24, 'twenty-five': 25, "twenty-six": 26,
        'twenty-seven': 27, 'twenty-eight': 28, 'twenty-nine': 29, 'thirty': 30,
        'thirty-one': 31, 'thirty-two': 32, 'thirty-three': 33, 'thirty-four': 34,
        'thirty-five': 35, 'thirty-six': 36, 'thirty-seven': 37, 'thirty-eight': 38,
        'thirty-nine': 39, 'forty': 40, 'forty-one': 41, 'forty-two': 42,
        'forty-three': 43, 'forty-four': 44, 'forty-five': 45, 'forty-six': 46,
        'forty-seven': 47, 'forty-eight': 48, 'forty-nine': 49, 'fifty': 50
    }

lower_degree_keywords = [
    "National Diploma", "ND", "N.D.",
    "Higher National Diploma", "HND", "H.N.D.",
    "Ordinary National Diploma", "OND", "O.N.D.",
    "Nigerian Certificate in Education", "NCE", "N.C.E.",
    "City and Guilds", "City & Guilds",

    # Associate Degrees
    "Associate of Arts", "AA", "A.A.",
    "Associate of Science", "AS", "A.S.",
    "Associate of Applied Science", "AAS", "A.A.S.",
    "Associate of Fine Arts", "AFA", "A.F.A.",
    "Associate of Business Administration", "ABA", "A.B.A.",
    "Associate of Engineering", "AE", "A.E."
]
higher_degree_keywords = [
    # Bachelor Degrees
    "Bachelor of Arts", "BA", "B.A.",
    "Bachelor of Science", "BSc", "BS", "B.Sc.", "B.S.",
    "Bachelor of Fine Arts", "BFA", "B.F.A.",
    "Bachelor of Business Administration", "BBA", "B.B.A.",
    "Bachelor of Engineering", "BEng", "BE", "B.Eng.", "B.E.",
    "Bachelor of Technology", "BTech", "B.Tech.",
    "Bachelor of Architecture", "BArch", "B.Arch.",
    "Bachelor of Education", "BEd", "B.Ed.",
    "Bachelor of Laws", "LLB", "LL.B.",
    "Bachelor of Commerce", "BCom", "B.Com.",
    "Bachelor of Computer Science", "BCS", "B.Comp.Sc.", "B.CompSc",
    "Bachelor of Nursing", "BN", "BSN", "B.N.", "B.S.N.",
    "Bachelor of Pharmacy", "BPharm", "B.Pharm.",
    "Bachelor of Social Work", "BSW", "B.S.W.",
    "Bachelor of Music", "BM", "B.M.",
    "Bachelor of Medical Science", "BMedSc", "B.Med.Sc.",
    "Bachelor of Public Administration", "BPA", "B.P.A.",

    # Master Degrees
    "Master of Arts", "MA", "M.A.",
    "Master of Science", "MSc", "MS", "M.Sc.", "M.S.",
    "Master of Fine Arts", "MFA", "M.F.A.",
    "Master of Business Administration", "MBA", "M.B.A.",
    "Master of Engineering", "MEng", "ME", "M.Eng.", "M.E.",
    "Master of Technology", "MTech", "M.Tech.",
    "Master of Architecture", "MArch", "M.Arch.",
    "Master of Education", "MEd", "M.Ed.",
    "Master of Laws", "LLM", "LL.M.",
    "Master of Commerce", "MCom", "M.Com.",
    "Master of Computer Science", "MCS", "M.Comp.Sc.", "M.CompSc",
    "Master of Nursing", "MN", "MSN", "M.N.", "M.S.N.",
    "Master of Pharmacy", "MPharm", "M.Pharm.",
    "Master of Social Work", "MSW", "M.S.W.",
    "Master of Public Health", "MPH", "M.P.H.",
    "Master of Public Administration", "MPA", "M.P.A.",
    "Master of Music", "MM", "MMus", "M.M.", "M.Mus.",

    # Doctorate Degrees
    "Doctor of Philosophy", "PhD", "Ph.D.", "DPhil", "D.Phil.",
    "Doctor of Medicine", "MD", "M.D.",
    "Doctor of Education", "EdD", "Ed.D.",
    "Doctor of Business Administration", "DBA", "D.B.A.",
    "Doctor of Engineering", "DEng", "EngD", "D.Eng.", "Eng.D.",
    "Doctor of Pharmacy", "PharmD", "Pharm.D.",
    "Doctor of Dental Surgery", "DDS", "D.D.S.",
    "Doctor of Public Health", "DrPH", "Dr.P.H.",
    "Doctor of Theology", "ThD", "DTh", "Th.D.", "D.Th.",
    "Doctor of Nursing Practice", "DNP", "D.N.P.",
    "Juris Doctor", "JD", "J.D."
]

degree_keywords = lower_degree_keywords + higher_degree_keywords

institution_keywords = [
    # Universities
    "University", "Uni", "Federal University", "State University", "Private University",
    "Open University", "National University", "International University",

    # Colleges
    "College", "College of Education", "College of Health", "College of Technology",
    "Teachers College", "Technical College", "Monotechnic", "School of Nursing",
    "School of Midwifery", "School of Health", "Business College",

    # Institutes
    "Institute", "Institute of Technology", "Institute of Management", "Research Institute",
    "Training Institute", "Professional Institute", "National Institute",
    "Industrial Training Institute", "Development Institute",

    # Polytechnics and Tech Schools
    "Polytechnic", "Federal Polytechnic", "State Polytechnic", "Polytechnic Institute", "School of Technology",

    # Certifying Bodies / Boards (optional, use contextually)
    "WAEC", "NECO", "NABTEB", "JAMB", "NTI", "TRCN", "NYSC",

    # Medical & Specialized Institutions
    "Teaching Hospital", "Nursing School", "Midwifery School", "Health Technology",
    "College of Medicine", "Medical School", "School of Public Health",

    # Vocational / Technical Centers
    "Technical School", "Technical Institute", "Vocational School", "Industrial Training Centre",
    "Trade Centre", "Skills Acquisition Centre", "Craft School", "Apprenticeship Centre",

    # Others
    "Academy", "Seminary", "Conservatory", "Business School", "Law School", "Graduate School",
    "Training Centre", "Training Center", "Leadership School", "Continuing Education",
    "Lifelong Learning Institute", "School of Arts",

    # Nigeria-Specific
    "Federal College", "State College", "FCE", "COE", "NDA", "NIPSS"
]

