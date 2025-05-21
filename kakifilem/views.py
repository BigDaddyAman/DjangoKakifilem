from django.shortcuts import render
from django.conf import settings

def index(request):
    return render(request, 'index.html')

def countdown(request):
    context = {
        'bot_api_url': settings.BOT_API_URL,
        'request': request  # Pass request to template
    }
    return render(request, 'countdown.html', context)
