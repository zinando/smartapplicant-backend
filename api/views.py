# api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import GeneralData
from .serializers import GeneralDataSerializer
from celery.result import AsyncResult
from .utils import extract_text, calculate_ats_score, parse_resume
from .tasks import async_extract_and_score

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
                data = {
                        'task_id': None,
                        'status': 'Completed',
                        'ats_score': ats_score,
                        'required_sections': parsed_data
                }
            return Response({'status': res_status, 'data': data, 'message':'success'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            error = str(e)
            print(f"Error: {error}")
            return Response({'status': 0, 'message': error}, status=status.HTTP_400_BAD_REQUEST)
        
class TaskStatusView(APIView):
    def get(self, request, task_id):
        task = AsyncResult(task_id)

        if task.state == 'PENDING':
            status = 2
            message = 'Still Processing'
        elif task.state == 'SUCCESS':
            status = 1
            message = 'Task Completed'
        elif task.state == 'FAILURE':
            status = 0
            message = 'Task Failed'
        
        data = {
            'task_id': task_id,
            'status': task.status,
            'result': task.result if task.ready() else None
        }
        
        return Response({'status': status, 'data': data, 'message': message}, status=status.HTTP_200_OK)


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
        