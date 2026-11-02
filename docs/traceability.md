# İzlenebilirlik matrisi: Açıklanabilir SOC Karar Destek Arayüzü

- **Güncelleme:** 2026-11-03 (G1–G8 uygulandı; sonuçlar `docs/test-plan.md` §6.1)

Görev kodları G1–G9: `docs/plans/2026-11-02-hafta-1-5-ciktilari-ve-demo.md`. Sonraki haftaların görevleri: `docs/proje-plani.md` §2.

| Gereksinim | Tasarım öğesi | Görev veya kod | Test | Durum |
|---|---|---|---|---|
| FR-01 | api `GET /api/incidents`; S1 | G7, G8 (basit); 7–8. hafta | TC-27 | Kısmi: demo listesi ve durum filtresi (G7, G8); tam kuyruk 7–8. hafta |
| FR-02 | `data.cards`, `aliases`; data-design §9.6; ADR-0005, ADR-0006 | G5 | TC-16 | Doğrulandı (2026-11-03) |
| FR-03 | `suggestions`; api §6 | G5, G7 | TC-17 | Doğrulandı (2026-11-03) |
| FR-04 | Deney planı §2 τ kuralı; `suggestions.needs_review` | G4, G5 | TC-05 | Doğrulandı (2026-11-03) |
| FR-05 | `model.explain`; ADR-0003 | G4 | TC-03, TC-04 | Doğrulandı (2026-11-03) |
| FR-06 | `decisions.record_decision` | G6 | TC-06 | Doğrulandı (2026-11-03) |
| FR-07 | `decisions` doğrulama kuralları (mimari §6) | G6 | TC-07, TC-08 | Doğrulandı (2026-11-03) |
| FR-08 | aynı | G6 | TC-09 | Doğrulandı (2026-11-03) |
| FR-09 | `decision_events`; data-design §2.1 | G5, G6 | TC-10 | Doğrulandı (2026-11-03) |
| FR-10 | `v_effective_decision`; mimari §5 | G6, G8 | TC-11, TC-19 | Doğrulandı (2026-11-03) |
| FR-11 | `is_duplicate`; mimari §6 kural 5 | G6 | TC-12 | Doğrulandı (2026-11-03) |
| FR-12 | `conflict_events` | 9–10 | TC-29 | Planlandı |
| FR-13 | `review` | 9–10 | TC-30 | Planlandı |
| FR-14 | `review`, `conflict_events` | 9–10 | TC-31 | Planlandı |
| FR-15 | labels.db; data-design §2.2, §5 | 7–10 | TC-32, TC-33 | Planlandı |
| FR-16 | `precheck` (kural) | 9–10 | TC-34 | Planlandı |
| FR-17 | `precheck` (LLM); mimari §8 | 11–12 | TC-35 | Planlandı |
| FR-18 | `precheck` geri düşme | 11–12 | TC-36 | Planlandı |
| FR-19 | `retrain` | 9–10 | TC-39 | Planlandı |
| FR-20 | `retrain.compare`; ADR-0004 | 9–10 | TC-40 | Planlandı |
| FR-21 | `model_versions.is_active`; `system_events` | 11–12 | TC-41 | Planlandı |
| FR-22 | Tek yazma yolu `review.*` (mimari §4.2) | G6 | TC-20 | Doğrulandı (2026-11-03) |
| FR-23 | `auth`; izin matrisi (mimari §7) | G7 (kısmi), 7–8 | TC-14, TC-15 | Kısmi: demo kimliği + sunucu tarafı rol denetimi, TC-14/TC-15 geçti; yerel hesap 7–8. hafta |
| FR-24 | `users.password_hash` | 7–8 | TC-28 | Planlandı |
| FR-25 | Arayüz şeridi; ağ çağrısı yok | G8 | TC-18 | Doğrulandı (2026-11-03) |
| FR-26 | `data.guide`, `data.features`; ADR-0004 | G2, G3 | TC-01, TC-02 | Doğrulandı (2026-11-03) |
| FR-27 | `model.baseline`; deney planı E1 | G4 | TC-21 | Doğrulandı (2026-11-03) |
| FR-28 | LightGBM; deney planı E2 | 9–10 | TC-42 | Planlandı |
| FR-29 | `sim`; deney planı E4 | 13–14 | TC-43 | Planlandı |
| FR-30 | denetim izi raporu | 13–14 | TC-44 | Planlandı |
| FR-31 | `study` | 15–16 | TC-45 | Planlandı |
| FR-32 | participants.db | 15–16 | TC-46 | Planlandı |
| FR-33 | participants.db CASCADE | 15–16 | TC-47 | Planlandı |
| FR-34 | `trials.is_practice` | 15–16 | TC-48 | Planlandı |
| NFR-01 | Önceden hesaplanmış öneri (mimari §10) | G5, G9 | TC-22 | Doğrulandı (2026-11-03) |
| NFR-02 | Tek INSERT, WAL | G6, G9 | TC-23 | Doğrulandı (2026-11-03) |
| NFR-03 | DuckDB toplama, float32 | G2, G3, G9 | TC-24 | Doğrulandı (2026-11-03) |
| NFR-04 | Deney planı §7 | 9–14 | TC-43 (süre) | Planlandı |
| NFR-05 | `auth.require` | G7 | TC-14 | Doğrulandı (2026-11-03) |
| NFR-06 | Tetikleyiciler | G5 | TC-13 | Doğrulandı (2026-11-03) |
| NFR-07 | `.gitignore`, ortam değişkenleri | G1, G9 | TC-26 | Doğrulandı (2026-11-03) |
| NFR-08 | Alan listesi (R3 ile) | 11–12 | TC-37 | Planlandı |
| NFR-09 | Şema doğrulaması | 11–12 | TC-38 | Planlandı |
| NFR-10 | İnsan çalışması SUS | 15–16 | Ölçüm | Planlandı |
| NFR-11 | İnsan çalışması gözlemi | 15–16 | Ölçüm | Planlandı |
| NFR-12 | Geri düşme | 11–12 | TC-36 | Planlandı |
| NFR-13 | `meta.json` | G4 | TC-21 (meta alanları), TC-43 | Kısmi: E1'de iki koşu aynı `metrics.json` (2026-11-03); TC-43 13–14. hafta |
| NFR-14 | README | 17 | TC-49 | Planlandı |
| NFR-15 | Kilitli test erişim kuralı | G4, 9–10 | TC-40 | Kısmi: E1'de kilitli test okunmadı (`meta.json` `locked_test_read=false`); TC-40 9–10. hafta |

## Kapsam özeti

- **Toplam gereksinim:** 34 FR + 15 NFR = 49. **Testi olan:** 49. **Doğrulanan:** 20 (2026-11-03). **Kısmi:** 4 (FR-01, FR-23, NFR-13, NFR-15).
- **Testi olmayan gereksinimler:** Yok. NFR-10 ve NFR-11 test değil, insan çalışmasında ölçümle doğrulanır.
- **Gereksinimi olmayan testler veya görevler:** Yok.
