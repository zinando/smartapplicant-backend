from django.contrib import admin
from django.urls import path
from api.views import (ResumeParseView, TaskStatusView, StatsAPIView, ResumeDownloadView,
                       AnalyticsAPIView, InputSuggestionsAPIView, facebook_login_view, facebook_callback,
                       facebook_select_page)
from auth_user.views import ResumeUploadView, ResumeAnalysisView, ResumeGeneratorView, ResumeMatchAndGenerateView
from django.urls import include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path("automation/", include("automation.urls")),
    path('api/parse/', ResumeParseView.as_view(), name='parse-resume'),
    path('api-auth/', include('rest_framework.urls')),
    path('api/task-status/<str:task_id>/', TaskStatusView.as_view()),
    path('api/auth/token/', TokenObtainPairView.as_view()),
    path('api/auth/token/refresh/', TokenRefreshView.as_view()),
    path('api/auth/', include('auth_user.url')),
    path('api/user/resume/', ResumeUploadView.as_view()),
    path('api/user/resume/analysis/', ResumeAnalysisView.as_view()),
    path('api/stats/', StatsAPIView.as_view()),
    path('api/download/<str:file_name>/', ResumeDownloadView.as_view(), name='download-resume'),
    path('api/user/resumes/generate/', ResumeGeneratorView.as_view(), name='resume-generator'),
    path('api/user/resumes/generate_matching/', ResumeMatchAndGenerateView.as_view()),
    path('api/analytics/<duration_days>/', AnalyticsAPIView.as_view(), name='analytics'),
    path('api/user/resume/input-suggestions/', InputSuggestionsAPIView.as_view()),
    path("facebook/login/", facebook_login_view, name="facebook_login"),
    path("facebook/callback/", facebook_callback, name="facebook_callback"),
    path("facebook/select-page/", facebook_select_page, name="facebook_select_page"),
]