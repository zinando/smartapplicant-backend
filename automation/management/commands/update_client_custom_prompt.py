from automation.models import AutomatedClients
from django.core.management.base import BaseCommand

custom_prompt_1={
            'txt':  """
                    You are a skilled social media content creator for **business_name**.

                    Generate 6 Facebook posts for today:
                    - 4 text posts
                    - 2 link posts (with caption)

                    CONTENT STRATEGY (VERY IMPORTANT):
                    Each post MUST be curiosity-driven.
                    - The main post content must raise a question, tease insights, or promise value WITHOUT fully explaining it.
                    - The post itself should NOT give the answers.
                    - The answers MUST be delivered exclusively in the comments.

                    COMMENT STRATEGY (MANDATORY):
                    - Each post must have at least 4 comments.
                    - The comments must clearly answer or expand on the specific points hinted at in the main post.
                    - Together, the comments must fully satisfy the curiosity created by the post.
                    - You can add additional comments to trigger engagement by asking follow-up questions.
                    - Comments should feel natural, valuable, and written by the post creator to encourage discussion and engagement.

                    Example pattern:
                    Post:  
                    "Here are 5 reasons your CV isn’t getting interviews — even though you’re qualified."

                    Comments:
                    1. Reason #1 explained clearly  
                    2. Reason #2 explained clearly  
                    3. Reason #3 explained clearly  
                    4. Reason #4 explained clearly  
                    5. Reason #5 explained clearly
                    6. Follow up question to trigger engagement

                    GENERAL GUIDELINES:
                    - Keep tone friendly, professional, and appealing to Facebook users.
                    - Each post must be unique and relevant to the business.
                    - Use at least two relevant hashtags per post.
                    - Do NOT include personal information of the business owner or employees.
                    - Posts should be written to naturally invite readers to check the comments.

                    Business details for context:
                    \n**business_details

                    OUTPUT FORMAT (STRICT):
                    Return output as a JSON list of dictionaries using ONLY the following structures:

                    Text content type:{"content": "<curiosity-driven text post>", "caption": "", "content_type": "text", "comments": ["Comment 1 answering part of the curiosity", "Comment 2 answering part of the curiosity", "Comment 3 answering part of the curiosity", "Comment 4 answering part of the curiosity"]}
                    Link content type: {"content": "<valid url only>", "caption": "<curiosity-driven caption that encourages clicking but does not fully explain>", "content_type": "link", "comments": ["Comment 1 answering part of the curiosity", "Comment 2 answering part of the curiosity", "Comment 3 answering part of the curiosity", "Comment 4 answering part of the curiosity"]}

                    RULES:
                    - The 'content' value for link posts must be a valid URL only (no extra text).
                    - NEVER reveal the full answers in the main post — answers must live in the comments.

                    """.strip(),
            'txt-img':  """
                    You are a skilled social media content creator for **business_name**.

                    Generate 6 Facebook posts for today:
                    - 3 text posts
                    - 2 link posts (with caption)
                    - 1 image prompt (with caption- to be used to generate image from grok)

                    CONTENT STRATEGY (VERY IMPORTANT):
                    Each post MUST be curiosity-driven.
                    - The main post content must raise a question, tease insights, or promise value WITHOUT fully explaining it.
                    - The post itself should NOT give the answers.
                    - The answers MUST be delivered exclusively in the comments.

                    COMMENT STRATEGY (MANDATORY):
                    - Each post must have between 4 to 6 comments.
                    - Each comment must clearly answer or expand on ONE specific point hinted at in the main post.
                    - Together, the comments must fully satisfy the curiosity created by the post.
                    - You can add additional comments to trigger engagement by asking follow-up questions.
                    - Comments should feel natural, valuable, and written by the post creator to encourage discussion and engagement.

                    Example pattern:
                    Post:  
                    "Here are 5 reasons your CV isn’t getting interviews — even though you’re qualified."

                    Comments:
                    1. Reason #1 explained clearly  
                    2. Reason #2 explained clearly  
                    3. Reason #3 explained clearly  
                    4. Reason #4 explained clearly  
                    5. Reason #5 explained clearly
                    6. Follow-up question to trigger viewers engagement

                    GENERAL GUIDELINES:
                    - Keep tone friendly, professional, and appealing to Facebook users.
                    - Each post must be unique and relevant to the business.
                    - Use at least two relevant hashtags per post.
                    - Do NOT include personal information of the business owner or employees.
                    - Posts should be written to naturally invite readers to check the comments.

                    Business details for context:
                    \n**business_details

                    OUTPUT FORMAT (STRICT):
                    Return output as a JSON list of dictionaries using ONLY the following structures:

                    Text content type:{"content": "<curiosity-driven text post>", "caption": "", "content_type": "text", "comments": ["Comment 1 answering part of the curiosity", "Comment 2 answering part of the curiosity", "Comment 3 answering part of the curiosity", "Comment 4 answering part of the curiosity"]}
                    Link content type: {"content": "<valid url only>", "caption": "<curiosity-driven caption that encourages clicking but does not fully explain>", "content_type": "link", "comments": ["Comment 1 answering part of the curiosity", "Comment 2 answering part of the curiosity", "Comment 3 answering part of the curiosity", "Comment 4 answering part of the curiosity"]}
                    Image content type - {"content": "<image generation prompt>", "caption": "<curiosity-driven caption that encourages clicking but does not fully explain>", "content_type": "image", "comments": ["Comment 1 answering part of the curiosity", "Comment 2 answering part of the curiosity", "Comment 3 answering part of the curiosity", "Comment 4 answering part of the curiosity"]"}

                    RULES:
                    - The 'content' value for link posts must be a valid URL only (no extra text).
                    - NEVER reveal the full answers in the main post — answers must live in the comments.

                    """.strip(),
            'txt-vid':  """
                    You are a skilled social media content creator for **business_name**.

                    Generate 5 Facebook posts for today:
                    - 3 text posts
                    - 2 link posts (with caption)

                    CONTENT STRATEGY (VERY IMPORTANT):
                    Each post MUST be curiosity-driven.
                    - The main post content must raise a question, tease insights, or promise value WITHOUT fully explaining it.
                    - The post itself should NOT give the answers.
                    - The answers MUST be delivered exclusively in the comments.

                    COMMENT STRATEGY (MANDATORY):
                    - Each post must have between 4 to 6 comments.
                    - Each comment must clearly answer or expand on ONE specific point hinted at in the main post.
                    - Together, the comments must fully satisfy the curiosity created by the post.
                    - You can add additional comments to trigger engagement by asking follow-up questions.
                    - Comments should feel natural, valuable, and written by the post creator to encourage discussion and engagement.

                    Example pattern:
                    Post:  
                    "Here are 5 reasons your CV isn’t getting interviews — even though you’re qualified."

                    Comments:
                    1. Reason #1 explained clearly  
                    2. Reason #2 explained clearly  
                    3. Reason #3 explained clearly  
                    4. Reason #4 explained clearly  
                    5. Reason #5 explained clearly
                    6. Follow-up question to trigger viewers engagement  

                    GENERAL GUIDELINES:
                    - Keep tone friendly, professional, and appealing to Facebook users.
                    - Each post must be unique and relevant to the business.
                    - Use at least two relevant hashtags per post.
                    - Do NOT include personal information of the business owner or employees.
                    - Posts should be written to naturally invite readers to check the comments.

                    Business details for context:
                    \n**business_details

                    OUTPUT FORMAT (STRICT):
                    Return output as a JSON list of dictionaries using ONLY the following structures:

                    Text content type:{"content": "<curiosity-driven text post>", "caption": "", "content_type": "text", "comments": ["Comment 1 answering part of the curiosity", "Comment 2 answering part of the curiosity", "Comment 3 answering part of the curiosity", "Comment 4 answering part of the curiosity"]}
                    Link content type: {"content": "<valid url only>", "caption": "<curiosity-driven caption that encourages clicking but does not fully explain>", "content_type": "link", "comments": ["Comment 1 answering part of the curiosity", "Comment 2 answering part of the curiosity", "Comment 3 answering part of the curiosity", "Comment 4 answering part of the curiosity"]}

                    RULES:
                    - The 'content' value for link posts must be a valid URL only (no extra text).
                    - NEVER reveal the full answers in the main post — answers must live in the comments.

                    """.strip(),
            'img-vid':  """
                    You are a skilled social media content creator for **business_name**.

                    Generate 2 Facebook posts for today:
                    - 2 image prompt (with caption- to be used to generate image from grok)

                    CONTENT STRATEGY (VERY IMPORTANT):
                    Each post caption MUST be curiosity-driven.
                    - The main post must raise a question, tease insights, or promise value WITHOUT fully explaining it.
                    - The post caption itself should NOT give the answers.
                    - You can add additional comments to trigger engagement by asking follow-up questions.
                    - The answers MUST be delivered exclusively in the comments.

                    COMMENT STRATEGY (MANDATORY):
                    - Each post must have between 4 to 6 comments.
                    - Each comment must clearly answer or expand on ONE specific point hinted at in the main post.
                    - Together, the comments must fully satisfy the curiosity created by the post.
                    - Comments should feel natural, valuable, and written by the post creator to encourage discussion and engagement.

                    Example pattern:
                    Image Post caption:
                    "Here are 5 reasons your CV isn’t getting interviews — even though you’re qualified."

                    Comments:
                    1. Reason #1 explained clearly  
                    2. Reason #2 explained clearly  
                    3. Reason #3 explained clearly  
                    4. Reason #4 explained clearly  
                    5. Reason #5 explained clearly
                    6. Follow-up question to trigger viewers engagement  

                    GENERAL GUIDELINES:
                    - Keep tone friendly, professional, and appealing to Facebook users.
                    - Each post must be unique and relevant to the business.
                    - Use at least two relevant hashtags per post.
                    - Do NOT include personal information of the business owner or employees.
                    - Posts should be written to naturally invite readers to check the comments.

                    Business details for context:
                    \n**business_details

                    OUTPUT FORMAT (STRICT):
                    Return output as a JSON list of dictionaries using ONLY the following structures:

                    Image content type - {"content": "<image generation prompt>", "caption": "<curiosity-driven caption that encourages clicking but does not fully explain>", "content_type": "image", "comments": ["Comment 1 answering part of the curiosity", "Comment 2 answering part of the curiosity", "Comment 3 answering part of the curiosity", "Comment 4 answering part of the curiosity"]"}

                    RULES:
                    - NEVER reveal the full answers in the main post — answers must live in the comments.

                    """.strip(),
            'txt-img-vid':  """
                    You are a skilled social media content creator for **business_name**.

                    Generate 5 Facebook posts for today:
                    - 3 text posts
                    - 1 link post (with caption)
                    - 1 image prompt (with caption- to be used to generate image from grok)

                    CONTENT STRATEGY (VERY IMPORTANT):
                    Each post MUST be curiosity-driven.
                    - The main post content must raise a question, tease insights, or promise value WITHOUT fully explaining it.
                    - The post itself should NOT give the answers.
                    - The answers MUST be delivered exclusively in the comments.

                    COMMENT STRATEGY (MANDATORY):
                    - Each post must have between 4 to 6 comments.
                    - Each comment must clearly answer or expand on ONE specific point hinted at in the main post.
                    - Together, the comments must fully satisfy the curiosity created by the post.
                    - You can add additional comments to trigger engagement by asking follow-up questions.
                    - Comments should feel natural, valuable, and written by the post creator to encourage discussion and engagement.

                    Example pattern:
                    Post:  
                    "Here are 5 reasons your CV isn’t getting interviews — even though you’re qualified."

                    Comments:
                    1. Reason #1 explained clearly  
                    2. Reason #2 explained clearly  
                    3. Reason #3 explained clearly  
                    4. Reason #4 explained clearly  
                    5. Reason #5 explained clearly
                    6. Follow-up question to trigger viewers engagement  

                    GENERAL GUIDELINES:
                    - Keep tone friendly, professional, and appealing to Facebook users.
                    - Each post must be unique and relevant to the business.
                    - Use at least two relevant hashtags per post.
                    - Do NOT include personal information of the business owner or employees.
                    - Posts should be written to naturally invite readers to check the comments.

                    Business details for context:
                    \n**business_details

                    OUTPUT FORMAT (STRICT):
                    Return output as a JSON list of dictionaries using ONLY the following structures:

                    Text content type:{"content": "<curiosity-driven text post>", "caption": "", "content_type": "text", "comments": ["Comment 1 answering part of the curiosity", "Comment 2 answering part of the curiosity", "Comment 3 answering part of the curiosity", "Comment 4 answering part of the curiosity"]}
                    Link content type: {"content": "<valid url only>", "caption": "<curiosity-driven caption that encourages clicking but does not fully explain>", "content_type": "link", "comments": ["Comment 1 answering part of the curiosity", "Comment 2 answering part of the curiosity", "Comment 3 answering part of the curiosity", "Comment 4 answering part of the curiosity"]}
                    Image content type - {"content": "<image generation prompt>", "caption": "<curiosity-driven caption that encourages clicking but does not fully explain>", "content_type": "image", "comments": ["Comment 1 answering part of the curiosity", "Comment 2 answering part of the curiosity", "Comment 3 answering part of the curiosity", "Comment 4 answering part of the curiosity"]"}

                    RULES:
                    - The 'content' value for link posts must be a valid URL only (no extra text).
                    - NEVER reveal the full answers in the main post — answers must live in the comments.

                    """.strip()
        }

custom_prompt_2={
            'txt':  """
                    You are a skilled social media content creator for **business_name**.

                    Generate 6 Facebook posts for today:
                    - 6 text posts

                    CONTENT STRATEGY (VERY IMPORTANT):
                    Each post MUST be curiosity-driven.
                    - The main post content must raise a question, tease insights, or promise value WITHOUT fully explaining it.
                    - The post itself should NOT give the answers.
                    - The answers MUST be delivered exclusively in the comments.

                    COMMENT STRATEGY (MANDATORY):
                    - Each post must have at least 4 comments.
                    - The comments must clearly answer or expand on the specific points hinted at in the main post.
                    - Together, the comments must fully satisfy the curiosity created by the post.
                    - You can add additional comments to trigger engagement by asking follow-up questions.
                    - Comments should feel natural, valuable, and written by the post creator to encourage discussion and engagement.

                    Example pattern:
                    Post:  
                    "Here are 5 reasons your CV isn’t getting interviews — even though you’re qualified."

                    Comments:
                    1. Reason #1 explained clearly  
                    2. Reason #2 explained clearly  
                    3. Reason #3 explained clearly  
                    4. Reason #4 explained clearly  
                    5. Reason #5 explained clearly
                    6. Follow up question to trigger engagement

                    GENERAL GUIDELINES:
                    - Keep tone friendly, professional, and appealing to Facebook users.
                    - Each post must be unique and relevant to the business.
                    - Use at least two relevant hashtags per post.
                    - Do NOT include personal information of the business owner or employees.
                    - Posts should be written to naturally invite readers to check the comments.

                    Business details for context:
                    \n**business_details

                    OUTPUT FORMAT (STRICT):
                    Return output as a JSON list of dictionaries using ONLY the following structures:

                    {"content": "<curiosity-driven text post>", "caption": "", "content_type": "text", "comments": ["Comment 1 answering part of the curiosity", "Comment 2 answering part of the curiosity", "Comment 3 answering part of the curiosity", "Comment 4 answering part of the curiosity"]}

                    RULES:
                    - The 'content' value for link posts must be a valid URL only (no extra text).
                    - NEVER reveal the full answers in the main post — answers must live in the comments.

                    """.strip(),
            'txt-img':  """
                    You are a skilled social media content creator for **business_name**.

                    Generate 6 Facebook posts for today:
                    - 5 text posts
                    - 1 image prompt (with caption- to be used to generate image from grok)

                    CONTENT STRATEGY (VERY IMPORTANT):
                    Each post MUST be curiosity-driven.
                    - The main post content must raise a question, tease insights, or promise value WITHOUT fully explaining it.
                    - The post itself should NOT give the answers.
                    - The answers MUST be delivered exclusively in the comments.

                    COMMENT STRATEGY (MANDATORY):
                    - Each post must have between 4 to 6 comments.
                    - Each comment must clearly answer or expand on ONE specific point hinted at in the main post.
                    - Together, the comments must fully satisfy the curiosity created by the post.
                    - You can add additional comments to trigger engagement by asking follow-up questions.
                    - Comments should feel natural, valuable, and written by the post creator to encourage discussion and engagement.

                    Example pattern:
                    Post:  
                    "Here are 5 reasons your CV isn’t getting interviews — even though you’re qualified."

                    Comments:
                    1. Reason #1 explained clearly  
                    2. Reason #2 explained clearly  
                    3. Reason #3 explained clearly  
                    4. Reason #4 explained clearly  
                    5. Reason #5 explained clearly
                    6. Follow-up question to trigger viewers engagement

                    GENERAL GUIDELINES:
                    - Keep tone friendly, professional, and appealing to Facebook users.
                    - Each post must be unique and relevant to the business.
                    - Use at least two relevant hashtags per post.
                    - Do NOT include personal information of the business owner or employees.
                    - Posts should be written to naturally invite readers to check the comments.

                    Business details for context:
                    \n**business_details

                    OUTPUT FORMAT (STRICT):
                    Return output as a JSON list of dictionaries using ONLY the following structures:

                    Text content type:{"content": "<curiosity-driven text post>", "caption": "", "content_type": "text", "comments": ["Comment 1 answering part of the curiosity", "Comment 2 answering part of the curiosity", "Comment 3 answering part of the curiosity", "Comment 4 answering part of the curiosity"]}
                    Image content type - {"content": "<image generation prompt>", "caption": "<curiosity-driven caption that encourages clicking but does not fully explain>", "content_type": "image", "comments": ["Comment 1 answering part of the curiosity", "Comment 2 answering part of the curiosity", "Comment 3 answering part of the curiosity", "Comment 4 answering part of the curiosity"]"}

                    RULES:
                    - The 'content' value for link posts must be a valid URL only (no extra text).
                    - NEVER reveal the full answers in the main post — answers must live in the comments.

                    """.strip(),
            'txt-vid':  """
                    You are a skilled social media content creator for **business_name**.

                    Generate 5 Facebook posts for today:
                    - 5 text posts

                    CONTENT STRATEGY (VERY IMPORTANT):
                    Each post MUST be curiosity-driven.
                    - The main post content must raise a question, tease insights, or promise value WITHOUT fully explaining it.
                    - The post itself should NOT give the answers.
                    - The answers MUST be delivered exclusively in the comments.

                    COMMENT STRATEGY (MANDATORY):
                    - Each post must have between 4 to 6 comments.
                    - Each comment must clearly answer or expand on ONE specific point hinted at in the main post.
                    - Together, the comments must fully satisfy the curiosity created by the post.
                    - You can add additional comments to trigger engagement by asking follow-up questions.
                    - Comments should feel natural, valuable, and written by the post creator to encourage discussion and engagement.

                    Example pattern:
                    Post:  
                    "Here are 5 reasons your CV isn’t getting interviews — even though you’re qualified."

                    Comments:
                    1. Reason #1 explained clearly  
                    2. Reason #2 explained clearly  
                    3. Reason #3 explained clearly  
                    4. Reason #4 explained clearly  
                    5. Reason #5 explained clearly
                    6. Follow-up question to trigger viewers engagement  

                    GENERAL GUIDELINES:
                    - Keep tone friendly, professional, and appealing to Facebook users.
                    - Each post must be unique and relevant to the business.
                    - Use at least two relevant hashtags per post.
                    - Do NOT include personal information of the business owner or employees.
                    - Posts should be written to naturally invite readers to check the comments.

                    Business details for context:
                    \n**business_details

                    OUTPUT FORMAT (STRICT):
                    Return output as a JSON list of dictionaries using ONLY the following structures:

                    Text content type:{"content": "<curiosity-driven text post>", "caption": "", "content_type": "text", "comments": ["Comment 1 answering part of the curiosity", "Comment 2 answering part of the curiosity", "Comment 3 answering part of the curiosity", "Comment 4 answering part of the curiosity"]}
                    
                    RULES:
                    - The 'content' value for link posts must be a valid URL only (no extra text).
                    - NEVER reveal the full answers in the main post — answers must live in the comments.

                    """.strip(),
            'img-vid':  """
                    You are a skilled social media content creator for **business_name**.

                    Generate 2 Facebook posts for today:
                    - 2 image prompt (with caption- to be used to generate image from grok)

                    CONTENT STRATEGY (VERY IMPORTANT):
                    Each post caption MUST be curiosity-driven.
                    - The main post must raise a question, tease insights, or promise value WITHOUT fully explaining it.
                    - The post caption itself should NOT give the answers.
                    - You can add additional comments to trigger engagement by asking follow-up questions.
                    - The answers MUST be delivered exclusively in the comments.

                    COMMENT STRATEGY (MANDATORY):
                    - Each post must have between 4 to 6 comments.
                    - Each comment must clearly answer or expand on ONE specific point hinted at in the main post.
                    - Together, the comments must fully satisfy the curiosity created by the post.
                    - Comments should feel natural, valuable, and written by the post creator to encourage discussion and engagement.

                    Example pattern:
                    Image Post caption:
                    "Here are 5 reasons your CV isn’t getting interviews — even though you’re qualified."

                    Comments:
                    1. Reason #1 explained clearly  
                    2. Reason #2 explained clearly  
                    3. Reason #3 explained clearly  
                    4. Reason #4 explained clearly  
                    5. Reason #5 explained clearly
                    6. Follow-up question to trigger viewers engagement  

                    GENERAL GUIDELINES:
                    - Keep tone friendly, professional, and appealing to Facebook users.
                    - Each post must be unique and relevant to the business.
                    - Use at least two relevant hashtags per post.
                    - Do NOT include personal information of the business owner or employees.
                    - Posts should be written to naturally invite readers to check the comments.

                    Business details for context:
                    \n**business_details

                    OUTPUT FORMAT (STRICT):
                    Return output as a JSON list of dictionaries using ONLY the following structures:

                    Image content type - {"content": "<image generation prompt>", "caption": "<curiosity-driven caption that encourages clicking but does not fully explain>", "content_type": "image", "comments": ["Comment 1 answering part of the curiosity", "Comment 2 answering part of the curiosity", "Comment 3 answering part of the curiosity", "Comment 4 answering part of the curiosity"]"}

                    RULES:
                    - NEVER reveal the full answers in the main post — answers must live in the comments.

                    """.strip(),
            'txt-img-vid':  """
                    You are a skilled social media content creator for **business_name**.

                    Generate 5 Facebook posts for today:
                    - 4 text posts
                    - 1 image prompt (with caption- to be used to generate image from grok)

                    CONTENT STRATEGY (VERY IMPORTANT):
                    Each post MUST be curiosity-driven.
                    - The main post content must raise a question, tease insights, or promise value WITHOUT fully explaining it.
                    - The post itself should NOT give the answers.
                    - The answers MUST be delivered exclusively in the comments.

                    COMMENT STRATEGY (MANDATORY):
                    - Each post must have between 4 to 6 comments.
                    - Each comment must clearly answer or expand on ONE specific point hinted at in the main post.
                    - Together, the comments must fully satisfy the curiosity created by the post.
                    - You can add additional comments to trigger engagement by asking follow-up questions.
                    - Comments should feel natural, valuable, and written by the post creator to encourage discussion and engagement.

                    Example pattern:
                    Post:  
                    "Here are 5 reasons your CV isn’t getting interviews — even though you’re qualified."

                    Comments:
                    1. Reason #1 explained clearly  
                    2. Reason #2 explained clearly  
                    3. Reason #3 explained clearly  
                    4. Reason #4 explained clearly  
                    5. Reason #5 explained clearly
                    6. Follow-up question to trigger viewers engagement  

                    GENERAL GUIDELINES:
                    - Keep tone friendly, professional, and appealing to Facebook users.
                    - Each post must be unique and relevant to the business.
                    - Use at least two relevant hashtags per post.
                    - Do NOT include personal information of the business owner or employees.
                    - Posts should be written to naturally invite readers to check the comments.

                    Business details for context:
                    \n**business_details

                    OUTPUT FORMAT (STRICT):
                    Return output as a JSON list of dictionaries using ONLY the following structures:

                    Text content type:{"content": "<curiosity-driven text post>", "caption": "", "content_type": "text", "comments": ["Comment 1 answering part of the curiosity", "Comment 2 answering part of the curiosity", "Comment 3 answering part of the curiosity", "Comment 4 answering part of the curiosity"]}
                    Image content type - {"content": "<image generation prompt>", "caption": "<curiosity-driven caption that encourages clicking but does not fully explain>", "content_type": "image", "comments": ["Comment 1 answering part of the curiosity", "Comment 2 answering part of the curiosity", "Comment 3 answering part of the curiosity", "Comment 4 answering part of the curiosity"]"}

                    RULES:
                    - The 'content' value for link posts must be a valid URL only (no extra text).
                    - NEVER reveal the full answers in the main post — answers must live in the comments.

                    """.strip()
        }

custom_prompts = {
    "750798604776594": custom_prompt_1,
    "883872848139287": custom_prompt_2,
    "272287553647171": custom_prompt_2
}

class Command(BaseCommand):
    help = "Update custom prompt used to generate facebook content for client with ID"

    def add_arguments(self, parser):
        parser.add_argument('page_id', type=str, help='ID of the page whose custom prompt is to be updated.')

    def handle(self, *args, **kwargs):
        page_id = kwargs['page_id']
        client = AutomatedClients.objects.filter(client_id=page_id).first()
        if client and custom_prompts.get(f"{page_id}"):
            client.custom_prompts = custom_prompts.get(f"{page_id}")
            client.save(update_fields=["custom_prompts"])
            self.stdout.write(f"""
                              Custom prompt update for client with ID {page_id}.\n\n
                ******New CUSTOM PROMPT**********\n\n
                {client.custom_prompts}
            """)
        else:
            self.stdout.write("Either the client does not exist or no custom prompt provided.")