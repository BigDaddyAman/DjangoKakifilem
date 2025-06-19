from django.shortcuts import render, redirect
from django.conf import settings
import psycopg2
import logging
import os
import redis
import json
from django.http import JsonResponse
from datetime import datetime

logger = logging.getLogger(__name__)

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

def miniapps(request):
    """Handle mini-apps page"""
    try:
        # First try to get user_id from query params (command)
        user_id = request.GET.get('user_id')
        
        # If no user_id, try to get from Telegram WebApp data
        if not user_id:
            webapp_data = request.headers.get('X-Telegram-Web-App-Data')
            if webapp_data:
                # Parse WebApp data
                try:
                    import base64
                    import json
                    decoded = base64.b64decode(webapp_data).decode('utf-8')
                    data = json.loads(decoded)
                    user_id = data.get('user', {}).get('id')
                    logging.info(f"Got user_id from WebApp: {user_id}")
                except Exception as e:
                    logging.error(f"Error parsing WebApp data: {e}")

        action = request.GET.get('action', 'bug')
        
        logging.info(f"Miniapps accessed by user_id: {user_id}, action: {action}")
        
        context = {
            'user_id': user_id or '',
            'action': action,
            'data': {}
        }

        if user_id:
            try:
                user_id = int(user_id)
                conn = None
                cur = None
                try:
                    db_settings = settings.DATABASES['default']
                    conn = psycopg2.connect(
                        dbname=db_settings['NAME'],
                        user=db_settings['USER'],
                        password=db_settings['PASSWORD'],
                        host=db_settings['HOST'],
                        port=db_settings['PORT']
                    )
                    cur = conn.cursor()

                    # Fixed premium query with better logging
                    cur.execute("""
                        SELECT COUNT(*) 
                        FROM premium_users 
                        WHERE user_id = %s 
                        AND expiry_date > NOW()
                    """, (user_id,))
                    
                    has_premium = cur.fetchone()[0] > 0
                    logging.info(f"Premium check for user {user_id}: {has_premium}")

                    if has_premium:
                        # Get premium details
                        cur.execute("""
                            SELECT start_date, expiry_date 
                            FROM premium_users 
                            WHERE user_id = %s 
                            AND expiry_date > NOW()
                            ORDER BY expiry_date DESC 
                            LIMIT 1
                        """, (user_id,))
                        premium_data = cur.fetchone()
                        
                        if premium_data:
                            start_date, expiry_date = premium_data
                            days_remaining = (expiry_date - datetime.now()).days
                            context['data']['premium'] = {
                                'active': True,
                                'days_remaining': days_remaining,
                                'expiry_date': expiry_date.strftime('%Y-%m-%d %H:%M:%S'),
                                'start_date': start_date.strftime('%Y-%m-%d %H:%M:%S')
                            }
                            logging.info(f"Found premium data for user {user_id}: expires in {days_remaining} days")
                    else:
                        context['data']['premium'] = {'active': False}
                        logging.info(f"User {user_id} is not premium")

                except Exception as e:
                    logging.error(f"Database error: {e}", exc_info=True)
                finally:
                    if cur:
                        cur.close()
                    if conn:
                        conn.close()
            except ValueError:
                logging.error(f"Invalid user_id format: {user_id}")

        return render(request, 'miniapps.html', context)
    except Exception as e:
        logging.error(f"Error in miniapps view: {e}", exc_info=True)
        return render(request, 'miniapps.html', {'error': 'Error checking status'})

async def handle_miniapps_submit(request):
    """Handle mini-apps form submissions"""
    try:
        data = await request.json()
        action = data.get('action')
        user_id = data.get('user_id')
        form_data = data.get('data', {})
        
        conn = None
        cur = None
        try:
            # Get database connection
            db_settings = settings.DATABASES['default']
            conn = psycopg2.connect(
                dbname=db_settings['NAME'],
                user=db_settings['USER'],
                password=db_settings['PASSWORD'],
                host=db_settings['HOST'],
                port=db_settings['PORT']
            )
            cur = conn.cursor()
            
            if action == 'bug':
                # Save bug report
                cur.execute("""
                    INSERT INTO bug_reports (user_id, title, description)
                    VALUES (%s, %s, %s)
                """, (user_id, form_data.get('title'), form_data.get('description')))
                
            elif action == 'request':
                # Save movie request
                cur.execute("""
                    INSERT INTO movie_requests (user_id, movie_name, additional_info)
                    VALUES (%s, %s, %s)
                """, (user_id, form_data.get('movieName'), form_data.get('additionalInfo')))
                
            elif action == 'report':
                cur.execute("""
                    INSERT INTO video_reports (user_id, video_id, reason)
                    VALUES (%s, %s, %s)
                """, (user_id, form_data.get('videoId'), form_data.get('reason')))
                
            conn.commit()
            return JsonResponse({'status': 'success'})
            
        except Exception as e:
            logger.error(f"Error in form submission: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
                
    except Exception as e:
        logger.error(f"Error processing form: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)})

# Add new admin handler
async def handle_admin_action(request):
    """Handle admin actions on reports/requests"""
    try:
        data = await request.json()
        item_type = data.get('type')
        item_id = data.get('id')
        action = data.get('action')  # 'approve' or 'reject'
        user_id = data.get('user_id')

        # Verify admin status
        conn = None
        cur = None
        try:
            db_settings = settings.DATABASES['default']
            conn = psycopg2.connect(
                dbname=db_settings['NAME'],
                user=db_settings['USER'],
                password=db_settings['PASSWORD'],
                host=db_settings['HOST'],
                port=db_settings['PORT']
            )
            cur = conn.cursor()
            
            # Update status based on action
            if item_type == 'bug':
                cur.execute("""
                    UPDATE bug_reports 
                    SET status = %s, 
                        completed_at = NOW() 
                    WHERE id = %s
                """, (action, item_id))
            elif item_type == 'request':
                cur.execute("""
                    UPDATE movie_requests 
                    SET status = %s, 
                        completed_at = NOW() 
                    WHERE id = %s
                """, (action, item_id))
            elif item_type == 'report':
                cur.execute("""
                    UPDATE video_reports 
                    SET status = %s, 
                        completed_at = NOW() 
                    WHERE id = %s
                """, (action, item_id))
                
            conn.commit()
            return JsonResponse({'status': 'success'})
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error in admin action: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
                
    except Exception as e:
        logger.error(f"Error processing admin action: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)})
