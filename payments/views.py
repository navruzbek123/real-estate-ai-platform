from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.conf import settings
from django.utils import timezone

from .models import PremiumTransaction
from .sberbank import SberbankClient
from listings.models import Listing


@login_required
def checkout(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)

    if listing.is_premium and listing.premium_until and listing.premium_until > timezone.now():
        messages.warning(request, 'Этот объект уже имеет статус Premium')
        return redirect('listing-detail', slug=listing.slug)

    if request.method == 'POST':
        amount = float(request.POST.get('amount', 5.00))
        days = int(request.POST.get('days', 7))

        transaction = PremiumTransaction.objects.create(
            user=request.user,
            listing=listing,
            amount=amount,
            description=f'Premium статус для: {listing.title} на {days} дней'
        )

        sberbank = SberbankClient()
        order_result = sberbank.create_order(
            amount=amount,
            description=transaction.description,
            order_id=str(transaction.id)
        )

        if order_result['success']:
            transaction.sberbank_order_id = order_result.get('order_id')
            transaction.save(update_fields=['sberbank_order_id'])
            return redirect(order_result['payment_url'])
        else:
            messages.error(request, f'Ошибка создания заказа: {order_result.get("error")}')
            return redirect('listing-detail', slug=listing.slug)

    context = {
        'listing': listing,
        'amount': 5.00,
        'days': 7
    }
    return render(request, 'payments/checkout.html', context)


@login_required
def payment_success(request):
    order_id = request.GET.get('orderId')
    status = request.GET.get('status')

    if order_id:
        try:
            transaction = PremiumTransaction.objects.get(sberbank_order_id=order_id)

            if status == 'success' or request.GET.get('success'):
                transaction.mark_as_completed()

                Notification.objects.create(
                    user=request.user,
                    notification_type='premium',
                    title='Premium активирован!',
                    message=f'Ваш объект "{transaction.listing.title}" получил Premium статус на 7 дней',
                    link=f'/listings/{transaction.listing.slug}/'
                )

                messages.success(request, 'Оплата прошла успешно! Premium статус активирован.')
            else:
                transaction.mark_as_failed()
                messages.error(request, 'Оплата не прошла. Попробуйте снова.')

        except PremiumTransaction.DoesNotExist:
            messages.error(request, 'Транзакция не найдена')
    else:
        messages.warning(request, 'Некорректные данные оплаты')

    return redirect('profile')


@login_required
def payment_cancel(request):
    order_id = request.GET.get('orderId')

    if order_id:
        try:
            transaction = PremiumTransaction.objects.get(sberbank_order_id=order_id)
            transaction.mark_as_failed()
        except PremiumTransaction.DoesNotExist:
            pass

    messages.warning(request, 'Оплата отменена')
    return redirect('profile')


@login_required
def payment_history(request):
    transactions = PremiumTransaction.objects.filter(user=request.user).select_related('listing')

    context = {
        'transactions': transactions
    }
    return render(request, 'payments/history.html', context)


@login_required
@csrf_protect
def api_create_payment(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)

        listing_id = data.get('listing_id')
        amount = float(data.get('amount', 5.00))
        days = int(data.get('days', 7))

        try:
            listing = Listing.objects.get(id=listing_id)
        except Listing.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Объект не найден'})

        transaction = PremiumTransaction.objects.create(
            user=request.user,
            listing=listing,
            amount=amount,
            description=f'Premium статус для: {listing.title} на {days} дней'
        )

        sberbank = SberbankClient()
        order_result = sberbank.create_order(
            amount=amount,
            description=transaction.description,
            order_id=str(transaction.id)
        )

        if order_result['success']:
            transaction.sberbank_order_id = order_result.get('order_id')
            transaction.save(update_fields=['sberbank_order_id'])
            return JsonResponse({
                'success': True,
                'payment_url': order_result['payment_url'],
                'transaction_id': transaction.id
            })
        else:
            return JsonResponse({
                'success': False,
                'error': order_result.get('error', 'Ошибка оплаты')
            })

    return JsonResponse({'success': False, 'error': 'Неверный метод'})


class Notification:
    pass
