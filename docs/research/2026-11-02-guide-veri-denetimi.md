# GUIDE veri denetimi (2026-11-02)

**Kaynak:** Kaggle, `Microsoft/microsoft-security-incident-prediction`, Version 2 (Kaggle'da "Updated 3 months ago"), zip 513 MB. Dosyalar `data/raw/guide/` altında; ham dosyalar değiştirilmez.
**Lisans:** CDLA-Permissive-2.0 (veri kartında belirtilmiş). Atıf: Freitas vd., *WWW Companion 2025*, s. 191–200, doi:10.1145/3701716.3715209. Sıralama etiketleri kullanılırsa ek atıf: Freitas, Gharib, Magenheim, *Adaptive Incident Prioritization…*, arXiv 2026.
**Yöntem:** DuckDB ile CSV'ler belleğe alınmadan tarandı. Betikler oturumun scratchpad klasöründe (`audit_guide.py`, `audit_incident.py`); proje iskeleti kurulunca `scripts/` altına taşınacak.

## Dosyalar

| Dosya | Boyut | Satır | Not |
|---|---|---|---|
| GUIDE_Train.csv | 2,43 GB | 9.516.837 | 46 sütun, kanıt (evidence) düzeyinde satır |
| GUIDE_Test.csv | 1,09 GB | 4.147.992 | + `Usage` sütunu (Public/Private) |
| GUIDE_Test_Queue_Rankings.csv | <1 MB | 9.980 | **Yeni (2026):** `OrgId, IncidentId, QueueRank`; 499 kurum kuyruğu, kuyruk başına ilk 20 |

## Bulgular

1. **Okunabilirlik (önceki "doğrulanmadı" maddesi kapandı).** `AlertTitle` metin değil, **anonim sayısal kimlik** (≈84.760 farklı değer). Hesap/cihaz/IP/dosya/URL/ülke/şehir alanlarının hepsi sayısal kimlik; her birinde tek bir değer satırların %70–99'unu kaplıyor (büyük olasılıkla "yok" anlamına gelen nöbetçi değer).
   Okunur metin olan alanlar: `Category` (20), `MitreTechniques` (1.107 kombinasyon; olayların %35'inde dolu; T-kodları MITRE adlarına çevrilebilir), `EntityType` (33), `EvidenceRole` (Impacted/Related), `SuspicionLevel`, `LastVerdict`, `Roles`, `ResourceType`, `ThreatFamily` (%0,8 dolu), `ActionGrouped/ActionGranular` (%0,6 dolu). `AntispamDirection` ve `LastVerdict` içinde `DomainPII_<hash>` değerleri de var (anonimleştirme artığı).
2. **Etiket olay düzeyinde tutarlı.** Eğitimde 730.778 olay (`OrgId+IncidentId`) var, hiçbirinde birden fazla `IncidentGrade` yok. Olay düzeyinde dağılım: BP %47,4, FP %29,4, TP %19,9, etiketsiz %3,2 (uyarı satırı düzeyinde TP %35; TP olaylar daha çok satır üretiyor). Etiketsiz satırlar (%0,5) eğitimden çıkarılır.
3. **Resmî bölme olay bazlı, zamana göre değil.** Train–test arasında ortak olay da ortak `Id` de 0. Kurumlar ortak (4.054 kurum her iki tarafta da var). İki dosyanın zaman aralığı aynı.
4. **Zaman.** Satırların %98'i 2024-05-21 ile 2024-06-16 arasında (~26 gün; veri kartında "iki hafta" yazıyor). 2023-11'e uzanan ince bir kuyruk da var. Dosya zamana göre sıralı değil (ardışık adımların %50'si geriye gidiyor), bu yüzden zaman sıralı bölme için önce sıralama gerekir.
5. **En sık 3 kategori:** olay düzeyinde InitialAccess (293.837), SuspiciousActivity (141.455), Exfiltration (91.926). Uyarı düzeyinde de aynı üçlü çıkıyor. Olayların %97,8'i tek kategorili.

   | Kategori | TP | BP | FP |
   |---|---|---|---|
   | InitialAccess | 22,8% | 34,6% | 42,6% |
   | SuspiciousActivity | 33,0% | 51,1% | 15,9% |
   | Exfiltration | 6,0% | 66,9% | 27,1% |
6. **Olay büyüklüğü.** Olay başına uyarı sayısı: medyan 1, %90'lık dilim 2, %99'luk dilim 9, en fazla 5.371. Olay başına kanıt satırı: medyan 4, %90'lık dilim 14, %99'luk dilim 116.
7. **Bellek.** pandas varsayılan tiplerle tüm Train için ~3,9 GB gerekir (16 GB RAM, ~7 GB boş). Kategorik tiplerle ya da DuckDB/Parquet ile rahat sığar.
8. **Görevler.** Veri seti artık üç görevi destekliyor: triage (TP/BP/FP, önerilen ölçüt macro-F1), müdahale önerisi (~26 bin olay) ve 2026'da eklenen kuyruk önceliklendirme (Precision@5/10/20).

## Projeye etkisi (karar kullanıcıda)

- **İnsan çalışmasındaki vaka gösterimi:** başlık metni yok. Bir vaka şu bilgilerle gösterilebilir: kategori, MITRE teknik adları, varlık türleri ve rolleri, şüphe ve hüküm alanları, uyarı ve kanıt sayıları. Bu bilgi analistin değerlendirmesi için yeterli mi, yoksa B planı (okunabilir sentetik veri) mı devreye girmeli? Açık karar.
- **LLM ön denetçisi:** LLM'e de aynı yapılandırılmış alanlar verilebilir. Serbest metin olmadığı için LLM'in katkısı açıklamayı okunur hâle getirmekle sınırlı kalır.
- **Bölme kararı:** zaman sıralı bölme uygulanabilir ama zaman damgalarına gürültü eklenmiş ve dosya sırasız. Olay zamanı olarak olayın ilk uyarısının zamanı alınabilir.

## Açık sorular

- `Id` alanındaki farklı değer sayısı yaklaşık 923 bin, olay sayısı ise 730 bin (yaklaşık sayımla). Veri kartı `Id` için "OrgId-IncidentId çifti başına tekil" diyor; bu tutarsızlık kesin sayımla doğrulanmadı.
- Nöbetçi değer varsayımı (örn. `DeviceId=98799`) veri kartında belgelenmemiş; çıkarım.
