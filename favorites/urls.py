from django.urls import path
from . import views

urlpatterns = [
    path('', views.favorites_list, name='favorites'),
    path('toggle/', views.toggle_favorite, name='toggle-favorite'),
    path('check/', views.check_favorite, name='check-favorite'),
    path('count/', views.get_favorites_count, name='favorites-count'),
    path('remove/<int:favorite_id>/', views.remove_favorite, name='remove-favorite'),
]
