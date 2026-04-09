from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update-profile'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark-notification-read'),
    path('notifications/read-all/', views.mark_all_notifications_read, name='mark-all-read'),
    path('dark-mode/', views.update_dark_mode, name='update-dark-mode'),
    path('api/register/', views.SignupView.as_view(), name='api-register'),
    path('api/profile/', views.UserProfileAPIView.as_view(), name='api-profile'),
    path('api/change-role/', views.ChangeRoleAPIView.as_view(), name='api-change-role'),
]
