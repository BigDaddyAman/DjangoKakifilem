from django.shortcuts import render, redirect
from django.conf import settings
import logging
from database import get_user_by_token  # Add this import

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'index.html')

def countdown(request):
    token = request.GET.get('token')
    video_name = request.GET.get('videoName')
    
    # Get telegram_id from database using token
    telegram_id = get_user_by_token(token)
    
    if not telegram_id:
        # If no user found, redirect to bot
        return redirect(f'https://t.me/KakifilemBot?start={token}')
    
    context = {
        'bot_api_url': settings.BOT_API_URL,
        'telegram_id': telegram_id,
        'token': token,
        'video_name': video_name
    }
    return render(request, 'countdown.html', context)
