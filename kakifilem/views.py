from django.shortcuts import render, redirect
from django.http import Http404, JsonResponse
from django.core.cache import cache
import logging
import json
from shortener.models import ShortURL

logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'index.html')

def countdown(request):
    return render(request, 'countdown.html')

def redirect_to_original(request, short_id):
    """Handle redirect for short URLs"""
    try:
        # First check Redis
        cache_key = f'short_url:{short_id}'
        cached_url = cache.get(cache_key)
        
        if cached_url:
            try:
                # Try to parse Redis data
                data = json.loads(cached_url) if isinstance(cached_url, str) else cached_url
                if isinstance(data, dict):
                    token = data.get('token')
                    video_name = data.get('videoName')
                    if token and video_name:
                        return redirect(f'/index.html?token={token}&videoName={video_name}')
            except:
                if isinstance(cached_url, str) and cached_url.startswith('http'):
                    return redirect(cached_url)

        # Fallback to database
        try:
            short_url = ShortURL.objects.get(short_id=short_id)
            return redirect(short_url.long_url)
        except ShortURL.DoesNotExist:
            logger.error(f"Short URL not found in DB: {short_id}")
            raise Http404("Short URL not found")
            
    except Exception as e:
        logger.error(f"Error processing short URL: {e}")
        raise Http404("Error processing URL")
