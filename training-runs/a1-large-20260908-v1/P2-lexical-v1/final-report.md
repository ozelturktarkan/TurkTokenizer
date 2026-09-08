# S06E E05 P2: kök, türemiş lemma ve kaynak politikası

P1 morfolojisi ve E05 ağırlıkları sabitken, ayrı bir sözlüksel görünüm puanlayıcısı geliştirildi. Morfolojik aday, ek yolu, başlangıç kökü ve BPE kimliği değiştirilmedi. Yeni bilgi, eski adayın üzerine ayrı lexical_analyses / lexical_decision alanlarıyla eklendi.

## Eski ölçütle aynı koşullarda sonuç

| Kol | DEV kök+tür /4070 | DEV özellik | DEV yanlış kesin | CALIB kök+tür /2266 | CALIB özellik | CALIB yanlış kesin |
|---|---:|---:|---:|---:|---:|---:|
| Önceki seçili E05 | 3173 | 3040 | 602 | 1738 | 1669 | 376 |
| Karma TRAIN ×0.00 | 3172 | 3039 | 602 | 1739 | 1671 | 377 |
| Karma TRAIN ×0.25 | 3170 | 3037 | 605 | — | — | — |
| Karma TRAIN ×0.50 | 3166 | 3035 | 606 | — | — | — |
| Karma TRAIN ×1.00 | 3171 | 3041 | 607 | — | — | — |
| IMST TRAIN ×0.00 | 3172 | 3039 | 602 | 1739 | 1671 | 377 |
| IMST TRAIN ×1.00 | 3174 | 3045 | 595 | 1751 | 1680 | 367 |

Karma eğitimde DEV seçimi 0 oldu; diğer katsayılar CALIB’de çalıştırılmadı. IMST başlığı ayrı ve açıkça keşif amaçlı bir uzantıdır. Kendi DEV seçimi mühürlendikten sonra CALIB kontrolü yapıldı; CALIB’ye göre katsayı değiştirilmedi. Referanslar ve tarihsel ölçüm kodu değiştirilmedi.

## Tek tahmin edilen sözlüksel lemma+tür

| Kol | DEV /4070 | CALIB /2266 |
|---|---:|---:|
| Karma başlık; eski P1 tercihi | 3239 | 1809 |
| IMST başlığı; eski P1 tercihi | 3263 | 1819 |
| IMST başlığı + seçim katkısı | 3350 | 1876 |

### DEV

Son sözlüksel lemma+tür: 3350/4070 = %82.3096. Beyan edilen sekiz özellik alanıyla birlikte 3210/4070.

Yalnız temsil katmanı: 101 eşleşme düzeldi, 10 gerileme oldu; net +91. Aynı IMST başlığıyla aday seçimi açılınca ilave 114 düzelen / 27 bozulan sözlüksel tercih var; net +87.

Eski kök+tür ölçütünde P1’e göre 18 düzelen / 16 bozulan kayıt; net +2. 166 sözcüğün seçilen morfolojik aday kimliği değişti.

Doğru cevap herhangi bir görünümde 3676/4070 sözcük için bulunuyor. Bu seçilmiş doğruluk değildir; görünüm havuzunun kapsamasıdır. Yeni morfolojik yol üretilmedi.

### CALIB

Son sözlüksel lemma+tür: 1876/2266 = %82.7891. Beyan edilen sekiz özellik alanıyla birlikte 1756/2266.

Yalnız temsil katmanı: 80 eşleşme düzeldi, 0 gerileme oldu; net +80. Aynı IMST başlığıyla aday seçimi açılınca ilave 72 düzelen / 15 bozulan sözlüksel tercih var; net +57.

Eski kök+tür ölçütünde P1’e göre 19 düzelen / 7 bozulan kayıt; net +12. 105 sözcüğün seçilen morfolojik aday kimliği değişti.

Doğru cevap herhangi bir görünümde 2123/2266 sözcük için bulunuyor. Bu seçilmiş doğruluk değildir; görünüm havuzunun kapsamasıdır. Yeni morfolojik yol üretilmedi.

## Sonucun kapsamı

Eski lemma alanı başlangıç köküdür; yeni görünüm türemiş sözlüksel lemmayı ayrıca bildirebilir. Bu iki çıktı türündeki puanları tek bir morfolojik doğruluk artışı gibi toplamak doğru değildir. Görünüm başlığı tek bir seçenek tahmin eder; bütün seçeneklerden referansa uyanı sonradan seçerek başarı hesaplanmadı.

Yeni özellik ölçüsü VerbForm, Polarity, Voice, Person[psor], Number[psor], Case, Number ve Person alanlarını denetler. Case/Number/Person yeni ölçüde ADJ/NUM üzerinde de denetlenir. Bu kapsam eski özellik ölçüsünden farklıdır; tam ek yolu, Tense/Aspect/Mood kapsamı veya bütün anlam doğruluğu değildir.

IMST politikası, bu veri kaynağındaki lemma/tür geleneğine yönelik açık bir çıktı politikasıdır. Bütün Türkçe metinlerde evrensel tür doğruluğu gibi sunulmaz. DEV ve CALIB geliştirmede görülmüştür; yeni bağımsız test değildir. TEST bu çalışmada açılmadı. %92 morfolojik doğruluk veya <%8 fallback hedefi bu sonuçla sağlanmış sayılmaz.

## Eğitim ve kontroller

- Karma: 10490 TRAIN cümlesi, 60389 karşılaştırmalı örnek, 100 optimizasyon adımı. Yakınsama durumu: False; STOP: TOTAL NO. of ITERATIONS REACHED LIMIT. Eğitim kaybı 0.315493 → 0.199070.
- IMST: 3260 TRAIN cümlesi, 18075 karşılaştırmalı örnek, 87 optimizasyon adımı. Yakınsama durumu: True; CONVERGENCE: NORM OF PROJECTED GRADIENT <= PGTOL. Eğitim kaybı 0.358969 → 0.160959.

2904 cümle çıktısında BPE geri kurma doğrulandı; 224.309 ID ve 256 bayt davranışı korundu. Beş şema testi ve API kontrolleri geçti. IMST başlığına ait elle yazılmış 8 bağlam tanısının 7 tanesi beklenen lemma+türle eşleşti; bunlar bağımsız test değildir.

Her yeni çözücü çıktısının toplam puanı ayrı yordamla yeniden hesaplandı; aday ve ham metin değişmezliği denetlendi. Sıfır katkılı IMST kontrolü, önceden doğrulanmış P1 kararlarını yeniden kullandı; onun için yeni bir çözücü koşusu yapılmış gibi sayı verilmedi.

## Teslim ve tercih

IMST DEV seçimi: **1.0**. Tarihsel E05’e göre her iki havuzdaki eski kök+tür, özellik ve yanlış kesin karar gerilememe denetimi: **True**. Yeni sürümün açık kullanım girişi `s06e_p2_policy.Tokenizer(strength=1.0)`; eski proje varsayılanı değiştirilmedi.

Kaynak, modeller ve yeni özel çıktılar V üzerinde iki ek kopyaya kaydedilir. Aynı fiziksel sürücüdeler; önceki dondurulmuş proje tabanı gerekir. GitHub kapsamı kod, test, toplu rapor ve hash kayıtlarıdır. Model ağırlıkları ve ham kaynak cümleleri yayımlanmaz.

## Kaynaklar

- [UD Türkçe](https://universaldependencies.org/tr/): kaynaklar arasında tür politikası farklılıkları.
- [IMST](https://universaldependencies.org/treebanks/tr_imst/index.html): referans etiket sözleşmesi.
- [Bedir ve arkadaşları, 2021](https://aclanthology.org/2021.law-1.12/): Türkçe türetim ve sıfır biçimbirimlerin temsil sorunları.
- [Hakkani-Tür ve arkadaşları, 2000](https://aclanthology.org/C00-1042/): türetim sınırlarıyla çekim grupları. Buradaki model o makalenin birebir uygulaması değildir.
