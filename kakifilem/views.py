from django.shortcuts import render
from django.conf import settings

def index(request):
    return render(request, 'index.html')

def countdown(request):
    context = {
        'bot_api_url': settings.BOT_API_URL,
        'telegram_id': request.GET.get('telegram_id', ''),  # Get telegram_id from URL
        'request': request
    }
    return render(request, 'countdown.html', context)
