from django.shortcuts import render, redirect
from django.http import Http404, JsonResponse
from django.core.cache import cache
from shortener.models import ShortURL
import logging

logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'index.html')

def countdown(request, short_id=None):
    if short_id:
        # If accessed via short URL, get the params from Redis/DB
        cache_key = f'short_url:{short_id}'
        long_url = cache.get(cache_key)
        
        if not long_url:
            try:
                short_url = ShortURL.objects.get(short_id=short_id)
                long_url = short_url.long_url
            except ShortURL.DoesNotExist:
                raise Http404("Short URL not found")
                
        # Pass the short_id to the template
        return render(request, 'countdown.html', {'short_id': short_id})
    
    return render(request, 'countdown.html')

def redirect_to_original(request, short_id):
    try:
        # Get URL from database
        short_url = ShortURL.objects.get(short_id=short_id)
        
        # Increment access count
        short_url.access_count += 1
        short_url.save()
        
        # If it's an index URL, redirect to countdown keeping short URL
        if 'index.html' in short_url.long_url:
            return redirect(f'/countdown/{short_id}/')
            
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
