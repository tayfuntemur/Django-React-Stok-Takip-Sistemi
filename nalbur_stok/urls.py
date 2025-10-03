
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('stok_takip/', include('stok_takip.urls')),  # Mevcut URL'ler
    path('api/', include('stok_takip.urls')),  # YENİ: REST API URL'leri
    path('api-auth/', include('rest_framework.urls')),  # YENİ: Login/Logout için
]

# Medya dosyaları için
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)