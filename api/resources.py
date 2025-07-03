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
