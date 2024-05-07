from django.urls import path
from .views import register_user,logout_user,login_user
from face import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('register/', register_user, name='register'),
    path('', login_user, name='login'),
    path('logout/', logout_user, name='logout'),


    path('admin-dashboard/', views.admin_dashboard_view, name='admin-dashboard'), 


    path('moderator-dashboard/', views.moderator_dashboard_view, name='moderator-dashboard'), 
    path('profile-view/', views.profile_view, name='profile-view'), 
    path('check-emotion/', views.check_emotion_view, name='check-emotion'), 
    path('emotion-detection/', views.emotion_detection_view, name='emotion-detection'), 
    path('capture-and-analyze/', views.capture_and_analyze, name='capture_and_analyze'),
    # path('analyze-emotions/', views.analyze_emotions, name='analyze_emotions'), 

    path('view_emotions/', views.view_emotions, name='view_emotions'),


    path('detect-emotions/', views.detect_emotions, name='detect_emotions'),
    path('emotion-view/', views.emotion_data_view, name='emotion-view'),
    path('calender-view/', views.calender_view, name='calender-view'),
     path('export-emotion-data/', views.export_emotion_data, name='export_emotion_data'),

    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
