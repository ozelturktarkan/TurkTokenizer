# GitHub'a elle yükleme

1. GitHub'da boş bir TürkTokenizer deposu oluşturun. Kaynak ZIP'ini açın; **içindeki dosyaları** depo köküne yükleyin. ZIP'in kendisi README yerine geçmez. Büyük research ZIP'i Git dosyası olarak yüklemeyin.
2. Releases → Draft a new release; etiket `v0.1.0-rc.1`, başlık `TürkTokenizer 0.1.0rc1 — Araştırma ön sürümü`. Pre-release kutusunu seçin.
3. `RELEASE_NOTES.md` metnini açıklamaya koyun. `TurkTokenizer-0.1.0rc1-windows-x64-research.zip`, wrapper `.whl` ve `SHA256SUMS.txt` dosyalarını release varlığı olarak ekleyin.
4. README/CITATION kurucu/mimar bilgisini içerir. Lisans kapsamını ve üçüncü taraf bildirimlerini birlikte tutun. Özel e-posta taslağı ve özgün düzenleme belgeleri yayın paketine dahil değildir.

GitHub tarayıcı dosya yüklemesi sınırı 25 MiB, normal Git dosyası engeli 100 MiB'dir. Büyük ikili dosyalar Releases'e ayrılır. Kontrol edilen resmi kaynak: https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github ve https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases .

## Yerel yeniden paketleme

Windows'ta Rust 1.95.0 + MSVC araçlarıyla `powershell -File native/build.ps1` derler. `python -m pip wheel --no-deps --no-build-isolation . -w dist` sarmalayıcı wheel'ini oluşturur (setuptools/wheel kurulu olmalıdır). `TURKTOKENIZER_RUNTIME` ayarlı iken `python -m unittest discover -s tests` runtime testlerini çalıştırır. Tam release içindeki verileri başka bir sürüme kopyalarken manifesti yeni dosya hash'leriyle yeniden üretin; eski makbuzları güncelleyerek geçmişi değiştirmeyin.
