# Yazılım Gereksinim Belirtimi (SRS-lite): Açıklanabilir SOC Karar Destek Arayüzü

- **Güncelleme:** 2026-11-02
- **Durum:** Onaylandı (2026-11-02)
- **İlgili dokümanlar:** `docs/plans/2026-11-02-hafta-1-5-ciktilari-ve-demo.md`, `docs/research/2026-11-02-guide-veri-denetimi.md`, `docs/research/2026-11-02-soc-sistemleri.md`, yol haritası (`SistemTasarimi_Yol_Haritasi.pdf` s.2-3, s.10, s.18), konu tanımı (`proje_hakkında.txt`), görüşme belgesi (Claude Docs, rev 43)

Bu belgenin 1. bölümü yol haritası Adım 1.1'deki tek sayfalık problem tanımıdır; 3–6. bölümler Adım 1.2'deki kullanıcı hikâyeleri, gereksinimler ve kabul testleridir; 7. bölüm Adım 1.3'ün veri ve araç kaydıdır.

## 1. Problem, hedef kullanıcı ve sınırlar

**Resmî başlık:** İnsan-Yapay Zekâ İşbirliğine Dayalı Açıklanabilir SOC Karar Destek Arayüzü (Grup 7: Ali İhsan Dağaşan, Mehmet Emin Duran; danışman Prof. Dr. İbrahim Arpacı).

**Problem.** Güvenlik operasyon merkezinde (SOC) analist, bir olayın gerçek tehdit mi, zararsız-beklenen bir etkinlik mi, yoksa yanlış alarm mı olduğuna karar verir. Bir sınıflandırma modeli bu kararı önerebilir. Ancak analist modelin güven skorunu ve gerekçesini göremezse öneriyi doğru değerlendiremez: yanlış öneriyi kabul eder (aşırı güven) ya da doğru öneriyi reddeder (eksik güven). İkinci sorun geri bildirimdir. Analistin düzeltmesi hatalı ya da başka bir analistinkiyle çelişkili olabilir. Bu düzeltme doğrudan eğitime girerse model bozulur. Her kaydı kıdemli bir analistin incelemesi de doğrulamayı darboğaza çevirir. Ayrıca kimin neyi neden değiştirdiği kaydedilmezse denetim izi kaybolur.

**Çözüm.** Microsoft GUIDE verisi üzerinde kendi eğittiğimiz model her olay için bir sınıf ve güven skoru önerir. Öneri, ham kayıttaki alanlara bağlı SHAP katkılarıyla açıklanır. Analist öneriyi kabul eder, düzeltir (doğru sınıf + gerekçe) ya da reddeder (inceleme gerekli). Her karar, silinmeyen bir denetim izine sürümlü olarak yazılır. Ardından bir ön denetçi (kural tabanlı ya da LLM) tutarsız geri bildirimi işaretler. Kıdemli analist işaretli kayıtları tek tek inceler, işaretsizleri toplu onaylar. Yalnız onaylanan kayıtlar ayrı bir eğitim etiketi deposuna geçer. Model çevrim dışı, sürümlü ve elle tetiklenerek yeniden eğitilir. Yeni sürüm, kilitli bir test kümesinde öncekiyle karşılaştırılır.

**Hedef kullanıcı.** SOC'de Kademe 1 analisti (karar verir), Kademe 2/3 kıdemli analisti (doğrular, çelişki çözer) ve güvenlik mühendisi karşılığı model sorumlusu (yeniden eğitimi yönetir). Araştırma ve insan çalışması için: siber güvenlik dersi almış bilgisayar mühendisliği öğrencileri (hedef 12–18). Ulaşılabilen SOC analistleri ayrı alt grup olarak raporlanır.

**Araştırma soruları.** AS1 (ana): %0/10/20/30 hatalı geri bildirim altında dört doğrulama düzeni (doğrulama yok; kıdemli her kaydı inceler; kural işaretler + kıdemli; LLM işaretler + kıdemli) yeniden eğitilen modeli kilitli testte ne kadar korur ve kıdemliye ne kadar iş bırakır? AS2: Model ile analist hangi olay kategorilerinde, ne sıklıkla uyuşmuyor? Karar süresi ne kadar? AS3 (konu tanımının sorusu): Yalnız insan / AI önerisi / AI önerisi + açıklama koşullarında karar doğruluğu, süresi, kullanılabilirlik ve güven kalibrasyonu nasıl değişiyor?

- **Kapsam içi:**
  - En sık üç olay kategorisi: InitialAccess, SuspiciousActivity, Exfiltration.
  - Üç sınıflı olay kararı: Gerçek tehdit (TP), Zararsız-beklenen (BP), Yanlış alarm (FP).
  - Olay inceleme ve geri bildirim arayüzü.
  - Denetim izi ve eğitim etiketi deposu.
  - Kural ve LLM ön denetçisi.
  - Çevrim dışı sürümlü yeniden eğitim ve sürüm karşılaştırması.
  - AS1 simülasyonu, AS2 raporu ve AS3 insan çalışması modu.
- **Kapsam dışı:**
  - Öncelik ve müdahale (aksiyon) kararı.
  - Otomatik müdahale ya da herhangi bir dış sisteme eylem gönderme.
  - Gerçek SIEM/XDR entegrasyonu ve canlı veri akışı.
  - Çevrimiçi (sürekli) öğrenme.
  - GUIDE'ın müdahale önerisi ve kuyruk önceliklendirme görevleri.
  - Üç kategori dışındaki olaylar.

## 2. Paydaşlar ve aktörler

| Aktör | Rolü | Temel hedefi |
|---|---|---|
| Analist (Kademe 1) | Olayı inceler, öneriyi kabul eder, düzeltir ya da reddeder | Doğru kararı hızlı ve gerekçeli vermek |
| Kıdemli analist (Kademe 2/3) | Geri bildirimi doğrular, çelişkileri çözer | Eğitime yalnız doğru etiketlerin girmesi, iş yükünün yönetilebilir kalması |
| Model sorumlusu | Yeniden eğitimi tetikler, sürümleri karşılaştırır, etkin sürümü seçer; etiket değiştiremez | Modelin geri bildirimle iyileştiğini kanıtla göstermek |
| Katılımcı (insan çalışması) | Çalışma modunda vaka kartlarına karar verir | — |
| Araştırmacı (ekip) | AS1 simülasyonunu ve insan çalışmasını yürütür | Tekrarlanabilir, ölçülmüş sonuç |
| Danışman | Projeyi değerlendirir | Yol haritasındaki kabul kanıtları |
| LLM servisi (dış sistem) | Ön denetçi olarak kaydı işaretler | — |

## 3. Kullanıcı hikâyeleri

| ID | Hikâye | Gereksinimler |
|---|---|---|
| US-01 | Analist olarak bekleyen olayları bir kuyrukta görmek istiyorum; böylece sırayla inceleyebilirim. | FR-01 |
| US-02 | Analist olarak bir olayın kategorisini, MITRE tekniklerini, varlıklarını ve uyarılarını görmek istiyorum; böylece kanıta bakarak karar verebilirim. | FR-02 |
| US-03 | Analist olarak modelin önerisini, güven skorunu ve SHAP gerekçesini görmek istiyorum; böylece öneriye ne kadar güveneceğimi bilirim. | FR-03, FR-04, FR-05 |
| US-04 | Analist olarak öneriyi kabul etmek, gerekçeyle düzeltmek ya da reddetmek istiyorum; böylece kararım kayda geçer. | FR-06, FR-07, FR-08 |
| US-05 | Analist olarak bir olaydaki önceki kararları ve gerekçelerini görmek istiyorum; böylece kararın neden değiştiğini izleyebilirim. | FR-09, FR-10 |
| US-06 | Kıdemli analist olarak yalnız işaretli kayıtları tek tek incelemek, işaretsizleri toplu onaylamak istiyorum; böylece her kaydı okumadan doğrulayabilirim. | FR-13, FR-16, FR-17, FR-18 |
| US-07 | Kıdemli analist olarak çelişkili kararları görüp gerekçeyle çözmek istiyorum; böylece eğitime tutarlı etiket girer. | FR-11, FR-12, FR-14 |
| US-08 | Model sorumlusu olarak yalnız onaylı etiketlerle yeni sürüm eğitip kilitli testte öncekiyle karşılaştırmak istiyorum; böylece geri bildirimin etkisini kanıtlarım. | FR-15, FR-19, FR-20, FR-21, FR-22 |
| US-09 | Her rol olarak yalnız rolümün izin verdiği işlemleri yapabilmek istiyorum; böylece görev ayrılığı korunur. | FR-23, FR-24 |
| US-10 | Araştırmacı olarak hatalı geri bildirim oranı ve doğrulama düzeni parametreleriyle simülasyon koşturmak istiyorum; böylece AS1'i cevaplarım. | FR-26, FR-27, FR-28, FR-29 |
| US-11 | Araştırmacı olarak model–analist uyuşmazlığını ve karar süresini kategori bazında raporlamak istiyorum; böylece AS2'yi cevaplarım. | FR-30 |
| US-12 | Araştırmacı olarak katılımcıya üç koşulu dengeli sırayla göstermek ve sonuçları anonim kaydetmek istiyorum; böylece AS3'ü cevaplarım. | FR-31, FR-32, FR-33, FR-34 |

## 4. İşlevsel gereksinimler

Öncelik: MoSCoW. **Hafta:** yol haritasındaki hedef hafta (5–6 iskelet ve karşılaştırma modeli; 7–8 MVP; 9–10 ana model ve karar mantığı; 11–12 açıklama, raporlama, arayüz bütünleştirme; 13–14 deneyler; 15–16 entegrasyon ve insan çalışması). **Demo:** ✓ olanlar 2026-11-03 demosunda çalışır; "kısmi" olanlarda kısıt nottadır.

### 4.1 Olay inceleme ve öneri

| ID | Gereksinim | Öncelik | Kaynak | Hafta | Demo | Kabul |
|---|---|---|---|---|---|---|
| FR-01 | Sistem, kapsamdaki üç kategorideki olayları, kararı bekleyenler önde olacak biçimde bir kuyrukta listelemeli. | Must | s.10 Adım 3 ("uyarı inceleme"); Kayıt türü kararı | 7–8 | kısmi: demo havuzunun basit listesi | AC-01 |
| FR-02 | Sistem, seçilen olay için kategoriyi, MITRE teknik kodlarını ve adlarını, varlık türlerini ve rollerini, şüphe ve hüküm alanlarını, uyarı sayısını ve olayın uyarılarını kanıt listesi olarak göstermeli; anonim sayısal kimlikleri tutarlı takma adla ("Kullanıcı-17") göstermeli. | Must | Karar birimi kararı; K2 | 5 | ✓ | AC-02 |
| FR-03 | Sistem, her olay için modelin önerdiği sınıfı (Gerçek tehdit / Zararsız-beklenen / Yanlış alarm), güven skorunu ve öneriyi üreten model sürümünü göstermeli. | Must | s.10 Hedef; s.3 | 5 | ✓ | AC-03 |
| FR-04 | Sistem, güven skoru deney planında gerekçelendirilen eşiğin altında kalan öneriyi "inceleme gerekli" olarak işaretlemeli. | Must | s.3 ("model belirsizliğinde inceleme gerekli") | 5 | ✓ | AC-04 |
| FR-05 | Sistem, öneriyi SHAP özellik katkılarıyla açıklamalı; her katkı, ham kayıttaki alan adına ve o olaydaki değerine bağlı olmalı ve katkıya göre sıralı gösterilmeli. | Must | s.3 ("açıklamayı kanıtla ilişkilendirin"); Açıklama kararı | 5 | ✓ | AC-05 |

### 4.2 Karar ve geri bildirim

| ID | Gereksinim | Öncelik | Kaynak | Hafta | Demo | Kabul |
|---|---|---|---|---|---|---|
| FR-06 | Analist öneriyi kabul edebilmeli; etkin karar önerilen sınıf olur. | Must | s.10 Hedef | 5 | ✓ | AC-06 |
| FR-07 | Analist öneriyi düzeltebilmeli; doğru sınıf ve boş olmayan gerekçe zorunludur, önerilen sınıfla aynı sınıf "düzeltme" olarak kabul edilmez. | Must | s.10 MVP; Analistin kararları | 5 | ✓ | AC-07 |
| FR-08 | Analist öneriyi reddedebilmeli; boş olmayan gerekçe zorunludur ve olay "inceleme gerekli" durumuna geçer. | Must | Analistin kararları ("Ret → inceleme gerekli"); kullanıcı kararı 2026-11-02 (gerekçe zorunlu) | 5 | ✓ | AC-08 |
| FR-09 | Sistem her kararı yalnız eklenebilen denetim izine şu alanlarla yazmalı: olay kimliği, model önerisi (sınıf + güven skoru), karar türü, karar sınıfı, gerekçe, karar zamanı, olayın açıldığı zaman, karar verenin rolü ve takma kimliği, model sürümü, veri sürümü. | Must | s.10 Adım 2-3, Kabul; m3 | 5 | ✓ | AC-09 |
| FR-10 | Sistem olay başına tek etkin karar tutmalı; yeni karar öncekini sürümlemeli ve önceki kararlar sürüm, zaman, rol ve gerekçeyle olay ekranında görünmeli. | Must | s.10 MVP ("önceki karar görülebilir"); K3 | 5 | ✓ | AC-10 |
| FR-11 | Bir olay için etkin kararla aynı sınıfta verilen tekrar karar denetim izine eklenmeli, ancak yeni karar sürümü ve yeni doğrulama işi oluşturmamalı. | Must | s.10 Adım 4 ("tekrarlı geri bildirim"); K3 | 9–10 | — | AC-11 |
| FR-12 | Farklı analistlerin aynı olay için farklı sınıfta verdiği kararlar "çelişkili" olarak işaretlenmeli ve kıdemli analistin kuyruğuna düşmeli. | Must | s.10 Adım 4 ("çelişkili geri bildirim"); K3 | 9–10 | — | AC-12 |

### 4.3 Doğrulama ve ön denetim

| ID | Gereksinim | Öncelik | Kaynak | Hafta | Demo | Kabul |
|---|---|---|---|---|---|---|
| FR-13 | Kıdemli analist doğrulama kuyruğunda işaretli kayıtları tek tek onaylayabilmeli ya da reddedebilmeli, işaretsiz kayıtları tek işlemle toplu onaylayabilmeli; her doğrulama kararı denetim izine yazılmalı. | Must | İşaretsiz geri bildirim kararı | 9–10 | — | AC-13 |
| FR-14 | Kıdemli analist çelişkili bir olayı sınıf seçip gerekçe yazarak çözebilmeli. | Must | K3; m14 | 9–10 | — | AC-14 |
| FR-15 | Eğitim etiketi deposuna yalnız kıdemli analistin onayladığı kayıtlar girmeli; bu depo denetim izinden ayrı tutulmalı ve her etiket hangi denetim kaydından geldiğini göstermeli. | Must | s.10 Adım 2-3, Kabul; K5 | 9–10 | — | AC-15 |
| FR-16 | Kural tabanlı ön denetçi, düzeltmenin sınıfı, gerekçesi ve kanıt (öneri, güven skoru, SHAP katkıları, olay alanları) birbiriyle tutarsızsa kaydı işaretlemeli ve işaret nedenini yazmalı. | Must | LLM rolü kararı (karşılaştırma tabanı) | 9–10 | — | AC-16 |
| FR-17 | LLM ön denetçisi aynı girdiyle kaydı işaretlemeli ve nedenini yazmalı; onay vermemeli, etiket üretmemeli. | Must | LLM rolü kararı; s.3 | 11–12 | — | AC-17 |
| FR-18 | LLM servisi yanıt vermezse, zaman aşımına uğrarsa ya da şemaya uymayan çıktı verirse sistem o kayıt için kural tabanlı ön denetçiye düşmeli ve bunu denetim izine yazmalı. | Must | s.3 ("servis yokken uygulanacak davranış") | 11–12 | — | AC-18 |

### 4.4 Model, yeniden eğitim ve sürüm

| ID | Gereksinim | Öncelik | Kaynak | Hafta | Demo | Kabul |
|---|---|---|---|---|---|---|
| FR-19 | Model sorumlusu yeniden eğitimi elle tetikleyebilmeli; eğitim çevrim dışı çalışmalı, yalnız GUIDE eğitim bölmesini ve eğitim etiketi deposunu kullanmalı ve yeni bir model sürümü üretmeli. | Must | s.10 Adım 3; Yeniden eğitim kararı | 9–10 | — | AC-19 |
| FR-20 | Sistem iki model sürümünü kilitli test kümesinde karşılaştırmalı; macro-F1, doğruluk, sınıf bazlı kesinlik, duyarlılık, F1 ve karışıklık matrisini raporlamalı. | Must | s.10 Adım 4; s.3; m1 | 9–10 | — | AC-20 |
| FR-21 | Model sorumlusu öneri üretecek etkin sürümü seçebilmeli; seçim denetim izine yazılmalı. | Should | K4 | 11–12 | — | AC-21 |
| FR-22 | Doğrulanmamış hiçbir kullanıcı girdisi modeli ya da eğitim etiketi deposunu otomatik değiştirmemeli. | Must | s.10 Kabul | 5 | ✓ | AC-22 |
| FR-23 | Sistem üç rolün izinlerini sunucu tarafında uygulamalı (izin matrisi: `docs/architecture.md`); model sorumlusu etiket ve karar değiştirememeli, analist doğrulama yapamamalı. | Must | K4; s.3; s.10 Adım 4 ("farklı rollerin erişimi") | 7–8 | kısmi: demoda yalnız analist işlemleri, hazır kullanıcılar | AC-23 |
| FR-24 | Kullanıcılar yerel hesapla (parola özetlenerek saklanır) giriş yapmalı; oturum süresi sınırlı olmalı. | Should | s.3 ("güvenli oturum yönetimi") | 7–8 | — (demoda hazır kullanıcı seçimi) | AC-24 |
| FR-25 | Sistem hiçbir dış sisteme müdahale ya da eylem göndermemeli; arayüz bunu açıkça belirtmeli. | Must | s.3; m9 | 5 | ✓ | AC-25 |

### 4.5 Veri hattı ve deneyler

| ID | Gereksinim | Öncelik | Kaynak | Hafta | Demo | Kabul |
|---|---|---|---|---|---|---|
| FR-26 | Veri hattı GUIDE_Train'i kapsamdaki üç kategoriye süzmeli, olay düzeyine indirgemeli, olay bazlı ve zaman sıralı dört dilime (T1 eğitim / T2 geri bildirim havuzu / doğrulama / kilitli test; ADR-0004) bölmeli ve her çıktıya veri sürümü vermeli; aynı olay iki dilimde bulunmamalı. | Must | s.2 Adım 2.3; s.3; Bölme kararı; m7 | 5 | ✓ | AC-26 |
| FR-27 | Basit bir karşılaştırma modeli eğitilmeli ve FR-20'deki ölçütlerle doğrulama kümesinde raporlanmalı. | Must | s.2 (5–6. hafta); s.3 | 5 | ✓ | AC-27 |
| FR-28 | Ana sınıflandırıcı eğitilmeli ve karşılaştırma modeliyle aynı ölçütlerle, aynı kümelerde karşılaştırılmalı. | Must | s.2 (9–10. hafta); Model kararı | 9–10 | — | AC-28 |
| FR-29 | AS1 simülasyonu şu parametrelerle tek komutla koşturulabilmeli: hatalı geri bildirim oranı (%0/10/20/30), gürültü türü (rastgele / sistematik), doğrulama düzeni (dört düzen), doğrulayıcı hata oranı ve tohum. Çıktı olarak macro-F1, sızan hatalı etiket oranı, kıdemlinin tek tek incelediği kayıt oranı ve işaretleyici kesinlik/duyarlılığı tablosu üretilmeli. | Must | AS1; H1; H2; m11 | 13–14 | — | AC-29 |
| FR-30 | Sistem kategori bazında model–analist uyuşmazlık oranını ve karar süresi dağılımını (medyan, çeyrekler) denetim izinden raporlamalı. | Must | s.10 Adım 4; AS2 | 13–14 | — | AC-30 |

### 4.6 İnsan çalışması

| ID | Gereksinim | Öncelik | Kaynak | Hafta | Demo | Kabul |
|---|---|---|---|---|---|---|
| FR-31 | Çalışma modu her katılımcıya üç koşulu (yalnız insan / AI önerisi / AI önerisi + açıklama) dengelenmiş sırayla sunmalı; koşula göre öneri ve açıklama gizlenmeli; vakalar koşullar arasında zorlukça eşleştirilmiş kümelerden gelmeli. | Must | Konu tanımı; İnsan çalışması kararı | 15–16 | — | AC-31 |
| FR-32 | Çalışma modu her vaka için karar, süre, koşul ve modelin önerisinin doğru olup olmadığını katılımcı deposuna anonim kodla yazmalı; aşırı güven (AI yanlışken kabul) ve eksik güven (AI doğruyken ret) oranları buradan hesaplanmalı. | Must | AS3; m12; K5 | 15–16 | — | AC-32 |
| FR-33 | Katılımcı verisi anonim koduyla istenince silinebilmeli; denetim izinde katılımcı kimliği bulunmamalı. | Must | K5 | 15–16 | — | AC-33 |
| FR-34 | Alıştırma modu, TP/BP/FP tanımlarını ve örneklerini içeren sentetik kartlarla çalışmalı; alıştırma sonuçları ölçüme katılmamalı. | Should | m13; K2 | 15–16 | — | AC-34 |

## 5. İşlevsel olmayan gereksinimler

Ölçümle kesinleşecek hedefler "ilk hedef" olarak yazıldı. Yol haritası (s.3) gereği hedef sonuç görüldükten sonra değişirse önceki hedef ve değişiklik nedeni korunur.

| ID | Nitelik | Gereksinim | Ölçüt | Hedef |
|---|---|---|---|---|
| NFR-01 | Performans verimliliği | Olay ayrıntısı, öneri ve SHAP açıklaması hızlı açılmalı | Olay açma isteği yanıt süresi, 100 olay, p95 | ≤ 2 s (16 GB RAM dizüstü, GPU yok) |
| NFR-02 | Performans verimliliği | Karar kaydı hızlı yazılmalı | Karar kaydetme isteği, p95 | ≤ 500 ms |
| NFR-03 | Performans verimliliği (kaynak) | Veri hattı ve eğitim dizüstüne sığmalı | Tepe bellek kullanımı | ≤ 6 GB (denetimde boş bellek ~7 GB) |
| NFR-04 | Performans verimliliği (kaynak) | Yeniden eğitim AS1 ızgarasını mümkün kılmalı | Tek eğitim süresi; AS1 tüm ızgara süresi | İlk hedef: ≤ 10 dk; ≤ 12 saat. Donanım ihtiyacı ilk ölçümden sonra kesinleşir |
| NFR-05 | Güvenlik | Rol izinleri sunucuda uygulanmalı | İzin matrisindeki her (rol, işlem) çifti için test; yetkisiz istek reddi | %100 geçer; yetkisiz istek 403 döner ve kaydedilir |
| NFR-06 | Güvenlik | Denetim izi değiştirilemez olmalı | Güncelleme ve silme girişimi testleri | Tümü reddedilir |
| NFR-07 | Güvenlik | Gizli anahtar ve parola kaynak kodda olmamalı | Depoda gizli bilgi taraması | 0 bulgu; anahtarlar ortam değişkeninde |
| NFR-08 | Güvenlik (gizlilik) | LLM'e yalnız yapılandırılmış olay alanları, öneri, SHAP katkıları ve gerekçe gitmeli; katılımcı ya da kullanıcı kimliği gitmemeli | Giden istek içeriği testi; belgelenmiş alan listesi | Listede olmayan alan 0 |
| NFR-09 | Güvenlik | Olay alanlarına ya da gerekçeye gömülü talimat (prompt injection) ön denetçinin davranışını değiştirmemeli | Enjeksiyon içeren test kayıtları | LLM çıktısı yalnız şemaya uyarsa kullanılır; aksi FR-18'e düşer |
| NFR-10 | Etkileşim yeteneği | Arayüz kullanılabilir olmalı | İnsan çalışmasında SUS ortalaması | ≥ 68 |
| NFR-11 | Etkileşim yeteneği | Alıştırmadan sonra karar akışı yardımsız tamamlanmalı | Yardımsız tamamlanan ilk görev oranı | ≥ %90 |
| NFR-12 | Güvenilirlik | LLM servisi yokken sistem çalışmaya devam etmeli | Servis kapalıyken uçtan uca akış; geri düşme süresi | Akış tamamlanır; ≤ 10 s (LLM zaman aşımı) |
| NFR-13 | Bakım yapılabilirlik (tekrarlanabilirlik) | Her eğitim ve deney koşusu model sürümü, veri sürümü, bağımlılık sürümleri, tohum ve ayarlarla kaydedilmeli | Aynı ayarla iki koşu | Ölçütler aynı (tohum sabit) |
| NFR-14 | Bakım yapılabilirlik | Temiz ortamdan kurulum belgelenmeli | README ile temiz kurulum süresi | ≤ 30 dk (veri indirme hariç) |
| NFR-15 | İşlevsel uygunluk | Test kümesi model ya da eşik seçiminde kullanılmamalı | Kod incelemesi + kilitli test erişim kaydı | Kilitli test yalnız sürüm karşılaştırmasında okunur |

## 6. Kabul ölçütleri

### AC-01 (FR-01)

```gherkin
# language: tr
Senaryo: Kuyruk yalnız kapsamdaki olayları, bekleyenler önde listeler
  Diyelim ki veritabanında üç kategoride kararı bekleyen ve kararı verilmiş olaylar ile kapsam dışı bir kategoride bir olay var
  Eğer ki analist kuyruğu açarsa
  O zaman yalnız InitialAccess, SuspiciousActivity ve Exfiltration olayları listelenir
  Ve kararı bekleyen olaylar kararı verilmiş olayların önündedir
```

### AC-02 (FR-02)

```gherkin
# language: tr
Senaryo: Olay ayrıntısı okunur alanları ve tutarlı takma adları gösterir
  Diyelim ki iki uyarısı olan ve aynı AccountObjectId değerini iki kez içeren bir olay var
  Eğer ki analist olayı açarsa
  O zaman kategori, MITRE teknik kodları ve adları, varlık türleri ve rolleri, şüphe ve hüküm alanları ile uyarı sayısı 2 görünür
  Ve aynı AccountObjectId iki yerde de aynı takma adla ("Kullanıcı-N") gösterilir
```

### AC-03 (FR-03)

```gherkin
# language: tr
Senaryo: Öneri sınıf, güven skoru ve model sürümüyle görünür
  Diyelim ki etkin model sürümü v1
  Eğer ki analist bir olayı açarsa
  O zaman üç sınıftan biri, 0 ile 1 arasında bir güven skoru ve "v1" görünür
```

### AC-04 (FR-04)

```gherkin
# language: tr
Senaryo: Düşük güvenli öneri "inceleme gerekli" işaretlenir
  Diyelim ki eşik 0,60 ve bir olayın en yüksek sınıf olasılığı 0,45
  Eğer ki analist olayı açarsa
  O zaman öneri "inceleme gerekli" işaretiyle gösterilir
Senaryo: Eşik üstündeki öneri işaretlenmez
  Diyelim ki eşik 0,60 ve bir olayın en yüksek sınıf olasılığı 0,85
  Eğer ki analist olayı açarsa
  O zaman öneri "inceleme gerekli" işareti taşımaz
```

(0,60 örnek değerdir; gerçek eşik deney planında gerekçelendirilir.)

### AC-05 (FR-05)

```gherkin
# language: tr
Senaryo: SHAP katkıları ham alanlara bağlıdır
  Diyelim ki model bir olay için öneri üretmiş
  Eğer ki analist açıklamayı görüntülerse
  O zaman her katkı satırında özellik adı, o olaydaki ham alan değeri ve katkı değeri bulunur
  Ve satırlar katkının mutlak değerine göre azalan sırada
  Ve taban değer ile katkıların toplamı modelin o sınıf için çıktısına eşittir (tolerans 1e-6)
```

### AC-06 (FR-06)

```gherkin
# language: tr
Senaryo: Kabul
  Diyelim ki öneri "Yanlış alarm" ve olayın etkin kararı yok
  Eğer ki analist öneriyi kabul ederse
  O zaman olayın etkin kararı "Yanlış alarm", karar türü "Kabul" ve sürüm 1 olur
```

### AC-07 (FR-07)

```gherkin
# language: tr
Senaryo: Gerekçeli düzeltme kaydedilir
  Diyelim ki öneri "Yanlış alarm"
  Eğer ki analist sınıfı "Gerçek tehdit" seçip gerekçe yazarak düzeltirse
  O zaman etkin karar "Gerçek tehdit" ve karar türü "Düzelt" olur
Senaryo: Gerekçesiz düzeltme reddedilir
  Diyelim ki öneri "Yanlış alarm"
  Eğer ki analist "Gerçek tehdit" seçip gerekçeyi boş bırakırsa
  O zaman kayıt yapılmaz ve gerekçenin zorunlu olduğu bildirilir
Senaryo: Önerilen sınıfa "düzeltme" yapılamaz
  Diyelim ki öneri "Yanlış alarm"
  Eğer ki analist düzeltmede yine "Yanlış alarm" seçerse
  O zaman kayıt yapılmaz ve bunun kabul işlemi olduğu bildirilir
```

### AC-08 (FR-08)

```gherkin
# language: tr
Senaryo: Ret olayı incelemeye gönderir
  Diyelim ki öneri "Zararsız-beklenen"
  Eğer ki analist öneriyi gerekçe yazarak reddederse
  O zaman olayın durumu "inceleme gerekli" olur ve karar türü "Ret" olarak kaydedilir
Senaryo: Gerekçesiz ret reddedilir
  Diyelim ki öneri "Zararsız-beklenen"
  Eğer ki analist gerekçeyi boş bırakarak reddederse
  O zaman kayıt yapılmaz ve gerekçenin zorunlu olduğu bildirilir
```

### AC-09 (FR-09)

```gherkin
# language: tr
Senaryo: Karar denetim izine tüm alanlarla eklenir
  Diyelim ki denetim izinde N kayıt var
  Eğer ki analist bir olay için düzeltme yaparsa
  O zaman denetim izinde N+1 kayıt olur
  Ve yeni kayıtta FR-09'daki alanların hepsi dolu
```

### AC-10 (FR-10)

```gherkin
# language: tr
Senaryo: Yeni karar öncekini sürümler, önceki görünür kalır
  Diyelim ki olayın etkin kararı "Kabul: Yanlış alarm" (sürüm 1)
  Eğer ki aynı olay için "Düzelt: Gerçek tehdit" gerekçeyle kaydedilirse
  O zaman etkin karar sürüm 2 "Gerçek tehdit" olur
  Ve olay ekranında sürüm 1 zamanı, rolü ve kararıyla geçmişte görünür
  Ve sürüm 1'in denetim kaydı değişmemiştir
```

### AC-11 (FR-11)

```gherkin
# language: tr
Senaryo: Aynı kararın tekrarı tekilleşir
  Diyelim ki olayın etkin kararı "Gerçek tehdit" (sürüm 2)
  Eğer ki başka bir analist de "Gerçek tehdit" kararı verirse
  O zaman denetim izine bir kayıt eklenir
  Ve etkin karar sürüm 2 olarak kalır
  Ve doğrulama kuyruğuna yeni iş eklenmez
```

### AC-12 (FR-12)

```gherkin
# language: tr
Senaryo: Farklı analistlerin çelişen kararları kıdemliye gider
  Diyelim ki analist A olay için "Yanlış alarm" kararı vermiş
  Eğer ki analist B aynı olay için "Gerçek tehdit" kararı verirse
  O zaman olay "çelişkili" işaretlenir
  Ve kıdemli analistin kuyruğunda görünür
```

### AC-13 (FR-13)

```gherkin
# language: tr
Senaryo: İşaretsizler toplu, işaretliler tek tek onaylanır
  Diyelim ki doğrulama kuyruğunda 3 işaretli ve 7 işaretsiz kayıt var
  Eğer ki kıdemli analist işaretsizleri toplu onaylarsa
  O zaman 7 kayıt onaylanır ve denetim izine 7 doğrulama kaydı eklenir
  Ve 3 işaretli kayıt tek tek karar bekler
```

### AC-14 (FR-14)

```gherkin
# language: tr
Senaryo: Çelişki gerekçeyle çözülür
  Diyelim ki "çelişkili" işaretli bir olay var
  Eğer ki kıdemli analist "Gerçek tehdit" seçip gerekçe yazarak çözerse
  O zaman olayın etkin kararı "Gerçek tehdit" olur ve "çelişkili" işareti kalkar
  Ve çözüm gerekçesi denetim izinde görünür
```

### AC-15 (FR-15)

```gherkin
# language: tr
Senaryo: Yalnız onaylı kayıt eğitim deposuna girer
  Diyelim ki bir düzeltme kaydı doğrulama bekliyor
  Eğer ki kıdemli analist kaydı reddederse
  O zaman eğitim etiketi deposunda o olay için etiket yoktur
  Ve kayıt denetim izinde "reddedildi" olarak kalır
Senaryo: Onaylı etiket kaynağını gösterir
  Diyelim ki kıdemli analist bir kaydı onaylamış
  O zaman eğitim etiketi deposundaki etiket, onaylanan denetim kaydının kimliğini taşır
```

### AC-16 (FR-16)

```gherkin
# language: tr
Senaryo: Kural işaretleyici tutarsız düzeltmeyi işaretler
  Diyelim ki model "Yanlış alarm" önermiş, güven skoru 0,95 ve en güçlü SHAP katkıları "Yanlış alarm" yönünde
  Eğer ki analist "Gerçek tehdit" düzeltmesini 10 karakterden kısa bir gerekçeyle kaydederse
  O zaman kayıt işaretlenir ve işaret nedeni yazılır
```

(Kural kümesi ve eşikleri tasarımda belirlenir; buradaki koşullar örnektir.)

### AC-17 (FR-17)

```gherkin
# language: tr
Senaryo: LLM işaretler ama onaylamaz
  Diyelim ki LLM ön denetçisi etkin
  Eğer ki bir düzeltme kaydı ön denetimden geçerse
  O zaman kayıt yalnız "işaretli" ya da "işaretsiz" durum ve bir neden alır
  Ve kayıt onaylanmış sayılmaz ve eğitim etiketi deposuna girmez
```

### AC-18 (FR-18)

```gherkin
# language: tr
Senaryo: LLM servisi yokken kurala düşülür
  Diyelim ki LLM servisi erişilemez
  Eğer ki bir düzeltme kaydı ön denetime gelirse
  O zaman kayıt kural tabanlı ön denetçiyle değerlendirilir
  Ve denetim izinde ön denetçi "kural (geri düşme)" olarak görünür
Senaryo: Şemaya uymayan LLM çıktısı kullanılmaz
  Diyelim ki LLM şemaya uymayan bir yanıt döndürüyor
  Eğer ki bir düzeltme kaydı ön denetime gelirse
  O zaman kayıt kural tabanlı ön denetçiyle değerlendirilir
```

### AC-19 (FR-19)

```gherkin
# language: tr
Senaryo: Elle tetiklenen eğitim yeni sürüm üretir
  Diyelim ki etkin sürüm v1 ve eğitim etiketi deposunda onaylı etiketler var
  Eğer ki model sorumlusu yeniden eğitimi tetiklerse
  O zaman v2 üretilir ve kaydında kullanılan veri sürümü ve etiket deposu anlık görüntüsü bulunur
  Ve v1 öneri üretmeye devam eder
```

### AC-20 (FR-20)

```gherkin
# language: tr
Senaryo: Sürümler kilitli testte karşılaştırılır
  Diyelim ki v1 ve v2 var
  Eğer ki model sorumlusu karşılaştırmayı başlatırsa
  O zaman iki sürüm için macro-F1, doğruluk, sınıf bazlı kesinlik, duyarlılık, F1 ve karışıklık matrisi aynı kilitli test kümesinde raporlanır
```

### AC-21 (FR-21)

```gherkin
# language: tr
Senaryo: Etkin sürüm değiştirilir ve kaydedilir
  Diyelim ki etkin sürüm v1
  Eğer ki model sorumlusu v2'yi etkin yaparsa
  O zaman yeni açılan olayların önerisi v2'den gelir
  Ve değişiklik denetim izinde görünür
```

### AC-22 (FR-22)

```gherkin
# language: tr
Senaryo: Doğrulanmamış girdi modeli değiştirmez
  Diyelim ki etkin sürüm v1 ve doğrulama bekleyen 100 düzeltme kaydı var
  Eğer ki hiçbir kayıt onaylanmadan sistem çalışmaya devam ederse
  O zaman etkin sürüm v1 kalır ve eğitim etiketi deposu boştur
```

### AC-23 (FR-23)

```gherkin
# language: tr
Senaryo: Model sorumlusu karar değiştiremez
  Diyelim ki kullanıcı "model sorumlusu" rolünde
  Eğer ki bir olay için karar kaydetmeye çalışırsa
  O zaman istek 403 ile reddedilir ve denetim izine yetkisiz deneme olarak yazılır
Senaryo: Analist doğrulama yapamaz
  Diyelim ki kullanıcı "analist" rolünde
  Eğer ki doğrulama kuyruğunda bir kaydı onaylamaya çalışırsa
  O zaman istek 403 ile reddedilir
```

### AC-24 (FR-24)

```gherkin
# language: tr
Senaryo: Yanlış parolayla giriş reddedilir
  Diyelim ki "analist1" hesabı var
  Eğer ki yanlış parolayla giriş denenirse
  O zaman oturum açılmaz
Senaryo: Parola açık metin saklanmaz
  O zaman kullanıcı tablosunda parola alanı özet değeri içerir, açık metin içermez
```

### AC-25 (FR-25)

```gherkin
# language: tr
Senaryo: Sistem dış eylem göndermez
  Diyelim ki analist bir olayı "Gerçek tehdit" olarak kabul etmiş
  O zaman sistem LLM servisi dışında hiçbir ağ çağrısı yapmaz
  Ve arayüzde "Sistem otomatik müdahale yapmaz" ibaresi görünür
```

### AC-26 (FR-26)

```gherkin
# language: tr
Senaryo: Bölme olay bazlı ve sızıntısızdır
  Diyelim ki veri hattı GUIDE_Train üzerinde çalıştırılmış
  O zaman eğitim, doğrulama ve kilitli test kümelerinin olay kimlikleri (OrgId+IncidentId) kesişimi boştur
  Ve her kümedeki her olayın ilk uyarı zamanı bir sonraki kümenin en erken olayından öncedir ya da eşittir
  Ve yalnız üç kapsam kategorisindeki olaylar bulunur
  Ve çıktılar bir veri sürümü kimliği taşır
```

### AC-27 (FR-27)

```gherkin
# language: tr
Senaryo: Karşılaştırma modeli raporlanır
  Diyelim ki eğitim ve doğrulama kümeleri hazır
  Eğer ki karşılaştırma modeli eğitilirse
  O zaman doğrulama kümesinde macro-F1, doğruluk, sınıf bazlı kesinlik/duyarlılık/F1 ve karışıklık matrisi bir dosyaya yazılır
  Ve kayıtta model sürümü, veri sürümü ve tohum bulunur
```

### AC-28 (FR-28)

```gherkin
# language: tr
Senaryo: Ana model karşılaştırma modeliyle aynı koşulda karşılaştırılır
  Eğer ki ana sınıflandırıcı eğitilirse
  O zaman sonuçlar karşılaştırma modeliyle aynı doğrulama kümesinde ve aynı ölçütlerle tek tabloda raporlanır
```

### AC-29 (FR-29)

```gherkin
# language: tr
Senaryo: AS1 ızgarası tek komutla koşar
  Diyelim ki gürültü {0, 10, 20, 30}, dört doğrulama düzeni ve 3 tohum ayarlanmış
  Eğer ki simülasyon komutu çalıştırılırsa
  O zaman her (gürültü, düzen, tohum) için macro-F1, sızan hatalı etiket oranı, tek tek incelenen kayıt oranı ve işaretleyici kesinlik/duyarlılığı içeren 48 satırlık tablo üretilir
  Ve aynı tohumla tekrar çalıştırma aynı tabloyu verir
```

### AC-30 (FR-30)

```gherkin
# language: tr
Senaryo: Uyuşmazlık ve karar süresi kategori bazında raporlanır
  Diyelim ki denetim izinde üç kategoriden kararlar var
  Eğer ki AS2 raporu üretilirse
  O zaman her kategori için uyuşmazlık oranı (Düzelt + Ret / tüm kararlar) ile karar süresinin medyanı ve çeyrekleri raporlanır
```

### AC-31 (FR-31)

```gherkin
# language: tr
Senaryo: Koşullar dengeli sırayla sunulur ve doğru gizlenir
  Diyelim ki 6 katılımcı kaydedilmiş
  O zaman üç koşulun 6 sıralamasının her biri bir katılımcıya atanır
  Ve "yalnız insan" koşulunda öneri ve açıklama görünmez
  Ve "AI önerisi" koşulunda öneri görünür, SHAP açıklaması görünmez
```

### AC-32 (FR-32)

```gherkin
# language: tr
Senaryo: Çalışma verisi anonim kaydedilir ve güven oranları hesaplanır
  Diyelim ki katılımcı P07 "AI önerisi" koşulunda modelin yanlış önerdiği bir vakayı kabul etmiş
  O zaman katılımcı deposunda P07, koşul, karar, süre ve "öneri yanlış" alanları bulunur
  Ve P07'nin aşırı güven oranı hesabına bu vaka dahil edilir
```

### AC-33 (FR-33)

```gherkin
# language: tr
Senaryo: Katılımcı verisi silinir, denetim izi etkilenmez
  Diyelim ki P07'nin kayıtları var
  Eğer ki P07'nin verisi silinirse
  O zaman katılımcı deposunda P07 kaydı kalmaz
  Ve denetim izinde katılımcı kimliği hiç bulunmaz
```

### AC-34 (FR-34)

```gherkin
# language: tr
Senaryo: Alıştırma ölçüme katılmaz
  Diyelim ki katılımcı alıştırmada 3 sentetik kart çözmüş
  O zaman bu kararlar katılımcı deposundaki ölçüm kayıtlarında bulunmaz
```

## 7. Kısıtlar, veri kaynağı ve araçlar

**Veri kaynağı** (Adım 1.3; ayrıntı: `docs/research/2026-11-02-guide-veri-denetimi.md`):

| Özellik | Değer |
|---|---|
| Veri seti | Microsoft GUIDE (Kaggle `Microsoft/microsoft-security-incident-prediction`, Version 2) |
| Lisans | CDLA-Permissive-2.0; atıf: Freitas vd., WWW Companion 2025, doi:10.1145/3701716.3715209 |
| Erişim tarihi | 2026-11-02 |
| Boyut | GUIDE_Train 9.516.837 kanıt satırı, 730.778 olay; GUIDE_Test 4.147.992 satır |
| Kapsam (3 kategori) | InitialAccess 293.837, SuspiciousActivity 141.455, Exfiltration 91.926 olay (toplam ~527 bin, eğitim olaylarının %72'si) |
| Sınıf dağılımı (olay, tümü) | BP %47,4, FP %29,4, TP %19,9, etiketsiz %3,2 (etiketsizler çıkarılır) |
| Kişisel veri | Yok; varlık alanları anonim sayısal kimlik. Gösterimde tutarlı takma ad kullanılır |
| Sınırlılık | Uyarı başlığı metin değil; etiketler müşteri beyanı ve gürültülü; zaman damgalarına gürültü eklenmiş |

**B planı (veri):** GUIDE'ın okunur alanları vaka kartına yetersiz kalırsa K2 yeniden ele alınır. Okunabilir sentetik veri ve onunla eğitilen model alternatif olarak kullanılır. Sentetik veri sonuçları gerçek ortam başarısı olarak sunulmaz (s.3).

**B planı (donanım):** Eğitim dizüstüne sığmazsa önce kapsam içi olaylardan zaman sıralı örneklem alınır, ardından bulut ya da laboratuvar makinesi denenir. Örneklem oranı deney kaydına yazılır.

**Araçlar ve gerekçeleri** (ayrıntı ADR'lerde):

| Araç | Kullanım | Gerekçe |
|---|---|---|
| Python 3.11, `.venv` | Bütün kod | Konu tanımının "gerekli beceriler" maddesi; kurulu sürüm (ADR-0003) |
| FastAPI + uvicorn | REST API, yetki | ADR-0001 |
| HTML/CSS/vanilla JS | Arayüz | Derleme adımı yok (ADR-0001) |
| SQLite (3 dosya) | Denetim izi, etiket deposu, katılımcı deposu | Sıfır kurulum; tetikleyicilerle değişmezlik (ADR-0002) |
| DuckDB + Parquet | GUIDE veri hattı | 9,5 M satır belleğe alınmadan işlenir (ADR-0002) |
| scikit-learn | Taban model (lojistik regresyon) | ADR-0003 |
| LightGBM | Ana model (9–10. hafta) | Yerleşik TreeSHAP (ADR-0003) |
| pytest, httpx | Testler | — |
| LLM sağlayıcısı | Ön denetçi (11–12. hafta) | R3 araştırmasıyla 9–10. haftada seçilecek (açık soru 3) |

**Kısıtlar:**
- Donanım: 16 GB RAM, GPU'suz dizüstü (Windows 11).
- Süre: 18 haftalık yol haritası.
- Gerçek üretim sistemlerine müdahale yok (s.3).
- Paylaşılması yasak veri teslim paketine eklenmez (s.18). GUIDE lisansı paylaşıma izin verir, ama ham veri pakete konmaz; indirme yolu belgelenir.

## 8. Sözlük

| Terim | Anlamı |
|---|---|
| Olay (incident) | GUIDE'da `OrgId + IncidentId` ile tekil, bir ya da daha çok uyarıdan oluşan karar birimi |
| Uyarı (alert) | Olayı oluşturan tespit; olay ekranında kanıt olarak listelenir |
| Kanıt satırı (evidence) | GUIDE'daki tek satır: bir uyarıdaki bir varlık |
| Gerçek tehdit / Zararsız-beklenen / Yanlış alarm | GUIDE `IncidentGrade` değerleri TP / BP / FP |
| Öneri | Etkin model sürümünün olay için sınıf + güven skoru çıktısı |
| İnceleme gerekli | Güven skoru eşiğin altında kalan öneri ya da reddedilen olayın durumu |
| Karar türü | Kabul, Düzelt, Ret |
| Etkin karar | Bir olayın en son geçerli karar sürümü |
| Denetim izi | Tüm karar, doğrulama ve sürüm olaylarının yalnız eklenebilen kaydı |
| Eğitim etiketi deposu | Yalnız kıdemli analistin onayladığı etiketlerin tutulduğu, denetim izinden ayrı depo |
| Ön denetçi | Geri bildirimi işaretleyen bileşen (kural tabanlı ya da LLM); onay vermez |
| Kilitli test kümesi | Model ya da eşik seçiminde kullanılmayan, yalnız sürüm karşılaştırmasında okunan küme |
| Veri sürümü / model sürümü | Bir bölme çıktısının ve eğitilmiş modelin değişmez kimliği |

## 9. Açık sorular

| # | Soru | Neyi etkiliyor | Durum |
|---|---|---|---|
| 1 | Ret kararında gerekçe zorunlu mu? | FR-08, AC-08 | Kapandı (2026-11-02): zorunlu |
| 2 | FR-11'deki "tekrar" yorumu doğru mu: tekrar karar denetim izine yazılır ama yeni sürüm ve doğrulama işi açmaz | FR-11, AC-11 | Kapandı (2026-11-02): doğru |
| 3 | Araçlar ve LLM sağlayıcısı (yerel ya da API), maliyet sınırı | §7, NFR-08, FR-17 | Faz 3'e ertelendi |
| 4 | "İnceleme gerekli" eşik değeri | FR-04 | Deney planına (4. hafta) ertelendi |
| 5 | Ölçekler (SUS, NASA-TLX, Jian) sistem içinde mi, ayrı formla mı toplanacak | FR-31, FR-32 | 11–12. haftaya ertelenebilir |
| 6 | K2 (vaka kartı yalnız yapılandırılmış alanlarla) yeniden açılacak mı | FR-02, FR-31 | Kullanıcıda; demo kart tasarımında hatırlatılacak |
