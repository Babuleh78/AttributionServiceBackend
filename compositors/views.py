from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import CustomUser  ## Кастомный пользователь
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
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import authentication_classes
from django.conf import settings
import redis
import uuid


session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

def get_creator():
    return CustomUser.objects.get(email="creator@example.com")  

@permission_classes([AllowAny])
@authentication_classes([])
@csrf_exempt
@swagger_auto_schema(method='post', request_body=UserProfileSerializer)
@api_view(['POST'])
def login_view(request):
    username = request.data.get("email")
    password = request.data.get("password")
    user = authenticate(request, email=username, password=password)
    
    if user is not None:
        # Конвертируем UUID в строку
        random_key = str(uuid.uuid4())  # Добавьте str() здесь
        
        try:
            session_storage.set(random_key, username, ex=86400)  # TTL 24 часа

            response = HttpResponse("{'status': 'ok'}")
            response.set_cookie("session_id", random_key, max_age=86400)
            return response
            
        except redis.RedisError as e:
            print(f"Redis error: {e}")
            return HttpResponse("{'status': 'error', 'error': 'session storage error'}", status=500)
            
    else:
        return HttpResponse("{'status': 'error', 'error': 'login failed'}", status=401)
    
@swagger_auto_schema(method='post', operation_description="Выход из системы")
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response({'status': 'Success', 'message': 'Logged out successfully'})

class ComposerListView(APIView):
    def get(self, request):
        composers = Composer.objects.filter(status=1)
        name = request.query_params.get('name', None)
        if name:
            composers = composers.filter(name__icontains=name)
        serializer = ComposerSerializer(composers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    permission_classes = [IsAuthenticated]
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
        composer = get_object_or_404(Composer, pk=pk, status=1)
        serializer = ComposerSerializer(composer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(request_body=ComposerSerializer)
    def put(self, request, pk):
        composer = get_object_or_404(Composer, pk=pk, status=1)
        data = request.data.copy()
        data.pop('status', None)  # запрещено менять напрямую
        serializer = ComposerSerializer(composer, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    permission_classes = [IsAuthenticated]
    def delete(self, request, pk):
        composer = get_object_or_404(Composer, pk=pk, status=1)
        creator = get_creator()
        if request.user != creator:
            return Response({"error": "Only creator can delete composers"}, status=status.HTTP_403_FORBIDDEN)
        if composer.portrait_url:
            delete_image_from_minio(composer.portrait_url)
        composer.status = 2
        composer.save()
        return Response({"message": "Composer deleted"}, status=status.HTTP_200_OK)


class ComposerImageUploadView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    
    @swagger_auto_schema(request_body=ComposerSerializer)
    def post(self, request, pk):
        creator = get_creator()
        if request.user != creator:
            return Response({"error": "Only creator can upload images"}, status=status.HTTP_403_FORBIDDEN)

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
        creator = get_creator()
        if request.user != creator:
            return Response({"error": "Only creator can add to draft"}, status=status.HTTP_403_FORBIDDEN)

        composer = get_object_or_404(Composer, pk=pk, status=1)

        draft_analysis, created = Analysis.objects.get_or_create(
            owner=creator,
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
    permission_classes = [IsAdmin]
    def get(self, request, pk):
        analysis = get_object_or_404(Analysis, pk=pk)
        if analysis.status == 5:
            return Response({"error": "Analysis not found"}, status=status.HTTP_404_NOT_FOUND)

        composers_data = []
        for ca in ComposerAnalysis.objects.filter(analysis=analysis):
            composer = ca.composer
            composers_data.append({
                "id": composer.id,
                "name": composer.name,
                "biography": composer.biography,
                "portrait_url": composer.portrait_url,
                "analyzed_works": composer.analyzed_works,
                "total_intervals": composer.total_intervals,
                "period": composer.period,
                "polyphony_type": composer.polyphony_type,
                "interval_stats": composer.interval_stats,
            })

        data = {
            "id": analysis.id,
            "status": analysis.get_status_display(),
            "date_created": analysis.date_created,
            "date_formation": analysis.date_formation,
            "date_complete": analysis.date_complete,
            "owner": analysis.owner.username if analysis.owner else None,
            "moderator": analysis.moderator.username if analysis.moderator else None,
            "composers": composers_data,
        }
        return Response(data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=AnalysisSerializer)
    def put(self, request, pk):
        analysis = get_object_or_404(Analysis, pk=pk)
        if analysis.status == 5:
            return Response({"error": "Analysis not found"}, status=status.HTTP_404_NOT_FOUND)

        creator = get_creator()
        if request.user == creator:
            protected_fields = {'id', 'owner'} 
        elif request.user.is_superuser:
            protected_fields = {'id', 'owner'}
        else:
            protected_fields = {'id', 'status', 'owner', 'moderator', 'date_created', 'date_formation', 'date_complete'}

        data = {k: v for k, v in request.data.items() if k not in protected_fields}

        serializer = AnalysisSerializer(analysis, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        analysis = get_object_or_404(Analysis, pk=pk)
        creator = get_creator()
        if request.user != creator:
            return Response({"error": "Only creator can delete analysis"}, status=status.HTTP_403_FORBIDDEN)
        analysis.status = 5
        analysis.save()
        return Response({"message": "Analysis deleted"}, status=status.HTTP_200_OK)


class AnalysisFormulateView(APIView):
    permission_classes = [IsAuthenticated, IsManager]
    @swagger_auto_schema(request_body=AnalysisSerializer)
    def put(self, request, pk):
        analysis = get_object_or_404(Analysis, pk=pk)
        creator = get_creator()

        if request.user != creator:
            return Response({"error": "Only creator can formulate"}, status=status.HTTP_403_FORBIDDEN)
        if analysis.status != 1:
            return Response({"error": "Only draft analysis can be formulated"}, status=status.HTTP_400_BAD_REQUEST)
        if not ComposerAnalysis.objects.filter(analysis=analysis).exists():
            return Response({"error": "At least one composer must be added"}, status=status.HTTP_400_BAD_REQUEST)

        analysis.date_formation = timezone.now()
        analysis.status = 2
        analysis.save()

        return Response({
            "message": "Analysis formulated successfully",
            "status": analysis.get_status_display(),
            "date_formation": analysis.date_formation
        }, status=status.HTTP_200_OK)


class AnalysisCompleteOrRejectView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    @swagger_auto_schema(request_body=AnalysisSerializer)
    def put(self, request, pk):
        analysis = get_object_or_404(Analysis, pk=pk)
        creator = get_creator()

        if not (request.user.is_staff or request.user == creator):
            return Response({"error": "Only moderators or creator can complete/reject"}, status=status.HTTP_403_FORBIDDEN)
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
            "moderator": request.user.username,
            "date_complete": analysis.date_complete
        }, status=status.HTTP_200_OK)


class CartIconView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        creator = get_creator()
        if request.user != creator:
            return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)

        draft_analysis = Analysis.objects.filter(owner=creator, status=1).first()
        if not draft_analysis:
            draft_analysis = Analysis.objects.create(
                owner=creator,
                status=1,
                date_created=timezone.now()
            )

        composer_count = ComposerAnalysis.objects.filter(analysis=draft_analysis).count()
        return Response({
            "order_id": draft_analysis.id,
            "item_count": composer_count
        }, status=status.HTTP_200_OK)



class ComposerAnalysisUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=ComposerAnalysisSerializer)
    def put(self, request, analysis_id, composer_id):
        analysis = get_object_or_404(Analysis, pk=analysis_id)
        creator = get_creator()

        if request.user != creator:
            return Response(
                {"error": "Only creator can modify draft"},
                status=status.HTTP_403_FORBIDDEN
            )

        if analysis.status != 1:
            return Response(
                {"error": "Can only modify draft"},
                status=status.HTTP_400_BAD_REQUEST
            )

        ca = get_object_or_404(ComposerAnalysis, analysis_id=analysis_id, composer_id=composer_id)

        anonymous_stats = request.data.get('anonymous_interval_stats')
        potential = request.data.get('potential_coincidence')

        if anonymous_stats is not None:
            ca.anonymous_interval_stats = anonymous_stats
        if potential is not None:
            ca.potential_coincidence = potential

        ca.save()

        return Response({
            "message": "ComposerAnalysis updated successfully",
            "anonymous_interval_stats": ca.anonymous_interval_stats,
            "potential_coincidence": ca.potential_coincidence
        }, status=status.HTTP_200_OK)


class ComposerAnalysisDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, analysis_id, composer_id):
        analysis = get_object_or_404(Analysis, pk=analysis_id)
        creator = get_creator()

        if request.user != creator:
            return Response({"error": "Only creator can modify draft"}, status=status.HTTP_403_FORBIDDEN)
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


