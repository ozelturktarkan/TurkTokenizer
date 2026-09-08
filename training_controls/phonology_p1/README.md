# S06E E05 P1: ses bilgisi onarımı

Bu ek sürüm A1 E05'i, A3 E00'ın beş adet 1 çarpanını ve eski ölçüm sözleşmesini korur. Morfolojik arama sınırları, ek kayıtları, kök kimlikleri ve BPE sözlüğü sabittir. Dört kol: `baseline`, `circumflex`, `pronunciation`, `combined`.

`circumflex`, yazımı değiştirmeden ses koşullarında â/î/û ünlülerini tanır. `pronunciation`, sözlükteki açık `Pr` kayıtlarını ve mevcut kısaltma okumalarını kullanır; Taylor ve İMKB için iki kaynaklı telaffuz kaydı ekler. Kısaltma modunu yalnız ünlü içerip içermemesinden tahmin etmez. Telaffuz, sıfır eklerden ve ünlüsüz eklerden sonra da korunur; gerçekleşen ekin ünlüsü sonraki uyumu belirler. `combined` iki onarımı birlikte uygular.

Önceki 270 vaka raporunda İMKB'nin `Abbrv` etiketinin olmadığı yazılmıştı. Kayıt dökümü bunun tersini gösteriyor: etiket var; `imkb` kökü ünlü içerdiği için eski harf okunuşu üreticisi çalışmıyordu. P1 bu tanıyı düzeltiyor. `İMKB'nin` için geçerli PROPN analizi üretmek, kaynak NOUN etiketini karşılamakla aynı şey değildir. `vicahiye` yazımı da `vicahîye` olarak sessizce değiştirilmez.

## Kullanım

Proje kökünde Python 3.11:

```python
from s06e_p1 import Tokenizer
rt = Tokenizer()  # opt-in combined kolu; mevcut varsayılan dosyası değişmez
out = rt.analyze_sentence("Taylor'ın sözünü İMKB'ye ilettim.")

from s06e_p1bpe import Tokenizer as Hybrid
codec = Hybrid()
assert codec.decode(codec.encode("Taylor’ın sözü. 😀")) == "Taylor’ın sözü. 😀"
```

E05 ağırlığı varsayılan olarak mevcut V yedeğindeki `A1/selected-ranker.json` konumundan yüklenir. Taşınmış dosya için `Tokenizer(ranker_path=...)` kullanılabilir; dosyanın SHA-256 değeri aynı E05 olmalıdır. Tam proje tabanı ve dondurulmuş model paketleri gerekir; bu küçük GitHub yaması tek başına dağıtım paketi değildir.

```text
python -X utf8 -m unittest training_controls.phonology_p1.test_phonology -v
python -X utf8 -m training_controls.phonology_p1.evaluate
python -X utf8 -m training_controls.phonology_p1.validate_runtime
```

Değerlendirme yeni `P1-phonology-v1` V klasörüne yazılır ve mevcut deneyi ezmez. DEV 4070, CALIB 2266 sözcük; bütün kollarda aynı paydalar kullanılır. Eski ham adaylar baseline ile yeniden üretilip karşılaştırılır. Puanlayıcıya referans etiketler verilmez. Aday ekleme/silme ve doğru/yanlış seçim değişimleri ayrı dökülür. Referansla uyuşmayan her yeni aday dilbilgisel hata sayılmaz. CALIB artık geliştirme verisidir; TEST açılmaz.

## Kaynaklar ve sınırlar

- [TDK düzeltme işareti](https://tdk.gov.tr/icerik/yazim-kurallari/duzeltme-isareti/): işaret ünlüye aittir ve ekleme sırasında korunur; işaret silmek anlam ayrımını bozabilir.
- [TDK kısaltmalar](https://tdk.gov.tr/icerik/yazim-kurallari/kisaltmalar/): harf harf okunan ve sözcük gibi okunan kısaltmaların ekleri kendi okunuşuna göre gelir.
- [MEB sanat tarihi kitabı](https://ogmmateryal.eba.gov.tr/kitap/guzel-sanatlar-lisesi/gorsel-sanatlar/cdst-12/files/basic-html/page124.html): Taylor için Teylır okunuşunu verir.
- Açık `Pr` değerleri projenin dondurulmuş Zemberek sözlüğünden alınır; bu yama bütün yabancı adlar için otomatik telaffuz üretmez.

Sınırlar: sözlükteki eski yinelenen ağız okuması `ağızı` yolunu hâlâ açabilir; kök–lemma/tür temsili, gözyaşı bileşikleri, zamir araçlığı ve şapkasız yazım varyantları bu paketin kapsamı dışındadır. Aynı fiziksel V sürücüsündeki iki kopya disk arızasına karşı bağımsız donanım yedeği değildir.
