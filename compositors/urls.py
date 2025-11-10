from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'attributionUser', views.UserViewSet, basename='user')


urlpatterns = [
    

    path('composers/', views.ComposerListView.as_view(), name='composer-list'),
    path('composers/<int:pk>/', views.ComposerDetailView.as_view(), name='composer-detail'),
    path('composers/<int:pk>/image/', views.ComposerImageUploadView.as_view(), name='composer-image-upload'),
    path('composers/<int:pk>/add-to-draft/', views.AddComposerToDraftView.as_view(), name='composer-add-to-draft'),
    
    # Анализы
    path('attributionAnalyses/', views.AnalysisListView.as_view(), name='analysis-list'),
    path('attributionAnalyses/<int:pk>/', views.AnalysisDetailView.as_view(), name='analysis-detail'),
    path('attributionAnalyses/<int:pk>/formulateAnalysis/', views.AnalysisFormulateView.as_view(), name='analysis-formulate'),
    path('attributionAnalyses/<int:pk>/complete-or-reject/', views.AnalysisCompleteOrRejectView.as_view(), name='analysis-complete-or-reject'),
    
    # Корзина
    path('attributionAnalyses/attributionDraft/', views.CartIconView.as_view(), name='cart-icon'),

    # М-М:  
    path('attributionAnalyses/<int:analysis_id>/composer/<int:composer_id>/',  views.ComposerAnalysisUpdateView.as_view(), name='composer-analysis-update'),
    path('attributionAnalyses/<int:analysis_id>/composer/<int:composer_id>/delete/', views.ComposerAnalysisDeleteView.as_view(), name='composer-analysis-delete'),

    # Пользователь
    path('', include(router.urls)),
    # path('attributionUser/register/', views.UserRegisterView.as_view(), name='user-register'),
    # path('attributionUser/login/',  views.login_view, name='login'),
    # path('attributionUser/logout/', views.logout_view, name='user-logout'),
    # path('attributionUser/profile/', views.UserProfileView.as_view(), name='user-profile'),

]