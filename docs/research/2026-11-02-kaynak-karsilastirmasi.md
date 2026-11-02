# Kaynak karşılaştırması: yöntem, veri, başarı ölçütü, sınırlılık

- **Tarih:** 2026-11-02
- **Hizmet ettiği çıktı:** Yol haritası Adım 1.1 ("en az beş ilgili akademik veya teknik kaynağı yöntem, veri, başarı ölçütü ve sınırlılık açısından karşılaştırın"); SRS §1; özgünlük cümlesi.
- **Yöntem:** 7. oturumun SOC araştırmasında (`docs/research/2026-11-02-soc-sistemleri.md`) birincil kaynaktan okunan yedi çalışma dört ölçüte göre yeniden düzenlendi. Yeni web taraması yapılmadı. Bir bilgi kaynağın yalnız özetinden geliyorsa öyle işaretlendi. Kaynak numaraları SOC raporunun kaynak listesiyle aynıdır.

## Karşılaştırma tablosu

| # | Kaynak | Yöntem | Veri | Başarı ölçütü ve sonuç | Sınırlılık | Bizim için | Güven |
|---|---|---|---|---|---|---|---|
| 1 | **Freitas vd., GUIDE / Copilot Guided Response** (arXiv 2407.09017; WWW Companion 2025) [3] | Üretimde çalışan triyaj ve aksiyon modelleri; haftalık çevrim dışı yeniden eğitim; etiket analist triyaj notlarından, karışık notlarda çoğunluk oyu (eşitlikte TP) | GUIDE: ~13 M kanıt, 1,6 M uyarı, 1 M olay, 6,1 bin kurum, 2 hafta; CDLA-Permissive-2.0 | Önerilen ölçüt macro-F1 (+ kesinlik, duyarlılık). İç CGR modeli bölge 2'de macro-F1 0,91. GUIDE için yayımlanmış taban model sonucu yok | BP'nin standart tanımı yok, etiketler SOC'lar arasında tutarsız; her olay notlanmıyor (yanlılık); resmî bölme zamana göre değil; anonimleştirme yüzünden alanlar sayısal kimlik (veri denetimimiz) | Veri kaynağımız ve üretimdeki geri bildirim → yeniden eğitim döngüsünün emsali. Çoğunluk oyunun denetlenemezliği K3 gerekçemiz | Orta |
| 2 | **Arp vd., "Dos and Don'ts of Machine Learning in Computer Security"** (USENIX Security 2022) [4] | Güvenlikte makine öğrenmesi tuzaklarının (P1–P10) tanımı ve üst düzey güvenlik konferanslarından seçilmiş makalelerde sıklık analizi (makale sayısı bu oturumda doğrulanmadı) | Seçilmiş güvenlik makaleleri ve vaka çalışmaları | Ölçüt yok (yöntem rehberi). Öneriler: etiket hatası (P2), veri gözetleme (P3), sahte korelasyon (P4), test kümesinde ayar (P5), taban model eksikliği (P6), dengesiz veri ölçütleri (P8) | Genel rehber; SOC'ye ya da insan geri bildirimine özgü değil | Bölme, kilitli test, taban model, SHAP'in denetim aracı olarak kullanımı ve "belirsiz etiket testten çıkarılmaz" kurallarımızın kaynağı | Yüksek |
| 3 | **Singh vd., ContextBuddy** (arXiv 2506.09365, 2025) [6] | Kullanıcı çalışması: denekiçi, 3 koşul (yalnız analist / tek seferlik AI yardımı / yinelemeli AI yardımı), sıra dengeli, 30 dk alıştırma, 2 pilot, etik onay; ek olarak ajan simülasyonu | Gerçek açık IDS veri kümeleri (HIKARI-2021, UNSW-NB15); koşul başına 4 uyarı (emin TP/TN, düşük güvenli FP/FN), vakalar özellik uzaklığıyla eşleştirilmiş; N=13 uzman olmayan | Karar doğruluğu (%65,4 → %86,5), süre (−%24), öz güven, açıklamaya güven, bilişsel yük; ölçülen güç 0,8 | Küçük, uzman olmayan örneklem; tek ön baskı; ağ akışı verisi (olay değil); geri bildirimin modele etkisi incelenmiyor | AS3 tasarımımızın en yakın emsali (koşul yapısı, eşleştirme, yanlış öneri vakaları, uzman olmayan katılımcı). "AI yanlışken kabul" bulgusu aşırı güven ölçütümüzü gerekçelendiriyor | Orta |
| 4 | **Rastogi vd., "Too Much to Trust?"** (CCS 2025; arXiv 2503.02065) [7] | Karma yöntem: anket ve yarı yapılandırılmış görüşme | 248 SOC profesyoneli (anket), 24 görüşme (Kademe 1/2/3: 9/11/4); materyal pano ekran görüntüleri ve GPT ile üretilmiş açıklamalar | Deneysel ölçüt yok; betimsel ve tematik bulgular: kanıta dayalı XAI daha düşük doğrulukta bile kabul görüyor; analistler model iç yapısından çok kısa göstergeler istiyor | Koşul karşılaştırması yok; öz beyan; makalede iç tutarsızlıklar (görüşme süresi, §8.4 rakamları) | SHAP katkısını ham alana bağlama kararımızın ve kısa gösterge odaklı ekran tasarımının gerekçesi | Orta |
| 5 | **Alahmadi, Axon, Martinovic, "99% False Positives"** (USENIX Security 2022) [8] | Nitel çalışma: anket ve görüşme | 20 anket, 21 görüşme (SOC analistleri) | Deneysel ölçüt yok; tematik bulgular: yanlış alarmların çoğu "zararsız tetik" (meşru davranışın doğru alarmı); elle doğrulama yorgunluk yaratıyor; iyi alarmın nitelikleri: güvenilir, açıklanabilir, analitik, bağlamsal, aktarılabilir | Küçük nitel örneklem; yalnız özet sayfası ve ikincil özet okundu | BP ile FP ayrımının zorluğu (alıştırma materyalinde tanım ve örnek, m13); kıdemli doğrulama yükünün gerçek bir sorun olduğu (AS1 iş yükü ölçütü) | Orta-yüksek |
| 6 | **Vielberth vd., "Security Operations Center: A Systematic Study and Open Challenges"** (IEEE Access 8, 2020) [2] | Sistematik literatür derlemesi | Akademik ve gri literatür (derlenen yayın sayısı bu çalışmada çıkarılmadı) | Ölçüt yok; SOC'nin insan, süreç, teknoloji ve yönetişim boyutlarını sınıflandırıyor; açık sorunlar listesi | 2020'de kalıyor (LLM ve güncel XAI yok); rol tanımları kurumdan kuruma değişebilir | Rollerimiz (Kademe 1 / Kademe 2-3 / güvenlik mühendisi) ve "kıdemliden geri bildirim eksikliği" açık sorunu, K4 ve AS1'in motivasyonu | Orta |
| 7 | **Veeramachaneni vd., AI²** (IEEE BigDataSecurity 2016) [5] | Aktif öğrenme: denetimsiz aykırılık tespiti analiste günde k olay sunar, analist etiketleri denetimli modeli yeniden eğitir | Bir kurumun web günlükleri (ölçek ayrıntısı bu oturumda doğrulanmadı) | Tespit oranı ~%86,8, yanlış pozitifte ~5 kat azalma | Yalnız özet ve proje sayfası okundu; veri ortamı ikincil kaynakta eleştirilmiş [5b]; analist etiketinin doğru olduğu varsayılıyor | Analist etiketinin modele döndüğü döngünün ilk örneği; **etiketi doğrulanmış sayması** bizim AS1 sorumuzun boşluğunu gösteriyor | Orta |

## Sentez

- **Ortak noktalar.** Analist geri bildirimi modele döndürülüyor: üretimde [3] ve aktif öğrenmede [5]. Ancak bu iki kaynak etiketin doğruluğunu ya varsayıyor [5] ya da çoğunluk oyuyla çözüyor [3]. Arp vd. [4] etiket hatasını güvenlikte makine öğrenmesinin temel tuzaklarından biri sayıyor.
- **Açıklama ve güven.** İnsan–AI çalışmaları ya deneysel ama küçük, uzman olmayan örneklemle ve ağ akışı verisiyle [6] ya da profesyonel ama deneysel olmayan bir tasarımla [7], [8] yürütülmüş. Gerçek bir olay veri kümesinde, model önerisi ve SHAP aynı kaynaktan gelirken, üç koşullu denekiçi karşılaştırma yapan bir çalışma görülen kaynaklarda yok.
- **Doğrulama iş yükü.** Elle doğrulamanın yorgunluk yarattığı biliniyor [8]. Literatürde açık sorun olarak kıdemliden geri bildirim eksikliği de geçiyor [2]. Fakat doğrulamanın yükünü bir ön denetçiyle (kural ya da LLM) azaltıp bunun modele sızan hatalı etiket üzerindeki etkisini ölçen bir çalışma görülen kaynaklarda bulunamadı. Bulunamamak yokluk kanıtı değildir.

## Özgünlük cümlesi (öneri)

> Çalışma, SOC analistinin geri bildirimini doğrudan eğitime almak yerine kıdemli onayından geçiren bir akışı, gerçek bir olay veri kümesi (GUIDE) üzerinde iki yönden sınar: (1) eklenen hatalı geri bildirim altında dört doğrulama düzeninin yeniden eğitilen modeli koruma gücü ve kıdemliye bıraktığı iş yükü, (2) aynı modelden gelen öneri ve SHAP açıklamasının analist kararına etkisi (üç koşullu insan çalışması).

Bu cümle ara rapordaki "amaç ve özgünlük" bölümüne aday. Kullanıcı onaylamadan belgeye girmez.

## Açık sorular

1. "Güvenlik ML'inde analist etiket gürültüsü" ve "insan döngülü etiket doğrulama" üzerine hedefli bir literatür taraması yapılmadı. Özgünlük iddiası ara rapordan önce bu taramayla sınanmalı. Güven: orta.
2. Vielberth vd.'nin derlediği yayın sayısı, Arp vd.'nin incelediği makale sayısı ve AI² verisinin ölçeği tam metinden doğrulanmalı.
3. Alahmadi vd. tam metni okunmadı; bulgular özet sayfası ve SOC raporundaki notlara dayanıyor.

## Kaynaklar

Numaralar ve bağlantılar: `docs/research/2026-11-02-soc-sistemleri.md` → "Kaynaklar" (1–10). Hepsine erişim tarihi 2026-11-02.
