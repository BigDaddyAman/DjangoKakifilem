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
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('index.html', views.index, name='index_html'),
    path('countdown/', views.countdown, name='countdown'),
    # Add this line to handle short URLs
    path('<str:short_id>/', views.redirect_to_original, name='redirect'),
    # JS files paths
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
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
