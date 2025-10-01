from rest_framework import serializers
from .models import Composer, Analysis, ComposerAnalysis, User  
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed


class ComposerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Composer
        fields = [
            'id', 'name', 'biography',  # вместо 'description'
            'portrait_url',  # вместо 'image'
            'analyzed_works', 'total_intervals',
            'period', 'polyphony_type', 'interval_stats'
        ]
        read_only_fields = ['status']

    # Убираем to_representation — он не нужен, если portrait_url уже URLField
    # Если всё же нужно переименовать portrait_url → image в API:
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Опционально: если клиент ожидает поле 'image'
        data['image'] = data.pop('portrait_url', None)
        return data


class AnalysisSerializer(serializers.ModelSerializer):
    owner_login = serializers.SerializerMethodField()
    moderator_login = serializers.SerializerMethodField()

    class Meta:
        model = Analysis
        fields = [
            'id', 'status', 'date_created', 'date_formation', 'date_complete',
            'owner_login', 'moderator_login'
        ]

    def get_owner_login(self, obj):
        return obj.owner.username if obj.owner else None

    def get_moderator_login(self, obj):
        return obj.moderator.username if obj.moderator else None


class ComposerAnalysisSerializer(serializers.ModelSerializer):
    composer = ComposerSerializer(read_only=True)

    class Meta:
        model = ComposerAnalysis
        fields = [
            'composer',
            'anonymous_interval_stats',
            'potential_coincidence'
        ]


class FullAnalysisSerializer(serializers.ModelSerializer):
    owner_login = serializers.SerializerMethodField()
    moderator_login = serializers.SerializerMethodField()
    composers = ComposerAnalysisSerializer(
        source='composeranalysis_set',  # ← важно!
        many=True,
        read_only=True
    )

    class Meta:
        model = Analysis
        fields = [
            'id', 'status', 'date_created', 'date_formation', 'date_complete',
            'owner_login', 'moderator_login', 'composers'
        ]

    def get_owner_login(self, obj):
        return obj.owner.username if obj.owner else None

    def get_moderator_login(self, obj):
        return obj.moderator.username if obj.moderator else None


# Остальные сериализаторы без изменений
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user is None:
            raise AuthenticationFailed("Invalid credentials")
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['username']