from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Subscription, SubscriptionType
from django.utils import timezone


class SubscriptionTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubscriptionType()
        fields = '__all__'

class SubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription()
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    date_joined = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    subscriptions = serializers.SerializerMethodField()
    account_type = serializers.SerializerMethodField()
    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'resume_data', 'phone_number', 'date_joined', 
                  'is_active', 'is_staff', 'is_superuser', 'first_name', 'last_name', 'username',
                  'subscriptions', 'account_type'
                  ]
        
    def get_account_type(self, obj):
        """Checks if user has an active subscription or not"""
        acct_type = 'basic'
        # Get all active subscriptions for a user
        active_subs = obj.subscriptions.filter(status='active', expiry_date__gte=timezone.now().date())
        if active_subs:
            acct_type = 'premium'
        
        # print(acct_type)
        return acct_type
    
    def get_subscriptions(self, obj):
        """Returns a single subscription info object"""
        object = {
            'status': 'active',
            'type': 'monthly',
            'lastPaymentDate': '2023-10-15',
            'amount': '₦2500.00',
            'expiryDate': '2023-11-15',
            'renewalAmount': '₦2500.00',
            'is_auto_renew': True
        }
        active_subs = obj.subscriptions.filter(status='active', expiry_date__gte=timezone.now().date())
        if active_subs:
            active_sub = active_subs[0]
            object['status'] = 'active' if active_sub.is_active else active_sub.status
            object['type'] = active_sub.subscription_type.name
            object['lastPaymentDate'] = active_sub.start_date.strftime('%Y-%m-%d')
            object['amount'] = f'₦{active_sub.payment_amount}'
            object['expiryDate'] = active_sub.expiry_date.strftime('%Y-%m-%d')
            object['renewalAmount'] = f'₦{active_sub.subscription_type.price}'
            object['is_auto_renew'] = active_sub.is_auto_renew
        
        return object