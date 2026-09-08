# P2: kök, türemiş lemma ve bağlam seçimi

P2, P1'in aynı morfolojik adaylarını kullanır. Başlangıç kökü, türetim sınırındaki lemma ve son kullanım türü artık aynı alana sıkıştırılmaz. Eski adayın `lemma`, `output_pos`, `features`, ek yolu ve kimliği korunur. Yeni bilgiler `lexical_analyses` ve `lexical_decision` alanlarındadır; bir görünümün `analysis_id` alanı onu aynı morfolojik yola bağlar.

`güzelliğinden` için `güzel` kökü korunurken kayıtlı A_NESS sınırından `güzellik` görünümü çıkarılır. K→ğ geri dönüşü yalnız kayıtlı aynı ekin k/ğ allomorf çiftiyle lisanslanır. Çekim eklerinin rastgele bittiği her önek lemma sayılmaz. Soru AUX görünümü yalnız soru sözlük okumasına, kısaltma NOUN görünümü yalnız `Abbrv` kaydına açılır. `mi` notasının NOUN okuması AUX yapılmaz.

Görünümler alternatiflerdir; hepsinin aynı bağlamda doğru olduğu varsayılmaz. Ayrı bir puanlayıcı, 10.490 TRAIN cümlesinin mevcut R5 aday önbelleğinden eğitilir. Ham sözcük, yakın komşular, aday özellikleri ve lisanslı görünüm bilgilerini kullanır. Tahmin sırasında referans lemma, tür, ilişki etiketi, `good_ids` veya seçilmiş komşu analizini okumaz. E05 dosyası yeniden eğitilmez. P1'in yeni açtığı yollar eğitim önbelleğinde yoktur; bu sınırlama raporlanır.

## Aynı koşullarda deney

Katkı katsayıları önceden `0`, `0.25`, `0.5`, `1.0` olarak kaydedilmiştir. Katsayı sıfır olduğunda eski morfolojik tercih ve kararlar P1 ile birebir aynı olmalıdır; yalnız yeni görünüm tahmini eklenir. Diğer katsayılarda, mevcut adayın UA puanına görünüm puanı eklenir; aynı ek puan UA referans geçişinde de kullanılır. UA içermeyen tarihsel Q0 referansına eklenmez.

DEV önce tamamlanır; katsayı seçimi kaydedilip dosya özetleriyle mühürlendikten sonra CALIB kontrolü yapılır. CALIB sonucuna göre katsayı değiştirilmez. TEST bu koşuda açılmaz. Bunlar geliştirmede görülmüş havuzlardır; yeni bağımsız test başarısı sayılmaz.

Rapor üç ayrı soruya cevap verir:

1. Eski kök+tür ve beyanlı özellik ölçütlerinde gerçekten daha doğru aday seçiliyor mu?
2. Tek tahmin edilen sözlüksel lemma+tür, aynı referansla daha iyi eşleşiyor mu? Sıfır katkı kolu, bunun temsil katkısını ayırır.
3. Herhangi bir görünümde doğru cevap bulunuyor mu? Bu yalnız aday kapsamasıdır; seçilmiş doğruluk diye gösterilmez.

Yeni görünümün özellik kontrolü, ilan edilen sekiz alanı kapsar; Case/Number/Person kontrolleri ADJ/NUM üzerinde de yapılır. Eski özellik ölçütünün kapsamı farklıdır. Tam morfem yolu doğruluğu ölçülmüş sayılmaz. Görünüm marjı kalibre edilmiş olasılık değildir.

## Kullanım

Mevcut proje tabanı ve V'de tutulan E05/P2 ağırlıkları gereklidir. Bu GitHub yaması tek başına dağıtım paketi değildir. Modelin konumu ve beklenen SHA-256 değeri `results_lexical_p2/model-location.json` dosyasındadır; taşınmış model için `head_path=...` ve E05 için `ranker_path=...` verilebilir. Aynı hash zorunludur.

```python
from s06e_p2 import Tokenizer
rt = Tokenizer(strength=0.0)  # P1 tercihi + öğrenilmiş sözlüksel görünüm
out = rt.analyze_sentence("Güzelliğinden söz ettim.")
for token in out["tokens"]:
    print(token["raw"], token["lexical_decision"]["preferred_view"])

from s06e_p2bpe import Tokenizer as Hybrid
codec = Hybrid(strength=0.0)
text = "Güzelliğinden söz ettim. 😀"
assert codec.decode(codec.encode(text)) == text
```

Son deneyde seçilen katsayı `results_lexical_p2/dev-selection-seal.json` içindedir. Eski proje varsayılanı bu modülün eklenmesiyle değişmez. `analyze_word` yalnız alternatifleri gösterir; bağlam yokken tek sözlüksel anlamı uydurmaz.

## IMST kaynak politikası uzantısı

Karma başlığın düşük katkılı DEV kolu geriledikten sonra, TRAIN içindeki kaynak politikası farklılıkları ayrıca incelendi. Yeni `policy-protocol.json` ile aynı özellik satırlarının yalnız 3.260 IMST TRAIN cümlesine ait 18.075 karşılaştırmalı örneği ayrıldı; bütün satırların etiket maskesi eski özellik önbelleğiyle doğrulandı. DEV/CALIB veya MAIN örnekleri eğitime eklenmedi. Bu keşif uzantısında yalnız 0 ve 1 katsayıları karşılaştırıldı; seçim DEV üzerinde mühürlendi.

IMST politikası için açık giriş:

```python
from s06e_p2_policy import Tokenizer, Codec
rt = Tokenizer(strength=1.0)
out = rt.analyze_sentence("Güzelliğinden söz ettim.")
codec = Codec(strength=1.0)
```

Bu başlığın modeli `results_lexical_p2/policy-imst/model-location.json`, DEV seçimi aynı klasördeki `dev-selection-seal.json` ile tanımlanır. Çıktıda `export_policy=UD_IMST` yazılır. Yeni başlık iki havuzda da önceki E05'in eski ölçütlerdeki gerilememe kontrollerini geçti. Bu, kaynak politikasını bütün Türkçe için evrensel bir dilbilgisi kuralına dönüştürmez. Genel proje varsayılanı değiştirilmedi.

## Kaynaklar

- [UD Türkçe rehberi](https://universaldependencies.org/tr/): soru parçacığı AUX, türetim ve ağaç bankası politikası ayrımları.
- [IMST belgesi](https://universaldependencies.org/treebanks/tr_imst/index.html): kullanılan etiketler ve kaynak özellikleri.
- [Bedir ve arkadaşları, 2021](https://aclanthology.org/2021.law-1.12/): Türkçe türetim ve sıfır biçimbirimlerinin UD temsilinde bilgi kaybı.
- [Hakkani-Tür ve arkadaşları, 2000](https://aclanthology.org/C00-1042/): türetim sınırlarına ayrılan çekim gruplarıyla morfolojik belirsizlik giderme. P2 bu makaledeki modeli birebir uygulamaz ve makalenin başarı oranını kendi sonucu olarak kullanmaz.
