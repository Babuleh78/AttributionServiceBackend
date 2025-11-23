from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import CustomUser  
from .models import Composer, Analysis, ComposerAnalysis
from .serializers import (
    ComposerSerializer,
    AnalysisSerializer,
    UserRegistrationSerializer,
    ComposerAnalysisSerializer,
    UserLoginSerializer,
    UserProfileSerializer
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from .utils import upload_image_to_minio, delete_image_from_minio
from drf_yasg.utils import swagger_auto_schema
from .permissions import IsManager, IsAdmin
from django.contrib.auth import authenticate, login, logout
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import authentication_classes
from django.conf import settings
import redis
import uuid
from django.http import JsonResponse
from rest_framework import permissions
from django.contrib.auth import get_user_model
import ast
import decimal
import requests
import threading
from django.http import JsonResponse
import os


session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)


class IsOwnerOrModeratorOrAdmin(permissions.BasePermission):
    """
    Разрешает доступ, если:
    - Пользователь — владелец объекта и делает SAFE-запрос (GET, HEAD, OPTIONS), ИЛИ
    - Пользователь — суперпользователь, ИЛИ
    - Пользователь — модератор объекта (если поле moderator существует).
    """

    def has_object_permission(self, request, view, obj):
        user, error_response = get_user_from_session(request)
        if error_response:
            return False

        if hasattr(obj, 'owner') and obj.owner == user:
            return request.method in permissions.SAFE_METHODS
        if user.is_superuser:
            return True
        if hasattr(obj, 'moderator') and obj.moderator == user:
            return True
        return False

    
User = get_user_model()

def get_user_from_session(request):
    """
    Новая версия с дебагом
    """
    print("=== GET_USER_FROM_SESSION DEBUG ===")
    session_id = request.COOKIES.get('session_id')
    print(f"Session ID: {session_id}")
    print(f"All cookies: {dict(request.COOKIES)}")
    
    if not session_id:
        print("❌ No session_id in cookies")
        return None, Response(
            {"error": "Session ID not found", "debug": "No session_id cookie"},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    try:
        session_data_bytes = session_storage.get(session_id)
        print(f"Raw session data from Redis: {session_data_bytes}")
        
        if not session_data_bytes:
            print("❌ No data in Redis for this session_id")
            return None, Response(
                {"error": "Invalid or expired session", "debug": "No data in Redis"},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        session_data = ast.literal_eval(session_data_bytes.decode('utf-8'))
        user_id = session_data.get('user_id')
        
        print(f"Parsed session data: {session_data}")
        print(f"Extracted user_id: {user_id}")
        
        if not user_id:
            print("❌ user_id not found in session data")
            return None, Response(
                {"error": "User not found in session", "debug": "No user_id in session data"},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        user = User.objects.get(id=user_id)
        print(f"✅ User authenticated: {user.email} (id: {user.id}, superuser: {user.is_superuser})")
        return user, None
        
    except User.DoesNotExist:
        print(f"❌ User with id {user_id} does not exist in database")
        return None, Response(
            {"error": "User does not exist", "debug": f"User id {user_id} not found"},
            status=status.HTTP_401_UNAUTHORIZED
        )
    except Exception as e:
        print(f"❌ Session validation error: {e}")
        return None, Response(
            {"error": "Session validation failed", "debug": str(e)},
            status=status.HTTP_401_UNAUTHORIZED
        )
    

@permission_classes([AllowAny])
@authentication_classes([])
@csrf_exempt
@swagger_auto_schema(method='post', request_body=UserLoginSerializer)
@api_view(['POST'])
def login_view(request):
    username = request.data.get("email")
    password = request.data.get("password")
    user = authenticate(request, email=username, password=password)
    
    if user is not None:
        login(request, user)
        random_key = str(uuid.uuid4())  
        
        try:
            session_data = {
                'username': username,
                'user_id': user.id,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser
            }
            session_storage.set(random_key, str(session_data), ex=86400)

            response_data = {
                'user_id': user.id,
                'email': user.email,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser
            }
            
            response = JsonResponse(response_data)
            response.set_cookie(
                key='session_id',
                value=random_key,
                httponly=True,
                samesite='None',
                secure=True,  
                domain='localhost', 
                path='/',
                max_age=86400
            )
                        
            return response
            
        except redis.RedisError as e:
            print(f"Redis error: {e}")
            return JsonResponse(
                { 'error': 'session storage error'}, 
                status=500
            )
            
    else:
        return JsonResponse(
            {'error': 'login failed'}, 
            status=401
        )
    
@api_view(['POST'])
@permission_classes([])  
@authentication_classes([])
@csrf_exempt
def logout_view(request):
    ssid = request.COOKIES.get("session_id")
    if ssid:
        session_storage.delete(ssid)

    response = JsonResponse({"message": "Logged out successfully"})
    response.delete_cookie("session_id")
    return response

class ComposerListView(APIView):
    def get(self, request):
        try:
            ssid = request.COOKIES["session_id"]
            print(ssid)
        except:
            print("failed")
       
        composers = Composer.objects.filter(status=1)
        name = request.query_params.get('name', None)
        if name:
            composers = composers.filter(name__icontains=name)
        serializer = ComposerSerializer(composers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @permission_classes([IsAuthenticated])
    @swagger_auto_schema(request_body=ComposerSerializer)
    def post(self, request):
        data = request.data.copy()
        data['status'] = 1
        serializer = ComposerSerializer(data=data)
        if serializer.is_valid():
            composer = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ComposerDetailView(APIView):
    def get(self, request, pk):
        # user, error_response = get_user_from_session(request)
        # if error_response:
        #     return error_response
        
        composer = get_object_or_404(Composer, pk=pk, status=1)
        serializer = ComposerSerializer(composer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @permission_classes([IsAuthenticated])
    @swagger_auto_schema(request_body=ComposerSerializer)
    def put(self, request, pk):

        user, error_response = get_user_from_session(request)
        if error_response:
            return error_response
        
        composer = get_object_or_404(Composer, pk=pk, status=1)
        data = request.data.copy()
        data.pop('status', None)  # запрещено менять напрямую
        serializer = ComposerSerializer(composer, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @permission_classes([IsAuthenticated])
    @swagger_auto_schema(request_body=ComposerSerializer)
    def delete(self, request, pk):

        user, error_response = get_user_from_session(request)
        if error_response:
            return error_response
        
        composer = get_object_or_404(Composer, pk=pk, status=1)
        
        if composer.portrait_url:
            delete_image_from_minio(composer.portrait_url)
        composer.status = 2
        composer.save()
        return Response({"message": "Composer deleted"}, status=status.HTTP_200_OK)


class ComposerImageUploadView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    
    @swagger_auto_schema(request_body=ComposerSerializer)
    def post(self, request, pk):

        composer = get_object_or_404(Composer, pk=pk, status=1)
        if 'image' not in request.FILES:
            return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)
        if composer.portrait_url:
            delete_image_from_minio(composer.portrait_url)
        file = request.FILES['image']
        image_url = upload_image_to_minio(file)
        composer.portrait_url = image_url
        composer.save()
        return Response({
            'message': 'Image uploaded successfully',
            'image_url': image_url
        }, status=status.HTTP_200_OK)


class AddComposerToDraftView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(request_body=ComposerSerializer)
    def post(self, request, pk):

        composer = get_object_or_404(Composer, pk=pk, status=1)

        draft_analysis, created = Analysis.objects.get_or_create(
            owner=request.user,
            status=1,
            defaults={'date_created': timezone.now()}
        )

        if ComposerAnalysis.objects.filter(analysis=draft_analysis, composer=composer).exists():
            return Response({'error': 'Композитор уже добавлен в черновик'}, status=status.HTTP_400_BAD_REQUEST)

        ComposerAnalysis.objects.create(
            analysis=draft_analysis,
            composer=composer,
            potential_coincidence=0
        )

        return Response({
            'message': 'Композитор успешно добавлен в черновик',
            'draft_id': draft_analysis.id,
            'composer_id': composer.id
        }, status=status.HTTP_201_CREATED)


class AnalysisListView(APIView):
    permission_classes = [IsAdmin]
    def get(self, request):
        analyses = Analysis.objects.exclude(status=5)

        status_filter = request.query_params.get('status')
        if status_filter:
            analyses = analyses.filter(status=status_filter)

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date:
            analyses = analyses.filter(date_formation__gte=start_date)
        if end_date:
            analyses = analyses.filter(date_formation__lte=end_date)

        serializer = AnalysisSerializer(analyses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AnalysisDetailView(APIView):
    
    def get(self, request, pk):
        # Сначала получаем пользователя
        user, error_response = get_user_from_session(request)
        if error_response:
            return error_response
        
        analysis = get_object_or_404(Analysis, pk=pk)
        if analysis.status == 5:
            return Response({"error": "Analysis not found"}, status=status.HTTP_404_NOT_FOUND)

        # Проверяем права через permission класс
        permission = IsOwnerOrModeratorOrAdmin()
        if not permission.has_object_permission(request, self, analysis):
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
    
        composers_data = []
        for ca in ComposerAnalysis.objects.filter(analysis=analysis):
            composer = ca.composer
            composer_data = ComposerSerializer(composer).data
            composers_data.append(composer_data)

        data = {
            "id": analysis.id,
            "status": analysis.get_status_display(),
            "date_created": analysis.date_created,
            "date_formation": analysis.date_formation,
            "date_complete": analysis.date_complete,
            "owner": analysis.owner.email if analysis.owner else None,
            "moderator": analysis.moderator.email if analysis.moderator else None,
            "composers": composers_data,
        }
        return Response(data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=AnalysisSerializer)
    def put(self, request, pk):
        analysis = get_object_or_404(Analysis, pk=pk)
        if analysis.status == 5:
            return Response({"error": "Analysis not found"}, status=status.HTTP_404_NOT_FOUND)

        if request.user.is_superuser:
            protected_fields = {'id', 'owner'}
        elif hasattr(analysis, 'moderator') and analysis.moderator == request.user:
       
            protected_fields = {'id', 'owner'}
        else:
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        data = {k: v for k, v in request.data.items() if k not in protected_fields}

        serializer = AnalysisSerializer(analysis, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        analysis = get_object_or_404(Analysis, pk=pk)
        if analysis.status == 5:
            return Response({"error": "Analysis not found"}, status=status.HTTP_404_NOT_FOUND)

        if not (request.user.is_superuser or (hasattr(analysis, 'moderator') and analysis.moderator == request.user)):
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        analysis.status = 5
        analysis.save()
        return Response({"message": "Analysis deleted"}, status=status.HTTP_200_OK)


class AnalysisFormulateView(APIView):
    permission_classes = [IsOwnerOrModeratorOrAdmin]
    
    @swagger_auto_schema(request_body=AnalysisSerializer)
    def put(self, request, pk):
        analysis = get_object_or_404(Analysis, pk=pk)

        if analysis.status != 1:
            return Response({"error": "Only draft analysis can be formulated"}, status=status.HTTP_400_BAD_REQUEST)
        
        composer_analyses = ComposerAnalysis.objects.filter(analysis=analysis)
        if not composer_analyses.exists():
            return Response({"error": "At least one composer must be added"}, status=status.HTTP_400_BAD_REQUEST)

        print(composer_analyses)
        # Асинхронно отправляем запросы в Go сервис для каждого composer_analysis
        for composer_analysis in composer_analyses:
            # Запускаем в отдельном потоке для асинхронности
            thread = threading.Thread(
                target=send_to_go_service,
                args=(composer_analysis.id, composer_analysis.composer_id, analysis.id)
            )
            thread.daemon = True
            thread.start()

        # Немедленно обновляем статус анализа
        analysis.date_formation = timezone.now()
        analysis.status = 2  # Статус "Сформирован"
        analysis.save()

        return Response({
            "message": "Analysis formulated successfully, coincidence calculations started",
            "status": analysis.get_status_display(),
            "date_formatiion": analysis.date_formation
        }, status=status.HTTP_200_OK)

def send_to_go_service(composer_analysis_id, composer_id, analysis_id):
    """
    Отправляет запрос в Go сервис для расчета совпадения
    """
    try:
        go_service_url = 'http://go-service:8888/api/calculate-coincidence'
                         
        data = {
            "composer_analysis_id": composer_analysis_id,
            "composer_id": composer_id,
            "analysis_id": analysis_id
        }
        
        # Отправляем запрос (таймаут 30 секунд)
        response = requests.post(
            go_service_url,
            json=data,
            timeout=30
        )
        
        if response.status_code != 202:
            print(f"Error sending to Go service: {response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request to Go service failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

class AnalysisCompleteOrRejectView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    @swagger_auto_schema(request_body=AnalysisSerializer)
    def put(self, request, pk):
        analysis = get_object_or_404(Analysis, pk=pk)

        if analysis.status != 2:
            return Response({"error": "Analysis must be 'In progress'"}, status=status.HTTP_400_BAD_REQUEST)

        action = request.data.get('action')
        if action not in ['complete', 'reject']:
            return Response({"error": "'action' must be 'complete' or 'reject'"}, status=status.HTTP_400_BAD_REQUEST)

        analysis.moderator = request.user
        analysis.date_complete = timezone.now()

        if action == 'complete':
            analysis.status = 3
        else:
            analysis.status = 4

        analysis.save()

        return Response({
            "message": f"Analysis {action}d successfully",
            "status": analysis.get_status_display(),
            "moderator": request.user.email,
            "date_complete": analysis.date_complete
        }, status=status.HTTP_200_OK)


class CartIconView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        draft_analysis = Analysis.objects.filter(owner=request.user, status=1).first()
        if not draft_analysis:
            draft_analysis = Analysis.objects.create(
                owner=request.user,
                status=1,
                date_created=timezone.now()
            )

        composer_count = ComposerAnalysis.objects.filter(analysis=draft_analysis).count()
        return Response({
            "order_id": draft_analysis.id,
            "item_count": composer_count
        }, status=status.HTTP_200_OK)


class ComposerAnalysisUpdateView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=ComposerAnalysisSerializer)
    def put(self, request, analysis_id, composer_id):
        analysis = get_object_or_404(Analysis, pk=analysis_id)
        ca = get_object_or_404(ComposerAnalysis, analysis_id=analysis_id, composer_id=composer_id)

        if analysis.status != 1:
            if list(request.data.keys()) != ['potential_coincidence']:
                return Response(
                    {"error": "Can only modify draft for fields other than potential_coincidence"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = ComposerAnalysisSerializer(
            ca, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "ComposerAnalysis updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "error": "Validation failed",
                "details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
    def get(self, request, analysis_id, composer_id):
        """GET метод для получения данных ComposerAnalysis"""
        ca = get_object_or_404(ComposerAnalysis, analysis_id=analysis_id, composer_id=composer_id)
        serializer = ComposerAnalysisSerializer(ca)
        return Response(serializer.data)

class ComposerAnalysisDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, analysis_id, composer_id):
        analysis = get_object_or_404(Analysis, pk=analysis_id)
        if analysis.status != 1:
            return Response({"error": "Can only modify draft"}, status=status.HTTP_400_BAD_REQUEST)

        ca = get_object_or_404(ComposerAnalysis, analysis_id=analysis_id, composer_id=composer_id)
        ca.delete()
        return Response({"message": "Composer removed from analysis"}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        return UserProfileSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        elif self.action == 'list':
            return [IsManager(), IsAdmin()]
        else:
            return [IsAdmin()]


