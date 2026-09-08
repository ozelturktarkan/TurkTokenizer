# S06E P3: YÖNT / 5N1K dilbilgisel özellik deneyi

DEV seçimi **C0_P2**; CALIB denetimi sonrası korunan yapı **C0_P2**. Varsayılan sürüm otomatik değiştirilmedi.

## Sabit adaylarla DEV karşılaştırması

| Koşul | Yerel kök+tür | Yerel özellik | Yanlış kesin kök+tür | Sözcüksel görünüm kök+tür | Görünüm özellik | P2 koruma koşulu |
|---|---:|---:|---:|---:|---:|---|
| C0_P2 | 3174 | 3045 | 595 | 3350 | 3210 | Geçti |
| GOV | 3174 | 3046 | 597 | 3349 | 3211 | Geçmedi |
| AGR | 3174 | 3045 | 596 | 3349 | 3209 | Geçmedi |
| LOCAL_COMBINED | 3173 | 3044 | 596 | 3349 | 3209 | Geçmedi |
| JOINT_HALF | 3176 | 3048 | 596 | 3351 | 3213 | Geçmedi |
| JOINT_FULL | 3175 | 3047 | 598 | 3348 | 3211 | Geçmedi |

Payda: 4.070 sözcük / 293 cümle. Sözcüksel görünüm UD_IMST çıktı politikasını kullanır; yerel kök ile ayrı bir ölçüttür.
GOV: istem/edat; AGR: kişi/iyelik/soru; LOCAL_COMBINED: birlikte yerel puan; JOINT_HALF ve JOINT_FULL: seçilmiş adaylar arasındaki etkileşimlerle yarım/tam katkı.

## CALIB ve kalan hata

| Koşul | Yerel kök+tür | Yerel özellik | Yanlış kesin kök+tür | Görünüm kök+tür | Görünüm özellik |
|---|---:|---:|---:|---:|---:|
| C0_P2 | 1751 | 1680 | 367 | 1876 | 1756 |

CALIB paydası 2.266 sözcük / 382 cümle. Korunan yapının iki havuzdaki görünüm kök+tür başarısı **5226/6336 = %82,48**; P2 5226/6336.
Doğru görünüm adayda mevcut fakat seçilememiş: **573**. Görünüm eşleşmesi bulunmayan veya çözülemeyen referans: **537**. Sabit çıktı sözleşmesinde aday kapsamı 5799/6336; bu oran dilbilgisi motorunun fiziksel tavanı değildir.
Ek çıktı denetimi: **518** yanlış, başka bir yerel aday seçilerek doğru görünüme ulaşabilir. **55** örnekte doğru görünüm vardır fakat dondurulmuş görünüm başlığı hiçbir adayda onu tepeye koymaz. Bu ikinci grup yalnız yerel adayları yeniden sıralamakla çözülemez. Sabit başlıkla erişilebilir çıktı kapsamı **5744/6336 = %90,66**.

## A2: karar verme doğruluğu ve kapsamı ayrı

- C0_P2: önceden belirlenmiş 121 eşik çiftinde iki ölçütte birlikte %92 hedefi sağlanamadı.

Bu kalibrasyon, kabul edilen alt kümenin CALIB üzerindeki ampirik doğruluğudur. Tüm sözcüklerin %92’sini doğru çözme, tam morfem yolu doğruluğu veya görünüm başlığının kalibre edilmiş güveni anlamına gelmez. DEV ve CALIB daha önce görülmüş havuzlardır; bağımsız genelleme kanıtı değildir. TEST bu deneyde açılmadı.

## Eğitim ve doğrulama

- 3.260 IMST TRAIN cümlesi; 4856 rekabetçi yerel örnek. Yeni insan etiketlemesi yapılmadı; mevcut referansla uyumlu alternatifler birlikte pozitif tutuldu.
- A3: 192 sabit TRAIN bağlamı, 338 hedef; her üç aile için iki madencilik/eğitim turu. Eski UA/AB04/N-gram beşli ağırlıkları 1 olarak sabit kaldı.
- İstem tercihleri, TRAIN’de gözlenen fiil/ses çatısı ve tümleç durumlarından öğrenildi; kapsamlı anlam bazlı istem sözlüğü oldukları varsayılmadı. Aday silme yapılmadı.
- Uzun bağlantılar yalnızca önceki planlayıcının tuttuğu kısmi planlar üzerinde puanlandı. Bu çalışma, daha önce budanmış planları geri getirmez; tam cümle sözdizimi çözümleyicisi değildir.
- Yedi birim testi, küçük zincirde kaba kuvvetle tam DP/marj eşitliği, 15 cümlede sıfır katkının P2’ye eşitliği ve aday sırası değişmezliği kontrol edildi.
- Her yeni değerlendirme çıktısında aday havuzu, bağımsız puan toplamı, ham metin ve BPE geri dönüşü denetlendi. 224.309 eski ID korundu. Seçilen API ile ek dört geri dönüş kontrolü geçti.
- Vurgu/sözcük sırası paketi bu ilk dar deneyin kapsamı dışında tutuldu.

Birleşik kolun son eğitimden önceki 338 sabit karşıtında 33 yanlış tercih vardı; bunların 12 tanesinde yeni özellik farkı tamamen sıfırdı. Bu karşıtlarda yalnız bu 26 bileşenin ağırlığını değiştirmek ayrım üretemez. Bu bir TRAIN tanısıdır, test doğruluğu değildir.

Tanısal, bağımsız olmayan 15 örnek: C0_P2 13/15, JOINT_HALF 13/15, JOINT_FULL 13/15. Bu sonuçlar seçim veya yeniden eğitim için kullanılmadı.

## Dosyalar ve devam

- `results_grammar_p3/comparison.json`: tüm karşılaştırmalar ve düzelme/gerileme sayıları.
- `results_grammar_p3/calibration.json`: eşikler, kabul kapsamı, Wilson aralıkları ve çevrimiçi doğrulama.
- `results_grammar_p3/model-location.json`: V üzerindeki model ve SHA256.
- `results_grammar_p3/backup-receipt.json`: iki artımlı V kopyasının doğrulama kaydı.
- Kullanım: `from s06e_p3 import load_selected; rt = load_selected(); rt.analyze_sentence("Sen geliyor musun?")`.
- Eski P2 kodu/modeli ile önceki dondurulmuş 47 dosya değişmedi. Bu P3 paketi eski proje tabanına ihtiyaç duyan artımlı bir deneydir.
- GitHub’a yeni yayın yapılmadı; önceki P2 dosya paketi için otomatik onay denetiminin istediği kapsam onayı hâlâ bekliyor.

Kaynak ve araştırma gerekçesi: `research/2026-09-09-yont-5n1k/arastirma.md`.

## Soru/nota örneğinde puan kanıtı

`Sen geldin mi?` cümlesinde doğru soru adayı mevcut. Tutulan aramadaki en iyi soru yolunun kazanana uzaklığı P2’de 28.3531, yarım katkıda 26.6545, tam katkıda 24.9559 puan. Yeni katkı farkı daralttı fakat tercihi çevirmedi. Bu örnek için adayın atlanması açıklaması desteklenmiyor. Ayrıntı: `results_grammar_p3/question-score-audit.json`.
