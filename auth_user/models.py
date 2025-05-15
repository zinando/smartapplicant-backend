from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
# from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

# User = get_user_model()



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

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        abstract = False

    def __str__(self):
        return self.username

User = CustomUser()

class SubscriptionType(models.Model):
    """Model to store different subscription types and their pricing"""
    MONTHLY = 'monthly'
    YEARLY = 'yearly'
    LIFETIME = 'lifetime'
    
    TYPE_CHOICES = [
        (MONTHLY, 'Monthly'),
        (YEARLY, 'Yearly'),
        (LIFETIME, 'Lifetime'),
    ]
    
    name = models.CharField(max_length=20, choices=TYPE_CHOICES, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    duration_days = models.PositiveIntegerField(help_text="Duration in days for this subscription type")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_name_display()} (${self.price})"

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
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s {self.subscription_type.get_name_display()} subscription"

    def save(self, *args, **kwargs):
        """Automatically set expiry_date based on subscription type"""
        if not self.pk:  # Only for new subscriptions
            if self.subscription_type.name == SubscriptionType.LIFETIME:
                self.expiry_date = timezone.now().date() + timedelta(days=365*100)  # 100 years
            else:
                self.expiry_date = timezone.now().date() + timedelta(days=self.subscription_type.duration_days)
            
            # Set payment amount from subscription type price
            self.payment_amount = self.subscription_type.price
        
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        """Determine if subscription is currently active"""
        today = timezone.now().date()
        return self.status == self.ACTIVE and today <= self.expiry_date

    def renew(self):
        """Renew the subscription"""
        today = timezone.now().date()
        if self.is_active and self.is_auto_renew:
            self.start_date = today
            if self.subscription_type.name != SubscriptionType.LIFETIME:
                self.expiry_date = today + timedelta(days=self.subscription_type.duration_days)
            self.save()
            return True
        return False

    class Meta:
        ordering = ['-expiry_date']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['expiry_date']),
        ]