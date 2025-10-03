from django.contrib import admin
from .models import Kategori,Tedarikci,Urun,UrunYerlesimYeri,SatisFiyati,SatisFisi,Satis,TedarikciIade,MusteriIade,Kasa,AlisDetay,AlisFisi,OdemeKasa
from django.db import models



@admin.register(Kategori)
class KategoriAdmin(admin.ModelAdmin):
    
    list_display = ['kategori_adi', 'id']
    search_fields = ['kategori_adi']
    ordering = ['kategori_adi']
    
    
    
@admin.register(Tedarikci)
class TedarikciAdmin(admin.ModelAdmin):
    
    list_display = ['firma_adi','telefon','adres']
    search_fields = ['firma_adi']
    ordering = ['firma_adi']
    
    
    
@admin.register(Urun)
class UrunAdmin(admin.ModelAdmin):
    
    list_display = ['stok_no','urun_adi','kategori','birim','barkod']
    search_fields = ['stok_no' , 'urun_adi','kategori__kategori_adi']
    list_filter =['kategori']
    
    fieldsets = (
       ('Temel Bilgiler',{
           'fields':('stok_no','urun_adi','kategori','birim')
       }),
      
       ('Barkod',{
           'fields':('barkod','barkod_resim'),
           'classes':('collapse',)
       }),
       ('Tarih', {
           'fields' : ('olusturma_tarihi','guncelleme_tarihi'),
           'classes' :('collapse',)
       }),
    )
    readonly_fields = ('olusturma_tarihi','guncelleme_tarihi')
    
    
@admin.register(UrunYerlesimYeri)
class UrunYerlesimYeriAdmin(admin.ModelAdmin):
    
    list_display = ['get_stok_no', 'get_urun_adi', 'miktar', 'konum', 'lot_no', 'son_kullanma_tarihi', 'skt_durumu']
    search_fields = ['urun__stok_no', 'urun__urun_adi', 'lot_no']
    list_filter = ['konum', 'son_kullanma_tarihi']
    
    def get_stok_no(self, obj):
        return obj.urun.stok_no
    get_stok_no.short_description = 'Stok No'
    
    def get_urun_adi(self, obj):
        return obj.urun.urun_adi
    get_urun_adi.short_description = 'Ürün Adı'
    
    def skt_durumu(self, obj):
        if not obj.son_kullanma_tarihi:
            return '-'
        
        from datetime import date, timedelta
        bugun = date.today()
        kalan_gun = (obj.son_kullanma_tarihi - bugun).days
        
        if kalan_gun < 0:
            return f'🔴 Süresi geçmiş ({abs(kalan_gun)} gün önce)'
        elif kalan_gun <= 30:
            return f'🟠 {kalan_gun} gün kaldı'
        elif kalan_gun <= 90:
            return f'🟡 {kalan_gun} gün kaldı'
        else:
            return f'🟢 {kalan_gun} gün kaldı'
    
    skt_durumu.short_description = 'SKT Durumu'
    
    fieldsets = (
        ('Ürün Bilgisi', {
            'fields': ('urun',)
        }),
        ('Yerleşim Detayı', {
            'fields': ('miktar', 'konum', 'lot_no', 'son_kullanma_tarihi')
        })
    )
    
@admin.register(SatisFiyati)
class SatisFiyatiAdmin(admin.ModelAdmin):
    
    list_display =['get_stok_no','get_urun_adi','alim_fiyati','kar_orani','kdv','iskonto_orani','satis_fiyati']
    search_fields=['urun__stok_no' , 'urun__urun_adi']
    
    def get_stok_no(self,obj):
        return obj.urun.stok_no
    get_stok_no.short_description = 'Stok No'
    
    def get_urun_adi(self,obj):
        return obj.urun.urun_adi
    get_urun_adi.short_description = 'Ürün Adı'
    
    fieldsets = (
        ('Ürün Bilgisi',{
            'fields':('urun',)
        }),
        ('Hesaplama Bilgileri',{
           'fields': ('alim_fiyati','kar_orani','kdv','iskonto_orani',)
        })
    )
    
# Inline: Fiş içinde satışları göster
class SatisInline(admin.TabularInline):
    model = Satis
    extra = 3
    fields = ['urun', 'get_mevcut_stok', 'miktar', 'birim_fiyat', 'toplam_fiyat']
    readonly_fields = ['get_mevcut_stok', 'birim_fiyat', 'toplam_fiyat']
    
    def get_mevcut_stok(self, obj):
        if obj and obj.urun:
            try:
                    # Tüm lotların toplamı
                toplam_stok = UrunYerlesimYeri.objects.filter(
                    urun=obj.urun
                ).aggregate(toplam=models.Sum('miktar'))['toplam'] or 0
                
                stok = toplam_stok
                
                # Renk kodu
                if stok == 0:
                   
                    ikon = '🔴'
                elif stok < 5:
                    
                    ikon = '🟠'
                else:
                   
                    ikon = '🟢'
                
                return f'Kalan Mevcut:{ikon} {stok} adet'
            except UrunYerlesimYeri.DoesNotExist:
                return '⚠️ Stok kaydı yok'
        return '-'
    
    get_mevcut_stok.short_description = 'Mevcut Stok'
    get_mevcut_stok.allow_tags = True


@admin.register(SatisFisi)
class SatisFisiAdmin(admin.ModelAdmin):
    list_display = ['fis_no', 'kullanici', 'get_urun_sayisi', 'toplam_tutar', 'get_tarih']
    list_filter = ['olusturma_tarihi', 'kullanici']
    search_fields = ['fis_no', 'kullanici__username']
    readonly_fields = ['fis_no', 'toplam_tutar', 'olusturma_tarihi']
    inlines = [SatisInline]
    
    def get_urun_sayisi(self, obj):
        return obj.satislar.count()
    get_urun_sayisi.short_description = 'Ürün Çeşidi'
    
    def get_tarih(self, obj):
        return obj.olusturma_tarihi.strftime('%d.%m.%Y %H:%M')
    get_tarih.short_description = 'Satış Tarihi'
    
    fieldsets = (
        ('Fiş Bilgileri', {
            'fields': ('fis_no', 'kullanici', 'olusturma_tarihi')
        }),
        ('Toplam Tutar', {
            'fields': ('toplam_tutar',),
        }),
    )


@admin.register(Satis)
class SatisAdmin(admin.ModelAdmin):
    list_display = ['get_fis_no', 'get_urun_adi', 'miktar', 'birim_fiyat', 'toplam_fiyat', 'get_tarih']
    list_filter = ['fis__olusturma_tarihi', 'urun__kategori']
    search_fields = ['fis__fis_no', 'urun__urun_adi', 'urun__stok_no']
    readonly_fields = ['birim_fiyat', 'toplam_fiyat']
    ordering = ['-fis__fis_no']
    
    def get_fis_no(self, obj):
        return f"Fiş #{obj.fis.fis_no}"
    get_fis_no.short_description = 'Fiş No'
    get_fis_no.admin_order_field = 'fis__fis_no' 
    
    def get_urun_adi(self, obj):
        return obj.urun.urun_adi
    get_urun_adi.short_description = 'Ürün'
    
    def get_tarih(self, obj):
        return obj.fis.olusturma_tarihi.strftime('%d.%m.%Y %H:%M')
    get_tarih.short_description = 'Tarih'
    
    fieldsets = (
        ('Fiş', {
            'fields': ('fis',)
        }),
        ('Ürün Bilgisi', {
            'fields': ('urun', 'miktar')
        }),
        ('Fiyat (Otomatik)', {
            'fields': ('birim_fiyat', 'toplam_fiyat'),
        }),
    )
    
    
@admin.register(TedarikciIade)
class TedarikciIadeAdmin(admin.ModelAdmin):
    list_display = ['get_iade_no', 'get_urun_adi', 'tedarikci', 'miktar', 'durum', 'iade_tarihi', 'durum_ikonu']
    list_filter = ['durum', 'iade_tarihi', 'tedarikci']
    search_fields = ['urun__urun_adi', 'urun__stok_no', 'iade_nedeni']
    readonly_fields = ['iade_tarihi']
    
    def get_iade_no(self, obj):
        return f"İADE-{obj.pk:04d}"
    get_iade_no.short_description = 'İade No'
    
    def get_urun_adi(self, obj):
        return f"{obj.urun.stok_no} - {obj.urun.urun_adi}"
    get_urun_adi.short_description = 'Ürün'
    
    def durum_ikonu(self, obj):
        ikonlar = {
            'beklemede': '🟡 Beklemede',
            'kabul': '🟢 Kabul Edildi',
            'red': '🔴 Reddedildi',
            'degisim': '✅ Değiştirildi',
        }
        return ikonlar.get(obj.durum, obj.durum)
    durum_ikonu.short_description = 'Durum'
    
    fieldsets = (
        ('Ürün Bilgisi', {
            'fields': ('urun', 'yerlesim', 'tedarikci', 'miktar')
        }),
        ('İade Detayları', {
            'fields': ('iade_nedeni', 'durum', 'iade_tarihi', 'cozum_tarihi')
        }),
        ('Notlar', {
            'fields': ('not_lar',),
            'classes': ('collapse',)
        }),
    )
    
@admin.register(MusteriIade)
class MusteriIadeAdmin(admin.ModelAdmin):
    list_display = ['get_iade_no', 'get_urun_adi', 'miktar', 'cozum_tipi', 'iade_tutari', 'durum', 'iade_tarihi', 'durum_ikonu']
    list_filter = ['durum', 'cozum_tipi', 'iade_tarihi']
    search_fields = ['urun__urun_adi', 'urun__stok_no', 'iade_nedeni']
    readonly_fields = ['iade_tarihi']
    
    def get_iade_no(self, obj):
        return f"M-İADE-{obj.pk:04d}"
    get_iade_no.short_description = 'İade No'
    
    def get_urun_adi(self, obj):
        return f"{obj.urun.stok_no} - {obj.urun.urun_adi}"
    get_urun_adi.short_description = 'Ürün'
    
    def durum_ikonu(self, obj):
        ikonlar = {
            'beklemede': '🟡 Beklemede',
            'onaylandi': '✅ Onaylandı',
            'reddedildi': '🔴 Reddedildi',
        }
        return ikonlar.get(obj.durum, obj.durum)
    durum_ikonu.short_description = 'Durum'
    
    fieldsets = (
        ('Ürün Bilgisi', {
            'fields': ('satis', 'urun', 'miktar')
        }),
        ('İade Detayları', {
            'fields': ('iade_nedeni', 'durum', 'cozum_tipi', 'iade_tutari', 'iade_tarihi', 'islem_tarihi')
        }),
        ('Notlar', {
            'fields': ('not_lar',),
            'classes': ('collapse',)
        }),
    )
    
@admin.register(Kasa)
class KasaAdmin(admin.ModelAdmin):
    list_display = ['bakiye', 'son_guncelleme']
    
    def has_add_permission(self, request):
        # Tek kayıt varsa ekleme izni yok
        return not Kasa.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Kasa silinemez
        return False
    
    
    
# Alış Detay Inline
class AlisDetayInline(admin.TabularInline):
    model = AlisDetay
    extra = 3
    fields = ['urun', 'miktar', 'birim_fiyat', 'toplam_fiyat', 'konum', 'son_kullanma_tarihi']
    readonly_fields = ['toplam_fiyat']


@admin.register(AlisFisi)
class AlisFisiAdmin(admin.ModelAdmin):
    list_display = ['fis_no', 'tedarikci', 'lot_no', 'toplam_tutar', 'fis_tarihi', 'get_urun_sayisi']
    list_filter = ['fis_tarihi', 'tedarikci']
    search_fields = ['fis_no', 'lot_no']
    readonly_fields = ['lot_no', 'toplam_tutar', 'kayit_tarihi']
    inlines = [AlisDetayInline]
    
    def get_urun_sayisi(self, obj):
        return obj.detaylar.count()
    get_urun_sayisi.short_description = 'Ürün Çeşidi'
    
    fieldsets = (
        ('Fiş Bilgileri', {
            'fields': ('fis_no', 'tedarikci', 'lot_no','fis_tarihi', 'kullanici')
        }),
        ('Toplam', {
            'fields': ('toplam_tutar', 'kayit_tarihi'),
        }),
    )


@admin.register(AlisDetay)
class AlisDetayAdmin(admin.ModelAdmin):
    list_display = ['get_fis_no', 'urun', 'miktar', 'birim_fiyat', 'toplam_fiyat', 'konum']
    list_filter = ['fis__fis_tarihi']
    search_fields = ['fis__fis_no', 'urun__urun_adi']
    readonly_fields = ['toplam_fiyat']
    
    def get_fis_no(self, obj):
        return obj.fis.fis_no
    get_fis_no.short_description = 'Fiş No'
    
@admin.register(OdemeKasa)
class OdemeKasaAdmin(admin.ModelAdmin):
    list_display = ['get_odeme_no', 'odeme_tipi', 'tutar', 'odeme_tarihi', 'kullanici']
    list_filter = ['odeme_tipi', 'odeme_tarihi']
    search_fields = ['aciklama']
    readonly_fields = ['islem_tarihi']
    
    def get_odeme_no(self, obj):
        return f"OD-{obj.pk:04d}"
    get_odeme_no.short_description = 'Ödeme No'
    
    fieldsets = (
        ('Ödeme Bilgileri', {
            'fields': ('odeme_tipi', 'tutar', 'odeme_tarihi', 'kullanici')
        }),
        ('Açıklama', {
            'fields': ('aciklama',)
        }),
        ('Kayıt', {
            'fields': ('islem_tarihi',),
            'classes': ('collapse',)
        }),
    )