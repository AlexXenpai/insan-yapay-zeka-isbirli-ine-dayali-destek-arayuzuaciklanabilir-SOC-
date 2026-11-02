# Görev planı: 1–5. hafta çıktıları ve küçük çalışan demo

- **Tarih:** 2026-11-02
- **İz:** Tam
- **Durum:** Uygulandı (2026-11-03); G1–G9 tamam, MITRE adları indirme bekliyor (S-15)

## 1. Süreç uyarlaması

- **İstek:** Hoca görüşmesine (2026-11-03) kadar yol haritası s.2-3'teki 1–5. hafta çıktılarının hepsi hazır olsun ve küçük, çalışan bir demo gösterilsin: tek olay için model önerisi + SHAP → analistin düzeltmesi + gerekçe → önceki karar görünür.
- **Bağlam:** Bitirme projesi (Grup 7; Ali İhsan Dağaşan, Mehmet Emin Duran; danışman Prof. Dr. İbrahim Arpacı). Süre bir gün. Donanım: 16 GB RAM dizüstü. Veri: GUIDE (Kaggle v2) `data/raw/guide/` altında, denetlendi.
- **Artefaktlar** (hafta listesine tam eşleşen set):
  - `docs/srs.md`: problem, hedef kullanıcı, sınırlar, kullanıcı hikâyeleri + kabul testleri, NFR (performans, güvenlik, kullanılabilirlik, kaynak), veri kaynağı/lisans/araçlar ve gerekçeleri, B planı, görev dağılımı (1–2. hafta)
  - `docs/research/2026-11-02-kaynak-karsilastirmasi.md`: ≥5 kaynağın yöntem/veri/ölçüt/sınırlılık karşılaştırması (1–2. hafta)
  - `docs/architecture.md`: bileşen ve veri akışı (roller, güven sınırları, hata durumları), ekran taslakları (3–4. hafta)
  - `docs/data-design.md`: veri şeması (geri bildirim kaydı ve eğitim etiketi deposu ayrı), olay bazlı sızıntısız bölme (3–4. hafta)
  - `docs/experiments/2026-11-02-temel-model-ve-as1.md`: deney planı; eşik ve kabul ölçütleri gerekçeli (3–4. hafta)
  - `docs/test-plan.md` (3–4. hafta)
  - `docs/risk-register.md`
  - `docs/traceability.md`
  - `docs/proje-plani.md`: görev dağılımı, sorumlu, hafta, kanıt; haftalık not; görüşme düzeni (Adım 1.4)
  - `docs/decisions/`: ADR'ler
  - Bu görev planı
  - Kod: proje iskeleti, veri okuma, en basit karşılaştırma modeli, demo (5. hafta)
- **Biçim:** Markdown, `docs/` altında; görüşme belgesinin 4. bölümüne dosya yolları yazılır.
- **Test yaklaşımı:** Bu iş için önce kod, sonra test (süre kısıtı; kullanıcının istisnası). Projenin olağan yaklaşımı TDD; görüşmeden sonraki işlerde TDD'ye dönülür ve demo kodunun testleri tamamlanır.
- **Fırsat taraması:** Yapılmadı. İleri bileşenler (kendi eğitilen model, SHAP, LLM ön denetçisi, AS1 simülasyonu) 4–7. oturumlarda karara bağlandı (`docs/STATUS.md`).

## 2. Dokunulan dokümanlar

| Doküman | Değişiklik |
|---|---|
| docs/srs.md | Oluşturuldu ve onaylandı (2026-11-02): FR-01–FR-34, NFR-01–NFR-15, AC-01–AC-34. Tutarlılık düzeltmeleri: FR-01 demo sütunu, FR-26 dört dilim, §7 araçlar |
| docs/research/2026-11-02-kaynak-karsilastirmasi.md | Oluşturuldu (R1) |
| docs/decisions/0001–0005 | Oluşturuldu |
| docs/architecture.md, docs/data-design.md, docs/test-plan.md, docs/risk-register.md, docs/traceability.md, docs/proje-plani.md | Oluşturuldu |
| docs/experiments/2026-11-02-temel-model-ve-as1.md | Oluşturuldu; §9 E1 sonuçları G4'te doldurulacak |

## 3. Kararlar

- 2026-11-02 (kullanıcı): İz Tam; hafta listesine eşleşen belge seti; biçim Markdown `docs/`; test önce kod sonra test (yalnız bu iş için).
- 2026-11-02 (kullanıcı): SRS tüm sistemi kapsar, demo alt kümesi işaretli. Demo = MVP dilimi (öneri + SHAP → kabul/düzelt/ret + gerekçe → sürümlü karar, önceki görünür). Demo mükemmel olmak zorunda değil.
- 2026-11-02 (kullanıcı): Kimlik doğrulama: yetki sunucuda (Must), yerel hesap (Should, 7–8. hafta); demoda hazır kullanıcı seçimi.
- 2026-11-02 (kullanıcı): Ret'te gerekçe zorunlu; tekrar karar denetim izine yazılır, yeni sürüm/doğrulama işi açmaz.
- 2026-11-02 (kullanıcı): Araştırma R1 + R2 şimdi; R3 (LLM sağlayıcısı) 9–10. haftaya.
- ADR-0001 mimari, ADR-0002 depolama (3 SQLite dosyası), ADR-0003 model ve açıklama yığını, ADR-0004 dört dilimli bölme 50/20/15/15, ADR-0005 yalnız okunur özellikler. K2 şimdilik olduğu gibi.
- 2026-11-02 (kullanıcı): Görev paketleri eşit ağırlıkta. **Paket A — Mehmet Emin Duran:** veri hattı ve bölme, depolar (denetim izi + eğitim etiketi deposu), vaka kartı dönüştürücü, karşılaştırma ve ana model + SHAP, yeniden eğitim ve sürüm karşılaştırması, AS1 simülasyonu, AS2 raporu. **Paket B — Ali İhsan Dağaşan:** arayüz, API ve karar akışı (K3), roller ve kimlik doğrulama, ön denetçi (kural + LLM), AS3 insan çalışması. Herkes kendi modülünün testlerini ve rapor bölümünü yazar, diğeri gözden geçirir. Bugünkü (2026-11-02) işleri Mehmet Emin tek başına yapıyor; dağılım sonraki haftalar için.

### Küçük karar listesi (onay 2026-11-02)

1. Paket adı `socxai`, `src/` düzeni, editable kurulum.
2. Demo kullanıcıları: `analist1`, `analist2` (Analist), `kidemli1` (Kıdemli), `modelci1` (Model sorumlusu).
3. Demo havuzu: T2'den 300 olay, kategoriye göre orantılı; en az 30 düşük güvenli, en az 30 modelin yanlış önerdiği olay. Seçimde GUIDE notu kullanılır, arayüzde gösterilmez. Tohum 42.
4. Olay kategorisi: uyarıların en sık kategorisi; eşitlikte alfabetik ilk.
5. Nöbetçi değer: bir kimlik alanının T1'deki en sık değeri; kartta gösterilmez.
6. Sözlük: 15 varlık türü, 7 `Roles` değeri, 20 MITRE tekniği (60 özellik).
7. Taban model: C ∈ {0,1; 1; 10}, tohum 42, `class_weight="balanced"`.
8. Model sürüm adı: `v1-lr-<veri sürümünün ilk 6 karakteri>`.
9. Gerekçe kırpılır, en çok 2.000 karakter.
10. Hata gövdesi `{"error", "message"}`; kodlar İngilizce, iletiler Türkçe.
11. Günlük: Python `logging`, INFO, konsola düz metin.
12. Test düzeni: `tests/unit`, `tests/integration`; gerçek veri testleri `-m realdata`.
13. Sunucu `127.0.0.1:8000`.
14. Arayüz: TP "Gerçek tehdit", BP "Zararsız-beklenen", FP "Yanlış alarm"; zaman yerel saatle `YYYY-MM-DD HH:mm`.
- 2026-11-02 (kullanıcı): MITRE adları resmî ATT&CK verisinden (ADR-0006); G5'e eklendi.

## 4. Görevler

Sıra bağımlılığa göredir. Bütün komutlar proje kökünde çalıştırılır; `PY` = `.venv/Scripts/python`. Yeni klasör yapısı:

```
tasarım/
  pyproject.toml  requirements.txt  README.md  .gitignore
  src/socxai/  __init__.py  config.py  decisions.py  auth.py
               data/ (guide.py, features.py, cards.py, mitre.py)
               model/ (baseline.py, explain.py, registry.py)
               store/ (db.py, suggestions.py, schema_app.sql, schema_labels.sql, schema_participants.sql)
               api/ (app.py, __main__.py)
  web/  index.html  incident.html  app.js  styles.css
  scripts/  build_dataset.py  train_baseline.py  seed_demo.py  demo_scenario.py  measure.py
  tests/  conftest.py  fixtures/guide_mini.csv  unit/  integration/
  data/raw/guide/ (var)  data/processed/  data/reference/  data/app/   (git dışı)
  artifacts/models/   (git dışı)
  docs/ (var)
```

### Görev G1: Proje iskeleti ve ortam

- **Gereksinimler:** NFR-07, NFR-13, NFR-14
- **Dosyalar:** oluştur `.gitignore` (data/, artifacts/, .venv/, *.db, .env, __pycache__), `pyproject.toml` (setuptools, src düzeni, paket `socxai`), `requirements.txt` (genel ortamda kurulu sürümlere sabitlenmiş: numpy, pandas, pyarrow, duckdb, scikit-learn, joblib, fastapi, uvicorn, pydantic, httpx, pytest), `README.md` (kurulum ve çalıştırma), `src/socxai/__init__.py`, `src/socxai/config.py`, `tests/conftest.py`, `tests/unit/test_smoke.py`
- **İşlemler:** `git init`; `py -3.11 -m venv .venv`; `PY -m pip install -r requirements.txt`; `PY -m pip install -e .`
- **Arayüzler:** sunar `socxai.config`: `CLASSES = ("TP","BP","FP")`, `CATEGORIES = ("InitialAccess","SuspiciousActivity","Exfiltration")`, `SPLIT_RATIOS = (0.50, 0.20, 0.15, 0.15)`, `SLICES = ("T1","T2","VAL","TEST")`, `Settings` (yollar; `SOCXAI_*` ortam değişkenleriyle ezilir)
- **Testler:** içe aktarma duman testi
- **Doğrulama:** `PY -m pytest -q` → `1 passed`; `git status` → depo kurulu, `data/` izlenmiyor
- [x] Tamamlandı (2026-11-02): `PY -m pytest -q --basetemp=<scratchpad>` → `1 passed`; `git check-ignore` → `data/` ve `.venv/` izlenmiyor; `pip list` → socxai 0.1.0 editable

### Görev G2: Veri hattı ve bölme (FR-26)

- **Gereksinimler:** FR-26, NFR-03
- **Dosyalar:** oluştur `src/socxai/data/guide.py`, `scripts/build_dataset.py`, `tests/fixtures/guide_mini.csv` (GUIDE sütunları; 3 kategoride ~40 olay; çok kategorili, etiketsiz ve kapsam dışı örnekler), `tests/integration/test_guide_pipeline.py`
- **Arayüzler:** sunar `build_incidents(raw_csv: Path, out_root: Path, ratios=SPLIT_RATIOS) -> Manifest`. Yazdıkları:
  - `data/processed/<dv>/incidents.parquet`: incident_key, org_id, incident_id, category, grade, first_seen, n_alerts, n_evidence, slice
  - `evidence.parquet`: kapsam içi satırlar; özellik ve kart için gerekli sütunlar
  - `manifest.json`: data_version, parametreler, dilim × sınıf sayıları, dilim zaman aralıkları
  - Kurallar `docs/data-design.md` §9.2–9.3 ve §9.7'de.
- **Testler:** TC-01 (fixture üzerinde; gerçek veri üzerinde `-m realdata` işaretli)
- **Doğrulama:** `PY scripts/build_dataset.py` → manifest özeti (4 dilim, oranlar ~50/20/15/15); `PY -m pytest tests/integration/test_guide_pipeline.py -q` → geçer
- [x] Tamamlandı (2026-11-02): `PY scripts/build_dataset.py` → veri sürümü `c928713f99f4`, 517.442 olay; T1 258.721 / T2 103.488 / VAL 77.617 / TEST 77.616 (50,00/20,00/15,00/15,00 %); 5 sızıntı denetimi True; 10,9 sn. `pytest tests/integration/test_guide_pipeline.py` → 15 passed (gerçek veri testi dahil)

### Görev G3: Özellikler (ADR-0005)

- **Gereksinimler:** FR-26, FR-05 (alan eşlemesi), NFR-03
- **Dosyalar:** oluştur `src/socxai/data/features.py`, `tests/unit/test_features.py`; değiştir `scripts/build_dataset.py` (özellikleri de üretir)
- **Arayüzler:**
  - `fit_vocab(con, slice="T1") -> Vocab`: en sık 15 varlık türü, 7 `Roles` değeri, 20 MITRE tekniği; `Vocab.to_json()` ve `from_json()`
  - `build_features(con, vocab, slice) -> pd.DataFrame`: dizin incident_key, 60 float32 sütun; data-design §9.4
  - `FEATURE_SOURCES: dict[str, tuple[str, str | None]]`: özellik → (ham alan, değer)
  - Çıktılar: `features_<dilim>.parquet`, `vocab.json`
- **Testler:** TC-02; TC-24 (tepe bellek; Windows `GetProcessMemoryInfo`, `scripts/measure.py memory`)
- **Doğrulama:** `PY -m pytest tests/unit/test_features.py -q` → geçer; `features_T1.parquet` 60 sütun
- [x] Tamamlandı (2026-11-02): `pytest tests/unit/test_features.py` → 8 passed; `features_T1.parquet` (258.721 × 60, float32); TC-24 `PY scripts/measure.py memory scripts/build_dataset.py` → tepe çalışma kümesi 3,68 GB ≤ 6 GB, OK

### Görev G4: Taban model, açıklama, eşik (E1)

- **Gereksinimler:** FR-27, FR-05, FR-04, NFR-13, NFR-15
- **Dosyalar:** oluştur `src/socxai/model/baseline.py`, `src/socxai/model/explain.py`, `src/socxai/model/registry.py`, `scripts/train_baseline.py`, `tests/unit/test_explain.py`, `tests/unit/test_threshold.py`; değiştir `docs/experiments/2026-11-02-temel-model-ve-as1.md` §9
- **Arayüzler:**
  - `train(X, y, C, seed) -> BaselineModel` (StandardScaler + LogisticRegression; `predict_proba`, `classes_`, `feature_names`)
  - `evaluate(model, X, y) -> dict` (macro-F1, doğruluk, sınıf bazlı P/R/F1, karışıklık matrisi)
  - `choose_threshold(proba, y, target_acc=0.80, min_coverage=0.50) -> (tau, info)` (deney planı §2)
  - `explain_linear(model, x_raw_row, raw_values) -> Explanation` (dict; mimari §6)
  - `registry.save(model, meta, root) -> version` (`v1-lr-<dv[:6]>`), `registry.load(version, root)`
  - Kilitli test bu görevde okunmaz.
- **Testler:** TC-03, TC-04, TC-05, TC-21
- **Doğrulama:** `PY scripts/train_baseline.py` → doğrulamada taban model ve katmanlı rastgele için macro-F1, seçilen C ve τ; `artifacts/models/<v>/metrics.json` ve `meta.json` var; `PY -m pytest tests/unit -q` → geçer
- [x] Tamamlandı (2026-11-02): `PY scripts/train_baseline.py` → `v1-lr-c92871`, VAL macro-F1 0,6147 (katmanlı rastgele 0,3227; fark 0,292), C = 10, τ = 0,54 (kapsam %54,9, seçici doğruluk 0,813); `metrics.json` + `meta.json` var; iki koşu aynı; `PY -m pytest -q` → 36 passed

### Görev G5: Depolar, vaka kartı, demo havuzu ve öneriler

- **Gereksinimler:** FR-02, FR-03, FR-04, FR-09 (şema), NFR-06, NFR-01
- **Dosyalar:** oluştur
  - `src/socxai/store/schema_app.sql`, `schema_labels.sql`, `schema_participants.sql` (data-design §2; tetikleyiciler; `v_effective_decision`)
  - `src/socxai/store/db.py`
  - `src/socxai/data/mitre.py`, `src/socxai/data/cards.py`
  - `scripts/fetch_mitre.py` (ADR-0006: mitre/cti `enterprise-attack.json` indirilir → `data/reference/mitre_techniques.csv`)
  - `src/socxai/store/suggestions.py`
  - `scripts/seed_demo.py`
  - `tests/integration/test_store.py`, `tests/unit/test_cards.py`
- **Arayüzler:**
  - `connect(path) -> sqlite3.Connection` (WAL, foreign_keys=ON, Row)
  - `migrate(conn, kind)`
  - `load_mitre_names(path) -> dict[str, str]` (dosya yoksa boş sözlük)
  - `build_cards(con, keys, sentinels, aliases) -> dict[str, dict]`
  - `score_pool(app_conn, model, version, X, raw)`
  - `seed_demo(n=300, seed=42)`: kullanıcılar, etkin model sürümü, T2'den 300 olay (kategoriye göre katmanlı; en az 30 "inceleme gerekli" ve en az 30 modelin yanlış önerdiği olay), kartlar, öneriler
- **Testler:** TC-13, TC-16, TC-17 (çekirdek kısmı)
- **Doğrulama:** `PY scripts/seed_demo.py` → `data/app/app.db`: 300 olay, 300 öneri, 4 kullanıcı; `PY -m pytest tests/integration/test_store.py tests/unit/test_cards.py -q` → geçer
- [x] Tamamlandı (2026-11-03): `PY scripts/seed_demo.py` → 300 olay (InitialAccess 163, SuspiciousActivity 81, Exfiltration 56), 300 öneri, 4 kullanıcı, 1.816 takma ad; 198 "inceleme gerekli", 118 yanlış öneri; `pytest tests/integration/test_store.py tests/unit/test_cards.py` → 23 passed

### Görev G6: Karar servisi (K3)

- **Gereksinimler:** FR-06, FR-07, FR-08, FR-09, FR-10, FR-11, FR-22, NFR-02
- **Dosyalar:** oluştur `src/socxai/decisions.py`, `tests/integration/test_decisions.py`
- **Arayüzler:**
  - `DecisionCommand(incident_key, decision_type, decided_class, reason, opened_at, actor_user_id, actor_role)`
  - `record_decision(conn, cmd) -> DecisionEvent`: `DecisionError(code)` fırlatır; kodlar mimari §6'da; işlem data-design §5'teki gibi
  - `effective(conn, key) -> DecisionEvent | None`
  - `history(conn, key) -> list[DecisionEvent]`
  - `status(conn, key) -> Literal["pending", "decided", "review"]`
- **Testler:** TC-06–TC-12, TC-19, TC-20
- **Doğrulama:** `PY -m pytest tests/integration/test_decisions.py -q` → geçer
- [x] Tamamlandı (2026-11-03): `pytest tests/integration/test_decisions.py` → 25 passed (TC-06–TC-12, TC-19 iki iş parçacığı, TC-20)

### Görev G7: API ve rol yetkisi

- **Gereksinimler:** FR-23 (demo), FR-03, FR-10, NFR-05
- **Dosyalar:** oluştur `src/socxai/auth.py`, `src/socxai/api/app.py`, `src/socxai/api/__main__.py`, `tests/integration/test_api.py`
- **Arayüzler:**
  - `PERMISSIONS: dict[str, frozenset[str]]` (mimari §7)
  - `get_current_user` (X-User başlığı → users)
  - `require(perm)`: FastAPI bağımlılığı; 403'te `system_events`'e kayıt
  - `create_app(settings) -> FastAPI`: mimari §6'nın 5. hafta satırları; `/` altında `web/` statik
  - `python -m socxai.api` → 127.0.0.1:8000
- **Testler:** TC-14, TC-15, TC-17
- **Doğrulama:** `PY -m pytest tests/integration/test_api.py -q` → geçer; `curl -H "X-User: analist1" localhost:8000/api/incidents` → 200 ve JSON
- [x] Tamamlandı (2026-11-03): `pytest tests/integration/test_api.py` → 21 passed (TC-14, TC-15, TC-17); `python -m socxai.api` + `curl -H "X-User: analist1" 127.0.0.1:8000/api/incidents?status=pending` → 200 ve JSON; başlıksız istek → 401 `unauthenticated`

### Görev G8: Demo arayüzü (S1, S2)

- **Gereksinimler:** FR-01 (basit), FR-02–FR-10, FR-25
- **Dosyalar:** oluştur `web/index.html`, `web/incident.html`, `web/app.js`, `web/styles.css`, `scripts/demo_scenario.py`
- **Arayüzler:** yalnız mimari §6 uç noktalarını kullanır; bütün metin `textContent` ile basılır; ekranlar mimari §11 S1 ve S2'deki gibi
- **Testler:** TC-18, TC-25
- **Doğrulama:** `PY scripts/demo_scenario.py` → olay aç → kabul → düzeltme + gerekçe → geçmişte iki sürüm, "OK"; tarayıcıda S1 → S2 akışı elle denenir ve ekran görüntüsü alınır
- [x] Tamamlandı (2026-11-03): `PY scripts/demo_scenario.py` → 4 adım + "OK" (app.db kopyasında); Chrome'da S1 kuyruk → S2 olay → Kabul (v1) → Düzelt + gerekçe (v2) → geçmişte v2, v1 (scratchpad kopyası üzerinde çalışan sunucu; konsol hatası yok; ekran görüntüleri alındı); TC-18 `tests/unit/test_no_external_calls.py` → 3 passed

### Görev G9: Ölçümler, doğrulama ve belgelerin kapanışı

- **Gereksinimler:** NFR-01, NFR-02, NFR-03, NFR-07
- **Dosyalar:** değiştir `scripts/measure.py` (gecikme), `docs/traceability.md`, `docs/test-plan.md` (durumlar), `docs/experiments/...` §9, `docs/STATUS.md`; görüşme belgesinin 4. bölümü (Claude Docs; kutular ve dosya yolları)
- **Testler:** TC-22, TC-23, TC-24, TC-26; bütün test takımı
- **Doğrulama:** `PY scripts/measure.py latency` → p95 değerleri hedef altında; `PY -m pytest -q` → hepsi geçer; gizli bilgi taraması 0 bulgu
- [x] Tamamlandı (2026-11-03): `PY scripts/measure.py latency` → olay açma p95 4,6 ms, karar p95 8,4 ms (OK); `PY -m pytest -q` → 106 passed; TC-26 `tests/unit/test_secrets.py` → 0 bulgu; izlenebilirlik (20 doğrulandı, 4 kısmi), test planı §6.1, deney planı §9, README, görüşme belgesi 4. bölüm (rev 54, 11 kutu + dosya yolları) güncellendi

## 5. Testler

Ayrıntılı senaryolar: `docs/test-plan.md` §6. Bu işte koşulacaklar TC-01–TC-26. Yaklaşım: önce kod, sonra test; her görev kendi testleriyle kapanır.

## 6. Riskler

| ID | Risk | Olasılık | Etki | Tetik | Azaltma |
|---|---|---|---|---|---|
| P-01 | MITRE indirmesi başarısız olur | Düşük | Düşük | `fetch_mitre.py` hatası | ADR-0006: yalnız kod gösterilir; indirme sonra yeniden denenir |
| P-02 | Taban modelin macro-F1 değeri E1 hedefinin altında | Orta | Orta | `train_baseline.py` çıktısı | Sonuç olduğu gibi raporlanır (R-02); demo yine çalışır |
| P-03 | `.venv` kurulumunda paket indirme sorunu | Düşük | Orta | pip hatası | Genel ortamdaki kurulu sürümlere sabitlenir; gerekirse `--system-site-packages` |
| P-04 | Gün içinde bitmeme | Orta | Orta | G6 öğleden sonra hâlâ açık | Öncelik sırası G1→G8; G9'daki ölçümler demodan sonra da yapılabilir |
| P-05 | Kart verisi (evidence.parquet) büyük çıkar | Düşük | Düşük | Dosya > 1 GB | Yalnız gerekli sütunlar tutulur; kart yalnız demo havuzu için üretilir |

## 7. İzlenebilirlik

Proje düzeyinde: `docs/traceability.md`. Bu işin görevleri G1–G9 orada eşlenmiştir.

## 8. Tutarlılık kontrolü

Builder check alt ajanı çalıştırılmadı. Kullanım kotası yüzünden alt ajanlar yalnız sorarak kullanılıyor (kullanıcı tercihi). Kontrol satır içinde yapıldı.

| ID | Tür | Önem | Yer | Bulgu | Çözüm |
|---|---|---|---|---|---|
| C-01 | Çelişki | Yüksek | SRS §7 | "Araçlar faz 3'te belirlenecek" yazıyordu; ADR'ler yazıldı | Düzeltildi: araç tablosu eklendi |
| C-02 | Çelişki | Orta | SRS FR-26 | Üç dilim yazıyordu; ADR-0004 dört dilim | Düzeltildi |
| C-03 | Kapsama | Düşük | SRS FR-01 | Demoda basit liste var, ama sütun "—" idi | Düzeltildi: "kısmi" |
| C-04 | Belirsizlik | Orta | NFR-08 | "Belgelenmiş alan listesi" henüz yok | Ertelendi: R3 ile 9–10. haftada (SRS açık soru 3) |
| C-05 | Eksik belirtim | Orta | FR-02 | MITRE adlarının kaynağı tanımsızdı | Çözüldü: ADR-0006 |
| C-06 | Kapsama | Düşük | K4 → izin matrisi | Kıdemli analistin olağan karar veremeyeceği K4'ten türetildi ("analist karar verir; kıdemli onaylar") | K4 ile çözülmüş; matriste açık (mimari §7) |
| C-07 | Terim | Düşük | Belgeler | "Kilitli test" ve "sabit test kümesi" aynı kavram | Sözlükte "kilitli test kümesi"; s.10 alıntılarında "sabit" korunur |

## 9. Önerilen commit noktaları

1. G1 sonrası: iskelet ve bütün planlama belgeleri (`docs/`)
2. G2–G4 sonrası: veri hattı ve taban model
3. G5–G7 sonrası: depolar, karar servisi, API
4. G8–G9 sonrası: demo arayüzü, ölçümler, belge güncellemeleri

## 10. Onay

2026-11-02: Kullanıcı planı, 14 maddelik küçük karar listesini ve ADR-0006'yı onayladı. Seçilen seçenek: **Temiz oturumda uygula** (faz 5, G1'den başlanır).

## 11. Sapmalar

- **S-01 (G1, küçük):** `socxai.config` plandaki sabitlere ek olarak `TARGET_ACCURACY = 0.80`, `MIN_COVERAGE = 0.50` (deney planı §2) ve `MAX_REASON_CHARS = 2000` (karar 9) içerir; mimari §4 `config` satırındaki "eşik" maddesini karşılar.
- **S-02 (G1, ortam):** `%TEMP%\pytest-of-Mehmet Emin` klasörünün izinleri bozuk (2026-06-04'ten kalma), pytest `tmp_path` oluşturamıyor. Doğrulamalar `--basetemp` ile scratchpad'de koşuldu. Kalıcı çözüm: kullanıcı o klasörü silebilir. Proje yapılandırması değiştirilmedi.
- **S-03 (G2, küçük):** Fixture `tests/fixtures/guide_mini.csv`, tohumlu üretici `tests/fixtures/make_guide_mini.py` ile üretilir (176 satır; 40 kapsam içi olay, çok kategorili, kısmen/tamamen etiketsiz, kapsam dışı ve zaman eşitliği örnekleri). Üretici de depoya girer.
- **S-04 (G2, küçük):** Veri sürümüne giren "özellik sözlüğü" (§9.7), sözlüğün kendisi değil boyutlarıdır (`config.VOCAB_SIZES`); sözlük T1'den öğrenildiği için bölmeden önce bilinemez ve bölme + boyutlar onu belirler. Ayrıca `config.PIPELINE_VERSION` eklendi.
- **S-05 (G2, küçük):** Etiket kuralı: `IncidentGrade` boş satırlar atılır, olay kalan satırlarıyla tutulur; hiç etiketli satırı olmayan olay kapsam dışıdır. Bir olayda birden çok etiket, okunamayan zaman damgası, bilinmeyen etiket ya da eksik sütun `PipelineError` verir; başarısız koşu çıktı bırakmaz.
- **S-06 (G3, arayüz, küçük):** `FEATURE_SOURCES` sabit değil, `Vocab.feature_sources()` yöntemi; çünkü 35 özelliğin adı T1 sözlüğüne bağlı. Ham değerler ayrıca saklanmaz, `raw_values()` ile `log1p` tersinden elde edilir. `Roles` özellikleri `roles=<değer>`, `EvidenceRole` özellikleri `role=<değer>` önekini kullanır. Teknik sözlüğü olay sayısına göre, varlık türü ve `Roles` sözlüğü satır sayısına göre sıralanır; eşitlikte alfabetik.
- **S-07 (G3, küçük):** Kilitli TEST dilimi için özellik dosyası üretilmez (`features_TEST.parquet` yok); yalnız son değerlendirmede üretilir.
- **S-08 (G3):** `scripts/measure.py` G3'te `memory` alt komutuyla oluşturuldu; G9 `latency` alt komutunu ekleyecek.
- **S-09 (G4, küçük):** `choose_threshold` imzasına `classes` parametresi eklendi (olasılık sütunlarının sınıf sırası; sklearn sınıfları alfabetik sıralar). `needs_review(confidence, tau)` (güven < τ) ve `dummy_baselines` aynı modülde (`model/baseline.py`). Kural 3'teki "kapsamı %50 yapan τ", kapsamı hâlâ ≥ %50 olan en büyük τ olarak uygulandı.
- **S-10 (G4, küçük):** `train` üç sınıfın hepsini ister (açıklama, sınıf başına bir katsayı satırına dayanıyor). Açıklamadaki "logit", çok terimli modelde hedef sınıfın softmax girdisi z_k'dir; taban değer b_k + w_k·μ̃ (μ̃: T1'de ölçeklenmiş özelliklerin ortalaması, ≈ 0).
- **S-11 (G4, küçük):** TC-21 için `tests/integration/test_train_baseline.py` eklendi (fixture'da betik koşusu + gerçek veride E1 hipotezi, `realdata`).
- **S-12 (G5, küçük):** Vaka kartında varlıklar (takma ad, tür, kanıt rolü) üzerinden birleştirilir; `Roles`, `SuspicionLevel` ve `LastVerdict` görülen değerlerin listesi, `count` kanıt satırı sayısıdır. Kimlik alanı olmayan türler satır bazında `<Tür>-N` alır ve `aliases` tablosuna `row:<Tür>` alanıyla yazılır. `DomainPII_*` hükümleri okunur olmadığı için kartta gösterilmez. `build_cards`'a isteğe bağlı `mitre_names` parametresi eklendi.
- **S-13 (G5, küçük):** `seed_demo` var olan `app.db`'yi silmez: durur; `--reset` ile eski dosyayı `app.db.bak-<UTC>` olarak taşır (denetim izi, K5). Model kaydı ve etkinleştirme `store/suggestions.py` içindeki `register_model` ile yapılır ve `system_events`'e `model_activated` yazılır. 9–10. hafta tabloları (`review_events`, `precheck_events`, `conflict_events`) bu göçte yok; ileride ayrı göçle eklenir (data-design §8).
- **S-14 (G5, gözlem):** Demo havuzunda önerilerin %66'sı "inceleme gerekli" (VAL'de τ = 0,54 ile %45). T2'de modelin güveni daha düşük; demo için sorun değil, E3'te yeniden değerlendirilir.
- **S-15 (G5, P-01):** MITRE indirmesi bağlantı hızı yüzünden (~26 KB/s) G5 sırasında bitmedi; kartlar şimdilik yalnız kod gösteriyor. İndirme bitince `fetch_mitre.py` CSV'yi yazar ve `seed_demo.py --reset` ile kartlar adlarla yeniden üretilir.
- **S-16 (G6, küçük):** Belgelenen hata kodlarına girdi doğrulaması için `reason_too_long`, `invalid_class`, `class_not_allowed`, `invalid_type`, `invalid_opened_at`, `not_found` eklendi (`decisions.ERRORS`). Kabulde isteğe bağlı gerekçe saklanır. Rol denetimi API'ye ek olarak serviste de yapılır (yalnız analist karar verir).
- **S-17 (G7, küçük):** `get_current_user` ve `require(perm)` FastAPI bağımlılıkları `api/app.py` içinde, istek başına bağlantı bağımlılığının yanında tanımlı; `auth.py` çerçeveden bağımsız `find_user`, `check`, `log_unauthorized` ve `PERMISSIONS` sunar. 401 kodu `unauthenticated`; şema dışı gövde 400 `invalid_request`. Olay listesine `first_seen`, olay ekranına `status`, öneriye `probs`, `threshold`, `model_kind` eklendi (S1/S2 ekranları için). OpenAPI belgesi `/api/docs`.
- **S-18 (G8, küçük):** `demo_scenario.py` varsayılan olarak `app.db`'nin SQLite yedekleme API'siyle alınmış geçici kopyasında, süreç içinde koşar; gerçek denetim izine yazmaz. `--base-url` ile çalışan sunucuya gider (kalıcı kayıt). Tarayıcı denemesi de kopya üzerinde çalışan sunucuyla yapıldı. TC-18'in kod incelemesi kısmı `tests/unit/test_no_external_calls.py` olarak otomatikleştirildi. Arayüz sistem temasına göre açık/koyu.
- **S-19 (G9, küçük):** Gecikme ölçümü süreç içi ASGI üzerinden (`TestClient`), `app.db` kopyasında yapıldı; HTTP soket katmanı dahil değil. TC-26 statik testi `tests/unit/test_secrets.py`.
