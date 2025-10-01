from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Composer, Analysis, ComposerAnalysis
from .serializers import (
    ComposerSerializer,
    AnalysisSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from .utils import upload_image_to_minio, delete_image_from_minio


def get_creator():
    return User.objects.get(username="creator")  


class ComposerListView(APIView):
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
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ComposerDetailView(APIView):
    def get(self, request, pk):
        composer = get_object_or_404(Composer, pk=pk, status=1)
        serializer = ComposerSerializer(composer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        composer = get_object_or_404(Composer, pk=pk, status=1)
        data = request.data.copy()

        for field in ['status']:
            data.pop(field, None)
        serializer = ComposerSerializer(composer, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        composer = get_object_or_404(Composer, pk=pk, status=1)
        if composer.portrait_url:
            delete_image_from_minio(composer.portrait_url)
        composer.status = 2
        composer.save()
        return Response({"message": "Composer deleted"}, status=status.HTTP_200_OK)


class ComposerImageUploadView(APIView):
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
            anonymous_interval_stats=[],
            potential_coincidence=0
        )

        return Response({
            'message': 'Композитор успешно добавлен в черновик',
            'draft_id': draft_analysis.id,
            'composer_id': composer.id
        }, status=status.HTTP_201_CREATED)


class AnalysisListView(APIView):
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

    def put(self, request, pk):
        analysis = get_object_or_404(Analysis, pk=pk)
        if analysis.status == 5:
            return Response({"error": "Analysis not found"}, status=status.HTTP_404_NOT_FOUND)

        if not request.user.is_superuser:
            protected_fields = {'id', 'status', 'owner', 'moderator', 'date_created', 'date_formation', 'date_complete'}
        else:
            protected_fields = {'id', 'owner'}

        data = {k: v for k, v in request.data.items() if k not in protected_fields}

        serializer = AnalysisSerializer(analysis, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        analysis = get_object_or_404(Analysis, pk=pk)
        creator = get_creator()
        if analysis.status != 1 or analysis.owner != creator or request.user != creator:
            return Response({"error": "Only creator can delete draft"}, status=status.HTTP_403_FORBIDDEN)
        analysis.status = 5
        analysis.save()
        return Response({"message": "Analysis deleted"}, status=status.HTTP_200_OK)


class AnalysisFormulateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        analysis = get_object_or_404(Analysis, pk=pk)
        creator = get_creator()

        if analysis.owner != creator or request.user != creator:
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
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        analysis = get_object_or_404(Analysis, pk=pk)

        if not request.user.is_staff:
            return Response({"error": "Only moderators can complete or reject"}, status=status.HTTP_403_FORBIDDEN)
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


class ComposerAnalysisDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, analysis_id, composer_id):
        analysis = get_object_or_404(Analysis, pk=analysis_id)
        creator = get_creator()

        if analysis.owner != creator or request.user != creator:
            return Response({"error": "Only creator can modify draft"}, status=status.HTTP_403_FORBIDDEN)
        if analysis.status != 1:
            return Response({"error": "Can only modify draft"}, status=status.HTTP_400_BAD_REQUEST)

        ca = get_object_or_404(ComposerAnalysis, analysis_id=analysis_id, composer_id=composer_id)
        ca.delete()
        return Response({"message": "Composer removed from analysis"}, status=status.HTTP_200_OK)


class ComposerAnalysisUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, analysis_id, composer_id):
        analysis = get_object_or_404(Analysis, pk=analysis_id)
        creator = get_creator()

        if analysis.owner != creator or request.user != creator:
            return Response({"error": "Only creator can modify draft"}, status=status.HTTP_403_FORBIDDEN)
        if analysis.status != 1:
            return Response({"error": "Can only modify draft"}, status=status.HTTP_400_BAD_REQUEST)

        ca = get_object_or_404(ComposerAnalysis, analysis_id=analysis_id, composer_id=composer_id)

        ca.save()

        return Response({
            "message": "ComposerAnalysis updated",
            "anonymous_interval_stats": ca.anonymous_interval_stats,
            "potential_coincidence": ca.potential_coincidence
        }, status=status.HTTP_200_OK)


class UserRegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "message": "User registered successfully",
                "user": UserProfileSerializer(user).data,
                "token": token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "message": "Login successful",
                "token": token.key,
                "user": UserProfileSerializer(user).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        request.user.auth_token.delete()
        return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)


class UserProfileView(APIView):
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