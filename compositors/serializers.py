from rest_framework import serializers
from .models import Composer, Analysis, ComposerAnalysis
from .models import CustomUser 
from django.contrib.auth import authenticate
from collections import OrderedDict
from django.contrib.auth.password_validation import validate_password

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

    def get_fields(self):
        fields = super().get_fields()
        for field in fields.values():
            field.required = False
        return fields

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['image'] = data.pop('portrait_url', None)
        return data

class ComposerAnalysisSerializer(serializers.ModelSerializer):
    composer = ComposerSerializer(read_only=True)
    
    class Meta:
        model = ComposerAnalysis
        fields = [
            'composer',
            'anon_unisons_seconds_freq',
            'anon_thirds_freq', 
            'anon_fourths_fifths_freq',
            'anon_sixths_sevenths_freq',
            'anon_octaves_freq',
            'potential_coincidence'
        ]


class AnalysisSerializer(serializers.ModelSerializer):
    owner_login = serializers.SerializerMethodField()
    moderator_login = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()  

    class Meta:
        model = Analysis
        fields = [
            'id', 'status',  # теперь status — текстовое значение
            'date_created', 'date_formation', 'date_complete',
            'owner_login', 'moderator_login'
        ]

    def get_fields(self):
        fields = super().get_fields()
        for field in fields.values():
            field.required = False
        return fields

    def get_owner_login(self, obj):
        return obj.owner.email if obj.owner else None

    def get_moderator_login(self, obj):
        return obj.moderator.email if obj.moderator else None

    def get_status(self, obj):
        return obj.get_status_display()  




class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации нового пользователя.
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = CustomUser
        fields = ('email', 'password')
        extra_kwargs = {
            'is_staff': {'default': False},
            'is_superuser': {'default': False},
        }

    def validate(self, attrs):
        return attrs

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            is_staff=validated_data.get('is_staff', False),
            is_superuser=validated_data.get('is_superuser', False),
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Сериализатор для входа пользователя.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if not user:
                raise serializers.ValidationError('Неверные учетные данные.')
        else:
            raise serializers.ValidationError('Должны быть указаны "email" и "password".')

        attrs['user'] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('email', 'is_staff', 'is_superuser')
        read_only_fields = ('email',)

    def get_fields(self):
        fields = super().get_fields()
        for field in fields.values():
            field.required = False
        return fields