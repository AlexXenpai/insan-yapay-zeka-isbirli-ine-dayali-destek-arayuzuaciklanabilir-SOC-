# Deney planı: Taban model, ana model ve AS1 doğrulama simülasyonu

- **Tarih:** 2026-11-02
- **Durum:** E1 koşuldu (2026-11-02, §9); E2–E4 9–14. haftalar
- **İlgili dokümanlar:** FR-04, FR-05, FR-20, FR-26–FR-29, NFR-03, NFR-04, NFR-13, NFR-15; ADR-0003, ADR-0004, ADR-0005; `docs/data-design.md` §9; `docs/research/2026-11-02-kaynak-karsilastirmasi.md`

Yol haritası s.3, eşik ve kabul hedeflerinin 4. haftada gerekçelendirilmesini istiyor. Aşağıdaki hedefler sonuçlar görülmeden yazıldı. Sonuç görüldükten sonra bir hedef değişirse önceki hedef ve değişikliğin nedeni §9'da korunur.

## 1. Sorular ve hipotezler

| Deney | Soru | Hipotez | Çürüten sonuç |
|---|---|---|---|
| E1 (5. hafta) | Okunur alanlarla basit bir model GUIDE'ın kapsam içi olaylarında anlamlı öneri üretiyor mu? | Lojistik regresyonun macro-F1 değeri katmanlı rastgele tahminden en az 0,10 yüksek | Fark < 0,10 |
| E2 (9–10. hafta) | Ana model (LightGBM) taban modeli geçiyor mu; kimlik alanları ne kadar katkı sağlıyor? | LightGBM (okunur alanlar) ≥ taban + 0,05 macro-F1; kimlik alanları ek kazanç sağlıyor | LightGBM < taban + 0,05 |
| E3 (9–10. hafta) | "İnceleme gerekli" eşiği uygun mu? | §2'deki kuralla seçilen τ'da işaretsiz önerilerin doğruluğu ≥ 0,80, kapsamı ≥ %50 | İkisi aynı anda sağlanamıyor |
| E4 (13–14. hafta, AS1) | Hatalı geri bildirim altında hangi doğrulama düzeni modeli korur, kıdemliye ne kadar iş bırakır? | H1: Doğrulamalı düzenlerde macro-F1 kaybı her gürültü düzeyinde doğrulamasız düzenden küçük; fark gürültü arttıkça büyüyor. H2: LLM işaretleyici, kuralla aynı iş yükünde daha az hatalı etiket sızdırıyor | H1: %20 ve %30 gürültüde fark, tohumlar arası standart sapmanın 2 katından küçük. H2: aynı iş yükünde sızıntı oranları arasındaki fark tohum dağılımı içinde kalıyor |

## 2. Metrikler ve kabul eşikleri

| Metrik | Tanım | Neden | Başarı eşiği (gerekçe) |
|---|---|---|---|
| **Macro-F1** (ana) | Üç sınıfın F1 ortalaması | GUIDE'ın önerdiği ölçüt [3]; sınıflar dengesiz (s.3) | E1: ≥ katmanlı rastgele + 0,10 (rastgele ≈ 0,33; 0,10 tutarlı bir öğrenme sinyalini rastlantıdan ayırır). E2: ≥ taban + 0,05 (ana modelin ek karmaşıklığı, tohum değişkenliğini aşan bir kazançla gerekçelenmeli) |
| Doğruluk, sınıf bazlı kesinlik / duyarlılık / F1, karışıklık matrisi | sklearn | s.3 ve m1 bunları istiyor | Raporlanır, eşik yok |
| Seçici doğruluk ve kapsam | Güven ≥ τ olan önerilerin doğruluğu ve oranı | FR-04 eşiğinin dayanağı | Doğruluk ≥ 0,80, kapsam ≥ %50 (aşağıdaki kural) |
| Sızan hatalı etiket oranı | Etiket deposuna giren etiketlerden gerçek etiketle uyuşmayanların oranı | AS1 | Raporlanır (karşılaştırmalı) |
| Kıdemli iş yükü | Tek tek incelenen kayıtların tüm geri bildirime oranı | AS1 | Raporlanır |
| İşaretleyici kesinlik / duyarlılık | Hatalı geri bildirimi işaretleme başarısı | H2 | Raporlanır |
| Açıklama tutarlılığı | taban + Σφ − model çıktısı | AC-05 | Mutlak hata ≤ 1e-6 |

**Eşik (τ) seçim kuralı (FR-04):**
1. Doğrulama kümesinde τ ∈ {0,34; 0,35; …; 0,95} taranır.
2. Seçici doğruluğu ≥ 0,80 olan en küçük τ seçilir.
3. Bu τ'da kapsam %50'nin altına düşüyorsa kapsamı %50 yapan τ seçilir ve hedefin tutmadığı raporlanır.

Gerekçe: "İnceleme gerekli" işareti olmayan öneriler analist tarafından çoğunlukla kabul edilecek. Bu önerilerin en az %80'i doğru olmalı. Öte yandan işaretin anlamını yitirmemesi için önerilerin en az yarısı işaretsiz kalmalı. 0,80 değeri bir varsayımdır ve ilk değerlendirme olarak konmuştur; insan çalışmasındaki aşırı güven ölçütüyle (m12) birlikte yeniden değerlendirilir. Demoda τ, E1'in doğrulama sonucuyla bu kurala göre belirlenir.

## 3. Taban çizgiler

1. **Katmanlı rastgele** (`DummyClassifier(strategy="stratified")`) ve **çoğunluk sınıfı**: alt sınır.
2. **E1 lojistik regresyon:** E2'nin taban çizgisi.
3. CGR'nin iç modeli bölge 2'de macro-F1 0,91 ölçmüş [3]. Ancak kimlik ve geçmiş özellikleri kullandığı ve veri dağılımı farklı olduğu için doğrudan karşılaştırılamaz; yalnız bağlam olarak anılır.

## 4. Veri

- Veri sürümü ve dilimler: `docs/data-design.md` §9; ADR-0004 (T1 / T2 / doğrulama / kilitli test = 50/20/15/15).
- E1–E3:
  - Eğitim T1'de yapılır; seçim doğrulamada yapılır.
  - Kilitli test yalnız v1–v2 karşılaştırmasında açılır (FR-20).
  - E1 raporunda kilitli test sonucu verilmez. Gerekçe: sürüm karşılaştırmasından önce test açılmaz; Arp vd. P5.
- E4: v1 = T1; geri bildirim havuzu T2 (gerçek etiketi GUIDE notu kabul edilir); seçim doğrulamada; değerlendirme kilitli testte.
- Sızıntı denetimleri: AC-26 testleri her koşuda çalışır. Ölçekleyici ve sözlük yalnız T1'den öğrenilir.

## 5. Yöntem ve ayarlar

**E1 (bugün):**
- `LogisticRegression` (çok terimli, lbfgs), `C=1.0`, `class_weight="balanced"`, `max_iter=2000`, `StandardScaler`, tohum 42.
- Hiperparametre taraması yok; yalnız C ∈ {0,1; 1; 10} doğrulamada denenir ve seçim kaydedilir.
- Açıklama: doğrusal SHAP (ADR-0003).

**E2:**
- LightGBM; doğrulamada erken durdurma; küçük bir ızgara (num_leaves, learning_rate, min_child_samples).
- Açıklama: `pred_contrib`.
- Özellik setleri: (a) okunur alanlar; (b) okunur alanlar + kimlik alanlarının T1'de öğrenilmiş hedef kodlaması (çapraz katlı); (c) (a) − `LastVerdict` (sızıntı denetimi).

**E4 (AS1) simülasyonu:**
1. Her (gürültü oranı p, gürültü türü, düzen, doğrulayıcı hata oranı e, tohum) için T2'den simüle analist geri bildirimi üretilir:
   - Gerçek etiket olasılık 1 − p ile korunur; p olasılıkla bozulur.
   - Rastgele türde başka bir sınıfa eşit olasılıkla geçer.
   - Sistematik türde bozulan geri bildirimin hepsi "FP" olur ("her şeye yanlış alarm diyen analist").
   - Gerekçe metni şablondan üretilir. Bu bir varsayımdır; bir kısmı insan çalışmasındaki gerçek gerekçelerle sınanır.
2. Ön denetçi (kural ya da LLM) her kaydı işaretler ya da işaretsiz bırakır.
3. Kıdemli düzene göre davranır:
   - Doğrulama yok: hepsi kabul edilir.
   - Tamamı: her kayıt tek tek incelenir.
   - Kural/LLM: işaretliler tek tek incelenir, işaretsizler toplu onaylanır.
   - Tek tek incelemede kıdemli e olasılıkla hata yapar (e ∈ {0; 0,05; 0,10}).
4. Onaylı etiketlerle v2 = T1 + onaylı T2 eğitilir. Kilitli testte macro-F1 ölçülür, sızıntı ve iş yükü hesaplanır.
5. Bütün düzenler aynı başlangıç modelini, aynı tohumları ve aynı kilitli testi kullanır (değişkenler tablosu, "kontrol").

| Sabit | Değer |
|---|---|
| Başlangıç modeli | v1 (E2'de seçilen model türü, okunur alanlar) |
| Tohumlar | {1, 2, 3} (AC-29); bütçe izin verirse 5 |
| Değerlendirme | Kilitli test |

## 6. Ablasyon

| Değişken | Değerler | Neyi sınar |
|---|---|---|
| Özellik seti (E2) | okunur / + kimlik / − LastVerdict | Doğruluk–açıklanabilirlik farkı; LastVerdict sızıntısı |
| C (E1) | 0,1 / 1 / 10 | Düzenlileştirme duyarlılığı |
| Gürültü oranı p (E4) | %0 / 10 / 20 / 30 | H1 |
| Gürültü türü (E4) | rastgele / sistematik | Gerçekçi en kötü durum |
| Doğrulama düzeni (E4) | yok / tamamı / kural / LLM | H1, H2 |
| Doğrulayıcı hata oranı e (E4) | 0 / 0,05 / 0,10 | Hatasız doğrulayıcı varsayımının etkisi |

## 7. Hesaplama bütçesi

- **Donanım:** 16 GB RAM dizüstü, GPU yok.
- **E1:** Veri hattı < 2 dk (DuckDB ile 9,5 M satırın taraması 2026-11-02'de ~5 s sürdü). Eğitim < 1 dk.
- **E4 ızgarası:**
  - Rastgele gürültü: 4 p × 4 düzen × 3 e × 3 tohum = 144 eğitim.
  - Sistematik gürültü: 4 p × 4 düzen × 1 e × 3 tohum = 48 eğitim.
  - LLM düzeni: her p ve tohum için T2 kayıtları LLM'e bir kez gönderilir ve sonuç önbelleğe alınır (maliyet, R3'te belirlenecek).
  - Hedef: tek eğitim ≤ 10 dk, ızgaranın tamamı ≤ 12 saat (NFR-04).
  - Aşarsa önce e düzeyleri {0; 0,10} olarak azaltılır, sonra T2'den katmanlı örneklem alınır; ikisi de raporlanır.

## 8. Tekrar üretilebilirlik

- **Tohumlar:** E1 için 42; E4 için {1, 2, 3}. numpy ve sklearn `random_state` değerleri açıkça verilir.
- **Sürümler:** Her model klasöründe `meta.json` bulunur: veri sürümü, kod sürümü (git commit), Python ve paket sürümleri, ayarlar, tohum, ölçütler.
- **Komut (E1):** `python scripts/build_dataset.py` → `python scripts/train_baseline.py` (çıktı `artifacts/models/<sürüm>/` ve `metrics.json`).

## 9. Sonuçlar

Hepsi doğrulama dilimi (VAL, 77.617 olay) üzerinde. Kilitli test okunmadı. Veri sürümü `c928713f99f4`, model `v1-lr-c92871`, tohum 42. Çıktılar: `artifacts/models/v1-lr-c92871/{metrics.json, meta.json}`.

| Çalıştırma | Ayar | Metrikler (VAL) | Not |
|---|---|---|---|
| E1, LR | C = 0,1 | macro-F1 0,6147; doğruluk 0,6650 | |
| E1, LR | C = 1 | macro-F1 0,6146; doğruluk 0,6649 | |
| E1, LR (seçilen) | C = 10 | macro-F1 **0,6147**; doğruluk 0,6650 | Üç C değeri 4. basamağa kadar aynı; düzenlileştirme duyarlılığı yok denecek kadar küçük (n = 258.721, d = 60) |
| Katmanlı rastgele | `DummyClassifier(stratified)` | macro-F1 0,3227; doğruluk 0,3487 | Alt sınır |
| Çoğunluk sınıfı | `DummyClassifier(most_frequent)` | macro-F1 0,1796; doğruluk 0,3688 | Alt sınır |

**Sınıf bazlı (seçilen model, VAL):**

| Sınıf | Kesinlik | Duyarlılık | F1 | Destek |
|---|---|---|---|---|
| TP | 0,336 | 0,463 | 0,390 | 12.099 |
| BP | 0,624 | 0,746 | 0,680 | 28.628 |
| FP | 0,921 | 0,668 | 0,775 | 36.890 |

Karışıklık matrisi (satır gerçek, sütun tahmin; TP/BP/FP): `[[5598, 5740, 761], [5928, 21356, 1344], [5119, 7112, 24659]]`.

**Eşik (E3'ün ilk değeri, demo için):** §2 kuralıyla τ = **0,54** seçildi. Bu τ'da kapsam %54,9, seçici doğruluk 0,813; hedef tuttu. Tarama örnekleri: τ = 0,50 → kapsam %71,2, doğruluk 0,702; τ = 0,60 → %45,7, 0,847; τ = 0,70 → %35,3, 0,919.

**Değerlendirme:**
- E1 hipotezi destekleniyor: macro-F1 farkı 0,6147 − 0,3227 = **0,292 ≥ 0,10**.
- Zayıf nokta TP sınıfı (F1 0,39): gerçek tehditlerin yarısından fazlası BP ya da FP tahmin ediliyor. SOC için en pahalı hata bu; E2'de (LightGBM, kimlik özellikleri) ilk bakılacak yer.
- T1'de macro-F1 0,593, VAL'de 0,615. Fark aşırı öğrenmeyi değil dağılım kaymasını gösteriyor: VAL'de FP oranı %47,5 (T1'de %28,9) ve model FP'de en iyi sınıfında.
- Tekrar üretilebilirlik (NFR-13): aynı ayarla iki koşunun `metrics.json` dosyası aynı.
- Kaynak (NFR-03): tepe çalışma kümesi veri hattında 3,68 GB, eğitimde 0,91 GB; eğitim 14,6 sn (üç C).

**Hedef değişiklikleri:** Yok.
