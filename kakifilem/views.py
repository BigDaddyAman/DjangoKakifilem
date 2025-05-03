from django.shortcuts import render, redirect
from django.http import Http404
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
    long_url = cache.get(cache_key)
    
    if not long_url:
        try:
            # Get from database if not in cache
            short_url = ShortURL.objects.get(short_id=short_id)
            long_url = short_url.long_url
            
            # Update access count
            short_url.access_count += 1
            short_url.save()
            
            # Cache frequently accessed URLs (more than 10 hits)
            if short_url.access_count > 10:
                cache.set(cache_key, long_url, timeout=86400)  # Cache for 24 hours
                
        except ShortURL.DoesNotExist:
            raise Http404("Short URL not found")
            
    return redirect(long_url)
