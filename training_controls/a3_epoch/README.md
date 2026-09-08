# A3: seçilmiş A1 E05 üzerinde gerçek epoch eğitimi

Yeni, ayrı A3 koşusu `a1-large-20260908-v1/A3` altında çalışır. Önceki A1,
eski A3 denemeleri, ürün varsayılanı ve ana checkout Git durumu değiştirilmez.

A1 E05'in UA özellik ağırlıkları sabittir. A3; UA, AB04 sözcük, AB04 ek yolu,
n-gram tür ve n-gram morfoloji olmak üzere beş kanal ağırlığını günceller.
Başlangıç çarpanları 1; Adam lr=0.001, batch=64, seed=20260908. Eski kareli
hinge sıralama hedefi, 0.1 düzenlileştirme ve [0.05, 3] sınırları korunur.

Her epoch 512 genel TRAIN hedefi ve 252 MAIN zor hedefinin tamamını kapsar.
584 bağlam tam çözücüyle yeniden çözülür; doğru ve yanlış tarafların en güçlü
tutulan planları üzerinden kontrastlar çıkarılır. Sonra 764 kontrastın her biri
bir kez güncellemede kullanılır. E00 madenciliği E01'in tam olarak aynı başlangıç
ağırlıklarını kullandığından ilk geçişte yeniden kullanılır. Sonraki her epoch
yeniden madencilik yapar. Bu yaklaşım planlayıcıdan tam türev alma iddiası taşımaz.

TRAIN/DEV tanı loss'u E00'da dondurulmuş kontrastlarda ölçülür; bu loss dinamik
madencilik havuzunun değişmesiyle karşılaştırılamaz hale gelmez. DEV probe,
her uygun cümlede hash ile seçilen bir yarışan lemma+tür hedefi kullanır.
Asıl model seçimi yine DEV'in tüm 4.070 sözcüğündeki tam çözücü doğruluğudur.
Başlangıç E05 sonucu yeniden üretilmeden eğitim başlamaz.

E70, sabır 9, E21'den itibaren üç ardışık overfitting sinyali kuralları bağlıdır.
Yeni güvenli tepe yoksa A3 E00, yani A1 E05 + bütün çarpanlar 1 korunur.
E05'e göre beyanlı özellik doğruluğu gerileyemez; yanlış kesin lemma kararları
artamaz. Adaylar, geri kurma, arama tamamlığı, ilişki grafiği ve amaç fonksiyonu
doğrulanır. MAIN artık eğitim örnekleridir; oradaki toparlanma test başarısı değildir.

Her epoch'un iki V: snapshot'ı A1 ağırlıkları, A3 ağırlıkları, Adam/RNG durumu,
sabit tanı matrisleri ve audit içerir. Her kopyada E00, best ve son iki epoch
korunur. Büyük dosyalar C:'ye yazılmaz.

Her epoch için dört küçük metrik/log dosyası GitHub outbox'ına hazırlanır.
CLI push mümkün değilse bağlı GitHub uygulaması yayını yapar. Sonraki epoch,
aynı dosya hash'lerine ait doğrulanmış `published.json` kaydı gelene kadar bekler.
15 dakika içinde gelmezse koşu devam edilebilir biçimde duraklar. Başarısız
heartbeat'e güvenilmez; bu koşunun yayını ve durum takibi aktif oturumdan yürütülür.

```text
python -X utf8 -m training_controls.a3_epoch.train --run-id a1-large-20260908-v1 --through-epoch 70
```

TEST/CALIB açılmaz; bu eğitici A2'yi kendiliğinden başlatmaz.
