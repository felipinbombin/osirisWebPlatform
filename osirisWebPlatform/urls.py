"""osirisWebPlatform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.conf.urls.static import static

urlpatterns = [
    url(r'^$', login_required(TemplateView.as_view(template_name="base_site.html")), name="index"),
    url(r'^admin/', include('scene.urls', namespace='scene')),
    url(r'^admin/', admin.site.urls),
    url(r'^myadmin/', include('myadmin.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

