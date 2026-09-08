# S06E E05 P1: ses sınıfı ve telaffuz onarımı

A1 E05 ve A3 E00 sabitken dört kol tamamlandı. Yeni eğitim yapılmadı; eski sözlük/ek dosyaları, referans etiketler, arama sınırları ve BPE kimlikleri değişmedi. Bu ayrı bir deney girişidir; eski varsayılan yükseltilmedi.

## Aynı koşullarda karşılaştırma

| Kol | DEV doğru lemma+tür /4070 | DEV özellik /4070 | DEV yanlış kesin karar | CALIB doğru lemma+tür /2266 | CALIB özellik /2266 | CALIB yanlış kesin karar |
|---|---:|---:|---:|---:|---:|---:|
| E05 kontrol | 3173 | 3040 | 602 | 1738 | 1669 | 376 |
| Şapkalı ünlü | 3173 | 3040 | 602 | 1738 | 1669 | 376 |
| Telaffuz | 3172 | 3039 | 602 | 1739 | 1671 | 377 |
| Birleşik P1 | 3172 | 3039 | 602 | 1739 | 1671 | 377 |

DEV model geliştirmede; CALIB kalibrasyon ve 270 vaka incelemesinde kullanılmıştır. Bunlar bağımsız yeni test sonuçları değildir. Tam morfem yolu doğruluğu ölçülmüş sayılmaz; kök+tür ve beyanlı özellik ölçüleri ayrıdır. TEST bu koşuda açılmadı.

## Birleşik koldaki aday ve seçim değişimleri

### DEV

Doğru lemma+tür: 3172/4070 = %77.9361. 0 eski hata düzeldi, 1 yeni seçim hatası oluştu; net -1.

Doğru aday kapsaması: +0 / -0 sözcük. 5 tokenın adayları değişti; 5 aday eklendi, 0 aday kaldırıldı. 11799 ortak adayın ID'si ve bütün içeriği korundu.

Eklenen adayların 0 tanesi mevcut kök+tür referansıyla eşleşiyor, 5 tanesi eşleşmiyor. Bu ikinci sayı dilbilgisel yanlış aday sayısı değildir; geçerli belirsizlik ve kaynak tür politikası farklarını da içerir.

### CALIB

Doğru lemma+tür: 1739/2266 = %76.7432. 1 eski hata düzeldi, 0 yeni seçim hatası oluştu; net +1.

Doğru aday kapsaması: +1 / -0 sözcük. 3 tokenın adayları değişti; 5 aday eklendi, 0 aday kaldırıldı. 6528 ortak adayın ID'si ve bütün içeriği korundu.

Eklenen adayların 2 tanesi mevcut kök+tür referansıyla eşleşiyor, 3 tanesi eşleşmiyor. Bu ikinci sayı dilbilgisel yanlış aday sayısı değildir; geçerli belirsizlik ve kaynak tür politikası farklarını da içerir.

## Dar davranış kontrolleri

| Kol | Geçerli yol + hatalı karşıt birlikte geçen çift /25 |
|---|---:|
| E05 kontrol | 9 |
| Şapkalı ünlü | 14 |
| Telaffuz | 20 |
| Birleşik P1 | 25 |

`vicahîye`, `zekâya`, `rükûya`, `Taylor’ın`, `İMKB’nin`, `Abby’ye` ve `Vodafone’a` için ses koşulları onarıldı. `Taylor’ım` / `TBMM’yim` gibi sıfır ek üzerinden geçen yollarda telaffuz korunuyor. Sesli ek gerçekleştikten sonra sonraki uyum o ekin ünlüsünden hesaplanıyor. Yazım ve ham karakter aralıkları değiştirilmedi.

Önceki rapor düzeltmesi: İMKB kaydında `Abbrv` etiketi yok denmişti; gerçekte etiket zaten var. Eski yükleyici `imkb` içinde ünlü bulunduğu için harf harf okuma üretmiyordu. Bu deney açık okuma moduyla bunu düzeltti. İMKB’nin PROPN analizi, kaynak NOUN etiketini otomatik karşılamaz.

## Değişen örneklerin incelemesi

DEV’de eklenen beş yol, mevcut kısaltma okumasının iyelik ekinden sonra korunmasından geliyor: POSS_2_SING + CASE_GEN. Hiçbir eski aday kaldırılmadı. RP’nin aday havuzundaki genişleme, aynı cümlede adayları değişmeyen `süren` sözcüğünün PART_AN/NOUN seçimini PART_AN/ADJ seçimine çevirdi. Referans VERB/Part iken eski uyumluluk yordamı ilk temsili kabul edip ikinciyi reddediyor. Ölçütteki -1 aynen korundu; bunun tartışmasız bir dilbilgisi hatası olduğu varsayılmadı. Aynı cümlede başka bir yanlış kesin karar belirsize döndüğü için toplam yanlış kesin karar sayısı değişmedi.

CALIB’de Taylor için CASE_GEN ve POSS_2_SING yolları geldi; çözücü doğru CASE_GEN yolunu seçti. Aynı cümledeki `bölümü` de belirtme durumundan doğru üçüncü tekil iyeliğe geçti. `üyeleri` sözcüğünün tercihi değişse de referansın sayı/iyelik özelliklerine hâlâ uymuyor; ek kazanım sayılmadı. İMKB için doğru CASE_GEN yolu seçildi fakat PROPN/NOUN temsil farkı nedeniyle mevcut ölçütte yeni bir yanlış kesin karar oluştu. Diğer yeni yol ABD kısaltmasındaki iyelik + tamlayan belirsizliğidir.

Şapkalı ünlü kolu bu iki havuzda hiç aday değiştirmedi. Dolayısıyla odaklı örneklerdeki onarımı havuz kazanımı olarak saymıyoruz. Bağlam etkisi ve tür/ortaç temsili, sonraki dar incelemenin konusu olmalı; bu sonuçlara göre puan ağırlıkları veya referans etiketleri değiştirilmedi.

## Karar ve kalan iş

Önceden belirlenmiş seçim kuralının sonucu: **REVIEW_REQUIRED_KEEP_E05**.

CALIB'deki önceki 121 eşik çiftinde %92 koşulunu sağlayan çift sayısı: kontrol 0, birleşik P1 0. Bu tarama tanı amaçlıdır; yeni A2 eşiği seçilmedi.

Şapkasız `vicahiye` otomatik düzeltilmiyor. Kök–lemma/tür temsili, gözyaşı bileşikleri ve zamir araçlığı henüz onarılmadı. Tarihsel yinelenen ağız okumasının `ağızı` adayına izin vermesi de ayrı bir sözlük sorunu olarak kaydedildi; P1 başarısı gibi sunulmadı.

25 karşıt çift sözcük ve ek yolu davranışını sınar; 25 bağlamlı anlam kararı veya bütün Türkçede kusursuzluk iddiası değildir. Her kaynak sözcükte yeni aday/tercih ayrıntıları V sürücüsündeki özel dökümlerdedir.

## Doğrulama ve dosyalar

Tüm kollarda 2700 cümle çıktısında BPE geri kurma doğrulandı. 224.309 eski ID aynen korundu. Ek API kontrolü 12 metin, 37 geri kurma ve 256 ham bayt değerini kapsadı. Kod bloklarının morfolojiye girmeden BPE üzerinden dönmesi kontrol edildi.

Ek iki karşıt kontrol de geçti: Fox’ta/Fox’da son sesin sertliğini, Taylor’dakinin/Taylor’dakının ise -ki sonrasında yeni ek ünlüsünün uyumu yönetmesini denetledi. Bunlar 25 çiftlik dört kollu karşılaştırmanın dışında raporlanan API kontrolleridir.

Seçilmiş E05 dosyası ve tarihsel kaynaklar deney öncesinde/sonrasında hash ile doğrulandı. Model ağırlıkları ve ham kaynak metinleri V sürücüsünde kalır. GitHub yayını yeni yama, testler, toplu raporlar ve hash kayıtlarından oluşur; bağımsız tam dağıtım paketi değildir.

İki V kopyası aynı fiziksel disktedir. Geri dönüş dosyaları ve kaynak hash listesi `backup-receipt.json` içinde kaydedilir.

## Dilbilimsel kaynaklar

- [TDK düzeltme işareti](https://tdk.gov.tr/icerik/yazim-kurallari/duzeltme-isareti/)
- [TDK kısaltmalar](https://tdk.gov.tr/icerik/yazim-kurallari/kisaltmalar/)
- [MEB Taylor/Teylır okunuşu](https://ogmmateryal.eba.gov.tr/kitap/guzel-sanatlar-lisesi/gorsel-sanatlar/cdst-12/files/basic-html/page124.html)
