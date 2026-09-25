# TürkTokenizer

BPE sistemler tamamen İngilizce düşünülerek yapıldığından özellikle küçük modellerde Türkçenin kök+ek yapısını çok fazla buduyor ve bu yüzden Türkçe gibi eklemeli dillerde Küçük dil modelleri (SLM)'lerde kök+ek yapısı budandığı için İngilizce kadar iyi bir başarım gösteremiyor. Bu yüzden Türk biçem biliminde, Türk sözcükleri yapay zekanın anlayacağı Türk sözcük bölümleyici (tokenizer) yaratma ihtiyacı ortaya çıktı. Bundan dolayı 2015 yılında kaleme aldığım Bilim Dili TÜRKÇE.pdf [Bilim Dili Türkçe](docs/Bilim-Dili-Turkce-Tarkan-Ozel.pdf) makalemi tarihi çıkış noktası olarak aldım ve güncel akademik makalelerle TürkTokenizer projesine uyarladım [Gelişim öyküsü](docs/GELISIM.md).

Bu ihtiyacı karşılamak için UPOS/LAS/UAS/Macro F1 ve Seçim Skoru gibi metrikleri içeren akademik yolla bu sorunu çözmeye çalıştım. Ancak bu yapıyı, 

%88.19 Bağlantı Başarımı (UAS = Hangi kelimenin hangi kelimeye bağlı olduğunu, yani cümlenin iskeletini/oklarını çizme), 

%76.46 Bağlamlı Bağlantı Doğruluk Oranı (LAS = Hem bağlantıyı doğru kurup hem de o bağlantının ne anlama geldiğini, yani bağlamını çözme),

%92.34 Etiketleme hassasiyeti (UPOS = Kelimelerin türünü/kimliğini belirleme),

şeklinde üretim seviyesi ile sota seviyesi arasına girecek bir model yaratmayı başarsam da, (v6.1 R4-P2 yani TürkTokenizer'in 6.1 sürümünün 4. düzeltme 2 faz yapısına kadar tarafsız deney sonuçlarını ayrıntılı olarak şuradan inceleyebilirsiniz). Her ne kadar gelecek vaat etse de bu yapı yanlış yazımlarda ve kurala uymayan yazımlarda çok kırılgan olacağından ve Türkçe sonsuz işlem kapasitesine sahip bulunduğundan kök+ek1+ek2 yerine kök:clE001+ksE004 şeklinde, Türkçedeki tüm ekleri sınıflandırıp numaralandırarak ve kaçırdığım yerleri sıradan BPE sisteme paslayan hibrit bir köklü bir mimari değişikliğe gittim. Buradaki Türkçe'deki ekleri sınıflandırmama örnek verdiğim yapıyı anlamak için ASCII sisteminde baş harf ve baş harften sonraki ilk sessiz harf olarak düşünün. clE001 diyorsak örneğin (cl = Çoğul, E = Eki) 001 ise örnek veriyorum -ler eki. Baş harf ile baş harften sonra ilk sessiz harfi etiketlerken almamın mantığına gelirsek sadece baş harfi alıp Zaman Ekine zE dediğimde, Zarf ekindeki zE ile çakıştığı içindi. Baş harften sonraki ilk sessiz harfi de alarak Zaman Eki için zmE, Zarf eki için zrE yaparak sorunu çözdüm. Ekleri E şeklinde büyük harf göstermemin sebebi ise bir Ekin bitip başka bir Ekin başladığını belirtmek içindi. Bu şekilde Türkçe için 43 ek sınıfı ve 876 adette sınıflandırılmış Türkçe ek sözlüğü 752 üretime açık kayıt oluşturdum. Araştırmacılar mantığı kavramak için sınıflandırılmış ek sözlüğüne dosyalardaki [**eksozlugu.md**](eksozlugu.md) kısmından ulaşabilirsiniz. Yüzey varyantları, sıfır biçimler, süreçler ve kurallar da dahildir. Örneğin `clE0001=ler`, `clE0002=lar`; ikisinin morfem kimliği `NUMBER_PL`'dir. Kısa insan okunur kayıt ID'si, morfem kimliği ve modele verilen sayısal token ID'si farklı kavramlardır. P21 toplam 345.127 ID sözleşmesini korur.

Sınıf etiketlerinde Türkçe adlardan türetilen kısaltmalar kullanılır; her kayıt bir ek değildir, `R` ve `K` etiketli sınıflar da bulunur. Sıra numarası dilbilimsel öncelik veya ağırlık değildir. Makine okunur kayıtlar [registry/](registry/) altındadır.

Şu an bu kural tabanlı YÖNT eklenmiş sistem Türkçe sözcüklerde doğru bölümleme yaparak statik soru-cevap testlerinde %98.91 oranda başarım sağlıyor ve Türkçe olmayan veya Türkçe olsa da kurala uymayan sözcükleri ise bir diğer güvenlik katmanı olarak mimarimiz için özelleştirilmiş BPE katmanına paslıyor. Ayrıntılı değerlendirme için 129. faz deney sonuçlarına P129'a bakabilirsiniz. Qwen3-0.6B-Base modeli ve aynı BPE girdisi; 4 koşul × 3 eğitim tohumu. 7.200 eğitim sorusu; 4.800 değerlendirme sorusu üzerinden bu deney gerçekleştirilmiştir. Test etmeniz için Google'nin Gemma 4 12B modeline TürkTokenizer'i ekleyip Q5_K_M, Q6_K_M, Q8_0 BF16 ve MLX 4bit 8bit olarak sıkıştırıp ilerleyen zamanlarda paylaşacağım. Şu an bu sunucu kiralayıp yapacak bütçem yok. Elbette bu değerler yeterli araştırma bütçesi, akademik destek sağlanırsa daha da arttırılabilir ancak şu an için elimizde bunu yapmak için yeterli bütçe, araştırma kredisi ve büyük sunucu çiftlikleri yok maalesef. Elimizden geldiğince TürkTokenizer'in 2015 yılında kaleme aldığım Bilim Dili TÜRKÇE makalesiyle tarihsel çıkış noktasını, mimariyi geliştirirken neyi neden yaptığımızı ve mantığını anlattığım noktaları, nerede başarılıyız ve neresi geliştirilebilir diye dürüst şekilde böyle detaylıca anlatmamın sebebi, benden çok daha teknik bilgiye ve ekibe, üniversite araştırma bütçelerine, yüzlerce H100 sunucu ortamlarına erişme imkanına sahip kişilere bu süreci kavratıp, onların benden sonra da projeyi devam ettirebilmesi içindir. Biz temel iskeleti oluşturarak Türk yapay zeka topluluğunun gelişmesi ve sanayi devrimini kaçırmamızdan bile daha büyük etkileri olacak bu çağda ileri gidebilmemiz için ufakta olsa bir destek sundum. Türk diline uygun bilgisayar dili yazılmadıkça kodlama ve yabancı sözcük kısımlarımda başarım artışı sağlamasa da, bu Türk sözcük bölümleyiciyle Türkçe girdinin modelin doğru anlaması ve doğru şekilde çıktı üretmesi özellikle sıkıştırma "quantize" edilmiş modellerde Türkçenin kök+ek yapısı budanıyor, bu bölümleyici bu budamanın önüne geçerek Türk dilinde 12B bir modelden yaklaşık 27B civarında başarım almanızı, daha az kaynak tüketip daha çok önbellek kullanmanızı sağlıyor. Böylece KDM/SLM denilen Küçük Dil Modellerinden BDM/LLM Büyük Dil Modellerine kadar Türkçede daha doğru bağlamla başarım artışı alınıyor ve MoE/VLM modellerde de yüksek verim alınıp yardımcı asistan ve sohbetlerde daha az halüsinasyon, otonom sistemlerinden sensörlerinin kullanıcıya aktarılmasında Türkçe daha doğru aktarım gibi gibi temel katmanda Türkçe için geliştirilmiş böyle bir mimari bir çok işe yarıyor. Bu yüzden kendi Türk yapay zeka modelimizi yapacaksak önce bu tarz sağlam bir bölümleyici (tokenizer) katmanından başlamalıyız.

Benim düşünceme göre dünya üzerinde 3 ana dil grubu var. Bunlar 1- Büklümlü diller (hint-avrupa/arapça) bunların kendi bölümleyicileri var. Sıradan BPE mimarisi zaten o kullanılıyor. 2- Eklemeli diller (Türk dilleri Ural/Altay) bu kısımda büyük bir açık var. 3- Sembolik diller (çince/vietnamca) bunlarda 1 sembol = 1 belirteç (token) olduğu için Kimi K3 gibi modellerde zaten kullanılıyor. Kuzenlerimiz ne yapmış diye baktığımda Türkçe Zemberek & Morfessor, Fince Omorfi + Morpho-BPE, Japonca SudachiPy / MeCab, Korece Mecab-ko ve Kakao/Naver gibi yaklaşımlarla oluşturulmuş sözcük bölümleyicileri var ama bir kaç iyi fikir verseler de hiçbiri istediğimiz sonucu üretemediğinden kendi mimari motorumuzu sınıflandırılıp numaralandırılmış ek sistemiyle yarattık. Bağlamı daha kolay bulup cümlenin öğelerini çıkartmak içinde hiçbir akademik makalede doğru düzgün bulunmayan tamamen Türk eğitim sisteminin bir sonucu olarak dershanelerin türettiği YÖNT (Yüklem, Özne, Nesne, Tümleç) formülü, FISTIKÇI ŞAHAP ve Y,Ş,S,N gibi kestirme formülleri kendimizde türetip A1-A2-A3 katmanlarına uyarlayarak sorunu çözdük. Buradaki mantığı açmam gerekirse YÖK'ün rezil eğitim sistemi yüzünden Türkleri yarış atı gibi şıklarla dolu test kutucuklarına mahkum edip her soru için neredeyse 1 dakikadan az zaman veriyorlar. Büyük paragraflı Türkçe sınavlarda ise soruyu okuyup anlamak ve karar vermek için yeterli zaman olmadığından dershaneler bu tür kestirme formüller geliştirip öğrencilerine onlarca dakikadan kurtaran yaratıcı formüller türetmek zorunda kalıyorlar. Matematik formülü gibi doğru yazılmış Türkçe bir metne bunları verdiğinde de öğeleri çıkartmak kolaylaşmış oluyor. Gazetecilikteki 5N1K (Ne-Neyi-Nerede-Ne zaman-Nasıl-Kim) kuralı soruları gibi kurallara da göz atarak A1 (Ek-Tümleç Uyumu Kestirmesi soruları) A2-A3 (Vurgu ve Temel Söz Dizimi Kestirmesi, Çekim Eki ve Şahıs Uyumu Kestirmesi ve Bağlaç ve Edat Öbekleri Kestirmesi) gibi pek çok deney yaptık ve en sağlıklı sonuçla A1-A2-A3 katmanını 21. fazda P21'de dondurduk. Ve güncel deneyleri P129 fazına kadar çıkarttık. Bu arada RTV (Radyo-Televizyonda) konuşma zamanını kağıt üzerinde sayarken 2 sözcük = 1 saniye şeklinde hesaplarız ve oldukça tutarlı sonuç verir. Mühendislerin alan dışı olduğu için böyle teknik ayrıntılar gözünden kaçabilir diye yazıdan metne bir yapay zeka ses modeli oluşturacağınız zaman bunu da dikkate alarak bir algoritma yazabilirsiniz. Okuduğunuz için teşekkür ederim, umarım Türk yapay zeka topluluğuna az da olsa bir katkımız olur. Özellikle Türkçe ve diğer Türk kardeşlerimizin ve (Macarca/Moğolca/Tunguzca/Korece/Japonca/Fince) kuzenlerimizin bu eksikliğini gidermek için bir temel olur. TürkTokenizer'in bu mimari yapısı kullanılarak TuranTokenizer adıyla tüm bu Türk Ural/Altay hattı kapsanarak bu ihtiyaç giderilebilir.

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

Üçüncü taraf kaynaklar ve araştırma model/veri varlıkları kendi bildirimlerini korur. Kaynak geçmişinde CC BY-SA ve **CC BY-NC-SA** materyal de vardır; araştırma paketinin tamamını sınırsız ticari kullanımlı tek bir Apache-2.0 eser gibi sunmuyoruz. Hiçbir ticari beklenti istemeden tamamı açık kaynak Türk milletine hizmete hazır, Türk araştırmacılara yol haritasıdır. Yol bazlı kapsam: [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). 

İletişim: **turktokenizer@cizgiturk.com** · https://www.cizgiturk.com
ozelturktarkanim@gmail.com

Bu proje yapay zekâ destekli yazılım ve deney tasarımıyla geliştirilmiştir. Amaç, Türkçe doğal dil işleme topluluğunun inceleyip geliştirebileceği, sonuçlarını dürüstçe paylaşan bir temel sağlamaktır.

## Önceki sürümler ve araştırma arşivi

[Eski main ve diğer araştırma dalları](ARSIV.md) korunmuştur. Güncel kaynaklar bu `main` dalındadır. Çalışma modeli/verileri ayrı araştırma release varlığıdır. Gaspralının dediği gibi DİLDE, İŞTE, FİKİRDE BİRLİK.  Var olun. Esen kalın

Tarkan Özel. -TürkTokenizer kurucu mimar-
