
from rest_framework import serializers
from .models import Composer, Analysis, ComposerAnalysis, User  
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed


class ComposerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Composer
        fields = [
            'id', 'name', 'description', 'price',
            'image', 'analyzed_works', 'total_intervals',
            'period', 'polyphony_type', 'interval_stats'
        ]
        read_only_fields = ['status']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.image:
            data['image'] = instance.image  
        return data

class AnalysisSerializer(serializers.ModelSerializer):
    """
    Сериализатор для анализа (Analysis)
    Включает информацию о владельце и модераторе (по логинам)
    """
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
    """
    Сериализатор для м-м связи (ComposerAnalysis)
    Включает поля length и value
    """
    composer = ComposerSerializer(read_only=True)  

    class Meta:
        model = ComposerAnalysis
        fields = ['composer', 'length', 'value']


class FullAnalysisSerializer(serializers.ModelSerializer):
    """
    Полный сериализатор для анализа — включает список композиторов с данными
    """
    owner_login = serializers.SerializerMethodField()
    moderator_login = serializers.SerializerMethodField()
    composers = ComposerAnalysisSerializer(many=True, read_only=True)

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