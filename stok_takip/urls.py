# urls.py

from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .viewsets import (
    KategoriViewSet, TedarikciViewSet, UrunViewSet,
    UrunYerlesimYeriViewSet, SatisFiyatiViewSet,
    SatisFisiViewSet, SatisViewSet, TedarikciIadeViewSet,
    MusteriIadeViewSet, KasaViewSet, AlisFisiViewSet,
    AlisDetayViewSet, OdemeKasaViewSet
)

# Router oluştur
router = DefaultRouter()

# ViewSet'leri router'a kaydet
router.register(r'kategoriler', KategoriViewSet, basename='kategori')
router.register(r'tedarikciler', TedarikciViewSet, basename='tedarikci')
router.register(r'urunler', UrunViewSet, basename='urun')
router.register(r'yerlesimler', UrunYerlesimYeriViewSet, basename='yerlesim')
router.register(r'satis-fiyatlari', SatisFiyatiViewSet, basename='satis-fiyati')
router.register(r'satis-fisleri', SatisFisiViewSet, basename='satis-fisi')
router.register(r'satislar', SatisViewSet, basename='satis')
router.register(r'tedarikci-iadeler', TedarikciIadeViewSet, basename='tedarikci-iade')
router.register(r'musteri-iadeler', MusteriIadeViewSet, basename='musteri-iade')
router.register(r'kasa', KasaViewSet, basename='kasa')
router.register(r'alis-fisleri', AlisFisiViewSet, basename='alis-fisi')
router.register(r'alis-detaylar', AlisDetayViewSet, basename='alis-detay')
router.register(r'odemeler', OdemeKasaViewSet, basename='odeme')

# API root view
@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'kategoriler': reverse('kategori-list', request=request, format=format),
        'tedarikciler': reverse('tedarikci-list', request=request, format=format),
        'urunler': reverse('urun-list', request=request, format=format),
        'yerlesimler': reverse('yerlesim-list', request=request, format=format),
        'satis-fiyatlari': reverse('satis-fiyati-list', request=request, format=format),
        'satis-fisleri': reverse('satis-fisi-list', request=request, format=format),
        'satislar': reverse('satis-list', request=request, format=format),
        'tedarikci-iadeler': reverse('tedarikci-iade-list', request=request, format=format),
        'musteri-iadeler': reverse('musteri-iade-list', request=request, format=format),
        'kasa': reverse('kasa-list', request=request, format=format),
        'alis-fisleri': reverse('alis-fisi-list', request=request, format=format),
        'alis-detaylar': reverse('alis-detay-list', request=request, format=format),
        'odemeler': reverse('odeme-list', request=request, format=format),
    })

app_name = 'stok_takip'

urlpatterns = [
    # Barkod okuyucu sayfası
    # path('barkod-okuyucu/', views.barkod_okuyucu, name='barkod_okuyucu'),
    
    # AJAX endpoints
    # path('api/barkod/urun-kaydet/', views.barkod_ile_urun_kaydet, name='barkod_urun_kaydet'),
    # path('api/barkod/urun-bul/', views.barkod_ile_urun_bul, name='barkod_urun_bul'),
    
    # Raporlar
    path('raporlar/envanter/', views.envanter_raporu, name='envanter_raporu'),
    path('raporlar/muhasebe/', views.muhasebe_raporu, name='muhasebe_raporu'),
    path('', include(router.urls)),
]