from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect

from .models import Favorite
from listings.models import Listing


@login_required
def favorites_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('listing', 'listing__realtor')
    paginator = Paginator(favorites, 12)
    page = request.GET.get('page')
    favorites_page = paginator.get_page(page)

    context = {
        'favorites': favorites_page,
        'count': favorites.count()
    }
    return render(request, 'favorites/favorites.html', context)


@login_required
@csrf_protect
def toggle_favorite(request):
    if request.method == 'POST':
        listing_id = request.POST.get('listing_id')

        if not listing_id:
            return JsonResponse({'success': False, 'error': 'ID объекта не указан'})

        try:
            listing = Listing.objects.get(id=listing_id)
        except Listing.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Объект не найден'})

        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            listing=listing
        )

        if not created:
            favorite.delete()
            return JsonResponse({
                'success': True,
                'action': 'removed',
                'is_favorite': False
            })

        return JsonResponse({
            'success': True,
            'action': 'added',
            'is_favorite': True,
            'favorite_id': favorite.id
        })

    return JsonResponse({'success': False, 'error': 'Неверный метод'})


@login_required
def check_favorite(request):
    listing_id = request.GET.get('listing_id')

    if not listing_id:
        return JsonResponse({'success': False, 'error': 'ID объекта не указан'})

    is_favorite = Favorite.objects.filter(
        user=request.user,
        listing_id=listing_id
    ).exists()

    return JsonResponse({
        'success': True,
        'is_favorite': is_favorite
    })


@login_required
def get_favorites_count(request):
    count = Favorite.objects.filter(user=request.user).count()
    return JsonResponse({
        'success': True,
        'count': count
    })


@login_required
def remove_favorite(request, favorite_id):
    try:
        favorite = Favorite.objects.get(id=favorite_id, user=request.user)
        favorite.delete()
        return JsonResponse({'success': True})
    except Favorite.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Не найдено'})
