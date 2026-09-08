# A1 → A3 → A2: E70 / P9 / OF3

Durum: **Bir sonraki gerçek epoch eğiticisi için hazır kontrol paketi.**
Bu paket eğitim başlatmaz. Mevcut `fit_a1.py`, `fit_a3.py`, çalışan süreçler ve
ana çalışma klasörünün Git durumu değiştirilmedi. Bu iki eğitici L-BFGS kullanır;
optimizasyon iterasyonları epoch olarak sayılmaz. Her epoch bütün sabit eğitim
örnekleri üzerinden bir tam geçiş olmalıdır. A3'te yeniden aday madenciliği bir
sonraki geçişten önce yapılır.

## Sabit kurallar

- A1 ve A3 için ayrı ayrı en fazla **70 epoch**.
- Sabit DEV kümesinde, tam çözücüyle ölçülen doğru lemma + tür sayısı ana ölçüt.
  Payda değişirse koşu reddedilir. TEST bu kararlara dahil edilmez.
- Güvenlik kontrollerini geçen katı bir doğruluk artışı yeni en iyi checkpoint'tir.
  Eşitlik yeni tepe değildir. Yeni tepede sabır 0/9 olur; art arda 9 başarısız
  epoch'ta eğitim durur. Güvensiz bir tepe eski güvenli tepenin yerine geçmez.
- Overfitting denetimi **E21'de** başlar. Önceki epoch'a göre TRAIN loss'u düşer,
  DEV loss'u yükselir ve DEV doğruluğu en iyi güvenli değerin altında kalırsa
  sinyal oluşur. Loss farkı için epsilon 1e-8. Art arda 3 sinyalde durur;
  sinyal yoksa sayaç sıfırlanır. Bu bir operasyonel belirti, kusursuz teşhis değildir.
- Loss karşılaştırması aynı örnekler, aynı aday karşıtları ve aynı ölçek üzerinde
  yapılmalıdır. A3'ün değişen hard-negative havuzunun anlık loss'u yerine sabit
  TRAIN/DEV tanı kümelerindeki loss kullanılmalıdır.
- Her durma nedeninde seçilen ağırlıklar **en iyi güvenli epoch** ağırlıklarıdır.
  Hiç güvenli epoch yoksa sonuç başarısızdır; güvensiz ağırlıklar seçilmez.
- A2, dondurulmuş model üzerinde yalnız CALIB ile yapılan eşik kalibrasyonudur.
  A2 için 70 epoch tanımlanmamıştır.

## V: yedekleri

`open_run` üretim giriş noktası, V: yoksa hata verir. Koşular ve Git nesneleri
`V:\TurkTokenizer\Yedekler\A123-E70-P9-OF3` altında tutulur.
Her epoch için `weights` ve `trainer_state` zorunludur. Ağırlıklar ve durum bilgisi
`copy-a` ve `copy-b` klasörlerine yazılır; SHA-256 değerleri karşılaştırıldıktan
sonra epoch tamamlandı olarak kaydedilir. Her kopyada son iki epoch ve en iyi
epoch korunur. Küçük metrik olay kayıtları bütün epoch'lar için saklanır.

İki kopya aynı V: diskindedir; disk arızasına karşı iki bağımsız yedek sayılmaz.
Yazım sonrası en az 5 GiB boşluk bırakılır. Alan yetersizse veya doğrulama
başarısızsa eğitim güvenle durmalıdır; C:'ye sessiz geçiş yapılmaz. Güç kesintisi
veya süreç öldürülmesinden kalan kilit/kısmi snapshot için otomatik silme yoktur;
doğrulanmış önceki checkpoint üzerinden kurtarma gerekir.

## GitHub

Hedef: `https://github.com/ozelturktarkan/TurkTokenizer.git`.
Her koşu/aşama `codex/e70-p9-logs/<run-id>-<stage>` dalını kullanır.
Yalnız `state.json`, `metrics.jsonl`, yapılandırılmış `training.log` ve
`checkpoint-sha256.json` gönderilir. Bu log; epoch, TRAIN/DEV loss, DEV doğruluğu,
sayaçlar ve durma nedenini içerir. Ham konsol çıktısı, eğitim verileri ve ağırlıklar
bu Git yayın kapsamına girmez.

Git işlemleri V: üzerindeki ayrı bare depoda yapılır; proje checkout'u ve ana dal
değişmez. Her epoch yerel commit oluşturulur ve push denenir. Push başarısızsa
yerel commit korunur; sonraki epoch veya `run.sync()` yeniden dener. Sonuç ayrıca
`github-sync.json` dosyasına yazılır. Ağ erişimi ve Git yazma yetkisi gerekir.
Force push yoktur. Hazırlık paketinin yayımlanması, bir eğitim epoch'unun
tamamlandığı anlamına gelmez.

## Eğiticiye bağlama

```python
from training_controls.e70p9.runtime import open_run

run = open_run('ornek-yeni-kosu', 'A3')  # A1 için ayrı durum/sabır bütçesi
# Her gerçek tam eğitim geçişi ve sabit DEV değerlendirmesi bittikten sonra:
result = run.complete_epoch(
    epoch,
    train_loss=fixed_train_probe_loss,
    dev_loss=fixed_dev_loss,
    dev_correct=int(full_decoder_dev_correct),
    dev_total=int(fixed_dev_total),
    safe=bool(safety_checks_pass),
    artifacts={
        'weights': weights_file_on_v,
        'trainer_state': trainer_state_file_on_v,
    },
)
if result['stop']:
    # Eğitici bu dosyayı yüklemeli, güncellemeleri durdurmalı ve A2'ye geçmelidir.
    chosen = result['best_checkpoint']
    if chosen is None:
        raise RuntimeError('Hiç güvenli checkpoint yok')
    load_weights(chosen['weights'])
    # break
```

`load_weights` eğiticinin kendi yükleme işlemini temsil eder; kontrol paketi model
belleğini kendiliğinden değiştirmez. Bütün ağırlık/durum dosyaları çağrı boyunca
sabit kalmalıdır. Durum dosyası; optimizer, rastgelelik durumları, veri bölümü
kimlikleri, aday/özellik sürümleri ve epoch bilgisini içermelidir. Sadece sayaç
kaydetmek tam eğitim devamlılığı sağlamaz. Güvenlik kontrollerinin kapsamını
eğitici tanımlar; kancaya koşulsuz `safe=True` bağlanmamalıdır.

Gerekli entegrasyon: L-BFGS yerine gerçek geçiş sınırları olan A1/A3 eğitim
döngüsü; sabit tanı loss'u ve tam çözücü DEV ölçümü; eksiksiz V: durum kaydı;
durma sonucuna uyulması ve seçilen checkpoint'in yüklenmesi. Bu entegrasyon
**mevcut çalışan koşuya uygulanmış değildir**.

Test: `python -m unittest training_controls.e70p9.test_controls -v`.
Testler küçük sentetik dosyalar ve yerel bir Git deposu kullanır; gerçek eğitim
verisini okumaz ve GitHub'a sahte epoch metrikleri göndermez.
