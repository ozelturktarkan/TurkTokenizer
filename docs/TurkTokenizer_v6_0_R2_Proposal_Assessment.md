# TurkTokenizer v6.0 R2 — `incele.md` değerlendirmesi

Tarih: 2026-08-21  
Öneri dosyası SHA-256: `676391958340040daef93ace17ea4f7cebfd782c4df523e47778473084ef692d`

## Karar özeti

R2, en güçlü yaşayan taban olan A1'den **sıfırdan** eğitilir. R1'in NULL-artırımlı doğrudan-yay decoder'ı taşınmaz; R1, OBJECT kaynak F1'ini `0.7287500` değerinden `0.7258567` değerine düşürmüş ve CALIB ekranında elenmiştir. R2'nin tek ana hipotezi, A1'in güçlü koşullu baş seçimini korurken doğrudan ilişki ailelerinde kaynak-token belirlemeyi bağımsız ve zengin bağlamla denetlemektir.

## Kabul edilen ve düzeltilerek uygulanan öneriler

1. **Kaynak aday ön-süzgeci:** `POSS_HEAD`, `OBJECT` ve `PARTICIPLE_HEAD` için ayrı kaynak skoru eklendi. Süzgeç; Transformer bağlamını, graph-message durumunu, bağlamsal morfoloji durumunu ve UPOS/UD-feature/dependency-relation posterior projeksiyonlarını birlikte görür. Ana baş logitleri A1'den korunur.
2. **Aile koruma ağırlıkları:** R1 gerilemesini telafi etmek amacıyla tüm relation loss'u keyfî biçimde yeniden tartmak yerine yalnızca yeni kaynak-süzgeci yardımcı kaybı `OBJECT=1.40`, `POSS_HEAD=1.15`, `PARTICIPLE_HEAD=1.15` olarak tartılır. Böylece değişiklik hedeflenen darboğazla sınırlı kalır.
3. **OBJECT hard-negative odağı:** Yanlış baş seçilmiş gerçek bir kaynağı bastırmak hatalı olur. Ek source hard-negative cezası yalnızca gold/consensus kaynak hedefi `<0.5` olan tokenlara uygulanır; OBJECT çarpanı `1.50`'dir.
4. **Numerik güvenlik:** `-1e4` ile `-20` sabitlerini eşitlemek yerine tamamen maskeli satırlarda bile sonlu ve tam sıfır sonuç veren masked-softmax kullanılır. Kaynak kanıtı, sentinel sabitleri olmadan geçerli başlar üzerinde `max` ve `log-mean-exp` ile hesaplanır.
5. **Patience = 5:** Syntax, relation ve hard-negative aşamalarının tamamında sınır `5`'tir. Seçim skoru `1e-4` değerinden fazla iyileşirse sayaç `0/5`; aksi durumda sayaç `+1/5` olur. Her epoch logunda skor, `improved=true/false` ve `patience=x/5` yazılır.
6. **Regresyonsuz ekran:** R2'nin tutulması için A1'e karşı macro relation F1 kazancı en az `+0.01`, bütün aile deltaları `>=0` ve UAS/LAS gerilemesi en fazla `0.005` olmalıdır.
7. **Bağlamsal morfoloji ölçümü:** Belgede geçen `0.6328`, A3 TRAIN kafesinin ham Top-1 ortak lemma+morfoloji kapsamasıdır; öğrenilmiş A1/R2 posterior doğruluğu değildir. R2 final CALIB audit'i bağlamsal Top-1 compatible recall, statik Top-1 ve uyumlu aday posterior kütlesini ayrı raporlar.

## Uygulanmayan veya ertelenen öneriler

- **Mask sabitlerini eşitleme:** İki sentinel sabitini aynı yapmak NaN/underflow güvenliği sağlamaz. Maskenin olasılık uzayında tam sıfır kütle alması gerekir.
- **`lr_syntax=0.00025`, `grad_clip=0.6`, warmup:** Mevcut A1/R1 kanıtında NaN, loss sıçraması veya gradient patlaması yoktur; relation learning rate zaten `0.00025`'tir. Üç optimizasyon değişikliğini ana mimari hipotezle karıştırmak nedensel yorumu bozar. Bu R2 ekranında syntax LR `0.0005`, grad clip `1.2` ve mevcut optimizer korunur.
- **Relative-position OOM iddiası:** Mevcut kod batch başına `B×N×N` mesafe matrisi üretmez; her layer'da `N×N` relative-index ve `H×N×N` bias oluşur. Kilitli TRAIN'de azami cümle uzunluğu 37'dir. Checkpointing/sparse tensor CPU eğitimini yavaşlatabileceğinden ve kanıtlanmış OOM olmadığından eklenmemiştir. Kullanılmayan dört-expert yığını forward sonucundan serbest bırakılmıştır.
- **`satisfies` içinde sıralı ek doğrulama:** A1'de `satisfies`, sırasız UD feature kümesi ile analyzer adayının uyumluluğunu denetler; morfotaktik üretici değildir. Ek sırasını burada zorlamak kavramsal olarak yanlıştır. Ordered-realization A2 zaten ayrı denenmiş ve OBJECT gerilemesiyle elenmiştir.
- **Tekil zamir/ek heuristiklerini ana kafese ekleme:** A3, TRAIN-only aday kapsamını yükseltmesine rağmen A1'e karşı macro/min ve CASE_GOVERNOR sonuçlarında geriledi. `bizim`, `hepsi`, `bunların`, `bunları`, `birbirlerine`, `-ki` ve birleşik zamanlar ayrı, sözlük/provenance kontrollü bir morfoloji sürümünde ele alınmalıdır; R2 ilişki deneyine karıştırılmamıştır.
- **Sparse expert hesaplama:** Dört expert tensörü mevcut füzyon için aynı anda oluşturulmaktadır. R2, metriklerce tüketilmeyen kalıcı kopyayı serbest bırakır; tepe belleği değiştirecek streaming füzyon ayrı eşdeğerlik testi gerektirir.

## Araştırma dayanağı

- [Character-Aware Neural Morphological Disambiguation](https://aclanthology.org/P17-2105/): doğru analizin yüzey ve cümle bağlamıyla eşleştirilmesi Türkçe ve Kazakçada güçlüdür.
- [A Graph-based Lattice Dependency Parser for Joint Morphological Segmentation and Syntactic Analysis](https://aclanthology.org/Q15-1026/): Türkçede morfolojik kafes ve sözdiziminin ortak modellenmesi pipeline sistemlerinden daha iyi sonuç verir.
- [Turkish Treebank as a Gold Standard for Morphological Disambiguation and Its Influence on Parsing](https://aclanthology.org/L14-1056/): morfoloji verisi ile hedef treebank alanı arasındaki uyum parsing başarısını doğrudan etkiler; elle yazılmış birkaç istisnanın genelleme kanıtı olmadığı için veri-provenance disiplini korunmalıdır.
- [Jointly Predicting Predicates and Arguments in Neural Semantic Role Labeling](https://aclanthology.org/P18-2058/): kaynak/argüman ve ilişki kararlarının paylaşılan zengin bağlamsal temsillerle birlikte öğrenilmesi, gold kaynak varsayımını kaldırır.
- [PriMeSRL-Eval](https://aclanthology.org/2023.findings-eacl.134/): argüman belirleme hataları sonraki sınıflandırma adımlarına yayılır; faktörize source ve conditional-head ölçümlerinin birlikte korunması gerekir.
- [Parallel Universal Dependencies Treebanks for Turkic Languages](https://aclanthology.org/2025.udw-1.14/): Türkçe, Azerbaycanca, Kırgızca ve Özbekçe için ortak fakat diller arası farklılıkları görünür kılan paralel UD kaynağı, ilerideki Türk dilleri aktarım kapısı için uygundur; mevcut R2 yalnızca Türkçe TRAIN/CALIB ekranıdır.
- [Modelling the Morphology of Verbal Paradigms](https://aclanthology.org/2026.sigturk-1.8/): Türkçenin şeffaf eklemeli yapısında küçük/atomik parçaların yararlı olabildiğini gösterir; bu bulgu karakter yolu + morfoloji kafesini koruma kararını destekler.

## Kalite ve veri kapıları

Mühürlü `INTERNAL_VAL`, BOUN/IMST/Penn external holdout'ları ve resmi test bölmeleri açılmaz. Eski mutlak kapılar gevşetilmez. `incele.md` üretim hedefleriyle birleşen etkin v6 kapıları `macro>=0.90`, `min-family>=0.87`, `UAS>=0.93`, `LAS>=0.85`; stretch hedefi dört ölçütte de `0.95`'tir.
