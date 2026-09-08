# 270 aday eksikliği: nedenler ve onarım sırası

İnceleme tamamlandı. Her vaka için kaynak kimliği ve metin aralığı, altın lemma/tür, mevcut analizler, sözlük kayıtları, gerçekleşme izleri, tanı grubu ve önerilen işlem kaydedildi. Bu çalışma A1 E05 ağırlıklarını, A3 seçimini, A2 eşiklerini, sözlüğü, üretim kurallarını veya referans etiketleri değiştirmedi. TEST açılmadı.

**Önceki yorumun düzeltilmesi:** %86,1871, mevcut CALIB kümesindeki dondurulmuş lemma+POS eşleştirme ölçütünün aday kapsama tavanıdır. Saf bir yüzey üretimi veya Türkçe morfolojik doğruluk tavanı değildir. 270 uyuşmazlığın 231'inde en az bir analiz vardır; 39'unda hiç analiz yoktur. Analizin bulunması onun doğru olduğu anlamına gelmez.

## Birbirini dışlayan tanı grupları

| Baskın uyuşmazlık | Sözcük | Kanıtın anlamı |
|---|---:|---|
| Soru parçacığında PART/AUX farkı | 26 | mi kökü ve soru yolu var; beklenen POS farklı |
| Aynı kökte ADJ/NUM–NOUN farkı | 89 | 77'sinde adayın kök türü bile referansla aynı; çekim sonrası tür NOUN |
| Diğer tür okuması / referans incelemesi | 36 | Aynı lemma var; doğru tür okuması eksik veya kaynak tür politikası farklı |
| Lemma/türetim sınırı farklı, uyumlu son tür var | 66 | Referans lemma bir gerçekleşme sınırında veya k→ğ türetim allomorfunda mevcut |
| Lemma ve tür birlikte incelenmeli | 6 | Sınır ve etiket birlikte uyuşmuyor |
| Düzeltme işareti / yazım karşılığı | 15 | Sözlükte/analizde şapkalı karşılık veya alternatif sorgu kanıtı var |
| Kaynak yazımı / konuşma biçimi | 8 | Yazım veya kullanım varyantı için inceleme gerekiyor |
| Bitişik sayı, ifade veya yineleme | 7 | Genel sözcük eklemekten farklı bir üretim/temsil ailesi gerekiyor |
| Sözlük kökü veya tür okuması yok | 10 | Aranan sözlük okuması bulunamadı; ekleme öncesi bağımsız kaynak gerekiyor |
| Kök var; geçiş/metadata engeli | 7 | Dar kural veya metadata engelleri belirlendi |
| **Toplam** | **270** | |

Bunlar baskın engel gruplarıdır; tek bir vakada ek engeller bulunabilir. Örneğin vicahiye, şapkasız yazımın yanında bir fonoloji hatası da içerdiğinden son gruba alındı. Otomatik ön taramada sözlük grubundaydı; inceleme kararı ayrı kaydedildi. Tür grubundaki kişi adları da yeni sözlük okumalarına ihtiyaç duyabilir. Dolayısıyla “yalnızca 10 gerçek sözlük eksiği var” sonucu çıkarılamaz.

## Çalıştırılarak doğrulanan somut engeller

1. **vicahîye:** `vicahî/ADJ` sözlükte bulunuyor. `hlE0016 / CASE_DAT / ye`, `last_segment` kısıtından reddediliyor. Motorun `VOWELS='aeıioöuü'` denetimi son `î` harfini ünsüz sayarken son ünlü hesabı `i` olarak normalize ediyor. Ses değişimi denetimleri birbiriyle tutarsız. Yalnızca şapkasız girdiyi düzeltmek yeterli değil.
2. **Taylor'ın:** kök PROPN olarak var. `hlE0031 / CASE_GEN / ın`, `WRONG_ALLOMORPH` nedeniyle reddediliyor; yazımdaki son ünlü `o` alınarak `u` uyumu bekleniyor. Alternatif `Taylor'un` sorgusu analiz veriyor. Bu doğru yazım önerisi değil, sesletim metadata ihtiyacını gösteren karşılaştırmadır.
3. **Neniz:** `ne` kökü var. `ylE0032 / POSS_2_PLUR / niz`, `possessive_paradigm=NE` kısıtından reddediliyor. `neyiniz` sorgusu NOUN/PRON analizi veriyor; kaynakta beklenen ADJ ayrıca incelenmeli.
4. **Keşkeymiş:** `keşke` ADV/INTJ kayıtları END evresinde başlıyor ve geçiş sınıfı listesi boş. Ek-fiil kullanımına izin veren yol açılmıyor. Her zarf için sınırsız çekim açmak yerine belgeli kullanım lisansı gerekir.
5. **Bununla:** `bu→bunun` GEN geçişi var; CASE evresinden INS geçişi yok. Zamire özel araçlık paradigması gerekir; bütün sözcüklere iki durum eki zinciri açılması önerilmiyor.
6. **gözyaşları:** `gözyaşı` kaydı `CompoundP3sg; Roots:göz-yaş` içeriyor. Mevcut bağlı kök yükleyicisi yalnızca alfabetik tek parça `Roots` değerlerini işliyor; tireli bileşik bu kapsamın dışında kalıyor.
7. **Yasası'nın:** kesme, kök `yasa` sonrasında değil. Mevcut arama yalnız kök uzunluğundaki kesmeyi kabul ediyor. `Yasasının` sorgusu analiz veriyor; kaynak yazımı ile kesme politikası birlikte ele alınmalı.

Ek olarak **İMKB'nin** kaydı PROPN olsa da `secondary=Abbrv` taşımıyor. Kısaltma sesletim yolu devreye girmiyor; kaynak NOUN etiketi de ayrı bir uyuşmazlık. Alternatif girdi sorguları özgün girdide kazanım sayılmadı.

## Sözlük genişletmeden önce çözülmesi gereken temsil ayrımı

`duygusal` için `duygu + RELATED`, `güzelliğinden` için `güzel + A_NESS + …`, `gerçekleştirilen` için `gerçek + BECOME + …` yolları mevcut. Motor analizde başlangıç kökünü `lemma` alanında koruyor; referans birçok yerde türemiş gövdeyi lemma olarak bekliyor. 66 sınır eşleşmesinin tamamı yeni türetim kuralı ihtiyacı değildir: `yaşındaydı/yaşındayım` örneklerinde kaynak lemma, CASE_LOC sonrasındaki `yaşında` biçimidir. Tam ek yolu ve özellik eşdeğerliği ayrıca kanıtlanmalıdır.

Tür uyuşmazlıkları da tek tür problem değil. Soru parçacığı mI'nin AUX olarak etiketlenmesi UD Türkçe kuralıdır; yerel motorun PART üretmesi sözlükte `mi` bulunmaması değildir. Türkçe ağaç bankalarının tür politikaları arasında farklar bulunduğu resmi belgede de belirtilir. [UD Türkçe rehberi](https://universaldependencies.org/tr/)

IMST istatistikleri PART etiketinin kullanılmadığını ve ADJ/NUM üzerinde nominal özellikler bulunduğunu gösterir. Bu, yerel izlerde görülen adlaşma farkının neden özel bir eşleştirme sözleşmesi gerektirdiğini destekler; her referans etiketini dilbilimsel olarak doğru ilan etmez. [IMST belgesi](https://universaldependencies.org/treebanks/tr_imst/index.html)

IMST'nin yarı otomatik dönüşüm geçmişi vardır. `Tokum/PROPN`, `Yeter/PROPN` veya yumuşamış `teyzeciğ` gibi referanslar incelemeye işaretlendi; hiçbiri otomatik değiştirilmedi. [Veri kümesi açıklaması](https://github.com/UniversalDependencies/UD_Turkish-IMST/blob/master/README.md)

## 81 yanlış kabulle ilişkisi

Her eşikte kabul edilen 81 yanlış kök+tür kararının **77'si bu 270 vakayla aynı sözcüklerdir**. Bunların 74'ü tür veya lemma sınırı gruplarında, 2'si düzeltme işareti grubunda, 1'i geçiş/metadata grubundadır. Bu listeler bağımsız 351 hata değildir. Tek gruplu her analizi reddetmek, ölçüm sözleşmesi uyuşmazlıklarını da fallback'e gönderir; güven kapısı tasarımı bu ayrımı kullanmalıdır.

## Önerilen onarım paketleri

1. **Dar ve yeniden üretilebilir motor hataları:** önce `î`/`â`/`û` için ses sınıfı tutarlılığı, sonra kısaltma/özel ad sesletim metadatası. Her düzeltme için geçerli ve geçersiz ek biçimleri birlikte kontrol edilmeli.
2. **Kaynaklı kök ve okuma ekleri:** Boltzmann, gradyent, Egemimarlık, Kocabeyoğlu gibi bulunmayan kökler; Devrim/Gül/Uğur gibi mevcut ortak kökün özel ad kullanımları. Kök, POS, telaffuz ve kaynak kaydı birlikte hazırlanmalı; etiket şüpheleri sözlükle ezberlenmemeli.
3. **Ayrı paradigma/temsil işi:** gözyaşı bileşikleri, zamir araçlığı, bitişik sayılar, m- yinelemesi ve çok sözcüklü ifadeler. Her aile kendi yapısal lisansını gerektirir.
4. **Kök–lemma–tür sözleşmesi:** başlangıç kökü, türemiş lemma, kök türü ve son türü ayrı tutan bir temsil tasarlanmalı. Eski ölçüm aynen raporlanmalı; yeni eşleştirme sonucu morfolojik üretim kazancı gibi sunulmamalı.

Bu aşamada yeni aday eklenmedi ve yeni başarım yüzdesi hesaplanmadı. Bir sonraki deneyde A1 E05 ağırlıkları sabit tutulmalı; özgün metinde doğru aday kazanımı, yanlış aday artışı ve seçici gerilemeler ayrı ölçülmeli. CALIB artık geliştirme incelemesine açık olduğundan nihai iddia geliştirmede kullanılmamış başka bir veriyle sınanmalıdır.

## Dosyalar ve doğrulama

`reviewed-cases.jsonl` ve `270-vaka-inceleme.md` her vakanın ayrıntısını içerir; ham cümleler yalnız yerel çalışma ve V yedeğinde tutulur. `final-summary.json` toplu sayıları, `blocker-probes.json` çalıştırılmış dar kısıt kontrollerini içerir. 270 benzersiz kaynak kimliği+aralık doğrulandı; bütün kaynak aramaları tamamlanmıştı. Dondurulmuş girdi, kaynak ve model hash'leri inceleme öncesinde ve sonrasında doğrulandı. 59 vakaya özel inceleme notu, diğerlerine gruba ve kaydedilmiş kanıta bağlı işlem önerisi eklendi. Bu, bağımsız dilbilimci hakemli etiket düzeltmesi değildir.
