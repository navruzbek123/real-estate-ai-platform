from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from .models import Message
from accounts.models import Notification


@login_required
def inbox(request):
    messages_list = Message.objects.filter(recipient=request.user).select_related('sender', 'listing')
    paginator = Paginator(messages_list, 20)
    page = request.GET.get('page')
    messages_page = paginator.get_page(page)

    unread_count = messages_list.filter(is_read=False).count()

    context = {
        'messages': messages_page,
        'unread_count': unread_count,
        'section': 'inbox'
    }
    return render(request, 'messages/inbox.html', context)


@login_required
def sent(request):
    messages_list = Message.objects.filter(sender=request.user).select_related('recipient', 'listing')
    paginator = Paginator(messages_list, 20)
    page = request.GET.get('page')
    messages_page = paginator.get_page(page)

    context = {
        'messages': messages_page,
        'section': 'sent'
    }
    return render(request, 'messages/sent.html', context)


@login_required
def compose(request):
    listing_id = request.GET.get('listing')
    recipient_id = request.GET.get('recipient')

    context = {
        'listing_id': listing_id,
        'recipient_id': recipient_id
    }
    return render(request, 'messages/compose.html', context)


@login_required
@csrf_protect
def send_message(request):
    if request.method == 'POST':
        recipient_id = request.POST.get('recipient_id')
        listing_id = request.POST.get('listing_id')
        subject = request.POST.get('subject', '')
        body = request.POST.get('body', '')

        if not recipient_id:
            return JsonResponse({'success': False, 'error': 'Укажите получателя'})

        if not body.strip():
            return JsonResponse({'success': False, 'error': 'Введите текст сообщения'})

        from accounts.models import UserAccount
        from listings.models import Listing

        recipient = get_object_or_404(UserAccount, id=recipient_id)
        listing = None
        if listing_id:
            listing = get_object_or_404(Listing, id=listing_id)

        message = Message.objects.create(
            sender=request.user,
            recipient=recipient,
            listing=listing,
            subject=subject or f'Сообщение о: {listing.title}' if listing else 'Без темы',
            body=body
        )

        Notification.objects.create(
            user=recipient,
            notification_type='message',
            title='Новое сообщение',
            message=f'{request.user.name} отправил вам сообщение',
            link=f'/messages/inbox/'
        )

        if recipient.profile.email_notifications:
            try:
                from django.core.mail import send_mail
                send_mail(
                    subject=f'Новое сообщение от {request.user.name}',
                    message=f'Вы получили новое сообщение: {body[:200]}',
                    from_email=None,
                    recipient_list=[recipient.email],
                    fail_silently=True
                )
            except Exception as e:
                print(f"Email error: {e}")

        return JsonResponse({'success': True, 'message_id': message.id})

    return JsonResponse({'success': False, 'error': 'Неверный метод'})


@login_required
def thread(request, message_id):
    message = get_object_or_404(Message, id=message_id)

    if message.recipient != request.user and message.sender != request.user:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden()

    if request.user == message.recipient:
        message.mark_as_read()

    messages_qs = Message.objects.filter(
        sender__in=[request.user, message.sender],
        recipient__in=[request.user, message.sender]
    ).filter(
        listing=message.listing
    ).order_by('created_at')

    paginator = Paginator(messages_qs, 50)
    page = request.GET.get('page')
    messages_page = paginator.get_page(page)

    context = {
        'message': message,
        'messages': messages_page,
        'other_user': message.sender if message.recipient == request.user else message.recipient
    }
    return render(request, 'messages/thread.html', context)


@login_required
def ajax_mark_read(request):
    if request.method == 'POST':
        message_id = request.POST.get('message_id')
        message = get_object_or_404(Message, id=message_id, recipient=request.user)
        message.mark_as_read()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


@login_required
def ajax_delete_message(request):
    if request.method == 'POST':
        message_id = request.POST.get('message_id')
        message = get_object_or_404(Message, id=message_id)

        if message.sender == request.user or message.recipient == request.user:
            message.delete()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Нет прав'})

    return JsonResponse({'success': False})


class MessageAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        inbox_qs = Message.objects.filter(recipient=request.user)
        sent_qs = Message.objects.filter(sender=request.user)

        unread = inbox_qs.filter(is_read=False).count()

        return Response({
            'inbox_count': inbox_qs.count(),
            'sent_count': sent_qs.count(),
            'unread_count': unread
        })


class SendMessageAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        recipient_id = request.data.get('recipient_id')
        listing_id = request.data.get('listing_id')
        subject = request.data.get('subject', '')
        body = request.data.get('body', '')

        if not recipient_id:
            return Response({'error': 'Укажите получателя'}, status=400)

        if not body.strip():
            return Response({'error': 'Введите текст сообщения'}, status=400)

        from accounts.models import UserAccount
        from listings.models import Listing

        recipient = get_object_or_404(UserAccount, id=recipient_id)
        listing = None
        if listing_id:
            listing = get_object_or_404(Listing, id=listing_id)

        message = Message.objects.create(
            sender=request.user,
            recipient=recipient,
            listing=listing,
            subject=subject or f'Сообщение о: {listing.title}' if listing else 'Без темы',
            body=body
        )

        Notification.objects.create(
            user=recipient,
            notification_type='message',
            title='Новое сообщение',
            message=f'{request.user.name} отправил вам сообщение',
            link=f'/messages/inbox/'
        )

        return Response({
            'success': True,
            'message_id': message.id
        })
