from django.urls import path
from .views import *

urlpatterns = [
    path('composers', index, name="composers"),
    path('composers/<int:composer_id>/', composer_page, name="composer_page"),
    path('analysiss/<int:analysis_id>/', analysis_page, name="analysis_page"),
    path('composers/<int:composer_id>/add_to_analysis/', add_composer_to_draft_analysis, name="add_composer_to_draft_analysis"),
    path('analysiss/<int:analysis_id>/delete/', delete_analysis, name="delete_analysis")
    
]
