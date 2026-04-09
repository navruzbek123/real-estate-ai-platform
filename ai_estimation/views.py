from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status

from .models import AIEstimationHistory
from .ml.predictor import estimate_price


class AIEstimateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user

        can_use, limit_type = user.can_use_ai_estimation()
        if not can_use:
            if limit_type == 'kunlik_limit':
                return Response({
                    'error': 'Достигнут дневной лимит AI оценок',
                    'limit_type': 'daily',
                    'daily_limit': user.get_daily_ai_limit(),
                    'used_today': user.ai_estimations_today
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            else:
                return Response({
                    'error': 'Достигнут месячный лимит AI оценок',
                    'limit_type': 'monthly',
                    'monthly_limit': user.get_monthly_ai_limit(),
                    'used_this_month': user.ai_estimations_this_month
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        try:
            area = int(request.data.get('area', 0))
            rooms = int(request.data.get('rooms', 1))
            city = request.data.get('city', 'Москва')
            floor = int(request.data.get('floor', 1))
            total_floors = int(request.data.get('total_floors', 5))
            home_type = request.data.get('home_type', 'Condo')

            if area <= 0 or area > 10000:
                return Response({'error': 'Площадь должна быть от 1 до 10000 м²'}, status=status.HTTP_400_BAD_REQUEST)
            if rooms < 1 or rooms > 20:
                return Response({'error': 'Количество комнат должно быть от 1 до 20'}, status=status.HTTP_400_BAD_REQUEST)

            result = estimate_price(area, rooms, city, floor, total_floors, home_type)

            discount = False
            if user.role in ['agent', 'premium']:
                result['price'] = int(result['price'] * 0.9)
                discount = True

            AIEstimationHistory.objects.create(
                user=user,
                area=area,
                rooms=rooms,
                city=city,
                floor=floor,
                total_floors=total_floors,
                property_type='apartment',
                home_type=home_type,
                estimated_price=result['price'],
                confidence=result['confidence'],
                is_premium_user=user.role in ['premium', 'agent'],
                discount_applied=discount
            )

            user.increment_ai_estimation()

            return Response({
                'success': True,
                'estimated_price': result['price'],
                'price_per_sqm': result['price_per_sqm'],
                'confidence': int(result['confidence'] * 100),
                'city': city,
                'area': area,
                'rooms': rooms,
                'floor': floor,
                'home_type': home_type,
                'discount_applied': discount,
                'remaining_daily': user.get_daily_ai_limit() - user.ai_estimations_today,
                'remaining_monthly': user.get_monthly_ai_limit() - user.ai_estimations_this_month if user.get_monthly_ai_limit() != float('inf') else None
            })

        except Exception as e:
            return Response({'error': f'Ошибка: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AIEstimatePublicView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            area = int(request.data.get('area', 0))
            rooms = int(request.data.get('rooms', 1))
            city = request.data.get('city', 'Москва')
            floor = int(request.data.get('floor', 1))
            total_floors = int(request.data.get('total_floors', 5))
            home_type = request.data.get('home_type', 'Condo')

            if area <= 0:
                return Response({'error': 'Площадь должна быть положительной'}, status=status.HTTP_400_BAD_REQUEST)

            result = estimate_price(area, rooms, city, floor, total_floors, home_type)

            return Response({
                'success': True,
                'estimated_price': result['price'],
                'price_per_sqm': result['price_per_sqm'],
                'confidence': int(result['confidence'] * 100),
                'city': city,
                'note': 'Для сохранения истории войдите в аккаунт'
            })

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AIEstimateHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        history = AIEstimationHistory.objects.filter(user=request.user)[:50]
        data = [{
            'id': h.id,
            'area': h.area,
            'rooms': h.rooms,
            'city': h.city,
            'estimated_price': h.estimated_price,
            'confidence': int(h.confidence * 100),
            'created_at': h.created_at.strftime('%d.%m.%Y %H:%M')
        } for h in history]

        return Response({
            'history': data,
            'stats': {
                'total_estimations': request.user.ai_estimations_this_month,
                'daily_limit': request.user.get_daily_ai_limit(),
                'monthly_limit': request.user.get_monthly_ai_limit(),
                'used_today': request.user.ai_estimations_today
            }
        })
