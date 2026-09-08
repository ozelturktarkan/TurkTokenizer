# P2 soru eki hizalaması: ek deney

Soru okumalarının PART etiketi yalnız n-gram puanlamasında AUX ile hizalandı. Dört lisanslı soru sözlük kaydı başlangıçta doğrulandı; nota adı olan NOUN okuması değiştirilmedi. Yeni eğitim, aday veya eşik araması yapılmadı.

| Kol | DEV kök+tür | DEV özellik | DEV yanlış kesin | DEV sözlüksel çıktı | CALIB kök+tür | CALIB özellik | CALIB yanlış kesin | CALIB sözlüksel çıktı |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| P2 IMST | 3174 | 3045 | 595 | 3350 | 1751 | 1680 | 367 | 1876 |
| Soru hizalama | 3174 | 3045 | 595 | 3350 | 1751 | 1680 | 367 | 1876 |

Önceden tanımlanan eski ölçütlerde gerilememe kontrolü: **True**. Ölçülen ek kazanç var mı: **False**. Gerilememe tek başına ek katmanı önerme nedeni sayılmadı. Teslim önerisi: `s06e_p2_policy.Tokenizer(strength=1.0)`. Genel proje varsayılanı değiştirilmedi.

Elle yazılmış bağlam tanılarında eşleşme **7/8**. “Sen geldin mi?” örneği hâlâ mi/NOUN seçiyor. Bu nedenle etiketi hizalamak tek başına bu anlam seçimi sorununu çözmüş sayılmaz.

İlk koşu iki DEV cümlesinden sonra durdu: aday sırası testi, çözümleyicinin paylaşılan önbellek listesini ters çevirmişti. Taze çalışma aynı adayları ve sırayı verdi; yanlışlık yalnız testin yan etkisiydi. Test girdisi derin kopyalanarak ayrı klasörde baştan çalıştırıldı. Adayların sırası ve içeriği için eşitlik kontrolü gevşetilmedi; ilk başarısız koşu korundu.

Tamamlanan ek koşuda 293 DEV + 382 CALIB cümlesinin morfolojik adayları P2 ile birebir karşılaştırıldı; toplam puan bağımsız yordamla, BPE ile geri kurma her çıktıda doğrulandı. DEV/CALIB geliştirmede görülmüş verilerdir; bağımsız test değildir. TEST açılmadı.

Ana P2 sonuçları ve temsil/seçim katkısı ayrı ana rapordadır. Bu ek deney onun dondurulmuş kaynaklarını veya 106 dosyalık çift yedeğini değiştirmez. Ek dosyalar snapshots/question-addendum altında ayrıca iki kez hash doğrulamasıyla saklanır.
