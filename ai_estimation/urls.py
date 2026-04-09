from django.urls import path
from django.shortcuts import render
from .views import AIEstimateView, AIEstimateHistoryView, AIEstimatePublicView

urlpatterns = [
    path('estimate/', AIEstimateView.as_view(), name='ai-estimate'),
    path('estimate/public/', AIEstimatePublicView.as_view(), name='ai-estimate-public'),
    path('history/', AIEstimateHistoryView.as_view(), name='ai-history'),
    path('', lambda request: render(request, 'ai_estimation/estimate.html'), name='ai-estimate-page'),
]
