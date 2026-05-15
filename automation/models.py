from django.db import models
from django.utils import timezone
from datetime import timedelta
from fernet_fields import EncryptedTextField

class Tenant(models.Model): # represents a business with a unique phone number and business details
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    waba_id = models.CharField(max_length=100, unique=True)  # WhatsApp Business Account ID
    waba_phone_number = models.CharField(max_length=20, unique=True) # associated phone number
    waba_phone_number_id = models.CharField(max_length=100, unique=True)  # WhatsApp Business Account Phone Number ID
    fb_page_id = models.CharField(max_length=100, null=True, blank=True)  # associated Facebook Page ID
    ig_business_account_id = models.CharField(max_length=100, null=True, blank=True)  # associated Instagram Business Account ID
    tg_bot_username = models.CharField(max_length=100, null=True, blank=True)  # associated Telegram Bot Username
    custom_prompts = models.JSONField(null=True, blank=True)  # custom prompt for content generation: {"platform": "custom prompt"}
    business_details = models.JSONField(null=True, blank=True)  # store additional business info
    content_schedule_times = models.JSONField(null=True, blank=True)  # preferred times to post content {"platform": [7, 9, 12, 15, 18, 21]}
    media_history = models.JSONField(default=list, blank=True)  # list of previously used media IDs {'platform': [{"id": "media_id", "caption": "caption text"}]}
    evergreen_content = models.JSONField(default=list, blank=True)  # list of evergreen text content items, can be used on any platform ["text content 1", "text content 2"]  
    created_at = models.DateTimeField(auto_now_add=True)
    customers = models.JSONField(default=list, blank=True)  # list of customer IDs {"customer ID": "customer name"}

    def __str__(self):
        return self.waba_phone_number_id
    
    def create_slug(self):
        return f'{self.name.lower().replace(" ", "-")}_{self.waba_phone_number_id}'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.create_slug()
        super().save(*args, **kwargs)

class FacebookAuthLog(models.Model):
    state = models.CharField(max_length=256) # generated before step one
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    step = models.CharField(
        max_length=50,
        choices=[
            ("code_request", "Code Request"),
            ("short_lived_token", "Short Lived Token"),
            ("long_lived_token", "Long Lived Token"),
            ("page_token", "Page Token")
        ],
        default="initiated"
    )
    step_status = models.CharField(
        max_length=20,
        choices=[
            ("initiated", "Initiated"),
            ("success", "Success"),
            ("failed", "Failed")
        ],
        default="initiated"
    )
    code = EncryptedTextField(null=True, blank=True)  # returned in step one
    short_lived_token_payload = EncryptedTextField(null=True, blank=True)  # returned in step two
    long_lived_token_payload = EncryptedTextField(null=True, blank=True)  # returned in step three. This step is optional
    page_access_token_payload = EncryptedTextField(null=True, blank=True)  # returned in step four
    message = models.TextField(null=True, blank=True)  # error or success message
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class AutomatedClientManager(models.Manager):
    def get_queryset(self):
        queryset = super().get_queryset()
        for instance in queryset:
            instance.run_subscription_expiry_check()
        return queryset

class AutomatedClients(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='automated_clients')
    auth_log = models.OneToOneField(FacebookAuthLog, on_delete=models.CASCADE, null=True, blank=True, related_name='automated_client')
    platform = models.CharField(max_length=50)  # e.g., "facebook", "instagram"
    client_id = models.CharField(max_length=100)  # e.g., Facebook Page ID or Instagram Business Account ID
    business_details = models.JSONField(null=True, blank=True)  # store additional business info
    media_history = models.JSONField(default=list, blank=True)  # list of previously used media IDs [{"id": "media_id", "caption": "caption text"}]
    evergreen_content = models.JSONField(default=list, blank=True)  # list of evergreen text content items, can be used on any platform ["text content 1", "text content 2"]
    custom_prompts = models.JSONField(null=True, blank=True) # custom prompt for content generation e.g {'txt':'prompt 1', 'txt-img': 'prompt 2', 'txt-img-vid':'prompt 3'}
    content_schedule_times = models.JSONField(null=True, blank=True)  # preferred times to post content [7, 9, 12, 15, 18, 21]
    page_access_token = EncryptedTextField(null=True, blank=True)  # Store access token securely
    token_expires_at = models.DateTimeField(null=True, blank=True)  # Token expiration time
    subscribed = models.BooleanField(default=False)  # Whether the webhook subscription is active
    subscription_ref = models.CharField(max_length=100, null=True, blank=True)  # Subscription reference ID
    subscription_expires_at = models.DateTimeField(null=True, blank=True)  # Subscription expiration time
    saved_content = models.JSONField(default=list, blank=True, null=True)  # content saved for posting later [{"content": "text or media", "content_type": "text/image/link", "caption": "caption text", "comments": []}]
    secret_questions = models.JSONField(null=True, blank=True)  # secret questions set by account owner for authentication purpose before any modification on account information (text)
    subscription_type = models.CharField(max_length=50,
        choices=[
            ("txt", "TXT"),
            ("txt-img", "TXT-IMG"),
            ("txt-img-vid", "TXT-IMG-VID")
        ],
        default="txt"
    )
    video_plan_history = models.JSONField(null=True, blank=True)  # history of video plans so AI doesn't repeat video plan content: [{}...]
    business_assets = models.JSONField(null=True, blank=True)  # store business assets like images and videos E.G ["str1", "str2"]
    default_video_plans = models.JSONField(default=list, blank=True, null=True)  # list of saved video plans [{"video_plan": {...}, "created_at": "datetime"}]
    saved_video_plan= models.JSONField(null=True, blank=True)  # current video plan being worked on {"media_type": "image | video", "url": "string", "overlay_text": "string", "voice_over": "string", "duration": number, "transition": "fade | slide | none", "fade_in": number, "fade_out": number}
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = AutomatedClientManager()

    def __str__(self):
        return f"{self.platform} - {self.client_id}"
    def run_subscription_expiry_check(self):
        """checks if subscription is expired and updates the status"""
        if self.subscription_expires_at and timezone.now() >= self.subscription_expires_at:
            self.subscribed = False
            self.save(update_fields=['subscribed'])

    @property
    def business_name(self):
        return self.business_details.get("name") if self.business_details else "my page name"

class MediaPostLog(models.Model):
    """Keeps track of daily image posts per client"""
    client = models.OneToOneField(AutomatedClients, on_delete=models.CASCADE, related_name='image_post_log')
    image_count = models.IntegerField()
    last_image_posted_at = models.DateTimeField()
    video_count = models.IntegerField()
    last_video_posted_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def has_posted_image_today(self):
        today = timezone.now().date()
        return self.last_image_posted_at.date() == today
    def has_posted_video_today(self):
        today = timezone.now().date()
        return self.last_video_posted_at.date() == today

    
class WebhookEvent(models.Model):
    PLATFORM_CHOICES = [
        ("whatsapp", "WhatsApp"),
        ("facebook", "Facebook"),
        ("instagram", "Instagram"),
        ("telegram", "Telegram"),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True)  # your tenant model
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES, default="whatsapp")
    sender_id = models.CharField(max_length=100, null=True, blank=True)
    sender_name = models.CharField(max_length=255, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    raw = models.JSONField()  # store full payload
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    media_id = models.CharField(max_length=100, null=True, blank=True)
    media_type = models.CharField(max_length=50, null=True, blank=True)
    mime_type = models.CharField(max_length=100, null=True, blank=True)
    caption = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.platform} | {self.sender_id or 'unknown'}"
