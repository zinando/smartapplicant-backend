from django.urls import path
from . import views

urlpatterns = [
    path("webhook/", views.webhook_entry, name="automation-webhook"),
    path("webhook", views.webhook_entry, name="automation-webhook"),
    path('prompt_ai/', views.AutomationToAiAgentView().as_view()),
    path('facebook_posts/', views.AutomationToFacebookView().as_view()),
]
