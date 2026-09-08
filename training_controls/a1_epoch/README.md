# A1 E01: büyük havuzda gerçek epoch eğitimi

Başlangıç, DEV ile seçilmiş mevcut A1 büyük havuz ağırlıklarıdır. E00 yeni eğitim
sayılmaz: başlangıç loss'u ve tam çözücü DEV sonuçları yeniden üretilir, iki
kopya yedeklenir ve güvenli geri dönüş noktası olur.

Her epoch 55.129 yarışan, kaynak etiketiyle uyumlu TRAIN kullanımının tamamından
bir kez geçer. Bunlar 10.490 cümlelik / 103.709 sözcük kullanımlık havuzdan gelir.
Eksik doğru adaylara veya çözülemeyen kaynak birimlerine yapay etiket verilmez.
Adam: öğrenme oranı 0.001, batch 256, seed 20260908. Önceki A1 amaç fonksiyonu
TRAIN örnek sayısına bölünerek korunur; L-BFGS yerine gerçek minibatch geçişleri
kullanılır. İlk epoch optimizer durumu sıfırdan, ağırlıklar mevcut modelden başlar.

Yalnız UA bağlamsal özellik ağırlıkları güncellenir. Adaylar, sözlük/ek kuralları,
AB04 büyük TRAIN sayımları, hizalı n-gramlar, ilişki kuralları ve BPE sabittir.
DEV'in 4.070 sözcüklük tam paydası korunur. Loss, uyumlu ve uyumsuz adayların
birlikte bulunduğu sabit altkümede hesaplanır; loss paydası tam doğruluk paydası
değildir. TEST ve CALIB bu çalıştırmada açılmaz.

E70/P9 ve E21 sonrası üç overfitting sinyali kontrolü bağlıdır. DEV doğru
lemma+tür sayısında katı artış gerekir. Ek olarak DEV beyanlı özellik başarımı
E00'ın altına düşmemeli ve yanlış kesin lemma kararları E00'dan fazla olmamalıdır.
Yapısal denetimler, aday kimliği, geri kurma, ilişki grafiği ve çözücü amaç
fonksiyonunu da doğrular. En iyi güvenli epoch korunur; hiçbiri ilerlemezse E00
kalır. Eğitim başarımı veya morfem yolu kusursuzluğu garantisi verilmez.

Kullanım (proje kökünden, Python 3.11):

```
python -m training_controls.a1_epoch.train --run-id a1-large-20260908-v1 --through-epoch 1
```

Bu çağrı E01 sonunda devam edilebilir durumda duraklar; bu bir erken durdurma
kararı değildir. Aynı koşuyu örneğin E70 üst sınırına kadar sürdürmek için aynı
run-id ile `--through-epoch 70` kullanılır. Son tamamlanan epoch'un ağırlıkları,
Adam momentleri, adım sayısı ve rastgelelik durumu geri yüklenir. Değişmiş
kaynak/konfigürasyonla sessiz devam edilmez; eşzamanlı ikinci eğitici kilitle
engellenir. Bir A1 çağrısı A3 veya A2'yi kendiliğinden başlatmaz.

Tüm büyük çalışma dosyaları, iki snapshot kopyası ve ayrı Git deposu V: altında
tutulur. `progress.json` çalışan aşamayı, `state.json` tamamlanmış epoch'u,
`selection.json` seçilen modeli gösterir. `selected-ranker.json` gerçekten
seçilen ağırlık dosyasının kopyasıdır; eski ürün varsayılanı değiştirilmez.

GitHub için her epoch'a ait dört toplu rapor dosyası `github-outbox/epoch-NNNNNN`
altında hash ile hazır edilir. Yerel Git commit/push denenir. CLI oturumu yoksa
gönderim bekler; bağlı GitHub uygulaması ile aynı toplu dosyalar yayımlanabilir.
Ham metinler, ağırlıklar ve optimizer durumu GitHub metrik yayınına dahil edilmez.

Doğrulama:
`python -m unittest training_controls.a1_epoch.test_epoch training_controls.e70p9.test_controls -v`
