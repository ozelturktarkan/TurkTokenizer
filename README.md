# TürkTokenizer

**Türkçe için morfolojik bölümleme, BPE yedeği ve deneysel YÖNT bağlantıları.**

**Kurucu / Mimar: Tarkan Özel** · Araştırma sürümü: **0.1.0rc1** · Çalışma motoru: **Rust / Windows x64**

TürkTokenizer, Türkçe sözcüklerin kök ve ek yapısını incelenebilir biçimde temsil etmek için geliştirilen bir araştırma projesidir. Kararlı P21 sözleşmesi; kök/ek adayları, bağlamsal sıralama, güven kapısı ve gerektiğinde kayıpsız BPE yedeğini kapsar. P119 bu hattın Rust uygulamasıdır. P128, belirli morfolojik adaylar arasında sınırlı yüklem–özne–nesne/sahip ilişkileri kurar. P129 ise bu bilgiyi BPE kullanan küçük bir dil modeline aktarma deneyidir.

## Neden bu proje?

Türkçenin üretken ek yapısını açıkça temsil etmenin küçük modellerde faydalı olup olmadığını araştırıyoruz. BPE parçalarının morfem sınırlarıyla örtüşmesi zorunlu değildir; fakat bu, BPE'nin Türkçeyi anlayamadığını veya alternatifimizin daha başarılı olduğunu tek başına göstermez. Hedefimiz, açık ölçümlerle yarar sağlayan bir Türkçe altyapısı geliştirmek ve araştırmacıların devam ettirebileceği kaynakları paylaşmaktır.

Tarkan Özel'in **16.12.2015** tarihli [Bilim Dili Türkçe](docs/Bilim-Dili-Turkce-Tarkan-Ozel.pdf) yazısı projenin düşünsel çıkış noktasıdır. PDF tarihsel görüş yazısı olarak, değiştirilmeden sunulur; güncel deney sonuçlarının veya dil/zekâ üstünlüğü iddialarının bilimsel doğrulaması değildir. [Gelişim öyküsü](docs/GELISIM.md).

## Sınıflandırılmış ek sözlüğü

[**eksozlugu.md**](eksozlugu.md), çalışan Rust tablosundan üretilmiştir: **43 sınıf, 876 kayıt, 752 üretime açık kayıt**. Bunlar 876 farklı bağımsız ek anlamına gelmez; yüzey varyantları, sıfır biçimler, süreçler ve kurallar da dahildir. Örneğin `clE0001=ler`, `clE0002=lar`; ikisinin morfem kimliği `NUMBER_PL`'dir. Kısa insan okunur kayıt ID'si, morfem kimliği ve modele verilen sayısal token ID'si farklı kavramlardır. P21 toplam 345.127 ID sözleşmesini korur.

Sınıf etiketlerinde Türkçe adlardan türetilen kısaltmalar kullanılır; her kayıt bir ek değildir, `R` ve `K` etiketli sınıflar da bulunur. Sıra numarası dilbilimsel öncelik veya ağırlık değildir. Makine okunur kayıtlar [registry/](registry/) altındadır. Başlangıçtaki 843 ifadesi güncel envanter sayısı olarak kullanılmamıştır.

## Son ölçüm: P129

Aynı Qwen3-0.6B-Base modeli ve aynı BPE girdisi; 4 koşul × 3 eğitim tohumu. 7.200 eğitim sorusu; 4.800 değerlendirme sorusu. Ana ölçüm, yeni sözcük/sıra/bileşim bölümlerindeki 3.600 sentetik sorunun üç tohum ortalamasıdır.

| Koşul | Dört seçenekli OOD soru-cevap doğruluğu |
|---|---:|
| Sade BPE + görev eğitimi | %99,5926 |
| BPE + morfoloji | %98,3889 |
| BPE + morfoloji + YÖNT | %98,9074 |
| BPE + morfoloji + karıştırılmış bağlantılar | %98,5093 |

**%98,91 sözcük bölümleme doğruluğu değildir.** Bu uygulamada YÖNT kolu sade kolun 0,6852 yüzde puan gerisindedir. Graph−plain farkının bağlam bazlı %98,333 bootstrap aralığı [−1,0093; −0,3796] puandır; üç tohumda da fark olumsuzdur. Veri ajan yazımı sentetiktir; genel Türkçe anlama veya bağımsız insan değerlendirmesi değildir. Görevin tavan etkisi büyüktür. [Protokol](experiments/P129-20260924/protocol.json), [sonuç](experiments/P129-20260924/summary.json), [ham sonuçlar](experiments/P129-20260924/results/), [değerlendirme](docs/DEGERLENDIRME-P129.md).

Release'te gösterim için en yüksek YÖNT koşusu `graph-12937` seçilmiştir: %99,1667. Aynı tohumdaki sade kol %99,7222'dir. Seçim değerlendirme sonrasıdır; bağımsız üstünlük kanıtı değildir. Diğer 11 ağırlık da araştırma release'inde korunur.

12B→27B eşdeğerliği, quantize modellerde kalite artışı, daha az halüsinasyon, genel BPE üstünlüğü, MoE/VLM kazancı veya Gemma entegrasyonu bu sürümde gösterilmiş değildir. Tarihsel UPOS/UAS/LAS sonuçları farklı görevlerdir; bu tabloya bölümleme veya anlama doğruluğu olarak karıştırılmaz.

## Hızlı başlangıç — Release

1. GitHub **Releases** bölümündeki `TurkTokenizer-0.1.0rc1-windows-x64-research.zip` dosyasını indirip tamamen açın. Kaynak ZIP'i büyük çalışma verilerini içermez.
2. **Python olmadan:** `DEMO_RUST.cmd` çalıştırın. Çıktı `output/native-demo.json` olur. `RUST.cmd < examples/native-request.jsonl` ile UTF-8 JSONL akışı da kullanılabilir.
3. **İsteğe bağlı Python sarmalayıcı**, Python 3.11+ ile release kökünde:

```cmd
python -m pip install --no-deps wheels\turktokenizer_native-0.1.0rc1-py3-none-any.whl
set "TURKTOKENIZER_RUNTIME=%CD%"
python -m turktokenizer_native --text "Çocuk öğretmenin kitabını okudu."
```

```python
from turktokenizer_native import NativeTokenizer

with NativeTokenizer(r"C:\TurkTokenizer-0.1.0rc1-windows-x64-research") as tokenizer:
    text = "Çocuk öğretmenin kitabını okudu."
    ids = tokenizer.encode(text)
    assert tokenizer.decode(ids) == text
    result = tokenizer.analyze(text)
    print(result["binding"]["conditional_role_answer"])
```

`analyze_sentence()` yalnız P21 uyumlu temel sonucu, `analyze()` buna ek olarak YÖNT ve aday izini verir. Sarmalayıcı model ağırlıklarını Python'a yüklemez; ayrı Rust sürecine JSONL gönderir. Python kullanılırsa Python sürecinin kendi bellek maliyeti vardır. `bpe()` tarihsel küçük BPE karşılaştırmasıdır; Qwen tokenizer'ı değildir.

Qwen tabanlı P129 gösterimi ve bağımlılık kurulumu: [P129 kullanım](docs/P129-KULLANIM.md). Qwen BPE ID'leri TürkTokenizer ID'leriyle doğrudan değiştirilemez; adaptör ve uyumlu eğitim gerekir. Wheel PyPI'ye yayımlanmış değildir. Güncel hazır binary Windows x64 içindir; Linux/macOS/MLX desteği vaat edilmez.

## YÖNT kapsamı

Örnek cümlede `Çocuk→okudu:özne`, `kitabını→okudu:nesne`, `öğretmenin→kitabını:sahip` bağlantıları aranır. Desteklenen G0: olumlu/etken basit geçmiş, açık yalın özne, belirtme durumunda nesne, isteğe bağlı ilgi/iyelik bağı; üç veya dört sözcüklü tek cümle. Bütçe veya aday araması tamamlanmazsa uzlaşı verilmez. Olumsuzluk, edilgenlik, genel yan cümle/tümleç kapsamı ve gerçek niyetin doğruluğu garanti edilmez. Temel motorun seçimi yan katman tarafından değiştirilmez.

## Kaynak, doğrulama ve katkı

`native/src/engine` donmuş P119 kaynakları; `native/src/binding.rs` P128; yeni CLI yalnız decode işlemini dışarı açar. `native/build.ps1` motoru derler. Python paketi `src/turktokenizer_native` altındadır. Araştırma matematiği: [formüller ve sorular](docs/MATEMATIK_FORMULLERI_VE_ARASTIRMA_SORULARI.md). Release'e `python tools/verify_package.py` ile bütünlük kontrolü uygulanabilir.

Anlamlı katkılar: yanlış aday/yanlış seçim örneklerini ayrıştırmak, morfem bilgisini aday tutarlılığını koruyarak modele taşımak, çekimserliği ölçmek ve BPE'nin tavana ulaşmadığı bağımsız değerlendirmeler tasarlamak. [CONTRIBUTING.md](CONTRIBUTING.md). Yeni bir örneğin doğru çalışması genel kalite kanıtı değildir.

## Lisans ve atıf

**TürkTokenizer'e ait özgün kod ve sarmalayıcı Apache-2.0 ile açık kaynak olarak sunulur. Kurucu / Mimar: Tarkan Özel.** [LICENSE](LICENSE), [NOTICE](NOTICE), [AUTHORS.md](AUTHORS.md).

Üçüncü taraf kaynaklar ve araştırma model/veri varlıkları kendi bildirimlerini korur. Kaynak geçmişinde CC BY-SA ve **CC BY-NC-SA** materyal de vardır; araştırma paketinin tamamını sınırsız ticari kullanımlı tek bir Apache-2.0 eser gibi sunmuyoruz. Yol bazlı kapsam: [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Yeni lisans, üçüncü taraf haklarını yeniden lisanslamaz.

İletişim: **turktokenizer@cizgiturk.com** · https://www.cizgiturk.com

Bu proje yapay zekâ destekli yazılım ve deney tasarımıyla geliştirilmiştir. Amaç, Türkçe doğal dil işleme topluluğunun inceleyip geliştirebileceği, sonuçlarını dürüstçe paylaşan bir temel sağlamaktır.

## Önceki sürümler ve araştırma arşivi

[Eski main ve diğer araştırma dalları](ARSIV.md) korunmuştur. Güncel kaynaklar bu `main` dalındadır. Çalışma modeli/verileri ayrı araştırma release varlığıdır.
