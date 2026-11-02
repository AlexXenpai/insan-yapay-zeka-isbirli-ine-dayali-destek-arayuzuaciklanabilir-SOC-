# ADR-0001: Python çekirdek paketi + FastAPI REST API + düz HTML/CSS/JS arayüz

- **Durum:** Kabul edildi (2026-11-02)
- **Kaynak:** Kullanıcının faz 3 seçimi (oturum 9). Önce hocanın belgeleri tarandı: konu tanımı (`proje_hakkında.txt`) yalnız "Python" diyor. Yeni yol haritasında yığın şartı yok. Eski genel rehber örnek olarak REST API ile React/Vue ya da HTML/CSS/JS, arka yüz için Django/Flask/FastAPI veriyor (bağlayıcı değil).

## Bağlam

- FR-23 / NFR-05: rol yetkileri sunucu tarafında uygulanmalı.
- FR-29: AS1 simülasyonu aynı karar ve doğrulama mantığını arayüzsüz koşturmalı.
- FR-31: çalışma modunda karar süresi güvenilir ölçülmeli.
- Görev paketleri: A (veri/model/depolar) ve B (API/arayüz/ön denetçi) arasında net bir sınır gerekiyor.
- Demo 2026-11-03'te. Node araç zinciri kurulu değil. fastapi, uvicorn, pydantic ve jinja2 kurulu.

## Değerlendirilen seçenekler

1. **Python çekirdek + FastAPI REST + düz HTML/CSS/JS** (seçildi): Alan mantığı (karar sürümleme, depolar, model, açıklama, ön denetçi) arayüzden bağımsız bir pakette. FastAPI bunu JSON REST API olarak sunar ve yetkiyi uygular. Arayüz derleme adımı olmayan statik sayfalardan oluşur ve API'yi `fetch` ile çağırır. Artısı: REST sözleşmesi baştan açık; AS1 çekirdeği doğrudan kullanır; bugüne yetişir. Eksisi: SPA'ya göre daha az zengin etkileşim; JS'i elle yazmak gerekir.
2. **FastAPI + Jinja2 sunucu taraflı HTML:** En az JS gerektirir. Ancak ayrı bir REST sözleşmesi oluşmaz; ileride SPA'ya geçilirse API yeniden tasarlanır.
3. **FastAPI REST + React:** En iyi kullanıcı deneyimi. Node araç zinciri gerekir, bugünkü demo için riskli ve B paketinin yükünü artırır.
4. **Streamlit:** En hızlı demo. Yetki oturum durumunda kalır, gerçek bir API olmaz; 7–8. haftada büyük olasılıkla yeniden yazılır. Elendi.

## Karar

- Alan mantığı `src/` altındaki tek bir Python paketinde. Bu paket HTTP'ye ve arayüze bağımlı değil.
- HTTP katmanı FastAPI. Bütün yazma ve okuma işlemleri `/api/...` altındaki JSON uç noktalarından geçer. Rol yetkisi her uç noktada sunucuda denetlenir.
- Arayüz FastAPI'nin statik olarak sunduğu HTML/CSS/vanilla JS dosyalarıdır. İş kuralı arayüzde değil API'de uygulanır; arayüzdeki doğrulama yalnız kolaylık içindir.
- AS1 simülasyonu ve betikler çekirdek paketi doğrudan içe aktarır, HTTP kullanmaz.

## Sonuçlar

- **Olumlu:** Paket A'nın çekirdeği ile Paket B'nin API ve arayüzü arasındaki sınır API sözleşmesiyle tanımlı. Arayüz ileride React'e geçse de API değişmez. Testler HTTP'siz çekirdek üzerinde koşabilir.
- **Olumsuz / riskler:** Vanilla JS büyüdükçe dağınıklaşabilir. Ekran sayısı sınırlı tutulmalı (kuyruk, olay, doğrulama, model, çalışma). Gerekirse ayrı bir ADR'yle SPA'ya geçilir.

## İzlenebilirlik

- **Gereksinim:** FR-23, FR-29, FR-31, NFR-01, NFR-02, NFR-05
- **Bağlantılı:** ADR-0002, ADR-0003
