# ADR-0004: Olay bazlı, zaman sıralı dört dilimli bölme (T1 / T2 / doğrulama / kilitli test)

- **Durum:** Kabul edildi (2026-11-02)
- **Kaynak:** Kullanıcının faz 3 seçimi. 7. oturumdaki bölme kararını (eğitim / doğrulama / kilitli test, olay bazlı, zaman sıralı) inceltir.

## Bağlam

- Yol haritası Adım 2.3 ve s.3: bölme kodlamadan önce belirlenir; ilişkili kayıtlar aynı kümede kalır; zamansal veride ileriye dönük bölme tercih edilir; test kümesi model ya da eşik seçiminde kullanılmaz.
- s.10: geri bildirimli sürüm sabit bir test kümesinde karşılaştırılır.
- Arayüzde analistin düzelttiği olaylar onaylanınca eğitim etiketi deposuna ve yeniden eğitime girer (FR-15, FR-19). Bu olaylar kilitli testten gelirse test etiketi eğitime sızar. Doğrulamadan gelirse v2'nin eşik ve model seçimi kirlenir.
- GUIDE'ın resmî bölmesi olay bazlı ama zamana göre değil. Satırların %98'i ~26 güne yayılıyor; zaman damgalarına gürültü eklenmiş; dosya sırasız (veri denetimi).

## Değerlendirilen seçenekler

1. **Dört dilim, 50/20/15/15** (seçildi): T1 eğitim (v1) → T2 geri bildirim havuzu (arayüz ve AS1) → doğrulama → kilitli test.
2. **Dört dilim, başka oranlar:** Yapı aynı; T2 küçülürse AS1'de etiket havuzu daralır.
3. **Üç dilim, arayüz doğrulama kümesinden:** Daha basit, ama v2'nin seçimi analist düzeltmelerinin girdiği kümede yapılmış olur (Arp vd. P3). Elendi.

## Karar

- **Birim:** olay (`OrgId + IncidentId`). Bir olayın bütün satırları aynı dilimde kalır.
- **Kapsam:** olay kategorisi InitialAccess, SuspiciousActivity ya da Exfiltration olan, `IncidentGrade` değeri dolu olaylar. Olay kategorisinin nasıl hesaplandığı `docs/data-design.md`'de yazılı.
- **Olay zamanı:** olayın en erken uyarı zaman damgası (`min(Timestamp)`).
- **Sıralama:** (olay zamanı, OrgId, IncidentId) artan. İkinci ve üçüncü anahtar eşit zamanlar için belirlenimci sıra sağlar.
- **Kesimler:** sıralı listenin ilk %50'si T1, sonraki %20'si T2, sonraki %15'i doğrulama, son %15'i kilitli test.
- **Kullanım kuralları:**
  - v1 yalnız T1'de eğitilir.
  - v2 = T1 + T2'nin onaylı etiketleri (etiket deposundan).
  - Ön işleme, sözlük ve ölçekleme yalnız T1'den öğrenilir. v2 için T1 ∪ (onaylı T2) kullanılır.
  - Eşik ve model seçimi doğrulamada yapılır.
  - Kilitli test yalnız sürüm karşılaştırmasında okunur (NFR-15).
  - Arayüze ve AS1'e yalnız T2 olayları girer.
  - Resmî GUIDE_Test ek sonuç olarak aynı kapsam süzgeciyle raporlanır.
- **Veri sürümü:** bölme çıktısı, girdi dosyalarının boyut ve değişiklik zamanından, bölme parametrelerinden ve kod sürümünden türetilen bir kimlik taşır (`docs/data-design.md`).

## Sonuçlar

- **Olumlu:** Arayüzden ya da AS1'den gelen etiketler test ve doğrulama kümelerine hiçbir yoldan sızamaz. v1–v2 karşılaştırması s.10'a uygun biçimde sabit test kümesinde yapılır.
- **Olumsuz / riskler:**
  - Zaman damgalarındaki gürültü yüzünden sıralama yaklaşıktır; sınırlılık olarak yazılır.
  - v1 verinin yalnız yarısıyla eğitilir.
  - Kurumlar dilimler arasında ortaktır (resmî bölmede de öyle); kurum düzeyinde genelleme ölçülmez.

## İzlenebilirlik

- **Gereksinim:** FR-19, FR-20, FR-26, FR-29, NFR-15
- **Bağlantılı:** ADR-0002, ADR-0005
