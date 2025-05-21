"""
URL configuration for kakifilem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView, RedirectView
from django.conf import settings
from django.conf.urls.static import static
from . import views

# Add CORS settings
CORS_ALLOW_ALL_ORIGINS = True  # Only for development
CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'OPTIONS',
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('index.html', views.index, name='index_html'),  # Add this line
    path('countdown/', views.countdown, name='countdown'),
    # Serve JS files from templates directory
    path('InPagePush.js', TemplateView.as_view(
        template_name='InPagePush.js',
        content_type='application/javascript',
    ), name='inpage-push-js'),
    path('monetag.js', TemplateView.as_view(
        template_name='monetag.js',
        content_type='application/javascript',
    ), name='monetag-js'),
    path('sw.js', TemplateView.as_view(
        template_name='sw.js',
        content_type='application/javascript',
    ), name='sw-js'),
    # Add this line for favicon.ico
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'favicon/favicon.ico')),
    path('apple-touch-icon.png', RedirectView.as_view(url=settings.STATIC_URL + 'favicon/apple-touch-icon.png')),
    path('apple-touch-icon-precomposed.png', RedirectView.as_view(url=settings.STATIC_URL + 'favicon/apple-touch-icon.png')),
    path('favicon-32x32.png', RedirectView.as_view(url=settings.STATIC_URL + 'favicon/favicon-32x32.png')),
    path('favicon-16x16.png', RedirectView.as_view(url=settings.STATIC_URL + 'favicon/favicon-16x16.png')),
    path('site.webmanifest', RedirectView.as_view(url=settings.STATIC_URL + 'favicon/site.webmanifest')),
    path('android-chrome-192x192.png', RedirectView.as_view(url=settings.STATIC_URL + 'favicon/android-chrome-192x192.png')),
    path('android-chrome-512x512.png', RedirectView.as_view(url=settings.STATIC_URL + 'favicon/android-chrome-512x512.png')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
