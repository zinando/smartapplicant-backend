from django.urls import path
from .views import SignUpView, LoginView, LogoutView, SubscriptionView, ProfileView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('subscription/', SubscriptionView.as_view()),
    path('profile/', ProfileView.as_view())
]
