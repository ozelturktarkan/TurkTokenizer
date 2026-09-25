# P129 — Yerel YÖNT ilişki deneyi

Durum: COMPLETE / mühendislik PASS.

Ön kayıtlı sentetik mekanizma eşiği: **GEÇMEDİ**. Bu genel Türkçe anlama/BPE üstünlüğü veya 12B–27B eşdeğerliği değildir.

| Koşul | IID | Yeni sözcükler | Yeni sıra | Üç cümle | OOD ort. |
|---|---:|---:|---:|---:|---:|
| base | 69.67% | 57.83% | 67.75% | 68.92% | 64.83% |
| plain | 99.94% | 99.33% | 99.94% | 99.50% | 99.59% |
| morph | 99.97% | 97.33% | 99.83% | 98.00% | 98.39% |
| graph | 99.94% | 98.00% | 99.69% | 99.03% | 98.91% |
| shuffled | 99.89% | 98.11% | 99.56% | 97.86% | 98.51% |

## Ön kayıtlı farklar

- graph − plain: -0.69 yüzde puan; %98.333 aralık [-1.01, -0.38]. Eşik: 10 puan.
- graph − morph: +0.52 yüzde puan; %98.333 aralık [+0.17, +0.88]. Eşik: 5 puan.
- graph − shuffled: +0.40 yüzde puan; %98.333 aralık [+0.06, +0.74]. Eşik: 5 puan.

## Yorum sınırları

Veri önceden yazılmış Türkçe şablonlardan üretilmiştir; insan gold veya genel doğal Türkçe değerlendirmesi değildir. Native analiz yalnız görünür bağlam cümlelerini alır; soru, seçenek ve doğru cevap öğretmen girdisi değildir. Grafik, sorunun aradığı rollere çok yakın bilgiyi içerir. Sonuç öğretmen+model sistemine aittir; çıplak modelin Türkçesini katladık diye okunamaz. BPE kolu aynı Qwen tokenizer/model tabanıdır. Tüm kollarda BPE dizisi, eğitim örnekleri, adımlar ve ayrılan parametreler eşittir; aktif özellik kapasitesi ve gerçek süre eşit olmak zorunda değildir. Grafik çıkarma süresi/önbelleği ayrı maliyettir. Olumsuzluk, edilgenlik ve genel yan cümle kapsamı bu eğitimde yoktur.

Ayrıntılar summary.json, results/eval-*.json, results/train-*.json ve data/native-cache.sqlite içinde. Sonuçlara bakılarak otomatik yeni deney veya eşik değişimi yapılmadı.
