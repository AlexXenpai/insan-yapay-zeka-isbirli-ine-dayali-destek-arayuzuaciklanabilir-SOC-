# İnsan-Yapay Zekâ İşbirliğine Dayalı Açıklanabilir SOC Karar Destek Arayüzü

Bitirme projesi, Grup 7: Ali İhsan Dağaşan, Mehmet Emin Duran. Danışman: Prof. Dr. İbrahim Arpacı.

**Grup odak noktası:** SOC analistinin model önerisini kabul, ret veya düzeltme yoluyla değerlendirdiği karar destek arayüzü (insan geri bildirimi, *human-in-the-loop*, HITL).

Planlama belgeleri `docs/` altında; başlangıç noktası `docs/proje-plani.md`.

## Kurulum (Windows, Python 3.11)

```powershell
py -3.11 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m pip install -e .
```

Veri: GUIDE (Microsoft, Kaggle v2) dosyaları `data/raw/guide/` altına konur (`GUIDE_Train.csv`). `data/` ve `artifacts/` git'e girmez.

## Çalıştırma

Aşağıdaki adımlar görev planındaki sırayla eklenir (`docs/plans/2026-11-02-hafta-1-5-ciktilari-ve-demo.md`).

```powershell
.venv\Scripts\python scripts\build_dataset.py     # olay tablosu, dört dilim, özellikler
.venv\Scripts\python scripts\train_baseline.py    # taban model, SHAP, eşik
.venv\Scripts\python scripts\fetch_mitre.py       # MITRE ATT&CK teknik adları
.venv\Scripts\python scripts\seed_demo.py         # demo deposu: 300 olay, öneriler, kullanıcılar
.venv\Scripts\python -m socxai.api                # http://127.0.0.1:8000
```

- `seed_demo.py` var olan `app.db`'yi silmez (denetim izi). Yeniden tohumlamak için `--reset`: eski dosya `app.db.bak-<UTC>` adıyla saklanır.
- Demo kullanıcıları: `analist1`, `analist2` (Analist), `kidemli1` (Kıdemli), `modelci1` (Model sorumlusu). Arayüzün sağ üstünden seçilir; kimlik yalnız yerel demo içindir.
- `fetch_mitre.py` bir kez çalışır (~50 MB indirme). Dosya yoksa kartta yalnız teknik kodu görünür.

Demo senaryosu ve ölçümler (`app.db`'nin geçici kopyasında koşar, gerçek denetim izine yazmaz):

```powershell
.venv\Scripts\python scripts\demo_scenario.py                                  # aç → kabul → düzelt + gerekçe → geçmiş
.venv\Scripts\python scripts\measure.py latency                                # NFR-01, NFR-02 (p95)
.venv\Scripts\python scripts\measure.py memory scripts\build_dataset.py        # NFR-03 (tepe bellek)
```

## Testler

```powershell
.venv\Scripts\python -m pytest -q                 # birim + entegrasyon
.venv\Scripts\python -m pytest -q -m realdata     # gerçek GUIDE verisiyle (yavaş)
```

Windows'ta `%TEMP%\pytest-of-<kullanıcı>` klasörü izin hatası verirse: `pytest --basetemp=<yazılabilir klasör>`.

## Yapılandırma

Yollar `SOCXAI_*` ortam değişkenleriyle ezilir: `SOCXAI_DATA_DIR`, `SOCXAI_RAW_GUIDE_DIR`, `SOCXAI_PROCESSED_DIR`, `SOCXAI_REFERENCE_DIR`, `SOCXAI_APP_DIR`, `SOCXAI_MODELS_DIR`, `SOCXAI_WEB_DIR`, `SOCXAI_HOST`, `SOCXAI_PORT`. Gizli bilgiler yalnız ortam değişkeninde ya da git'e girmeyen `.env` dosyasında tutulur.

## Veri ve atıflar

- GUIDE: Microsoft, Kaggle Version 2, CDLA-Permissive-2.0. Freitas vd., *WWW Companion 2025*, doi:10.1145/3701716.3715209.
- MITRE ATT&CK®, The MITRE Corporation (`data/reference/mitre_techniques.csv`, kaynak: `github.com/mitre/cti`).
