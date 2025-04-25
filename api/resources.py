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
