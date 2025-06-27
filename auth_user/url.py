from django.urls import path
from .views import (SignUpView, LoginView, LogoutView, SubscriptionView, 
                    ProfileView, PremiumServiceOrderView, PremiumServiceOrderVerificationView,
                    AdminChangePasswordView, RequestPasswordResetView)

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('subscription/', SubscriptionView.as_view()),
    path('profile/', ProfileView.as_view()),
    path('premium-service/order/', PremiumServiceOrderView.as_view()),
    path('premium-service/verify-order/<reference>/', PremiumServiceOrderVerificationView.as_view()),
    path('change-user-password/<email>/', AdminChangePasswordView.as_view()),
    path('request-password-reset/<email>/', RequestPasswordResetView.as_view()),
    # path('resumes/generate/', ResumeGeneratorView.as_view(), name='resume-generator'),
]
