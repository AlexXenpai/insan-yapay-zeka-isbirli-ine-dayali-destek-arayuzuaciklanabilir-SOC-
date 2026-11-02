# ADR-0006: MITRE teknik adları resmî ATT&CK verisinden

- **Durum:** Kabul edildi (2026-11-02)
- **Kaynak:** Kullanıcının faz 4 onay kapısındaki seçimi.

## Bağlam

- FR-02: Vaka kartında MITRE teknik kodları ve adları gösterilmeli.
- GUIDE yalnız kod veriyor (ör. `T1566.002`). Olayların %35'inde `MitreTechniques` dolu (veri denetimi).
- Okunur alanların az olduğu kartta (K2, R-01) teknik adları analistin olayı anlaması için önemli.

## Değerlendirilen seçenekler

1. **MITRE'nin resmî ATT&CK verisi** (seçildi): `github.com/mitre/cti` deposundaki `enterprise-attack/enterprise-attack.json` (STIX 2.x) bir kez indirilir. Kod → ad eşlemesi `data/reference/mitre_techniques.csv` dosyasına çıkarılır. Doğru ve eksiksiz; ATT&CK kullanım şartları atıfla ücretsiz kullanıma izin veriyor.
2. **Şimdilik yalnız kodlar:** İndirme gerekmez, ama kart daha az okunur olur.
3. **Elle kısa liste:** İndirme gerekmez, ama yazım hatası riski var ve kaynak kanıtı zayıf kalır.

## Karar

- `scripts/fetch_mitre.py` dosyayı bir kez indirir. İndirilen JSON scratchpad'e ya da `data/reference/raw/` altına konur.
- Betik yalnız `attack-pattern` nesnelerinden `external_references[source_name="mitre-attack"].external_id` → `name` eşlemesini CSV'ye yazar. İptal edilmiş (`revoked`) ve kullanımdan kalkmış (`x_mitre_deprecated`) teknikler işaretli olarak tutulur.
- CSV'nin ilk satırında ATT&CK sürümü ve erişim tarihi yer alır.
- İndirilen içerik veri olarak işlenir; içindeki hiçbir şey çalıştırılmaz.
- Atıf README'ye ve rapora yazılır: "MITRE ATT&CK®, The MITRE Corporation".
- Dosya yoksa `load_mitre_names` boş sözlük döndürür ve kartta yalnız kod gösterilir.

## Sonuçlar

- **Olumlu:** Kartta resmî teknik adları görünür. Eşleme yeniden üretilebilir.
- **Olumsuz / riskler:** Tek seferlik bir dış indirme gerekir. GUIDE'daki bazı kodlar ATT&CK'in güncel sürümünde iptal edilmiş olabilir; bunlar "(kullanımdan kalktı)" etiketiyle gösterilir.

## İzlenebilirlik

- **Gereksinim:** FR-02
- **Bağlantılı:** ADR-0005
