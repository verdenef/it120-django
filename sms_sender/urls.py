"""
URL configuration for sms_sender project.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('sms_app.urls')),
]
