from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import psycopg2
import logging
import os
import redis
import json
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)

def get_db_connection():
    """Get database connection using Django settings"""
    try:
        db_settings = settings.DATABASES['default']
        return psycopg2.connect(
            dbname=db_settings['NAME'],
            user=db_settings['USER'],
            password=db_settings['PASSWORD'],
            host=db_settings['HOST'],
            port=db_settings['PORT']
        )
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise

def get_videos_by_name(search_term: str, page: int = 1, per_page: int = 10):
    """Search videos with pagination"""
    if not search_term:
        return 0, []

    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # First get total count
        cur.execute("""
            SELECT COUNT(*) FROM videos 
            WHERE video_name ILIKE %s
        """, (f"%{search_term}%",))
        total_count = cur.fetchone()[0]

        # Then get paginated results
        offset = (page - 1) * per_page
        cur.execute("""
            SELECT id, video_name, caption, file_id, file_size, upload_date
            FROM videos 
            WHERE video_name ILIKE %s
            ORDER BY upload_date DESC
            LIMIT %s OFFSET %s
        """, (f"%{search_term}%", per_page, offset))
        
        results = cur.fetchall()
        return total_count, results

    except Exception as e:
        logger.error(f"Database search error: {e}")
        return 0, []
    finally:
        cur.close()
        conn.close()

def save_token(video_id: int, user_id: int, token: str):
    """Save video token to database"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO video_tokens (video_id, user_id, token, expires_at)
            VALUES (%s, %s, %s, NOW() + INTERVAL '24 hours')
        """, (video_id, user_id, token))
        conn.commit()
    except Exception as e:
        logger.error(f"Error saving token: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def get_user_by_token(token):
    """Get telegram_id for a given token"""
    if not token:
        return None
        
    conn = None
    cur = None
    try:
        # Get database URL from settings
        db_settings = settings.DATABASES['default']
        conn = psycopg2.connect(
            dbname=db_settings['NAME'],
            user=db_settings['USER'],
            password=db_settings['PASSWORD'],
            host=db_settings['HOST'],
            port=db_settings['PORT']
        )
        cur = conn.cursor()
        
        cur.execute("""
            SELECT user_id FROM video_tokens 
            WHERE token = %s AND expires_at > NOW()
            LIMIT 1
        """, (token,))
        
        result = cur.fetchone()
        return result[0] if result else None
        
    except Exception as e:
        logger.error(f"Database error: {e}")
        return None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def index(request):
    # Check if request is from bot domain
    if request.get_host() != 'bot.kakifilem.com':
        return redirect('https://bot.kakifilem.com/index.html')
    return render(request, 'index.html')

def countdown(request):
    # Check if request is from bot domain
    if request.get_host() != 'bot.kakifilem.com':
        return redirect('https://bot.kakifilem.com/countdown/')
    
    token = request.GET.get('token')
    video_name = request.GET.get('videoName')
    
    # Get user_id from token
    telegram_id = get_user_by_token(token)
    
    context = {
        'bot_api_url': settings.BOT_API_URL,
        'telegram_id': telegram_id or '',
        'token': token,
        'video_name': video_name
    }
    return render(request, 'countdown.html', context)

def expand_short_url(request, code):
    """Handle short URL redirects"""
    try:
        # Connect to Redis using settings
        redis_client = redis.from_url(settings.REDIS_URL)
        
        # Get URL data
        url_data = redis_client.get(f"url:{code}")
        if not url_data:
            return redirect('/')
            
        # Parse the JSON data
        params = json.loads(url_data)
        
        # Change: Redirect to index.html with parameters
        return redirect(f'/index.html?token={params["token"]}&videoName={params["videoName"]}')
        
    except Exception as e:
        logger.error(f"Error expanding URL: {e}")
        return redirect('/')

@csrf_exempt
def search_videos(request):
    """API endpoint for searching videos"""
    query = request.GET.get('q', '')
    page = int(request.GET.get('page', 1))
    per_page = 10

    try:
        # Get total count and paginated results
        total_count, videos = get_videos_by_name(query, page, per_page)

        # Format results
        results = []
        for video in videos:
            # Generate token for video using timestamp for uniqueness
            token = hashlib.sha256(f"{video[0]}:{datetime.now().timestamp()}".encode()).hexdigest()[:32]
            
            # Save token with null user_id since we don't have authentication
            save_token(video[0], None, token)

            results.append({
                'name': video[1],
                'size': video[4],
                'token': token
            })

        return JsonResponse({
            'total': total_count,
            'page': page,
            'results': results
        })

    except Exception as e:
        logger.error(f"Search error: {e}")
        return JsonResponse({'error': 'Search failed'}, status=500)

def search_page(request):
    """Render search page"""
    return render(request, 'search.html')
