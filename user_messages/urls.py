from django.urls import path
from . import views

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('sent/', views.sent, name='sent'),
    path('compose/', views.compose, name='compose'),
    path('send/', views.send_message, name='send-message'),
    path('thread/<int:message_id>/', views.thread, name='message-thread'),
    path('ajax/mark-read/', views.ajax_mark_read, name='ajax-mark-read'),
    path('ajax/delete/', views.ajax_delete_message, name='ajax-delete-message'),
    path('api/', views.MessageAPIView.as_view(), name='messages-api'),
    path('api/send/', views.SendMessageAPIView.as_view(), name='send-message-api'),
]
