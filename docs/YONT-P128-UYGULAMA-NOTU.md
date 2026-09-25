# P128 — Formülleri sözcüklere bağlayan Rust çekirdeği

24 Eylül 2026. Kullanıcının matematik uzmanı ekleme ve mevcut formülleri somut sözcük/cümle yapılarına bağlama talimatıyla yapıldı. Otomatik deney döngüsü açılmadı.

## Ekibin kararı

Uygun uzmanlık **kısıt optimizasyonu, biçimsel dilbilgisi ve yapısal çıkarım algoritmaları**. Logaritma bir uzmanlık hedefi veya bu problemin çözüm süresi garantisi değil. Matematik uzmanı, morfoloji uzmanı ve Muhalif mevcut YÖNT kaynaklarını ve yeni uygulamayı inceledi.

Eski kişi uyumu, hâl ve tamlayan–iyelik bilgileri korunarak yeni bir bağlama sözleşmesi kuruldu. Bu prototip eski YÖNT katmanlarının tamamının yeniden yazımı değildir.

## Değişen şey

Her bağlantı artık şu somut bilgileri birlikte taşır:

`sözcük aralığı + seçilmiş kök/ek aday anahtarı + karşı sözcüğün aday anahtarı + ilişki + cümlecik + kural`

Bir adaydan hâl bilgisini, farklı bir adaydan iyelik bilgisini alıp hayalî bir çözüm kurmak yasaktır. Plan boyunca aynı sözcük aynı adaya bağlı kalır. Kaynak puanlar saklanır; düşük puanlı alternatifler taramadan çıkarılmaz.

Örneğin gerçek native çıktıda **“Çocuk öğretmenin kitabını okudu.”** için:

| Soru | G0 kapsamındaki rol cevabı |
|---|---|
| Yüklem hangisi? | okudu → oku |
| Sözdizimsel özne hangisi? | Çocuk |
| Nesne hangisi? | kitabını |
| Açık tamlayan hangi başa bağlı? | öğretmenin → kitabını |

**“Öğretmenin kitabını çocuk okudu.”** sıralamasında da aynı sözcükler aynı görevlere bağlanıyor.

## Matematiksel güvence tam olarak ne?

`F(x,C,G0)`, verilen ham cümle ve aday havuzunda G0 kurallarını birlikte sağlayan bütün planlar olsun. `Q(P)`, planın yüklem/özne/nesne/açık tamlayan cevabı olsun.

**Aramalar tamamlanmış, F boş değil ve bütün P planları aynı Q cevabını veriyorsa koşullu rol cevabı verilir.**

Bu önerme, gerçek yorumun aday havuzunda bulunduğunu veya G0'ın her Türkçe cümleye uygun olduğunu kanıtlamaz. Aynı rol cevabı da aynı morfolojik aday seçimi demek değildir. Bu yüzden çıktıdaki rol cevabı ile örnek morfolojik tanık ayrıdır.

Tarama bütçesi dolarsa `INCOMPLETE`; birden çok rol cevabı varsa `G0_AMBIGUOUS`; bu gramerde çözüm yoksa `NO_G0_PLAN` döner. Sonuncusu Türkçe cümlenin yanlış olduğu anlamına gelmez.

## İlk kapsam ve ölçülenler

G0 yalnız olumlu, etkin, basit geçmiş cümlesini; açık yalın özneyi, belirtme hâlli nesneyi ve isteğe bağlı bir açık tamlayanı kapsar. Gizli özne, yalın nesne, olumsuzluk, edilgenlik, soru, eşgüdüm ve yan cümleler henüz çözümlenmez. Bütün ham metin kapsanır; desteklenmeyen parçayı atıp kalan bölümden cevap üretilemez.

- **128 mühendislik kontrolü geçti.** Bağımsız doğrulayıcı rolleri önce, Rust adayları önce tarayarak plan sayılarını ve cevap kümelerini karşılaştırdı. Bütçe, aday karışması, puan değişimi, aday/kelime sırası ve eksik ham metin kontrolleri dahil.
- **24 ajan yazımı cümlede** P119'un bütün analiz/aday/puan/ID çıktıları aynı kaldı. BPE ID ve ham geri dönüş kontrolleri de geçti. Yan katmana hata verildiğinde temel çıktı korundu.
- 11 cümlede G0 koşullu rol birliği; 1 cümlede belirsizlik; 6 cümlede G0 planı yok; 6 cümle kapsam dışı. **Bu dağılım doğruluk oranı değildir.**
- P119 makbuzundaki 149 iç ve 285 dış dosya, P21 kilidindeki 166 dosya deney öncesi/sonrası aynı kaldı.
- Üretim bileşeni Rust; Python yalnız mevcut deney denetleyicisi ve kontrol sürücüsü. Kapalı TEST kullanılmadı, model eğitilmedi.

Önemli belirsizlik örneği **“Öğretmenin çocuğu kitabı okudu.”**: gramer ve aday havuzu içinde çocuk/kitap görevlerini değiştiren iki plan var. Sıradan okuma çocuğun kitabı okumasıdır; iki plan eşit doğallıkta değildir. Dünya bilgisi veya anlam tercihi eklenmediğinden sistem bunlardan birini kesinmiş gibi seçmiyor.

Matematik uzmanı ham kayıtlardan sayımları yeniden hesapladı, Muhalif dosya özetleri ve çıktı eşitliğini denetledi, morfoloji uzmanı örnek bağlantıları gözden geçirdi. [Bağımsız ajan denetimi](C:/Users/HAKAN/Documents/ChatGPT/TurkTokenizer/DENETIM-P128.json) geçti. Tek rol cevabı çıkan 11 örneğin tamamında G0 dışında kalan adaylar da bulunuyor; bu nedenle koşullu gramer kapsamı özellikle korunmalı.

## Küçük modele giden sonraki adım

Şimdi elimizde modele eklenebilecek **sözcüklere bağlı ilişki bilgisi** var. Henüz bunu tüketen bir SLM mekanizması yok. Sonraki tasarım, bu ilişkileri BPE parça aralıklarıyla eşleyip küçük modelin hesaplamasına taşımayı ele almalı; etiketi ekleyip modelin kendiliğinden kullanmasını bekleyen eski P127 reçetesi aynen büyütülmemeli.

Kontroller aynı küçük model, aynı eğitim metinleri ve karşılaştırılabilir hesap bütçesiyle yapılmalı: olağan BPE; BPE + eşdeğer morfolojik bilgi; gerçek bağlı ilişkiler; bağlantıları bozulan fakat bilgi miktarı benzer kontrol. Başarı sorusu, sözcükler aynıyken kişi/nesne/iyelik/kapsam değişimini doğru ayırt edebilmek olmalı. Bağlı ilişkilerin BPE sistemine de verilebildiği açıkça kabul edilmeli; katkı hangi bileşendeyse ona yazılmalı.

**SLM Türkçe anlama kazancı veya BPE üstünlüğü henüz gösterilmedi.** P127'nin olumsuz sonucu değişmedi. Buradaki kazanım, tartıştığımız bağıntıların çalıştırılabilir ve denetlenebilir hale gelmesi.

## Dosyalar

- [Deney raporu](V:/TurkTokenizer/Deneyler/P128-20260924/REPORT.md)
- [Matematik ve kapsam sözleşmesi](V:/TurkTokenizer/Deneyler/P128-20260924/DESIGN.md)
- [Rust bağlayıcı](V:/TurkTokenizer/Deneyler/P128-20260924/src/binding.rs)
- [Ham native sonuçlar](V:/TurkTokenizer/Deneyler/P128-20260924/results/native-raw.json)
- [Mühendislik doğrulamalarının ham kaydı](V:/TurkTokenizer/Deneyler/P128-20260924/results/contract-raw.json)
