# TürkTokenizer: P2 sonrası devam noktası

Geliştirme için önerilen açık giriş: `s06e_p2_policy.Tokenizer(strength=1.0)`. E05 ana varsayılanı korunuyor.

P2 IMST kolunda eski kök+tür: DEV 3174/4070, CALIB 1751/2266; önceki E05 toplamına göre net +14. Yanlış kesin karar toplamı 978 → 962. Yeni sözlüksel çıktı 3350/4070 ve 1876/2266; aynı çıktı sözleşmesiyle puanlayıcı katkısı net +144. Temsil katmanının ayrı katkısı net +171. Bunlar aynı tür doğruluk artışı olarak birleştirilmez.

Ana rapor: `S06E-E05-P2-degerlendirmesi.md`. Ek soru deneyi: `results_lexical_p2/question-report.md`. Deneylerin protokol, eğitim, DEV seçimi ve CALIB kayıtları `results_lexical_p2` ile `training_controls/lexical_p2` içindedir.

Kalan somut açık: “Sen geldin mi?” sorusundaki mi nota adı seçilebiliyor. Sonraki inceleme, soru ve nota okumalarının E05 UA, sözlüksel başlık ve cümle geçiş puanlarını aynı sabit adaylar üzerinde ayırmaktır. Yeni kuralı yalnız bir cümleye göre zorlamadan soru/nota karşıt kullanımlarıyla sınamak gerekir.

Eski 270 vakalık lemma+tür tanısını, yeni görünüm ölçümüyle yeniden yorumlamak gerekir; temsil uyuşmazlığı ve gerçek analiz eksikliği ayrı tutulmalıdır. %92 morfolojik doğruluk veya <%8 BPE hedefi henüz sağlanmadı. TEST açılmadı.

Özel deney kökü: `V:\TurkTokenizer\Yedekler\A123-E70-P9-OF3\runs\a1-large-20260908-v1\P2-lexical-v1`. İlk çift yedek: `snapshots/copy-a`, `snapshots/copy-b`; ek deney yedeği: `snapshots/question-addendum/copy-a`, `copy-b`. Aynı fiziksel V sürücüsündeler; önceki proje tabanı gereklidir.

GitHub hedefi: `ozelturktarkan/TurkTokenizer`, dal `codex/s06e-e05-p1-phonology`. Doğrulanmış önceki commit: `d6ac73c55e4fc3603b8cbb3cd69cfa4df1f6e69d`. Bu P2 tesliminin uzak doğrulama kaydı yerelde `results_lexical_p2/publication-receipt.json` olarak tutulur; kaydın yokluğu gönderimin henüz doğrulanmadığı anlamına gelir.
