from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
# from django.contrib.auth import get_user_model
from django.utils import timezone
# from datetime import timedelta
import datetime
import uuid



class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    class HowYouHeardOptions(models.TextChoices):
        EMAIL = "EMAIL", "Email"
        SOCIAL_MEDIA = "SOCIAL", "Social Media"
        SEARCH = "ORGANIC", "Organic"
        REFERRAL = "REFERRAL", "Referral"
        BLOG = "BLOG", "Blog/Content"
        AD = "AD", "Paid Ad"
        OTHER = "OTHER", "Other"
        UNSPECIFIED = "UNSPECIFIED", "Unspecified"

    username = models.CharField(
        max_length=150,
        unique=True,
        error_messages={'unique': 'A user with that username already exists.'},
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
    )
    email = models.EmailField(max_length=254, unique=True, verbose_name='email address')
    first_name = models.CharField(max_length=150, blank=True, verbose_name='first name')
    last_name = models.CharField(max_length=150, blank=True, verbose_name='last name')
    resume_data = models.JSONField(null=True, blank=True, help_text="Store list of resume data in JSON format.")
    phone_number = models.CharField(max_length=15, null=True, blank=True, help_text="Enter your phone number.")
    resume_credits = models.PositiveIntegerField(default=0, help_text="Number of resume credits available for the user.")
    how_you_heard = models.CharField(        max_length=20,
        choices=HowYouHeardOptions.choices,
        default=HowYouHeardOptions.UNSPECIFIED,
        help_text="How the user heard about the service."
    )
    
    # Standard fields
    is_active = models.BooleanField(default=True, help_text='Designates whether this user should be treated as active.')
    is_staff = models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.')
    is_superuser = models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.')
    date_joined = models.DateTimeField(default=timezone.now, verbose_name='date joined')

    # Required permissions
    groups = models.ManyToManyField('auth.Group', blank=True, related_name='user_set', related_query_name='user', verbose_name='groups')
    user_permissions = models.ManyToManyField('auth.Permission', blank=True, related_name='user_set', related_query_name='user', verbose_name='user permissions')

    # Manager
    objects = CustomUserManager()

    # Password and authentication
    USERNAME_FIELD = 'email'  # Use email as the primary identifier
    REQUIRED_FIELDS = ['username', 'company_name']  # Add company_name to required fields for superuser creation

    def save(self, *args, **kwargs):
        # Automatically set the username by extracting the part before '@' in the email
        if not self.username:
            self.username = self.email.split('@')[0]
        super().save(*args, **kwargs)
    
    def is_premium(self):
        """Checks if user has an active subscription or not"""
        active_subs = self.subscriptions.filter(status=Subscription.ACTIVE, expiry_date__gte=timezone.now().date())
        return bool(active_subs)

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        abstract = False

    def __str__(self):
        return self.username

User = CustomUser()

class SubscriptionType(models.Model):
    """Model to store different subscription types and their pricing"""
    
    name = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    duration_days = models.PositiveIntegerField(help_text="Duration in days for this subscription type")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name()} (${self.price})"

    class Meta:
        ordering = ['price']

class Subscription(models.Model):
    """Model to track user subscriptions"""
    ACTIVE = 'active'
    EXPIRED = 'expired'
    CANCELED = 'canceled'
    
    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (EXPIRED, 'Expired'),
        (CANCELED, 'Canceled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    subscription_type = models.ForeignKey(SubscriptionType, on_delete=models.PROTECT, related_name='subscriptions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ACTIVE)
    start_date = models.DateField(default=timezone.now)
    expiry_date = models.DateField()
    is_auto_renew = models.BooleanField(default=True)
    is_renewed = models.BooleanField(default=False, help_text="Indicates if the subscription is renewed or not.")
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s {self.subscription_type.get_name_display()} subscription"

    @property
    def is_active(self):
        """Determine if subscription is currently active"""
        today = timezone.now().date()
        return self.status == self.ACTIVE and today <= self.expiry_date

    # def renew(self):
    #     """Renew the subscription"""
    #     today = timezone.now().date()
    #     if self.is_active and self.is_auto_renew:
    #         self.start_date = today
    #         if self.subscription_type.name != SubscriptionType.LIFETIME:
    #             self.expiry_date = today + timedelta(days=self.subscription_type.duration_days)
    #         self.save()
    #         return True
    #     return False

    class Meta:
        ordering = ['-expiry_date']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['expiry_date']),
        ]

class Order(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"
        FAILED = "FAILED", "Failed"
    class OrderType(models.TextChoices):
        CREDIT = "CREDIT", "Credit"
        SUBSCRIPTION = "SUBSCRIPTION", "Subscription"
    class PaymentMethod(models.TextChoices):
        PAYSTACK = "PAYSTACK", "Paystack"
        FLUTTERWAVE = "FLUTTERWAVE", "Flutterwave"
        STRIPE = "STRIPE", "Stripe"
        RAVE = "RAVE", "Rave"
        PAYPAL = "PAYPAL", "Paypal"
        BANK_TRANSFER = "BANK_TRANSFER", "Bank Transfer"
        CASH_ON_DELIVERY = "CASH_ON_DELIVERY", "Cash on Delivery"
        WALLET = "WALLET", "Wallet"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=50, unique=True, editable=False)
    price= models.FloatField(default=0)
    quantity = models.PositiveIntegerField(default=1, help_text="Total number of resume credits purchased in this order.")
    total = models.FloatField(default=0)
    discount = models.FloatField(default=0)
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders', help_text="Subscription associated with this order, if any.")
    # shipping_cost = models.FloatField(default=0)
    payment_status = models.CharField(choices=PaymentStatus.choices, default=PaymentStatus.PENDING, max_length=20)
    # discount_code = models.CharField(max_length=50, null=True, blank=True)
    # delivery_address = models.TextField(null=True, blank=True)
    # delivery_city = models.CharField(max_length=50, null=True, blank=True)
    # delivery_state = models.CharField(max_length=50, null=True, blank=True)
    # delivery_country = models.CharField(max_length=50, null=True, blank=True)
    # delivery_method = models.CharField(max_length=50, null=True, blank=True)
    # delivery_type = models.CharField(max_length=50, null=True, blank=True)
    # order_status = models.CharField(choices=OrderStatus.choices, default=OrderStatus.PENDING, max_length=20)
    txn_ref = models.CharField(max_length=200, null=True, blank=True)
    order_type = models.CharField(choices=OrderType.choices, default=OrderType.SUBSCRIPTION, max_length=20)
    # redeem_requested = models.BooleanField(default=False)
    # redeem_code = models.CharField(max_length=50, null=True, blank=True)
    payment_method = models.CharField(choices=PaymentMethod.choices, default=PaymentMethod.PAYSTACK, max_length=20)
    # delivery_date = models.DateField(null=True, blank=True)
    delete_flag = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} - {self.total_price}'
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f'ORD-{str(self.user.id)}-{str(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))}'
        super().save(*args, **kwargs)
class UserCards(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='debit_cards')
    card_token = models.CharField(unique=True)
    card_name = models.CharField( max_length=50)
    exp_month = models.CharField( max_length=7)
    exp_year = models.CharField( max_length=7)
    first6 = models.CharField( max_length=7)
    bank = models.CharField( max_length=50)
    is_valid = models.BooleanField(default=True)
    is_disabled= models.BooleanField(default=False)
    rdate= models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.user.username}: {self.card_name} - {self.first6} - {self.exp_month}/{self.exp_year} - {self.bank}'
class PGRequest(models.Model): #payment gateway request log
    class TransactionType(models.TextChoices):
        SUBSCRIPTION = "SUBSCRIPTION", "Subscription"
        CREDIT = "CREDIT", "Credit"
        REFUND = "REFUND", "Refund"
    
    class ResponseStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"
        CANCELLED = "CANCELLED", "Cancelled"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions", null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="transactions")
    user_card = models.ForeignKey(UserCards, on_delete=models.CASCADE, related_name="transactions", null=True, blank=True)
    amount = models.FloatField( default=0)
    ref_id = models.CharField( max_length=100, null=True, blank=True)
    txn_type = models.CharField(choices=TransactionType.choices, default=TransactionType.SUBSCRIPTION, max_length=20)
    customer_email = models.EmailField()
    hook_res_id = models.CharField( max_length=50, null=True, blank=True)
    res_status = models.CharField(choices=ResponseStatus.choices, default=ResponseStatus.PENDING, max_length=20)
    callback_body = models.JSONField(null=True, blank=True)
    txn_verified = models.BooleanField(default=False)
    currency = models.CharField(max_length=10, default='NGN', help_text="Currency code for the transaction, e.g., NGN for Nigerian Naira.")
    hook_check = models.BooleanField(default=False)
    reqhash = models.CharField( max_length=50, null=True, blank=True)
    # contribute_code= models.CharField( max_length=50, null=True, blank=True)
    # personal_message= models.TextField(null=True, blank=True)
    delete_flag = models.BooleanField(default=False)
    rdate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.first_name} - {self.amount} on {self.rdate.strftime("%d-%M-%Y %HH:%MM:%SS")}'
    
    def save(self, *args, **kwargs):
        if not self.ref_id:
            # generate a unique refid with uuid
            if self.user:
                self.ref_id = f'REF-{self.user.id}-{str(uuid.uuid4().hex[:8].upper())}'
            else:
                self.ref_id = f'REF-{str(uuid.uuid4().hex[:8].upper())}'
        super().save(*args, **kwargs)

class PaystackHook(models.Model):
    resp = models.TextField()
    hook_res_id = models.CharField(max_length=50, null=True, blank=True)
    transactionid = models.CharField( max_length=100)
    hookdate = models.DateTimeField(auto_now_add=True)
    hook_verified = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.transactionid} - {self.hookdate.strftime("%d-%M-%Y %HH:%MM:%SS")}- {self.resp}'

# class for storing matched resume data traceable to user
class MatchedResumeData(models.Model):
    class TransactionType(models.TextChoices):
        CREDIT = "CREDIT", "Credit"
        SUBSCRIPTION = "SUBSCRIPTION", "Subscription"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matched_resumes')
    resume_data = models.JSONField(help_text="Matched resume data in JSON format.")
    job_title = models.CharField(max_length=255, default='Job Title', help_text="Title of the job for which the resume was matched.")
    matched_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Matched Resume for {self.user.username} on {self.matched_date.strftime("%Y-%m-%d %H:%M:%S")}'
    
    class Meta:
        ordering = ['-matched_date']
        indexes = [
            models.Index(fields=['user', 'job_title']),
            models.Index(fields=['matched_date']),
        ]

class ResumeDraft(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resume_drafts')
    draft_data = models.JSONField(help_text="Draft resume data in JSON format.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Resume Draft for {self.user.username} created on {self.created_at.strftime("%Y-%m-%d %H:%M:%S")}'
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['created_at']),
        ]