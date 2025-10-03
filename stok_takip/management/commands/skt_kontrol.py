from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from stok_takip.models import UrunYerlesimYeri
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Son kullanma tarihi yaklaşan ürünleri kontrol eder'

    def handle(self, *args, **options):
        bugun = date.today()
        
        # 30 gün içinde süresi dolacak ürünler
        uyari_30_gun = bugun + timedelta(days=30)
        
        # Süresi geçmiş ürünler
        suresi_gecmis = UrunYerlesimYeri.objects.filter(
            son_kullanma_tarihi__lt=bugun,
            son_kullanma_tarihi__isnull=False
        )
        
        # 30 gün içinde dolacaklar
        yakinda_dolacak = UrunYerlesimYeri.objects.filter(
            son_kullanma_tarihi__gte=bugun,
            son_kullanma_tarihi__lte=uyari_30_gun,
            son_kullanma_tarihi__isnull=False
        )
        
        # Konsola yazdır
        self.stdout.write(self.style.WARNING('\n' + '='*60))
        self.stdout.write(self.style.WARNING('SON KULLANMA TARİHİ KONTROL RAPORU'))
        self.stdout.write(self.style.WARNING(f'Tarih: {bugun.strftime("%d.%m.%Y")}'))
        self.stdout.write(self.style.WARNING('='*60 + '\n'))
        
        # Süresi geçmiş
        if suresi_gecmis.exists():
            self.stdout.write(self.style.ERROR(f'\n🔴 SÜRESİ GEÇMİŞ ÜRÜNLER ({suresi_gecmis.count()} adet):'))
            for item in suresi_gecmis:
                kalan = (bugun - item.son_kullanma_tarihi).days
                self.stdout.write(self.style.ERROR(
                    f'  • {item.urun.urun_adi} (Lot: {item.lot_no}) - {item.konum} - '
                    f'{kalan} gün önce süresi doldu - {item.miktar} adet'
                ))
        else:
            self.stdout.write(self.style.SUCCESS('✅ Süresi geçmiş ürün yok\n'))
        
        # Yakında dolacak
        if yakinda_dolacak.exists():
            self.stdout.write(self.style.WARNING(f'\n🟠 30 GÜN İÇİNDE SÜRESİ DOLACAK ({yakinda_dolacak.count()} adet):'))
            for item in yakinda_dolacak:
                kalan = (item.son_kullanma_tarihi - bugun).days
                self.stdout.write(self.style.WARNING(
                    f'  • {item.urun.urun_adi} (Lot: {item.lot_no}) - {item.konum} - '
                    f'{kalan} gün kaldı - {item.miktar} adet'
                ))
        else:
            self.stdout.write(self.style.SUCCESS('✅ 30 gün içinde dolacak ürün yok\n'))
        
        self.stdout.write(self.style.WARNING('\n' + '='*60 + '\n'))
        
        # Email gönder (opsiyonel)
        if suresi_gecmis.exists() or yakinda_dolacak.exists():
            self.send_email_alert(suresi_gecmis, yakinda_dolacak)
    
    def send_email_alert(self, suresi_gecmis, yakinda_dolacak):
        """Email uyarısı gönder"""
        # Şimdilik atla, isterseniz sonra ekleriz
        pass