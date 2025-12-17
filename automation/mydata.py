notes = """
            1. The information provided here is for educating AI models to better understand the business for the purposes of generating social media post content and to provide accurate responses to customer inquiries in comments.
            2. Secret questions and answers are included for authentication purposes. They should never be revealed to anyone including the business owner.
            2. Personal information must not be included in public posts. They should only be used to answer customer's enquiry in comments. E.g when customer inquires about business contact, address etc.
"""
business_info = {
        'name': "Smart Applicant",
        'type': "service provider",
        'description': "Smart Applicant is an AI-powered resume building and optimization platform designed to help job seekers create professional, ATS-compatible resumes quickly and easily. Our platform leverages advanced AI technology to provide intelligent suggestions, smart refinements, and customization options, ensuring that users can craft resumes that stand out to recruiters and hiring managers. With Smart Applicant, users can build their dream resumes in minutes, access premium features for enhanced customization, and improve their chances of landing their desired jobs.",
        'how_to_use': "1. You can scan your current cv/resume to get ATS-compatibility score on the home page at https://smartapplicant.net/#analyze. This feature is FOC and does not require you to login/signup.\n2. Sign up for a free account or log in to get access to other features such as: Generating a new cv/resume from scratch using our enhanced resume builder with intelligent suggestions (users can download their resumes if they only have one entry per section of the resume. for multiple intems per section, a subscription/resume credit has to be purchased and used), analyzing resume agaisnt job descriptions using AI (this is also FOC), Automatic tailoring your existing resume to match job escription (this completely requires either a subsceiption or a resume credit).",
        'features': "1. ATS-compatibility scoring\n2. Detailed suggestions on how to improve ATS-compatibility\n2. New resume generation from scratch\n4. Intelligent suggestions with the resume builder\n5. Job-matching analysis\n6. Automatic resume tailoring",
        'website': "https://smartapplicant.net",
        'address': "28 Alhaji Waheed Adeyemi street, Elebu, Ibadan, Nigeria",
        'business_contacts': "2347031104270 (call or WhatsApp)",
        'social_links': "1. Facebook: https://www.facebook.com/share/15sb3h5biZ/\n2. Instagram: https://www.instagram.com/smart.applicant.net/\n3. Twitter: https://twitter.com/smartapplicant",
        'services': "AI-powered Resume Building and Optimization",
        'products': "",
        'pricing': "Free to use with basic features. Premium features available: resume credit - N1500/unit (use all premium features to get 1 resume); monthly subscriptions: 1 month - N17,500.00, 3 months - N45,000.00, 6 months - N80,000.00, 12 months - N150,000.00. (unlimited resumes within subscription period).",
        'image_links': "",
        'business_links': "1. official website: https://smartapplicant.net\n2. scan resume for ATS compatibility score: https://smartapplicant.net/#analyze\n2. resume builder: https://smartapplicant.net/new_resume\n3. login/signup: https://smartapplicant.net/login\n4. pricing page: https://smartapplicant.net/premium",
        'secret_questions': "Q: Mother's maiden name? A: Isietu. Q: Best friend's name in Logiss (my secondary school)? A: Ikechukwu Nnadilim. Q: last primary school attended? A: Pioneer Primary School, Edenta, Awo-Idemili, Imo State.",
        'last_updated': "2025-06-10",
        'notes': notes
    }
business_info_form_template = """"
    # name
    * Your business name here

    # type
    * Your business type here (service provider or product seller)

    # description
    * A brief description of your business here

    # how_to_use
    * Instructions on how customers can use your services/products

    # features
    * Key features of your services/products

    # website
    * Your business website address here

    # address
    * Your business physical address here

    # business_contacts
    * Your business contact information here (must include whatsapp phone number. Email is optional)

    # social_links
    * Links to your business social media profiles here (Facebook, Instagram, Twitter, LinkedIn, etc)

    # services
    * List of services your business offers here (for service providers only)

    # products
    * List of products your business sells here (for product sellers only)

    # pricing
    * Pricing details for your services/products here

    # image_links
    * Links to images representing your business here (logo, products, services, etc). provide descriptions for each image link

    # business_links
    * Important links related to your business here (official website, product pages, service pages, etc). provide descriptions for each link

    # secret_questions
    * List of at least two secret questions with answers for authentication when using customer service here (these should not be revealed to anyone)

    # last_updated
    * Date when this business information was last updated (format: YYYY-MM-DD)

    <<<<<<<<<<<<<<<<<<<<<<<<<< How To Fill The Form >>>>>>>>>>>>>>>>>>>>>>
        Copy the entire text and paste into your typing area.
        Replace each section that has "*" mark with your business information.
        You can use multiple lines for each section if necessary, ensuring each line starts with "*".

        Example:

        # name
        * Smart Applicant

        # business_links
        * official website: https://smartapplicant.net
        * scan resume for ATS compatibility score: https://smartapplicant.net/#analyze
    <<<<<<<<<<<<<<<<<<<<<<<<<<<<< End Of Form >>>>>>>>>>>>>>>>>>>>>>
"""
tenant_info = {
        'name': "Smart Applicant",
        'description': "Smart Applicant is a leading provider of AI-powered chatbot development, automation, and AI solutions for businesses looking to enhance customer engagement and streamline operations. We also provide resume building and optimization solutions through our SmartApplicant platform.",
        'admin_contacts': {
            "owner": "2347031104270",
            "support": "2347031104270",
            "order": "2347031104270",
            "delivery": "2347031104270"
        },
        'ceo': "Ndubumma Samuel Nnadozie",
        'address': "28 Alhaji Waheed Adeyemi street, Elebu, Ibadan, Nigeria",
        'services': ["AI-powered WhatsApp Customer Care Solution", "AI-powered Faccebook Customer Care Solution", "AI-powered Instagram Customer Care Solution", "AI-powered Telegram Customer Care Solution", "Facebook Page Content Creation Automation", "Instagram Business Content Creation Automation", "Resume Building and Optimization"],
        'pricing': {
            "Customer Care Solutions": "Initial Setup - starting at N100,000.00, depending on complexity and features. Monthly Subscription/Maintenance - N25,000.00 per month/platform.",
            "Resume Building": "Free to use with basic features. Premium features available: resume credit - N1500/unit (use all premium features to get 1 resume); monthly subscriptions: 1 month - N17,500.00, 3 months - N45,000.00, 6 months - N80,000.00, 12 months - N150,000.00. (unlimited resumes within subscription period)."
        },
        'image_data': [],
        'business_links': [
            'official website: https://smartapplicant.net',
            'scan resume for ATS compatibility score: https://smartapplicant.net/#analyze'
        ],
        'faq': [],
        'use_marketing': False,
        'last_updated': "2025-06-10"
    }

tenant = {
    "name": "Smart Applicant",
    "waba_id": "814931971241538",
    "waba_phone_number": "2349159433860",
    "waba_phone_number_id": "758491714023567",
    "fb_page_id": "750798604776594",
    "ig_business_account_id": "17841476699966994",
    "tg_bot_username": "SmartApplicantBot",
    "custom_prompts": None,
    "business_details": tenant_info,
    "content_schedule_times": {
        "facebook": [7, 9, 12, 15, 19, 21],
        "instagram": [8, 10, 13, 16, 20, 22],
        "telegram": [9, 11, 14, 17, 18, 21]
    },
    "media_history": {
        "facebook": [
            {"id": "122131999634955403", "caption": "🚀 Build your dream résumé in minutes — for FREE! SmartApplicant helps you craft professional, polished résumés with intelligent AI suggestions and smart refinements. You only pay when you want more customization — but your first build is completely free!👉 Try it now: https://smartapplicant.net #SmartApplicant #AIResumeBuilder #CareerGrowth #JobReady #SmartCareer"},
            {"id": "122131381064955403", "caption": "✨ Stop guessing your way through resumes — SmartApplicant helps your skills shine with AI-powered suggestions that impress recruiters 👉 smartapplicant.net"},
            {"id": "122127013994955403", "caption": "🚀 Build a resume that actually speaks for you — SmartApplicant gives you the right words, skills, and tone recruiters love. Try it today 👉 smartapplicant.net"},
            {"id": "122124144668955403", "caption": "📄 Every great career begins with one page — make yours powerful, professional, and unforgettable with SmartApplicant."},
            {"id": "122124142118955403", "caption": "🔥 Your story, sharpened. Your future, unlocked. Don’t leave your career to chance — make it Smart."},
            {"id": "122124138560955403", "caption": "💼 A CV that speaks the recruiter’s language, reflects your ambition, and turns luck into strategy — that’s the SmartApplicant promise."},
            {"id": "122124137300955403", "caption": "⚡ A CV shouldn’t just exist — it should perform. SmartApplicant brings AI, ATS power, and design brilliance in one."},
            {"id": "122124136208955403", "caption": "🔑 Your CV is your first impression — let SmartApplicant turn it into your strongest career advantage."},
            {"id": "122124135836955403", "caption": "🤝 Your CV is the handshake before the meeting — make it unforgettable with SmartApplicant."},
            {"id": "2080993235973251", "caption": "💡 Create and download your complete AI-powered resume for free — pay only if you add extra entries. Try SmartApplicant now! 👉 smartapplicant.net"}
        ],
        "instagram": [],
        "telegram": []
    },
    "evergreen_content": [
        "🚀 Build your dream résumé in minutes — for FREE! SmartApplicant helps you craft professional, polished résumés with intelligent AI suggestions and smart refinements. You only pay when you want more customization — but your first build is completely free!👉 Try it now: https://smartapplicant.net #SmartApplicant #AIResumeBuilder #CareerGrowth #JobReady #SmartCareer",
        "✨ Stop guessing your way through resumes — SmartApplicant helps your skills shine with AI-powered suggestions that impress recruiters 👉 smartapplicant.net",
        "🚀 Build a resume that actually speaks for you — SmartApplicant gives you the right words, skills, and tone recruiters love. Try it today 👉 smartapplicant.net",
        "📄 Every great career begins with one page — make yours powerful, professional, and unforgettable with SmartApplicant.",
        "🔥 Your story, sharpened. Your future, unlocked. Don’t leave your career to chance — make it Smart.",
        "💼 A CV that speaks the recruiter’s language, reflects your ambition, and turns luck into strategy — that’s the SmartApplicant promise.",
        "⚡ A CV shouldn’t just exist — it should perform. SmartApplicant brings AI, ATS power, and design brilliance in one.",
        "🔑 Your CV is your first impression — let SmartApplicant turn it into your strongest career advantage.",
        "🤝 Your CV is the handshake before the meeting — make it unforgettable with SmartApplicant.",
        "💡 Create and download your complete AI-powered resume for free — pay only if you add extra entries. Try SmartApplicant now! 👉 smartapplicant.net"
    ],
    "customers": []
}