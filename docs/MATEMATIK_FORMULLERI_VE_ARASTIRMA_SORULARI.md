# TürkTokenizer: kullanılan matematik, amaçları ve geliştirme soruları

25 Eylül 2026 — P21 / P119 / P128 / P129 kaynaklarına dayalı teknik tartışma dosyası.

**Amaç:** Matematik konusunda deneyimli bir araştırmacının mevcut sistemi denetleyebilmesi ve hangi varsayımın değiştirilmesinin anlamlı olacağını tartışabilmesi. Bu dosya yeni deney veya genel Türkçe anlama garantisi sunmaz. Formüller kodun okunabilir matematiksel gösterimidir; sayısal ayrıntılarda kaynak uygulama esas alınmalıdır.

## 0. Önce mimariyi ayıralım

| Katman | Gerçekte yaptığı | Yapmadığı |
|---|---|---|
| P21; native uygulaması P119 | Sözcük için kök/ek adaylarını üretir, sıralar ve kabul/çekimserlik kararı verir | Bütün cümlenin anlamını kanıtlamaz |
| Tarihsel P3/P7 formülleri | Durum eki, sahiplik, kişi uyumu gibi ipuçlarını sayısal özellik yapar | P129'a ayrıca çalışan ikinci bir gramer motoru olarak eklenmiş değildir |
| P128 | Dar G0 gramerinde belirli morfolojik adaylara bağlı özne/nesne/sahip ilişkilerini arar | Genel Türkçe, örtük özne, olumsuzluk, edilgenlik, her tür tümleç veya yan cümle çözmez |
| P129 | Aynı Qwen BPE dizisine morfoloji ve ilişki mesajları ekleyen giriş adaptörünü eğitir | BPE dizisini daha kısa ID dizisine dönüştürmez; Qwen'in tokenizer'ını değiştirmez |

YÖNT, yüklem–özne–nesne–tümleç yönünü anlatan proje adıdır. Çalışan P128 kapsamı bu adın çağrıştırdığı bütün Türkçe dilbilgisinden dardır. “Dinamik kök:ek şablonunu tek ID'ye paketleme” fikri P129'un çalışan mekanizması değildir. Bit paketlemek de tek başına modelin o ID'nin anlamını öğrenmesini sağlamaz.

İncelenecek alan yalnız logaritmalar değildir: **kısıt programlama, biçimsel dilbilgisi, olasılıksal grafik modelleri, temsil öğrenme ve deney istatistiği** birlikte önemlidir.

## 1. Simgeler ve değişmeyen sözleşme

- Metin: x. Sözcükler: w₁,…,wₙ; her biri ham metinde Unicode karakter aralığına bağlıdır.
- Cᵢ: i. sözcük için motorun ürettiği kanonik adaylar.
- Aday c: `(kök, kök türü, [(morfem kimliği, türetim sınırı), …], son tür)`.
- BPE konumları: t=1,…,T. Sözcük indeksi ile BPE konumu aynı şey değildir.
- P21'de 345.127 kimlik, sözlük, aday kuralları ve metin sınırları kilitlidir. P128 bunları değiştirmez.

Önemli ayrım: doğru adayın Cᵢ içinde bulunması, o adayın seçilmesi ve seçilen adayın kabul edilmesi üç ayrı olaydır. Eksik doğru adayı daha iyi sıralama formülüyle seçemeyiz.

## 2. Morfolojik aday puanı ve kabul kapısı — çalışan native hat

### 2.1 P119 sıralaması

Kanonik adaydan çıkarılan, ağırlık dizisine işaret eden özellik indeksleri I(x,i,c) olsun. Olağan puan:

$$s_i(c)=\operatorname{f32sum}_{j\in I(x,i,c)}\theta_j.$$

Amaç, adayları öğrenilmiş yerel ve bağlamsal belirtilere göre sıralamaktır. Yerel indeksler 524288'in altındadır; diğer indeksler bağlamsal parçayı oluşturur. Toplam, yerel ve bağlam puanı ayrı hesaplanır. Kaynakta belirli adaylar için önceden verilen `forced` puan dalı da vardır; yukarıdaki ifade olağan daldır.

**Sayısal sözleşme:** Ağırlıklar f32'dir. `numeric.rs` NumPy uyumlu belirli bir f32 toplama sırasını taklit eder; sonuç sonra f64'e çevrilir. Bu sırayı değiştirmek veya tümünü f64 toplamak matematiksel toplamı yakın tutsa da mevcut bit eşitliği sözleşmesini bozabilir. Toplam puanı, ayrı ayrı yuvarlanmış yerel ve bağlamsal puanları toplayarak yeniden üretmek de aynı sonucu zorunlu kılmaz.

Skorların göreli dağılımı:

$$p_i(c)=\frac{\exp(s_i(c)-m_i)}{\sum_{d\in C_i}\exp(s_i(d)-m_i)},\quad m_i=\max_d s_i(d).$$

Maksimumun çıkarılması sayısal taşmayı azaltır. `p` bütün Türkçe anlamların gerçek olasılığı değildir; yalnız eldeki aday skorlarının normalizasyonudur. Doğru aday dışarıdaysa yanlış adayın p değeri çok yüksek olabilir.

Ek belirtiler: en iyi ve rakip puan farkı; aynı kökün toplam olasılık kütlesi; yerel/bağlamsal kazananların anlaşması; aday ve kök entropisi. Yol entropisi:

$$H_i=\frac{-\sum_c p_i(c)\log p_i(c)}{\max(1,\log |C_i|)}.$$

Bu tam olarak kodun paydasıdır; klasik “log K'ya bölme” ifadesiyle sessizce değiştirilmemelidir. Özellik amaçları, ne kadar rekabet/belirsizlik bulunduğunu kabul kapısına aktarmaktır.

### 2.2 A2 kabul kapısı

Temel belirtiler b, rakip/bağlam kanıtları e olsun:

$$z=\beta_e^\top e+\beta_b^\top b,\qquad q=\frac{1}{1+\exp(-\operatorname{clip}(z,-60,60))}.$$

Kapı uygunluk/koruma kontrollerinden sonra tanımlı eşik varsa q≥τ koşulunu kullanır. Kaynak değişkeni `risk` adını taşır; fakat kabul kodu büyük değeri tercih eder. Sadece bu isimden “büyük değer daha çok hata demektir” sonucu çıkarılmamalıdır. q bir öğrenilmiş kapı çıktısıdır; her yeni dağılımda aynı doğruluk garantisi değildir. Eşik ve model birlikte korunmalıdır. A3 değişirse A2'nin eski kalibrasyonu otomatik geçerli kalmaz.

Kaynaklar: `native/src/engine/{ranking,numeric,gate,features,gate_model}.rs`.

## 3. Daha önce kullandığımız dilbilgisi formülleri — tarihsel P3/P7

### 3.1 Fiil–durum eki tercihi

Fiil kökü ve çatı için gözlenen durum sayısı nₖ, toplam n olsun:

$$\widehat P(k\mid v,\text{çatı})=\frac{n_k+0.5}{n+3},\qquad g=\operatorname{clip}\left(\log\frac{\widehat P(k\mid v,\text{çatı})}{1/6},-2,2\right).$$

Amaç: altı durum için eşit temel dağılıma kıyasla gözlenen fiil tercihine yumuşak destek vermek. +0,5 sıfır sayımı yumuşatır; altı sınıfta toplam ön sayım 3'tür. n<3, uygun fiil olmaması veya yalın durum halinde katkı 0'dır. Yalın adın özne mi belirtisiz nesne mi olduğu belirsiz olduğundan yokluğu cezaya çevrilmez. Veri sayımı dilbilgisi yasağı değildir; seyrek fiili kesin kural gibi okumamak gerekir.

### 3.2 Komşu adaylardan destek/çatışma

Uzaklık d≥1, komşunun incelenen yorum sayısı K, uyum işareti h(c) olsun:

$$u^+=\frac{\sum_{c=1}^{K}\mathbf1[h(c)>0]}{\max(1,K)[1+0.2(d-1)]},\quad
u^-=\frac{\sum_{c=1}^{K}\mathbf1[h(c)<0]}{\max(1,K)[1+0.2(d-1)]}.$$

Komşular üzerinde hem maksimum hem `min(2, toplam)` özellikleri alınır. Aynı komşunun hem destekleyen hem çelişen adayları varsa belirsizlik özelliği eklenir. Amaç, uzaktaki ve çok yorumlu komşunun etkisini azaltmaktır. Bu oranlar adayların gerçek posterior olasılığı değildir; aday sayısı arttığında destek mekanik olarak değişebilir.

P7 artık puanı:

$$s'_i(c)=s_i^{\mathrm{önceki}}(c)+\lambda\sum_k a_k\phi_k(x,i,c),\qquad \widetilde s'_i(c)=s'_i(c)-\max_d s'_i(d).$$

Son sabit çıkarımı sıralamayı değiştirmez. Formül ailesi, lambda ve ağırlıklar model seçiminin parçalarıdır. Buradaki eski özellikler güncel P128'in eksiksiz aday bağlı aramasından ayrı tutulmalıdır.

Kaynaklar: `history/python-sources/grammar_p3.py:case_preference`, `formulas_p7.py:evidence/collect`, `s06e_p7.py:FormulaRanker`.

## 4. P128: formülü doğru sözcüğün doğru adayına bağlamak

Bu bölüm, çalışan DFS aramasının kısıtlarla eşdeğer açıklamasıdır; kodda ILP çözücüsü çalıştırılmıyor.

Her sözcük için seçim değişkeni:

$$z_{i,c}\in\{0,1\},\qquad \sum_{c\in C_i^{G0}}z_{i,c}=1.$$

Bir ilişki hem uç sözcükleri hem uçlardaki kanonik adayları taşır. `(i,c)→(j,d)` kenarı kullanılıyorsa zᵢ,c=zⱼ,d=1 olmalıdır. Böylece bir sözcüğün bir adayındaki özne özelliği ile başka adayındaki ek özelliği aynı çözümde fark edilmeden birleştirilmez.

G0, üç veya dört sözcüklü tam bir basit cümlede şu koşulları uygular:

- Tek desteklenen etken/olumlu geçmiş zaman fiili; desteklenen fiil çerçevesi.
- Bir yalın özne ve bir belirtme durumlu nesne; en çok bir ilgi durumlu sahip.
- Özne–yüklem kişi uyumu. Sayı uyumu birinci/ikinci kişide zorunlu; üçüncü kişide zorunlu değildir.
- Sahip varsa, iki nominal baştan uygun iyelik taşıyanına bağlanır; yine kişi ve ilk iki kişide sayı kontrolü vardır.
- Türetim ve desteklenmeyen operatörler G0 dışında kalır. Ham metin/sözcük aralıkları tam örtüşmelidir.

Uyum fonksiyonunun mevcut biçimi:

$$A(a,b)=[p_a=p_b]\land[(p_a=3)\lor(n_a=n_b)].$$

Tüm geçerli G0 planları F(x), bir plandan alınan rol özeti ise

$$Q(f)=(\text{yüklem indeksi/kökü},\text{özne},\text{nesne},\text{açık sahip/baş})$$

olsun. Koşullu cevap ancak şu durumda çıkar:

$$\text{arama tam}\land\text{aday üretimi tam}\land F(x)\ne\varnothing
\land |\{Q(f):f\in F(x)\}|=1.$$

Buradaki tamlık, raporlanan aday envanteri ve G0 için geçerlidir. G0 dışında kalan adaylar silinmiş doğru yorumlar gibi gizlenmez; ayrıca listelenir. Kaynak aday skorları korunur fakat **P128 uzlaşı hesabında kullanılmaz**. Bir temsilî plan gösterilir; tüm planların morfem seçiminde de aynı olduğu iddia edilmez.

**Kanıtlanabilen koşullu önerme:** Eğer gerçek yorum f* gerçekten F(x)'in içindeyse ve tam taranan F(x)'in bütün elemanları aynı Q değerini taşıyorsa dönen Q gerçek yorumun Q'suna eşittir. Gerekçe: f* de aynı kümenin bir elemanıdır. Fakat “gerçek yorum F(x)'te mi?” varsayımını bu önerme kanıtlamaz. G0 dışı yapı, eksik aday, yanlış morfolojik okuma veya anlamsal dünya bilgisi ihtiyacı bu varsayımı bozabilir.

Örnek: “Çocuk öğretmenin kitabını okudu.” için `Çocuk→okudu:özne`, `kitabını→okudu:nesne`, `öğretmenin→kitabını:sahip` bağlantıları çıkar. “Öğretmenin çocuğu kitabı okudu.” gibi çok yorumlu biçimlerde yalnız biçimsel kurallar anlamsal olarak tuhaf bir rol değişimini dışlayamayabilir. Bu yüzden tek bir sezgisel okuma kesin cevap diye zorlanmaz.

Arama maliyeti adayların Kartezyen çarpımına bağlıdır: yaklaşık ∏ᵢ|Cᵢᴳ⁰| yaprak. Mevcut n yalnız 3/4'tür; kapsam genişletilirse cümle uzunluğuyla üstel büyüme riski vardır. Varsayılan düğüm bütçesi 200.000; izin verilen en büyük bütçe 2.000.000. Bütçe biterse `INCOMPLETE` döner; ilk bulunan plan uzlaşı sayılmaz. Bir logaritma eklemek bu kombinatoryal maliyeti ortadan kaldırmaz.

Kaynak: `native/src/binding.rs`, özellikle `classify`, `agrees`, `dfs`, `leaf`, `solve`.

## 5. P129: BPE + morfoloji + YÖNT modele nasıl aktarılıyor?

### 5.1 BPE–sözcük hizalama

BPE gömmesi Eₜ∈ℝᴴ, H=1024; düşük boyut R=32. Aᵢₜ, token konumu t'nin sözcük i ile örtüştüğünü belirten 0/1 matrisidir. Kod bir token'ın birden fazla sözcüğe taşmasını reddeder. Soru/seçenek konumları morfolojik sözcüğe bağlanmaz.

$$u_i=\frac{\sum_t A_{it}E_t}{\max(1,\sum_t A_{it})}.$$

uᵢ, sözcüğün BPE parçalarının ortalamasıdır. Henüz Transformer'dan geçmemiş giriş gömmeleridir; bağlamla derinleştirilmiş anlamsal durumlar değildir.

### 5.2 Morfoloji özelliği

Fᵢ, o sözcüğün bütün native adaylarından toplanan kök türü, son tür ve morfem özelliklerinin birleşimidir. Sözlük sadece eğitim verisinden kurulur. Bilinmeyen özellik 0 kimliğine gider ve sıfır gömme taşır.

$$f_i=\frac{\sum_{k\in F_i}\operatorname{Emb}_{\rm feat}(k)}{\sqrt{\max(1,|F_i^{\ne0}|)}}.$$

Amaç, çok özellikli sözcüğün vektörünün kontrolsüz büyümesini azaltmaktır. **Önemli bilgi kaybı:** Özellikler aday bazında ayrılmaz; birbiriyle çelişen adayların özellikleri aynı toplamda bulunabilir. Dolayısıyla native P128'in aday bağlı mantığı, P129 morfoloji vektöründe birebir korunmuş değildir.

### 5.3 İlişki mesajları

Özne→yüklem, nesne→yüklem, sahip→iyelik başı ve bunların ters yönleri toplam altı ilişki türü verir. P128 yalnız koşullu uzlaşı varsa bu kenarlar kullanılır.

$$m_{j\to i}=\tanh\big(W_\downarrow\operatorname{LN}(u_j)+r_{\rho(j,i)}\big),$$
$$g_i=\frac{\sum_{j\to i}m_{j\to i}}{\sqrt{\max(1,d_i)}}.$$

W↓: ℝ¹⁰²⁴→ℝ³², rρ∈ℝ³²; dᵢ gelen geçerli kenar sayısıdır. LN katman normalizasyonudur. Mesaj bir kez komşudan taşınır; çok adımlı mantıksal çıkarım veya genel cümle kapsamı hesabı yapılmaz. Toplama komşu sırasına duyarsızdır; kaynak konum, morfolojik aday kimliği, kural/şahit ayrıntısı mesaj vektörüne ayrı değişken olarak girmez.

### 5.4 Girişe düzeltme

$$\delta_i=W_\uparrow(a f_i+b g_i),\qquad
E'_t=E_t+\sum_i A_{it}\delta_i.$$

W↑: ℝ³²→ℝ¹⁰²⁴; başlangıçta sıfırdır. Böylece başlangıçta E′=E olur. Düzeltme FP32 hesaplanır, gömmeye eklenirken temel gömmenin BF16 türüne çevrilir.

| Koşul | a | b | Kenarlar |
|---|---:|---:|---|
| plain | 0 | 0 | Etkisiz |
| morph | 1 | 0 | Etkisiz |
| graph | 1 | 1 | P128 koşullu kenarları |
| shuffled | 1 | 1 | Uçları kaydırılan kontrol kenarları |

Karıştırma, her uç indeksi için `(i+k) mod n`, 1≤k≤n−1 uygular. Kenar tür sayıları ve derece çoklu kümesi korunur; doğru sözcük/cümle bağları korunmaz. Bu kontrol “aynı miktar yapı eklemek yeterli mi?” sorusuna yöneliktir. Her kolda ayrılmış parametreler aynı olsa da aktif gradyan/hesap kapasitesi aynı değildir.

### 5.5 LoRA

Temel model donuktur. Yalnız q/v izdüşümlerinde:

$$W'=W+\frac{\alpha}{r}BA,\qquad r=8,\ \alpha=16.$$

Bu bölümdeki A düşük dereceli ağırlıktır; 5.1'deki hizalama matrisiyle aynı nesne değildir. LoRA ve ilişki adaptörü toplam **1.213.408** eğitilebilir parametre içerir; modelin raporladığı donuk parametre **596.050.945**'tir. Eski yardımcı morfoloji başı bu deneyde donuktur; yardımcı kayıp kullanılmaz.

Kaynaklar: `experiments/P129-20260924/scripts/{dataset,relation_model,pretrained_model}.py`. Dört kolun BPE ID dizisi aynıdır. Native analiz yalnız görünür bağlam cümlelerine uygulanır; soru, seçenek veya doğru cevap native girdisi değildir.

## 6. Eğitimde gerçekten neyi optimize ettik?

Son giriş konumunun gizli durumu h, A/B/C/D token'larının sabit çıktı gömmeleri eₖ olsun:

$$\ell_k=e_k^\top h,\qquad P(k\mid x,q,\text{seçenekler})=\frac{e^{\ell_k}}{\sum_{j=1}^4e^{\ell_j}},$$
$$\mathcal L=-\frac1B\sum_{b=1}^{B}\log P(y_b\mid x_b,q_b,\text{seçenekler}_b).$$

Bu **dört seçenek arasında koşullu çapraz entropidir**; tam sözlük dil modeli kaybı/perplexity değildir. Doğru seçenek etiket olarak yalnız kayba girer. Bağlamın bütünü sorudan önce görünürdür. Aynı önceden çıkarılmış bağlam grafiğini, o bağlamın kelimelerini soldan sağa tahmin ederken kullanmak gelecek bilgisi sızdırabilir; P129 böyle bir dil modeli başarısı iddiası yapmaz.

AdamW, ana öğrenme oranı 0,0002; weight decay 0,01; gradyan norm sınırı 1. Etkin batch 16, microbatch 2; 7.200 soru ×3 epoch =21.600 gösterim, 1.350 optimizer adımı. İlk `floor(0,05×1350)=67` adım doğrusal ısınma, sonra 0,1 tabanına inen kosinüs çarpanı kullanılır. Kodda zamanlama uç değerleri adım indeksine bağlıdır; genel kosinüs ifadesiyle yeniden yazarken bu ayrıntı korunmalıdır.

Kaynak: `scripts/worker.py:train/evaluate`. Bu kaybı azaltmak genel Türkçe anlama başarısının monoton arttığını kanıtlamaz; yalnız verilen eğitim sorularına uygunluğu optimize eder.

## 7. Ölçüm formülü ve sonuç

Her sabit tohum s, bölüm d ve soru j için doğruluk göstergesi Iₛ,d,j:

$$\widehat{Acc}=\frac13\sum_{s=1}^3\frac13\sum_{d\in\{lexical,order,composition\}}\frac1{1200}\sum_{j=1}^{1200}I_{s,d,j}.$$

Fark Δ=Acc(graph)−Acc(kontrol). Belirsizlik, her OOD bölümünde bağlam/episode grupları yeniden örneklenerek hesaplanır; aynı bağlamın soruları birlikte kalır. 10.000 bootstrap örneği; üç karşılaştırma için α=0,05/3, aralık %98,333. Üç sabit tohum ortalanır; bu aralık yeni rastgele eğitim tohumlarının popülasyon belirsizliğini bütünüyle ölçmez.

| Kol | OOD doğruluk |
|---|---:|
| plain | %99,5926 |
| morph | %98,3889 |
| graph | %98,9074 |
| shuffled | %98,5093 |

Graph−plain: **−0,6852 puan**, aralık **[−1,0093; −0,3796]**. Üç tohumda da negatif. Graph, morph ve shuffled'dan ortalamada biraz iyi olsa da bu kontrollerin her birine karşı bir tohumda yön ters. Genel BPE üstünlüğü yok.

En iyi graph-12937 tek koşu: %99,1667; eş tohumlu plain: %99,7222. En iyi tohum sonuca bakarak seçildiği için yeni bağımsız başarı kanıtı değildir. Ön kayıtlı plain'e +10, diğerlerine +5 puan hedefleri geçmedi. Plain %99,59 iken en fazla +0,4074 puan alan kalması, görevin büyük fark ölçmek için fazla kolay olduğunu da gösterir.

Kaynak: `scripts/report.py`, `protocol.json`, `summary.json`, `results/eval-*.json`. Bu mevcut kayıtların açıklamasıdır; bu doküman hazırlanırken yeni kalite deneyi yapılmadı.

## 8. Matematikçi arkadaşla tartışılacak somut sorular

### A. Aday bağlı mantık, sinir ağına aktarılırken kayboluyor mu?

P128 tek planda tutarlı aday seçerken P129 morfoloji özellikleri bütün adayları topluyor. İncelenecek öneri:

$$f_i^{\rm öneri}=\sum_{c\in C_i}\pi_{i,c}\,\phi(c),\qquad \sum_c\pi_{i,c}=1.$$

Bu **uygulanmadı**. π gerçek bağlama göre kalibre edilmezse yanlış adayı daha güçlü verebilir. Adaylar arası ilişkiler korunmadan yalnız beklenen özellik almak da mantıksal tutarlılığı garanti etmez. Önce farklı yorumların mevcut temsilde hangi koşullarda aynı vektöre düştüğü bulunmalı.

### B. Model gereksiz ya da yanlış düzeltmeyi sıfıra indirebiliyor mu?

Mevcut W↑ başlangıçta sıfırdır fakat örneğe özgü güven kapısı yoktur. Öneri:

$$E'_t=E_t+\sum_i A_{it}\gamma_i(x)\delta_i,\qquad 0\le\gamma_i\le1.$$

Bu da **uygulanmadı**. γ=0 seçeneği sade modeli temsil kümesine dahil eder; optimizer'ın her örnekte doğru kapıyı bulacağını veya test doğruluğunun düşmeyeceğini kanıtlamaz. “Sade modeli kapsıyoruz, o halde en az onun kadar iyiyiz” çıkarımı sonlu veri/eğitim için geçerli değildir.

### C. Toplanan tek adımlı mesaj hangi ayrımları korumuyor?

`tanh(W↓LN(u)+r)` yalnız ham sözcük gömmesi ve ilişki türünü görüyor. Morfem sırası, aday anahtarı, olumsuzluk kapsamı ve çok adımlı ilişki durumu ayrı temsil edilmiyor. Aynı u/f/g'ye düşen farklı yapıların karşı örnekleri kâğıt üzerinde aranabilir. Yeni ilişki türü eklemek, gramerin o ilişkiyi doğru ürettiği ayrıca gösterilmedikçe çözüm değildir.

### D. Koşullu doğruluk önermesindeki varsayımı nasıl ölçeriz?

Asıl açık, gerçek yorumun aday envanteri ve G0 içinde bulunmasıdır. Tamlık, dilbilgisel uygunluk, pragmatik uygunluk ve doğru rol bağlama ayrı hata sınıfları olarak düşünülmeli. Yalnız uzlaşı çıkan örnekleri raporlamak yanlı kapsam yaratır; cevaplama oranı ve yanlış cevap oranı birlikte gerekir.

### E. Deney yapmadan hangi hüküm verilebilir?

Bir formülün boyutu, simetrisi, aday tutarlılığı, hesaplama karmaşıklığı ve açık karşı örneği denetlenebilir. Fakat “yeni model daha iyi geneller” sonucu bu denetimlerden çıkmaz. Eski sonuçlara tekrar tekrar bakarak seçilen zor sorular geliştirme malzemesidir; bağımsız değerlendirme sayılmaz. Mevcut kayıtlar ilk hata incelemesi için yeterlidir; aynı 16 saatlik koşuyu gerekçesiz tekrarlamak gerekmez.

## 9. Önerilen tartışma çıktısı

Arkadaşımızdan genel bir “daha iyi formül” yerine şu dört somut çıktı istenebilir:

1. Mevcut temsilde aynı görünen fakat farklı anlama sahip en az bir yapı çifti ve eşitliğin hangi adımda oluştuğu.
2. Bu ayrımı koruyan en küçük temsil/kısıt değişikliği; işlem/bellek maliyeti ve yeni hata riski.
3. Değişikliğin hangi dar önermeyi matematiksel olarak garanti ettiği; hangi kısmın yine deney gerektirdiği.
4. Sade BPE'nin doygun olmadığı, hedeflenen ayrımı gerçekten ölçen bir değerlendirme taslağı ve seçme yanlılığını önleme yöntemi.

**Son değerlendirme:** Formüllerimiz vardı ve çalışıyorlar; fakat morfolojik uyumluluk, koşullu rol uzlaşısı ve küçük modelin genel anlaması aynı iddia değildir. P129, mevcut aktarım biçiminin aranan üstünlüğü sağlamadığını gösteriyor. Geliştirme için en somut matematik sorusu, aday bağlı bilgiyi kaybetmeden ve yanlış bilgiyle temel modeli bozmayı azaltarak nasıl temsil edeceğimizdir.

---

## Kaynaklara erişim

Bu dosya GitHub kaynak ve araştırma release paketleriyle birlikte okunabilir. Yukarıdaki yollar açılmış paket köküne göredir. Tarihsel kaynaklar açıklama için dahil edilmiştir; bütün geçmiş veri/bağımlılıklar paketlenmiş değildir. Güncel çalıştırma `README.md` içindedir. Eski kaynaklar, kilit, ağırlıklar ve makbuzlar bu tartışma için değiştirilmedi.
