"""Main URLs module."""

from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    # Django Admin
    path(settings.ADMIN_URL, admin.site.urls),

    # Circle urls
    path('', include(('cride.circles.urls', 'circles')), name='circles'),
    path('', include(('cride.rides.urls', 'rides')), name='rides'),
    path('', include(('cride.users.urls', 'users')), name='users'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
