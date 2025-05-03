from django.shortcuts import render, redirect
from django.http import Http404, JsonResponse
from django.core.cache import cache
from shortener.models import ShortURL
import logging

logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'index.html')

def countdown(request):
    return render(request, 'countdown.html')

def redirect_to_original(request, short_id):
    # Try to get URL from Redis cache first
    cache_key = f'short_url:{short_id}'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        try:
            # Parse the JSON data
            import json
            data = json.loads(cached_data)
            # Reconstruct the countdown URL with parameters
            return redirect(f"/countdown/?token={data['token']}&videoName={data['videoName']}")
        except:
            pass
            
    # Fallback to database lookup
    try:
        short_url = ShortURL.objects.get(short_id=short_id)
        return redirect(short_url.long_url)
    except ShortURL.DoesNotExist:
        raise Http404("Short URL not found")

def shorten_url(request):
    """Create short URL for countdown page"""
    token = request.GET.get('token')
    video_name = request.GET.get('videoName')
    
    if not token or not video_name:
        return JsonResponse({'error': 'Missing parameters'}, status=400)
        
    long_url = f"/countdown/?token={token}&videoName={video_name}"
    
    try:
        # Create short URL
        short_url = ShortURL.objects.create(long_url=long_url)
        return JsonResponse({'short_id': short_url.short_id})
    except Exception as e:
        logger.error(f"Error creating short URL: {e}")
        return JsonResponse({'error': 'Failed to create short URL'}, status=500)
