# backend/urls.py
from django.contrib import admin
from django.urls import path, include  # Исправлено: было 'django.utils', должно быть 'django.urls'
from django.http import HttpResponse

def home(request):
    return HttpResponse('<h1>Probation Services API</h1><p>Go to <a href="/api/">API</a> or <a href="/admin/">Admin Panel</a></p>')

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]