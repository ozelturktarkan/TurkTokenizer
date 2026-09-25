# TürkTokenizer — Sınıflandırılmış ek sözlüğü

**Kurucu / Mimar: Tarkan Özel** · P21 sözleşmesi / P119 native tablo

Bu belge çalışan Rust tablosunun 876 kaydını, 43 sınıf altında listeler. 752 kayıt üretime açıktır; bütün koşullarda uygulanabildikleri anlamına gelmez. 747 kayıt türü `suffix` olan satır vardır. Yüzey varyantları, sıfır morfemler, yokluk işaretleri, klitikler ve kurallar ayrı kayıt sayılır; 876 bağımsız ek iddiası değildir.

S05 tabanı 852 kayıttır; native tabloda P9 kökenli 16 ve P21 kökenli 8 ek kayıt vardır. Önceki 843 sayısı bu sürümün sayımı değildir. Kayıt ID, morfem kimliği ve sayısal token ID birbirinden farklıdır. Örneğin clE0001=ler ve clE0002=lar aynı NUMBER_PL morfeminin yüzeyleridir. R kural, K ayrı birim sınıflarında da görünür; sıra numarası anlamsal öncelik taşımaz.

`∅`: boş yüzey. `—`: yüzey eklenmesi uygulanmıyor. Evet/Hayır: generator_enabled karşılığı. Girdi/çıktı türleri yürütücü sınıflarıdır; tek başlarına kullanım izni değildir. Tam koşullar, şablon ve kaynak atıfları [S05 JSON](registry/s05-v0.3.1.json) ve [native kayıt JSON](registry/native-records.json) içindedir. P9/P21 ekleri native kaynak satırına bağlıdır. Sözlük bir bağımsız dilbilim doğruluk sertifikası değildir.

| Sınıf | Başlık | Kayıt | Üretime açık |
|---|---|---:|---:|
| apR | 11. Ses ve yazım kural kayıtları | 1 | 0 |
| atE | 4.5. Aitlik/ilgi — atE | 3 | 2 |
| bfE | 5.6. Ek-fiil/kopula — bfE | 37 | 35 |
| bgK | 9.3. Bağlayıcı ki — bgK | 3 | 1 |
| bvE | 7. Betimleyici/birleşik fiil biçimleri — bvE | 33 | 32 |
| clE | 4.1. Çokluk — clE | 4 | 3 |
| ctE | 5.1. Çatı — ctE | 48 | 44 |
| diR | 11. Ses ve yazım kural kayıtları | 1 | 0 |
| ffE | 8.11. Fiilden fiil — ffE | 7 | 6 |
| fiE | 8.9. Fiilden kalıcı isim — fiE | 73 | 63 |
| flE | 6. Fiilimsiler — ad-fiiller, sıfat-fiiller ve zarf-fiiller | 111 | 106 |
| fsE | 8.10. Fiilden kalıcı sıfat/zarf — fsE | 35 | 26 |
| hdR | 11. Ses ve yazım kural kayıtları | 1 | 0 |
| hlE | 4.3. Durum/hal — hlE | 45 | 42 |
| ifE | 8.3. İsimden fiil — ifE | 25 | 20 |
| iiE | 8.1. İsimden isim — iiE | 29 | 28 |
| isE | 8.2. İsimden sıfat/zarf — isE | 58 | 49 |
| isK | 9.4. ise — isK | 4 | 3 |
| kcE | 8.6. Küçültme/sevecenlik — kcE | 27 | 21 |
| ksE | Z paradigması | 76 | 68 |
| kvR | 10. Pekiştirme sonek değildir — kvR | 6 | 0 |
| kyR | 11. Ses ve yazım kural kayıtları | 4 | 0 |
| odK | 9.2. Odak/ekleme da/de — odK | 3 | 2 |
| olE | 5.2. Kutupluluk — olE | 9 | 6 |
| sdE | 4.6. Sayı türetimleri — sdE | 18 | 16 |
| sfE | 8.5. Sıfattan fiil — sfE | 11 | 9 |
| siE | 8.4. Sıfattan isim — siE | 17 | 9 |
| soK | 9.1. Soru — soK | 5 | 4 |
| spR | 11. Ses ve yazım kural kayıtları | 1 | 0 |
| suR | 11. Ses ve yazım kural kayıtları | 1 | 0 |
| syE | 8.8. Aile/topluluk ve saygı bağlantısı — syE | 2 | 1 |
| udR | 11. Ses ve yazım kural kayıtları | 3 | 0 |
| unR | 11. Ses ve yazım kural kayıtları | 4 | 0 |
| uoR | 11. Ses ve yazım kural kayıtları | 1 | 0 |
| uyR | 11. Ses ve yazım kural kayıtları | 2 | 0 |
| uzR | 11. Ses ve yazım kural kayıtları | 1 | 0 |
| vtE | 4.4. Vasıta/birliktelik ve eşitlik — vtE | 15 | 14 |
| ybE | 5.3. Yeterlik/olasılık — ybE | 9 | 8 |
| ylE | 4.2. İyelik — ylE | 52 | 51 |
| ypE | 8.12. Ödünç bağlı biçimler ve sonekimsiler — ypE9xxx | 22 | 20 |
| zaR | 11. Ses ve yazım kural kayıtları | 2 | 0 |
| zmE | 5.4. Zaman–görünüş–kip — zmE | 45 | 45 |
| zyE | 8.7. Benzerlik/zayıflatma — zyE | 22 | 18 |

## apR — 11. Ses ve yazım kural kayıtları

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| apR0001 | — | Özel ad/kısaltmada sınıfa bağlı kesme / PROCESS_apR0001 |  →  | rule | Hayır |

## atE — 4.5. Aitlik/ilgi — atE

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| atE0000 | ∅ | yok / ABSENCE_atE |  →  | absence_marker | Hayır |
| atE0001 | ki | İlgi/aitlik ile sıfat veya zamir / REL_KI_ADJ, REL_KI_PRON | NOUN,PROPN,PRON,NOMINALIZED,ADV → ADJ,PRON | suffix | Evet |
| atE0002 | kü | İlgi/aitlik ile sıfat veya zamir / REL_KI_ADJ, REL_KI_PRON | NOUN,PROPN,PRON,NOMINALIZED,ADV → ADJ,PRON | suffix | Evet |

## bfE — 5.6. Ek-fiil/kopula — bfE

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| bfE0000 | ∅ | Sıfır şimdiki ek-fiil / COP_PRESENT | PREDICATE → PREDICATE | zero_morpheme | Evet |
| bfE0001 | dı | Geçmiş ek-fiil / COP_PAST | PREDICATE → PREDICATE | suffix | Evet |
| bfE0002 | di | Geçmiş ek-fiil / COP_PAST | PREDICATE → PREDICATE | suffix | Evet |
| bfE0003 | du | Geçmiş ek-fiil / COP_PAST | PREDICATE → PREDICATE | suffix | Evet |
| bfE0004 | dü | Geçmiş ek-fiil / COP_PAST | PREDICATE → PREDICATE | suffix | Evet |
| bfE0005 | tı | Geçmiş ek-fiil / COP_PAST | PREDICATE → PREDICATE | suffix | Evet |
| bfE0006 | ti | Geçmiş ek-fiil / COP_PAST | PREDICATE → PREDICATE | suffix | Evet |
| bfE0007 | tu | Geçmiş ek-fiil / COP_PAST | PREDICATE → PREDICATE | suffix | Evet |
| bfE0008 | tü | Geçmiş ek-fiil / COP_PAST | PREDICATE → PREDICATE | suffix | Evet |
| bfE0009 | ydı | Geçmiş ek-fiil / COP_PAST | PREDICATE → PREDICATE | suffix | Evet |
| bfE0010 | ydi | Geçmiş ek-fiil / COP_PAST | PREDICATE → PREDICATE | suffix | Evet |
| bfE0011 | ydu | Geçmiş ek-fiil / COP_PAST | PREDICATE → PREDICATE | suffix | Evet |
| bfE0012 | ydü | Geçmiş ek-fiil / COP_PAST | PREDICATE → PREDICATE | suffix | Evet |
| bfE0013 | mış | Dolaylı kanıtsallık ek-fiili / COP_EVID | PREDICATE → PREDICATE | suffix | Evet |
| bfE0014 | miş | Dolaylı kanıtsallık ek-fiili / COP_EVID | PREDICATE → PREDICATE | suffix | Evet |
| bfE0015 | muş | Dolaylı kanıtsallık ek-fiili / COP_EVID | PREDICATE → PREDICATE | suffix | Evet |
| bfE0016 | müş | Dolaylı kanıtsallık ek-fiili / COP_EVID | PREDICATE → PREDICATE | suffix | Evet |
| bfE0017 | ymış | Dolaylı kanıtsallık ek-fiili / COP_EVID | PREDICATE → PREDICATE | suffix | Evet |
| bfE0018 | ymiş | Dolaylı kanıtsallık ek-fiili / COP_EVID | PREDICATE → PREDICATE | suffix | Evet |
| bfE0019 | ymuş | Dolaylı kanıtsallık ek-fiili / COP_EVID | PREDICATE → PREDICATE | suffix | Evet |
| bfE0020 | ymüş | Dolaylı kanıtsallık ek-fiili / COP_EVID | PREDICATE → PREDICATE | suffix | Evet |
| bfE0021 | sa | Şart ek-fiili / COP_COND | PREDICATE → PREDICATE | suffix | Evet |
| bfE0022 | se | Şart ek-fiili / COP_COND | PREDICATE → PREDICATE | suffix | Evet |
| bfE0023 | ysa | Şart ek-fiili / COP_COND | PREDICATE → PREDICATE | suffix | Evet |
| bfE0024 | yse | Şart ek-fiili / COP_COND | PREDICATE → PREDICATE | suffix | Evet |
| bfE0025 | ken | Ek-fiil ile eşzamanlılık / COP_WHILE | PREDICATE → ADV | suffix | Evet |
| bfE0026 | yken | Ek-fiil ile eşzamanlılık / COP_WHILE | PREDICATE → ADV | suffix | Evet |
| bfE0027 | ya | Sınırlı şart ek-fiili adayı / COP_COND_YA | PREDICATE → PREDICATE | suffix | Hayır |
| bfE0028 | ye | Sınırlı şart ek-fiili adayı / COP_COND_YA | PREDICATE → PREDICATE | suffix | Hayır |
| bfE0029 | dır | Bildirme/genelleme / COP_GENERAL | PREDICATE → PREDICATE | suffix | Evet |
| bfE0030 | dir | Bildirme/genelleme / COP_GENERAL | PREDICATE → PREDICATE | suffix | Evet |
| bfE0031 | dur | Bildirme/genelleme / COP_GENERAL | PREDICATE → PREDICATE | suffix | Evet |
| bfE0032 | dür | Bildirme/genelleme / COP_GENERAL | PREDICATE → PREDICATE | suffix | Evet |
| bfE0033 | tır | Bildirme/genelleme / COP_GENERAL | PREDICATE → PREDICATE | suffix | Evet |
| bfE0034 | tir | Bildirme/genelleme / COP_GENERAL | PREDICATE → PREDICATE | suffix | Evet |
| bfE0035 | tur | Bildirme/genelleme / COP_GENERAL | PREDICATE → PREDICATE | suffix | Evet |
| bfE0036 | tür | Bildirme/genelleme / COP_GENERAL | PREDICATE → PREDICATE | suffix | Evet |

## bgK — 9.3. Bağlayıcı ki — bgK

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| bgK0000 | ∅ | bgK / ABSENCE_bgK |  →  | absence_marker | Hayır |
| bgK0001 | ki | Bağlayıcı ki / CONJ_KI, DISCOURSE_KI | CLAUSE,HOST → CONJ,PARTICLE | particle | Evet |
| bgK0002 | kü | Çünkü içindeki tarihî parça / LEX_CUNKU_COMPONENT | LEXICAL_BASE → CONJ | composite_display | Hayır |

## bvE — 7. Betimleyici/birleşik fiil biçimleri — bvE

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| bvE0000 | ∅ | yok / ABSENCE_bvE |  →  | absence_marker | Hayır |
| bvE0001 | ıver | Tezlik / V_HASTE | VERB → VERB | suffix | Evet |
| bvE0002 | iver | Tezlik / V_HASTE | VERB → VERB | suffix | Evet |
| bvE0003 | uver | Tezlik / V_HASTE | VERB → VERB | suffix | Evet |
| bvE0004 | üver | Tezlik / V_HASTE | VERB → VERB | suffix | Evet |
| bvE0005 | yıver | Tezlik / V_HASTE | VERB → VERB | suffix | Evet |
| bvE0006 | yiver | Tezlik / V_HASTE | VERB → VERB | suffix | Evet |
| bvE0007 | yuver | Tezlik / V_HASTE | VERB → VERB | suffix | Evet |
| bvE0008 | yüver | Tezlik / V_HASTE | VERB → VERB | suffix | Evet |
| bvE0009 | agel | Süregelme / V_EVER | VERB → VERB | suffix | Evet |
| bvE0010 | egel | Süregelme / V_EVER | VERB → VERB | suffix | Evet |
| bvE0011 | yagel | Süregelme / V_EVER | VERB → VERB | suffix | Evet |
| bvE0012 | yegel | Süregelme / V_EVER | VERB → VERB | suffix | Evet |
| bvE0013 | adur | Süredurma / V_CONTINUE | VERB → VERB | suffix | Evet |
| bvE0014 | edur | Süredurma / V_CONTINUE | VERB → VERB | suffix | Evet |
| bvE0015 | yadur | Süredurma / V_CONTINUE | VERB → VERB | suffix | Evet |
| bvE0016 | yedur | Süredurma / V_CONTINUE | VERB → VERB | suffix | Evet |
| bvE0017 | agör | -Agör yardımcı-eylem yapısı; süreklilik/uyarı / V_TRY | VERB → VERB | suffix | Evet |
| bvE0018 | egör | -Agör yardımcı-eylem yapısı; süreklilik/uyarı / V_TRY | VERB → VERB | suffix | Evet |
| bvE0019 | yagör | -Agör yardımcı-eylem yapısı; süreklilik/uyarı / V_TRY | VERB → VERB | suffix | Evet |
| bvE0020 | yegör | -Agör yardımcı-eylem yapısı; süreklilik/uyarı / V_TRY | VERB → VERB | suffix | Evet |
| bvE0021 | akal | Durumda kalma / V_STAY | VERB → VERB | suffix | Evet |
| bvE0022 | ekal | Durumda kalma / V_STAY | VERB → VERB | suffix | Evet |
| bvE0023 | yakal | Durumda kalma / V_STAY | VERB → VERB | suffix | Evet |
| bvE0024 | yekal | Durumda kalma / V_STAY | VERB → VERB | suffix | Evet |
| bvE0025 | akoy | Başlama/sürdürme / V_START | VERB → VERB | suffix | Evet |
| bvE0026 | ekoy | Başlama/sürdürme / V_START | VERB → VERB | suffix | Evet |
| bvE0027 | yakoy | Başlama/sürdürme / V_START | VERB → VERB | suffix | Evet |
| bvE0028 | yekoy | Başlama/sürdürme / V_START | VERB → VERB | suffix | Evet |
| bvE0029 | ayaz | Yaklaşma / V_ALMOST | VERB → VERB | suffix | Evet |
| bvE0030 | eyaz | Yaklaşma / V_ALMOST | VERB → VERB | suffix | Evet |
| bvE0031 | yayaz | Yaklaşma / V_ALMOST | VERB → VERB | suffix | Evet |
| bvE0032 | yeyaz | Yaklaşma / V_ALMOST | VERB → VERB | suffix | Evet |

## clE — 4.1. Çokluk — clE

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| clE0000 | ∅ | Number=Sing/Unmarked / ABSENCE_clE |  →  | absence_marker | Hayır |
| clE0001 | ler | Ad çokluğu / NUMBER_PL | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| clE0002 | lar | Ad çokluğu / NUMBER_PL | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| P9:clE:zero3pl | ∅ | Ad çokluğu / NUMBER_PL | PRON → PRON | zero_morpheme | Evet |

## ctE — 5.1. Çatı — ctE

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| ctE0000 | ∅ | yalın etken / ABSENCE_ctE |  →  | absence_marker | Hayır |
| ctE0001 | ış | İşteş çatı / VOICE_RECIP | VERB → VERB | suffix | Evet |
| ctE0002 | iş | İşteş çatı / VOICE_RECIP | VERB → VERB | suffix | Evet |
| ctE0003 | uş | İşteş çatı / VOICE_RECIP | VERB → VERB | suffix | Evet |
| ctE0004 | üş | İşteş çatı / VOICE_RECIP | VERB → VERB | suffix | Evet |
| ctE0005 | ş | İşteş çatı / VOICE_RECIP | VERB → VERB | suffix | Evet |
| ctE0006 | ın | Dönüşlü çatı / VOICE_REFL | VERB → VERB | suffix | Evet |
| ctE0007 | in | Dönüşlü çatı / VOICE_REFL | VERB → VERB | suffix | Evet |
| ctE0008 | un | Dönüşlü çatı / VOICE_REFL | VERB → VERB | suffix | Evet |
| ctE0009 | ün | Dönüşlü çatı / VOICE_REFL | VERB → VERB | suffix | Evet |
| ctE0010 | n | Dönüşlü çatı / VOICE_REFL | VERB → VERB | suffix | Evet |
| ctE0011 | ıl | Edilgen çatı / VOICE_PASS | VERB → VERB | suffix | Evet |
| ctE0012 | il | Edilgen çatı / VOICE_PASS | VERB → VERB | suffix | Evet |
| ctE0013 | ul | Edilgen çatı / VOICE_PASS | VERB → VERB | suffix | Evet |
| ctE0014 | ül | Edilgen çatı / VOICE_PASS | VERB → VERB | suffix | Evet |
| ctE0015 | l | Edilgen çatı / VOICE_PASS | VERB → VERB | suffix | Hayır |
| ctE0016 | ın | Edilgen çatı / VOICE_PASS | VERB → VERB | suffix | Evet |
| ctE0017 | in | Edilgen çatı / VOICE_PASS | VERB → VERB | suffix | Evet |
| ctE0018 | un | Edilgen çatı / VOICE_PASS | VERB → VERB | suffix | Evet |
| ctE0019 | ün | Edilgen çatı / VOICE_PASS | VERB → VERB | suffix | Evet |
| ctE0020 | n | Edilgen çatı / VOICE_PASS | VERB → VERB | suffix | Evet |
| ctE0021 | nıl | Edilgen çatı / VOICE_PASS | VERB → VERB | suffix | Evet |
| ctE0022 | nil | Edilgen çatı / VOICE_PASS | VERB → VERB | suffix | Evet |
| ctE0023 | nul | Edilgen çatı / VOICE_PASS | VERB → VERB | suffix | Evet |
| ctE0024 | nül | Edilgen çatı / VOICE_PASS | VERB → VERB | suffix | Evet |
| ctE0025 | t | Ettirgen çatı / VOICE_CAUS | VERB → VERB | suffix | Evet |
| ctE0026 | dır | Ettirgen çatı / VOICE_CAUS | VERB → VERB | suffix | Evet |
| ctE0027 | dir | Ettirgen çatı / VOICE_CAUS | VERB → VERB | suffix | Evet |
| ctE0028 | dur | Ettirgen çatı / VOICE_CAUS | VERB → VERB | suffix | Evet |
| ctE0029 | dür | Ettirgen çatı / VOICE_CAUS | VERB → VERB | suffix | Evet |
| ctE0030 | tır | Ettirgen çatı / VOICE_CAUS | VERB → VERB | suffix | Evet |
| ctE0031 | tir | Ettirgen çatı / VOICE_CAUS | VERB → VERB | suffix | Evet |
| ctE0032 | tur | Ettirgen çatı / VOICE_CAUS | VERB → VERB | suffix | Evet |
| ctE0033 | tür | Ettirgen çatı / VOICE_CAUS | VERB → VERB | suffix | Evet |
| ctE0034 | ır | Ettirgen çatı / VOICE_CAUS | VERB → VERB | suffix | Evet |
| ctE0035 | ir | Ettirgen çatı / VOICE_CAUS | VERB → VERB | suffix | Evet |
| ctE0036 | ur | Ettirgen çatı / VOICE_CAUS | VERB → VERB | suffix | Evet |
| ctE0037 | ür | Ettirgen çatı / VOICE_CAUS | VERB → VERB | suffix | Evet |
| ctE0038 | ar | Ettirgen çatı / VOICE_CAUS | VERB → VERB | suffix | Evet |
| ctE0039 | er | Ettirgen çatı / VOICE_CAUS | VERB → VERB | suffix | Evet |
| ctE0040 | ıt | Ettirgen çatı / VOICE_CAUS | VERB → VERB | suffix | Evet |
| ctE0041 | it | Ettirgen çatı / VOICE_CAUS | VERB → VERB | suffix | Evet |
| ctE0042 | ut | Ettirgen çatı / VOICE_CAUS | VERB → VERB | suffix | Evet |
| ctE0043 | üt | Ettirgen çatı / VOICE_CAUS | VERB → VERB | suffix | Evet |
| ctE0044 | at | Ettirgen çatı / VOICE_CAUS | VERB → VERB | suffix | Evet |
| ctE0045 | et | Ettirgen çatı / VOICE_CAUS | VERB → VERB | suffix | Evet |
| ctE0046 | art | Ettirgen bileşik gösterimi / VOICE_CAUS_STACK | VERB → VERB | composite_display | Hayır |
| ctE0047 | ert | Ettirgen bileşik gösterimi / VOICE_CAUS_STACK | VERB → VERB | composite_display | Hayır |

## diR — 11. Ses ve yazım kural kayıtları

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| diR0001 | — | de/ye için geçişe bağlı gövde seçimi / PROCESS_diR0001 |  →  | rule | Hayır |

## ffE — 8.11. Fiilden fiil — ffE

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| ffE0000 | ∅ | türetim yok / ABSENCE_ffE |  →  | absence_marker | Hayır |
| ffE0001 | ala | Sözlüksel yineleme/yoğunluk / V_REPEAT_ALA | VERB → VERB | suffix | Evet |
| ffE0002 | ele | Sözlüksel yineleme/yoğunluk / V_REPEAT_ALA | VERB → VERB | suffix | Evet |
| ffE0003 | ıştır | Sözlüksel yineleme/yoğunluk / V_REPEAT_ISTIR | VERB → VERB | suffix | Evet |
| ffE0004 | iştir | Sözlüksel yineleme/yoğunluk / V_REPEAT_ISTIR | VERB → VERB | suffix | Evet |
| ffE0005 | uştur | Sözlüksel yineleme/yoğunluk / V_REPEAT_ISTIR | VERB → VERB | suffix | Evet |
| ffE0006 | üştür | Sözlüksel yineleme/yoğunluk / V_REPEAT_ISTIR | VERB → VERB | suffix | Evet |

## fiE — 8.9. Fiilden kalıcı isim — fiE

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| fiE0000 | ∅ | türetim yok / ABSENCE_fiE |  →  | absence_marker | Hayır |
| fiE0001 | ım | Eylem/sonuç adı / VN_IM | VERB → NOUN | suffix | Evet |
| fiE0002 | im | Eylem/sonuç adı / VN_IM | VERB → NOUN | suffix | Evet |
| fiE0003 | um | Eylem/sonuç adı / VN_IM | VERB → NOUN | suffix | Evet |
| fiE0004 | üm | Eylem/sonuç adı / VN_IM | VERB → NOUN | suffix | Evet |
| fiE0005 | ı | Sözlüksel eylem/sonuç adı / VN_I | VERB → NOUN | suffix | Evet |
| fiE0006 | i | Sözlüksel eylem/sonuç adı / VN_I | VERB → NOUN | suffix | Evet |
| fiE0007 | u | Sözlüksel eylem/sonuç adı / VN_I | VERB → NOUN | suffix | Evet |
| fiE0008 | ü | Sözlüksel eylem/sonuç adı / VN_I | VERB → NOUN | suffix | Evet |
| fiE0009 | gı | Ürün/araç/sonuç / VN_GI | VERB → NOUN | suffix | Evet |
| fiE0010 | gi | Ürün/araç/sonuç / VN_GI | VERB → NOUN | suffix | Evet |
| fiE0011 | gu | Ürün/araç/sonuç / VN_GI | VERB → NOUN | suffix | Evet |
| fiE0012 | gü | Ürün/araç/sonuç / VN_GI | VERB → NOUN | suffix | Evet |
| fiE0013 | kı | Ürün/araç/sonuç / VN_GI | VERB → NOUN | suffix | Evet |
| fiE0014 | ki | Ürün/araç/sonuç / VN_GI | VERB → NOUN | suffix | Evet |
| fiE0015 | ku | Ürün/araç/sonuç / VN_GI | VERB → NOUN | suffix | Evet |
| fiE0016 | kü | Ürün/araç/sonuç / VN_GI | VERB → NOUN | suffix | Evet |
| fiE0017 | gın | Durum/kişi adı / VN_GIN | VERB → NOUN | suffix | Evet |
| fiE0018 | gin | Durum/kişi adı / VN_GIN | VERB → NOUN | suffix | Evet |
| fiE0019 | gun | Durum/kişi adı / VN_GIN | VERB → NOUN | suffix | Evet |
| fiE0020 | gün | Durum/kişi adı / VN_GIN | VERB → NOUN | suffix | Evet |
| fiE0021 | kın | Durum/kişi adı / VN_GIN | VERB → NOUN | suffix | Evet |
| fiE0022 | kin | Durum/kişi adı / VN_GIN | VERB → NOUN | composite_display | Hayır |
| fiE0023 | kun | Durum/kişi adı / VN_GIN | VERB → NOUN | composite_display | Hayır |
| fiE0024 | kün | Durum/kişi adı / VN_GIN | VERB → NOUN | composite_display | Hayır |
| fiE0025 | ınç | Duygu/sonuç adı / VN_INC | VERB → NOUN | suffix | Evet |
| fiE0026 | inç | Duygu/sonuç adı / VN_INC | VERB → NOUN | suffix | Evet |
| fiE0027 | unç | Duygu/sonuç adı / VN_INC | VERB → NOUN | suffix | Hayır |
| fiE0028 | ünç | Duygu/sonuç adı / VN_INC | VERB → NOUN | suffix | Evet |
| fiE0029 | ak | Yer/araç/sonuç / VN_AK | VERB → NOUN | suffix | Evet |
| fiE0030 | ek | Yer/araç/sonuç / VN_AK | VERB → NOUN | suffix | Evet |
| fiE0031 | gaç | Araç adı / VN_GAC | VERB → NOUN | suffix | Evet |
| fiE0032 | geç | Araç adı / VN_GAC | VERB → NOUN | suffix | Evet |
| fiE0033 | kaç | Araç adı / VN_GAC | VERB → NOUN | suffix | Evet |
| fiE0034 | keç | Araç adı / VN_GAC | VERB → NOUN | suffix | Hayır |
| fiE0035 | tı | Sonuç/belirti / VN_TI | VERB → NOUN | suffix | Evet |
| fiE0036 | ti | Sonuç/belirti / VN_TI | VERB → NOUN | suffix | Evet |
| fiE0037 | tu | Sonuç/belirti / VN_TI | VERB → NOUN | suffix | Evet |
| fiE0038 | tü | Sonuç/belirti / VN_TI | VERB → NOUN | suffix | Evet |
| fiE0039 | dı | Sonuç/belirti / VN_DI | VERB → NOUN | suffix | Evet |
| fiE0040 | di | Sonuç/belirti / VN_DI | VERB → NOUN | suffix | Evet |
| fiE0041 | du | Sonuç/belirti / VN_DI | VERB → NOUN | suffix | Evet |
| fiE0042 | dü | Sonuç/belirti / VN_DI | VERB → NOUN | suffix | Hayır |
| fiE0043 | ca | Eylem/sonuç adı / VN_CA | VERB → NOUN | suffix | Evet |
| fiE0044 | ce | Eylem/sonuç adı / VN_CA | VERB → NOUN | suffix | Evet |
| fiE0045 | ça | Eylem/sonuç adı / VN_CA | VERB → NOUN | suffix | Evet |
| fiE0046 | çe | Eylem/sonuç adı / VN_CA | VERB → NOUN | suffix | Hayır |
| fiE0047 | maca | Oyun/nesne adı / VN_MACA | VERB → NOUN | suffix | Evet |
| fiE0048 | mece | Oyun/nesne adı / VN_MACA | VERB → NOUN | suffix | Evet |
| fiE0049 | ıt | Araç/ürün / VN_IT | VERB → NOUN | suffix | Evet |
| fiE0050 | it | Araç/ürün / VN_IT | VERB → NOUN | suffix | Evet |
| fiE0051 | ut | Araç/ürün / VN_IT | VERB → NOUN | suffix | Evet |
| fiE0052 | üt | Araç/ürün / VN_IT | VERB → NOUN | suffix | Evet |
| fiE0053 | ay | Eylem/sonuç adı / VN_AY | VERB → NOUN | suffix | Evet |
| fiE0054 | ey | Eylem/sonuç adı / VN_AY | VERB → NOUN | suffix | Hayır |
| fiE0055 | av | Eylem/sonuç adı / VN_AV | VERB → NOUN | suffix | Hayır |
| fiE0056 | ev | Eylem/sonuç adı / VN_AV | VERB → NOUN | suffix | Evet |
| fiE0057 | man | Kişi/meslek / VN_MAN | VERB → NOUN | suffix | Evet |
| fiE0058 | men | Kişi/meslek / VN_MAN | VERB → NOUN | suffix | Evet |
| fiE0059 | gıç | Sınırlı yapan/kişi adı / VN_GIC | VERB → NOUN | suffix | Evet |
| fiE0060 | giç | Sınırlı yapan/kişi adı / VN_GIC | VERB → NOUN | suffix | Evet |
| fiE0061 | maç | Sınırlı araç/sonuç adı / VN_MAC | VERB → NOUN | suffix | Evet |
| fiE0062 | meç | Sınırlı araç/sonuç adı / VN_MAC | VERB → NOUN | suffix | Evet |
| fiE0063 | y | Eylem/sonuç adı / VN_AY | VERB → NOUN | suffix | Evet |
| fiE0064 | v | Eylem/sonuç adı / VN_AV | VERB → NOUN | suffix | Evet |
| P9:fiE:fsE0001 | ıcı | V_AGENT / V_AGENT | VERB → NOUN | suffix | Evet |
| P9:fiE:fsE0002 | ici | V_AGENT / V_AGENT | VERB → NOUN | suffix | Evet |
| P9:fiE:fsE0003 | ucu | V_AGENT / V_AGENT | VERB → NOUN | suffix | Evet |
| P9:fiE:fsE0004 | ücü | V_AGENT / V_AGENT | VERB → NOUN | suffix | Evet |
| P9:fiE:fsE0005 | yıcı | V_AGENT / V_AGENT | VERB → NOUN | suffix | Evet |
| P9:fiE:fsE0006 | yici | V_AGENT / V_AGENT | VERB → NOUN | suffix | Evet |
| P9:fiE:fsE0007 | yucu | V_AGENT / V_AGENT | VERB → NOUN | suffix | Evet |
| P9:fiE:fsE0008 | yücü | V_AGENT / V_AGENT | VERB → NOUN | suffix | Evet |

## flE — 6. Fiilimsiler — ad-fiiller, sıfat-fiiller ve zarf-fiiller

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| flE0000 | ∅ | fiilimsi yok / ABSENCE_flE |  →  | absence_marker | Hayır |
| flE0001 | mak | Mastar / INF_MAK | VERB → NOMINALIZED | suffix | Evet |
| flE0002 | mek | Mastar / INF_MAK | VERB → NOMINALIZED | suffix | Evet |
| flE0003 | ma | Eylem adı / VN_MA | VERB → NOMINALIZED | suffix | Evet |
| flE0004 | me | Eylem adı / VN_MA | VERB → NOMINALIZED | suffix | Evet |
| flE0005 | ış | Oluş/kılış adı / VN_IS | VERB → NOMINALIZED | suffix | Evet |
| flE0006 | iş | Oluş/kılış adı / VN_IS | VERB → NOMINALIZED | suffix | Evet |
| flE0007 | uş | Oluş/kılış adı / VN_IS | VERB → NOMINALIZED | suffix | Evet |
| flE0008 | üş | Oluş/kılış adı / VN_IS | VERB → NOMINALIZED | suffix | Evet |
| flE0009 | yış | Oluş/kılış adı / VN_IS | VERB → NOMINALIZED | suffix | Evet |
| flE0010 | yiş | Oluş/kılış adı / VN_IS | VERB → NOMINALIZED | suffix | Evet |
| flE0011 | yuş | Oluş/kılış adı / VN_IS | VERB → NOMINALIZED | suffix | Evet |
| flE0012 | yüş | Oluş/kılış adı / VN_IS | VERB → NOMINALIZED | suffix | Evet |
| flE0013 | an | Özne odaklı sıfat-fiil / PART_AN | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0014 | en | Özne odaklı sıfat-fiil / PART_AN | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0015 | yan | Özne odaklı sıfat-fiil / PART_AN | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0016 | yen | Özne odaklı sıfat-fiil / PART_AN | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0017 | dık | DIK sıfat-fiili/adlaştırma / PART_DIK | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0018 | dik | DIK sıfat-fiili/adlaştırma / PART_DIK | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0019 | duk | DIK sıfat-fiili/adlaştırma / PART_DIK | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0020 | dük | DIK sıfat-fiili/adlaştırma / PART_DIK | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0021 | tık | DIK sıfat-fiili/adlaştırma / PART_DIK | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0022 | tik | DIK sıfat-fiili/adlaştırma / PART_DIK | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0023 | tuk | DIK sıfat-fiili/adlaştırma / PART_DIK | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0024 | tük | DIK sıfat-fiili/adlaştırma / PART_DIK | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0025 | acak | Gelecek sıfat-fiili/adlaştırma / PART_FUT | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0026 | ecek | Gelecek sıfat-fiili/adlaştırma / PART_FUT | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0027 | yacak | Gelecek sıfat-fiili/adlaştırma / PART_FUT | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0028 | yecek | Gelecek sıfat-fiili/adlaştırma / PART_FUT | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0029 | acağ | Gelecek sıfat-fiili/adlaştırma / PART_FUT | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0030 | eceğ | Gelecek sıfat-fiili/adlaştırma / PART_FUT | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0031 | yacağ | Gelecek sıfat-fiili/adlaştırma / PART_FUT | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0032 | yeceğ | Gelecek sıfat-fiili/adlaştırma / PART_FUT | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0033 | mış | mIş sıfat-fiili / PART_MIS | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0034 | miş | mIş sıfat-fiili / PART_MIS | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0035 | muş | mIş sıfat-fiili / PART_MIS | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0036 | müş | mIş sıfat-fiili / PART_MIS | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0037 | ar | Geniş zaman sıfat-fiili / PART_AOR | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0038 | er | Geniş zaman sıfat-fiili / PART_AOR | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0039 | ır | Geniş zaman sıfat-fiili / PART_AOR | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0040 | ir | Geniş zaman sıfat-fiili / PART_AOR | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0041 | ur | Geniş zaman sıfat-fiili / PART_AOR | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0042 | ür | Geniş zaman sıfat-fiili / PART_AOR | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0043 | r | Geniş zaman sıfat-fiili / PART_AOR | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0044 | maz | Olumsuz geniş sıfat-fiili bileşik gösterimi / NEG_PART_AOR_DISPLAY | VERB → ADJ | composite_display | Hayır |
| flE0045 | mez | Olumsuz geniş sıfat-fiili bileşik gösterimi / NEG_PART_AOR_DISPLAY | VERB → ADJ | composite_display | Hayır |
| flE0046 | ası | İstek/eğilim sıfat-fiili / PART_ASI | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0047 | esi | İstek/eğilim sıfat-fiili / PART_ASI | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0048 | yası | İstek/eğilim sıfat-fiili / PART_ASI | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0049 | yesi | İstek/eğilim sıfat-fiili / PART_ASI | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0050 | ıp | Sıralama zarf-fiili / CONV_IP | VERB → ADV | suffix | Evet |
| flE0051 | ip | Sıralama zarf-fiili / CONV_IP | VERB → ADV | suffix | Evet |
| flE0052 | up | Sıralama zarf-fiili / CONV_IP | VERB → ADV | suffix | Evet |
| flE0053 | üp | Sıralama zarf-fiili / CONV_IP | VERB → ADV | suffix | Evet |
| flE0054 | yıp | Sıralama zarf-fiili / CONV_IP | VERB → ADV | suffix | Evet |
| flE0055 | yip | Sıralama zarf-fiili / CONV_IP | VERB → ADV | suffix | Evet |
| flE0056 | yup | Sıralama zarf-fiili / CONV_IP | VERB → ADV | suffix | Evet |
| flE0057 | yüp | Sıralama zarf-fiili / CONV_IP | VERB → ADV | suffix | Evet |
| flE0058 | arak | Tarz zarf-fiili / CONV_ARAK | VERB → ADV | suffix | Evet |
| flE0059 | erek | Tarz zarf-fiili / CONV_ARAK | VERB → ADV | suffix | Evet |
| flE0060 | yarak | Tarz zarf-fiili / CONV_ARAK | VERB → ADV | suffix | Evet |
| flE0061 | yerek | Tarz zarf-fiili / CONV_ARAK | VERB → ADV | suffix | Evet |
| flE0062 | ınca | Zaman zarf-fiili / CONV_INCA | VERB → ADV | suffix | Evet |
| flE0063 | ince | Zaman zarf-fiili / CONV_INCA | VERB → ADV | suffix | Evet |
| flE0064 | unca | Zaman zarf-fiili / CONV_INCA | VERB → ADV | suffix | Evet |
| flE0065 | ünce | Zaman zarf-fiili / CONV_INCA | VERB → ADV | suffix | Evet |
| flE0066 | yınca | Zaman zarf-fiili / CONV_INCA | VERB → ADV | suffix | Evet |
| flE0067 | yince | Zaman zarf-fiili / CONV_INCA | VERB → ADV | suffix | Evet |
| flE0068 | yunca | Zaman zarf-fiili / CONV_INCA | VERB → ADV | suffix | Evet |
| flE0069 | yünce | Zaman zarf-fiili / CONV_INCA | VERB → ADV | suffix | Evet |
| flE0070 | alı | Başlangıçtan beri / CONV_ALI | VERB → ADV | suffix | Evet |
| flE0071 | eli | Başlangıçtan beri / CONV_ALI | VERB → ADV | suffix | Evet |
| flE0072 | yalı | Başlangıçtan beri / CONV_ALI | VERB → ADV | suffix | Evet |
| flE0073 | yeli | Başlangıçtan beri / CONV_ALI | VERB → ADV | suffix | Evet |
| flE0074 | dıkça | Süreklilik/oran / CONV_DIKCA | VERB → ADV | suffix | Evet |
| flE0075 | dikçe | Süreklilik/oran / CONV_DIKCA | VERB → ADV | suffix | Evet |
| flE0076 | dukça | Süreklilik/oran / CONV_DIKCA | VERB → ADV | suffix | Evet |
| flE0077 | dükçe | Süreklilik/oran / CONV_DIKCA | VERB → ADV | suffix | Evet |
| flE0078 | tıkça | Süreklilik/oran / CONV_DIKCA | VERB → ADV | suffix | Evet |
| flE0079 | tikçe | Süreklilik/oran / CONV_DIKCA | VERB → ADV | suffix | Evet |
| flE0080 | tukça | Süreklilik/oran / CONV_DIKCA | VERB → ADV | suffix | Evet |
| flE0081 | tükçe | Süreklilik/oran / CONV_DIKCA | VERB → ADV | suffix | Evet |
| flE0082 | asıya | -(y)AsIyA zarf-fiili; uç derece/sınır / CONV_ASIYA | VERB → ADV | suffix | Evet |
| flE0083 | esiye | -(y)AsIyA zarf-fiili; uç derece/sınır / CONV_ASIYA | VERB → ADV | suffix | Evet |
| flE0084 | yasıya | -(y)AsIyA zarf-fiili; uç derece/sınır / CONV_ASIYA | VERB → ADV | suffix | Evet |
| flE0085 | yesiye | -(y)AsIyA zarf-fiili; uç derece/sınır / CONV_ASIYA | VERB → ADV | suffix | Evet |
| flE0086 | madan | Olumsuz zarf-fiil / CONV_MADAN | VERB → ADV | suffix | Evet |
| flE0087 | meden | Olumsuz zarf-fiil / CONV_MADAN | VERB → ADV | suffix | Evet |
| flE0088 | maksızın | Yoksunluk zarf-fiili / CONV_MAKSIZIN | VERB → ADV | suffix | Evet |
| flE0089 | meksizin | Yoksunluk zarf-fiili / CONV_MAKSIZIN | VERB → ADV | suffix | Evet |
| flE0090 | a | Yinelemeli zarf-fiil / CONV_REPEAT_A | VERB → ADV | suffix | Evet |
| flE0091 | e | Yinelemeli zarf-fiil / CONV_REPEAT_A | VERB → ADV | suffix | Evet |
| flE0092 | ya | Yinelemeli zarf-fiil / CONV_REPEAT_A | VERB → ADV | suffix | Evet |
| flE0093 | ye | Yinelemeli zarf-fiil / CONV_REPEAT_A | VERB → ADV | suffix | Evet |
| flE0094 | ken | Eşzamanlılık / CONV_KEN | PREDICATE → ADV | suffix | Evet |
| flE0095 | yken | Eşzamanlılık / CONV_KEN | PREDICATE → ADV | suffix | Evet |
| flE0096 | casına | Gibi davranma / CONV_CASINA | VERB → ADV | suffix | Evet |
| flE0097 | cesine | Gibi davranma / CONV_CASINA | VERB → ADV | suffix | Evet |
| flE0098 | çasına | Gibi davranma / CONV_CASINA | VERB → ADV | suffix | Evet |
| flE0099 | çesine | Gibi davranma / CONV_CASINA | VERB → ADV | suffix | Evet |
| flE0100 | masına | Eylem adı + iyelik + yönelme gösterimi / VN_POSS_DAT_DISPLAY | VERB → NOMINALIZED | composite_display | Hayır |
| flE0101 | mesine | Eylem adı + iyelik + yönelme gösterimi / VN_POSS_DAT_DISPLAY | VERB → NOMINALIZED | composite_display | Hayır |
| flE0102 | z | Olumsuz geniş sıfat-fiili z gerçekleşmesi / PART_AOR | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0103 | dığ | DIK sıfat-fiili, ünlülü devam / PART_DIK | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0104 | diğ | DIK sıfat-fiili, ünlülü devam / PART_DIK | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0105 | duğ | DIK sıfat-fiili, ünlülü devam / PART_DIK | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0106 | düğ | DIK sıfat-fiili, ünlülü devam / PART_DIK | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0107 | tığ | DIK sıfat-fiili, ünlülü devam / PART_DIK | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0108 | tiğ | DIK sıfat-fiili, ünlülü devam / PART_DIK | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0109 | tuğ | DIK sıfat-fiili, ünlülü devam / PART_DIK | VERB → ADJ,NOMINALIZED | suffix | Evet |
| flE0110 | tüğ | DIK sıfat-fiili, ünlülü devam / PART_DIK | VERB → ADJ,NOMINALIZED | suffix | Evet |

## fsE — 8.10. Fiilden kalıcı sıfat/zarf — fsE

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| fsE0000 | ∅ | türetim yok / ABSENCE_fsE |  →  | absence_marker | Hayır |
| fsE0001 | ıcı | Yapan/araç/alışkanlık / V_INHERENT | VERB → ADJ,ADV | suffix | Evet |
| fsE0002 | ici | Yapan/araç/alışkanlık / V_INHERENT | VERB → ADJ,ADV | suffix | Evet |
| fsE0003 | ucu | Yapan/araç/alışkanlık / V_INHERENT | VERB → ADJ,ADV | suffix | Evet |
| fsE0004 | ücü | Yapan/araç/alışkanlık / V_INHERENT | VERB → ADJ,ADV | suffix | Evet |
| fsE0005 | yıcı | Yapan/araç/alışkanlık / V_INHERENT | VERB → ADJ,ADV | suffix | Evet |
| fsE0006 | yici | Yapan/araç/alışkanlık / V_INHERENT | VERB → ADJ,ADV | suffix | Evet |
| fsE0007 | yucu | Yapan/araç/alışkanlık / V_INHERENT | VERB → ADJ,ADV | suffix | Evet |
| fsE0008 | yücü | Yapan/araç/alışkanlık / V_INHERENT | VERB → ADJ,ADV | suffix | Evet |
| fsE0009 | gan | Eğilim/süreklilik / V_GAN | VERB → ADJ,ADV | suffix | Evet |
| fsE0010 | gen | Eğilim/süreklilik / V_GAN | VERB → ADJ,ADV | suffix | Evet |
| fsE0011 | kan | Eğilim/süreklilik / V_GAN | VERB → ADJ,ADV | suffix | Evet |
| fsE0012 | ken | Eğilim/süreklilik / V_GAN | VERB → ADJ | suffix | Evet |
| fsE0013 | ık | Sonuç niteliği / V_IK | VERB → ADJ,ADV | suffix | Evet |
| fsE0014 | ik | Sonuç niteliği / V_IK | VERB → ADJ,ADV | suffix | Evet |
| fsE0015 | uk | Sonuç niteliği / V_IK | VERB → ADJ,ADV | suffix | Evet |
| fsE0016 | ük | Sonuç niteliği / V_IK | VERB → ADJ,ADV | suffix | Evet |
| fsE0017 | mış | Sözlükselleşmiş geçmiş nitelik / LEX_PART_MIS | VERB → ADJ | composite_display | Hayır |
| fsE0018 | miş | Sözlükselleşmiş geçmiş nitelik / LEX_PART_MIS | VERB → ADJ | composite_display | Hayır |
| fsE0019 | muş | Sözlükselleşmiş geçmiş nitelik / LEX_PART_MIS | VERB → ADJ | composite_display | Hayır |
| fsE0020 | müş | Sözlükselleşmiş geçmiş nitelik / LEX_PART_MIS | VERB → ADJ | composite_display | Hayır |
| fsE0021 | ak | Eğilim/sonuç / V_AK | VERB → ADJ,ADV | suffix | Evet |
| fsE0022 | ek | Eğilim/sonuç / V_AK | VERB → ADJ,ADV | suffix | Evet |
| fsE0023 | gın | Durum/eğilim / V_GIN | VERB → ADJ,ADV | suffix | Evet |
| fsE0024 | gin | Durum/eğilim / V_GIN | VERB → ADJ,ADV | suffix | Evet |
| fsE0025 | gun | Durum/eğilim / V_GIN | VERB → ADJ,ADV | suffix | Evet |
| fsE0026 | gün | Durum/eğilim / V_GIN | VERB → ADJ,ADV | suffix | Evet |
| fsE0027 | kın | Durum/eğilim / V_GIN | VERB → ADJ,ADV | suffix | Evet |
| fsE0028 | kin | Durum/eğilim / V_GIN | VERB → ADJ,ADV | suffix | Evet |
| fsE0029 | kun | Durum/eğilim / V_GIN | VERB → ADJ,ADV | suffix | Evet |
| fsE0030 | kün | Durum/eğilim / V_GIN | VERB → ADJ,ADV | suffix | Evet |
| fsE0031 | ası | Sözlükselleşmiş tasarlanan nitelik / LEX_PART_ASI | VERB → ADJ | composite_display | Hayır |
| fsE0032 | esi | Sözlükselleşmiş tasarlanan nitelik / LEX_PART_ASI | VERB → ADJ | composite_display | Hayır |
| fsE0033 | yası | Sözlükselleşmiş tasarlanan nitelik / LEX_PART_ASI | VERB → ADJ | composite_display | Hayır |
| fsE0034 | yesi | Sözlükselleşmiş tasarlanan nitelik / LEX_PART_ASI | VERB → ADJ | composite_display | Hayır |

## hdR — 11. Ses ve yazım kural kayıtları

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| hdR0001 | — | Sözlüksel ünsüz düşmesi/değişmesi / PROCESS_hdR0001 |  →  | rule | Hayır |

## hlE — 4.3. Durum/hal — hlE

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| hlE0000 | ∅ | Case=Nom/Bare / ABSENCE_hlE |  →  | absence_marker | Hayır |
| hlE0001 | ı | Hâl: Acc / CASE_ACC | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| hlE0002 | i | Hâl: Acc / CASE_ACC | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| hlE0003 | u | Hâl: Acc / CASE_ACC | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| hlE0004 | ü | Hâl: Acc / CASE_ACC | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| hlE0005 | yı | Hâl: Acc / CASE_ACC | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| hlE0006 | yi | Hâl: Acc / CASE_ACC | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| hlE0007 | yu | Hâl: Acc / CASE_ACC | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| hlE0008 | yü | Hâl: Acc / CASE_ACC | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| hlE0009 | nı | Hâl: Acc / CASE_ACC | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| hlE0010 | ni | Hâl: Acc / CASE_ACC | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| hlE0011 | nu | Hâl: Acc / CASE_ACC | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| hlE0012 | nü | Hâl: Acc / CASE_ACC | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| hlE0013 | a | Hâl: Dat / CASE_DAT | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| hlE0014 | e | Hâl: Dat / CASE_DAT | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| hlE0015 | ya | Hâl: Dat / CASE_DAT | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| hlE0016 | ye | Hâl: Dat / CASE_DAT | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| hlE0017 | na | Hâl: Dat / CASE_DAT | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| hlE0018 | ne | Hâl: Dat / CASE_DAT | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| hlE0019 | da | Hâl: Loc / CASE_LOC | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| hlE0020 | de | Hâl: Loc / CASE_LOC | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| hlE0021 | ta | Hâl: Loc / CASE_LOC | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| hlE0022 | te | Hâl: Loc / CASE_LOC | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| hlE0023 | nda | Hâl: Loc / CASE_LOC | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| hlE0024 | nde | Hâl: Loc / CASE_LOC | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| hlE0025 | dan | Hâl: Abl / CASE_ABL | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| hlE0026 | den | Hâl: Abl / CASE_ABL | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| hlE0027 | tan | Hâl: Abl / CASE_ABL | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| hlE0028 | ten | Hâl: Abl / CASE_ABL | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| hlE0029 | ndan | Hâl: Abl / CASE_ABL | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| hlE0030 | nden | Hâl: Abl / CASE_ABL | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| hlE0031 | ın | Hâl: Gen / CASE_GEN | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| hlE0032 | in | Hâl: Gen / CASE_GEN | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| hlE0033 | un | Hâl: Gen / CASE_GEN | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| hlE0034 | ün | Hâl: Gen / CASE_GEN | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| hlE0035 | nın | Hâl: Gen / CASE_GEN | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| hlE0036 | nin | Hâl: Gen / CASE_GEN | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| hlE0037 | nun | Hâl: Gen / CASE_GEN | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| hlE0038 | nün | Hâl: Gen / CASE_GEN | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| hlE0039 | yın | Hâl: Gen / CASE_GEN | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Hayır |
| hlE0040 | yin | Hâl: Gen / CASE_GEN | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| hlE0041 | yun | Hâl: Gen / CASE_GEN | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| hlE0042 | yün | Hâl: Gen / CASE_GEN | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Hayır |
| hlE0043 | im | Ben/biz genitifi / CASE_GEN | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| P9:hlE:pron:im | im | Hâl: Gen / CASE_GEN | PRON → PRON | suffix | Evet |

## ifE — 8.3. İsimden fiil — ifE

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| ifE0000 | ∅ | türetim yok / ABSENCE_ifE |  →  | absence_marker | Hayır |
| ifE0001 | la | Yapma/uygulama / MAKE | NOUN,PROPN,PRON,NOMINALIZED → VERB | suffix | Evet |
| ifE0002 | le | Yapma/uygulama / MAKE | NOUN,PROPN,PRON,NOMINALIZED → VERB | suffix | Evet |
| ifE0003 | lan | Edinme/durumlanma / ACQUIRE | NOUN,PROPN,PRON,NOMINALIZED → VERB | suffix | Evet |
| ifE0004 | len | Edinme/durumlanma / ACQUIRE | NOUN,PROPN,PRON,NOMINALIZED → VERB | suffix | Evet |
| ifE0005 | laş | Dönüşme / BECOME | NOUN,PROPN,PRON,NOMINALIZED → VERB | suffix | Evet |
| ifE0006 | leş | Dönüşme / BECOME | NOUN,PROPN,PRON,NOMINALIZED → VERB | suffix | Evet |
| ifE0007 | a | Sözlüksel ad-fiil türetimi / N_V_A | NOUN,PROPN,PRON,NOMINALIZED → VERB | suffix | Evet |
| ifE0008 | e | Sözlüksel ad-fiil türetimi / N_V_A | NOUN,PROPN,PRON,NOMINALIZED → VERB | suffix | Evet |
| ifE0009 | ı | Sözlüksel ad-fiil türetimi / N_V_I | NOUN,PROPN,PRON,NOMINALIZED → VERB | suffix | Evet |
| ifE0010 | i | Sözlüksel ad-fiil türetimi / N_V_I | NOUN,PROPN,PRON,NOMINALIZED → VERB | suffix | Hayır |
| ifE0011 | u | Sözlüksel ad-fiil türetimi / N_V_I | NOUN,PROPN,PRON,NOMINALIZED → VERB | suffix | Evet |
| ifE0012 | ü | Sözlüksel ad-fiil türetimi / N_V_I | NOUN,PROPN,PRON,NOMINALIZED → VERB | suffix | Hayır |
| ifE0013 | al | Durum değişimi / N_V_AL | NOUN,PROPN,PRON,NOMINALIZED → VERB | suffix | Hayır |
| ifE0014 | el | Durum değişimi / N_V_AL | NOUN,PROPN,PRON,NOMINALIZED → VERB | suffix | Evet |
| ifE0015 | ar | Renk/durum değişimi / N_V_AR | NOUN,PROPN,PRON,NOMINALIZED → VERB | suffix | Evet |
| ifE0016 | er | Renk/durum değişimi / N_V_AR | NOUN,PROPN,PRON,NOMINALIZED → VERB | suffix | Evet |
| ifE0017 | sa | Sayma/değer verme / N_V_SA | NOUN,PROPN,PRON,NOMINALIZED → VERB | suffix | Evet |
| ifE0018 | se | Sayma/değer verme / N_V_SA | NOUN,PROPN,PRON,NOMINALIZED → VERB | suffix | Evet |
| ifE0019 | ımsa | Sözlüksel benimseme/küçümseme / N_V_IMSA | NOUN,PROPN,PRON,NOMINALIZED → VERB | suffix | Evet |
| ifE0020 | imse | Sözlüksel benimseme/küçümseme / N_V_IMSA | NOUN,PROPN,PRON,NOMINALIZED → VERB | suffix | Evet |
| ifE0021 | umsa | Sözlüksel benimseme/küçümseme / N_V_IMSA | NOUN,PROPN,PRON,NOMINALIZED → VERB | suffix | Hayır |
| ifE0022 | ümse | Sözlüksel benimseme/küçümseme / N_V_IMSA | NOUN,PROPN,PRON,NOMINALIZED → VERB | suffix | Evet |
| ifE0023 | da | Yansıma gövdeden fiil / SOUND_VERB | IDEO → VERB | suffix | Evet |
| ifE0024 | de | Yansıma gövdeden fiil / SOUND_VERB | IDEO → VERB | suffix | Evet |

## iiE — 8.1. İsimden isim — iiE

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| iiE0000 | ∅ | türetim yok / ABSENCE_iiE |  →  | absence_marker | Hayır |
| iiE0001 | lık | Ad/yer/araç/soyutluk / N_NESS_PLACE | NOUN,PROPN,PRON,NOMINALIZED → NOUN | suffix | Evet |
| iiE0002 | lik | Ad/yer/araç/soyutluk / N_NESS_PLACE | NOUN,PROPN,PRON,NOMINALIZED → NOUN | suffix | Evet |
| iiE0003 | luk | Ad/yer/araç/soyutluk / N_NESS_PLACE | NOUN,PROPN,PRON,NOMINALIZED → NOUN | suffix | Evet |
| iiE0004 | lük | Ad/yer/araç/soyutluk / N_NESS_PLACE | NOUN,PROPN,PRON,NOMINALIZED → NOUN | suffix | Evet |
| iiE0005 | cı | Kişi/meslek/yanlılık / N_AGENT | NOUN,PROPN,PRON,NOMINALIZED → NOUN | suffix | Evet |
| iiE0006 | ci | Kişi/meslek/yanlılık / N_AGENT | NOUN,PROPN,PRON,NOMINALIZED → NOUN | suffix | Evet |
| iiE0007 | cu | Kişi/meslek/yanlılık / N_AGENT | NOUN,PROPN,PRON,NOMINALIZED → NOUN | suffix | Evet |
| iiE0008 | cü | Kişi/meslek/yanlılık / N_AGENT | NOUN,PROPN,PRON,NOMINALIZED → NOUN | suffix | Evet |
| iiE0009 | çı | Kişi/meslek/yanlılık / N_AGENT | NOUN,PROPN,PRON,NOMINALIZED → NOUN | suffix | Evet |
| iiE0010 | çi | Kişi/meslek/yanlılık / N_AGENT | NOUN,PROPN,PRON,NOMINALIZED → NOUN | suffix | Evet |
| iiE0011 | çu | Kişi/meslek/yanlılık / N_AGENT | NOUN,PROPN,PRON,NOMINALIZED → NOUN | suffix | Evet |
| iiE0012 | çü | Kişi/meslek/yanlılık / N_AGENT | NOUN,PROPN,PRON,NOMINALIZED → NOUN | suffix | Evet |
| iiE0013 | daş | Ortaklık/yoldaşlık / N_FELLOW | NOUN,PROPN,PRON,NOMINALIZED → NOUN | suffix | Evet |
| iiE0014 | deş | Ortaklık/yoldaşlık / N_FELLOW | NOUN,PROPN,PRON,NOMINALIZED → NOUN | suffix | Evet |
| iiE0015 | taş | Ortaklık/yoldaşlık / N_FELLOW | NOUN,PROPN,PRON,NOMINALIZED → NOUN | suffix | Evet |
| iiE0016 | teş | Ortaklık/yoldaşlık / N_FELLOW | NOUN,PROPN,PRON,NOMINALIZED → NOUN | suffix | Evet |
| iiE0017 | cıl | Eğilim/bağlılık / N_AFFINITY | NOUN,PROPN,PRON,NOMINALIZED → NOUN | suffix | Evet |
| iiE0018 | cil | Eğilim/bağlılık / N_AFFINITY | NOUN,PROPN,PRON,NOMINALIZED → NOUN | suffix | Evet |
| iiE0019 | cul | Eğilim/bağlılık / N_AFFINITY | NOUN,PROPN,PRON,NOMINALIZED → NOUN | suffix | Evet |
| iiE0020 | cül | Eğilim/bağlılık / N_AFFINITY | NOUN,PROPN,PRON,NOMINALIZED → NOUN | suffix | Evet |
| iiE0021 | çıl | Eğilim/bağlılık / N_AFFINITY | NOUN,PROPN,PRON,NOMINALIZED → NOUN | suffix | Evet |
| iiE0022 | çil | Eğilim/bağlılık / N_AFFINITY | NOUN,PROPN,PRON,NOMINALIZED → NOUN | suffix | Evet |
| iiE0023 | çul | Eğilim/bağlılık / N_AFFINITY | NOUN,PROPN,PRON,NOMINALIZED → NOUN | suffix | Evet |
| iiE0024 | çül | Eğilim/bağlılık / N_AFFINITY | NOUN,PROPN,PRON,NOMINALIZED → NOUN | suffix | Evet |
| iiE0025 | lığ | Ad/yer/araç/soyutluk; ünlülü devam / N_NESS_PLACE | NOUN,PROPN,PRON,NOMINALIZED → NOUN | suffix | Evet |
| iiE0026 | liğ | Ad/yer/araç/soyutluk; ünlülü devam / N_NESS_PLACE | NOUN,PROPN,PRON,NOMINALIZED → NOUN | suffix | Evet |
| iiE0027 | luğ | Ad/yer/araç/soyutluk; ünlülü devam / N_NESS_PLACE | NOUN,PROPN,PRON,NOMINALIZED → NOUN | suffix | Evet |
| iiE0028 | lüğ | Ad/yer/araç/soyutluk; ünlülü devam / N_NESS_PLACE | NOUN,PROPN,PRON,NOMINALIZED → NOUN | suffix | Evet |

## isE — 8.2. İsimden sıfat/zarf — isE

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| isE0000 | ∅ | türetim yok / ABSENCE_isE |  →  | absence_marker | Hayır |
| isE0001 | lı | Bulundurma/nitelik / WITH | NOUN,PROPN,PRON,NOMINALIZED → ADJ,ADV | suffix | Evet |
| isE0002 | li | Bulundurma/nitelik / WITH | NOUN,PROPN,PRON,NOMINALIZED → ADJ,ADV | suffix | Evet |
| isE0003 | lu | Bulundurma/nitelik / WITH | NOUN,PROPN,PRON,NOMINALIZED → ADJ,ADV | suffix | Evet |
| isE0004 | lü | Bulundurma/nitelik / WITH | NOUN,PROPN,PRON,NOMINALIZED → ADJ,ADV | suffix | Evet |
| isE0005 | sız | Yoksunluk / WITHOUT | NOUN,PROPN,PRON,NOMINALIZED → ADJ,ADV | suffix | Evet |
| isE0006 | siz | Yoksunluk / WITHOUT | NOUN,PROPN,PRON,NOMINALIZED → ADJ,ADV | suffix | Evet |
| isE0007 | suz | Yoksunluk / WITHOUT | NOUN,PROPN,PRON,NOMINALIZED → ADJ,ADV | suffix | Evet |
| isE0008 | süz | Yoksunluk / WITHOUT | NOUN,PROPN,PRON,NOMINALIZED → ADJ,ADV | suffix | Evet |
| isE0009 | sal | İlişki/alan / RELATED | NOUN,PROPN,PRON,NOMINALIZED → ADJ,ADV | suffix | Evet |
| isE0010 | sel | İlişki/alan / RELATED | NOUN,PROPN,PRON,NOMINALIZED → ADJ,ADV | suffix | Evet |
| isE0011 | ca | Tarz/dil/benzerlik / DERIV_LANGUAGE_CA, DERIV_MANNER_CA, DERIV_SIMILAR_CA | NOUN,PROPN,PRON,NOMINALIZED → ADJ,ADV | suffix | Evet |
| isE0012 | ce | Tarz/dil/benzerlik / DERIV_LANGUAGE_CA, DERIV_MANNER_CA, DERIV_SIMILAR_CA | NOUN,PROPN,PRON,NOMINALIZED → ADJ,ADV | suffix | Evet |
| isE0013 | ça | Tarz/dil/benzerlik / DERIV_LANGUAGE_CA, DERIV_MANNER_CA, DERIV_SIMILAR_CA | NOUN,PROPN,PRON,NOMINALIZED → ADJ,ADV | suffix | Evet |
| isE0014 | çe | Tarz/dil/benzerlik / DERIV_LANGUAGE_CA, DERIV_MANNER_CA, DERIV_SIMILAR_CA | NOUN,PROPN,PRON,NOMINALIZED → ADJ,ADV | suffix | Evet |
| isE0015 | cıl | Eğilim/özellik / N_AFFINITY | NOUN,PROPN,PRON,NOMINALIZED → ADJ,ADV | suffix | Evet |
| isE0016 | cil | Eğilim/özellik / N_AFFINITY | NOUN,PROPN,PRON,NOMINALIZED → ADJ,ADV | suffix | Evet |
| isE0017 | cul | Eğilim/özellik / N_AFFINITY | NOUN,PROPN,PRON,NOMINALIZED → ADJ,ADV | suffix | Evet |
| isE0018 | cül | Eğilim/özellik / N_AFFINITY | NOUN,PROPN,PRON,NOMINALIZED → ADJ,ADV | suffix | Evet |
| isE0019 | çıl | Eğilim/özellik / N_AFFINITY | NOUN,PROPN,PRON,NOMINALIZED → ADJ,ADV | suffix | Evet |
| isE0020 | çil | Eğilim/özellik / N_AFFINITY | NOUN,PROPN,PRON,NOMINALIZED → ADJ,ADV | suffix | Evet |
| isE0021 | çul | Eğilim/özellik / N_AFFINITY | NOUN,PROPN,PRON,NOMINALIZED → ADJ,ADV | suffix | Evet |
| isE0022 | çül | Eğilim/özellik / N_AFFINITY | NOUN,PROPN,PRON,NOMINALIZED → ADJ,ADV | suffix | Evet |
| isE0023 | lık | Kullanım/süre ilişkisi / FOR | NOUN,PROPN,PRON,NOMINALIZED → ADJ,ADV | suffix | Evet |
| isE0024 | lik | Kullanım/süre ilişkisi / FOR | NOUN,PROPN,PRON,NOMINALIZED → ADJ,ADV | suffix | Evet |
| isE0025 | luk | Kullanım/süre ilişkisi / FOR | NOUN,PROPN,PRON,NOMINALIZED → ADJ,ADV | suffix | Evet |
| isE0026 | lük | Kullanım/süre ilişkisi / FOR | NOUN,PROPN,PRON,NOMINALIZED → ADJ,ADV | suffix | Evet |
| isE0027 | arası | Arası yapısı / INTER | NOUN,PROPN,PRON,NOMINALIZED → ADJ,ADV | composite_display | Hayır |
| isE0028 | ları | Vakit zarfı / TIME_LARI | NOUN,PROPN,PRON,NOMINALIZED → ADJ,ADV | composite_display | Hayır |
| isE0029 | leri | Vakit zarfı / TIME_LARI | NOUN,PROPN,PRON,NOMINALIZED → ADJ,ADV | composite_display | Hayır |
| isE0030 | layın | Vakit zarfı / TIME_LAYIN | NOUN,PROPN,PRON,NOMINALIZED → ADJ,ADV | suffix | Hayır |
| isE0031 | leyin | Vakit zarfı / TIME_LAYIN | NOUN,PROPN,PRON,NOMINALIZED → ADJ,ADV | suffix | Evet |
| isE0032 | lığ | Kullanım/süre ilişkisi; ünlülü devam / FOR | NOUN,PROPN,PRON,NOMINALIZED → ADJ,ADV | suffix | Evet |
| isE0033 | liğ | Kullanım/süre ilişkisi; ünlülü devam / FOR | NOUN,PROPN,PRON,NOMINALIZED → ADJ,ADV | suffix | Evet |
| isE0034 | luğ | Kullanım/süre ilişkisi; ünlülü devam / FOR | NOUN,PROPN,PRON,NOMINALIZED → ADJ,ADV | suffix | Evet |
| isE0035 | lüğ | Kullanım/süre ilişkisi; ünlülü devam / FOR | NOUN,PROPN,PRON,NOMINALIZED → ADJ,ADV | suffix | Evet |
| isE0036 | cılayın | Sınırlı eşitlik/benzerlik adayı / SIM_CILAYIN | PRON → ADV | suffix | Hayır |
| isE0037 | cileyin | Sınırlı eşitlik/benzerlik adayı / SIM_CILAYIN | PRON → ADV | suffix | Evet |
| isE0038 | dır | Süre bildiren DIr / TIME_SINCE | NOUN → ADV | suffix | Evet |
| isE0039 | dir | Süre bildiren DIr / TIME_SINCE | NOUN → ADV | suffix | Evet |
| isE0040 | dur | Süre bildiren DIr / TIME_SINCE | NOUN → ADV | suffix | Evet |
| isE0041 | dür | Süre bildiren DIr / TIME_SINCE | NOUN → ADV | suffix | Evet |
| isE0042 | tır | Süre bildiren DIr / TIME_SINCE | NOUN → ADV | suffix | Evet |
| isE0043 | tir | Süre bildiren DIr / TIME_SINCE | NOUN → ADV | suffix | Evet |
| isE0044 | tur | Süre bildiren DIr / TIME_SINCE | NOUN → ADV | suffix | Evet |
| isE0045 | tür | Süre bildiren DIr / TIME_SINCE | NOUN → ADV | suffix | Evet |
| isE0046 | cak | Topluluk/tarz / COLLECTIVE | NOUN,PROPN,PRON,NOMINALIZED,ADJ → ADV | suffix | Hayır |
| isE0047 | cek | Topluluk/tarz / COLLECTIVE | NOUN,PROPN,PRON,NOMINALIZED,ADJ → ADV | suffix | Evet |
| isE0048 | canak | Topluluk/tarz / COLLECTIVE | NOUN,PROPN,PRON,NOMINALIZED,ADJ → ADV | suffix | Hayır |
| isE0049 | cenek | Topluluk/tarz / COLLECTIVE | NOUN,PROPN,PRON,NOMINALIZED,ADJ → ADV | suffix | Hayır |
| P21:isE:manner:ca | ca | deriv manner ca / DERIV_MANNER_CA | ADJ → ADV | suffix | Evet |
| P21:isE:manner:ce | ce | deriv manner ca / DERIV_MANNER_CA | ADJ → ADV | suffix | Evet |
| P21:isE:manner:ça | ça | deriv manner ca / DERIV_MANNER_CA | ADJ → ADV | suffix | Evet |
| P21:isE:manner:çe | çe | deriv manner ca / DERIV_MANNER_CA | ADJ → ADV | suffix | Evet |
| P21:isE:asif:ca | ca | Gibi davranma / CONV_CASINA | ADJ → ADJ | suffix | Evet |
| P21:isE:asif:ce | ce | Gibi davranma / CONV_CASINA | ADJ → ADJ | suffix | Evet |
| P21:isE:asif:ça | ça | Gibi davranma / CONV_CASINA | ADJ → ADJ | suffix | Evet |
| P21:isE:asif:çe | çe | Gibi davranma / CONV_CASINA | ADJ → ADJ | suffix | Evet |

## isK — 9.4. ise — isK

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| isK0000 | ∅ | isK / ABSENCE_isK |  →  | absence_marker | Hayır |
| isK0001 | ise | Karşıtlık/konu geçişi ise / CONTRAST_ISE | HOST → PARTICLE | clitic | Evet |
| isK0002 | ysa | Karşıtlık/konu geçişi ise / CONTRAST_ISE | HOST → PARTICLE | clitic | Evet |
| isK0003 | yse | Karşıtlık/konu geçişi ise / CONTRAST_ISE | HOST → PARTICLE | clitic | Evet |

## kcE — 8.6. Küçültme/sevecenlik — kcE

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| kcE0000 | ∅ | yok / ABSENCE_kcE |  →  | absence_marker | Hayır |
| kcE0001 | cık | Küçültme/sevecenlik / DIM_CIK | NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV → NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV | suffix | Evet |
| kcE0002 | cik | Küçültme/sevecenlik / DIM_CIK | NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV → NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV | suffix | Evet |
| kcE0003 | cuk | Küçültme/sevecenlik / DIM_CIK | NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV → NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV | suffix | Evet |
| kcE0004 | cük | Küçültme/sevecenlik / DIM_CIK | NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV → NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV | suffix | Evet |
| kcE0005 | çık | Küçültme/sevecenlik / DIM_CIK | NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV → NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV | suffix | Evet |
| kcE0006 | çik | Küçültme/sevecenlik / DIM_CIK | NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV → NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV | suffix | Evet |
| kcE0007 | çuk | Küçültme/sevecenlik / DIM_CIK | NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV → NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV | suffix | Evet |
| kcE0008 | çük | Küçültme/sevecenlik / DIM_CIK | NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV → NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV | suffix | Evet |
| kcE0009 | cağız | Sevecenlik/acınma / DIM_CAGIZ | NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV → NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV | suffix | Evet |
| kcE0010 | ceğiz | Sevecenlik/acınma / DIM_CAGIZ | NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV → NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV | suffix | Evet |
| kcE0011 | cak | Sözlüksel küçültme / DIM_CAK | NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV → NOUN | suffix | Evet |
| kcE0012 | cek | Sözlüksel küçültme / DIM_CAK | NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV → NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV | suffix | Hayır |
| kcE0013 | ıcık | Sınır ünlüsü + küçültme / DIM_ICIK_DISPLAY | NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV → NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV | composite_display | Hayır |
| kcE0014 | icik | Sınır ünlüsü + küçültme / DIM_ICIK_DISPLAY | NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV → NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV | composite_display | Hayır |
| kcE0015 | ucuk | Sınır ünlüsü + küçültme / DIM_ICIK_DISPLAY | NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV → NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV | composite_display | Hayır |
| kcE0016 | ücük | Sınır ünlüsü + küçültme / DIM_ICIK_DISPLAY | NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV → NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV | composite_display | Hayır |
| kcE0017 | cığ | Küçültme/sevecenlik; ünlülü devam / DIM_CIK | NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV → NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV | suffix | Evet |
| kcE0018 | ciğ | Küçültme/sevecenlik; ünlülü devam / DIM_CIK | NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV → NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV | suffix | Evet |
| kcE0019 | cuğ | Küçültme/sevecenlik; ünlülü devam / DIM_CIK | NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV → NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV | suffix | Evet |
| kcE0020 | cüğ | Küçültme/sevecenlik; ünlülü devam / DIM_CIK | NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV → NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV | suffix | Evet |
| kcE0021 | çığ | Küçültme/sevecenlik; ünlülü devam / DIM_CIK | NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV → NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV | suffix | Evet |
| kcE0022 | çiğ | Küçültme/sevecenlik; ünlülü devam / DIM_CIK | NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV → NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV | suffix | Evet |
| kcE0023 | çuğ | Küçültme/sevecenlik; ünlülü devam / DIM_CIK | NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV → NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV | suffix | Evet |
| kcE0024 | çüğ | Küçültme/sevecenlik; ünlülü devam / DIM_CIK | NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV → NOUN,PROPN,PRON,NOMINALIZED,ADJ,ADV | suffix | Evet |
| kcE0025 | cik | Bir → biricik: sözlüksel sayıdan sıfat küçültmesi / DIM_CIK | NUM → ADJ | suffix | Evet |
| kcE0026 | ciğ | Bir → biricik: sözlüksel sayıdan sıfat küçültmesi / DIM_CIK | NUM → ADJ | suffix | Evet |

## ksE — Z paradigması

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| ksE0000 | ∅ | Sıfır üçüncü tekil uyum / AGR_3_SING | PREDICATE → PREDICATE | zero_morpheme | Evet |
| ksE0001 | ım | Yüklem uyumu: 1. kişi Sing / AGR_1_SING | PREDICATE → PREDICATE | suffix | Evet |
| ksE0002 | im | Yüklem uyumu: 1. kişi Sing / AGR_1_SING | PREDICATE → PREDICATE | suffix | Evet |
| ksE0003 | um | Yüklem uyumu: 1. kişi Sing / AGR_1_SING | PREDICATE → PREDICATE | suffix | Evet |
| ksE0004 | üm | Yüklem uyumu: 1. kişi Sing / AGR_1_SING | PREDICATE → PREDICATE | suffix | Evet |
| ksE0005 | yım | Yüklem uyumu: 1. kişi Sing / AGR_1_SING | PREDICATE → PREDICATE | suffix | Evet |
| ksE0006 | yim | Yüklem uyumu: 1. kişi Sing / AGR_1_SING | PREDICATE → PREDICATE | suffix | Evet |
| ksE0007 | yum | Yüklem uyumu: 1. kişi Sing / AGR_1_SING | PREDICATE → PREDICATE | suffix | Evet |
| ksE0008 | yüm | Yüklem uyumu: 1. kişi Sing / AGR_1_SING | PREDICATE → PREDICATE | suffix | Evet |
| ksE0009 | sın | Yüklem uyumu: 2. kişi Sing / AGR_2_SING | PREDICATE → PREDICATE | suffix | Evet |
| ksE0010 | sin | Yüklem uyumu: 2. kişi Sing / AGR_2_SING | PREDICATE → PREDICATE | suffix | Evet |
| ksE0011 | sun | Yüklem uyumu: 2. kişi Sing / AGR_2_SING | PREDICATE → PREDICATE | suffix | Evet |
| ksE0012 | sün | Yüklem uyumu: 2. kişi Sing / AGR_2_SING | PREDICATE → PREDICATE | suffix | Evet |
| ksE0013 | ız | Yüklem uyumu: 1. kişi Plur / AGR_1_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0014 | iz | Yüklem uyumu: 1. kişi Plur / AGR_1_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0015 | uz | Yüklem uyumu: 1. kişi Plur / AGR_1_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0016 | üz | Yüklem uyumu: 1. kişi Plur / AGR_1_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0017 | yız | Yüklem uyumu: 1. kişi Plur / AGR_1_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0018 | yiz | Yüklem uyumu: 1. kişi Plur / AGR_1_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0019 | yuz | Yüklem uyumu: 1. kişi Plur / AGR_1_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0020 | yüz | Yüklem uyumu: 1. kişi Plur / AGR_1_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0021 | sınız | Yüklem uyumu: 2. kişi Plur / AGR_2_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0022 | siniz | Yüklem uyumu: 2. kişi Plur / AGR_2_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0023 | sunuz | Yüklem uyumu: 2. kişi Plur / AGR_2_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0024 | sünüz | Yüklem uyumu: 2. kişi Plur / AGR_2_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0025 | lar | Yüklem uyumu: 3. kişi Plur / AGR_3_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0026 | ler | Yüklem uyumu: 3. kişi Plur / AGR_3_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0027 | m | Yüklem uyumu: 1. kişi Sing / AGR_1_SING | PREDICATE → PREDICATE | suffix | Evet |
| ksE0028 | n | Yüklem uyumu: 2. kişi Sing / AGR_2_SING | PREDICATE → PREDICATE | suffix | Evet |
| ksE0029 | k | Yüklem uyumu: 1. kişi Plur / AGR_1_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0030 | nız | Yüklem uyumu: 2. kişi Plur / AGR_2_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0031 | niz | Yüklem uyumu: 2. kişi Plur / AGR_2_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0032 | nuz | Yüklem uyumu: 2. kişi Plur / AGR_2_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0033 | nüz | Yüklem uyumu: 2. kişi Plur / AGR_2_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0034 | lar | Yüklem uyumu: 3. kişi Plur / AGR_3_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0035 | ler | Yüklem uyumu: 3. kişi Plur / AGR_3_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0036 | ∅ | Sıfır ikinci tekil emir uyumu / AGR_2_SING | PREDICATE → PREDICATE | zero_morpheme | Evet |
| ksE0037 | sın | Yüklem uyumu: 3. kişi Sing / AGR_3_SING | PREDICATE → PREDICATE | suffix | Evet |
| ksE0038 | sin | Yüklem uyumu: 3. kişi Sing / AGR_3_SING | PREDICATE → PREDICATE | suffix | Evet |
| ksE0039 | sun | Yüklem uyumu: 3. kişi Sing / AGR_3_SING | PREDICATE → PREDICATE | suffix | Evet |
| ksE0040 | sün | Yüklem uyumu: 3. kişi Sing / AGR_3_SING | PREDICATE → PREDICATE | suffix | Evet |
| ksE0041 | ın | Yüklem uyumu: 2. kişi Plur / AGR_2_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0042 | in | Yüklem uyumu: 2. kişi Plur / AGR_2_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0043 | un | Yüklem uyumu: 2. kişi Plur / AGR_2_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0044 | ün | Yüklem uyumu: 2. kişi Plur / AGR_2_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0045 | yın | Yüklem uyumu: 2. kişi Plur / AGR_2_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0046 | yin | Yüklem uyumu: 2. kişi Plur / AGR_2_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0047 | yun | Yüklem uyumu: 2. kişi Plur / AGR_2_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0048 | yün | Yüklem uyumu: 2. kişi Plur / AGR_2_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0049 | ınız | Yüklem uyumu: 2. kişi Plur / AGR_2_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0050 | iniz | Yüklem uyumu: 2. kişi Plur / AGR_2_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0051 | unuz | Yüklem uyumu: 2. kişi Plur / AGR_2_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0052 | ünüz | Yüklem uyumu: 2. kişi Plur / AGR_2_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0053 | yınız | Yüklem uyumu: 2. kişi Plur / AGR_2_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0054 | yiniz | Yüklem uyumu: 2. kişi Plur / AGR_2_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0055 | yunuz | Yüklem uyumu: 2. kişi Plur / AGR_2_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0056 | yünüz | Yüklem uyumu: 2. kişi Plur / AGR_2_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0057 | sınlar | Yüklem uyumu: 3. kişi Plur / AGR_3_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0058 | sinler | Yüklem uyumu: 3. kişi Plur / AGR_3_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0059 | sunlar | Yüklem uyumu: 3. kişi Plur / AGR_3_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0060 | sünler | Yüklem uyumu: 3. kişi Plur / AGR_3_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0061 | ayım | Yüklem uyumu: 1. kişi Sing / TAM_OPT, AGR_1_SING | PREDICATE → PREDICATE | composite_display | Hayır |
| ksE0062 | eyim | Yüklem uyumu: 1. kişi Sing / TAM_OPT, AGR_1_SING | PREDICATE → PREDICATE | composite_display | Hayır |
| ksE0063 | yayım | Yüklem uyumu: 1. kişi Sing / TAM_OPT, AGR_1_SING | PREDICATE → PREDICATE | composite_display | Hayır |
| ksE0064 | yeyim | Yüklem uyumu: 1. kişi Sing / TAM_OPT, AGR_1_SING | PREDICATE → PREDICATE | composite_display | Hayır |
| ksE0065 | alım | Yüklem uyumu: 1. kişi Plur / TAM_OPT, AGR_1_PLUR | PREDICATE → PREDICATE | composite_display | Hayır |
| ksE0066 | elim | Yüklem uyumu: 1. kişi Plur / TAM_OPT, AGR_1_PLUR | PREDICATE → PREDICATE | composite_display | Hayır |
| ksE0067 | yalım | Yüklem uyumu: 1. kişi Plur / TAM_OPT, AGR_1_PLUR | PREDICATE → PREDICATE | composite_display | Hayır |
| ksE0068 | yelim | Yüklem uyumu: 1. kişi Plur / TAM_OPT, AGR_1_PLUR | PREDICATE → PREDICATE | composite_display | Hayır |
| ksE0069 | m | Yüklem uyumu: 1. kişi Sing / AGR_1_SING | PREDICATE → PREDICATE | suffix | Evet |
| ksE0070 | lım | İstek sonrası birinci çoğul uyum / AGR_1_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0071 | lim | İstek sonrası birinci çoğul uyum / AGR_1_PLUR | PREDICATE → PREDICATE | suffix | Evet |
| ksE0072 | sana | Pekiştirilmiş/ricalı emir; 2Sing / AGR_2_SING | VERB → PREDICATE | suffix | Evet |
| ksE0073 | sene | Pekiştirilmiş/ricalı emir; 2Sing / AGR_2_SING | VERB → PREDICATE | suffix | Evet |
| ksE0074 | sanıza | Pekiştirilmiş/ricalı emir; 2Plur / AGR_2_PLUR | VERB → PREDICATE | suffix | Evet |
| ksE0075 | senize | Pekiştirilmiş/ricalı emir; 2Plur / AGR_2_PLUR | VERB → PREDICATE | suffix | Evet |

## kvR — 10. Pekiştirme sonek değildir — kvR

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| kvR0000 | ∅ | pekiştirme yok / ABSENCE_kvR |  →  | absence_marker | Hayır |
| kvR0001 | — | Baş parça tekrarı, ara ünsüz m / PROCESS_kvR0001 |  →  | reduplicative_process | Hayır |
| kvR0002 | — | Baş parça tekrarı, ara ünsüz p / PROCESS_kvR0002 |  →  | reduplicative_process | Hayır |
| kvR0003 | — | Baş parça tekrarı, ara ünsüz r / PROCESS_kvR0003 |  →  | reduplicative_process | Hayır |
| kvR0004 | — | Baş parça tekrarı, ara ünsüz s / PROCESS_kvR0004 |  →  | reduplicative_process | Hayır |
| kvR0005 | — | sözlüksel düzensiz pekiştirme / PROCESS_kvR0005 | ADJ,ADV → ADV | reduplicative_process | Hayır |

## kyR — 11. Ses ve yazım kural kayıtları

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| kyR0001 | — | Yüzey allomorfundaki koşullu y / PROCESS_kyR0001 |  →  | rule | Hayır |
| kyR0002 | — | Üçüncü kişi iyelik/zamir sonrası n / PROCESS_kyR0002 |  →  | rule | Hayır |
| kyR0003 | — | Ünlü sonrası üçüncü tekil iyelik s / PROCESS_kyR0003 |  →  | rule | Hayır |
| kyR0004 | — | Üleştirme ş gerçekleşmesi / PROCESS_kyR0004 |  →  | rule | Hayır |

## odK — 9.2. Odak/ekleme da/de — odK

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| odK0000 | ∅ | odK / ABSENCE_odK |  →  | absence_marker | Hayır |
| odK0001 | da | Odak/ekleme parçacığı / PARTICLE_DA | HOST → PARTICLE | clitic | Evet |
| odK0002 | de | Odak/ekleme parçacığı / PARTICLE_DA | HOST → PARTICLE | clitic | Evet |

## olE — 5.2. Kutupluluk — olE

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| olE0000 | ∅ | Polarity=Pos / ABSENCE_olE |  →  | absence_marker | Hayır |
| olE0001 | ma | Olumsuzluk / POLARITY_NEG | VERB → VERB | suffix | Evet |
| olE0002 | me | Olumsuzluk / POLARITY_NEG | VERB → VERB | suffix | Evet |
| olE0003 | mı | Olumsuzluk / POLARITY_NEG | VERB → VERB | suffix | Evet |
| olE0004 | mi | Olumsuzluk / POLARITY_NEG | VERB → VERB | suffix | Evet |
| olE0005 | mu | Olumsuzluk / POLARITY_NEG | VERB → VERB | suffix | Evet |
| olE0006 | mü | Olumsuzluk / POLARITY_NEG | VERB → VERB | suffix | Evet |
| olE0007 | maz | Olumsuz geniş zaman bileşik gösterimi / NEG_AOR_DISPLAY | VERB → VERB | composite_display | Hayır |
| olE0008 | mez | Olumsuz geniş zaman bileşik gösterimi / NEG_AOR_DISPLAY | VERB → VERB | composite_display | Hayır |

## sdE — 4.6. Sayı türetimleri — sdE

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| sdE0000 | ∅ | temel sayı / ABSENCE_sdE |  →  | absence_marker | Hayır |
| sdE0001 | ıncı | Sıra sayısı / NUM_ORD | NUM → NUM | suffix | Evet |
| sdE0002 | inci | Sıra sayısı / NUM_ORD | NUM → NUM | suffix | Evet |
| sdE0003 | uncu | Sıra sayısı / NUM_ORD | NUM → NUM | suffix | Evet |
| sdE0004 | üncü | Sıra sayısı / NUM_ORD | NUM → NUM | suffix | Evet |
| sdE0005 | ncı | Sıra sayısı / NUM_ORD | NUM → NUM | suffix | Evet |
| sdE0006 | nci | Sıra sayısı / NUM_ORD | NUM → NUM | suffix | Evet |
| sdE0007 | ncu | Sıra sayısı / NUM_ORD | NUM → NUM | suffix | Evet |
| sdE0008 | ncü | Sıra sayısı / NUM_ORD | NUM → NUM | suffix | Evet |
| sdE0009 | ar | Üleştirme / NUM_DIST | NUM → NUM | suffix | Evet |
| sdE0010 | er | Üleştirme / NUM_DIST | NUM → NUM | suffix | Evet |
| sdE0011 | şar | Üleştirme / NUM_DIST | NUM → NUM | suffix | Evet |
| sdE0012 | şer | Üleştirme / NUM_DIST | NUM → NUM | suffix | Evet |
| sdE0013 | ız | Sözlüksel sayı topluluğu / NUM_COLLECTIVE | NUM → NOUN,ADJ | suffix | Hayır |
| sdE0014 | iz | Sözlüksel sayı topluluğu / NUM_COLLECTIVE | NUM → ADJ,NOUN | suffix | Evet |
| sdE0015 | uz | Sözlüksel sayı topluluğu / NUM_COLLECTIVE | NUM → ADJ,NOUN | suffix | Evet |
| sdE0016 | üz | Sözlüksel sayı topluluğu / NUM_COLLECTIVE | NUM → ADJ,NOUN | suffix | Evet |
| sdE0017 | z | Sözlüksel sayı topluluğu / NUM_COLLECTIVE | NUM → NOUN,ADJ | suffix | Evet |

## sfE — 8.5. Sıfattan fiil — sfE

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| sfE0000 | ∅ | türetim yok / ABSENCE_sfE |  →  | absence_marker | Hayır |
| sfE0001 | la | Niteliği uygulama / A_MAKE | ADJ → VERB | suffix | Evet |
| sfE0002 | le | Niteliği uygulama / A_MAKE | ADJ → VERB | suffix | Evet |
| sfE0003 | lan | Niteliği edinme / A_ACQUIRE | ADJ → VERB | suffix | Evet |
| sfE0004 | len | Niteliği edinme / A_ACQUIRE | ADJ → VERB | suffix | Evet |
| sfE0005 | laş | Niteliğe dönüşme / A_BECOME | ADJ → VERB | suffix | Evet |
| sfE0006 | leş | Niteliğe dönüşme / A_BECOME | ADJ → VERB | suffix | Evet |
| sfE0007 | ar | Renk/durum değişimi / A_V_AR | ADJ → VERB | suffix | Evet |
| sfE0008 | er | Renk/durum değişimi / A_V_AR | ADJ → VERB | suffix | Hayır |
| sfE0009 | al | Durum değişimi / A_V_AL | ADJ → VERB | suffix | Evet |
| sfE0010 | el | Durum değişimi / A_V_AL | ADJ → VERB | suffix | Evet |

## siE — 8.4. Sıfattan isim — siE

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| siE0000 | ∅ | türetim yok / ABSENCE_siE |  →  | absence_marker | Hayır |
| siE0001 | lık | Özellik/soyutluk / A_NESS | ADJ → NOUN | suffix | Evet |
| siE0002 | lik | Özellik/soyutluk / A_NESS | ADJ → NOUN | suffix | Evet |
| siE0003 | luk | Özellik/soyutluk / A_NESS | ADJ → NOUN | suffix | Evet |
| siE0004 | lük | Özellik/soyutluk / A_NESS | ADJ → NOUN | suffix | Evet |
| siE0005 | cı | Kişi/yanlı / A_AGENT | ADJ → NOUN | suffix | Hayır |
| siE0006 | ci | Kişi/yanlı / A_AGENT | ADJ → NOUN | suffix | Hayır |
| siE0007 | cu | Kişi/yanlı / A_AGENT | ADJ → NOUN | suffix | Hayır |
| siE0008 | cü | Kişi/yanlı / A_AGENT | ADJ → NOUN | suffix | Hayır |
| siE0009 | çı | Kişi/yanlı / A_AGENT | ADJ → NOUN | suffix | Evet |
| siE0010 | çi | Kişi/yanlı / A_AGENT | ADJ → NOUN | suffix | Hayır |
| siE0011 | çu | Kişi/yanlı / A_AGENT | ADJ → NOUN | suffix | Hayır |
| siE0012 | çü | Kişi/yanlı / A_AGENT | ADJ → NOUN | suffix | Hayır |
| siE0013 | lığ | Özellik/soyutluk; ünlülü devam / A_NESS | ADJ → NOUN | suffix | Evet |
| siE0014 | liğ | Özellik/soyutluk; ünlülü devam / A_NESS | ADJ → NOUN | suffix | Evet |
| siE0015 | luğ | Özellik/soyutluk; ünlülü devam / A_NESS | ADJ → NOUN | suffix | Evet |
| siE0016 | lüğ | Özellik/soyutluk; ünlülü devam / A_NESS | ADJ → NOUN | suffix | Evet |

## soK — 9.1. Soru — soK

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| soK0000 | ∅ | soK / ABSENCE_soK |  →  | absence_marker | Hayır |
| soK0001 | mı | mI parçacığı / PARTICLE_MI | HOST → PARTICLE | clitic | Evet |
| soK0002 | mi | mI parçacığı / PARTICLE_MI | HOST → PARTICLE | clitic | Evet |
| soK0003 | mu | mI parçacığı / PARTICLE_MI | HOST → PARTICLE | clitic | Evet |
| soK0004 | mü | mI parçacığı / PARTICLE_MI | HOST → PARTICLE | clitic | Evet |

## spR — 11. Ses ve yazım kural kayıtları

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| spR0001 | — | Özgün boşluk/sınırları koruma / PROCESS_spR0001 |  →  | rule | Hayır |

## suR — 11. Ses ve yazım kural kayıtları

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| suR0001 | — | su iyelik/genitif paradigması / PROCESS_suR0001 |  →  | rule | Hayır |

## syE — 8.8. Aile/topluluk ve saygı bağlantısı — syE

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| syE0000 | ∅ | yok / ABSENCE_syE |  →  | absence_marker | Hayır |
| syE0001 | gil | Aile/çevre/topluluk / FAMILY_GIL | NOUN,PROPN,PRON,NOMINALIZED → NOUN | suffix | Evet |

## udR — 11. Ses ve yazım kural kayıtları

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| udR0001 | — | Sözlüksel iç ünlü düşmesi / PROCESS_udR0001 |  →  | rule | Hayır |
| udR0002 | — | Şimdiki zaman öncesi gövde değişimi / PROCESS_udR0002 |  →  | rule | Hayır |
| udR0003 | — | Olumsuzluk daralması / PROCESS_udR0003 |  →  | rule | Hayır |

## unR — 11. Ses ve yazım kural kayıtları

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| unR0001 | — | Son sesin ötümlülüğüne göre d/t / PROCESS_unR0001 |  →  | rule | Hayır |
| unR0002 | — | Son sesin ötümlülüğüne göre c/ç / PROCESS_unR0002 |  →  | rule | Hayır |
| unR0003 | — | Lisanslı ekte ünlülü devam öncesi k/ğ / PROCESS_unR0003 |  →  | rule | Hayır |
| unR0004 | — | Sözlüksel kök/gövde ötümlüleşmesi / PROCESS_unR0004 |  →  | rule | Hayır |

## uoR — 11. Ses ve yazım kural kayıtları

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| uoR0001 | — | Sözlüksel ses uyumu profili / PROCESS_uoR0001 |  →  | rule | Hayır |

## uyR — 11. Ses ve yazım kural kayıtları

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| uyR0001 | — | Son fonolojik ünlüye göre a/e / PROCESS_uyR0001 |  →  | rule | Hayır |
| uyR0002 | — | Son fonolojik ünlüye göre ı/i/u/ü / PROCESS_uyR0002 |  →  | rule | Hayır |

## uzR — 11. Ses ve yazım kural kayıtları

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| uzR0001 | — | Sözlüksel ünsüz ikizleşmesi / PROCESS_uzR0001 |  →  | rule | Hayır |

## vtE — 4.4. Vasıta/birliktelik ve eşitlik — vtE

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| vtE0000 | ∅ | Case=None / ABSENCE_vtE |  →  | absence_marker | Hayır |
| vtE0001 | la | Vasıta/birliktelik / CASE_INS | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| vtE0002 | le | Vasıta/birliktelik / CASE_INS | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| vtE0003 | yla | Vasıta/birliktelik / CASE_INS | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| vtE0004 | yle | Vasıta/birliktelik / CASE_INS | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| vtE0005 | ca | Eşitlik/görelik / CASE_EQU | NOUN,PROPN,PRON,NOMINALIZED → NOMINALIZED,ADV | suffix | Evet |
| vtE0006 | ce | Eşitlik/görelik / CASE_EQU | NOUN,PROPN,PRON,NOMINALIZED → NOMINALIZED,ADV | suffix | Evet |
| vtE0007 | ça | Eşitlik/görelik / CASE_EQU | NOUN,PROPN,PRON,NOMINALIZED → NOMINALIZED,ADV | suffix | Evet |
| vtE0008 | çe | Eşitlik/görelik / CASE_EQU | NOUN,PROPN,PRON,NOMINALIZED → NOMINALIZED,ADV | suffix | Evet |
| vtE0009 | nca | Eşitlik/görelik / CASE_EQU | NOUN,PROPN,PRON,NOMINALIZED → NOMINALIZED,ADV | suffix | Evet |
| vtE0010 | nce | Eşitlik/görelik / CASE_EQU | NOUN,PROPN,PRON,NOMINALIZED → NOMINALIZED,ADV | suffix | Evet |
| P9:vtE:pron:nunla | nunla | Vasıta/birliktelik / CASE_INS | PRON → PRON | suffix | Evet |
| P9:vtE:pron:nla | nla | Vasıta/birliktelik / CASE_INS | PRON → PRON | suffix | Evet |
| P9:vtE:pron:inle | inle | Vasıta/birliktelik / CASE_INS | PRON → PRON | suffix | Evet |
| P9:vtE:pron:imle | imle | Vasıta/birliktelik / CASE_INS | PRON → PRON | suffix | Evet |

## ybE — 5.3. Yeterlik/olasılık — ybE

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| ybE0000 | ∅ | yeterlik yok / ABSENCE_ybE |  →  | absence_marker | Hayır |
| ybE0001 | abil | Yeterlik / ABILITY | VERB → VERB | suffix | Evet |
| ybE0002 | ebil | Yeterlik / ABILITY | VERB → VERB | suffix | Evet |
| ybE0003 | yabil | Yeterlik / ABILITY | VERB → VERB | suffix | Evet |
| ybE0004 | yebil | Yeterlik / ABILITY | VERB → VERB | suffix | Evet |
| ybE0005 | a | Olumsuz yeterlik gövdesi / ABILITY_NEG_BASE | VERB → VERB | suffix | Evet |
| ybE0006 | e | Olumsuz yeterlik gövdesi / ABILITY_NEG_BASE | VERB → VERB | suffix | Evet |
| ybE0007 | ya | Olumsuz yeterlik gövdesi / ABILITY_NEG_BASE | VERB → VERB | suffix | Evet |
| ybE0008 | ye | Olumsuz yeterlik gövdesi / ABILITY_NEG_BASE | VERB → VERB | suffix | Evet |

## ylE — 4.2. İyelik — ylE

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| ylE0000 | ∅ | Poss=None / ABSENCE_ylE |  →  | absence_marker | Hayır |
| ylE0001 | ım | İyelik: 1. kişi Sing / POSS_1_SING | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0002 | im | İyelik: 1. kişi Sing / POSS_1_SING | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0003 | um | İyelik: 1. kişi Sing / POSS_1_SING | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0004 | üm | İyelik: 1. kişi Sing / POSS_1_SING | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0005 | m | İyelik: 1. kişi Sing / POSS_1_SING | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0006 | ın | İyelik: 2. kişi Sing / POSS_2_SING | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0007 | in | İyelik: 2. kişi Sing / POSS_2_SING | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0008 | un | İyelik: 2. kişi Sing / POSS_2_SING | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0009 | ün | İyelik: 2. kişi Sing / POSS_2_SING | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0010 | n | İyelik: 2. kişi Sing / POSS_2_SING | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0011 | ı | İyelik: 3. kişi Sing / POSS_3_SING | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0012 | i | İyelik: 3. kişi Sing / POSS_3_SING | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0013 | u | İyelik: 3. kişi Sing / POSS_3_SING | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0014 | ü | İyelik: 3. kişi Sing / POSS_3_SING | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0015 | sı | İyelik: 3. kişi Sing / POSS_3_SING | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0016 | si | İyelik: 3. kişi Sing / POSS_3_SING | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0017 | su | İyelik: 3. kişi Sing / POSS_3_SING | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0018 | sü | İyelik: 3. kişi Sing / POSS_3_SING | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0019 | ımız | İyelik: 1. kişi Plur / POSS_1_PLUR | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0020 | imiz | İyelik: 1. kişi Plur / POSS_1_PLUR | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0021 | umuz | İyelik: 1. kişi Plur / POSS_1_PLUR | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0022 | ümüz | İyelik: 1. kişi Plur / POSS_1_PLUR | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0023 | mız | İyelik: 1. kişi Plur / POSS_1_PLUR | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0024 | miz | İyelik: 1. kişi Plur / POSS_1_PLUR | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0025 | muz | İyelik: 1. kişi Plur / POSS_1_PLUR | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0026 | müz | İyelik: 1. kişi Plur / POSS_1_PLUR | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0027 | ınız | İyelik: 2. kişi Plur / POSS_2_PLUR | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0028 | iniz | İyelik: 2. kişi Plur / POSS_2_PLUR | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0029 | unuz | İyelik: 2. kişi Plur / POSS_2_PLUR | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0030 | ünüz | İyelik: 2. kişi Plur / POSS_2_PLUR | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0031 | nız | İyelik: 2. kişi Plur / POSS_2_PLUR | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0032 | niz | İyelik: 2. kişi Plur / POSS_2_PLUR | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0033 | nuz | İyelik: 2. kişi Plur / POSS_2_PLUR | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0034 | nüz | İyelik: 2. kişi Plur / POSS_2_PLUR | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0035 | ları | İyelik: 3. kişi Plur / POSS_3_PLUR | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0036 | leri | İyelik: 3. kişi Plur / POSS_3_PLUR | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0037 | yum | İyelik: 1. kişi Sing / POSS_1_SING | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0038 | yun | İyelik: 2. kişi Sing / POSS_2_SING | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0039 | yu | İyelik: 3. kişi Sing / POSS_3_SING | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0040 | yumuz | İyelik: 1. kişi Plur / POSS_1_PLUR | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0041 | yunuz | İyelik: 2. kişi Plur / POSS_2_PLUR | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0042 | yim | Ne zamirinin 1. kişi Sing iyeliği / POSS_1_SING | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0043 | yin | Ne zamirinin 2. kişi Sing iyeliği / POSS_2_SING | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0044 | yimiz | Ne zamirinin 1. kişi Plur iyeliği / POSS_1_PLUR | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0045 | yiniz | Ne zamirinin 2. kişi Plur iyeliği / POSS_2_PLUR | PRON → PRON | suffix | Evet |
| ylE0046 | ı | Açık çoğul sonrası üçüncü çoğul iyelik / POSS_3_PLUR | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0047 | i | Açık çoğul sonrası üçüncü çoğul iyelik / POSS_3_PLUR | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0048 | u | Açık çoğul sonrası üçüncü çoğul iyelik / POSS_3_PLUR | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| ylE0049 | ü | Açık çoğul sonrası üçüncü çoğul iyelik / POSS_3_PLUR | NOUN,PROPN,PRON,NOMINALIZED → NOUN,PROPN,PRON,NOMINALIZED | suffix | Evet |
| P9:ylE:zero3sg | ∅ | İyelik: 3. kişi Sing / POSS_3_SING | PRON → PRON | zero_morpheme | Evet |
| P9:ylE:zero3pl | ∅ | İyelik: 3. kişi Plur / POSS_3_PLUR | PRON → PRON | zero_morpheme | Evet |

## ypE — 8.12. Ödünç bağlı biçimler ve sonekimsiler — ypE9xxx

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| ypE9001 | hane | Farsça; yer/kurum / BORROWED_9001 | LEXICAL_BASE → NOUN,ADJ | suffixoid | Evet |
| ypE9002 | name | Farsça; kitap/belge / BORROWED_9002 | LEXICAL_BASE → NOUN,ADJ | suffixoid | Evet |
| ypE9003 | baz | Farsça; uğraşan/oynayan / BORROWED_9003 | LEXICAL_BASE → NOUN,ADJ | suffixoid | Evet |
| ypE9004 | dar | Farsça; sahip/taşıyan / BORROWED_9004 | LEXICAL_BASE → NOUN,ADJ | suffixoid | Evet |
| ypE9005 | kâr | Farsça; yapan/meslek / BORROWED_9005 | LEXICAL_BASE → NOUN,ADJ | suffixoid | Evet |
| ypE9006 | gâh | Farsça; yer / BORROWED_9006 | LEXICAL_BASE → NOUN,ADJ | suffixoid | Evet |
| ypE9007 | perest | Farsça; aşırı bağlı / BORROWED_9007 | LEXICAL_BASE → NOUN,ADJ | suffixoid | Evet |
| ypE9008 | zade | Farsça; soy/çocuk / BORROWED_9008 | LEXICAL_BASE → NOUN,ADJ | suffixoid | Evet |
| ypE9009 | istan | Farsça; ülke/yer / BORROWED_9009 | LEXICAL_BASE → NOUN,ADJ | suffixoid | Evet |
| ypE9010 | vari | Farsça kökenli; benzer tarz / BORROWED_9010 | LEXICAL_BASE → NOUN,ADJ | suffixoid | Evet |
| ypE9011 | — | Arapça nispet biçimi / BORROWED_9011 | LEXICAL_BASE → NOUN,ADJ | deprecated | Hayır |
| ypE9012 | at | Arapça çoğul/soyut biçim / BORROWED_9012 | LEXICAL_BASE → NOUN,ADJ | suffixoid | Evet |
| ypE9013 | izm | Batı dilleri; akım/doktrin / BORROWED_9013 | LEXICAL_BASE → NOUN,ADJ | suffixoid | Evet |
| ypE9014 | ist | Batı dilleri; kişi/uzman/yanlı / BORROWED_9014 | LEXICAL_BASE → NOUN,ADJ | suffixoid | Evet |
| ypE9015 | ik | Batı dilleri; sıfat/ad / BORROWED_9015 | LEXICAL_BASE → NOUN,ADJ | suffixoid | Evet |
| ypE9016 | al | Batı dilleri; ilişki sıfatı / BORROWED_9016 | LEXICAL_BASE → NOUN,ADJ | suffixoid | Evet |
| ypE9017 | oloji | Grekçe kökenli bilim alanı biçimi / BORROWED_9017 | LEXICAL_BASE → NOUN,ADJ | suffixoid | Evet |
| ypE9018 | log | Grekçe kökenli uzman biçimi / BORROWED_9018 | LEXICAL_BASE → NOUN,ADJ | suffixoid | Evet |
| ypE9019 | graf | Grekçe kökenli yazan/aygıt biçimi / BORROWED_9019 | LEXICAL_BASE → NOUN,ADJ | suffixoid | Evet |
| ypE9020 | matik | Batı dilleri; otomatik/aygıt / BORROWED_9020 | LEXICAL_BASE → NOUN,ADJ | suffixoid | Evet |
| ypE9021 | î | Sözlüksel nispet biçimi / BORROWED_9011 | LEXICAL_BASE → ADJ | suffixoid | Evet |
| ypE9022 | i | Sözlüksel nispet biçimi / BORROWED_9011 | LEXICAL_BASE → ADJ | composite_display | Hayır |

## zaR — 11. Ses ve yazım kural kayıtları

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| zaR0001 | — | ben/sen yönelme gövdeleri / PROCESS_zaR0001 |  →  | rule | Hayır |
| zaR0002 | — | o/bu/şu zamir gövdeleri / PROCESS_zaR0002 |  →  | rule | Hayır |

## zmE — 5.4. Zaman–görünüş–kip — zmE

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| zmE0000 | ∅ | Sıfır emir kipi / TAM_IMP | PREDICATE → PREDICATE | zero_morpheme | Evet |
| zmE0001 | dı | Görülen geçmiş / TAM_PAST | VERB → VERB | suffix | Evet |
| zmE0002 | di | Görülen geçmiş / TAM_PAST | VERB → VERB | suffix | Evet |
| zmE0003 | du | Görülen geçmiş / TAM_PAST | VERB → VERB | suffix | Evet |
| zmE0004 | dü | Görülen geçmiş / TAM_PAST | VERB → VERB | suffix | Evet |
| zmE0005 | tı | Görülen geçmiş / TAM_PAST | VERB → VERB | suffix | Evet |
| zmE0006 | ti | Görülen geçmiş / TAM_PAST | VERB → VERB | suffix | Evet |
| zmE0007 | tu | Görülen geçmiş / TAM_PAST | VERB → VERB | suffix | Evet |
| zmE0008 | tü | Görülen geçmiş / TAM_PAST | VERB → VERB | suffix | Evet |
| zmE0009 | mış | Dolaylı kanıtsallık/geçmiş / TAM_EVID | VERB → VERB | suffix | Evet |
| zmE0010 | miş | Dolaylı kanıtsallık/geçmiş / TAM_EVID | VERB → VERB | suffix | Evet |
| zmE0011 | muş | Dolaylı kanıtsallık/geçmiş / TAM_EVID | VERB → VERB | suffix | Evet |
| zmE0012 | müş | Dolaylı kanıtsallık/geçmiş / TAM_EVID | VERB → VERB | suffix | Evet |
| zmE0013 | ıyor | Şimdiki zaman / TAM_PROG1 | VERB → VERB | suffix | Evet |
| zmE0014 | iyor | Şimdiki zaman / TAM_PROG1 | VERB → VERB | suffix | Evet |
| zmE0015 | uyor | Şimdiki zaman / TAM_PROG1 | VERB → VERB | suffix | Evet |
| zmE0016 | üyor | Şimdiki zaman / TAM_PROG1 | VERB → VERB | suffix | Evet |
| zmE0017 | yor | Şimdiki zaman / TAM_PROG1 | VERB → VERB | suffix | Evet |
| zmE0018 | makta | Sürmekte oluş / TAM_PROG2 | VERB → VERB | suffix | Evet |
| zmE0019 | mekte | Sürmekte oluş / TAM_PROG2 | VERB → VERB | suffix | Evet |
| zmE0020 | acak | Gelecek / TAM_FUT | VERB → VERB | suffix | Evet |
| zmE0021 | ecek | Gelecek / TAM_FUT | VERB → VERB | suffix | Evet |
| zmE0022 | yacak | Gelecek / TAM_FUT | VERB → VERB | suffix | Evet |
| zmE0023 | yecek | Gelecek / TAM_FUT | VERB → VERB | suffix | Evet |
| zmE0024 | acağ | Gelecek / TAM_FUT | VERB → VERB | suffix | Evet |
| zmE0025 | eceğ | Gelecek / TAM_FUT | VERB → VERB | suffix | Evet |
| zmE0026 | yacağ | Gelecek / TAM_FUT | VERB → VERB | suffix | Evet |
| zmE0027 | yeceğ | Gelecek / TAM_FUT | VERB → VERB | suffix | Evet |
| zmE0028 | ar | Geniş zaman / TAM_AOR | VERB → VERB | suffix | Evet |
| zmE0029 | er | Geniş zaman / TAM_AOR | VERB → VERB | suffix | Evet |
| zmE0030 | ır | Geniş zaman / TAM_AOR | VERB → VERB | suffix | Evet |
| zmE0031 | ir | Geniş zaman / TAM_AOR | VERB → VERB | suffix | Evet |
| zmE0032 | ur | Geniş zaman / TAM_AOR | VERB → VERB | suffix | Evet |
| zmE0033 | ür | Geniş zaman / TAM_AOR | VERB → VERB | suffix | Evet |
| zmE0034 | r | Geniş zaman / TAM_AOR | VERB → VERB | suffix | Evet |
| zmE0035 | malı | Gereklilik / TAM_NEC | VERB → VERB | suffix | Evet |
| zmE0036 | meli | Gereklilik / TAM_NEC | VERB → VERB | suffix | Evet |
| zmE0037 | sa | Şart/dilek / TAM_COND | VERB → VERB | suffix | Evet |
| zmE0038 | se | Şart/dilek / TAM_COND | VERB → VERB | suffix | Evet |
| zmE0039 | a | İstek / TAM_OPT | VERB → VERB | suffix | Evet |
| zmE0040 | e | İstek / TAM_OPT | VERB → VERB | suffix | Evet |
| zmE0041 | ya | İstek / TAM_OPT | VERB → VERB | suffix | Evet |
| zmE0042 | ye | İstek / TAM_OPT | VERB → VERB | suffix | Evet |
| zmE0043 | z | Olumsuz geniş zaman z gerçekleşmesi / TAM_AOR | VERB → VERB | suffix | Evet |
| zmE0044 | ∅ | Olumsuz geniş zaman sıfır gerçekleşmesi / TAM_AOR | VERB → VERB | zero_morpheme | Evet |

## zyE — 8.7. Benzerlik/zayıflatma — zyE

| Kayıt ID | Yüzey | Açıklama / morfem | Girdi → çıktı | Tür | Açık |
|---|---|---|---|---|---|
| zyE0000 | ∅ | yok / ABSENCE_zyE |  →  | absence_marker | Hayır |
| zyE0001 | ımsı | Benzerlik/zayıflatma / SIMILAR | NOUN,PROPN,PRON,NOMINALIZED,ADJ → ADJ | suffix | Evet |
| zyE0002 | imsi | Benzerlik/zayıflatma / SIMILAR | NOUN,PROPN,PRON,NOMINALIZED,ADJ → ADJ | suffix | Evet |
| zyE0003 | umsu | Benzerlik/zayıflatma / SIMILAR | NOUN,PROPN,PRON,NOMINALIZED,ADJ → ADJ | suffix | Evet |
| zyE0004 | ümsü | Benzerlik/zayıflatma / SIMILAR | NOUN,PROPN,PRON,NOMINALIZED,ADJ → ADJ | suffix | Evet |
| zyE0005 | sı | Benzerlik/zayıflatma / SIMILAR | NOUN,PROPN,PRON,NOMINALIZED,ADJ → ADJ | suffix | Evet |
| zyE0006 | si | Benzerlik/zayıflatma / SIMILAR | NOUN,PROPN,PRON,NOMINALIZED,ADJ → ADJ | suffix | Evet |
| zyE0007 | su | Benzerlik/zayıflatma / SIMILAR | NOUN,PROPN,PRON,NOMINALIZED,ADJ → ADJ | suffix | Evet |
| zyE0008 | sü | Benzerlik/zayıflatma / SIMILAR | NOUN,PROPN,PRON,NOMINALIZED,ADJ → ADJ | suffix | Evet |
| zyE0009 | ımtırak | Yaklaşık renk/nitelik / APPROX_MTIRAK | NOUN,PROPN,PRON,NOMINALIZED,ADJ → ADJ | suffix | Evet |
| zyE0010 | imtırak | Yaklaşık renk/nitelik / APPROX_MTIRAK | NOUN,PROPN,PRON,NOMINALIZED,ADJ → ADJ | suffix | Evet |
| zyE0011 | umtırak | Yaklaşık renk/nitelik / APPROX_MTIRAK | NOUN,PROPN,PRON,NOMINALIZED,ADJ → ADJ | suffix | Evet |
| zyE0012 | ümtırak | Yaklaşık renk/nitelik / APPROX_MTIRAK | NOUN,PROPN,PRON,NOMINALIZED,ADJ → ADJ | suffix | Hayır |
| zyE0013 | msı | Ünlü sonrası benzerlik/zayıflatma / SIMILAR | NOUN,PROPN,PRON,NOMINALIZED,ADJ → ADJ | suffix | Evet |
| zyE0014 | msi | Ünlü sonrası benzerlik/zayıflatma / SIMILAR | NOUN,PROPN,PRON,NOMINALIZED,ADJ → ADJ | suffix | Evet |
| zyE0015 | msu | Ünlü sonrası benzerlik/zayıflatma / SIMILAR | NOUN,PROPN,PRON,NOMINALIZED,ADJ → ADJ | suffix | Evet |
| zyE0016 | msü | Ünlü sonrası benzerlik/zayıflatma / SIMILAR | NOUN,PROPN,PRON,NOMINALIZED,ADJ → ADJ | suffix | Evet |
| zyE0017 | mtırak | Yaklaşık renk/nitelik, ünlü sonrası / APPROX_MTIRAK | ADJ → ADJ | suffix | Evet |
| zyE0018 | sıl | Sınırlı benzerlik / SIM_SIL | NOUN → ADJ | suffix | Evet |
| zyE0019 | sil | Sınırlı benzerlik / SIM_SIL | NOUN,PROPN,PRON,NOMINALIZED,ADJ → ADJ | suffix | Hayır |
| zyE0020 | sul | Sınırlı benzerlik / SIM_SIL | NOUN → ADJ | suffix | Evet |
| zyE0021 | sül | Sınırlı benzerlik / SIM_SIL | NOUN,PROPN,PRON,NOMINALIZED,ADJ → ADJ | suffix | Hayır |

## Kaynak kimliği

- Native tablo SHA-256: `716c00c0a8cf0033491dfca9379fba81c9789ddc6e1ffc071bba3ca93c09be5b`.
- S05 JSON SHA-256: `724511e7132c9c59da87ae50639df0a887c48dc2c75aad97443d0041d81e2cca`.
- Zemberek atıfları özgün JSON kayıtlarının evidence/source_refs alanlarında korunur. Lisans bildirimleri THIRD_PARTY_NOTICES.md altındadır. `licenses-v0.3.0.json` adındaki tarihsel dosya, telif lisansından farklı olarak sözcüksel kullanım izinleri içerir.
