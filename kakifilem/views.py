from django.shortcuts import render, redirect
from django.conf import settings
import psycopg2
from urllib.parse import urlparse

def get_user_by_token(token):
    """Get telegram_id for a given token"""
    if not token:
        return None
        
    try:
        conn = psycopg2.connect(settings.DATABASES['default']['url'])
        cur = conn.cursor()
        cur.execute("""
            SELECT user_id FROM video_tokens WHERE token = %s AND expires_at > NOW()
        """, (token,))
        result = cur.fetchone()
        return result[0] if result else None
    except Exception as e:
        print(f"Database error: {e}")
        return None
    finally:
        cur.close()
        conn.close()

def index(request):
    return render(request, 'index.html')

def countdown(request):
    token = request.GET.get('token')
    video_name = request.GET.get('videoName')
    
    # Get user_id from token
    telegram_id = get_user_by_token(token)
    
    context = {
        'bot_api_url': settings.BOT_API_URL,
        'telegram_id': telegram_id or '',  # Use empty string if None
        'token': token,
        'video_name': video_name
    }
    return render(request, 'countdown.html', context)
