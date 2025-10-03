from django.core.management.base import BaseCommand
from django.db.models import Sum
from stok_takip.models import Kasa, SatisKasa, AlisFisi, OdemeKasa
from datetime import date, datetime
from decimal import Decimal


class Command(BaseCommand):
    help = 'Aylık muhasebe raporu'
    
    def add_arguments(self, parser):
        parser.add_argument('--ay', type=int, help='Ay (1-12)')
        parser.add_argument('--yil', type=int, help='Yıl')

    def handle(self, *args, **options):
        ay = options.get('ay') or date.today().month
        yil = options.get('yil') or date.today().year
        
        # Ay başı ve sonu
        ay_basi = datetime(yil, ay, 1)
        if ay == 12:
            ay_sonu = datetime(yil + 1, 1, 1)
        else:
            ay_sonu = datetime(yil, ay + 1, 1)
        
        self.stdout.write(self.style.WARNING('\n' + '='*80))
        self.stdout.write(self.style.WARNING(f'MUHASEBE RAPORU - {ay_basi.strftime("%B %Y")}'))
        self.stdout.write(self.style.WARNING('='*80 + '\n'))
        
        # Kasa bakiye
        kasa = Kasa.objects.first()
        self.stdout.write(self.style.SUCCESS(f"\nGÜNCEL KASA BAKİYESİ: {kasa.bakiye} TL\n"))
        
        # Satış toplamı
        satislar = SatisKasa.objects.filter(
            islem_tarihi__gte=ay_basi,
            islem_tarihi__lt=ay_sonu
        )
        satis_toplam = satislar.aggregate(toplam=Sum('tutar'))['toplam'] or Decimal('0.00')
        
        self.stdout.write(self.style.SUCCESS(f"GELİRLER:"))
        self.stdout.write(f"  Satış Geliri: {satis_toplam} TL ({satislar.count()} işlem)")
        
        # Giderler
        self.stdout.write(self.style.ERROR(f"\nGİDERLER:"))
        
        # Alış giderleri
        alislar = AlisFisi.objects.filter(
            fis_tarihi__gte=ay_basi.date(),
            fis_tarihi__lt=ay_sonu.date()
        )
        alis_toplam = alislar.aggregate(toplam=Sum('toplam_tutar'))['toplam'] or Decimal('0.00')
        self.stdout.write(f"  Alış: {alis_toplam} TL ({alislar.count()} fiş)")
        
        # Ödemeler
        odemeler = OdemeKasa.objects.filter(
            odeme_tarihi__gte=ay_basi.date(),
            odeme_tarihi__lt=ay_sonu.date()
        )
        
        for odeme_tip in OdemeKasa.ODEME_TIP:
            tip_kod = odeme_tip[0]
            tip_adi = odeme_tip[1]
            tip_toplam = odemeler.filter(odeme_tipi=tip_kod).aggregate(toplam=Sum('tutar'))['toplam'] or Decimal('0.00')
            if tip_toplam > 0:
                self.stdout.write(f"  {tip_adi}: {tip_toplam} TL")
        
        odeme_toplam = odemeler.aggregate(toplam=Sum('tutar'))['toplam'] or Decimal('0.00')
        
        # Özet
        toplam_gider = alis_toplam + odeme_toplam
        net_kar = satis_toplam - toplam_gider
        
        self.stdout.write(self.style.WARNING(f"\n{'='*80}"))
        self.stdout.write(f"TOPLAM GELİR: {satis_toplam} TL")
        self.stdout.write(f"TOPLAM GİDER: {toplam_gider} TL")
        self.stdout.write(self.style.SUCCESS(f"NET KAR/ZARAR: {net_kar} TL"))
        self.stdout.write(self.style.WARNING('='*80 + '\n'))