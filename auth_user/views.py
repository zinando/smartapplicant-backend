from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from .serializers import UserSerializer
from django.db.models import Q
from api.utils import *
from api.tasks import *
from api.models import GeneralData
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from decimal import Decimal
from .utils import *
from .models import Order, PGRequest, SubscriptionType, Subscription
import os
import requests
from dotenv import load_dotenv

load_dotenv()


User = get_user_model()

class SignUpView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def sanitize_string(self, value):
        """Sanitize a string by removing leading/trailing whitespace and converting to lowercase."""
        if value:
            return value.strip().lower()
        return None
    def normalize_how_you_heard_value(self, value: str) -> str:
        value = self.sanitize_string(value).title() if value else 'Unspecified'
        try:
            # Match input with enum by value or label (case-insensitive)
            return User.HowYouHeardOptions[value.upper()].value
        except KeyError:
            return User.HowYouHeardOptions.UNSPECIFIED
    def create(self, request, *args, **kwargs):
        try:
            email = request.data.get('email')
            password = request.data.get('password')
            phone = request.data.get('phone', None)
            first_name = request.data.get('first_name', None)
            last_name = request.data.get('last_name', None)
            how_you_heard = request.data.get('how_you_heard', 'Unspecified')
            
            if not email or not password:
                raise ValueError("Email and password are required")
            
            # Validate password
            validate_password(password=password)
            
            if User.objects.filter(email=email).exists():
                raise ValueError("Email already exists")
            
            user = User.objects.create(
                email= self.sanitize_string(email),
                password= make_password(password),
                phone_number= self.sanitize_string(phone),
                first_name= self.sanitize_string(first_name).title() if first_name else None,
                last_name= self.sanitize_string(last_name).title() if last_name else None,
                how_you_heard= self.normalize_how_you_heard_value(how_you_heard)
            )

            # update general data table 
            created, gen_obj = GeneralData.objects.get_or_create(
                id = 1,
                defaults= {
                    "ats_score": {},
                    "premium_users": 0,
                    "registered_users": 1,
                    "currently_online": 1
                }
            )
            if not created:
                gen_obj.registered_users += 1
                gen_obj.currently_online += 1
                gen_obj.save() 

            print(f'how_you_heard: {how_you_heard}')
            
            refresh = RefreshToken.for_user(user)
            serializer = self.get_serializer(user)
            data = serializer.data
            return Response({
                'status': 1,
                'message': 'User created successfully',
                'user': data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'status': 0, 'message': str(e)},
                status=status.HTTP_200_OK
            )

class LoginView(TokenObtainPairView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        try:
            if not username or not password:
                raise ValueError("Username and password are required")
            
            user = authenticate(request, username=username, password=password)

            if user is None:
                raise ValueError("Invalid username or password")
            
            refresh = RefreshToken.for_user(user)
            serializer = self.get_serializer(user)
            data = serializer.data
            return Response({
                'status': 1,
                'message': 'Login successful',
                'user': data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'status': 0, 'message': str(e)},
                status=status.HTTP_200_OK
            )

class LogoutView(generics.GenericAPIView):
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            
            if not refresh_token:
                raise ValueError("Refresh token is required")
                
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            # update general stat data
            created, gen_obj = GeneralData.objects.get_or_create(
                id = 1,
                defaults= {
                    "ats_score": {},
                    "premium_users": 0,
                    "registered_users": 1,
                    "currently_online": 0
                }
            )
            if not created:
                if gen_obj.currently_online > 0:
                    gen_obj.currently_online = 1
                gen_obj.save()

            return Response({'status':1, 'message': 'Successfully logged out'},status=status.HTTP_205_RESET_CONTENT)
            
        except Exception as e:
            print(e)
            return Response(
                {'status': 0, 'message': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class ResumeUploadView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        try:
            user = request.user
            file = request.FILES.get('resume')
            title = request.data.get('title')
            
            if not file:
                raise ValueError("Resume file is required")
            
            if file.size > 5 * 1024 * 1024:  # 5MB
                raise Exception("File too large (max 5MB)")
            
            # Read file content into memory
            file_bytes = file.read()

            if file.size > 2 * 1024 * 1024:  # Example: 2MB+ → async
                task = async_extract_and_score.delay(file_bytes, file.name)
                res_status = 2
                data = {
                    'task_id': task.id,
                    'status': 'Processing',
                    'ats_score': None,
                    'required_sections': None
                }
            else:
                result = extract_text(file_bytes, file.name)
                if result['status'] == 0:
                    raise Exception(result['message'])
                
                text = result['text']

                # parse resume text to get data
                parsed_data = parse_resume(text)

                # Calculate ATS optimization score with the parsed data
                ats_score = calculate_ats_score(parsed_data)
                kw_data = get_keyword_coverage(text, title)

                analytics = {}
                analytics['ats_score'] = ats_score
                analytics['parsed_data'] = parsed_data
                analytics['suggestions'] = get_suggestions_for_resume(parsed_data, kw_data)
                analytics['score_comparison'] = compare_ats_score(ats_score)
                analytics['keyword_coverage'] = kw_data
                analytics['score_rating'] = get_resume_score_rating(ats_score)

                mr = {}
                mr['title'] = title.lower()
                mr['last_updated'] = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
                mr['is_active'] = False
                mr['analytics'] = analytics
                mr['resume_text'] = text

                # Add resume data to user profile
                if not add_user_resume_data(user, mr):
                    raise Exception("Resume data already exists")

            serializer = self.get_serializer(user)
            return Response({
                'status': 1,
                'message': 'Resume uploaded successfully',
                'user': serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response(
                {'status': 0, 'message': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def delete(self, request, *args, **kwargs):
        try:
            user = request.user
            resume_id = request.data.get('resume_id')

            if not resume_id:
                raise ValueError("Resume ID is required")
            
            # Check if the resume exists
            if not user.resume_data:
                raise Exception("No resumes found for this user")
            resume = [data for data in user.resume_data if data['id'] == resume_id]
            if not resume:
                raise Exception("Resume not found")
            resume = resume[0]
            # Remove the resume from the user's profile
            user.resume_data.remove(resume)
            user.save()

            # Update the resume IDs
            update_user_resume_data_id(user)

            return Response({
                'status': 1,
                'message': 'Resume deleted successfully',
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(
                {'status': 0, 'message': str(e)},
                status=status.HTTP_200_OK
            )
        
# create a view for analyzing the resume vs job description
class ResumeAnalysisView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        try:
            user = request.user
            resume_id = request.data.get('resume_id')
            job_title = request.data.get('job_title')
            job_description = request.data.get('job_description')

            if not resume_id or not job_description:
                raise ValueError("Resume ID and job description are required")
            
            # Check if the resume exists
            if not user.resume_data:
                raise Exception("No resumes found for this user")
            # print(f'user.resume_data: {user.resume_data}, resume_id: {resume_id}')
            resume = [data for data in user.resume_data if data['id'] == resume_id]
            if not resume:
                raise Exception("Resume not found")
            resume = resume[0]

            # Submit the analysis task
            task = async_match_resume_with_jd.delay(resume["resume_text"], job_description, user.id, job_title)

            return Response({
                'status': 1,
                'message': 'Resume analysis completed successfully',
                'analysis_result': None,
                'task_id': task.id,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'status': 0, 'message': str(e)},
                status=status.HTTP_200_OK
            )

class SubscriptionView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        """This method is used to subscribe"""
        try:
            
            return Response({
                'status': 1,
                'message': 'Resume analysis completed successfully',
                'user': ''
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'status': 0, 'message': str(e)},
                status=status.HTTP_200_OK
            )
    
    def put(self, request, *args, **kwargs):
        """This method is used to update subscription state: autorenewal"""
        try:
            user = request.user
            auto_renew = request.data.get('subscriptionAutoRenewal', None)

            if auto_renew:
                renew_status = 'enabled'
            else:
                renew_status = 'disabled'

            if auto_renew is None:
                raise Exception('Auto renewal state must be provided.')
            
            # Update subscription state
            active_sub = user.subscriptions.filter(status='active')
            if not active_sub:
                raise Exception('No active subscriptions found.')
            
            active_sub[0].is_auto_renew = auto_renew
            active_sub[0].save()
            
            serializer = self.get_serializer(user)

            return Response({
                'status': 1,
                'message': f'Auto renew subscription has been {renew_status} for {user.first_name}.',
                'user': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'status': 0, 'message': str(e)},
                status=status.HTTP_200_OK
            )
    
    def delete(self, request, *args, **kwargs):
        """This method is used to cancel subscription"""
        try:
            
            return Response({
                'status': 1,
                'message': 'Resume analysis completed successfully',
                'user': ''
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'status': 0, 'message': str(e)},
                status=status.HTTP_200_OK
            )

class ProfileView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        """This method is used to update profile information"""
        try:
            user = request.user
            form = request.data

            check = User.objects.filter(~Q(id=user.id),email=form.get('email')).exists()
            if check:
                raise Exception('Email already exists.')
            
            user.email = form.get('email', user.email)
            user.phone_number = form.get('phone', user.phone_number)
            user.first_name = form.get('firstName', user.first_name).title()
            user.last_name = form.get('lastName', user.last_name).title()
            user.save()
            user.username = user.email.split('@')[0]
            user.save()

            serializer = self.get_serializer(user)
            return Response({
                'status': 1,
                'message': 'Profile updated successful.',
                'user': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'status': 0, 'message': str(e)},
                status=status.HTTP_200_OK
            )
    
    def put(self, request, *args, **kwargs):
        """This method is used to change user password."""
        try:
            user = request.user
            password = request.data.get('newPassword')
            oldPassword = request.data.get('currentPassword')

            check = authenticate(request, username=user.username, password=oldPassword)

            if check is None:
                raise ValueError("Current Password is wrong.")
            
            validate_password(password=password)

            user.password = make_password(password)
            user.save()

            serializer = self.get_serializer(user)

            return Response({
                'status': 1,
                'message': f'Password changed successfully.',
                'user': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'status': 0, 'message': str(e)},
                status=status.HTTP_200_OK
            )
    
    def delete(self, request, *args, **kwargs):
        """This method is used to cancel subscription"""
        try:
            
            return Response({
                'status': 1,
                'message': 'Resume analysis completed successfully',
                'user': ''
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'status': 0, 'message': str(e)},
                status=status.HTTP_200_OK
            )

# new resume generator view
class ResumeGeneratorView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        try:
            user = request.user
            resume_data = request.data

            # authenticate the user
            if not user.is_authenticated:
                raise ValueError("User is not authenticated")

            # Generate the new resume
            filename = f"{user.username}_resume.docx"
            task = async_generate_resume.delay(resume_data, filename, user)

            return Response({
                'status': 1,
                'message': 'Resume generation started successfully',
                'task_id': task.id,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'status': 0, 'message': str(e)},
                status=status.HTTP_200_OK
            )
        
class ResumeMatchAndGenerateView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        try:
            user = request.user
            resume_data = request.data

            # authenticate the user
            if not user.is_authenticated:
                raise ValueError("User is not authenticated")
            
            # check if user is a premium user
            serialized_user = self.get_serializer(user).data
            if serialized_user['account_type'] != 'premium' or serialized_user['resume_credits'] <= 0:
                raise Exception('You must be a premium user to generate a matching resume. Please purchase resume credits or subscribe to our premium service.')
            
            # Generate resume text
            resume = [resume for resume in serialized_user['resume_data'] if resume['id'] == resume_data['resume_id']]
            if not resume:
                raise ValueError('Resume not found')
            
            resume_data['resume_text'] = resume[0]['resume_text']

            # Generate the new resume
            filename = f"{user.username}_matched_resume.docx"
            task = async_generate_matching_resume.delay(resume_data, filename, user)

            return Response({
                'status': 1,
                'message': 'Resume generation started successfully',
                'user': self.get_serializer(user).data,
                'task_id': task.id,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'status': 0,
                 'user': self.get_serializer(user).data if user.is_authenticated else None, 
                 'message': str(e)},
                status=status.HTTP_200_OK
            )

# create a view for checking if user is a premium user or not
class PremiumServiceOrderView(generics.GenericAPIView):
    """This view is used to prepare order for premium service"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_premium_cost(self, order_type):
        """Returns the cost of the premium service based on the order type"""
        cost = 0
        subscription_type = SubscriptionType.objects.get(name=order_type)
        if subscription_type:
            cost += int(subscription_type.price)
        return cost
        
    def log_subscription_type(self):
        """This is used to log subscription types applicable to the app"""
        sub_types = [
            {"name":"resume_credit", "price": os.getenv('cost_per_credit_unit'), "description":"Purchase resume credits for premium services."},
            {"name":"one_month_subscription", "price": os.getenv('cost_per_one_month_subscription'), "description":"Subscribe to our premium service for 30 days."},
            {"name":"three_months_subscription", "price": os.getenv('cost_per_three_months_subscription'), "description":"Subscribe to our premium service for 90 days."},
            {"name":"six_months_subscription", "price": os.getenv('cost_per_six_months_subscription'), "description": "Subscribe to our premium service for 180 days."},
            {"name":"one_year_subscription", "price": os.getenv('cost_per_one_year_subscription'), "description": "Subscribe to our premium service for 365 days."}
        ]

        for sub in sub_types:
            # check if subscription type already exists
            if not SubscriptionType.objects.filter(name=sub['name']).exists():
                # determine number of days for sub
                if sub['name'] == 'one_month_subscription':
                    duration = 30
                elif sub['name'] == 'three_months_subscription':
                    duration = 90
                elif sub['name'] == 'six_months_subscription':
                    duration = 180
                elif sub['name'] == 'one_year_subscription':
                    duration = 365
                else:
                    duration = 0

                SubscriptionType.objects.create(
                    name=sub['name'],
                    price=Decimal(sub['price']),
                    description=sub['description'],
                    duration_days=duration
                )
            else:
                # compare prices and update if necessary
                subscription_type = SubscriptionType.objects.get(name=sub['name'])
                if subscription_type.price != Decimal(sub['price']):
                    subscription_type.price = Decimal(sub['price'])
                    subscription_type.save()


    def post(self, request, *args, **kwargs): 
        self.log_subscription_type()
        try:
            user = request.user
            data = request.data
            serialized_user = self.get_serializer(user).data

            # authenticate the user
            if not user.is_authenticated:
                raise ValueError("User is not authenticated")

            # check if user is a premium user
            if serialized_user['account_type'] == 'premium':
                raise Exception('User is already a premium user.')
            
            order_type = data.get('order_type', None)
            if not order_type:
                raise ValueError("Order type is required")
            
            if order_type == 'resume_credit':
                credits = data.get('credits', None)
                if not credits or not isinstance(credits, int) or credits <= 0:
                    raise ValueError("Invalid number of resume credits")
                
                # log the order
                cost = self.get_premium_cost(order_type)
                order = Order.objects.create(
                    user=user,
                    price= cost,
                    quantity=credits,
                    total= float(cost * credits),
                    txn_ref= f'{order_type}-{timezone.now().timestamp()}',  # unique transaction reference
                    order_type='CREDIT'
                )
                # Log the order in PGRequest
                PGRequest.objects.create(
                    user=user,
                    order=order,
                    ref_id=order.txn_ref,  # unique transaction reference
                    amount=order.total,
                    currency= data.get('currency', 'NGN'),
                    txn_type='CREDIT',
                    customer_email=user.email
                )
                
                # prepare order for resume credits
                order_data = {
                    'type': 'resume_credits',
                    'name': user.username,
                    'phone': user.phone_number,
                    'email': user.email,
                    'app': 'Smart Applicant',
                    'reference': order.txn_ref,  # unique transaction reference
                    'amount': order.total,  # in Naira
                    'currency': data.get('currency', 'NGN'),
                    'description': f'Purchase {credits} resume credit units',
                    'paystackPublicKey': os.getenv('PAYSTACK_PUBLIC_KEY')
                }
                return Response({
                    'status': 1,
                    'message': 'Order prepared successfully',
                    'order': order_data
                }, status=status.HTTP_200_OK)
            
            elif order_type in ['one_month_subscription', 'three_months_subscription', 'six_months_subscription', 'one_year_subscription']:
                # log the order
                cost = self.get_premium_cost(order_type)
                order = Order.objects.create(
                    user=user,
                    price= cost,
                    quantity=1,
                    total=float(cost * 1),  # total is the cost for one subscription
                    txn_ref= f'{order_type}-{timezone.now().timestamp()}',  # unique transaction reference
                    order_type='SUBSCRIPTION'
                )
                # Log the order in PGRequest
                PGRequest.objects.create(
                    user=user,
                    order=order,
                    ref_id=order.txn_ref,  # unique transaction reference
                    amount=order.total,
                    currency= data.get('currency', 'NGN'),
                    txn_type='SUBSCRIPTION',
                    customer_email=user.email
                )
                
                # prepare order for subscription
                order_data = {
                    'type': 'subscription',
                    'name': user.username,
                    'phone': user.phone_number,
                    'email': user.email,
                    'app': 'Smart Applicant',
                    'reference': order.txn_ref,  # unique transaction reference
                    'amount': order.total,  # in Naira
                    'currency': data.get('currency', 'NGN'),
                    'description': f'Subscription to {order_type} plan',
                    'paystackPublicKey': os.getenv('PAYSTACK_PUBLIC_KEY')
                }
                return Response({
                    'status': 1,
                    'message': 'Order prepared successfully',
                    'order': order_data
                }, status=status.HTTP_200_OK)
            
            else:
                raise ValueError("Invalid order type. Must be one of: resume_credit, one_month_subscription, three_months_subscription, six_months_subscription, one_year_subscription")
        except Exception as e:
            return Response(
                {'status': 0, 'message': str(e)},
                status=status.HTTP_200_OK
            )

# class view for verifying paystack payment
class PremiumServiceOrderVerificationView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            reference = kwargs.get('reference', None)

            if not reference:
                raise ValueError("Transaction reference is required")
            
            # Verify the payment with Paystack API
            verification = self.verify_paystack_payment(reference)
            if not verification['status']:
                raise Exception(verification['message'])
            
            # update the PGRequest object
            txn = PGRequest.objects.get(ref_id=reference)
            txn.res_status = verification['data']['status'].upper()
            txn.callback_body = verification['data']
            txn.txn_verified = verification['status']
            txn.save()

            order_type = reference.split('-')[0]  # Extract order type from reference
            order = Order.objects.get(txn_ref=reference)

            # update the order payment status
            order.payment_status = 'PAID'
            order.save()
            
            if order.order_type == 'CREDIT':
                user.resume_credits += order.quantity 
                user.save()
                message = f"You have successfully purchased {order.quantity} resume credit units."
            elif order.order_type == 'SUBSCRIPTION':
                # Activate the subscription for the user
                self.activate_user_subscription(user, order, order_type)
                message = f"You have successfully subscribed to {order_type} plan."
            
            return Response({
                'status': 1,
                'message': message,
                'user': self.get_serializer(user).data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'status': 0, 'message': str(e)},
                status=status.HTTP_200_OK
            )
    
    def verify_paystack_payment(self, txn_reference):
        url = f"https://api.paystack.co/transaction/verify/{txn_reference}"
        
        headers = {
            "Authorization": f"Bearer {os.getenv('PAYSTACK_SECRETE_KEY')}",
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)

        data = {
                    "status": False,
                    "message": "Verification failed",
                    "data": {}
                }

        if response.status_code == 200:
            data = response.json()
            if data['status']:
                data['data']['amount'] = data['data']['amount'] / 100
                # check if the amount is correct
                txn = PGRequest.objects.get(ref_id=txn_reference)
                if txn.amount == data['data']['amount']:
                    data['status'] = True
                    data['message'] = "Verification successful"
                else:
                    data['message'] = "Amount mismatch"
                    data['status'] = False
        else:
            data['message'] = response.text
        return data
    
    def activate_user_subscription(self, user, order, subscription_plan):
        """Activates subscription for user"""
        # Log subscription for user if none exists
        subscription_type = SubscriptionType.objects.get(name=subscription_plan)

        if not user.subscriptions.filter(subscription_type=subscription_type).exists():
            subscription = Subscription.objects.create(
                user = user,
                subscription_type = subscription_type,
                status= 'active',
                start_date = timezone.now(),
                expiry_date = timezone.now() + timezone.timedelta(days=subscription_type.duration_days),
                payment_amount = Decimal(order.price),
            )
        else:
            # update existing record
            subscription = user.subscriptions.get(subscription_type=subscription_type)
            subscription.status = 'active'
            subscription.start_date = timezone.now()
            subscription.expiry_date = timezone.now() + timezone.timedelta(days=subscription_type.duration_days)
            subscription.payment_amount = Decimal(order.price)
            subscription.is_renewed = True
            subscription.save()
        
        # update order
        order.subscription = subscription
        order.save()
