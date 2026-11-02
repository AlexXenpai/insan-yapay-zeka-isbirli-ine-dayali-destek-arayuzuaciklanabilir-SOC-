# ADR-0002: Uygulama depoları SQLite, GUIDE işlenmiş verisi Parquet/DuckDB

- **Durum:** Kabul edildi (2026-11-02)
- **Kaynak:** Kullanıcının faz 3 cevabı: "Dosyaları inceleyip öyle karar verelim; belirtmediyse önerinden devam." Hocanın belgelerinde veritabanı şartı yok. Eski genel rehber yalnız "SQL veya NoSQL kararı verin" diyor ve PostgreSQL ile MongoDB'yi örnek veriyor.

## Bağlam

- NFR-06: Denetim izi değiştirilemez olmalı.
- s.10 / FR-15: Geri bildirim kaydı ile eğitim etiketi deposu ayrı tutulmalı.
- K5 / FR-33: Katılımcı verisi ayrı depoda tutulmalı ve silinebilmeli.
- GUIDE_Train 9,5 M satır (2,43 GB CSV). DuckDB kurulu ve veri denetiminde bellek sorunu çıkmadan kullanıldı.
- Çalışma oturumları tek makinede yürütülecek. Kurulum kolaylığı NFR-14'ü (temiz kurulum ≤ 30 dk) etkiliyor.

## Değerlendirilen seçenekler

1. **SQLite (uygulama) + Parquet/DuckDB (veri)** (seçildi): SQLite standart kütüphanede gelir, kurulum gerektirmez. `BEFORE UPDATE/DELETE` tetikleyicileriyle yalnız eklenebilir tablo kurulabilir. Depolar ayrı dosyalar olarak tutulabilir. Eksisi: tek yazıcı, ağ üzerinden çok kullanıcı yok, rol izinleri veritabanı düzeyinde değil.
2. **PostgreSQL + Parquet:** Çok kullanıcılı, veritabanında rol izinleri ve daha güçlü değişmezlik sağlar. Eksisi: servis kurulumu ve işletim yükü; tek makinelik çalışma için fazla.
3. **Tümü DuckDB:** Tek motor. DuckDB tetikleyici desteklemediği için NFR-06 veritabanı düzeyinde uygulanamaz. Elendi.

## Karar

- Uygulama verisi üç ayrı SQLite dosyasında durur (kullanıcının faz 3 seçimi):
  - `app.db`: kullanıcılar, olay kartları, öneriler, denetim izi.
  - `labels.db`: eğitim etiketi deposu. Yalnız kıdemli onayıyla yazılır; eğitim kodu yalnız bu dosyayı okur.
  - `participants.db`: katılımcı verisi, anonim kodla, silinebilir.
- Dosyalar arası yabancı anahtar yoktur. `labels.db` → `app.db` bağı uygulama düzeyinde denetlenir ve test edilir.
- GUIDE'dan türetilen olay tablosu ve bölmeler `data/processed/<veri_sürümü>/` altında Parquet olarak tutulur, DuckDB ile üretilir. Ham CSV'lere dokunulmaz.
- Erişim standart `sqlite3` modülü ve elle yazılmış SQL ile yapılır (ORM yok). Şema `schema.sql` dosyalarında durur. WAL kipi açıktır.
- Denetim izi tablolarında `BEFORE UPDATE` ve `BEFORE DELETE` tetikleyicileri `RAISE(ABORT)` ile değişikliği engeller.

## Sonuçlar

- **Olumlu:** Sıfır kurulum. Denetim izinin değişmezliği veritabanı düzeyinde sağlanır. Katılımcı verisini silmek tek bir işlemle yapılır.
- **Olumsuz / riskler:** Çok kullanıcılı ağ dağıtımı gerekirse PostgreSQL'e geçiş ayrı bir ADR olur. Elle yazılmış SQL taşınabilir tutulacak.

## İzlenebilirlik

- **Gereksinim:** FR-09, FR-10, FR-15, FR-26, FR-33, NFR-03, NFR-06, NFR-14
- **Bağlantılı:** ADR-0001
