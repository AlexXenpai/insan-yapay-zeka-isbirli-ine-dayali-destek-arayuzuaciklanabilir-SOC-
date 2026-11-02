# Proje planı ve görev dağılımı

- **Güncelleme:** 2026-11-02
- **İlgili dokümanlar:** `docs/srs.md` (FR/NFR ve hedef haftalar), `docs/test-plan.md`, `docs/plans/2026-11-02-hafta-1-5-ciktilari-ve-demo.md`

Bu belge yol haritası Adım 1.4'ün çıktısıdır: görevler sorumlu, teslim haftası ve doğrulama kanıtıyla izlenir; haftalık kısa ilerleme notu tutulur; iki haftada bir danışman görüşmesi yapılır. s.18'e göre veri/yöntem, yazılım ve test/dokümantasyon sorumlulukları paylaşılır ve her öğrenci diğerinin modülünü de anlatabilmelidir.

## 1. Görev paketleri (eşit ağırlık; kullanıcı kararı 2026-11-02)

| | Paket A: Veri ve model | Paket B: Etkileşim ve insan |
|---|---|---|
| **Sorumlu** | Mehmet Emin Duran | Ali İhsan Dağaşan |
| **AI bileşeni** | Taban ve ana model, SHAP açıklaması | Ön denetçi: kural ve LLM (H2) |
| **Araştırma sorusu** | AS1 simülasyonu (ana soru), AS2 raporu | AS3 insan çalışması (etik süreç, materyal, oturumlar, analiz) |
| **Yazılım** | Veri hattı ve bölme, depolar (denetim izi, etiket deposu), vaka kartı dönüştürücü, yeniden eğitim ve sürüm karşılaştırması | REST API ve karar akışı (K3), roller ve kimlik doğrulama, web arayüzü |
| **Test ve doküman** | Kendi modüllerinin testleri ve rapor bölümleri; B'nin kodunu gözden geçirir | Kendi modüllerinin testleri ve rapor bölümleri; A'nın kodunu gözden geçirir |

Paketlerin kesiştiği yerler:
- API → çekirdek: `docs/architecture.md` §3 ve §6.
- AS1 → ön denetçi: `socxai.precheck.check(record) -> Flag`.
- Çalışma modu → kart ve model: `socxai.data.cards`, `socxai.store.suggestions`.

## 2. Haftalık görevler

"Kanıt" sütunu, görevin bitmiş sayılması için gereken doğrulamadır: geçen testler, ölçüm dosyası ya da belge. Ekran görüntüsü tek başına kanıt sayılmaz (s.18).

| Hafta | Sorumlu | Görev | Gereksinim | Kanıt |
|---|---|---|---|---|
| 1–2 | A + B | Problem tanımı, kaynak karşılaştırması, SRS, veri kaynağı ve araçlar, B planı, bu plan | — | `docs/srs.md`, `docs/research/2026-11-02-kaynak-karsilastirmasi.md`, ADR-0001–0005 |
| 3–4 | A + B | Mimari, ekran taslakları, veri şeması, bölme, deney ve test planı, risk kaydı | — | `docs/architecture.md`, `docs/data-design.md`, `docs/experiments/2026-11-02-temel-model-ve-as1.md`, `docs/test-plan.md`, `docs/risk-register.md` |
| 5 | A | Proje iskeleti, veri hattı, özellikler, taban model, açıklama, demo havuzu | FR-02–05, FR-26, FR-27 | TC-01–05, TC-16, TC-21, TC-24 geçer; `metrics.json` |
| 5 | B | Karar servisi, API, demo arayüzü (S1, S2) | FR-06–11, FR-22, FR-23 (kısmi), FR-25 | TC-06–15, TC-17–20, TC-25 geçer |
| 6 | A + B | Demo kodunun eksik testleri, kapsam ölçümü (TDD'ye geçiş) | — | `pytest --cov` raporu; test planı §4 hedefleri |
| 7–8 | B | Kuyruk (FR-01), yerel hesap ve oturum (FR-24), izin matrisinin tamamı (FR-23) | FR-01, FR-23, FR-24 | TC-14, TC-27, TC-28; MVP ara demosu (s.3, 8. hafta) |
| 7–8 | A | Etiket deposu şeması ve uzlaştırma betiği; GUIDE_Test'in işlenmesi | FR-15 (altyapı) | Göç testleri; manifest |
| 9–10 | A | LightGBM ana model, E2 ablasyonu, E3 eşik; yeniden eğitim ve sürüm karşılaştırması | FR-19, FR-20, FR-28, FR-04 | TC-39, TC-40, TC-42; deney planı §9 |
| 9–10 | B | Doğrulama kuyruğu, toplu onay, çelişki (K3), kural ön denetçisi; R3 LLM araştırması ve ADR | FR-11–16 | TC-29–34; `docs/research/...-llm-saglayici.md` |
| 11–12 | B | LLM ön denetçisi ve geri düşme; arayüzün bütünleştirilmesi (S3, S4) | FR-17, FR-18, FR-21 | TC-35–38, TC-41 |
| 11–12 | A | Model sürümü ekranının arka ucu, AS2 raporunun altyapısı | FR-21, FR-30 | TC-41, TC-44 |
| 13–14 | A | AS1 ızgarası, AS2 raporu, hata analizi | FR-29, FR-30 | TC-43, TC-44; sonuç tablosu |
| 13–14 | B | Çalışma modu (FR-31–34), vaka seçimi ve eşleştirme, pilot | FR-31–34 | TC-45–48; pilot notu |
| 15–16 | B (A destek) | İnsan çalışması oturumları, ölçekler, AS3 analizi | AS3 | Katılımcı verisi (anonim), analiz defteri |
| 15–16 | A + B | Normal kullanım, boş/geçersiz girdi, yetki, servis kesintisi, kaynak yetersizliği kontrolleri (s.2) | NFR'ler | Test raporu |
| 17–18 | A + B | Temiz kurulum, rapor, demo ve yedek video | NFR-14 | TC-49; teslim listesi (s.18) |

## 3. Haftalık ilerleme notu (s.18)

Her hafta `docs/haftalik/YYYY-Www.md` dosyasına iki kişi birlikte yazar:

```
# Hafta NN (tarih aralığı)
1. Ne tamamlandı?
2. Hangi kanıt üretildi? (test, ölçüm, belge bağlantısı)
3. Ne engelliyor?
4. Gelecek hafta ne teslim edilecek?
5. Kim sorumlu?
```

## 4. Danışman görüşmeleri

İki haftada bir görüşme yapılır. Gündem belgesi görüşmeden önce hazırlanır. Görüşmede hocanın cevabı belgeye yazılır, değişen kararlar ADR olarak kaydedilir. İlk görüşme 2026-11-03'te.
