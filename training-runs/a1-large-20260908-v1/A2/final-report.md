# A1 → A3 → A2 sonucu: %92 hedefi mevcut eşiklerle karşılanmadı

A2, korunmuş A1 E05 ve A3 E00 (beş kanal katsayısı 1) üzerinde tamamlandı. CALIB kümesinin 382 cümlesi ve 2.266 noktalama dışı sözcüğü değerlendirildi. Önceden belirlenmiş 121 eşik çiftinin hiçbiri kabul edilen sözcüklerde hem kök+tür hem de tanımlı morfolojik özellik doğruluğunu %92'ye çıkaramadı. A2 ayarı `null` bırakıldı; varsayılan model değiştirilmedi.

| CALIB ölçümü | Sonuç |
|---|---:|
| Bütün sözcüklerde doğru kök+tür tercihi | 1.738 / 2.266 = %76,6990 |
| Bütün sözcüklerde doğru tanımlı özellikler | 1.669 / 2.266 = %73,6540 |
| Doğru kök+tür adayı havuzda mevcut | 1.953 / 2.266 = %86.1871 |
| İki %92 koşulunu sağlayan eşik çifti | 0 / 121 |

## Marjı yükseltmek ne yaptı?

| Eşikler (kök+tür, özellik) | Kabul | Bütün sözcüklerde kapsam | Kabulde kök+tür doğruluğu | Kabulde özellik doğruluğu |
|---|---:|---:|---:|---:|
| (0, 0), mevcut yapısal kapı korunarak | 1.933 | %85,30 | %82,10 (346 hata) | %78,89 (408 hata) |
| (20, 20), önceden belirlenmiş en yüksek çift | 958 | %42,28 | %87,68 (118 hata) | %86,01 (134 hata) |

Izgaradaki en yüksek ortak doğruluk da bu son düzeyde kaldı; (0, 20) aynı sayıları verdi. Bunlar tanı amaçlı sonuçlardır, onaylanmış A2 ayarı değildir. Kabulü azaltmak tek başına %92 doğruluk sağlamadı.

## Sorun nerede?

2.266 sözcüğün birbirini dışlayan dağılımı: 1.738 doğru kök+tür tercihi; doğru aday varken yanlış seçilen 215 sözcük; hizalı ve altın etiketi aktarılabilir olmasına rağmen doğru adayı bulunmayan 270 sözcük; altın etiketi ortografik birime aktarılamayan 38 birim; ayrıca 5 hizalanamayan birim. Son 43 birim paydadan çıkarılmadı.

Her eşik çiftinde kabul edilen 702 sözcükte iki marj da `None`: adaylar ilgili iki karar katmanında tek grup oluşturuyor. Mevcut A2 uygulaması bu durumlarda marj koşulunu geçmiş sayıyor. Bu 702 sözcük içinde 81 kök+tür ve 96 özellik hatası var. Envanterde rakibin bulunmaması doğruluk garantisi sağlamıyor; marjı büyütmek bu hataları elemiyor. Bunlar tek neden değil: son 958 kabul içinde toplam 118/134 hata var.

Aday havuzu sabitken kusursuz bir sıralayıcının bile bu CALIB paydasındaki kök+tür tavanı %86.1871. %92 için en az 2.085 doğru sözcük gerekir: tüm mevcut doğru adaylar seçilse bile en az 132 ek sözcükte doğru aday erişimi gereklidir. Bu, aday eksikleri ve etiket/hizalama kapsamını ayrı incelemeyi; mevcut 215 sıralama hatasını da ayrı çözmeyi gerektirir.

## Doğrulama ve kayıt

Altı seçim politikası testi geçti. 539 çözücü bloğunun hedef puanı, 6.528 aday kaydı, arama tamlığı, yeniden birleştirme ve ilişki grafiği kontrol edildi. (0, 0) ve tanı amaçlı (20, 20) kararları 382 cümlenin tamamında gerçek A2 uygulamasıyla aynı kabul sayılarını verdi; tercih edilen adaylar değişmedi. Girdi, kaynak ve model SHA-256 kontrolleri geçti.

V: üzerinde 106 dosyalık iki snapshot yeniden doğrulandı; gerçek A1 ağırlıkları, A3 katsayıları, girdiler, kaynak, özel çıktı ve durum dosyaları bu kopyalara dahil. Rapor ve tanı dosyaları ayrıca iki kopya olarak kaydedilir. GitHub'a kaynak kod, toplu metrikler, loglar ve hash makbuzları aktarılır; ağırlıklar ve ham sözcük kayıtları V: üzerinde kalır. İki V kopyası aynı diskte olduğu için fiziksel disk arızasına karşı bağımsız yedek değildir.

CALIB eşik seçiminde kullanıldı; bu sonuç bağımsız TEST doğruluğu değildir. Önceki DEV sonucu %77,9607 idi ve ayrı bir veri kümesini ölçüyordu. TEST açılmadı. Tanımlı özellik doğruluğu tam morfem yolu doğruluğu değildir. Gerçek BPE yönlendirme oranı ölçülmedi; %92 TürkTokenizer + %8 BPE hedefine ulaşıldığı söylenemez. Wilson aralıkları yalnızca betimseldir; eşik seçimi ve belge bağımlılığı için düzeltilmemiştir.

Sonraki geliştirme için somut öncelik: tek gruplu yanlış kabullerin kök nedenleri, doğru aday bulunmayan 270 sözcük ve doğru adaylı 215 sıralama hatası. Bu CALIB sonuçlarına göre yapılacak değişiklikler için yeni bağımsız değerlendirme gerekir.
