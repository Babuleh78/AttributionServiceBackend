from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'IntervalAttribution_app'
    verbose_name = "Атрибуция музыкального произведения по частотности интервалов"
