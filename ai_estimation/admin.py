from django.contrib import admin
from .models import AIEstimationHistory


@admin.register(AIEstimationHistory)
class AIEstimationHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'area', 'rooms', 'city', 'estimated_price', 'confidence', 'created_at')
    list_display_links = ('id', 'user')
    search_fields = ('user__email', 'city')
    list_filter = ('created_at', 'is_premium_user')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)
