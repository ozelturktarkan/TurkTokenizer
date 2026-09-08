# A3 — A1 E05 tabanlı epoch koşusunun sonucu

A3, **E09 sonunda PATIENCE_9 ile durdu**. Hiçbir epoch seçilmiş A1 E05 modelini güvenli biçimde geçemedi. Sonuç olarak **A1 E05 korundu**; A3'ün seçilen noktası, başlangıç çarpanlarını temsil eden **A3 E00** oldu.

Seçilen modelin DEV doğruluğu **3.173 / 4.070 = %77,960688**. Bu A3 koşusunun seçilen modele ek doğru kullanım kazancı **0**. Son eğitilen E09, başlangıçtan üç doğru kullanım daha düşük sonuç verdi ve seçilmedi.

## Başlangıç ve son epoch

| Ölçüt | Korunan A1 E05 / A3 E00 | A3 E09 |
|---|---:|---:|
| Doğru lemma + tür | **3.173** | 3.170 |
| Tam DEV paydasında doğruluk | **%77,960688** | %77,886978 |
| Doğru beyanlı morfolojik özellik | **3.040** | 3.037 |
| Kesin karar sayısı | 3.644 | 3.619 |
| Doğru kesin lemma kararı | **3.042** | 3.029 |
| Yanlış kesin lemma kararı | 602 | 590 |
| Sabit TRAIN sıralama loss'u | 40,840595 | 35,080984 |
| Sabit DEV sıralama loss'u | 8,819400 | 7,763111 |

Yanlış kesin karar sayısı 12 azaldı; toplam kesin karar sayısı da 25, doğru kesin karar sayısı ise 13 azaldı. Bu azalmayı tek başına doğru seçim kazanımı olarak değerlendirmiyoruz. E09'da tercih edilen doğru lemma+tür ve morfolojik özellik sayıları üçer azaldı.

Sıralama loss'u düşmesine rağmen tam çözücü doğruluğu artmadı. Bu deneme, mevcut beş kanalın genel ağırlıklarını değiştiren A3 yaklaşımıyla E05'in aşılabildiğini göstermedi. Bütün A3 yöntemlerinin başarısız olduğu sonucu çıkarılamaz.

## Eğitim ve seçim koşulları

Koşu: `a1-large-20260908-v1/A3`.

A1 E05'in UA özellik ağırlıkları sabit kaldı. Yalnız beş puan kanalının çarpanları eğitildi: UA, AB04 sözcük, AB04 ek yolu, n-gram tür ve n-gram morfoloji. Morfolojik aday motoru, arama sınırları ve kaynak modeller değiştirilmedi.

Eğitim kümesi **512 genel TRAIN hedefi + 252 MAIN zor hedefinden** oluştu: **764 hedef, 584 bağlam**. Her epoch bütün hedeflerden bir geçiş yaptı. Dokuz epoch'ta 6.876 hedef geçişi ve 108 Adam güncellemesi yapıldı; bunlar 6.876 farklı örnek değildir.

Adam öğrenme oranı 0.001, batch 64, seed 20260908; kanal sınırları [0.05, 3], kareli hinge marjı 1 ve düzenlileştirme katsayısı 0.1 kullanıldı. İlk madencilik, E00/E01'in aynı başlangıç ağırlıklarıyla yapıldı. Sonraki her epoch öncesinde bütün eğitim bağlamları güncel tam çözücüyle yeniden çözüldü. Her hedefin doğru/yanlış taraflarının puan farkı ve çözücü marjı bağımsız olarak doğrulandı.

TRAIN tanı loss'u E00'da sabitlenen 764 kontrastta, DEV tanı loss'u her uygun cümleden hash ile seçilmiş **284 hedefte** hesaplandı. Bu tanı kümeleri ve karşıtları epoch'lar arasında değişmedi. Tanı loss'u düzenlileştirme içermez. A1'in NLL loss'u ile A3'ün kareli hinge loss'u aynı ölçü değildir; sayısal düzeyleri birbiriyle karşılaştırılmamalıdır.

Model seçimi, **293 DEV cümlesindeki 4.070 sözcüğün tamamında** doğru lemma+tür sayısına göre yapıldı. Beyanlı özellik doğruluğu E05'in altına düşemedi; yanlış kesin lemma kararları E05'i aşamadı. Aday kimliği, arama tamamlığı, metni geri kurma, ilişki grafiği ve çözücü amaç fonksiyonu denetlendi. E05 başlangıç sonucu yeni yükleyiciyle birebir yeniden üretildi.

| Epoch | DEV doğru / 4.070 | TRAIN loss | DEV loss | Güvenlik | Sabır |
|---|---:|---:|---:|---|---|
| E01 | 3173 | 40.119667 | 8.692731 | Geçti | 1/9 |
| E02 | 3173 | 39.456123 | 8.569998 | Geçti | 2/9 |
| E03 | 3173 | 38.819786 | 8.452966 | Geçti | 3/9 |
| E04 | 3172 | 38.157768 | 8.329610 | Geçemedi | 4/9 |
| E05 | 3172 | 37.534854 | 8.210956 | Geçemedi | 5/9 |
| E06 | 3171 | 36.936054 | 8.099065 | Geçemedi | 6/9 |
| E07 | 3171 | 36.305469 | 7.979909 | Geçemedi | 7/9 |
| E08 | 3170 | 35.667003 | 7.865949 | Geçemedi | 8/9 |
| E09 | 3170 | 35.080984 | 7.763111 | Geçemedi | 9/9 |

E01–E03 eşit sonuç verdiği için sabır sıfırlanmadı. E04–E09 güvenlik koşulunu geçemedi. E09 sonunda sabır 9/9 oldu. E70 üst sınırına veya E21'de başlayacak overfitting takibine ulaşılmadı. Durma nedeni **PATIENCE_9**; overfitting alarmı değildir.

TEST ve CALIB verileri bu koşuda açılmadı. DEV seçimde kullanıldı; bu sonuç bağımsız test başarımı değildir. MAIN zor örnekleri eğitimde kullanıldığı için oradaki toparlanma test sonucu olarak sunulamaz.

## Seçilen dosyalar ve yedekler

Koşu dizini:

`V:\TurkTokenizer\Yedekler\A123-E70-P9-OF3\runs\a1-large-20260908-v1\A3`

`selected-ranking.json`, her iki A3 E00 ağırlık kopyasıyla birebir eşleşiyor. Seçilen modelde A3 çarpanları başlangıç değerlerinde kaldı; korunmuş A1 E05 ağırlıklarının hash'i:

`eed03755d0026c36b055f68ba18daf7188037cbac85265b24add5c2c7a182ff2`

Seçilen A3 tanımının hash'i:

`d0537300fa21b9e94e70bb0bf3e96a8d3386cab2f57d6e863c53fa5d5446f336`

Her epoch'ta iki snapshot doğrulandı. Saklama politikası nedeniyle her kopyada E00, E08 ve E09 tutuluyor: toplam **6 snapshot**. A1 ağırlıkları, A3 ağırlıkları, optimizer/RNG, sabit tanı matrisleri, audit ve durum hash'leri yeniden doğrulandı. Bütün epoch'ların küçük olay ve GitHub kayıtları korundu.

E00 ve E09 optimizer dosyaları iki kopyada da açılıp doğrulandı; E09'da 108 güncelleme ve geri yüklenebilir rastgelelik durumu bulundu. **78 kaynak dosyası**, **9 dondurulmuş girdi**, **4 üretilmiş probe/cache dosyası** ve **4 sabit runtime model dosyası** hash denetimini geçti. Hazırlıkta **22 test** geçti. Eğitici normal biçimde sona erdi ve kilidini kaldırdı.

## GitHub ve takip

[E01–E09 GitHub kayıtları](https://github.com/ozelturktarkan/TurkTokenizer/tree/codex/e70-p9-logs/a1-large-20260908-v1-A3/training-runs/a1-large-20260908-v1/A3)

Her epoch için dört toplu metrik/log dosyası ayrı commit ile yayımlandı. **36 Git blob hash'i** outbox dosyalarıyla eşleşti; dokuz commit'in sıralı ebeveyn zinciri doğrulandı.

İlk yerel Git işlemi gecikti. A3'e ait küçük bare depodaki nesneler tamamlandı, yalnız bu depoda etkileşimli kimlik doğrulama beklemesi kapatıldı ve indeks yazımı doğrulandı. Sonraki yayınlar bağlı GitHub uygulamasıyla yapıldı. Her epoch, aynı dosya hash'lerine ait yayın onayı gelmeden sonraki epoch'a geçmedi. Ana checkout'un Git durumu değiştirilmedi.

Takip aktif oturumdan yürütüldü; A1'de tetiklenmeyen heartbeat kullanılmadı. Bu rapor heartbeat'in onarıldığı iddiasını taşımaz. Eğitim metinleri, model checkpoint'leri ve optimizer dosyaları metrik yayınına eklenmedi; bunlar V: üzerinde tutuldu.

**A2 başlatılmadı ve ürünün varsayılan modeli değiştirilmedi.** A1 → A3 → A2 sırasındaki sonraki aşama, korunmuş model üzerinde A2 marj kalibrasyonudur.
