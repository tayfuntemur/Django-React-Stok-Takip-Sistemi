from typing import Iterable
from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django.core.exceptions import ValidationError


    # Kategori
class Kategori(models.Model):
    kategori_adi = models.CharField(max_length=100 , unique=True , verbose_name='Kategori Adı')
    
    def __str__(self) :
        return self.kategori_adi
    
    class Meta:
        
        verbose_name = 'Kategori'
        verbose_name_plural = 'Kategoriler'
        ordering = ['kategori_adi']
        
        
        
#    Tedarikçiler     
class Tedarikci(models.Model):
    """Tedarikçi firmalar"""
    firma_adi = models.CharField(max_length=255, unique=True, verbose_name='Firma Adı')
    telefon = models.CharField(max_length=20, blank=True, verbose_name='Telefon')
    adres = models.TextField(blank=True, verbose_name='Adres')
    
    def __str__(self):
        return self.firma_adi

    class Meta:
        verbose_name = 'Tedarikçi'
        verbose_name_plural = 'Tedarikçiler'
        ordering = ['firma_adi']
    
    # Ürünler    
class Urun(models.Model):
    stok_no = models.CharField(max_length=100, unique=True,default='287900000100', primary_key=True)
    urun_adi = models.CharField(max_length=200)
    kategori = models.ForeignKey(Kategori, on_delete=models.CASCADE)
    birim = models.CharField(
        max_length=20,
        choices=[
            ('adet', 'Adet'),
            ('kg', 'Kilogram'),
            ('lt', 'Litre'),
            ('m', 'Metre'),
            ('m2', 'Metrekare'),
            ('paket', 'Paket'),
        ],
        default='adet',
        verbose_name='Birim'
    )
    barkod = models.CharField(max_length=13, unique=True,default='869000000100', blank=True)
    barkod_resim = models.ImageField(upload_to='barkodlar/', blank=True, null=True)
    olusturma_tarihi = models.DateTimeField(auto_now_add=True)
    guncelleme_tarihi = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.stok_no} - {self.urun_adi}"
    
    class Meta:
        verbose_name = 'Ürün'
        verbose_name_plural = 'Ürünler'
        ordering = ['kategori', 'urun_adi']


# Yerleşim modeli
class UrunYerlesimYeri(models.Model):
    urun = models.ForeignKey(Urun, on_delete=models.CASCADE, related_name='yerlesimler')
    miktar = models.IntegerField(default=0, verbose_name='Miktar')  # ✅ IntegerField
    konum = models.CharField(max_length=50, verbose_name='Konum')  # ✅ CharField
    lot_no = models.CharField(max_length=50, blank=True, verbose_name='Lot/Parti No')  # YENİ
    son_kullanma_tarihi = models.DateField(blank=True, null=True, verbose_name='Son Kullanma Tarihi')  # YENİ
    giris_tarihi = models.DateTimeField(auto_now_add=True, verbose_name='Giriş Tarihi')  # YENİ
    
    def save(self, *args, **kwargs):
        # Lot no boşsa otomatik oluştur
        if not self.lot_no:
            from datetime import date
            bugun = date.today()
            
            # Bugün eklenen son lot numarasını bul
            son_lot = UrunYerlesimYeri.objects.filter(
                lot_no__startswith=f'L{bugun.strftime("%Y%m%d")}'
            ).order_by('-lot_no').first()
            
            if son_lot:
                # Son lot'tan sıra numarasını al ve 1 artır
                son_sira = int(son_lot.lot_no.split('-')[-1])
                yeni_sira = son_sira + 1
            else:
                # Bugün ilk lot
                yeni_sira = 1
            
            # Format: L20251002-001
            self.lot_no = f'L{bugun.strftime("%Y%m%d")}-{yeni_sira:03d}'
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        lot_bilgi = f" - Lot: {self.lot_no}" if self.lot_no else ""
        return f"{self.urun.stok_no} - {self.urun.urun_adi} - {self.konum}{lot_bilgi}"
    
    class Meta:
        verbose_name = 'Ürün Yerleşim Yeri'
        verbose_name_plural = 'Ürün Yerleşim Yerleri'
        ordering = ['son_kullanma_tarihi', 'konum']  # SKT'ye göre sırala
        
        
    
    # Ürün Satış Fiyatı
class SatisFiyati(models.Model):
    KDV_ORANLARI = [
        (1,'%1'),
        (10,'%10'),
        (20,'%20'),
    ]
    
    urun = models.ForeignKey(Urun , on_delete=models.CASCADE,verbose_name='Ürün') 
    alim_fiyati=models.DecimalField(max_digits=10,decimal_places=2,verbose_name='Alım Fiyatı')
    kar_orani= models.DecimalField(max_digits=5,decimal_places=2,default=25.0, verbose_name='Kar Oranı %')
    kdv = models.IntegerField(choices=KDV_ORANLARI,default=20,verbose_name='KDV Oranı')
    iskonto_orani=models.DecimalField(max_digits=5,decimal_places=2,default=0, verbose_name='İskonto Oranı %')
    satis_fiyati = models.DecimalField(max_digits=10,decimal_places=2,verbose_name='Net Satis Fiyatı')
    guncelleme_tarihi=models.DateTimeField( auto_now=True)

    def save(self, *args, **kwargs):
        # Decimal'leri kullanarak hesaplama yap
        kar_tutari = self.alim_fiyati * (self.kar_orani / Decimal('100'))
        kdv_tutari = (self.alim_fiyati + kar_tutari) * (Decimal(self.kdv) / Decimal('100'))
        liste_satis_fiyati = self.alim_fiyati + kar_tutari + kdv_tutari
        iskonto_tutari = liste_satis_fiyati * (self.iskonto_orani / Decimal('100'))
        self.satis_fiyati = liste_satis_fiyati - iskonto_tutari
        
        # 2 ondalık basamağa yuvarla
        self.satis_fiyati = self.satis_fiyati.quantize(Decimal('0.01'))
        
        super().save(*args, **kwargs)
            
    def __str__(self):
        return f"{self.urun.stok_no} - {self.satis_fiyati} TL"

    class Meta:
        verbose_name = 'Ürün Satış Fiyatı'
        verbose_name_plural = 'Ürün Satış Fiyatları'
        


class SatisFisi(models.Model):
    fis_no = models.PositiveIntegerField(
        unique=True,
        verbose_name='Fiş No',
        editable=False,
        null=True,
        blank=True
    )
    kullanici = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='kullanici')
    toplam_tutar = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Toplam Tutar')
    olusturma_tarihi = models.DateTimeField(auto_now_add=True, verbose_name='Satış Tarihi')
    
    def save(self, *args, **kwargs):
        if not self.fis_no:
            son_fis = SatisFisi.objects.order_by('-fis_no').first()
            self.fis_no = 1 if not son_fis else (son_fis.fis_no or 0) + 1
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Fiş #{self.fis_no} - {self.kullanici.username} - {self.toplam_tutar} TL"
    
    class Meta:
        verbose_name = 'Satış Fişi'
        verbose_name_plural = 'Satış Fişleri'
        ordering = ['-olusturma_tarihi']


class Satis(models.Model):
    fis = models.ForeignKey(SatisFisi, on_delete=models.CASCADE, related_name='satislar', verbose_name='Fiş')
    urun = models.ForeignKey(Urun, on_delete=models.PROTECT, verbose_name='Ürün')
    miktar = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Miktar')
    birim_fiyat = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Birim Fiyat', editable=False, null=True, blank=True)
    toplam_fiyat = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Toplam Fiyat', editable=False, null=True, blank=True)
    
    def clean(self):
        """Form validasyonu - admin panelinde hata gösterir"""
        super().clean()
        
        if not self.urun or not self.miktar:
            return
        
        # Toplam stok kontrolü (tüm lotların toplamı)
        from django.db.models import Sum
        
        toplam_stok = UrunYerlesimYeri.objects.filter(
            urun=self.urun
        ).aggregate(toplam=Sum('miktar'))['toplam'] or 0
        
        # Eğer bu kayıt güncelleme ise, önceki miktarı geri ekle
        if self.pk:
            try:
                eski_satis = Satis.objects.get(pk=self.pk)
                toplam_stok += int(eski_satis.miktar)
            except Satis.DoesNotExist:
                pass
        
        # Şimdi kontrol et
        if toplam_stok < int(self.miktar):
            raise ValidationError({
                'miktar': f'Yetersiz stok! Toplam stokta {toplam_stok} adet var, {int(self.miktar)} adet satmaya çalışıyorsunuz.'
            })
        
        if toplam_stok == 0:
            raise ValidationError({
                'urun': f'{self.urun.urun_adi} için stokta ürün yok!'
            })
    
    def save(self, *args, **kwargs):
        # 1. Birim fiyatı çek
        try:
            fiyat_bilgisi = SatisFiyati.objects.get(urun=self.urun)
            self.birim_fiyat = fiyat_bilgisi.satis_fiyati
        except SatisFiyati.DoesNotExist:
            raise ValidationError(f"{self.urun.urun_adi} için satış fiyatı tanımlanmamış!")
        
        # 2. Toplam fiyatı hesapla
        self.toplam_fiyat = (self.birim_fiyat * self.miktar).quantize(Decimal('0.01'))
        
        # 3. Stok güncelleme - FIFO mantığı ile
        if self.pk:  # Güncelleme ise eski miktarı geri ekle
            try:
                eski_satis = Satis.objects.get(pk=self.pk)
                eski_yerlesim = UrunYerlesimYeri.objects.filter(
                    urun=self.urun,
                    miktar__gt=0
                ).order_by('son_kullanma_tarihi', 'giris_tarihi').first()
                if eski_yerlesim:
                    eski_yerlesim.miktar += int(eski_satis.miktar)
                    eski_yerlesim.save()
            except Satis.DoesNotExist:
                pass
        
        # Yeni satış için stok düş - FIFO mantığıyla
        kalan_miktar = int(self.miktar)
        
        while kalan_miktar > 0:
            # En eski SKT'li ve stokta olan lot'u bul
            yerlesim = UrunYerlesimYeri.objects.filter(
                urun=self.urun,
                miktar__gt=0
            ).order_by('son_kullanma_tarihi', 'giris_tarihi').first()
            
            if not yerlesim:
                raise ValidationError(f'{self.urun.urun_adi} için yeterli stok yok!')
            
            # Bu lot'tan ne kadar düşülebilir?
            if yerlesim.miktar >= kalan_miktar:
                # Bu lot yeterli
                yerlesim.miktar -= kalan_miktar
                yerlesim.save()
                kalan_miktar = 0
            else:
                # Bu lot'u tamamen bitir, kalanı bir sonraki lot'tan düş
                kalan_miktar -= yerlesim.miktar
                yerlesim.miktar = 0
                yerlesim.save()
        
        # 4. Kaydet
        super().save(*args, **kwargs)
        
        # 5. Fiş toplamını güncelle
        self.fis.toplam_tutar = sum(
            satis.toplam_fiyat for satis in self.fis.satislar.all()
        )
        self.fis.save()
        
        # 6. KASA KAYDI OLUŞTUR
        SatisKasa.objects.get_or_create(
            satis=self,
            defaults={'tutar': self.toplam_fiyat}
        )
        
    def __str__(self):
        return f"Satış #{self.fis.fis_no} - {self.urun.urun_adi} - {self.miktar} adet"
    
    class Meta:
        verbose_name = 'Satış'
        verbose_name_plural = 'Satışlar'
        ordering = ['-fis__olusturma_tarihi']
        
class TedarikciIade(models.Model):
    IADE_DURUM = [
        ('beklemede', 'İade Beklemede'),
        ('kabul', 'Tedarikçi Kabul Etti'),
        ('red', 'Tedarikçi Reddetti'),
        ('degisim', 'Yenisiyle Değiştirildi'),
    ]
    
    urun = models.ForeignKey(Urun, on_delete=models.PROTECT, verbose_name='Ürün')
    yerlesim = models.ForeignKey(UrunYerlesimYeri, on_delete=models.PROTECT, verbose_name='Lot/Yerleşim', blank=True, null=True)
    tedarikci = models.ForeignKey(Tedarikci, on_delete=models.PROTECT, verbose_name='Tedarikçi')
    miktar = models.IntegerField(verbose_name='İade Miktarı')
    iade_nedeni = models.TextField(verbose_name='İade Nedeni')
    durum = models.CharField(max_length=20, choices=IADE_DURUM, default='beklemede', verbose_name='Durum')
    iade_tarihi = models.DateTimeField(auto_now_add=True, verbose_name='İade Tarihi')
    cozum_tarihi = models.DateTimeField(blank=True, null=True, verbose_name='Çözüm Tarihi')
    not_lar = models.TextField(blank=True, verbose_name='Notlar')
    
    def save(self, *args, **kwargs):
        # İade kaydedilince stoktan düş
        if not self.pk and self.yerlesim:  # Yeni kayıt
            self.yerlesim.miktar -= self.miktar
            if self.yerlesim.miktar < 0:
                raise ValidationError('Yetersiz stok!')
            self.yerlesim.save()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"İade #{self.pk} - {self.urun.urun_adi} - {self.miktar} adet"
    
    class Meta:
        verbose_name = 'Tedarikçi İade'
        verbose_name_plural = 'Tedarikçi İadeler'
        ordering = ['-iade_tarihi']
            
            
class MusteriIade(models.Model):
    IADE_DURUM = [
        ('beklemede', 'İade Beklemede'),
        ('onaylandi', 'İade Onaylandı'),
        ('reddedildi', 'İade Reddedildi'),
    ]
    
    COZUM_TIP = [
        ('para', 'Para İadesi'),
        ('degisim', 'Ürün Değişimi'),
        ('kupon', 'İndirim Kuponu'),
    ]
    
    satis = models.ForeignKey(Satis, on_delete=models.PROTECT, verbose_name='Satış Kaydı', blank=True, null=True)
    urun = models.ForeignKey(Urun, on_delete=models.PROTECT, verbose_name='Ürün')
    miktar = models.IntegerField(verbose_name='İade Miktarı')
    iade_nedeni = models.TextField(verbose_name='İade Nedeni')
    durum = models.CharField(max_length=20, choices=IADE_DURUM, default='beklemede', verbose_name='Durum')
    cozum_tipi = models.CharField(max_length=20, choices=COZUM_TIP, blank=True, verbose_name='Çözüm Tipi')
    iade_tutari = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='İade Tutarı')
    iade_tarihi = models.DateTimeField(auto_now_add=True, verbose_name='İade Tarihi')
    islem_tarihi = models.DateTimeField(blank=True, null=True, verbose_name='İşlem Tarihi')
    not_lar = models.TextField(blank=True, verbose_name='Notlar')
    
    def save(self, *args, **kwargs):
        # İlk kez onaylanıyor mu kontrol et
        yeni_onay = False
        if self.pk:
            eski = MusteriIade.objects.get(pk=self.pk)
            if eski.durum != 'onaylandi' and self.durum == 'onaylandi':
                yeni_onay = True
        else:
            # Yeni kayıt ve zaten onaylı
            if self.durum == 'onaylandi':
                yeni_onay = True
        
        super().save(*args, **kwargs)
        
        # İade onaylanınca stok artar ve para iadesi yapılırsa kasa düşer
        if yeni_onay:
            # 1. Stoka geri ekle
            yerlesim = UrunYerlesimYeri.objects.filter(
                urun=self.urun,
                miktar__gt=0
            ).order_by('son_kullanma_tarihi', 'giris_tarihi').first()
            
            if yerlesim:
                yerlesim.miktar += self.miktar
                yerlesim.save()
            
            # 2. Para iadesi ise kasadan düş
            if self.cozum_tipi == 'para':
                kasa = Kasa.objects.first()
                if kasa:
                    kasa.bakiye -= self.iade_tutari
                    kasa.save()
    
    def __str__(self):
        return f"Müşteri İade #{self.pk} - {self.urun.urun_adi} - {self.miktar} adet"
    
    class Meta:
        verbose_name = 'Müşteri İade'
        verbose_name_plural = 'Müşteri İadeler'
        ordering = ['-iade_tarihi']
        
        
class Kasa(models.Model):
    bakiye = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Güncel Bakiye')
    son_guncelleme = models.DateTimeField(auto_now=True, verbose_name='Son Güncelleme')
    
    def __str__(self):
        return f"Kasa Bakiyesi: {self.bakiye} TL"
    
    class Meta:
        verbose_name = 'Kasa'
        verbose_name_plural = 'Kasa'
    
    def save(self, *args, **kwargs):
        # Tek kayıt olsun
        if not self.pk and Kasa.objects.exists():
            raise ValidationError('Sadece bir kasa kaydı olabilir!')
        super().save(*args, **kwargs)
        
# İŞLEM KAYITLARI

class SatisKasa(models.Model):
    satis = models.OneToOneField(Satis, on_delete=models.CASCADE, verbose_name='Satış')
    tutar = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Tutar')
    islem_tarihi = models.DateTimeField(auto_now_add=True, verbose_name='İşlem Tarihi')
    
    def save(self, *args, **kwargs):
        # Kasayı güncelle (Para GİRİŞİ)
        super().save(*args, **kwargs)
        kasa = Kasa.objects.first()
        if kasa:
            kasa.bakiye += self.tutar
            kasa.save()
    
    def __str__(self):
        return f"Satış #{self.satis.fis.fis_no} - {self.tutar} TL"
    
    class Meta:
        verbose_name = 'Satış Kasa Hareketi'
        verbose_name_plural = 'Satış Kasa Hareketleri'
        ordering = ['-islem_tarihi']


# ALIŞ FİŞİ (Toplu alış)
class AlisFisi(models.Model):
    fis_no = models.CharField(max_length=50, unique=True, verbose_name='Fiş/Fatura No')
    tedarikci = models.ForeignKey(Tedarikci, on_delete=models.PROTECT, verbose_name='Tedarikçi')
    lot_no = models.CharField(max_length=50, blank=True, verbose_name='Lot No')
    
    toplam_tutar = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Toplam Tutar')
    fis_tarihi = models.DateField(verbose_name='Fiş Tarihi')
    kayit_tarihi = models.DateTimeField(auto_now_add=True, verbose_name='Kayıt Tarihi')
    kullanici = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='İşlemi Yapan')
    
    def save(self, *args, **kwargs):
        # Lot no otomatik oluştur
        if not self.lot_no:
            from datetime import date
            bugun = date.today()
            son_lot = AlisFisi.objects.filter(
                lot_no__startswith=f'L{bugun.strftime("%Y%m%d")}'
            ).order_by('-lot_no').first()
            
            if son_lot:
                son_sira = int(son_lot.lot_no.split('-')[-1])
                yeni_sira = son_sira + 1
            else:
                yeni_sira = 1
            
            self.lot_no = f'L{bugun.strftime("%Y%m%d")}-{yeni_sira:03d}'
        
        # Eski toplam tutarı sakla
        eski_tutar = Decimal('0.00')
        if self.pk:
            try:
                eski_fis = AlisFisi.objects.get(pk=self.pk)
                eski_tutar = eski_fis.toplam_tutar
            except AlisFisi.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        # Kasa farkını güncelle
        fark = self.toplam_tutar - eski_tutar
        if fark != 0:
            kasa = Kasa.objects.first()
            if kasa:
                kasa.bakiye -= fark
                kasa.save()
            
    def __str__(self):
        return f"Alış Fişi #{self.fis_no} - {self.tedarikci.firma_adi}"
    
    class Meta:
        verbose_name = 'Alış Fişi'
        verbose_name_plural = 'Alış Fişleri'
        ordering = ['-fis_tarihi']


# ALIŞ DETAY (Her ürün için ayrı satır)
class AlisDetay(models.Model):
    fis = models.ForeignKey(AlisFisi, on_delete=models.CASCADE, related_name='detaylar', verbose_name='Alış Fişi')
    urun = models.ForeignKey(Urun, on_delete=models.PROTECT, verbose_name='Ürün')
    miktar = models.IntegerField(verbose_name='Miktar')
    birim_fiyat = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Birim Fiyat')
    toplam_fiyat = models.DecimalField(max_digits=10, decimal_places=2, editable=False, verbose_name='Toplam Fiyat')
    konum = models.CharField(max_length=50, verbose_name='Yerleşim Konumu')
    son_kullanma_tarihi = models.DateField(blank=True, null=True, verbose_name='Son Kullanma Tarihi')
    def save(self, *args, **kwargs):
        # Toplam fiyat hesapla
        self.toplam_fiyat = self.birim_fiyat * self.miktar
    
        super().save(*args, **kwargs)
        
        # UrunYerlesimYeri oluştur veya güncelle
        yerlesim, created = UrunYerlesimYeri.objects.get_or_create(
            urun=self.urun,
            lot_no=self.fis.lot_no,
            konum=self.konum,
            defaults={
                'miktar': self.miktar,
                'son_kullanma_tarihi': self.son_kullanma_tarihi
            }
        )
        
        if not created:
            yerlesim.miktar += self.miktar
            yerlesim.save()
        
        # Fiş toplamını güncelle
        self.fis.toplam_tutar = sum(
            detay.toplam_fiyat for detay in self.fis.detaylar.all()
        )
        self.fis.save()
        
        # ORTALAMA MALİYET HESAPLA VE SATIŞ FİYATINI GÜNCELLE
        from django.db.models import Sum, F
        
        # Tüm lotlardaki toplam stok ve toplam maliyet
        lotlar = UrunYerlesimYeri.objects.filter(
            urun=self.urun,
            miktar__gt=0
        )
        
        if lotlar.exists():
            # Her lot için (miktar × birim_fiyat) hesapla
            toplam_maliyet = Decimal('0.00')
            toplam_miktar = 0
            
            for lot in lotlar:
                # Bu lotun alış fiyatını bul
                alis = AlisDetay.objects.filter(
                    urun=self.urun,
                    fis__lot_no=lot.lot_no
                ).first()
                
                if alis:
                    toplam_maliyet += alis.birim_fiyat * lot.miktar
                    toplam_miktar += lot.miktar
            
            if toplam_miktar > 0:
                ortalama_maliyet = toplam_maliyet / toplam_miktar
                
                # SatisFiyati'ni güncelle veya oluştur
                satis_fiyati, created = SatisFiyati.objects.get_or_create(
                    urun=self.urun,
                    defaults={
                        'alim_fiyati': ortalama_maliyet,
                        'kar_orani': Decimal('25.00'),
                        'kdv': 20,
                        'iskonto_orani': Decimal('0.00'),
                        'satis_fiyati': Decimal('0.00')
                    }
                )
                
                if not created:
                    # Mevcut kayıt var, sadece alım fiyatını güncelle
                    satis_fiyati.alim_fiyati = ortalama_maliyet
                
                # Satış fiyatını yeniden hesapla (SatisFiyati modelinin save metodu otomatik hesaplar)
                satis_fiyati.save()
    
    def __str__(self):
        return f"{self.urun.urun_adi} - {self.miktar} adet"
    
    class Meta:
        verbose_name = 'Alış Detayı'
        verbose_name_plural = 'Alış Detayları'


class OdemeKasa(models.Model):
    ODEME_TIP = [
        ('fatura', 'Fatura'),
        ('kira', 'Kira'),
        ('maas', 'Maaş'),
        ('vergi', 'Vergi'),
        ('elektrik', 'Elektrik'),
        ('su', 'Su'),
        ('internet', 'İnternet'),
        ('kargo', 'Kargo'),
        ('diger', 'Diğer'),
    ]
    
    odeme_tipi = models.CharField(max_length=20, choices=ODEME_TIP, verbose_name='Ödeme Tipi')
    tutar = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Tutar')
    aciklama = models.TextField(verbose_name='Açıklama')
    odeme_tarihi = models.DateField(verbose_name='Ödeme Tarihi')
    islem_tarihi = models.DateTimeField(auto_now_add=True, verbose_name='Kayıt Tarihi')
    kullanici = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='İşlemi Yapan')
    
    def save(self, *args, **kwargs):
        yeni_kayit = self.pk is None
        
        super().save(*args, **kwargs)
        
        # Kasayı güncelle (Sadece ilk kayıtta)
        if yeni_kayit:
            kasa = Kasa.objects.first()
            if kasa:
                kasa.bakiye -= self.tutar
                kasa.save()
    
    def __str__(self):
        return f"{self.get_odeme_tipi_display()} - {self.tutar} TL"
    
    class Meta:
        verbose_name = 'Ödeme'
        verbose_name_plural = 'Ödemeler'
        ordering = ['-odeme_tarihi']