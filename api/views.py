from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import GeneralData
from celery.result import AsyncResult
from auth_user.serializers import UserSerializer
from auth_user.models import PGRequest, Order, Subscription, SubscriptionType
from .utils import extract_text, calculate_ats_score, parse_resume
from .tasks import async_extract_and_score
from .analytics import RevenueAnalytics
import os
from django.http import FileResponse, Http404


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
            print(f"Error: {error}")
            return Response({'status': 0, 'message': error}, status=status.HTTP_400_BAD_REQUEST)
        
class TaskStatusView(APIView):
    def get(self, request, task_id):
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
            print(f"Analytics error: {e}")
            return Response({'status': 0, 'message': str(e)}, status=status.HTTP_200_OK)