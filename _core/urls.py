"""
URL configuration for _core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from api.views import ResumeParseView, TaskStatusView, StatsAPIView
from auth_user.views import ResumeUploadView, ResumeAnalysisView
from django.urls import include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/parse/', ResumeParseView.as_view(), name='parse-resume'),
    path('api-auth/', include('rest_framework.urls')),
    path('api/task-status/<str:task_id>/', TaskStatusView.as_view()),
    path('api/auth/token/', TokenObtainPairView.as_view()),
    path('api/auth/token/refresh/', TokenRefreshView.as_view()),
    path('api/auth/', include('auth_user.url')),
    path('api/user/resume/', ResumeUploadView.as_view()),
    path('api/user/resume/analysis/', ResumeAnalysisView.as_view()),
    path('api/stats/', StatsAPIView.as_view()),
]