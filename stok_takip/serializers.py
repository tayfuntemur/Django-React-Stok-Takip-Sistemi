from rest_framework import serializers
from .models import (
    Kategori, Tedarikci, Urun, UrunYerlesimYeri, SatisFiyati,
    SatisFisi, Satis, TedarikciIade, MusteriIade, 
    Kasa, SatisKasa, AlisFisi, AlisDetay, OdemeKasa
)
from django.contrib.auth.models import User


# 1. KULLANICI SERİALİZER
class KullaniciSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


# 2. KATEGORİ SERİALİZER
class KategoriSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kategori
        fields = '__all__'


# 3. TEDARİKÇİ SERİALİZER
class TedarikciSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tedarikci
        fields = '__all__'


# 4. ÜRÜN SERİALİZER
class UrunSerializer(serializers.ModelSerializer):
    kategori_adi = serializers.CharField(source='kategori.kategori_adi', read_only=True)
    toplam_stok = serializers.SerializerMethodField()
    satis_fiyati = serializers.SerializerMethodField()
    
    class Meta:
        model = Urun
        fields = ['stok_no', 'urun_adi', 'kategori', 'kategori_adi', 
                  'birim', 'barkod', 'barkod_resim', 'toplam_stok', 'satis_fiyati',
                  'olusturma_tarihi', 'guncelleme_tarihi']
    
    def get_toplam_stok(self, obj):
        """Tüm lotlardaki toplam stok miktarı"""
        from django.db.models import Sum
        toplam = UrunYerlesimYeri.objects.filter(urun=obj).aggregate(
            toplam=Sum('miktar')
        )['toplam']
        return toplam or 0
    
    def get_satis_fiyati(self, obj):
        """Ürünün satış fiyatı"""
        try:
            fiyat = SatisFiyati.objects.get(urun=obj)
            return float(fiyat.satis_fiyati)
        except SatisFiyati.DoesNotExist:
            return None


# 5. ÜRÜN YERLEŞİM YERİ SERİALİZER
class UrunYerlesimYeriSerializer(serializers.ModelSerializer):
    urun_adi = serializers.CharField(source='urun.urun_adi', read_only=True)
    urun_stok_no = serializers.CharField(source='urun.stok_no', read_only=True)
    
    class Meta:
        model = UrunYerlesimYeri
        fields = '__all__'


# 6. SATIŞ FİYATI SERİALİZER
class SatisFiyatiSerializer(serializers.ModelSerializer):
    urun_adi = serializers.CharField(source='urun.urun_adi', read_only=True)
    
    class Meta:
        model = SatisFiyati
        fields = '__all__'
        read_only_fields = ['satis_fiyati', 'guncelleme_tarihi']


# 7. SATIŞ SERİALİZERLERİ
class SatisSerializer(serializers.ModelSerializer):
    urun_adi = serializers.CharField(source='urun.urun_adi', read_only=True)
    urun_barkod = serializers.CharField(source='urun.barkod', read_only=True)
    
    class Meta:
        model = Satis
        fields = '__all__'
        read_only_fields = ['birim_fiyat', 'toplam_fiyat']


class SatisFisiSerializer(serializers.ModelSerializer):
    kullanici_adi = serializers.CharField(source='kullanici.get_full_name', read_only=True)
    satislar = SatisSerializer(many=True, read_only=True)
    
    class Meta:
        model = SatisFisi
        fields = '__all__'
        read_only_fields = ['fis_no', 'toplam_tutar', 'olusturma_tarihi']


# 8. İADE SERİALİZERLERİ
class TedarikciIadeSerializer(serializers.ModelSerializer):
    urun_adi = serializers.CharField(source='urun.urun_adi', read_only=True)
    tedarikci_adi = serializers.CharField(source='tedarikci.firma_adi', read_only=True)
    
    class Meta:
        model = TedarikciIade
        fields = '__all__'


class MusteriIadeSerializer(serializers.ModelSerializer):
    urun_adi = serializers.CharField(source='urun.urun_adi', read_only=True)
    
    class Meta:
        model = MusteriIade
        fields = '__all__'


# 9. KASA SERİALİZERLERİ
class KasaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kasa
        fields = '__all__'
        read_only_fields = ['son_guncelleme']


class SatisKasaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SatisKasa
        fields = '__all__'
        read_only_fields = ['islem_tarihi']


class OdemeKasaSerializer(serializers.ModelSerializer):
    kullanici_adi = serializers.CharField(source='kullanici.get_full_name', read_only=True)
    odeme_tipi_display = serializers.CharField(source='get_odeme_tipi_display', read_only=True)
    
    class Meta:
        model = OdemeKasa
        fields = '__all__'
        read_only_fields = ['islem_tarihi']


# 10. ALIŞ SERİALİZERLERİ
class AlisDetaySerializer(serializers.ModelSerializer):
    urun_adi = serializers.CharField(source='urun.urun_adi', read_only=True)
    
    class Meta:
        model = AlisDetay
        fields = '__all__'
        read_only_fields = ['toplam_fiyat']


class AlisFisiSerializer(serializers.ModelSerializer):
    tedarikci_adi = serializers.CharField(source='tedarikci.firma_adi', read_only=True)
    kullanici_adi = serializers.CharField(source='kullanici.get_full_name', read_only=True)
    detaylar = AlisDetaySerializer(many=True, read_only=True)
    
    class Meta:
        model = AlisFisi
        fields = '__all__'
        read_only_fields = ['lot_no', 'toplam_tutar', 'kayit_tarihi']