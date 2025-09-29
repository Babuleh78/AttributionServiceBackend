
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Composer, Analysis, ComposerAnalysis
from .serializers import ComposerSerializer, AnalysisSerializer, UserLoginSerializer, UserProfileSerializer, UserRegistrationSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from .utils import upload_image_to_minio, delete_image_from_minio

def get_creator():
    return User.objects.first()  


class ComposerListView(APIView):
    """
    GET /composers/ — список композиторов (только действующих)
    POST /composers/ — добавление нового композитора (без изображения)
    """
    def get(self, request):
        composers = Composer.objects.filter(status=1)
        name = request.query_params.get('name', None)
        if name:
            composers = composers.filter(name__icontains=name)
        serializer = ComposerSerializer(composers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data.copy()
        data['status'] = 1
        serializer = ComposerSerializer(data=data)
        if serializer.is_valid():
            composer = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class ComposerDetailView(APIView):
    """
    GET /composers/<id>/ — детали одного композитора
    PUT /composers/<id>/ — изменение композитора
    DELETE /composers/<id>/ — удаление (мягкое + удаление изображения из MinIO)
    """

    def get(self, request, pk):
        composer = get_object_or_404(Composer, pk=pk, status=1)
        serializer = ComposerSerializer(composer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        composer = get_object_or_404(Composer, pk=pk, status=1)
        data = request.data.copy()
        if 'status' in data:
            del data['status']
        serializer = ComposerSerializer(composer, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        composer = get_object_or_404(Composer, pk=pk, status=1)
        if composer.image:
            delete_image_from_minio(composer.image)
        composer.status = 2
        composer.save()
        return Response({"message": "Composer deleted"}, status=status.HTTP_200_OK)

class ComposerImageUploadView(APIView):
    """
    POST /composers/<id>/image/ — загрузка изображения для композитора
    Старое изображение удаляется, новое загружается в MinIO.
    Название генерируется на латинице.
    """
    def post(self, request, pk):
        composer = get_object_or_404(Composer, pk=pk, status=1)
        if 'image' not in request.FILES:
            return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)
        if composer.image:
            delete_image_from_minio(composer.image)
        file = request.FILES['image']
        image_url = upload_image_to_minio(file)
        composer.image = image_url
        composer.save()
        return Response({
            'message': 'Image uploaded successfully',
            'image_url': image_url
        }, status=status.HTTP_200_OK)
    

class AddComposerToDraftView(APIView):
    """
    POST /composers/<id>/add-to-draft/

    Добавляет композитора в заявку-черновик текущего пользователя (создателя)
    """

    def post(self, request, pk):
        composer = get_object_or_404(Composer, pk=pk, status=1)
        creator = get_creator()
        if not creator:
            return Response(
                {'error': 'Создатель (владелец) не найден. Создайте хотя бы одного пользователя.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        draft_analysis, created = Analysis.objects.get_or_create(
            owner=creator,
            status=1,
            defaults={
                'date_created': timezone.now(),
               
            }
        )

        if ComposerAnalysis.objects.filter(
            analysis=draft_analysis,
            composer=composer
        ).exists():
            return Response(
                {'error': 'Композитор уже добавлен в черновик'},
                status=status.HTTP_400_BAD_REQUEST
            )

        ComposerAnalysis.objects.create(
            analysis=draft_analysis,
            composer=composer,
            length=0,   
            value=0    
        )

        return Response({
            'message': 'Композитор успешно добавлен в черновик',
            'draft_id': draft_analysis.id,
            'composer_id': composer.id
        }, status=status.HTTP_201_CREATED)
    

class AnalysisListView(APIView):
    """
    GET /analyses/ — список анализов (не удалённых)
    Фильтрация:
      - по статусу: ?status=...
      - по диапазону даты формирования: ?start_date=...&end_date=...
    """
    def get(self, request):
        analyses = Analysis.objects.exclude(status__in=[1, 5])

        status_filter = request.query_params.get('status', None)
        if status_filter:
            analyses = analyses.filter(status=status_filter)

        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        if start_date:
            analyses = analyses.filter(date_formation__gte=start_date)
        if end_date:
            analyses = analyses.filter(date_formation__lte=end_date)

        data = []
        for analysis in analyses:
            data.append({
                "id": analysis.id,
                "status": analysis.get_status_display(),
                "date_created": analysis.date_created,
                "date_formation": analysis.date_formation,
                "date_complete": analysis.date_complete,
                "owner": analysis.owner.username if analysis.owner else None,
                "moderator": analysis.moderator.username if analysis.moderator else None,
            })

        return Response(data, status=status.HTTP_200_OK)


class AnalysisDetailView(APIView):
    """
    GET /analyses/<id>/ — детали анализа, включая композиторов
    """
    def get(self, request, pk):
        analysis = get_object_or_404(Analysis, pk=pk)
        if analysis.status == 5:  
            return Response({"error": "Analysis not found"}, status=status.HTTP_404_NOT_FOUND)

        composers_data = []
        composer_analyses = ComposerAnalysis.objects.filter(analysis=analysis)
        for ca in composer_analyses:
            composer = ca.composer
            composers_data.append({
                "id": composer.id,
                "name": composer.name,
                "description": composer.description,
                "price": composer.price,
                "image": composer.image if composer.image else None,
                "length": ca.length,
                "value": ca.value,
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
    
    def put(self, request, pk):
        analysis = get_object_or_404(Analysis, pk=pk)
        if analysis.status == 5: 
            return Response({"error": "Analysis not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        if 'status' in data:
            del data['status']

        serializer = AnalysisSerializer(analysis, data=data, partial=True)  
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        analysis = get_object_or_404(Analysis, pk=pk)
        analysis.status = 5  
        analysis.save()
        analysis.date_formation = timezone.now() 
        return Response({"message": "Analysis deleted"}, status=status.HTTP_200_OK)

class AnalysisFormulateView(APIView):
    """
    PUT /analyses/<id>/formulate/ — создатель устанавливает дату формирования
    Проверяет: есть ли хотя бы один композитор в анализе
    """

    def put(self, request, pk):
        analysis = get_object_or_404(Analysis, pk=pk)
        if analysis.status != 1:  
            return Response({"error": "Only draft analysis can be formulated"}, status=status.HTTP_400_BAD_REQUEST)

        if not ComposerAnalysis.objects.filter(analysis=analysis).exists():
            return Response({"error": "At least one composer must be added to the analysis"}, status=status.HTTP_400_BAD_REQUEST)

        analysis.date_formation = timezone.now()
        analysis.status = 2  
        analysis.save()

        return Response({
            "message": "Analysis formulated successfully",
            "status": analysis.get_status_display(),
            "date_formation": analysis.date_formation
        }, status=status.HTTP_200_OK)


class AnalysisCompleteOrRejectView(APIView):
    """
    PUT /analyses/<id>/complete-or-reject/ — модератор завершает или отклоняет заявку
    Ожидает: {"action": "complete" | "reject", "moderator_id": int}
    При завершении: рассчитывает value для каждого ComposerAnalysis
    """

    def put(self, request, pk):
        analysis = get_object_or_404(Analysis, pk=pk)
        if analysis.status != 2:  
            return Response({"error": "Analysis must be in 'In progress' status"}, status=status.HTTP_400_BAD_REQUEST)

        action = request.data.get('action')
        moderator_id = request.data.get('moderator_id')

        if not action or action not in ['complete', 'reject']:
            return Response({"error": "'action' must be 'complete' or 'reject'"}, status=status.HTTP_400_BAD_REQUEST)

        if not moderator_id:
            return Response({"error": "'moderator_id' is required"}, status=status.HTTP_400_BAD_REQUEST)

        moderator = get_object_or_404(User, pk=moderator_id)

        analysis.moderator = moderator
        analysis.date_complete = timezone.now()

        if action == 'complete':
            analysis.status = 3  
            for ca in ComposerAnalysis.objects.filter(analysis=analysis):
                ca.value = ca.length * ca.composer.price // 100
                ca.save()
        else:  
            analysis.status = 4 

        analysis.save()

        return Response({
            "message": f"Analysis {action}d successfully",
            "status": analysis.get_status_display(),
            "moderator": moderator.username,
            "date_complete": analysis.date_complete
        }, status=status.HTTP_200_OK)

class CartIconView(APIView):
        """
        GET /cart-icon/ — иконка корзины: ID черновика и количество композиторов в нём
        Черновик = Analysis со статусом 1 ("Введён") и owner = текущий создатель (singleton)
        """
        def get(self, request):
            creator = get_creator()
            if not creator:
                return Response({"error": "No creator user found"}, status=status.HTTP_404_NOT_FOUND)

            draft_analysis = Analysis.objects.filter(
                owner=creator,
                status=1
            ).first()

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
        


class ComposerAnalysisDeleteView(APIView):
    """
    DELETE /analyses/<analysis_id>/composer/<composer_id>/
    Удаляет композитора из заявки (без PK м-м)
    """
    def delete(self, request, analysis_id, composer_id):
        try:
            ca = ComposerAnalysis.objects.get(
                analysis_id=analysis_id,
                composer_id=composer_id
            )
            ca.delete()
            return Response({"message": "Composer removed from analysis"}, status=status.HTTP_200_OK)
        except ComposerAnalysis.DoesNotExist:
            return Response({"error": "Composer not found in this analysis"}, status=status.HTTP_404_NOT_FOUND)


class ComposerAnalysisUpdateView(APIView):
    """
    PUT /analyses/<analysis_id>/composer/<composer_id>/
    Изменяет length и/или value для связи м-м
    """
    def put(self, request, analysis_id, composer_id):
        try:
            ca = ComposerAnalysis.objects.get(
                analysis_id=analysis_id,
                composer_id=composer_id
            )
        except ComposerAnalysis.DoesNotExist:
            return Response({"error": "Composer not found in this analysis"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()

        if 'length' in data:
            ca.length = int(data['length'])
        if 'value' in data:
            ca.value = int(data['value'])

        ca.save()

        return Response({
            "message": "ComposerAnalysis updated",
            "length": ca.length,
            "value": ca.value
        }, status=status.HTTP_200_OK)
    


class UserRegisterView(APIView):
    """
    POST /register/ — регистрация нового пользователя

    
    """

    permission_classes = [AllowAny] 
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "message": "User registered successfully",
                "user": UserProfileSerializer(user).data,
                "token": token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """
    POST /login/ — аутентификация
    Возвращает токен
    """
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "message": "Login successful",
                "token": token.key,
                "user": UserProfileSerializer(user).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(APIView):
    """
    POST /logout/ — деавторизация
    Удаляет токен текущего пользователя
    """
    def post(self, request):
        if hasattr(request.user, 'auth_token'):
            request.user.auth_token.delete()
        return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    """
    GET /profile/ — получить профиль текущего пользователя
    PUT /profile/ — обновить профиль
    Требует аутентификации
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)