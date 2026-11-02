# ADR-0005: Taban model ve demo yalnız okunur alanlardan türetilen özelliklerle; kimlik alanları ana modelde ablasyonla sınanır

- **Durum:** Kabul edildi (2026-11-02)
- **Kaynak:** Kullanıcının faz 3 seçimi.

## Bağlam

- FR-05: SHAP katkısı ham alana bağlı olmalı.
- K2: vaka kartı GUIDE'ın okunur alanlarıyla kurulur.
- Veri denetimi: `AlertTitle`, `DetectorId`, `OrgId` ve bütün varlık alanları anonim sayısal kimlik. Bunlar büyük olasılıkla güçlü tahmin ediciler, ama analist için anlamsız.
- Bazı alanlar triyajdan sonra oluşur ve etiketi sızdırabilir: `ActionGrouped` ve `ActionGranular` (müdahale eylemi, GUIDE'ın müdahale görevinin etiketi).

## Değerlendirilen seçenekler

1. **Yalnız okunur alanlar; kimlikler 9–10. haftada ablasyonla** (seçildi): SHAP satırları kartta görünen alanlara bağlanır. Doğruluk kimlik alanları kullanan çözümlerden düşük kalabilir.
2. **Kimlik alanları da dahil:** Daha yüksek macro-F1 beklenir. Ancak SHAP'te opak satırlar çıkar ve kartla uyumsuz olur.

## Karar

- Taban modelde ve demoda yalnız şu alanlardan türetilen olay düzeyi özellikler kullanılır:
  - `Category`
  - `MitreTechniques`
  - `EntityType`
  - `EvidenceRole`
  - `SuspicionLevel`
  - `LastVerdict`
  - `Roles`
  - `ResourceType`
  - `ThreatFamily` (dolu mu)
  - Sayımlar: uyarı, kanıt satırı, farklı varlık türü, farklı teknik
- Özellik listesi ve kodlaması `docs/data-design.md` §9'da tanımlıdır.
- `ActionGrouped` ve `ActionGranular` sızıntı riski yüzünden hiçbir modelde kullanılmaz.
- Kimlik alanları (`DetectorId`, `AlertTitle`, `OrgId`; yalnız T1'den öğrenilen hedef kodlamayla) ana modelde ekli ve eksik olarak karşılaştırılır (`docs/experiments/2026-11-02-temel-model-ve-as1.md`, ablasyon). Ana modelin hangi özellik setiyle arayüze çıkacağına bu sonuca göre karar verilir. Sonuç ve doğruluk–açıklanabilirlik farkı rapora girer.
- `LastVerdict` otomatik incelemenin hükmüdür ve olası bir sızıntı kaynağıdır. Taban modelde kalır, ama ablasyonda çıkarılarak da ölçülür.

## Sonuçlar

- **Olumlu:** Açıklama analistin gördüğü kanıtla birebir. Sızıntılı alanlar baştan dışarıda.
- **Olumsuz / riskler:** Taban modelin macro-F1 değeri düşük kalabilir. Bu bir sonuç olarak raporlanır ve ablasyon farkı açıklanır.

## İzlenebilirlik

- **Gereksinim:** FR-02, FR-05, FR-27, FR-28
- **Bağlantılı:** ADR-0003, ADR-0004
