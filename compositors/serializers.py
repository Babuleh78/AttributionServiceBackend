from rest_framework import serializers
from .models import Composer, Analysis, ComposerAnalysis, User  
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed


class IntervalStatsField(serializers.Field):
    def to_representation(self, value):
        return [
            {
                "IntervalGroup": "Унисоны и секунды",
                "Frequency": float(value.unisons_seconds_freq) if value.unisons_seconds_freq is not None else None,
                "StdDev": float(value.unisons_seconds_stddev) if value.unisons_seconds_stddev is not None else None,
            },
            {
                "IntervalGroup": "Терции",
                "Frequency": float(value.thirds_freq) if value.thirds_freq is not None else None,
                "StdDev": float(value.thirds_stddev) if value.thirds_stddev is not None else None,
            },
            {
                "IntervalGroup": "Кварты и квинты",
                "Frequency": float(value.fourths_fifths_freq) if value.fourths_fifths_freq is not None else None,
                "StdDev": float(value.fourths_fifths_stddev) if value.fourths_fifths_stddev is not None else None,
            },
            {
                "IntervalGroup": "Сексты и септимы",
                "Frequency": float(value.sixths_sevenths_freq) if value.sixths_sevenths_freq is not None else None,
                "StdDev": float(value.sixths_sevenths_stddev) if value.sixths_sevenths_stddev is not None else None,
            },
            {
                "IntervalGroup": "Октавы",
                "Frequency": float(value.octaves_freq) if value.octaves_freq is not None else None,
                "StdDev": float(value.octaves_stddev) if value.octaves_stddev is not None else None,
            },
        ]


class AnonymousIntervalStatsField(serializers.Field):
    def to_representation(self, value):
        return [
            {
                "IntervalGroup": "Унисоны и секунды",
                "Frequency": float(value.anon_unisons_seconds_freq) if value.anon_unisons_seconds_freq is not None else None,
                "StdDev": float(value.anon_unisons_seconds_stddev) if value.anon_unisons_seconds_stddev is not None else None,
            },
            {
                "IntervalGroup": "Терции",
                "Frequency": float(value.anon_thirds_freq) if value.anon_thirds_freq is not None else None,
                "StdDev": float(value.anon_thirds_stddev) if value.anon_thirds_stddev is not None else None,
            },
            {
                "IntervalGroup": "Кварты и квинты",
                "Frequency": float(value.anon_fourths_fifths_freq) if value.anon_fourths_fifths_freq is not None else None,
                "StdDev": float(value.anon_fourths_fifths_stddev) if value.anon_fourths_fifths_stddev is not None else None,
            },
            {
                "IntervalGroup": "Сексты и септимы",
                "Frequency": float(value.anon_sixths_sevenths_freq) if value.anon_sixths_sevenths_freq is not None else None,
                "StdDev": float(value.anon_sixths_sevenths_stddev) if value.anon_sixths_sevenths_stddev is not None else None,
            },
            {
                "IntervalGroup": "Октавы",
                "Frequency": float(value.anon_octaves_freq) if value.anon_octaves_freq is not None else None,
                "StdDev": float(value.anon_octaves_stddev) if value.anon_octaves_stddev is not None else None,
            },
        ]


class ComposerSerializer(serializers.ModelSerializer):
    interval_stats = IntervalStatsField(source='*')  

    class Meta:
        model = Composer
        fields = [
            'id', 'name', 'biography',  
            'portrait_url',  
            'analyzed_works', 'total_intervals',
            'period', 'polyphony_type', 'interval_stats'
        ]
        read_only_fields = ['status']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['image'] = data.pop('portrait_url', None)
        return data


class ComposerAnalysisSerializer(serializers.ModelSerializer):
    composer = ComposerSerializer(read_only=True)
    anonymous_interval_stats = AnonymousIntervalStatsField(source='*')

    class Meta:
        model = ComposerAnalysis
        fields = [
            'composer',
            'anonymous_interval_stats',
            'potential_coincidence'
        ]


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


class FullAnalysisSerializer(serializers.ModelSerializer):
    owner_login = serializers.SerializerMethodField()
    moderator_login = serializers.SerializerMethodField()
    composers = ComposerAnalysisSerializer(
        source='composeranalysis_set',
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
        