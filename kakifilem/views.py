from django.shortcuts import render, redirect
from django.conf import settings
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'index.html')

def countdown(request):
    telegram_id = request.GET.get('telegram_id', '')
    token = request.GET.get('token')
    video_name = request.GET.get('videoName')
    
    # Convert 'None' string to empty string
    if telegram_id == 'None':
        telegram_id = ''
        
    logger.info(f"Countdown request - Token: {token}, Video: {video_name}, Telegram ID: {telegram_id}")
    
    context = {
        'bot_api_url': settings.BOT_API_URL,
        'telegram_id': telegram_id,
        'token': token,
        'video_name': video_name
    }
    return render(request, 'countdown.html', context)
