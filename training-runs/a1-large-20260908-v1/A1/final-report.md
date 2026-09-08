# A1 E70 / P9 koşusu — nihai rapor

Koşu: `a1-large-20260908-v1` · Tamamlanma: 8 Eylül 2026, 16:38:16 (İstanbul).

A1, E14 sonunda art arda dokuz epoch boyunca güvenli yeni tepe oluşmadığı için `PATIENCE_9` ile durdu. Seçilen ve dondurulan model **E05** oldu. Başlangıca göre DEV'de **4 ek doğru lemma+tür seçimi** elde edildi: **3.173 / 4.070 = %77,960688**. Bu, **0,098280 yüzde puanlık** sınırlı bir artıştır.

## Sonuçlar

| Ölçüt | E00 başlangıç | E05 seçilen | E14 son |
|---|---:|---:|---:|
| Doğru lemma + tür / 4.070 | 3.169 | **3.173** | 3.167 |
| Doğru lemma + tür, tam payda | %77,862408 | **%77,960688** | %77,813268 |
| Doğru beyanlı morfolojik özellik | 3.037 | **3.040** | 3.035 |
| Yanlış kesin lemma kararı | 605 | **602** | 603 |
| TRAIN tanısal loss | 0,120687 | 0,130713 | 0,123817 |
| DEV tanısal loss | 0,368238 | **0,365004** | 0,366747 |
| Güvenlik denetimi | Başlangıç referansı | Geçti | Geçemedi |

Doğruluk, 293 DEV cümlesindeki 4.070 sözcüğün tamamını kapsar. Loss, sabit yarışan/etiketi kullanılabilir altkümede hesaplanır; DEV loss paydası 2.283'tür ve düzenlileştirme terimini içermez. TRAIN loss, önceki L-BFGS ile eğitilmiş E00'a göre E05'te daha yüksektir. DEV doğruluğundaki küçük kazanç, her ölçütte iyileşme anlamına gelmez.

Bu koşuda TEST ve CALIB açılmadı. DEV model seçiminde kullanıldığı için sonuç bağımsız test başarımı veya genel Türkçe doğruluğu olarak yorumlanamaz. Lemma+tür doğruluğu, kusursuz morfem bölümlemesi ölçüsü değildir.

## Öğrenme kapsamı ve durdurma

Başlangıç, daha önce DEV ile seçilmiş A1 büyük havuz modelidir. Adam optimizer durumu E01'de sıfırlandı; model ağırlıkları mevcut modelden alındı. Her epoch, 10.490 cümle / 103.709 sözcük kullanımlık TRAIN havuzundan elde edilmiş 55.129 yarışan, etiketli örneğin tamamından bir kez geçti.

Yalnız UA ağırlıkları güncellendi: mevcut unigram bölümleme, bağlam, hal eki ve kapsamlı kişi uyumu öznitelikleri. 243.304 TRAIN özelliği, Adam lr=0.001, batch=256, seed=20260908 ve epoch başına 216 güncelleme kullanıldı. Morfoloji/adaylar, AB04 sayımları, hizalı n-gramlar, ilişki kuralları, arama sınırları ve BPE sabit kaldı.

Yeni tepe için tam çözücü DEV lemma+tür sayısında katı artış ve güvenlik denetimlerinin geçmesi gerekti. Beyanlı özellik doğruluğu E00'ın altına düşemedi; yanlış kesin lemma kararları E00'ı aşamadı. Aday kimliği, geri kurma, ilişki grafiği ve çözücü amaç fonksiyonu denetlendi.

E05'te sabır 0/9'a sıfırlandı. E06–E14 arasında yeni güvenli tepe oluşmadı ve E14'te 9/9 ile durdu. E20 sonrasındaki üç ardışık overfitting sinyali kuralı E21'de başlayacaktı; koşu daha önce bittiği için bu kural tetiklenmedi. E14'ün beyanlı özellik sayısı 3.035 ile E00'ın altındadır; son ağırlıklar seçilmedi.

| Epoch | DEV doğru | DEV % | TRAIN loss | DEV loss | Güvenli | En iyi | Sabır |
|---|---:|---:|---:|---:|---|---|---|
| E01 | 3172 | 77.9361 | 0.139803 | 0.364525 | Evet | E01 | 0/9 |
| E02 | 3171 | 77.9115 | 0.136758 | 0.366512 | Evet | E01 | 1/9 |
| E03 | 3170 | 77.8870 | 0.134240 | 0.364123 | Evet | E01 | 2/9 |
| E04 | 3170 | 77.8870 | 0.132189 | 0.364409 | Evet | E01 | 3/9 |
| E05 | 3173 | 77.9607 | 0.130713 | 0.365004 | Evet | E05 | 0/9 |
| E06 | 3170 | 77.8870 | 0.129229 | 0.362887 | Evet | E05 | 1/9 |
| E07 | 3169 | 77.8624 | 0.128107 | 0.363953 | Hayır | E05 | 2/9 |
| E08 | 3170 | 77.8870 | 0.127224 | 0.366328 | Evet | E05 | 3/9 |
| E09 | 3167 | 77.8133 | 0.126457 | 0.365208 | Hayır | E05 | 4/9 |
| E10 | 3170 | 77.8870 | 0.125751 | 0.365613 | Evet | E05 | 5/9 |
| E11 | 3170 | 77.8870 | 0.125296 | 0.365538 | Evet | E05 | 6/9 |
| E12 | 3170 | 77.8870 | 0.124636 | 0.364937 | Evet | E05 | 7/9 |
| E13 | 3169 | 77.8624 | 0.124156 | 0.365864 | Evet | E05 | 8/9 |
| E14 | 3167 | 77.8133 | 0.123817 | 0.366747 | Hayır | E05 | 9/9 |

## Kalan açıklığın anlamı

E05'te 897 kullanım doğru lemma+tür seçimine ulaşmadı. Mevcut aday/eşleme ölçümünde doğru aday 3.420 kullanımda bulunuyor: gözlenen kapsam tavanı %84,029484. Bunun 247'sinde doğru aday bulunduğu halde tercih edilmedi; diğer 650 kullanım aday veya referans eşleme kapsamı dışında kaldı. Bu ikinci grup yalnız puanlayıcı eğitimiyle kapanamaz. Kapsam ölçüsü eşleme/etiketleme sınırlarını da içerdiğinden 650 kaydın tamamını sözlük hatası saymak doğru olmaz. %92 hedefine bu koşuda ulaşılmadı.

## Yedek ve bütünlük doğrulaması

V: üzerindeki koşu dizini:

`V:\TurkTokenizer\Yedekler\A123-E70-P9-OF3\runs\a1-large-20260908-v1\A1`

Her epoch iki SHA-256 doğrulanmış snapshot oluşturdu. Saklama politikası her kopyada E00, en iyi E05 ve son iki epoch E13/E14'ü koruyor. İki kopyada toplam sekiz tutulan snapshot'ın ağırlık, optimizer, audit ve durum dosyaları yeniden doğrulandı.

`selected-ranker.json`, her iki E05 ağırlık kopyasıyla birebir aynı:
`eed03755d0026c36b055f68ba18daf7188037cbac85265b24add5c2c7a182ff2`

Her iki E05 optimizer yedeğinde 243.304 boyut, 1.080 Adam adımı, sonlu momentler ve geri yüklenebilir rastgelelik durumu doğrulandı. 11 dondurulmuş girdinin ve 71 kaynak kod dosyasının hash'i değişmedi. Eğitici kilidi kaldırıldı; süreç tamamlandı. Önceden yapılan 16 birim testi geçti; nihai kontrol için eğitim yeniden çalıştırılmadı.

## GitHub ve bildirim aksaması

E01–E14 için ayrı ayrı toplu metrik/log commit'leri yayımlandı. Her epoch'ta dört dosyanın toplam 56 Git blob hash'i yerel outbox içeriğiyle eşleşti; 14 commit'in ebeveyn zinciri doğrulandı. Ham eğitim metni, ağırlık veya optimizer dosyaları bu metrik yayınına eklenmedi.

[GitHub epoch kayıtları](https://github.com/ozelturktarkan/TurkTokenizer/tree/codex/e70-p9-logs/a1-large-20260908-v1-A1/training-runs/a1-large-20260908-v1/A1)

240 saniyelik otomasyon kurulmuş olmasına rağmen inceleme anında çalıştırma kaydı yoktu ve son çalıştırma zamanı boştu. Bu nedenle istenen periyodik bildirimler gerçekleşmedi. Kesin tetiklenmeme nedeni doğrulanamadı; otomasyonun kurulmuş olması çalıştığının kanıtı olarak sunulmamalıydı.

Yerel epoch commit'leri ve V: snapshot'ları üretildi. Git CLI kimlik doğrulaması hazır olmadığı ve heartbeat hiç tetiklenmediği için GitHub yayın kuyruğu gecikti. Bekleyen kayıtlar bu oturumda bağlı GitHub uygulamasıyla tamamlandı. Bildirim zamanlayıcısının düzeltildiği iddia edilmiyor; başarısız takip otomasyonu duraklatıldı.

A3 ve A2 başlatılmadı. Seçilen E05 deneme çıktısı olarak kaydedildi; ürünün varsayılan modeli değiştirilmedi.
