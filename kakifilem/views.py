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
    """Search videos with pagination and flexible search patterns"""
    if not search_term:
        return 0, []

    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Clean and prepare search patterns
        search_patterns = []
        
        # Original search term
        search_patterns.append(search_term)
        
        # Add "dia." prefix if not present
        if not search_term.lower().startswith('dia.'):
            search_patterns.append(f"dia.{search_term}")
            
        # Remove "dia." prefix if present
        if search_term.lower().startswith('dia.'):
            search_patterns.append(search_term[4:])
            
        # Create patterns with dots and spaces
        for pattern in search_patterns[:]:
            search_patterns.append(pattern.replace(' ', '.'))
            search_patterns.append(pattern.replace('.', ' '))
            
        # Remove duplicates while preserving order
        search_patterns = list(dict.fromkeys(search_patterns))
        
        # Build dynamic query parts
        like_conditions = []
        query_params = []
        
        for pattern in search_patterns:
            like_conditions.append("LOWER(video_name) LIKE LOWER(%s)")
            query_params.append(f"%{pattern}%")
            
        # Get total count
        count_query = f"""
            SELECT COUNT(DISTINCT id) FROM videos 
            WHERE {' OR '.join(like_conditions)}
        """
        cur.execute(count_query, query_params)
        total_count = cur.fetchone()[0]
        
        # Get paginated results
        offset = (page - 1) * per_page
        query = f"""
            SELECT DISTINCT id, video_name, caption, file_id, file_size, 
                   upload_date, thumbnail_id,
                   CASE 
                       WHEN LOWER(video_name) = LOWER(%s) THEN 1
                       ELSE 2
                   END as match_rank
            FROM videos 
            WHERE {' OR '.join(like_conditions)}
            ORDER BY match_rank, upload_date DESC
            LIMIT %s OFFSET %s
        """
        
        # Add parameters for exact match and pagination
        query_params.append(search_term)  # For exact match priority
        query_params.extend([per_page, offset])  # For pagination
        
        cur.execute(query, query_params)
        results = cur.fetchall()
        
        # Remove the match_rank from results before returning
        cleaned_results = [(r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in results]
        
        logger.info(f"Search patterns tried: {search_patterns}")
        logger.info(f"Found {total_count} results for '{search_term}'")
        
        return total_count, cleaned_results

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
    telegram_id = request.GET.get('telegram_id')
    per_page = 10

    try:
        # Fix: Better handling of telegram_id
        user_id = None
        if telegram_id and telegram_id.lower() != 'null':
            try:
                user_id = int(telegram_id)
            except (TypeError, ValueError):
                logger.warning(f"Invalid telegram_id received: {telegram_id}")
                user_id = None
        
        total_count, videos = get_videos_by_name(query, page, per_page)
        results = []
        
        for video in videos:
            # Only create and save token if user is logged in
            token = None
            if user_id:
                token = hashlib.sha256(f"{video[0]}:{datetime.now().timestamp()}".encode()).hexdigest()[:32]
                try:
                    save_token(video[0], user_id, token)
                except Exception as e:
                    logger.error(f"Error saving token: {e}")
                    continue

            result = {
                'name': video[1],
                'size': video[4],
                'token': token,
                'needs_login': user_id is None
            }
            
            if video[6]:  # thumbnail_id is at index 6
                result['thumbnail'] = video[6]

            results.append(result)

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

@csrf_exempt
def auth_callback(request):
    """Handle Telegram auth callback"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.info(f"Auth callback received: {data}")
            return JsonResponse({'status': 'success'})
        except Exception as e:
            logger.error(f"Auth callback error: {e}")
            return JsonResponse({'status': 'error'}, status=400)
    return redirect('/search/')
