from django.urls import path
from . import views

urlpatterns = [
    path('', views.listings, name='listings'),
    path('search/', views.search, name='search'),
    path('create/', views.create_listing, name='create-listing'),
    path('<slug:slug>/', views.listing_detail, name='listing-detail'),
]

