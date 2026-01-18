notes = """
            1. The information provided here is for educating AI models to better understand the business for the purposes of generating social media post content and to provide accurate responses to customer inquiries in comments.
            2. Secret questions and answers are included for authentication purposes. They should never be revealed to anyone including the business owner.
            2. Personal information must not be included in public posts. They should only be used to answer customer's enquiry in comments. E.g when customer inquires about business contact, address etc.
"""
business_info = {
        'name': "Smart Applicant",
        'email': "zinando2000@gmail.com",
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
        'business_links': "1. official website: https://smartapplicant.net\n2. scan resume for ATS compatibility score: https://smartapplicant.net/#analyze\n3. resume builder: https://smartapplicant.net/new_resume\n4. login/signup: https://smartapplicant.net/login\n5. pricing page: https://smartapplicant.net/premium\n6. signup for facebook post automation service: https://smartapplicant.net/facebook_login/",
        'secret_questions': "Q: Mother's maiden name? A: Isietu. Q: Best friend's name in Logiss (my secondary school)? A: Ikechukwu Nnadilim. Q: last primary school attended? A: Pioneer Primary School, Edenta, Awo-Idemili, Imo State.",
        'other_info': "",
        'last_updated': "2025-06-10",
        'notes': notes
    }
business_info_form_template = """"
    # name
    * Your business name here

    # email
    * Your business email

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

    # other_info
    * Any other relevant information about your business not covered in the sections above

    # last_updated
    * Date when this business information was last updated (format: YYYY-MM-DD)

    <<<<<<<<<<<<<<<<<<<<<<<<<< How To Fill The Form >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
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
        'email': "contact@smartapplicant.net",
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
            'scan resume for ATS compatibility score: https://smartapplicant.net/#analyze',
            'resume builder: https://smartapplicant.net/new_resume',
            'login/signup: https://smartapplicant.net/login',
            'pricing page: https://smartapplicant.net/premium',
            'signup for facebook post automation service: https://smartapplicant.net/facebook_login/'
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
sample_content = [
    {'content': "Is your resume getting lost in the digital black hole? 🧐 Stop guessing and start knowing! Our free ATS compatibility scanner gives you instant feedback on how well your resume will pass the automated screening systems used by most top companies. Give it a try today—no sign-up needed!\n\nWhat's the scariest part of applying for a new job? Let us know below! 👇\n#ATSCompability #JobSearchTips", 'caption': '', 'content_type': 'text', 'comments': ['This is a game-changer! Knowing where you stand *before* submitting saves so much time. Highly recommend running your current CV through the scanner.', "We designed this feature to take the guesswork out of initial screening. Think of it as your resume's first interview!", "If you've ever wondered why you weren't called back, the ATS score might hold the answer. Let's boost those scores!", 'Curious about how deep the analysis goes? It checks formatting, keyword density, and structure specific to what robots look for!', 'What’s the highest score you think a perfectly optimized resume should achieve? Share your thoughts!']}, 
    {'content': "Dream job description in hand? Don't just copy-paste! ✂️ Our AI-powered Automatic Resume Tailoring feature takes your existing resume and instantly refines it to align perfectly with the specific requirements of the job you're targeting. Make every application feel custom-made!", 'caption': '', 'content_type': 'text', 'comments': ['This feature truly maximizes your chances. Generic resumes get generic results—tailoring is key!', "Remember, tailoring isn't just swapping a few words; it's about demonstrating direct relevance to the employer's needs.", 'For users looking to try this, remember tailoring requires either a subscription or a resume credit to unlock the full refinement process.', "What's one keyword you always ensure is present when tailoring for a tech role?", "Imagine submitting a document that speaks directly to the hiring manager's requirements—that's the Smart Applicant difference!"]}, 
    {'content': 'Building a resume from a blank page can be daunting! 😩 Our intelligent Resume Builder guides you step-by-step, offering smart suggestions as you input your experience. Create a polished, professional document in minutes, not hours.', 'caption': '', 'content_type': 'text', 'comments': ['The intelligent suggestions are fantastic for phrasing accomplishments powerfully. No morre vague bullet points!', 'We focus on structure and content flow so you can concentrate on what matters: your achievements.', "If you're new to resume writing, the builder removes 90% of the stress. Check out the link in our bio to start!", 'What section do you usually find the hardest to write: Summary, Experience, or Skills?', 'Pro Tip: Use the builder to explore different professional layouts instantly!']}, 
    {'content': 'https://smartapplicant.net', 'caption': 'Ready to transform your job application materials? Smart Applicant is the AI-powered platform designed to make your resume ATS-compatible and recruiter-ready. Click the link to sign up for free and explore the power of intelligent optimization!', 'content_type': 'link', 'comments': ['Signing up is quick and easy! Once registered, you unlock the full potential of the resume builder.', 'We believe in providing tools that genuinely improve outcomes. Give the platform a spin!', "If you're aiming for large corporations, ATS compatibility isn't optional—it's mandatory. Start here!", "Let us know in the comments once you've signed up, and we can share a quick tip for getting started!", 'Did you know you can analyze a job description against your current resume for free after logging in? Leverage that power!']}, 
    {'content': 'https://smartapplicant.net/premium', 'caption': 'Unlock the full power of AI customization! Premium features like unlimited tailoring, detailed suggestions, and advanced resume generation are waiting. See our subscription tiers and find the perfect fit for your career goals today!', 'content_type': 'link', 'comments': ['The premium features are worth it when aiming for highly competitive roles. That extra polish makes a difference.', 'Which premium feature are you most excited to try first? We love the Job-Matching Analysis!', 'We regularly update our AI models to reflect the latest hiring trends, ensuring your subscription stays relevant.', 'Thinking about upgrading? The 3-month plan often balances cost and immediate access perfectly.', "If you have any questions about what the premium features offer specifically, drop a question below—we're here to help!"]},
    {'content': 'https://smartapplicant.net/#analyze', 'caption': 'Wondering how your resume stacks up against ATS standards? Use our free ATS Compatibility Scanner to get instant feedback and actionable insights. No sign-up required—just upload your resume and see where you stand!', 'content_type': 'link', 'comments': ['This tool is a lifesaver for job seekers! Knowing your ATS score helps you understand what recruiters see first.', 'We designed the scanner to be user-friendly—just upload and get results in seconds!', "If you're unsure about the results, our blog has tips on interpreting ATS scores effectively.", 'What’s the most surprising insight you’ve gained from using the ATS scanner?', 'For best results, ensure your resume is in a compatible format (like .docx or .pdf) before uploading.']}
]

custom_prompts= {
    'txt': """
            You are a skilled social media content creator for **business_name.
            Generate 6 Facebook posts for today: 4 text posts, and 2 link posts (with caption). If business has no sharable link, return all 6 posts as text posts.
            Each post must be unique, engaging, and relevant to the business, with at least two hashtags. 
            Keep tone friendly, professional, and appealing to Facebook users. 
            For each post, create between 4 to 6 unique comments to further buttress the point of the post or to drive engagement. 
            You are commenting as the post creator to encourage engagement and to add value to the post. 
            You must not include personal information of the business owner or employees in the posts. 

            Business details for context:
            \n**business_details

            Return output as a JSON list of dictionaries, with the following structures:\n
            Text content type - {"content": "<text>", "caption": "<empty>", "content_type": "text", "comments": "<List of 4 or more unique text comments to buttress the post>"}\n
            Link content type - {"content": "<url>", "caption": "<Text to encourage users to click the url>", "content_type": "link","comments": "<List of 4 or more unique text comments to buttress the post>"}

            RULES:
            - the 'content' value for link posts must be valid url only. No extra texts.
            - you should only include link posts if the business has a website and valid urls
            - if the business does not have a website, all 6 posts must be text posts only.
        """.strip(),
    'txt-img': """
            You are a skilled social media content creator for **business_name.
            Generate 6 Facebook posts for today: 3 text posts, 2 link posts (with caption) and 1 image prompt (with caption- to be used to generate image from grok). If business has no sharable link, return 5 text posts and 1 image generation post.
            Each post must be unique, engaging, and relevant to the business, with at least two hashtags. 
            Keep tone friendly, professional, and appealing to Facebook users. 
            For each post, create between 4 to 6 unique comments to further buttress the point of the post or to drive engagement. 
            You are commenting as the post creator to encourage engagement and to add value to the post. 
            You must not include personal information of the business owner or employees in the posts. 

            Business details for context:
            \n**business_details

            Return output as a JSON list of dictionaries, with the following structures:\n
            Text content type - {"content": "<text>", "caption": "<empty>", "content_type": "text", "comments": "<List of 4 or more unique text comments to buttress the post>"}\n
            Link content type - {"content": "<url>", "caption": "<Text to encourage users to click the url>", "content_type": "link","comments": "<List of 4 or more unique text comments to buttress the post>"}
            Image content type - {"content": "<image generation prompt>", "caption": "<Text to be posted with the image>", "content_type": "image", "comments": "<List of 4 or more unique text comments to buttress the post>"}

            RULES:
            - the 'content' value for link posts must be valid url only. No extra texts.
            - you should only include link posts if the business has a website and valid urls
            - if the business does not have a website, return 5 text posts and 1 image post
        """.strip(),
    'txt-vid': """
            You are a skilled social media content creator for **business_name.
            Generate 5 Facebook posts for today: 3 text posts, 2 link posts (with caption).
            If business has no sharable link, return all 4 text posts, 1 image post, and 1 video post.
            Each post must be unique, engaging, and relevant to the business, with at least two hashtags. 
            Keep tone friendly, professional, and appealing to Facebook users. 
            For each post, create between 4 to 6 unique comments to further buttress the point of the post or to drive engagement. 
            You are commenting as the post creator to encourage engagement and to add value to the post. 
            You must not include personal information of the business owner or employees in the posts. 

            Business details for context:
            \n**business_details

            Return output as a JSON list of dictionaries, with the following structures:\n
            Text content type - {"content": "<text>", "caption": "<empty>", "content_type": "text", "comments": "<List of 4 or more unique text comments to buttress the post>"}\n
            Link content type - {"content": "<url>", "caption": "<Text to encourage users to click the url>", "content_type": "link","comments": "<List of 4 or more unique text comments to buttress the post>"}
            
            RULES:
            - the 'content' value for link posts must be valid url only. No extra texts.
            - you should only include link posts if the business has a website and valid urls
            - if the business does not have a website, all 5 posts must be text posts only.
            """.strip(),
    'img-vid': """
            You are a skilled social media content creator for **business_name.
            Generate 2 Facebook posts for today: 2 image prompt (with caption- to be used to generate image from grok).
            Each post must be unique, engaging, and relevant to the business, with at least two hashtags. 
            Keep tone friendly, professional, and appealing to Facebook users. 
            For each post, create between 4 to 6 unique comments to further buttress the point of the post or to drive engagement. 
            You are commenting as the post creator to encourage engagement and to add value to the post. 
            You must not include personal information of the business owner or employees in the posts. 

            Business details for context:
            \n**business_details

            Return output as a JSON list of dictionaries, with the following structures:\n
            {"content": "<image generation prompt>", "caption": "<Text to be posted with the image>", "content_type": "image", "comments": "<List of 4 or more unique text comments to buttress the post>"}
            """.strip(),
    'txt-img-vid': """
            You are a skilled social media content creator for **business_name.
            Generate 5 Facebook posts for today: 3 text posts, 1 link posts (with caption), 1 image prompt (with caption- to be used to generate image from grok).
            If business has no sharable link, return all 4 text posts, and 1 image post.
            Each post must be unique, engaging, and relevant to the business, with at least two hashtags. 
            Keep tone friendly, professional, and appealing to Facebook users. 
            For each post, create between 4 to 6 unique comments to further buttress the point of the post or to drive engagement. 
            You are commenting as the post creator to encourage engagement and to add value to the post. 
            You must not include personal information of the business owner or employees in the posts. 

            Business details for context:
            \n**business_details

            Return output as a JSON list of dictionaries, with the following structures:\n
            Text content type - {"content": "<text>", "caption": "<empty>", "content_type": "text", "comments": "<List of 4 or more unique text comments to buttress the post>"}\n
            Link content type - {"content": "<url>", "caption": "<Text to encourage users to click the url>", "content_type": "link","comments": "<List of 4 or more unique text comments to buttress the post>"}
            Image content type - {"content": "<image generation prompt>", "caption": "<Text to be posted with the image>", "content_type": "image", "comments": "<List of 4 or more unique text comments to buttress the post>"}
            
            RULES:
            - the 'content' value for link posts must be valid url only. No extra texts.
            - you should only include link posts if the business has a website and valid urls
            - if the business does not have a website, return 4 text posts and 1 image post.
            
        """.strip()
}

video_plan = {
  "media_type": "video",
  "page_id": "750798604776594",
  "caption": "Transform your nails from bitten and dull to beautiful and healthy in minutes 💅✨",
  "comments": [
    "Which nail problem do you struggle with the most?",
    "DM us now to get your nail care kit today!"
  ],
  "background_music_url": "https://drive.google.com/file/d/1y-0z2zqXXnlfocaFGpud1FDuxxr0DTLj/view?usp=drivesdk",
  "video_cover_url": "https://drive.google.com/file/d/1c3WnhAyX-naa7SBPexHv6EG4BlcILxEY/view?usp=drivesdk",
  "watermark": {"text":"Nail Extras", "text_color":"green", "font":"anton"},
  "scenes": [
    {
      "media_type": "video",
      "url": "https://drive.google.com/file/d/1ensR02kvLKjq--hhL-CWnMLqAshJpiB1/view?usp=drivesdk",
      "overlay_text": {"text":"Do you bite your nails and feel embarrassed to show your hands?", "text_color":"green", "font":"anton", "font_size":60},
      "voice_over": "Do you bite your nails and feel embarrassed to show your hands?",
      "duration": 5,
      "transition": "fade",
      "fade_in": 0.5,
      "fade_out": 0.5,
      "animation": "zoom_in",
      "background_url": None
      
    },
#     {
#       "media_type": "image",
#       "url": "https://drive.google.com/file/d/1hlFaDtqEN8wqm6-HEKkimpr_d_9g82ZD/view?usp=drivesdk",
#       "overlay_text": "Ugly, damaged nails",
#       "voice_over": "Damaged nails can make you lose confidence.",
#       "duration": 4,
#       "transition": "fade",
#       "fade_in": 0.3,
#       "fade_out": 0.3,
#       "animation": "pan",
#       "background_url": None,
#       "background_music_url": "https://drive.google.com/file/d/1y-0z2zqXXnlfocaFGpud1FDuxxr0DTLj/view?usp=drivesdk"
#     },
#     {
#       "media_type": "image",
#       "url": "https://drive.google.com/file/d/1OJbF59bfS1nvmiBV43ViJj1_DfQajG7J/view?usp=drivesdk",
#       "overlay_text": "Smooth & clean",
#       "voice_over": "With the right tools, your nails can look clean and smooth.",
#       "duration": 5,
#       "transition": "fade",
#       "fade_in": 0.3,
#       "fade_out": 0.3,
#       "animation": "zoom_in",
#       "background_url": None,
#       "background_music_url": "https://drive.google.com/file/d/1y-0z2zqXXnlfocaFGpud1FDuxxr0DTLj/view?usp=drivesdk"
#     },
#     {
#       "media_type": "image",
#       "url": "https://drive.google.com/file/d/1kTxjYUIYEaYAvvVeLl8Mv6uLkBi6pu2I/view?usp=drivesdk",
#       "overlay_text": "Trim & shape",
#       "voice_over": "Trim and shape your nails the right way.",
#       "duration": 4,
#       "transition": "fade",
#       "fade_in": 0.3,
#       "fade_out": 0.3,
#       "animation": "pan",
#       "background_url": None,
#       "background_music_url": "https://drive.google.com/file/d/1y-0z2zqXXnlfocaFGpud1FDuxxr0DTLj/view?usp=drivesdk"
#     },
#     {
#       "media_type": "image",
#       "url": "https://drive.google.com/file/d/1IGZPLIn1g7q72wvPWvN558JHHTfbKxve/view?usp=drivesdk",
#       "overlay_text": "Nourish your cuticles",
#       "voice_over": "Keep your cuticles healthy with nourishing oil.",
#       "duration": 4,
#       "transition": "fade",
#       "fade_in": 0.3,
#       "fade_out": 0.3,
#       "animation": "zoom_in",
#       "background_url": None,
#       "background_music_url": "https://drive.google.com/file/d/1y-0z2zqXXnlfocaFGpud1FDuxxr0DTLj/view?usp=drivesdk"
#     },
#     {
#       "media_type": "image",
#       "url": "https://drive.google.com/file/d/15MY0jk9nQ5ix3BKC5_UF0I5di91pS9k-/view?usp=drivesdk",
#       "overlay_text": "Beautiful, healthy nails",
#       "voice_over": "Enjoy beautiful, healthy looking nails every day.",
#       "duration": 4,
#       "transition": "fade",
#       "fade_in": 0.4,
#       "fade_out": 0.4,
#       "animation": "zoom_in",
#       "background_url": None,
#       "background_music_url": "https://drive.google.com/file/d/1y-0z2zqXXnlfocaFGpud1FDuxxr0DTLj/view?usp=drivesdk"
#     },
#     {
#       "media_type": "image",
#       "url": "https://drive.google.com/file/d/1CGTal8-apfpiC7Qto4ZKMFA8-tMX4z6v/view?usp=drivesdk",
#       "overlay_text": "Get yours today",
#       "voice_over": "Get your complete nail care kit today and feel confident again.",
#       "duration": 4,
#       "transition": "fade",
#       "fade_in": 0.5,
#       "fade_out": 0.5,
#       "animation": "zoom_in",
#       "background_url": None,
#       "background_music_url": "https://drive.google.com/file/d/1y-0z2zqXXnlfocaFGpud1FDuxxr0DTLj/view?usp=drivesdk"
#     }
  ]
}

assets = [
    "media type: image, url: https://drive.google.com/file/d/1Mfo_4itHFt16TFi2C_nYcDU6GV2dRObQ/view?usp=drivesdk, description: image showing smartapplicant.net page where ATS Compatibility scan is processing, no results displayed yet",
    "media type: video, url: https://drive.google.com/file/d/1ensR02kvLKjq--hhL-CWnMLqAshJpiB1/view?usp=drivesdk, description: video showing displayed ATS-compatibility scan results. The screen scrolls down from the score, through all resume sections, down to AI-generated suggestions for improvement. Video is 17 seconds long",
    "media type: image, url: https://drive.google.com/file/d/1kgtTYqpyOCDfgm7xRKOXYS_zhZRFzVMU/view?usp=drivesdk, description: image of smartapplicant.net page showing ATS_compatibility scan button with file already selected.",
    "media type: image, url: https://drive.google.com/file/d/1UTqMTWnpSFZBXcG5qGpIIMzVF_WC10zG/view?usp=drivesdk, description: image of smartapplicant.net page showing ATS_compatibility scan button with No files selected.",
    "media type : image, Url : https://drive.google.com/file/d/1GN-e-t-TEHWlNiSdt3eWeIsY6X2wIdsz/view?usp=drivesdk, Description : image of smartapplicant.net home page. Logo and name, mobile menu button (breadcrumb icon) are visible. Also, a button that says 'Analyze your resume - it's free' is visible as well. This button will take u to ATS-compatibility scan button where they can select their resume and scan for ATS-compatibility score.",
    "media type :image, Url : https://drive.google.com/file/d/1PD_s22pLYf9YAYXJuAUMtL-7LQkPHOVk/view?usp=drivesdk, Description : image of smartapplicant.net logo",
    "media type : audio, Url : https://drive.google.com/file/d/162glnaUtXE44bGDRw2F-0ExdlcAIk7Rt/view?usp=drivesdk, Description: music by 2face idibia title IF LOVE IS A CRIME and it is 4:26 long",
    "media type : audio, url : https://drive.google.com/file/d/16KzWbCeABKlky3U81MwUYHjGCSxsRewS/view?usp=drivesdk, description : song by Alan Walker (remixed) titled FADED and it is 0.37 long",
    "media type : audio, Url : https://drive.google.com/file/d/1P7ERN1sfs-zFVzKoIUAVc-rFE-HbTw_M/view?usp=drivesdk, Description : song by Sean Kingston titled FACE DROP and it's 3.07 long",
    "media type : audio, Url : https://drive.google.com/file/d/13rFQqUbCb66Opy7dSr7LqVsc2jUfKF_C/view?usp=drivesdk, Description : instrumental titled EPIC RISE and it's 2.23 long",
    "media type: image, url: https://drive.google.com/file/d/1O3VNz1PhNdxdljcyCTFbGsWEJph2tevX/view?usp=drivesdk, description: a page on smartapplicant.net showing user statistics and usage statistics"
]
