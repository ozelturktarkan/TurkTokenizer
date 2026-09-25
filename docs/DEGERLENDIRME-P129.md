# P129 — Tamamlanan yerel deneyin değerlendirmesi

25 Eylül 2026. Kullanıcı deneyi yerelde tamamladı. Yeni eğitim/deney başlatılmadan rapor ve ham kayıtlar incelendi.

## Sonuç

**Deney COMPLETE / engineering PASS; ön kayıtlı mekanizma hedefi geçmedi.** Bu uygulamada YÖNT ilişki adaptörü sade BPE tabanlı aynı küçük modelden daha kötü sonuç verdi. Bulguyu küçük modelin Türkçe anlama kapasitesinin arttığına veya genel BPE üstünlüğüne kanıt sayamayız.

Üç sabit tohumun lexical/order/composition değerlendirmelerinde ortalama doğruluk:

| Koşul | Doğruluk | 10.800 tekrarlı değerlendirmedeki hata |
|---|---:|---:|
| Sade BPE + görev eğitimi | %99,5926 | 44 |
| BPE + morfoloji | %98,3889 | 174 |
| BPE + morfoloji + doğru YÖNT bağlantıları | %98,9074 | 118 |
| BPE + morfoloji + karıştırılmış bağlantılar | %98,5093 | 161 |

10.800 karar, aynı 3.600 OOD sorunun üç model tohumuyla tekrar ölçülmesidir; 10.800 bağımsız soru değildir. Taban model görev eğitiminden önce %64,8333'tedir. Sade BPE kolunun yüksek sonucu, tokenizer'ın tek başına anlaması değil, aynı 0.6B modelin olağan görev eğitimiyle bu sentetik örüntüleri öğrenmesidir.

Graph − plain farkı −0,6852 yüzde puandır. Raporlanan bağlam bazlı %98,333 bootstrap aralığı [−1,0093, −0,3796] puan. Üç tohum farkı ayrı ayrı −0,8333, −0,6667, −0,5556 puan; yön hep olumsuzdur. Bootstrap üç sabit tohuma koşulludur, genel tohum popülasyonu belirsizliğini ölçmez. Aralık bu incelemede yeniden üretilmedi; donmuş rapor ve kayıtlardan alındı. Ham başarı/hata sayıları yeniden hesaplandı.

Graph, morph'tan ortalamada +0,5185, shuffled'dan +0,3981 puan iyi; her ikisine karşı birer tohumda yön ters. Bunlar anlamlı büyüklük eşiğinin altında ve sade BPE karşısındaki kaybı ortadan kaldırmıyor.

## Deney tasarımından çıkarılacak ders

Ön kayıtlı +10 puan hedefi, sade kol %99,59'a ulaştığında matematiksel olarak erişilemez hale geldi: tavana yalnız 0,41 puan kalmıştı. Eşik sonradan değiştirilmedi. Bu kolaylık sonuçları iptal etmez; bu görevde ek katmanın fayda sağlamadığı bulgusunu korur. Fakat veri seti genel Türkçe anlamada büyük bir fark aramak için yeterince zor/ayırt edici değildi. Büyük koşudan önce görev zorluğunu ve tavanı daha küçük bir fizibiliteyle sınamamak hazırlayan asistanın tasarım eksikliğidir.

Sorular ajan yazımı kontrollü olumlu geçmiş cümlelerinden gelir. Genel Türkçe, serbest cevap, olumsuzluk/kapsam/örtük özne başarısı ölçülmedi. Bu sonuç bütün morfoloji/ilişki yaklaşımlarının imkânsızlığını da kanıtlamaz; bu bilgi sunumu, eğitim ve görev düzeninde üstünlük yoktur.

Bu reçeteye daha fazla epoch, daha büyük model veya daha çok aynı şablonu eklemeyi sonuç desteklemiyor. Yeni GPU deneyi önermeden önce eldeki yanlışları ve görev kestirmelerini incelemek gerekir. Bir sonraki karşılaştırmanın gerçekten ayırt edici olduğuna düşük maliyetle bakılmalı; zor örnekler yalnız BPE yanlış yaptığı için seçilip bağımsız değerlendirme diye sunulmamalı.

## Kayıt denetimi

- Release makbuzunun 75 dosya SHA-256 değeri eşleşti.
- Execution freeze kaynak hash'leri ve dış makbuz hash'leri eşleşti.
- 12 ana eğitim COMPLETE; her biri 1.350 adım ve 21.600 örnek gösterimi.
- Tohum başına başlangıç, örnek sırası, adım/örnek sayısı, ayrılmış parametre sayısı, protokol ve veri manifest hash'leri aynı.
- 12 × 4.800 = 57.600 ham tahminde ID kümesi, grup/bölüm/rol/hedef, olasılık argmax'ı ve doğru/yanlış bayrağı kontrol edildi; başarı/hata sayıları yeniden hesaplandı.
- failure.json yok. Eğitim döngülerinin toplam süresi 60.916,64 saniye: yaklaşık 16 saat 55 dakika. Bu yalnız eğitim toplamıdır.
- Eski deney sonuçları ve makbuzlar değiştirilmedi. Kapalı TEST açılmadı. Yeni deney/otomasyon başlatılmadı.

Kaynak: `V:/TurkTokenizer/Deneyler/P129-20260924/summary.json`, `SONUC_OZETI.md`, `release-receipt.json`, `results/train-*.json`, `results/eval-*.json`, `data/eval.jsonl`.
