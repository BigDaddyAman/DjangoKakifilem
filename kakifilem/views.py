from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def countdown(request):
    return render(request, 'countdown.html')
