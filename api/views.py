from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import GeneralData
from .serializers import JobTitleSerializer
from celery.result import AsyncResult
from auth_user.serializers import UserSerializer
from .utils import extract_text, calculate_ats_score, parse_resume
from .suggestion_utils import get_suggestions_for_all_job_titles
from .tasks import (async_extract_and_score, async_process_new_jt_suggestion, async_process_new_skill_suggestion)
from .analytics import RevenueAnalytics
import os
from django.http import FileResponse, Http404
from django.conf import settings
from django.shortcuts import render, redirect
import requests
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from automation.helpers import save_cache, get_cache
from automation.models import FacebookAuthLog
import secrets
import json
from  _core.utils import QueuedTaskTracker

ENV_FILE = os.path.join(settings.BASE_DIR, ".env")
task_tracker = QueuedTaskTracker()

def safe_json_loads(value, default=None):
    """
    Safely decode JSON stored in the database.

    Returns `default` when:
    - value is None/empty
    - JSON is malformed
    - decoded value is not usable
    """
    if not value:
        return {} if default is None else default

    try:
        data = json.loads(value)

        if data is None:
            return {} if default is None else default

        return data

    except (json.JSONDecodeError, TypeError, ValueError):
        return {} if default is None else default


class ResumeParseView(APIView):
    def post(self, request):
        try:
            # Validate file exists and is within size limit
            if 'resume' not in request.FILES:
                raise Exception("No file uploaded")
            
            file = request.FILES['resume']
            if file.size > 5 * 1024 * 1024:  # 5MB
                raise Exception("File too large (max 5MB)")
            
            # Read file content into memory
            file_bytes = file.read()

            if file.size > 2 * 1024 * 1024:  # Example: 2MB+ → async
                task = async_extract_and_score.delay(file_bytes, file.name)
                task_tracker.track_task(task.id)

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
                res_status = 1
                # print(f'parsed_data: {parsed_data}')
                data = {
                        'task_id': None,
                        'status': 'Completed',
                        'ats_score': parsed_data.get('ats_score', 0),
                        'required_sections': {k: v for k, v in parsed_data.items() if k in ('name', 'email', 'phone', 'education', 'experience', 'skills', 'certificates', 'errors')}
                }
            return Response({'status': res_status, 'data': data, 'message':'success'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            error = str(e)
            # print(f"Error: {error}")
            return Response({'status': 0, 'message': error}, status=status.HTTP_400_BAD_REQUEST)
        
class TaskStatusView(APIView):
    def get(self, request, task_id):
        try:
            if not task_id:
                raise ValueError("Task ID is required")
            
            if not task_tracker.is_task_tracked(task_id):
                raise ValueError("Task ID not found or expired")
            
            task = AsyncResult(task_id)
            result = None

            if task.state == 'PENDING':
                message = 'Still Processing'
            elif task.state == 'SUCCESS':
                message = 'Task Completed'
                result = task.result
            elif task.state == 'FAILURE':
                message = 'Task Failed'
                result = str(task.result)
            
            data = {
                'task_id': task_id,
                'status': task.status,
                'result': result,
            }
            
            return Response({'status': 1, 'data': data, 'message': message}, status=status.HTTP_200_OK)
        except Exception as e:
            error = str(e)
            # print(f"Error: {error}")
            return Response({'status': 0, 'message': error}, status=status.HTTP_400_BAD_REQUEST)

class StatsAPIView(APIView):
    def get(self, request):
        try:
            stats = GeneralData.objects.first()
            if not stats:
                raise Exception('No stat data found.')
            data = {
                'registered_users': stats.registered_users,
                'premium_subscribers': stats.premium_users,
                'currently_online': stats.currently_online
            }
            return Response(
                {
                    'status': 1,
                    'message': 'success',
                    'data': data
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    'status': 0,
                    'message': f'{e}'
                },
                status=status.HTTP_200_OK
            )
        
class ResumeDownloadView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, file_name):
        # authorize user
        file_path = os.path.join('generated_docs', file_name)
        user = request.user
        if not user.is_authenticated:
            return Response({'status': 0, 'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if not os.path.exists(file_path):
            raise Http404("File not found.")

        # Serve file as a response
        response = FileResponse(
            open(file_path, 'rb'),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            filename=os.path.basename(file_path),
            as_attachment=True
        )

        # After file is served, delete it (after response is closed)
        def delete_file(response):
            try:
                os.remove(file_path)
                # print(f"Deleted file: {file_path}")
            except Exception as e:
                print(f"Failed to delete file: {e}")

        response.close = lambda old_close=response.close: (
            old_close(),
            delete_file(response)
        )[0]  # Ensure original close() is called first

        return response
        
# view for fetching analytics data
class AnalyticsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        try:
            # Ensure user is authenticated
            if not request.user.is_authenticated:
                raise Exception("User not authenticated")
            
            # Check if user is admin
            serialized_user = self.serializer_class(request.user)
            if not serialized_user.data.get('is_admin', False):
                raise Exception("User does not have permission to access analytics data")
            
            duration_days = int(kwargs.get('duration_days', 30))  # Default to last 30 days

            # Initialize analytics with the specified duration
            analytics = RevenueAnalytics(duration_days=duration_days)
            # Get dashboard data
            dashboard_data = analytics.get_dashboard_data()

            return Response({'status': 1, 'data': dashboard_data, 'message': 'success'}, status=status.HTTP_200_OK)
        except Exception as e:
            # print(f"Analytics error: {e}")
            return Response({'status': 0, 'message': str(e)}, status=status.HTTP_200_OK)

# view for fetching input suggestions during form filling
class InputSuggestionsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = JobTitleSerializer
    def get(self, request, *args, **kwargs):
        try:
            suggestions, skills = get_suggestions_for_all_job_titles()
            return Response({
                'status': 1, 
                'resume_input_suggestions': suggestions,
                'resume_skill_suggestions': skills,
                'message': 'success'
                }, status=status.HTTP_200_OK)
        except Exception as e:
            # print(f"Input suggestions error: {e}")
            return Response({'status': 0, 'message': str(e)}, status=status.HTTP_200_OK)
        
    def put(self, request, *args, **kwargs):
        """ When a user enters a new JT or new skill, it will be sent to AI to generate suggestions for them via this endpoint """
        try:
            new_job_title = request.GET.get('new_job_title', '').strip().lower()
            new_skill = request.GET.get('new_skill', '').strip().lower()

            if new_job_title:
                task = async_process_new_jt_suggestion.delay(new_job_title)
                task_tracker.track_task(task.id)
            elif new_skill:
                job_title = request.GET.get('job_title', '').strip().lower()
                if not job_title:
                    raise Exception("Job title must be provided when suggesting a new skill")
                task = async_process_new_skill_suggestion.delay(new_skill, job_title)
                task_tracker.track_task(task.id)
            else:
                raise Exception("No new job title or skill provided")
            
            return Response({
                'status': 1,
                'task_id': task.id,
                'message': 'job submitted for suggestions update'}, 
                status=status.HTTP_200_OK)
        except Exception as e:
            # print(f"Input suggestions update error: {e}")
            return Response({'status': 0, 'message': str(e)}, status=status.HTTP_200_OK)

@api_view(["GET"])
@csrf_exempt
def facebook_login_view(request):
    state = secrets.token_urlsafe(32)
    auth_log = FacebookAuthLog.objects.create(
        state=state,
        step="code_request",
        step_status="initiated",
        ip_address=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
    )
    auth_url = (
        "https://www.facebook.com/v19.0/dialog/oauth"
        f"?client_id={settings.SMARTAPPLICANT['APP_ID']}"
        f"&redirect_uri={settings.SMARTAPPLICANT['REDIRECT_URI']}"
        "&scope=pages_manage_posts,pages_read_engagement,pages_show_list,pages_manage_metadata,pages_read_user_content,pages_manage_engagement"
        "&display=popup"
        "&auth_type=rerequest"
        f"&state={state}"
        "&response_type=code"
    )

    return Response(
        {"auth_url": auth_url,
         "app_id": settings.SMARTAPPLICANT['APP_ID'],
         "app_version": settings.SMARTAPPLICANT['APP_VERSION']
        },
        status=status.HTTP_200_OK
    )


@api_view(["POST", "GET"])
@csrf_exempt
def facebook_callback(request):
    """Handles redirect from Facebook OAuth; retrieves the user's pages."""
    state = request.GET.get("state")
    code = request.GET.get("code")
    auth_log = FacebookAuthLog.objects.filter(state=state).first()
    if not auth_log:
        return redirect("https://smartapplicant.net/fb_page_selector/?error=Forbidden_invalid_state")
    if not code:
        auth_log.step_status = "failed"
        auth_log.message = f"Missing code parameter in callback: {request.GET}"
        auth_log.save()
        return redirect("https://smartapplicant.net/fb_page_selector/?error=missing_code")
    auth_log.code = code
    auth_log.step_status = "success"
    auth_log.save()
    
    # 1. Exchange code for short-lived user access token
    token_url = (
        f"{settings.META_GRAPH_URL}/oauth/access_token"
        f"?client_id={settings.SMARTAPPLICANT['APP_ID']}"
        f"&redirect_uri={settings.SMARTAPPLICANT['REDIRECT_URI']}"
        f"&client_secret={settings.SMARTAPPLICANT['APP_SECRET']}"
        f"&code={code}"
    )
    auth_log.step = "short_lived_token"
    auth_log.step_status = "initiated"
    auth_log.save()

    response = requests.get(token_url)
    token_res = response.json()
    
    access_token = token_res.get("access_token")

    if not access_token:
        auth_log.step_status = "failed"
        auth_log.message = f"Failed to exchange code for access token: {token_res}"
        auth_log.save()
        return redirect("https://smartapplicant.net/fb_page_selector/?error=token_exchange_failed")
    auth_log.step_status = "success"
    auth_log.short_lived_token_payload = json.dumps(token_res)
    auth_log.save()

    # 2. Fetch pages the user manages
    pages_url = f"https://graph.facebook.com/me/accounts?access_token={access_token}"
    auth_log.step = "page_token"
    auth_log.step_status = "initiated"
    auth_log.save()
    
    pages_res = requests.get(pages_url).json()
    pl_data = {}

    if "data" not in pages_res or len(pages_res["data"]) == 0:
        auth_log.step_status = "failed"
        auth_log.message = f"No pages found for user: {pages_res}"
        auth_log.save()
        return redirect("https://smartapplicant.net/fb_page_selector/?error=no_pages_found")
    pl_data["fetch_pages_payload"] = pages_res
    auth_log.page_access_token_payload = json.dumps(pl_data)
    auth_log.save()

    # Show page selection UI
    return redirect(f"https://smartapplicant.net/fb_page_selector/?code={state}")


@api_view(["POST", "GET"])
@csrf_exempt
def facebook_select_page(request):
    """
    GET:
        Return all Facebook pages available for the current session.

    POST:
        Connect one selected Facebook page.

    Multiple pages can be selected using the same `state`.
    Each selected page is stored under `selected_pages[page_id]`
    so selecting another page does not overwrite previous selections.
    """

    # ============================================================
    # GET
    # Return all Facebook pages available for this session
    # ============================================================

    if request.method == "GET":
        try:
            state = request.GET.get("code")

            if not state:
                return Response(
                    "Missing code parameter.",
                    status=400
                )

            auth_log = (
                FacebookAuthLog.objects
                .filter(state=state)
                .first()
            )

            if not auth_log:
                return Response(
                    "Invalid code parameter.",
                    status=400
                )

            # Safely decode page_access_token_payload
            payload = safe_json_loads(
                auth_log.page_access_token_payload,
                default={}
            )

            if not isinstance(payload, dict):
                return Response(
                    "Invalid page data stored in auth log.",
                    status=400
                )

            page_data = payload.get(
                "fetch_pages_payload",
                {}
            )

            if not isinstance(page_data, dict):
                return Response(
                    "Invalid Facebook pages payload.",
                    status=400
                )

            pages = page_data.get("data", [])

            if not isinstance(pages, list):
                return Response(
                    "Invalid Facebook pages data.",
                    status=400
                )

            return Response(
                pages,
                status=200
            )

        except Exception as e:
            return Response(
                f"Error: {e}",
                status=400
            )

    # ============================================================
    # POST
    # User selects a Facebook page
    # ============================================================

    request_data = request.data

    page_id = request_data.get("page_id")
    state = request_data.get("code")

    if not page_id or not state:
        return Response(
            "Missing page_id or code parameter.",
            status=status.HTTP_400_BAD_REQUEST
        )

    # ------------------------------------------------------------
    # Find the auth log belonging to this business/session
    # ------------------------------------------------------------

    auth_log = (
        FacebookAuthLog.objects
        .filter(state=state)
        .first()
    )

    if not auth_log:
        return Response(
            "Invalid code parameter.",
            status=status.HTTP_400_BAD_REQUEST
        )

    # ============================================================
    # Get Facebook user access token
    # ============================================================

    short_lived_token_payload = safe_json_loads(
        auth_log.short_lived_token_payload,
        default={}
    )

    if not isinstance(short_lived_token_payload, dict):
        return Response(
            "Invalid Facebook user token data. Restart login.",
            status=status.HTTP_400_BAD_REQUEST
        )

    user_token = short_lived_token_payload.get(
        "access_token"
    )

    if not user_token:
        return Response(
            "Missing user access token. Restart login.",
            status=400
        )

    # ============================================================
    # 1. Fetch Page Access Token
    # ============================================================

    page_token_url = (
        f"https://graph.facebook.com/{page_id}"
        f"?fields=access_token"
        f"&access_token={user_token}"
    )

    try:
        response = requests.get(
            page_token_url,
            timeout=15
        )
        response.raise_for_status()
        page_data = response.json()

    except requests.RequestException as e:
        auth_log.step_status = "failed"
        auth_log.message = (
            f"Facebook API request failed: {e}"
        )
        auth_log.save(
            update_fields=[
                "step_status",
                "message",
            ]
        )

        return Response(
            "Failed to communicate with Facebook.",
            status=status.HTTP_502_BAD_GATEWAY
        )

    except ValueError:
        auth_log.step_status = "failed"
        auth_log.message = (
            "Facebook returned an invalid JSON response."
        )
        auth_log.save(
            update_fields=[
                "step_status",
                "message",
            ]
        )

        return Response(
            "Facebook returned an invalid response.",
            status=status.HTTP_502_BAD_GATEWAY
        )

    # Make sure Facebook returned an object/dict
    if not isinstance(page_data, dict):
        auth_log.step_status = "failed"
        auth_log.message = (
            "Unexpected Facebook API response format."
        )
        auth_log.save(
            update_fields=[
                "step_status",
                "message",
            ]
        )

        return Response(
            "Unexpected Facebook API response.",
            status=status.HTTP_502_BAD_GATEWAY
        )

    # ============================================================
    # Check Facebook API error
    # ============================================================

    facebook_error = page_data.get("error")

    if facebook_error:
        auth_log.step_status = "failed"
        auth_log.message = (
            f"Error fetching page access token: "
            f"{facebook_error}"
        )
        auth_log.save(
            update_fields=[
                "step_status",
                "message",
            ]
        )

        return Response(
            {
                "error": "Failed to fetch page access token.",
                "details": facebook_error,
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    page_access_token = page_data.get(
        "access_token"
    )

    if not page_access_token:
        auth_log.step_status = "failed"
        auth_log.message = (
            "Facebook response did not contain a page access token."
        )
        auth_log.save(
            update_fields=[
                "step_status",
                "message",
            ]
        )

        return Response(
            "Failed to retrieve Page Access Token.",
            status=status.HTTP_400_BAD_REQUEST
        )

    # ============================================================
    # 2. Safely update selected pages
    # ============================================================

    pl_data = safe_json_loads(
        auth_log.page_access_token_payload,
        default={}
    )

    if not isinstance(pl_data, dict):
        pl_data = {}

    # Existing selected pages
    selected_pages = pl_data.get(
        "selected_pages",
        {}
    )

    # Make sure selected_pages is a dictionary
    if not isinstance(selected_pages, dict):
        selected_pages = {}

    # ------------------------------------------------------------
    # Store this page by page_id.
    #
    # If the page was already selected, this updates its data.
    # Other selected pages remain untouched.
    # ------------------------------------------------------------

    selected_pages[str(page_id)] = {
        **page_data,
        "page_id": str(page_id),
    }

    pl_data["selected_pages"] = selected_pages

    auth_log.page_access_token_payload = json.dumps(
        pl_data
    )

    auth_log.step_status = "success"
    auth_log.message = (
        f"Page {page_id} connected successfully."
    )

    auth_log.save(
        update_fields=[
            "page_access_token_payload",
            "step_status",
            "message",
        ]
    )

    # ============================================================
    # 3. Save Page Access Token to .env
    # ============================================================

    page_name = f"page_{page_id}"

    update_env(
        page_name,
        page_access_token
    )

    # ============================================================
    # 4. Check whether Client already exists
    # ============================================================

    client = update_existing_client(
        page_id,
        page_access_token
    )

    if client:
        auth_log.message = (
            f"Existing client updated with new page access token "
            f"for page ID {page_id}."
        )

        auth_log.save(
            update_fields=["message"]
        )

        wa_url = (
            f"https://wa.me/"
            f"{settings.SMARTAPPLICANT['PHONE_NUMBER']}"
            f"?text=I've%20updated%20my%20Facebook%20page%20"
            f"{client.business_name}"
            f"%20connection%20with%20a%20new%20page%20access%20token."
        )

        return Response(
            {
                "message": "Page connected successfully.",
                "redirect_url": wa_url,
            },
            status=200
        )

    # ============================================================
    # 5. New Client
    # Redirect to WhatsApp
    # ============================================================

    wa_url = (
        f"https://wa.me/"
        f"{settings.SMARTAPPLICANT['PHONE_NUMBER']}"
        f"?text=I've%20connected%20my%20Facebook%20page"
        f"%20with%20page_id:%20{page_id}"
        f"%20and%20session%20ID:%20{state}."
    )

    return Response(
        {
            "message": "Page connected successfully.",
            "redirect_url": wa_url,
        },
        status=200
    )


@api_view(["POST", "GET"])
@csrf_exempt
def facebook_select_pagexxx(request):
    """User selects which page to connect → save PAT + page_id → redirect to WhatsApp"""
    if request.method == "GET":
        try:
            state = request.GET.get("code")
            if not state:
                raise Exception(f"Missing code parameter. Returned code: {state}")
            auth_log = FacebookAuthLog.objects.filter(state=state).first()
            if not auth_log:
                raise Exception("Invalid code parameter.")
            page_data = {}
            if auth_log.page_access_token_payload:
                page_data = json.loads(auth_log.page_access_token_payload).get("fetch_pages_payload", {})
        
            if not page_data:
                raise Exception("No page data found in auth log.")
            pages = page_data.get("data", [])
            return Response(pages, status=200)
        except Exception as e:
            return Response(f"Error: {e}", status=400)
    
    request_data = request.data
    page_id = request_data.get("page_id")
    state = request_data.get("code")
    auth_log = FacebookAuthLog.objects.filter(state=state).first()
    if not auth_log:
        return Response("Invalid code parameter.", status=400)
    short_lived_token_payload = {}
    if auth_log.short_lived_token_payload:
        short_lived_token_payload = json.loads(auth_log.short_lived_token_payload)
    user_token = short_lived_token_payload.get("access_token")
    
    if not page_id or not user_token:
        return Response("Missing page_id and or user access token, restart login.", status=400)

    # 1. Fetch the page access token for the selected page
    page_token_url = (
        f"https://graph.facebook.com/{page_id}"
        f"?fields=access_token&access_token={user_token}"
    )

    response = requests.get(page_token_url)
    page_data = response.json()
    if "error" in page_data and "access_token" not in page_data:
        auth_log.step_status = "failed"
        auth_log.message = f"Error fetching page access token: {page_data['error']}"
        auth_log.save()
        return Response(f"Error fetching page access token: {page_data['error']}", status=400)

    page_access_token = page_data.get("access_token")
    page_name = f'page_{page_id}' # page_data.get("name", "Unknown Page")

    if not page_access_token:
        auth_log.step_status = "failed"
        auth_log.message = "Failed to retrieve Page Access Token. Access token missing in response."
        auth_log.save()
        return Response("Failed to retrieve Page Access Token. Access token missing in response.", status=400)
    
    auth_log.step_status = "success"
    pl_data = json.loads(auth_log.page_access_token_payload)
    pl_data["selected_page_data_payload"] = page_data
    auth_log.page_access_token_payload = json.dumps(pl_data)
    auth_log.save()

    # 2. Save to .env
    update_env(page_name, page_access_token)

    client = update_existing_client(page_id, page_access_token)
    if client:
        auth_log.message = f"Existing client updated with new page access token for page ID {page_id}."
        auth_log.save()

        wa_url = f"https://wa.me/{settings.SMARTAPPLICANT['PHONE_NUMBER']}?text=I've%20updated%20my%20Facebook%20page%20{client.business_name}%20connection%20with%20a%20new%20page%20access%20token."
        return Response(
            {"message": "Page connected successfully.", "redirect_url": wa_url},
            status=200
        )

    # 3. Redirect to WhatsApp
    wa_url = f"https://wa.me/{settings.SMARTAPPLICANT['PHONE_NUMBER']}?text=I've%20connected%20my%20Facebook%20page%20with%20page_id:%20{page_id}%20and%20session%20ID:%20{state}."
    return Response(
        {"message": "Page connected successfully.", "redirect_url": wa_url},
        status=200
    )


def update_env(key, value):
    """Safely rewrites or adds key=value in the .env file."""
    lines = []
    updated = False

    with open(ENV_FILE, "r") as f:
        lines = f.readlines()

    with open(ENV_FILE, "w") as f:
        for line in lines:
            if line.startswith(key + "="):
                f.write(f"{key}={value}\n")
                updated = True
            else:
                f.write(line)

        if not updated:
            f.write(f"{key}={value}\n")

def update_existing_client(page_id, page_access_token):
    """Updates the existing client's page access token and auth log with the latest login info"""
    from automation.models import AutomatedClients

    try:
        obj  = AutomatedClients.objects.get(client_id=page_id)
        obj.page_access_token = str(page_access_token)
        obj.save(update_fields=['page_access_token'])
        return obj

    except AutomatedClients.DoesNotExist:
        return False
