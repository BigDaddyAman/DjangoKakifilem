from django.shortcuts import render
from django.conf import settings
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'index.html')

def countdown(request):
    telegram_id = request.GET.get('telegram_id')
    token = request.GET.get('token')
    video_name = request.GET.get('videoName')
    
    logger.info(f"Countdown request - Token: {token}, Video: {video_name}, Telegram ID: {telegram_id}")
    
    # Don't redirect immediately, always show countdown
    context = {
        'bot_api_url': settings.BOT_API_URL,
        'telegram_id': telegram_id,
        'request': request
    }
    return render(request, 'countdown.html', context)
