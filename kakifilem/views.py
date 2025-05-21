from django.shortcuts import render, redirect
from django.conf import settings

def index(request):
    return render(request, 'index.html')

def countdown(request):
    telegram_id = request.GET.get('telegram_id')
    if not telegram_id:
        # If no telegram_id, redirect to bot with token
        token = request.GET.get('token')
        if token:
            return redirect(f'https://t.me/KakifilemBot?start={token}')
            
    context = {
        'bot_api_url': settings.BOT_API_URL,
        'telegram_id': telegram_id,
        'request': request
    }
    return render(request, 'countdown.html', context)
