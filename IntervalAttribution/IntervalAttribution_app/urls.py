# bmstu_lab/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('composers', views.get_composers_with_stats, name='composers'),
    path('composer/<int:id>', views.get_composer_interval_profile, name='composer_detail'),
    path('attribution-candidates', views.view_attribution_results, name='attribution_candidates'),
]