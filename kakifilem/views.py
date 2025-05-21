from django.shortcuts import render, redirect
from django.conf import settings
import logging
import sys
import os

# Add bot directory to Python path
bot_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../KakifilemBot-main'))
sys.path.append(bot_path)

# Import from bot's database.py
from database import get_user_by_token

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'index.html')

def countdown(request):
    token = request.GET.get('token')
    video_name = request.GET.get('videoName')
    
    # Get telegram_id from bot's database
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
