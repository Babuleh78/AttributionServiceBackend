from django.urls import path
from IntervalAttribution_app import views

urlpatterns = [
    path("composers", views.get_composers_with_stats, name="composers"),
    path("composer/<int:id>/", views.get_composer_interval_profile, name="composer_detail"),
    path("attribution-results/", views.view_attribution_results, name="attribution_results"),
]
