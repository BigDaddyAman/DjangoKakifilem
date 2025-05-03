from django.shortcuts import render, redirect
from django.http import Http404, JsonResponse
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'index.html')

def countdown(request):
    return render(request, 'countdown.html')
