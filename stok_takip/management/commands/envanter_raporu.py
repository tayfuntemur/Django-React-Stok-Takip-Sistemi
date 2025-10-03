from django.core.management.base import BaseCommand
from django.db.models import Sum
from stok_takip.models import Urun, UrunYerlesimYeri
from datetime import date


class Command(BaseCommand):
    help = 'Envanter raporu oluşturur'

    def handle(self, *args, **options):
        bugun = date.today()
        
        self.stdout.write(self.style.WARNING('\n' + '='*80))
        self.stdout.write(self.style.WARNING(f'ENVANTER RAPORU - {bugun.strftime("%B %Y")}'))
        self.stdout.write(self.style.WARNING('='*80 + '\n'))
        
        # Tüm ürünleri al
        urunler = Urun.objects.all()
        
        for urun in urunler:
            # Bu ürünün tüm lotlarını al
            lotlar = UrunYerlesimYeri.objects.filter(urun=urun)
            
            if lotlar.exists():
                toplam_miktar = lotlar.aggregate(toplam=Sum('miktar'))['toplam'] or 0
                
                self.stdout.write(f"\n{urun.stok_no} - {urun.urun_adi}")
                self.stdout.write(f"  Toplam: {toplam_miktar} {urun.birim}")
                
                for lot in lotlar:
                    self.stdout.write(f"    • Lot: {lot.lot_no}, Konum: {lot.konum}, Miktar: {lot.miktar}")
        
        self.stdout.write(self.style.WARNING('\n' + '='*80 + '\n'))