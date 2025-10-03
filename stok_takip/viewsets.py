from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Q
from datetime import date, timedelta

from .models import (
    Kategori, Tedarikci, Urun, UrunYerlesimYeri, SatisFiyati,
    SatisFisi, Satis, TedarikciIade, MusteriIade, 
    Kasa, SatisKasa, AlisFisi, AlisDetay, OdemeKasa
)
from .serializers import (
    KategoriSerializer, TedarikciSerializer, UrunSerializer,
    UrunYerlesimYeriSerializer, SatisFiyatiSerializer,
    SatisFisiSerializer, SatisSerializer, TedarikciIadeSerializer,
    MusteriIadeSerializer, KasaSerializer, SatisKasaSerializer,
    AlisFisiSerializer, AlisDetaySerializer, OdemeKasaSerializer
)


# 1. KATEGORİ VIEWSET
class KategoriViewSet(viewsets.ModelViewSet):
    """
    Kategori işlemleri:
    - Liste (GET /api/kategoriler/)
    - Detay (GET /api/kategoriler/1/)
    - Oluştur (POST /api/kategoriler/)
    - Güncelle (PUT /api/kategoriler/1/)
    - Sil (DELETE /api/kategoriler/1/)
    """
    queryset = Kategori.objects.all()
    serializer_class = KategoriSerializer
    permission_classes = [IsAuthenticated]


# 2. TEDARİKÇİ VIEWSET
class TedarikciViewSet(viewsets.ModelViewSet):
    queryset = Tedarikci.objects.all()
    serializer_class = TedarikciSerializer
    permission_classes = [IsAuthenticated]


# 3. ÜRÜN VIEWSET
class UrunViewSet(viewsets.ModelViewSet):
    queryset = Urun.objects.all()
    serializer_class = UrunSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def barkod_ara(self, request):
        """
        Barkod ile ürün ara
        URL: /api/urunler/barkod_ara/?barkod=123456789
        """
        barkod = request.query_params.get('barkod', None)
        if barkod:
            try:
                urun = Urun.objects.get(barkod=barkod)
                serializer = self.get_serializer(urun)
                return Response(serializer.data)
            except Urun.DoesNotExist:
                return Response(
                    {'error': 'Ürün bulunamadı'},
                    status=status.HTTP_404_NOT_FOUND
                )
        return Response(
            {'error': 'Barkod parametresi gerekli'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['get'])
    def dusuk_stok(self, request):
        """
        Düşük stoklu ürünleri listele
        URL: /api/urunler/dusuk_stok/?limit=10
        """
        limit = int(request.query_params.get('limit', 10))
        
        # Her ürün için toplam stok hesapla
        urunler = []
        for urun in Urun.objects.all():
            toplam_stok = UrunYerlesimYeri.objects.filter(
                urun=urun
            ).aggregate(toplam=Sum('miktar'))['toplam'] or 0
            
            if toplam_stok <= limit:
                urunler.append(urun)
        
        serializer = self.get_serializer(urunler, many=True)
        return Response(serializer.data)


# 4. ÜRÜN YERLEŞİM YERİ VIEWSET
class UrunYerlesimYeriViewSet(viewsets.ModelViewSet):
    queryset = UrunYerlesimYeri.objects.all()
    serializer_class = UrunYerlesimYeriSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def skt_yaklasiyor(self, request):
        """
        Son kullanma tarihi yaklaşan ürünler
        URL: /api/yerlesimler/skt_yaklasiyor/?gun=30
        """
        gun = int(request.query_params.get('gun', 30))
        bugun = date.today()
        gelecek = bugun + timedelta(days=gun)
        
        yerlesimler = UrunYerlesimYeri.objects.filter(
            son_kullanma_tarihi__lte=gelecek,
            son_kullanma_tarihi__gte=bugun,
            miktar__gt=0
        ).order_by('son_kullanma_tarihi')
        
        serializer = self.get_serializer(yerlesimler, many=True)
        return Response(serializer.data)


# 5. SATIŞ FİYATI VIEWSET
class SatisFiyatiViewSet(viewsets.ModelViewSet):
    queryset = SatisFiyati.objects.all()
    serializer_class = SatisFiyatiSerializer
    permission_classes = [IsAuthenticated]


# 6. SATIŞ FİŞİ VIEWSET
class SatisFisiViewSet(viewsets.ModelViewSet):
    queryset = SatisFisi.objects.all()
    serializer_class = SatisFisiSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def bugun(self, request):
        """
        Bugünün satışları
        URL: /api/satis-fisleri/bugun/
        """
        bugun = date.today()
        fisler = SatisFisi.objects.filter(
            olusturma_tarihi__date=bugun
        )
        serializer = self.get_serializer(fisler, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def ozet(self, request):
        """
        Satış özeti
        URL: /api/satis-fisleri/ozet/
        """
        bugun = date.today()
        
        # Bugün
        bugun_satis = SatisFisi.objects.filter(
            olusturma_tarihi__date=bugun
        ).aggregate(toplam=Sum('toplam_tutar'))['toplam'] or 0
        
        # Bu ay
        ay_satis = SatisFisi.objects.filter(
            olusturma_tarihi__year=bugun.year,
            olusturma_tarihi__month=bugun.month
        ).aggregate(toplam=Sum('toplam_tutar'))['toplam'] or 0
        
        return Response({
            'bugun': float(bugun_satis),
            'bu_ay': float(ay_satis),
            'fis_sayisi': SatisFisi.objects.filter(
                olusturma_tarihi__date=bugun
            ).count()
        })


# 7. SATIŞ VIEWSET
class SatisViewSet(viewsets.ModelViewSet):
    queryset = Satis.objects.all()
    serializer_class = SatisSerializer
    permission_classes = [IsAuthenticated]


# 8. TEDARİKÇİ İADE VIEWSET
class TedarikciIadeViewSet(viewsets.ModelViewSet):
    queryset = TedarikciIade.objects.all()
    serializer_class = TedarikciIadeSerializer
    permission_classes = [IsAuthenticated]


# 9. MÜŞTERİ İADE VIEWSET
class MusteriIadeViewSet(viewsets.ModelViewSet):
    queryset = MusteriIade.objects.all()
    serializer_class = MusteriIadeSerializer
    permission_classes = [IsAuthenticated]


# 10. KASA VIEWSET
class KasaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Kasa sadece okunabilir (güncelleme otomatik)
    """
    queryset = Kasa.objects.all()
    serializer_class = KasaSerializer
    permission_classes = [IsAuthenticated]


# 11. ALIŞ FİŞİ VIEWSET
class AlisFisiViewSet(viewsets.ModelViewSet):
    queryset = AlisFisi.objects.all()
    serializer_class = AlisFisiSerializer
    permission_classes = [IsAuthenticated]


# 12. ALIŞ DETAY VIEWSET
class AlisDetayViewSet(viewsets.ModelViewSet):
    queryset = AlisDetay.objects.all()
    serializer_class = AlisDetaySerializer
    permission_classes = [IsAuthenticated]


# 13. ÖDEME VIEWSET
class OdemeKasaViewSet(viewsets.ModelViewSet):
    queryset = OdemeKasa.objects.all()
    serializer_class = OdemeKasaSerializer
    permission_classes = [IsAuthenticated]