from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from .models import UserAccount, Notification, UserProfile


def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if not all([name, email, password, password2]):
            messages.error(request, 'Заполните все поля')
            return redirect('register')

        if password != password2:
            messages.error(request, 'Пароли не совпадают')
            return redirect('register')

        if len(password) < 6:
            messages.error(request, 'Пароль должен содержать минимум 6 символов')
            return redirect('register')

        if UserAccount.objects.filter(email=email).exists():
            messages.error(request, 'Пользователь с таким email уже существует')
            return redirect('register')

        user = UserAccount.objects.create_user(
            email=email,
            name=name,
            password=password
        )

        login(request, user)
        messages.success(request, 'Добро пожаловать!')
        return redirect('home')

    return render(request, 'accounts/register.html')


class SignupView(APIView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        password = request.data.get('password')
        password2 = request.data.get('password2')

        if not all([name, email, password, password2]):
            return Response({'error': 'Заполните все поля'}, status=status.HTTP_400_BAD_REQUEST)

        if password != password2:
            return Response({'error': 'Пароли не совпадают'}, status=status.HTTP_400_BAD_REQUEST)

        if len(password) < 6:
            return Response({'error': 'Пароль должен содержать минимум 6 символов'}, status=status.HTTP_400_BAD_REQUEST)

        if UserAccount.objects.filter(email=email).exists():
            return Response({'error': 'Пользователь с таким email уже существует'}, status=status.HTTP_400_BAD_REQUEST)

        user = UserAccount.objects.create_user(
            email=email,
            name=name,
            password=password
        )

        return Response({
            'success': 'Пользователь успешно создан',
            'user_id': user.id
        }, status=status.HTTP_201_CREATED)


def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            messages.error(request, 'Введите email и пароль')
            return redirect('login')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.name}!')

            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, 'Неверный email или пароль')
            return redirect('login')

    return render(request, 'accounts/login.html')


def user_logout(request):
    logout(request)
    messages.success(request, 'Вы вышли из аккаунта')
    return redirect('home')


@login_required
def profile(request):
    user = request.user

    notifications = Notification.objects.filter(user=user, is_read=False)[:10]

    favorite_count = user.favorites.count()
    listing_count = user.listings.count()

    ai_stats = {
        'today': user.ai_estimations_today,
        'daily_limit': user.get_daily_ai_limit(),
        'monthly': user.ai_estimations_this_month,
        'monthly_limit': user.get_monthly_ai_limit()
    }

    context = {
        'user': user,
        'notifications': notifications,
        'notification_count': notifications.count(),
        'favorite_count': favorite_count,
        'listing_count': listing_count,
        'ai_stats': ai_stats,
        'profile': user.profile if hasattr(user, 'profile') else None
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user

        user.name = request.POST.get('name', user.name)
        user.phone = request.POST.get('phone', user.phone)
        user.bio = request.POST.get('bio', user.bio)

        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']

        user.save()

        if hasattr(user, 'profile'):
            profile = user.profile
            profile.dark_mode = request.POST.get('dark_mode') == 'on'
            profile.notifications_enabled = request.POST.get('notifications_enabled') == 'on'
            profile.email_notifications = request.POST.get('email_notifications') == 'on'
            profile.save()

        messages.success(request, 'Профиль обновлен')
        return redirect('profile')

    return redirect('profile')


@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user)[:50]

    context = {
        'notifications': notifications
    }
    return render(request, 'accounts/notifications.html', context)


@login_required
def mark_notification_read(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.mark_as_read()
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Не найдено'})


@login_required
def mark_all_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'success': True})


@login_required
@csrf_protect
def update_dark_mode(request):
    if request.method == 'POST':
        dark_mode = request.POST.get('dark_mode') == 'true'

        if hasattr(request.user, 'profile'):
            request.user.profile.dark_mode = dark_mode
            request.user.profile.save(update_fields=['dark_mode'])
            return JsonResponse({'success': True, 'dark_mode': dark_mode})

        return JsonResponse({'success': False, 'error': 'Профиль не найден'})

    return JsonResponse({'success': False})


class UserProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'role': user.role,
            'role_display': user.get_role_display_name(),
            'phone': user.phone,
            'avatar': user.avatar.url if user.avatar else None,
            'bio': user.bio,
            'date_joined': user.date_joined.strftime('%d.%m.%Y'),
            'ai_stats': {
                'today': user.ai_estimations_today,
                'daily_limit': user.get_daily_ai_limit(),
                'monthly': user.ai_estimations_this_month,
                'monthly_limit': user.get_monthly_ai_limit()
            },
            'listing_limit': user.get_listing_limit(),
            'profile': {
                'dark_mode': user.profile.dark_mode if hasattr(user, 'profile') else False,
                'notifications_enabled': user.profile.notifications_enabled if hasattr(user, 'profile') else True,
            } if hasattr(user, 'profile') else None
        }
        return Response(data)


class ChangeRoleAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        user_id = request.data.get('user_id')
        new_role = request.data.get('role')

        if not user_id or not new_role:
            return Response({'error': 'Укажите user_id и role'}, status=status.HTTP_400_BAD_REQUEST)

        if new_role not in ['admin', 'agent', 'premium', 'free']:
            return Response({'error': 'Неверная роль'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = UserAccount.objects.get(id=user_id)
            user.role = new_role
            user.save(update_fields=['role'])

            return Response({
                'success': True,
                'user_id': user.id,
                'new_role': new_role
            })
        except UserAccount.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)
