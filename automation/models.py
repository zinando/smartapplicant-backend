from django.db import models
from django.utils import timezone
from datetime import timedelta

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

class AutomatedClientManager(models.Manager):
    def get_queryset(self):
        queryset = super().get_queryset()
        for instance in queryset:
            instance.run_subscription_expiry_check()
        return queryset

class AutomatedClients(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    platform = models.CharField(max_length=50)  # e.g., "facebook", "instagram"
    client_id = models.CharField(max_length=100)  # e.g., Facebook Page ID or Instagram Business Account ID
    access_token = models.TextField()  # Store access token securely
    token_expires_at = models.DateTimeField(null=True, blank=True)  # Token expiration time
    subscribed = models.BooleanField(default=False)  # Whether the webhook subscription is active
    subscription_ref = models.CharField(max_length=100, null=True, blank=True)  # Subscription reference ID
    subscription_expires_at = models.DateTimeField(null=True, blank=True)  # Subscription expiration time
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = AutomatedClientManager()

    def __str__(self):
        return f"{self.tenant.name} - {self.platform}"
    def run_subscription_expiry_check(self):
        """checks if subscription is expired and updates the status"""
        if self.subscription_expires_at and timezone.now() >= self.subscription_expires_at:
            self.subscribed = False
            self.save(update_fields=['subscribed'])
    
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
