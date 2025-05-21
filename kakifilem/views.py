from django.shortcuts import render, redirect
from django.conf import settings
import logging
import psycopg2
from urllib.parse import urlparse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Get database connection using URL"""
    url = urlparse(settings.DATABASES['default']['url'])
    return psycopg2.connect(
        dbname=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )

def get_user_by_token(token):
    """Get telegram_id for a given token"""
    if not token:
        return None
        
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT u.user_id 
            FROM video_tokens vt
            JOIN users u ON vt.user_id = u.user_id
            WHERE vt.token = %s AND vt.expires_at > NOW()
            LIMIT 1
        """, (token,))
        
        result = cur.fetchone()
        return result[0] if result else None
        
    except Exception as e:
        logger.error(f"Error getting user by token: {e}")
        return None
    finally:
        cur.close()
        conn.close()

def index(request):
    return render(request, 'index.html')

def countdown(request):
    token = request.GET.get('token')
    video_name = request.GET.get('videoName')
    
    telegram_id = get_user_by_token(token)
    
    if not telegram_id:
        return redirect(f'https://t.me/KakifilemBot?start={token}')
    
    context = {
        'bot_api_url': settings.BOT_API_URL,
        'telegram_id': telegram_id,
        'token': token,
        'video_name': video_name
    }
    return render(request, 'countdown.html', context)
