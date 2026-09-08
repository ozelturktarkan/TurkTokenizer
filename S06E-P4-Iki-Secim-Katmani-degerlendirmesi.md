# S06E P4: iki seçim katmanının ayrı onarımı

DEV seçimi **HR_0.25**; CALIB koruma denetimi sonrası tutulan yapı **HR_0.25**. Varsayılan eski sürüm otomatik değiştirilmedi.

## Ne değişti?

Çıktı başlığı, aynı morfolojik adayın görünümleri arasında koşullu bir seçim öğreniyor. Bu başlık tek başına değiştiğinde morfolojik aday, cümle puanı, eski güven kararı ve BPE ID’leri aynı kalıyor.
Sıralayıcı, eski P2 tam cümle max-marjinal puanlarını eğitimde sabit başlangıç puanı olarak kullanıyor. Pozitif etiket yalnızca başlığın gerçekten yayımladığı görünüm referansla uyumluysa veriliyor; aday içindeki seçilmeyen gizli bir doğru görünüm yeterli sayılmıyor.
Eski ve yeni başlık için aynı rekabetçi TRAIN sözcüklerinde ayrı sıralayıcılar eğitildi. Yeni sıralama katkısı yalnız son ana geçişe ekleniyor; Q0 ve UA referans geçişleri, eski P2 puan başlığı, AB04 ve n-gram ağırlıkları korunuyor.

## Çıktı başlığı tek başına: DEV

| Başlık katkısı | Görünüm kök+tür /4070 | Görünüm özellik |
|---|---:|---:|
| 0.00 | 3350 | 3210 |
| 0.25 | 3352 | 3209 |
| 0.50 | 3356 | 3211 |
| 1.00 | 3359 | 3212 |

Başlık seçimi 1; bu koşullarda yerel kök+tür 3174, yerel özellik 3045, yanlış kesin karar 595 olarak aynen kaldı.

## Tam çözücü: DEV

| Koşul | Yerel kök+tür | Yerel özellik | Yanlış kesin | Görünüm kök+tür | Görünüm özellik | Koruma |
|---|---:|---:|---:|---:|---:|---|
| P2 | 3174 | 3045 | 595 | 3350 | 3210 | Geçti |
| H | 3174 | 3045 | 595 | 3359 | 3212 | Geçti |
| R_0.25 | 3181 | 3058 | 581 | 3366 | 3231 | Geçti |
| R_0.50 | 3174 | 3053 | 577 | 3361 | 3231 | Geçti |
| R_1.00 | 3110 | 2989 | 611 | 3317 | 3179 | Geçmedi |
| HR_0.25 | 3185 | 3060 | 591 | 3373 | 3228 | Geçti |
| HR_0.50 | 3175 | 3054 | 577 | 3370 | 3230 | Geçti |
| HR_1.00 | 3113 | 2989 | 618 | 3330 | 3182 | Geçmedi |

H: yalnız yeni başlık. R: eski başlıkla hizalı yeni sıralayıcı. HR: yeni başlıkla hizalı yeni sıralayıcı. R/HR sonundaki sayı, öğrenilen sıralama katkısının katsayısıdır.
DEV paydası 4.070 sözcük / 293 cümle. Başlık seçimi ve sıralama seçimleri DEV ile yapıldı. Yeni bağımsız test sonucu değildir.

## Mühürlenmiş CALIB denetimi

CALIB’de yalnız P2 kontrolü ve DEV’de seçilmiş tek yapı karşılaştırıldı; diğer kollar CALIB’ye göre yeniden seçilmedi.

| Koşul | Yerel kök+tür /2266 | Yerel özellik | Yanlış kesin | Görünüm kök+tür | Görünüm özellik |
|---|---:|---:|---:|---:|---:|
| P2 | 1751 | 1680 | 367 | 1876 | 1756 |
| HR_0.25 | 1763 | 1692 | 360 | 1897 | 1774 |

Korunan yapının DEV+CALIB görünüm kök+tür başarısı **5270/6336 = %83,18**; P2 5226/6336. Ayrı yerel başlangıç kökü+tür ölçütü **4948/6336 = %78,09**. Bu iki ölçüt birbirinin yerine kullanılmamalı.
Eski kesin karar sayısı 5637, yeni 5628; yanlış kesin karar 962 → 951. Karar vermekten kaçınma da değişebildiği için yanlış kesin karardaki azalmanın tamamı düzeltilen hata olarak sayılmıyor. Gerçek tercih düzeltmeleri aşağıdaki eşlenmiş karşılaştırmada ayrı gösteriliyor.

| Ölçüt | Düzeltilen eski hata | Yeni gerileme |
|---|---:|---:|
| preferred_lemma_pos | 46 | 23 |
| preferred_declared_features | 53 | 26 |
| predicted_view_lemma_pos | 93 | 49 |
| predicted_view_features | 84 | 48 |

## Kalan iki seçim katmanı

- Yeniden sıralamayla erişilebilir yanlış çıktı: **435** (P2: 518).
- Doğru görünüm var, fakat hiçbir adayda başlığın tepe seçimi değil: **94** (P2: 55).
- Eşleşen görünüm yok veya referans çözülemiyor: **537** (P2: 537).
- Sabit adaylarda herhangi bir görünüm kapsamı 5799/6336; seçili başlıkla erişilebilir kapsam 5705/6336. Bunlar motorun fiziksel veya evrensel doğruluk tavanı değildir.

Başlığın bütün adaylarda doğru görünümü geri plana attığı hata grubundaki artış bir gerilemedir. Sıralamayla erişilebilir yanlışlar grubundaki azalmanın tamamı çözülmüş hata değildir; bazı vakalar başlık engeli grubuna geçmiştir. Toplam tercih kazanımı eşlenmiş karşılaştırmayla ölçülmelidir. P4 iki katmanı tamamen onarmış sayılmaz.
Sonraki başlık deneyinde yalnız seçilmiş çıktı başarısını değil, doğru görünümün adaylar arasında erişilebilir kalmasını da koruyan bir eğitim hedefi sınanmalı. Bu tanıya göre mevcut DEV/CALIB seçimi veya ağırlıkları yeniden ayarlanmadı.

## A2 ve doğrulama

- P2: önceden belirlenen 121 eşik çiftinde iki ölçütte birlikte %92 sağlanamadı.
- HR_0.25: önceden belirlenen 121 eşik çiftinde iki ölçütte birlikte %92 sağlanamadı.

Başlık: 7424 sözcük, 15240 aday içi örnek. Sıralama: her iki modelde aynı 16516 TRAIN sözcüğü. Toplam TRAIN 3.260 IMST cümlesi. DEV/CALIB/TEST etiketleri kayıp fonksiyonuna girmedi.
Başlıkta her sözcüğün toplam eğitim ağırlığı eşit tutuldu. Sıralama kaybı, dondurulmuş cümle marjinal puanları üzerinde yerel bir yaklaştırmadır; ortak CRF azami olabilirlik eğitimi olarak sunulmuyor. Son kararlar gerçek tam çözücüyle tekrar ölçüldü.
Sıfır katkı ve başlık-only ayrımı 18 cümlede, BPE geri dönüşü 19 kontrolde doğrulandı. Aday sırası, etiket sızıntısı, yayımlanan görünümle pozitif etiket uyumu ve A2’nin tek geçişte uygulanması kontrol edildi. Ağırlıklı kaybın türevi sayısal sonlu farkla ve puan kaydırma değişmezliğiyle doğrulandı.
Her yeni tam çözücü çıktısında bağımsız puan toplamı, aday havuzu ve metin geri dönüşü doğrulandı. 224.309 BPE/morfoloji ID’si aynı kaldı.
İlk puan önbelleği denemesi boş bilinmeyen işaretini gerçek adayla karşılaştıran kontrol hatasında durdu; kayıt ve betik saklandı. Düzeltmeden sonra 3.260 cümlenin tamamı cache-r1 içinde yeniden doğrulandı.
Tam morfem yolu doğruluğu ve görünüm başlığının kalibre güveni bu ölçümlerle kanıtlanmıyor. TEST açılmadı; %92 morfolojik kapsama ve <%8 fallback hedefleri otomatik sağlanmış sayılmaz.

Tanısal 15 örnek (seçim veya yeniden eğitimde kullanılmadı): P2: 13/15, H: 13/15, HR_0.25: 13/15.
“Sen geldin mi?” örneğinde doğru soru adayının kazanana puan uzaklığı P2'de 28.35, seçili yapıda 18.72. Uzaklığın azalması doğru seçimin yapıldığı anlamına gelmez; bu örnek hâlâ çözülemedi.

## Kullanım ve kayıtlar

`from s06e_p4 import load_selected; rt = load_selected(); out = rt.analyze_sentence("Sen geldin mi?")`

Model: `results_layers_p4/model-location.json`. Seçim: `results_layers_p4/selection.json`. Tam karşılaştırma: `results_layers_p4/comparison.json`. Yedek doğrulaması: `results_layers_p4/backup-receipt.json`.
İki V kopyası artımlıdır ve aynı fiziksel sürücüdedir; eski proje tabanına ihtiyaç duyar. P2/P3 kaynakları ve sonuçları değişmedi. Yeni GitHub yayını yapılmadı; önceki P2 paketinin kapsam onayı ayrı olarak bekliyor.
