from django.shortcuts import render, redirect
from django.http import Http404, JsonResponse
from django.core.cache import cache
import logging
from shortener.models import ShortURL

logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'index.html')

def countdown(request):
    return render(request, 'countdown.html')

def redirect_to_original(request, short_id):
    """Handle redirect for short URLs"""
    try:
        # Get the ShortURL object
        short_url = ShortURL.objects.get(short_id=short_id)
        
        # Extract token and videoName from long_url if needed
        if 'index.html' in short_url.long_url or 'token=' in short_url.long_url:
            # Keep using long URL format for now
            return redirect(short_url.long_url)
        
        # Increment access count
        short_url.access_count += 1
        short_url.save()
        
        return redirect(short_url.long_url)
        
    except ShortURL.DoesNotExist:
        raise Http404("Short URL not found")
