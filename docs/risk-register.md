# Risk kaydı: Açıklanabilir SOC Karar Destek Arayüzü

- **Güncelleme:** 2026-11-02

Görüşme belgesinin "Belirsizlikler ve riskler" tablosu (rev 43) ile tasarımda ortaya çıkan teknik riskleri birleştirir. Olasılık ve etki üç düzeylidir. Sıralama önem derecesine göredir.

| ID | Risk | Olasılık | Etki | Tetik / erken uyarı | Azaltma | Durum |
|---|---|---|---|---|---|---|
| R-01 | GUIDE'da uyarı başlığı ve varlık alanları sayısal kimlik. Vaka kartı yalnız yapılandırılmış alanlarla kurulur ve karar vermeye yetmeyebilir (K2) | Orta | Yüksek | Demo ya da pilotta katılımcılar kartla karar veremiyor; iki ekip üyesinin doğru cevapta uyuşmadığı kart oranı yüksek (m13) | Kart okunur alanlar ve tutarlı takma adlarla kurulur. Yetersiz kalırsa K2 yeniden açılır; B planı okunabilir sentetik veri ve onunla eğitilen model | Açık |
| R-02 | Okunur alanlarla taban modelin macro-F1 değeri düşük kalır (ADR-0005) | Orta | Orta | E1'de macro-F1 < rastgele + 0,10 | Sonuç raporlanır. E2'de LightGBM ve kimlik alanı ablasyonu yapılır. Doğruluk–açıklanabilirlik farkı bir bulgu olarak sunulur | Açık |
| R-03 | Simüle hatalı geri bildirime gerekçe metni de gerekir. LLM ve kural işaretleyicisi yapay metinle sınanır | Yüksek | Orta | — | Gerekçe üretimi varsayım olarak raporlanır; bir kısmı insan katılımcıların gerçek gerekçeleriyle sınanır | Açık |
| R-04 | GUIDE etiketleri müşteri beyanı ve gürültülü; BP için tanım yok | Yüksek | Orta | — | Sınırlılık olarak yazılır. Belirsiz etiketler testten çıkarılmaz (Arp vd.). Sürümler aynı kilitli testte karşılaştırılır | Açık |
| R-05 | Etik kurul onayı haftalar sürebilir; insan çalışması 15–16. haftaya yetişmeyebilir | Orta | Yüksek | Hocanın cevabı (görüşme sorusu 1) | Başvuru erken yapılır. Onay gecikirse simülasyon deneyi ve arayüz demosu sunulur | Açık |
| R-06 | LLM servisi erişilemez ya da maliyetli | Orta | Orta | R3 araştırması (9–10. hafta) | Kural tabanlı işaretleyiciye düşülür (FR-18). Giden veri ve maliyet belgelenir. Sağlayıcı R3 ile seçilir | Açık |
| R-07 | Uyarı alanlarına ya da gerekçeye gömülü talimat (prompt injection) | Orta | Orta | TC-38 | LLM onay vermez, etiket üretmez. Alanlar talimattan ayrı verilir. Şema dışı çıktı geri düşmeye gider (NFR-09) | Açık |
| R-08 | Simülasyon varsayımları (gürültü türü, doğrulayıcının doğruluğu) sonucu belirler | Orta | Orta | — | Varsayımlar parametre yapılır ve birden fazla düzeyle raporlanır (deney planı §6) | Açık |
| R-09 | `LastVerdict` triyaj sonrası bir hüküm olabilir ve etiketi sızdırabilir | Orta | Orta | E2'de "− LastVerdict" ablasyonunda büyük düşüş | Ablasyonla ölçülür. Sızıntı kanıtlanırsa özellik çıkarılır ve ADR-0005 güncellenir | Açık |
| R-10 | Katılımcı sayısı az olabilir | Orta | Orta | Duyuru sonrası kayıt sayısı | Sonuçlar keşifsel; etki büyüklüğü ve güven aralığı | Açık |
| R-11 | AS1 ızgarası hesaplama bütçesini aşar (NFR-04) | Düşük | Orta | Tek eğitim > 10 dk | Önce e düzeyleri azaltılır, sonra T2'den örneklem alınır; raporlanır | Açık |
| R-12 | Zaman damgalarına gürültü eklenmiş; zaman sıralı bölme yaklaşık | Yüksek | Düşük | — | Sınırlılık olarak yazılır; olay zamanı ilk uyarı zamanı | Açık |
| R-13 | Jian güven ölçeğinin doğrulanmış Türkçe uyarlaması olmayabilir | Orta | Düşük | Literatür taraması | Çeviri–geri çeviri; sınırlılık | Açık |
| R-14 | Demo kimliği (`X-User`) güvenli değil | Yüksek | Düşük | — | Yalnız 127.0.0.1'e bağlanır. 7–8. haftada yerel hesap ve oturum gelir (FR-24) | Açık |
| R-15 | Python 3.11 ile güncel shap ve xgboost sürümleri uyumsuz | Gerçekleşti | Düşük | R2 kontrolü | ADR-0003: shap kullanılmaz; LightGBM'in yerleşik TreeSHAP'i ve doğrusal kapalı form kullanılır | Kapandı |
| R-16 | İki paket (A/B) arasında entegrasyon uyumsuzluğu | Orta | Orta | API sözleşmesi dışında çağrı | `docs/architecture.md` §6 sözleşmesi; çekirdek fonksiyon imzaları; çapraz kod incelemesi | Açık |
