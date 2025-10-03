from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Sum
from decimal import Decimal
from datetime import datetime, date
from .models import *


@staff_member_required
def envanter_raporu(request):
    """Envanter raporu sayfası"""
    
    # Tüm ürünleri ve lotlarını getir
    urunler = []
    for urun in Urun.objects.all():
        lotlar = UrunYerlesimYeri.objects.filter(urun=urun, miktar__gt=0)  # miktar > 0 eklendi
        if lotlar.exists():
            toplam_miktar = lotlar.aggregate(toplam=Sum('miktar'))['toplam'] or 0
            urunler.append({
                'urun': urun,
                'toplam': toplam_miktar,
                'lotlar': lotlar
            })
    
    context = {
        'urunler': urunler,
        'tarih': date.today()
    }
    
    return render(request, 'admin/envanter_raporu.html', context)


@staff_member_required
def muhasebe_raporu(request):
    """Muhasebe raporu sayfası"""
    
    # Ay ve yıl parametreleri
    ay = int(request.GET.get('ay', date.today().month))
    yil = int(request.GET.get('yil', date.today().year))
    
    # Ay başı ve sonu
    ay_basi = datetime(yil, ay, 1)
    if ay == 12:
        ay_sonu = datetime(yil + 1, 1, 1)
    else:
        ay_sonu = datetime(yil, ay + 1, 1)
    
    # Kasa
    kasa = Kasa.objects.first()
    
    # Satışlar
    satislar = SatisKasa.objects.filter(
        islem_tarihi__gte=ay_basi,
        islem_tarihi__lt=ay_sonu
    )
    satis_toplam = satislar.aggregate(toplam=Sum('tutar'))['toplam'] or Decimal('0.00')
    
    # Alışlar
    alislar = AlisFisi.objects.filter(
        fis_tarihi__gte=ay_basi.date(),
        fis_tarihi__lt=ay_sonu.date()
    )
    alis_toplam = alislar.aggregate(toplam=Sum('toplam_tutar'))['toplam'] or Decimal('0.00')
    
    # Ödemeler (kategorilere göre)
    odemeler = OdemeKasa.objects.filter(
        odeme_tarihi__gte=ay_basi.date(),
        odeme_tarihi__lt=ay_sonu.date()
    )
    
    odeme_detay = []
    for odeme_tip in OdemeKasa.ODEME_TIP:
        tip_kod = odeme_tip[0]
        tip_adi = odeme_tip[1]
        tip_toplam = odemeler.filter(odeme_tipi=tip_kod).aggregate(toplam=Sum('tutar'))['toplam'] or Decimal('0.00')
        if tip_toplam > 0:
            odeme_detay.append({
                'tip': tip_adi,
                'tutar': tip_toplam
            })
    
    odeme_toplam = odemeler.aggregate(toplam=Sum('tutar'))['toplam'] or Decimal('0.00')
    
    # Hesaplamalar
    toplam_gider = alis_toplam + odeme_toplam
    net_kar = satis_toplam - toplam_gider
    
    context = {
        'ay': ay,
        'yil': yil,
        'ay_adi': ay_basi.strftime('%B'),
        'kasa_bakiye': kasa.bakiye if kasa else 0,
        'satis_toplam': satis_toplam,
        'satis_adet': satislar.count(),
        'alis_toplam': alis_toplam,
        'alis_adet': alislar.count(),
        'odeme_detay': odeme_detay,
        'odeme_toplam': odeme_toplam,
        'toplam_gider': toplam_gider,
        'net_kar': net_kar,
    }
    
    return render(request, 'admin/muhasebe_raporu.html', context)