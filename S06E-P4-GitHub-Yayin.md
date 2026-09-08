# S06E P4 GitHub kayıt kapsamı

2026-09-09: Kullanıcının yeni yayın onayıyla, P1 dalında bekleyen P2 çalışması ile P3 ve P4 kaynakları, testleri ve sonuç raporları birlikte kaydedilir. Hedef depo `ozelturktarkan/TurkTokenizer`, dal `codex/s06e-e05-p1-phonology`.

Yerel P2/P3/P4 deney raporları ve hash ile dondurulmuş kaynaklar tarihsel kayıt olarak aynen korunur. Deponun `PUBLICATION_POLICY.md` sınırına uygun olarak, GitHub rapor kopyalarında özel veri havuzu/önbellek/çıktı hashleri `[PRIVATE_HASH_OMITTED]` ile değiştirilir; sayısal sonuçlar korunur. Bu özet kopyalar tam yerel doğrulama manifestlerinin yerine kullanılamaz. Eski belgelerdeki “GitHub onayı bekliyor / yayımlanmadı” ifadeleri deneyin tamamlandığı ana aittir; bu yayın yeni kullanıcı onayını izler.

## Sonuç ve kullanım

P4'ün seçilmiş deneysel yapılandırması `HR_0.25`: çıktı görünümü başlığı katsayısı 1, bu başlığa hizalı sıralayıcı katkısı 0,25. DEV'de seçildi, CALIB'de önceden belirlenmiş gerilememe kontrollerini geçti. Eski varsayılan otomatik yükseltilmedi.

DEV+CALIB toplam 6.336 sözcükte çıktı lemma+tür doğruluğu 5.226 → 5.270 (%82,48 → %83,18); yerel başlangıç kökü+tür doğruluğu 4.925 → 4.948 (%77,73 → %78,09). Çıktıda 93 eski hata düzeldi, 49 yeni gerileme oluştu. Doğru görünümü her adayda geri plana atan başlık vakaları 55 → 94: iki seçim katmanı tamamen çözülmüş değildir. %92 hedefi karşılanmadı; bağımsız TEST açılmadı.

Tam karşılaştırma: [P4 değerlendirmesi](S06E-P4-Iki-Secim-Katmani-degerlendirmesi.md). Önceki deney: [P3 YÖNT değerlendirmesi](S06E-P3-YONT-degerlendirmesi.md).

Bu commit bir kaynak ve deney kaydıdır. Ham eğitim havuzları, cümle başına değerlendirme dökümleri, öğrenilmiş tam model ağırlıkları ve yerel yedek arşivleri bu yayında bulunmaz. `model-location.json` dosyaları, yereldeki modele ait konum ve doğrulama hashlerini içerir; model dosyasının kendisi değildir. Çalıştırmak için mevcut proje tabanı, bağımlılıklar ve hashleri eşleşen özel model dosyaları gerekir. Yeni bir makinede yalnız bu commit'i indirmek yeterli değildir.

Yerel tam ortamda seçili P4 modeli `s06e_p4.load_selected()` ile açılır. `Tokenizer()` sıfır katkılı kontrol yapılandırmasını korur. 224.309 mevcut kimliğin korunması ve kayıpsız BPE metin geri dönüşü doğrulanmıştır; bu, her morfolojik kararın doğru olduğu anlamına gelmez.

P4'ün iki V kopyasında 101'er dosya SHA256 ile doğrulanmıştır. Kopyalar aynı fiziksel sürücüdedir ve önceki proje tabanını gerektiren artımlı yedeklerdir. Yayın dosyalarının açık listesi `training-runs/a1-large-20260908-v1/P4-two-layer-v1/github-manifest.json` içinde bulunur. GitHub commit ve dal doğrulamasının nihai makbuzu yerelde `results_publication_p4/publication-receipt.json` dosyasına yazılır.
