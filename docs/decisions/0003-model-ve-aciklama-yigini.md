# ADR-0003: Taban model lojistik regresyon, ana model LightGBM; SHAP yerleşik ve kapalı form; Python 3.11 sanal ortamı

- **Durum:** Kabul edildi (2026-11-02)
- **Kaynak:** Kullanıcının faz 3 seçimi. Uyum bilgisi R2 kontrolünden (PyPI, 2026-11-02).

## Bağlam

- FR-05 / AC-05: SHAP katkıları ham alana bağlı olmalı ve taban değer ile katkıların toplamı model çıktısına eşit olmalı.
- FR-27: 5. haftada en basit karşılaştırma modeli; FR-28: 9–10. haftada ana sınıflandırıcı.
- R2 bulgusu: `shap` ≥ 0.52 ve `xgboost` ≥ 3.3 Python ≥ 3.12 istiyor. Kurulu Python 3.11.9. Python 3.11'i destekleyen son sürümler shap 0.51.0 ve xgboost 3.2.0. LightGBM 4.7.0 Python 3.11'i destekliyor ve `predict(pred_contrib=True)` ile TreeSHAP katkılarını kendisi üretiyor.
- Kurulu paketler: numpy 2.4.6, pandas 3.0.3, scikit-learn 1.9.0, duckdb 1.5.3, pyarrow 24.0.0.

## Değerlendirilen seçenekler

1. **Lojistik regresyon + LightGBM; SHAP yerleşik ya da kapalı form; Python 3.11 venv** (seçildi): Yalnız `lightgbm` eklenir. Doğrusal modelde, özellikler bağımsız varsayılırsa SHAP kesin ve kapalı formdur: φ_kj = β_kj · (x_j − E[x_j]). LightGBM'de kesin TreeSHAP kullanılır. Eksisi: shap'in hazır grafikleri yok, ama arayüz grafiği zaten kendimiz çiziyoruz.
2. **shap 0.51 kütüphanesi:** Standart API. Eski sürüme sabitlenir ve pandas 3.0 uyumu doğrulanmadı.
3. **Python 3.12+ ve güncel shap/xgboost:** Yeni yorumlayıcı kurulumu gerekir; bugün buna ihtiyaç yok.

## Karar

- **Taban model (FR-27):** scikit-learn `LogisticRegression` (çok terimli), standartlaştırılmış özellikler.
  - Açıklama, önerilen sınıf k'nin logit'i için doğrusal SHAP'tir: `φ_j = β_kj · (z_j − mean_train(z_j))`. Burada z ölçeklenmiş özelliktir.
  - Taban değer `β_k0 + Σ_j β_kj · mean_train(z_j)` olur.
  - Arayüzde z yerine ham alan değeri gösterilir.
- **Ana model (FR-28):** LightGBM `LGBMClassifier`. Açıklama `pred_contrib=True` ile alınır (sınıf başına katkılar + taban değer, ham skor ölçeğinde).
- **Demo** taban modelle çalışır.
- **Ortam:** Proje kökünde Python 3.11 sanal ortamı (`.venv`). Sürümler `requirements.txt` dosyasında sabitlenir (NFR-13).
- shap kütüphanesi kullanılmaz. Toplam eşitliği (AC-05) testle doğrulanır.

## Sonuçlar

- **Olumlu:** Tek yeni bağımlılık var. Açıklama iki modelde de kesin. Python 3.11'de kalınıyor.
- **Olumsuz / riskler:**
  - Doğrusal SHAP özelliklerin bağımsız olduğunu varsayar; bu sınırlılık olarak yazılır.
  - shap'in KernelExplainer gibi modelden bağımsız açıklayıcıları yok.
  - İleride gerekirse Python 3.12'ye geçiş ayrı bir ADR olur.

## İzlenebilirlik

- **Gereksinim:** FR-05, FR-27, FR-28, NFR-13
- **Bağlantılı:** ADR-0001
