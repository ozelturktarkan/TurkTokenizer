"""Post-run aggregate diagnosis and report; never change the selected A2 policy."""
import collections
import gzip
import json
import math
import shutil
from pathlib import Path
from .calibrate import BASE, HERE, ROOT, read, digest, atomic_json, require, verify_freeze, validate_application


def main():
    folder = BASE / 'a1-large-20260908-v1' / 'A2'
    report_dir = folder / 'reports'
    require(not report_dir.exists(), 'REFUSING_TO_OVERWRITE_REPORT')
    require(not (folder / 'failure.json').exists(), 'CALIBRATION_FAILED')
    require(read(folder / 'progress.json')['status'] == 'COMPLETE', 'CALIBRATION_NOT_COMPLETE')
    frozen = read(folder / 'freeze.json')
    verify_freeze(folder, frozen)
    receipt = read(folder / 'backup-receipt.json')
    for copy in receipt['copies']:
        require(read(folder / copy / 'snapshot-sha256.json') == receipt['sha256'], 'BACKUP_MANIFEST_CHANGED')
        for name, expected in receipt['sha256'].items():
            require(digest(folder / copy / name) == expected, 'SNAPSHOT_CHANGED:' + name)
    summary = read(folder / 'summary.json')
    grid = read(folder / 'threshold-grid.json')
    with gzip.open(folder / 'word-metrics.jsonl.gz', 'rt', encoding='utf-8') as stream:
        rows = [json.loads(line) for line in stream]
    counts = collections.Counter()
    for row in rows:
        category = ('unprojectable' if not row['gold_projectable'] else
                    'unaligned' if not row['aligned'] else
                    'missing_lemma_candidate' if not row['candidate_lemma_pos'] else
                    'wrong_ranking' if not row['preferred_lemma_pos'] else 'correct_lemma')
        counts[category] += 1
        if row['A2_eligible'] and row['lemma_margin'] is None and row['feature_margin'] is None:
            counts['accepted_at_every_grid_pair'] += 1
            counts['always_accepted_lemma_wrong'] += not row['preferred_lemma_pos']
            counts['always_accepted_feature_wrong'] += not row['preferred_declared_features']
    best_diagnostic = max(grid, key=lambda r: (min(r['lemma_precision_pct'] or 0,
                                                  r['feature_precision_pct'] or 0), r['accepted']))
    strictest = next(r for r in grid if r['thresholds'] == {'lemma_threshold': 20, 'feature_threshold': 20})
    refs = [json.loads(line) for line in (folder / 'inputs/calib.jsonl').read_text(encoding='utf-8').splitlines()]
    accepted = 0
    with gzip.open(folder / 'outputs.jsonl.gz', 'rt', encoding='utf-8') as stream:
        for ref in refs:
            rec = json.loads(next(stream))
            require(rec['id'] == ref['id'], 'OUTPUT_ORDER_CHANGED')
            _, count = validate_application(ref, rec['output'], strictest['thresholds'])
            accepted += count
        require(next(stream, None) is None, 'EXTRA_OUTPUT_RECORDS')
    require(accepted == strictest['accepted'], 'STRICTEST_ONLINE_GATE_MISMATCH')
    baseline = summary['baseline_counts']; words = baseline['words']
    diagnosis = {'categories_all_words': dict(counts),
                 'best_precision_grid_pair_diagnostic_only': best_diagnostic,
                 'strictest_predeclared_pair_diagnostic_only': strictest,
                 'strictest_online_offline_verified_sentences': len(refs),
                 'candidate_lemma_pos_ceiling_pct_all_words': 100 * baseline['candidate_lemma_pos'] / words,
                 'minimum_correct_words_for_92pct': math.ceil(words * .92),
                 'minimum_new_correct_candidates_needed_for_92pct': math.ceil(words * .92) - baseline['candidate_lemma_pos'],
                 'not_a_selected_configuration': True, 'TEST_opened': False}
    report_dir.mkdir()
    atomic_json(report_dir / 'diagnosis.json', diagnosis)
    report = f"""# A1 → A3 → A2 sonucu: %92 hedefi mevcut eşiklerle karşılanmadı

A2, korunmuş A1 E05 ve A3 E00 (beş kanal katsayısı 1) üzerinde tamamlandı. CALIB kümesinin 382 cümlesi ve 2.266 noktalama dışı sözcüğü değerlendirildi. Önceden belirlenmiş 121 eşik çiftinin hiçbiri kabul edilen sözcüklerde hem kök+tür hem de tanımlı morfolojik özellik doğruluğunu %92'ye çıkaramadı. A2 ayarı `null` bırakıldı; varsayılan model değiştirilmedi.

| CALIB ölçümü | Sonuç |
|---|---:|
| Bütün sözcüklerde doğru kök+tür tercihi | 1.738 / 2.266 = %76,6990 |
| Bütün sözcüklerde doğru tanımlı özellikler | 1.669 / 2.266 = %73,6540 |
| Doğru kök+tür adayı havuzda mevcut | 1.953 / 2.266 = %{diagnosis['candidate_lemma_pos_ceiling_pct_all_words']:.4f} |
| İki %92 koşulunu sağlayan eşik çifti | 0 / 121 |

## Marjı yükseltmek ne yaptı?

| Eşikler (kök+tür, özellik) | Kabul | Bütün sözcüklerde kapsam | Kabulde kök+tür doğruluğu | Kabulde özellik doğruluğu |
|---|---:|---:|---:|---:|
| (0, 0), mevcut yapısal kapı korunarak | 1.933 | %85,30 | %82,10 (346 hata) | %78,89 (408 hata) |
| (20, 20), önceden belirlenmiş en yüksek çift | 958 | %42,28 | %87,68 (118 hata) | %86,01 (134 hata) |

Izgaradaki en yüksek ortak doğruluk da bu son düzeyde kaldı; (0, 20) aynı sayıları verdi. Bunlar tanı amaçlı sonuçlardır, onaylanmış A2 ayarı değildir. Kabulü azaltmak tek başına %92 doğruluk sağlamadı.

## Sorun nerede?

2.266 sözcüğün birbirini dışlayan dağılımı: 1.738 doğru kök+tür tercihi; doğru aday varken yanlış seçilen 215 sözcük; hizalı ve altın etiketi aktarılabilir olmasına rağmen doğru adayı bulunmayan 270 sözcük; altın etiketi ortografik birime aktarılamayan 38 birim; ayrıca 5 hizalanamayan birim. Son 43 birim paydadan çıkarılmadı.

Her eşik çiftinde kabul edilen 702 sözcükte iki marj da `None`: adaylar ilgili iki karar katmanında tek grup oluşturuyor. Mevcut A2 uygulaması bu durumlarda marj koşulunu geçmiş sayıyor. Bu 702 sözcük içinde 81 kök+tür ve 96 özellik hatası var. Envanterde rakibin bulunmaması doğruluk garantisi sağlamıyor; marjı büyütmek bu hataları elemiyor. Bunlar tek neden değil: son 958 kabul içinde toplam 118/134 hata var.

Aday havuzu sabitken kusursuz bir sıralayıcının bile bu CALIB paydasındaki kök+tür tavanı %{diagnosis['candidate_lemma_pos_ceiling_pct_all_words']:.4f}. %92 için en az 2.085 doğru sözcük gerekir: tüm mevcut doğru adaylar seçilse bile en az 132 ek sözcükte doğru aday erişimi gereklidir. Bu, aday eksikleri ve etiket/hizalama kapsamını ayrı incelemeyi; mevcut 215 sıralama hatasını da ayrı çözmeyi gerektirir.

## Doğrulama ve kayıt

Altı seçim politikası testi geçti. 539 çözücü bloğunun hedef puanı, 6.528 aday kaydı, arama tamlığı, yeniden birleştirme ve ilişki grafiği kontrol edildi. (0, 0) ve tanı amaçlı (20, 20) kararları 382 cümlenin tamamında gerçek A2 uygulamasıyla aynı kabul sayılarını verdi; tercih edilen adaylar değişmedi. Girdi, kaynak ve model SHA-256 kontrolleri geçti.

V: üzerinde 106 dosyalık iki snapshot yeniden doğrulandı; gerçek A1 ağırlıkları, A3 katsayıları, girdiler, kaynak, özel çıktı ve durum dosyaları bu kopyalara dahil. Rapor ve tanı dosyaları ayrıca iki kopya olarak kaydedilir. GitHub'a kaynak kod, toplu metrikler, loglar ve hash makbuzları aktarılır; ağırlıklar ve ham sözcük kayıtları V: üzerinde kalır. İki V kopyası aynı diskte olduğu için fiziksel disk arızasına karşı bağımsız yedek değildir.

CALIB eşik seçiminde kullanıldı; bu sonuç bağımsız TEST doğruluğu değildir. Önceki DEV sonucu %77,9607 idi ve ayrı bir veri kümesini ölçüyordu. TEST açılmadı. Tanımlı özellik doğruluğu tam morfem yolu doğruluğu değildir. Gerçek BPE yönlendirme oranı ölçülmedi; %92 TürkTokenizer + %8 BPE hedefine ulaşıldığı söylenemez. Wilson aralıkları yalnızca betimseldir; eşik seçimi ve belge bağımlılığı için düzeltilmemiştir.

Sonraki geliştirme için somut öncelik: tek gruplu yanlış kabullerin kök nedenleri, doğru aday bulunmayan 270 sözcük ve doğru adaylı 215 sıralama hatası. Bu CALIB sonuçlarına göre yapılacak değişiklikler için yeni bağımsız değerlendirme gerekir.
"""
    (report_dir / 'final-report.md').write_text(report, encoding='utf-8', newline='\n')
    final = {**summary, 'diagnosis': diagnosis, 'final_verification': {
        'snapshot_files_per_copy': receipt['files_per_copy'], 'verified_copies': 2,
        'report_source_sha256': digest(Path(__file__)), 'TEST_opened': False, 'default_promoted': False}}
    atomic_json(report_dir / 'final-summary.json', final)
    for name in ('summary.json', 'selection.json', 'threshold-grid.json', 'freeze.json',
                 'backup-receipt.json', 'calibration.log', 'progress.json'):
        shutil.copyfile(folder / name, report_dir / name)
    hashes = {p.name: digest(p) for p in report_dir.iterdir() if p.is_file()}
    atomic_json(report_dir / 'report-sha256.json', hashes)
    files = [p for p in report_dir.iterdir() if p.is_file()]
    for name in ('copy-a', 'copy-b'):
        (report_dir / name).mkdir()
        for file in files:
            dest = report_dir / name / file.name
            shutil.copyfile(file, dest)
            require(digest(file) == digest(dest), 'REPORT_BACKUP_MISMATCH')
    verify_freeze(folder, frozen)
    print(json.dumps({'status': 'FINAL_VERIFIED', 'report_files_per_copy': len(files), 'diagnosis': diagnosis}, ensure_ascii=False))


if __name__ == '__main__':
    main()
