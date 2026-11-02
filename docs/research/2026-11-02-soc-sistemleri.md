# Araştırma: SOC organizasyonu, analist geri bildirimi, insan–AI çalışmaları ve GUIDE

- **Tarih:** 2026-11-02
- **Hizmet ettiği karar:** STATUS.md'deki açık kararlar K2 (sentetik vaka kartı mı GUIDE mı), K4 (roller); m7 (veri bölme); AS1 gürültü tasarımı ve insan çalışması ölçütleri. Görüşme belgesi: https://claude.ai/artifact/FgjY9xPk4ZuHuj58K12kr5
- **Kapsam:** Kurumsal SOC pratiği (Microsoft Defender XDR örneği), akademik SOC literatürü (2015–2026), GUIDE veri kümesi (CDLA-2.0). Kullanım kotası nedeniyle sınırlı ve sırayla yapılan arama; subagent kullanılmadı.
- **Önceki rapor:** yok

## Sorular

1. **(A)** Bir SOC'ta roller, kademeler ve onay zinciri nasıl? Uyarıdan olaya iş akışı ve sınıflama nasıl yapılıyor?
2. **(B)** Analist geri bildirimi üretimdeki ML modellerine nasıl dönüyor? Etiket kalitesi, çelişkili geri bildirim ve denetim izi nasıl ele alınıyor?
3. **(C)** SOC'ta insan–AI işbirliği ve açıklanabilirlik kullanıcı çalışmaları vaka materyalini (sentetik ya da gerçek), katılımcıları ve ölçütleri nasıl seçiyor?
4. **(D)** GUIDE'ın alanları, okunabilirliği, lisansı, resmî bölmesi ve IncidentGrade etiketi nasıl?

## Özet

- **S1 (A), güven orta-yüksek.** Literatürde yaygın model şudur: Kademe 1 (triyaj) uyarıyı doğrular ya da yanlış alarm sayar ve çözemediğini yükseltir. Kademe 2 (olay müdahale) derin analiz yapar. Kademe 3 (tehdit avcısı) en kıdemli kademedir ve alt kademelerin çıktısını gözden geçirir. Bunlara SOC yöneticisi ve tespit kurallarını yazan güvenlik mühendisi eklenir [2]. Defender XDR'de olay tek bir sahibe atanır ve üç sınıftan birine konur: *True positive*, *Informational, expected activity*, *False positive*. Kapanışta çözüm notu yazılır, kullanıcının ve sistemin her değişikliği etkinlik günlüğüne düşer. Sınıflamanın tespiti zamanla iyileştirdiği belirtilir [1]. **Etkisi:** Üç sınıfımız (Gerçek tehdit / Zararsız-beklenen / Yanlış alarm), Defender'ın ve GUIDE'ın (TP/BP/FP) sınıflarıyla birebir örtüşüyor. Üç rolümüz literatürdeki L1 / L2-L3 / güvenlik mühendisi ayrımına karşılık geliyor. "Model sorumlusu" adı literatürde geçmiyor; en yakın karşılığı tespit kurallarını yazan güvenlik mühendisi. K4 için destekleyici.
- **S2 (B), güven orta.** GUIDE'ı yayımlayan Microsoft hattında etiketler müşteri analistlerinin triyaj notlarından gelir; model haftalık, çevrim dışı yeniden eğitilir. Bir olayda karışık notlar varsa çoğunluk alınır, eşitlikte TP seçilir [3]. Makalenin kendisi de BP için standart bir tanım olmadığını ve bu yüzden SOC'lar arasında ve SOC içinde tutarsızlık bulunduğunu söylüyor [3]. Arp vd. güvenlikte etiket hatasını (P2) temel tuzak sayar; etiketlerin elle doğrulanmasını, belirsiz örneklerin test kümesinden çıkarılmamasını ve zaman sızıntısından (P3) kaçınılmasını önerir [4]. Aktif öğrenmede klasik örnek AI²'dir: analist her gün az sayıda aykırı olayı etiketler, model bunlarla yeniden eğitilir [5]. **Etkisi:** Çevrim dışı, sürümlü yeniden eğitim kararımız üretim pratiğiyle uyumlu. K3'te çelişkili kararları kıdemliye göndermemiz, Microsoft'un kural tabanlı çoğunluk oyundan daha denetlenebilir; bu fark belgeye gerekçe olarak yazılabilir. AS1 için iki sonuç var: (1) GUIDE'ın kendi etiketleri gürültülü, bu yüzden "%0 gürültü" temiz veri değil, "eklenen gürültü %0" anlamına gelir. (2) Test etiketleri de gürültülü; bu sınırlılık olarak yazılmalı.
- **S3 (C), güven orta.** En yakın emsal ContextBuddy'nin (2025) kullanıcı çalışması [6]. Denekiçi tasarımda 3 koşul ve **uzman olmayan 13 katılımcı** var; ölçülen güç 0,8. Vakalar sentetik değil, **gerçek açık veri kümelerinden (HIKARI-2021, UNSW-NB15) seçilmiş**. Her koşulda 4 uyarı var: AI'ın emin ve doğru olduğu 2, düşük güvenle yanlış olduğu 2. Koşullar arası vakalar özellik uzaklığı en küçük olacak biçimde eşleştirilmiş. Çalışmada 30 dakikalık alıştırma aşaması, sıra dengeleme ve etik kurul onayı da var. Katılımcıların bir kısmı, doğru verdikleri kararı AI önerisini görünce yanlışa çevirmiş; yazarlar bundan açıklamanın "ne zaman güvenmemeli"yi de göstermesi gerektiği sonucunu çıkarıyor. Profesyonel analistlerle yapılan çalışmalar ise çoğunlukla anket ve görüşmeye dayanıyor (N=248 anket, 24 görüşme). Bunlara göre analistler model iç yapısından çok kısa göstergeler istiyor ve kanıta dayalı açıklama, düşük doğrulukta bile kabul görüyor [7]. Alahmadi vd.'ne göre yanlış alarmların çoğu aslında "zararsız tetik"tir, yani meşru davranışın ürettiği doğru alarmlardır [8]. **Etkisi:** K2 için karma yaklaşımı destekliyor: model GUIDE'da eğitilir; insan çalışması GUIDE'dan seçilip okunur karta dönüştürülen gerçek olaylarla yapılır; sentetik kart yalnızca alıştırma ve B planı için kullanılır. 12–18 katılımcı hedefimiz emsalle uyumlu. "AI yanlışken kabul" (aşırı güven) ölçütü açıkça eklenmeli. BP ile FP ayrımı katılımcı için zor; alıştırma materyalinde tanım ve örnek verilmeli.
- **S4 (D), güven orta (okunabilirlik düşük).** GUIDE iki haftalık veri içeriyor: yaklaşık 13 milyon kanıt, 1,6 milyon uyarı, 1 milyon olay, 6,1 bin kurum, 45 sütun. Lisansı CDLA-2.0 [3]. Bölme %70 eğitim / %30 test; IncidentGrade, OrgId ve DetectorId'ye göre tabakalı ve **zamana göre değil**. Olayların bölmelerde bir arada tutulduğu söyleniyor ama açıkça yazılmamış [3]. Hassas değerler SHA1 ile özetlenip rastgele kimliklerle değiştirilmiş, zaman damgalarına gürültü eklenmiş [3]. Sınıf dağılımı yaklaşık TP %14–19, FP %34–35, BP %46–52; makalede iki farklı rakam veriliyor. Önerilen ana ölçüt macro-F1 [3]. Hangi sütunların okunur kaldığı makalede yazmıyor ve doğrulanamadı; Kaggle sayfası okunamadı. **Etkisi:** m7'deki "zaman/kurum kuralı" resmî bölmeyle çelişiyor: resmî bölmede aynı kurum hem eğitimde hem testte var ve bölme zamana göre yapılmamış. Hangi bölmeyi kullanacağımız ayrı bir karar. Okunabilirlik ise veri denetiminde ilk iş olarak kalıyor; insan çalışmasının kart tasarımı buna bağlı.

## Bulgular

### S1: SOC rolleri, onay zinciri, iş akışı

- Kademe 1 (triyaj uzmanı) uyarıyı gözden geçirir, kritikliğini doğrular ya da ayarlar ve zenginleştirir. "Her uyarı için haklı mı yoksa yanlış alarm mı" kararını verir, çözemediğini Kademe 2'ye yükseltir ([2], §V-A) · Güven: orta
- Kademe 2 (olay müdahale) yükseltilen olayları tehdit istihbaratıyla derinlemesine inceler, kapsamı belirler, sınırlama ve kurtarma stratejisini tasarlar; gerekirse Kademe 3'e yükseltir ([2]) · Güven: orta
- Kademe 3 (tehdit avcısı) en deneyimli kademedir. Büyük olayları alır, izleme araçlarının iyileştirilmesini önerir ve "Kademe 1 ile 2'nin sağladığı kritik uyarı ve verileri bu kademe gözden geçirmelidir" ([2]) · Güven: orta
- SOC yöneticisi ekibi yönetir. Güvenlik mühendisi SOC araçlarını geliştirir ve bakımını yapar, SIEM tespit kurallarını yazmaya ve güncellemeye yardım eder ([2]) · Güven: orta
- Literatürde açık sorun olarak "kıdemli analistten geri bildirim eksikliği" ve "Kademe 1 ile 2 arasında geri bildirim döngüsü" ihtiyacı geçiyor ([2], §VI) · Güven: orta
- Defender XDR'de olay tek kullanıcıya ya da gruba atanır ve atama olayın tüm uyarılarına geçer. Durumlar Active → In progress → Resolved'dır; Resolved seçilince çözüm notu istenir ve not etkinlik günlüğünde görünür ([1]) · Güven: yüksek (resmî belge)
- Defender XDR sınıfları: *Not set*; *True positive* (tehdit türüyle); *Informational, expected activity* (güvenlik testi, red team, güvenilir uygulamanın beklenen olağandışı davranışı); *False positive* (teknik olarak hatalı ya da yanıltıcı). Belgeye göre "sınıflama, Defender'ın zamanla daha iyi tespit kararı vermesine yardım eder" ([1]) · Güven: yüksek
- Defender XDR'de kullanıcının ya da sistemin olayda yaptığı her değişiklik etkinlik günlüğüne kaydedilir ([1]) · Güven: yüksek
- Profesyonel analistlerle yapılan çalışmalarda örneklem Kademe 1/2/3'e göre tabakalanıyor (9/11/4) ([7]) · Güven: orta

### S2: Analist geri bildirimi → model

- Microsoft Copilot Guided Response (CGR): eğitim hattı haftalık çalışır ve geçmiş SOC telemetrisinden triyaj ve aksiyon modellerini eğitir. Etiketler müşteri analistlerinin triyaj notlarıdır ([3], §3, §7.2) · Güven: orta (tek birincil kaynak)
- CGR'de bir olayda karışık notlar varsa çoğunluk etiketi alınır, eşitlikte TP seçilir ([3], §4.1 T4) · Güven: orta
- Aynı makaleye göre BP için standart tanım yok ve bu yüzden SOC'lar arasında ve SOC içinde sınıflama tutarsız. Her olay notlanmıyor, bu da yanlılık yaratıyor; uyarıların çoğunda analist aksiyon almıyor ([3], §7.3, §7.5) · Güven: orta
- Arp vd. (USENIX Sec '22): P2 etiket hatası için etiketler mümkün olduğunca elle doğrulanmalı. Gürültü sürüyorsa üç yol var: dayanıklı model, gürültüyü modelleme, eğitim verisini temizleme. "Belirsiz etiketli örnekler test verisinden çıkarılmamalı" ([4]) · Güven: yüksek (çok atıflı, ödüllü birincil kaynak)
- Arp vd.: P3 veri gözetleme. Test kümesi erken ayrılmalı; ön işleme (ölçekleme, gömme vb.) yalnız eğitim verisinden hesaplanmalı; zaman bağımlılığı bölmede dikkate alınmalı. P5: eşik ve hiperparametre test kümesinde değil, ayrı doğrulama kümesinde seçilmeli. P6: basit taban modeller karşılaştırmaya konmalı. P8: dengesiz veride kesinlik ve duyarlılık kullanılmalı ([4]) · Güven: yüksek
- Arp vd. P4: sahte korelasyonları bulmak için açıklama teknikleri (SHAP vb.) önerilir ([4]) · Güven: yüksek. *Bizim için:* SHAP yalnız kullanıcıya gösterilen bir açıklama değil, model denetim aracı olarak da gerekçelendirilebilir.
- AI² (Veeramachaneni vd., 2016): denetimsiz aykırılık tespiti, analiste günde k olay sunar; analist etiketleri denetimli modeli yeniden eğitir. Yayımlanan sonuç: yaklaşık %86,8 tespit oranı ve yanlış pozitiflerde 5 kat azalma ([5]). Veri ortamı ikincil bir kaynakta eleştirilmiş ([5b]) · Güven: orta
- Görülen kaynaklarda "çelişkili analist geri bildiriminin kıdemli onayına gitmesi" için üretimden belgelenmiş bir örnek bulunamadı. CGR çoğunluk oyu kullanıyor · Güven: düşük (bulunamamak yokluk kanıtı değil)

### S3: İnsan–AI kullanıcı çalışmaları

- ContextBuddy (Singh vd., CSIRO Data61, arXiv 2506.09365, 2025): denekiçi, 3 koşul (yalnız analist / tek seferlik yardım / yinelemeli yardım), uzman olmayan N=13 (yalnız 1 kişinin IDS deneyimi var), ölçülen güç 0,8 ([6]) · Güven: orta (tek ön baskı)
  - Vakalar gerçek açık IDS veri kümelerinden; simülasyonda kullanılmayan örneklerden rastgele seçilmiş. Her koşulda 4 uyarı: emin TP, emin TN, düşük güvenli FP ve FN. Koşullar arası vakalar ikili uzaklığı en küçük olacak biçimde eşleştirilmiş, çünkü aynı vaka tekrar kullanılamıyor.
  - Katılımcılara yalnız geçmiş veriden hesaplanan alan istatistikleri (ortalama, medyan, mod) gösterilmiş. Amaç, SHAP açıklamasını eleştirel değerlendirebilmeleri ve öneriyi pasif kabul etmemeleri.
  - 30 dakikalık alıştırma ve iki pilot çalışma yapılmış; C1 ile C2 sırası dengelenmiş, C3 hep sonda. Ölçütler: doğruluk, süre, öz güven (0–100), açıklamaya güven ölçeği, bilişsel yük (Klepsch). Etik kurul onayı alınmış.
  - Sonuç: doğruluk %65,4'ten %86,5'e çıkmış, süre %24 azalmış. Simülasyonda bazı ajanlar doğru kararı AI önerisiyle yanlışa çevirmiş; yazarlar açıklamanın "ne zaman güvenmemeli"yi de göstermesi gerektiğini söylüyor.
- Rastogi vd. (RIT, CCS 2025, "Too Much to Trust?"): 248 SOC profesyoneline anket ve 24 görüşme (Kademe 1/2/3: 9/11/4). Deneysel koşul karşılaştırması yok. Vaka materyali pano ekran görüntüleri ve GPT ile üretilmiş açıklamalar. Bulgular: analistler XAI çıktısını açıklama ilgili ve kanıta dayalıysa "daha düşük doğrulukta bile" kabul ediyor; triyajda model iç yapısından çok kısa göstergeleri ve yapılacak aksiyonu öne çıkarıyorlar ([7]) · Güven: orta. Not: makalede iç tutarsızlıklar var (görüşme süresi iki farklı değer; §8.4'teki rakamlar yöntemsiz).
- Alahmadi vd. (Oxford, USENIX Sec '22): 20 anket ve 21 görüşme. Yanlış alarm oranı yüksek ve elle doğrulama gerekiyor; yanlış alarmların çoğu meşru davranışın tetiklediği doğru alarmlar (zararsız tetik). Doğrulama işi yorgunluğa ve duyarsızlaşmaya yol açıyor. İyi alarm için önerilen nitelikler: güvenilir, açıklanabilir, analitik, bağlamsal, aktarılabilir ([8]) · Güven: orta-yüksek
- 32 öğrenci ve 32 profesyonelle yapıldığı söylenen bir XAI-SOC çalışması bir ResearchGate özetinde görüldü, tam metne ulaşılamadı ([9]) · Güven: düşük; kullanılmamalı.

### S4: GUIDE

- Boyut ve kapsam: yaklaşık 13 milyon kanıt, 1,6 milyon uyarı, 1 milyon olay; 6,1 bin kurum, 9,1 bin DetectorId, 441 MITRE tekniği; iki hafta; 33 varlık türü. "Gerçek dünya siber olaylarının izin verici CDLA-2.0 ile yayımlanan en büyük açık koleksiyonu" ([3], §1.1, §7.2) · Güven: orta (tek birincil kaynak, iki ikincil kaynak tekrar ediyor)
- 45 sütun: Id, OrgId, IncidentId, AlertId, Timestamp, DetectorId, AlertTitle, Category, MitreTechniques, IncidentGrade, ActionGrouped, ActionGranular, EntityType, EvidenceRole, Roles, DeviceId, DeviceName, Sha256, IpAddress, Url, AccountSid, AccountUpn, AccountObjectId, AccountName, NetworkMessageId, EmailClusterId, RegistryKey, RegistryValueName, RegistryValueData, ApplicationId, ApplicationName, OAuthApplicationId, ThreatFamily, FileName, FolderPath, ResourceIdName, ResourceType, OSFamily, OSVersion, AntispamDirection, SuspicionLevel, LastVerdict, CountryCode, State, City ([3], Tablo 4) · Güven: orta
- Anonimleştirme: hassas değerler önce SHA1 ile özetlenmiş, sonra rastgele kimliklerle değiştirilmiş; zaman damgalarına gürültü eklenmiş ([3], Ek C) · Güven: orta. **Hangi sütunların "hassas" sayıldığı yazmıyor.** Tablo 4 AlertTitle'ı "uyarının başlığı" diye tanımlıyor ama değerin metin mi kimlik mi olduğunu söylemiyor · Güven: düşük
- Bölme: %70 eğitim / %30 test, "triyaj notu, OrgId ve DetectorId'ye göre tabakalı" ([3], Ek B). "Olaylar eğitim ve test kümelerinde birlikte tabakalanır" deniyor; olay düzeyinde gruplama ima ediliyor ama açıkça yazılmamış. Zamana göre bölme yok; GUIDE için doğrulama kümesi tanımlanmamış · Güven: orta
- IncidentGrade: TP / BP / FP. BP için örnek "bilgilendirme amaçlı" diye verilmiş, resmî tanım yok. Dağılım §7.3'te TP %19 / FP %35 / BP %46, GUIDE'ın türetildiği bölge için (Tablo 2) TP %14 / FP %34 / BP %52; iki rakamın tutarsızlığı makalede açıklanmıyor ([3]) · Güven: orta
- Önerilen ana ölçüt macro-F1, yanında kesinlik ve duyarlılık. GUIDE için ayrı bir taban model sonucu yayımlanmamış; makaledeki rakamlar iç CGR modeline ait (bölge 2'de macro-F1 0,91) ([3]) · Güven: orta
- GUIDE'ın 2026 uzantısı: Freitas vd. 499 kurum kuyruğundaki 9.980 olaya uzman öncelik etiketleri eklemiş ("AIP", Defender Queue Assistant'ın sıralama algoritması) ([10]) · Güven: orta (yalnız özet okundu). Bizim için kapsam dışı; ilgili çalışma olarak anılabilir.

## Karşılaştırma

K2 için insan çalışmasında vaka materyali seçenekleri:

| Aday | Ekolojik geçerlilik | Okunabilirlik | Model ile tutarlılık | Hocanın konu tanımına uyum | Emsal | Risk |
|---|---|---|---|---|---|---|
| Tamamen sentetik vaka kartı | Düşük (Arp P9: yalnız laboratuvar) | Tam kontrol | Zayıf: model GUIDE'da eğitilir, kart başka dağılımdan gelir; ayrı model gerekir | Birebir ("sentetik vaka kartları") | [7] GPT ile üretilmiş bağlam (yalnız görüşme) | Bulgular gerçek veriye genellenemez |
| GUIDE ham satırları | Yüksek | Muhtemelen düşük (anonim kimlikler) | Tam | Zayıf | — | Katılımcı karar veremez |
| **Karma: GUIDE'dan seçilip okunur karta dönüştürülen gerçek olay; sentetik kart yalnız alıştırma ve B planı için** | Orta-yüksek | Okunur alanlar karta, anonim kimlikler "Kullanıcı-17" gibi tutarlı takma adlarla | Tam (öneri ve SHAP aynı modelden) | Kart biçimi korunur, içerik gerçek veriden türetilir | [6] gerçek açık veriden seçilmiş, eşleştirilmiş vakalar, uzman olmayan katılımcılar | Okunabilirlik veri denetimine bağlı; kartın "doğru cevabı" müşteri etiketi ve gürültülü olabilir, bu yüzden ekip iki kişi olarak elle doğrulamalı (Arp P2) |

K4 için roller:

| Bizim rol | Literatür karşılığı | Yetki (önerilen) |
|---|---|---|
| Analist | Kademe 1 triyaj uzmanı [2]; Defender'da olayın sahibi [1] | Kabul / Düzelt (+gerekçe) / Ret |
| Kıdemli analist | Kademe 2/3; "alt kademelerin çıktısını gözden geçirir" [2] | İşaretli geri bildirimi tek tek, işaretsizi toplu onaylar; çelişkileri çözer; etiket deposuna yazmayı onaylar |
| Model sorumlusu | Güvenlik mühendisi, tespit kurallarını yazar ve günceller [2] (literatürde "model sorumlusu" adı geçmiyor) | Onaylı etiketlerle yeniden eğitimi tetikler, sürümleri karşılaştırır; etiket değiştiremez (görev ayrılığı) |

## Pratik durum

| Aday | Son sürüm | Açık hata kayıtları | Lisans | Donanım | Windows / Python |
|---|---|---|---|---|---|
| GUIDE (Kaggle) | 2024 (arXiv v4) | Kaggle tartışmaları okunmadı | CDLA-2.0 (izin verici) | Tam veri yaklaşık 13 milyon satır; pandas ile bellek ihtiyacı ölçülmeli. Örnekleme veya `usecols`/dtype ile 16 GB RAM'de muhtemelen yeterli (doğrulanmadı) | CSV; platformdan bağımsız |

## Açık sorular

1. **GUIDE'ta hangi sütunlar okunur metin?** (AlertTitle, Category, MitreTechniques, ThreatFamily, FileName, EntityType, EvidenceRole, SuspicionLevel, LastVerdict.) Kaggle'dan inen CSV'de `df.head()` ve `nunique()` ile 10 dakikada cevaplanır; Kaggle'a giriş gerektiği için kullanıcının indirmesi gerekiyor. K2'nin karma seçeneği bu cevaba bağlı.
2. Resmî bölmede bir olayın tüm satırları aynı kümede mi? Veride `IncidentId` kesişimi kontrol edilerek doğrulanır.
3. TP/BP/FP oranının iki farklı rakamı: veride `value_counts` ile ölçülür.
4. MITRE'nin "11 Strategies" kitabı (SOC yapısı için birincil kaynak) 403 verdiği için okunamadı. Rol bulguları tek bir akademik derlemeye ve Defender belgesine dayanıyor.
5. Türkçe uyarlanmış SUS, Jian ve NASA-TLX ölçekleri bu araştırmanın kapsamı dışında kaldı.

## Kaynaklar

1. [Manage incidents in the Microsoft Defender portal (legacy)](https://learn.microsoft.com/en-us/defender-xdr/manage-incidents): birincil (resmî belge, güncelleme 2026-09-23), erişim 2026-11-02
2. [Vielberth vd., "Security Operations Center: A Systematic Study and Open Challenges", IEEE Access 8, 2020](https://epub.uni-regensburg.de/44375/3/09296846.pdf) (DOI 10.1109/ACCESS.2020.3045514): birincil (sistematik derleme), erişim 2026-11-02
3. [Freitas vd., "AI-Driven Guided Response for Security Operation Centers with Microsoft Copilot for Security" (GUIDE), arXiv 2407.09017](https://arxiv.org/html/2407.09017): birincil, erişim 2026-11-02
4. [Arp vd., "Dos and Don'ts of Machine Learning in Computer Security", USENIX Security 2022](https://www.usenix.org/conference/usenixsecurity22/presentation/arp) ([PDF](https://arxiv.org/pdf/2010.09470)): birincil, erişim 2026-11-02
5. [Veeramachaneni vd., "AI²: Training a big data machine to defend", 2016](https://people.csail.mit.edu/kalyan/AI2_Paper.pdf) ([proje sayfası](https://people.csail.mit.edu/kalyan/AI2)): birincil (yalnız özet ve proje sayfası okundu), erişim 2026-11-02
   - 5b. [Security Intelligence eleştirisi](https://securityintelligence.com/with-ai2-machine-learning-and-analysts-come-together-to-impress-part-3-the-experiment): ikincil, erişim 2026-11-02
6. [Singh vd., "ContextBuddy: AI-Enhanced Contextual Insights for Security Alert Investigation", arXiv 2506.09365, 2025](https://arxiv.org/pdf/2506.09365): birincil (ön baskı), erişim 2026-11-02
7. [Rastogi vd., "Too Much to Trust? Measuring the Security and Cognitive Impacts of Explainability in AI-Driven SOCs", arXiv 2503.02065 (CCS 2025)](https://arxiv.org/html/2503.02065): birincil, erişim 2026-11-02
8. [Alahmadi, Axon, Martinovic, "99% False Positives: A Qualitative Study of SOC Analysts' Perspectives on Security Alarms", USENIX Security 2022](https://www.usenix.org/conference/usenixsecurity22/presentation/alahmadi): birincil (özet sayfası okundu), erişim 2026-11-02
9. [Explainable AI for SOC Analysts (ResearchGate)](https://www.researchgate.net/publication/404704611_Explainable_AI_for_SOC_Analysts_A_Framework_for_Bridging_Model_Output_and_Operational_Trust_Through_Counterfactual_and_Causal_Explanations): ikincil ya da doğrulanamadı, kullanılmadı, erişim 2026-11-02
10. [Freitas, Gharib, Magenheim, "Adaptive Incident Prioritization for Security Operations at Scale", arXiv 2607.16963](https://arxiv.org/abs/2607.16963): birincil (yalnız özet okundu), erişim 2026-11-02
