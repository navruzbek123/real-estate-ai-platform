from django.urls import path
from . import views

urlpatterns = [
    path('checkout/<int:listing_id>/', views.checkout, name='checkout'),
    path('success/', views.payment_success, name='payment-success'),
    path('cancel/', views.payment_cancel, name='payment-cancel'),
    path('history/', views.payment_history, name='payment-history'),
    path('api/create/', views.api_create_payment, name='api-create-payment'),
]
