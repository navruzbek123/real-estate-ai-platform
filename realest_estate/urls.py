from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.shortcuts import render

from listings import views as listing_views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from ai_estimation.views import AIEstimateView, AIEstimateHistoryView, AIEstimatePublicView

# Asosiy URL patternlar
urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/accounts/', include('accounts.urls')),
    path('api/realtors/', include('realtors.urls')),
    path('api/listings/', include('listings.api_urls')),
    path('api/contacts/', include('contacts.urls')),
    path('api/ai/estimate/', AIEstimateView.as_view(), name='ai-estimate'),
    path('api/ai/estimate/public/', AIEstimatePublicView.as_view(), name='ai-estimate-public'),
    path('api/ai/history/', AIEstimateHistoryView.as_view(), name='ai-history'),
    
    # Frontend sahifalar
    path('accounts/', include('accounts.urls')),
    path('listings/', include('listings.urls')),
    path('messages/', include('user_messages.urls')),
    path('favorites/', include('favorites.urls')),
    path('payments/', include('payments.urls')),
    
    # AI estimation sahifasi
    path('ai-estimate/', lambda request: render(request, 'ai_estimation/estimate.html'), name='ai-estimate-public'),
    
    # Bosh sahifa
    path('', listing_views.index, name='home'),
]

# 🔴 MUHIM: STATIC VA MEDIA FAYLLAR - ENG OXIRIDA!
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 🔴 CATCH-ALL PATTERN - FAQAT BOSHQA HECH NARSA TOPILMASA!
if not settings.DEBUG:
    urlpatterns += [
        re_path(r'^.*', TemplateView.as_view(template_name='index.html')),
    ]