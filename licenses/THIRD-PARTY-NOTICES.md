# Kaynak ve lisanslar

`data/benchmark-3000.jsonl`, UD Turkish-FrameNet verisinin mevcut proje TRAIN bölümünden alınmış alt kümesidir. Katkıcılar, kaynak ve CC BY-SA 4.0 lisansı `data/FrameNet-README.md` ve `data/FrameNet-LICENSE.txt` içindedir. Bu lisans örnek alt kümesine de uygulanır. Seçim manifesti kullanılan gerçek TRAIN hash değerini ve alt küme hash değerini taşır; r2.15 kamu verisi değerlendirmede kullanılmamıştır.

Zemberek sözcük/paradigma verisi ve Java kaynak karşılaştırmaları `ae2fbe31438dda4dddc674a2a8991d518984d392` commitinden alınmıştır. `data/Zemberek-LICENSE` (Apache License 2.0 bildirimi) ve `data/source-manifest.json` kaynak kimliklerini içerir. R5 Python uygulaması ayrı bir uygulamadır; Zemberek çözücüsü çalıştırılmış gibi sunulmaz.

`data/curated-lexemes.dict` yalnız kullanıcının örneğindeki Ali özel adını ekler. `lexicon-combined.dict` yukarıdaki altı sözlüğün ve bu küçük ekin sıralı birleştirmesidir.

`vendor/r4/TurkTokenizer_v5_11_v4_train_LOCKED.py` kullanıcının doğrulanmış R4 arşivindeki kaynaktır; SHA-256 `f7483e504c12181bd8a72bdbb62f69fae37dec85578dac6dd59db25fefa6667e`. Yalnız gerçek collator uyumluluk kontrolünde import edilir. Eğitim fonksiyonları çağrılmamıştır. Model checkpoint veya kapalı değerlendirme verisi bu pakette bulunmaz.


## v0.7.0: UD Turkish-IMST n-gram kaynağı

Bu araştırma sürümündeki POS/morfoloji sayımları UD Turkish-IMST r2.15 TRAIN verisinden kuruldu. Kaynak dosya, atıf ve özgün lisans `data/ngram/` altında korunur. Kaynak lisansı CC BY-NC-SA 3.0'dır; bütün dosyalar için tek bir sınırsız kullanım lisansı iddia edilmez. Kaynak: https://github.com/UniversalDependencies/UD_Turkish-IMST/tree/r2.15 . Tam içerik hash'i ve belge ayrımı `evaluation/ngram-split-freeze.json` içindedir.

Atıflar: Umut Sulubacak ve Gülşen Eryiğit, Implementing Universal Dependency, Morphology and Multiword Expression Annotation Standards for Turkish Language Processing (2018); Sulubacak ve diğerleri, Universal Dependencies for Turkish (COLING 2016); Oflazer ve diğerleri, Building a Turkish Treebank (2003).
