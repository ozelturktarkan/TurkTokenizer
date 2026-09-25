# Lisans kapsamı ve üçüncü taraf kaynaklar

## Özgün kod

TürkTokenizer algoritma kaynakları, yeni CLI/Python sarmalayıcı ve proje belgelerine ait Tarkan Özel tarafından lisanslanabilen özgün katkılar Apache-2.0 kapsamında sunulur. Kopyalanan üçüncü taraf bildirimleri bu lisansla değiştirilmez. Kaynaklar yeni düzen içine kopyalandı; donmuş motor kaynakları değişmedi. CLI'ye decode erişimi ve Python IPC katmanı eklendi.

## Araştırma varlıkları

| Kapsam / kaynak | Korunan bildirim |
|---|---|
| Zemberek kaynaklı sözlüksel/morfotaktik malzeme, registry atıfları | Apache-2.0; Ahmet A. Akın / Mehmet D. Akın, sabit commit bilgisi kaynak bildiriminde |
| UD Turkish-FrameNet eğitim kaynakları / bunlarla ilişkili veri-model geçmişi | CC BY-SA 4.0 kaynak bildirimi |
| UD Turkish-IMST n-gram geçmişi | CC BY-NC-SA 3.0 kaynak bildirimi; Apache-2.0 ile yeniden lisanslanmadı |
| Qwen3-0.6B-Base temel model / tokenizer | Snapshot README: Apache-2.0; özgün README ve indirme makbuzu release'te |
| P21/P119 model parametreleri, derlenmiş sözcük/veri tabloları ve P129 adaptörleri | Araştırma köken ve makbuzları korunur; bütününe tek, sınırsız ticari kullanım lisansı iddia edilmez |
| native/src/engine içindeki üretilmiş veri/parametre tabloları (ör. gate_model.rs, rule_data.rs) | Algoritma kodu ile kaynak veri kökeni birbirinden ayrıdır; mevcut ilgili kaynak bildirimleri geçerlidir |
| Bilim Dili Türkçe PDF | Tarkan Özel tarafından sağlanan tarihsel belge; alıntıların kaynak hakları korunur |

`licenses/` mevcut tam bildirimleri içerir. `registry/s05-v0.3.1.json` kaynak kimlikleri ve Zemberek kanıt bağlantılarını taşır. Native veri/model varlıklarının tamamını yalnız Apache-2.0 olarak etiketlemeyin. Kodun açık kaynak olması bütün veri kaynaklarının koşullarını kaldırmaz. Bu paket yeni bir hukuki uyumluluk sertifikası değildir.

Apache metni: https://www.apache.org/licenses/LICENSE-2.0 . UD kaynak ayrıntıları özgün notices dosyalarındadır. Kapalı TEST veya karma TrMor içeriği paylaşılmaz.
