"""Write measured report, two verified V snapshots and an explicit public outbox."""
import json
import shutil
from pathlib import Path

from bootstrap import ROOT
from training_controls.a2_calibration.calibrate import verify_freeze, require
from training_controls.e70p9.epoch_control import read, digest, atomic_json
from .evaluate import DEST, LOCAL, PARENT, HERE

PUBLIC_PREFIX = 'training-runs/a1-large-20260908-v1/P1-phonology-v1'


def report(result):
    lines = ['# S06E E05 P1: ses sınıfı ve telaffuz onarımı', '',
        'A1 E05 ve A3 E00 sabitken dört kol tamamlandı. Yeni eğitim yapılmadı; eski sözlük/ek dosyaları, referans etiketler, arama sınırları ve BPE kimlikleri değişmedi. Bu ayrı bir deney girişidir; eski varsayılan yükseltilmedi.', '',
        '## Aynı koşullarda karşılaştırma', '',
        '| Kol | DEV doğru lemma+tür /4070 | DEV özellik /4070 | DEV yanlış kesin karar | CALIB doğru lemma+tür /2266 | CALIB özellik /2266 | CALIB yanlış kesin karar |',
        '|---|---:|---:|---:|---:|---:|---:|']
    labels = {'baseline': 'E05 kontrol', 'circumflex': 'Şapkalı ünlü',
              'pronunciation': 'Telaffuz', 'combined': 'Birleşik P1'}
    for arm, data in result['arms'].items():
        d, c = data['dev']['counts'], data['calib']['counts']
        lines.append(f"| {labels[arm]} | {d['preferred_lemma_pos']} | {d['preferred_declared_features']} | {d['legacy_selected_lemma_wrong']} | {c['preferred_lemma_pos']} | {c['preferred_declared_features']} | {c['legacy_selected_lemma_wrong']} |")
    lines += ['', 'DEV model geliştirmede; CALIB kalibrasyon ve 270 vaka incelemesinde kullanılmıştır. Bunlar bağımsız yeni test sonuçları değildir. Tam morfem yolu doğruluğu ölçülmüş sayılmaz; kök+tür ve beyanlı özellik ölçüleri ayrıdır. TEST bu koşuda açılmadı.', '',
              '## Birleşik koldaki aday ve seçim değişimleri', '']
    for split in ('dev', 'calib'):
        data = result['arms']['combined'][split]; delta = data['candidate_delta']; pair = data['paired']
        n = data['counts']['words']; correct = data['counts']['preferred_lemma_pos']
        change = pair['preferred_lemma_pos']; coverage = pair['candidate_lemma_pos']
        lines += [f"### {split.upper()}", '',
            f"Doğru lemma+tür: {correct}/{n} = %{100*correct/n:.4f}. {change['fixed']} eski hata düzeldi, {change['regressed']} yeni seçim hatası oluştu; net {change['net']:+d}.", '',
            f"Doğru aday kapsaması: +{coverage['fixed']} / -{coverage['regressed']} sözcük. {delta.get('changed_tokens',0)} tokenın adayları değişti; {delta.get('added_candidates',0)} aday eklendi, {delta.get('removed_candidates',0)} aday kaldırıldı. {delta.get('retained_candidate_ids',0)} ortak adayın ID'si ve bütün içeriği korundu.", '',
            f"Eklenen adayların {delta.get('added_reference_matching_candidates',0)} tanesi mevcut kök+tür referansıyla eşleşiyor, {delta.get('added_reference_mismatching_candidates',0)} tanesi eşleşmiyor. Bu ikinci sayı dilbilgisel yanlış aday sayısı değildir; geçerli belirsizlik ve kaynak tür politikası farklarını da içerir.", '']
    focused = result['focused_contrasts']
    lines += ['## Dar davranış kontrolleri', '', '| Kol | Geçerli yol + hatalı karşıt birlikte geçen çift /25 |', '|---|---:|']
    for arm in labels:
        rows = [r for r in focused if r['arm'] == arm]
        lines.append(f"| {labels[arm]} | {sum(r['good_path_present'] and r['bad_path_absent'] for r in rows)} |")
    lines += ['',
        '`vicahîye`, `zekâya`, `rükûya`, `Taylor’ın`, `İMKB’nin`, `Abby’ye` ve `Vodafone’a` için ses koşulları onarıldı. `Taylor’ım` / `TBMM’yim` gibi sıfır ek üzerinden geçen yollarda telaffuz korunuyor. Sesli ek gerçekleştikten sonra sonraki uyum o ekin ünlüsünden hesaplanıyor. Yazım ve ham karakter aralıkları değiştirilmedi.', '',
        'Önceki rapor düzeltmesi: İMKB kaydında `Abbrv` etiketi yok denmişti; gerçekte etiket zaten var. Eski yükleyici `imkb` içinde ünlü bulunduğu için harf harf okuma üretmiyordu. Bu deney açık okuma moduyla bunu düzeltti. İMKB’nin PROPN analizi, kaynak NOUN etiketini otomatik karşılamaz.', '',
        '## Değişen örneklerin incelemesi', '',
        'DEV’de eklenen beş yol, mevcut kısaltma okumasının iyelik ekinden sonra korunmasından geliyor: POSS_2_SING + CASE_GEN. Hiçbir eski aday kaldırılmadı. RP’nin aday havuzundaki genişleme, aynı cümlede adayları değişmeyen `süren` sözcüğünün PART_AN/NOUN seçimini PART_AN/ADJ seçimine çevirdi. Referans VERB/Part iken eski uyumluluk yordamı ilk temsili kabul edip ikinciyi reddediyor. Ölçütteki -1 aynen korundu; bunun tartışmasız bir dilbilgisi hatası olduğu varsayılmadı. Aynı cümlede başka bir yanlış kesin karar belirsize döndüğü için toplam yanlış kesin karar sayısı değişmedi.', '',
        'CALIB’de Taylor için CASE_GEN ve POSS_2_SING yolları geldi; çözücü doğru CASE_GEN yolunu seçti. Aynı cümledeki `bölümü` de belirtme durumundan doğru üçüncü tekil iyeliğe geçti. `üyeleri` sözcüğünün tercihi değişse de referansın sayı/iyelik özelliklerine hâlâ uymuyor; ek kazanım sayılmadı. İMKB için doğru CASE_GEN yolu seçildi fakat PROPN/NOUN temsil farkı nedeniyle mevcut ölçütte yeni bir yanlış kesin karar oluştu. Diğer yeni yol ABD kısaltmasındaki iyelik + tamlayan belirsizliğidir.', '',
        'Şapkalı ünlü kolu bu iki havuzda hiç aday değiştirmedi. Dolayısıyla odaklı örneklerdeki onarımı havuz kazanımı olarak saymıyoruz. Bağlam etkisi ve tür/ortaç temsili, sonraki dar incelemenin konusu olmalı; bu sonuçlara göre puan ağırlıkları veya referans etiketleri değiştirilmedi.', '',
        '## Karar ve kalan iş', '', f"Önceden belirlenmiş seçim kuralının sonucu: **{result['selection']}**.", '',
        f"CALIB'deki önceki 121 eşik çiftinde %92 koşulunu sağlayan çift sayısı: kontrol {result['arms']['baseline']['calib']['A2_feasible_grid_pairs_diagnostic_only']}, birleşik P1 {result['arms']['combined']['calib']['A2_feasible_grid_pairs_diagnostic_only']}. Bu tarama tanı amaçlıdır; yeni A2 eşiği seçilmedi.", '',
        'Şapkasız `vicahiye` otomatik düzeltilmiyor. Kök–lemma/tür temsili, gözyaşı bileşikleri ve zamir araçlığı henüz onarılmadı. Tarihsel yinelenen ağız okumasının `ağızı` adayına izin vermesi de ayrı bir sözlük sorunu olarak kaydedildi; P1 başarısı gibi sunulmadı.', '',
        '25 karşıt çift sözcük ve ek yolu davranışını sınar; 25 bağlamlı anlam kararı veya bütün Türkçede kusursuzluk iddiası değildir. Her kaynak sözcükte yeni aday/tercih ayrıntıları V sürücüsündeki özel dökümlerdedir.', '',
        '## Doğrulama ve dosyalar', '',
        f"Tüm kollarda {sum(d[s]['BPE_roundtrips'] for d in result['arms'].values() for s in ('dev','calib'))} cümle çıktısında BPE geri kurma doğrulandı. 224.309 eski ID aynen korundu. Ek API kontrolü 12 metin, 37 geri kurma ve 256 ham bayt değerini kapsadı. Kod bloklarının morfolojiye girmeden BPE üzerinden dönmesi kontrol edildi.", '',
        'Ek iki karşıt kontrol de geçti: Fox’ta/Fox’da son sesin sertliğini, Taylor’dakinin/Taylor’dakının ise -ki sonrasında yeni ek ünlüsünün uyumu yönetmesini denetledi. Bunlar 25 çiftlik dört kollu karşılaştırmanın dışında raporlanan API kontrolleridir.', '',
        'Seçilmiş E05 dosyası ve tarihsel kaynaklar deney öncesinde/sonrasında hash ile doğrulandı. Model ağırlıkları ve ham kaynak metinleri V sürücüsünde kalır. GitHub yayını yeni yama, testler, toplu raporlar ve hash kayıtlarından oluşur; bağımsız tam dağıtım paketi değildir.', '',
        'İki V kopyası aynı fiziksel disktedir. Geri dönüş dosyaları ve kaynak hash listesi `backup-receipt.json` içinde kaydedilir.', '',
        '## Dilbilimsel kaynaklar', '',
        '- [TDK düzeltme işareti](https://tdk.gov.tr/icerik/yazim-kurallari/duzeltme-isareti/)',
        '- [TDK kısaltmalar](https://tdk.gov.tr/icerik/yazim-kurallari/kisaltmalar/)',
        '- [MEB Taylor/Teylır okunuşu](https://ogmmateryal.eba.gov.tr/kitap/guzel-sanatlar-lisesi/gorsel-sanatlar/cdst-12/files/basic-html/page124.html)', '']
    return '\n'.join(lines)


def main():
    result = read(LOCAL / 'comparison.json')
    require(result['status'] == 'EXPERIMENT_COMPLETE', 'P1_EXPERIMENT_INCOMPLETE')
    require(not (LOCAL / 'backup-receipt.json').exists(), 'REFUSING_TO_OVERWRITE_P1_DELIVERY')
    runtime = read(LOCAL / 'runtime-contracts.json')
    require(runtime['status'] == 'PASS', 'P1_RUNTIME_CONTRACTS_FAILED')
    unit = read(LOCAL / 'unit-contracts.json')
    require(unit['status'] == 'PASS' and unit['verified_exit_code'] == 0, 'P1_UNIT_CONTRACTS_FAILED')
    for n, h in unit['source_sha256'].items():
        require(digest(ROOT / n) == h, 'P1_UNIT_SOURCE_CHANGED:' + n)
    for n, h in runtime['implementation_sha256'].items():
        require(digest(ROOT / n) == h, 'P1_VALIDATED_RUNTIME_CHANGED:' + n)
    frozen = read(LOCAL / 'freeze.json')
    require(all(digest(ROOT / n) == h for n, h in frozen['new_sources'].items()), 'P1_EVALUATED_SOURCE_CHANGED')
    verify_freeze(PARENT / 'A2', read(PARENT / 'A2/freeze.json'))
    for arm, splits in result['arms'].items():
        for split, summary in splits.items():
            for n, h in summary['artifact_sha256'].items():
                require(digest(DEST / arm / split / n) == h, 'P1_RESULT_FILE_CHANGED:' + n)
    text = report(result)
    (LOCAL / 'final-report.md').write_text(text, encoding='utf-8', newline='\n')
    (ROOT / 'S06E-E05-P1-degerlendirmesi.md').write_text(text, encoding='utf-8', newline='\n')
    # Record concrete files only; never glob unrelated backups or credentials.
    patch = ['analyzer_s06e_p1.py', 's06e_p1.py', 's06e_p1bpe.py',
             'data/s06e-p1/pronunciations.json', 'S06E-E05-P1-degerlendirmesi.md']
    patch += [p.relative_to(ROOT).as_posix() for p in sorted(HERE.iterdir()) if p.suffix in ('.py', '.json', '.md')]
    public = {n: ROOT / n for n in patch}
    for n in ('final-report.md', 'comparison.json', 'freeze.json', 'runtime-contracts.json', 'unit-contracts.json'):
        require((LOCAL / n).is_file(), 'P1_MISSING_DELIVERY:' + n)
        public[PUBLIC_PREFIX + '/' + n] = LOCAL / n
    # The two snapshots contain the patch, fixed selected weights and all new
    # raw outputs; this is an incremental backup atop the existing project base.
    snapshots = {('source/' + n): p for n, p in public.items() if not n.startswith(PUBLIC_PREFIX)}
    snapshots.update({('results/' + p.relative_to(DEST).as_posix()): p
                      for p in DEST.rglob('*') if p.is_file()})
    snapshots.update({('reports/' + p.name): p for p in LOCAL.iterdir() if p.is_file()})
    snapshots.update({'models/a1-e05-ranker.json': PARENT / 'A1/selected-ranker.json',
                      'models/a3-e00-ranking.json': PARENT / 'A3/selected-ranking.json'})
    hashes = {n: digest(p) for n, p in snapshots.items()}
    require(shutil.disk_usage(PARENT).free > 2 * sum(p.stat().st_size for p in snapshots.values()) + 5 * 1024 ** 3,
            'P1_SNAPSHOT_SPACE_LOW')
    base = DEST / 'snapshots'
    require(not base.exists(), 'P1_SNAPSHOTS_EXIST')
    for copy in ('copy-a', 'copy-b'):
        for name, source in snapshots.items():
            dest = base / copy / name
            require(dest.resolve().is_relative_to((base / copy).resolve()), 'P1_UNSAFE_COPY_PATH')
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, dest)
            require(digest(dest) == hashes[name], 'P1_SNAPSHOT_HASH_MISMATCH:' + name)
        atomic_json(base / copy / 'sha256.json', hashes)
    receipt = {'status': 'TWO_V_SNAPSHOTS_VERIFIED', 'files_per_copy': len(hashes),
               'snapshot_directory': str(base), 'same_physical_drive': True,
               'scope': 'INCREMENTAL_PATCH_PLUS_SELECTED_MODELS_AND_NEW_EXPERIMENT_OUTPUTS',
               'requires_existing_frozen_project_base': True, 'sha256': hashes}
    atomic_json(LOCAL / 'backup-receipt.json', receipt)
    atomic_json(DEST / 'backup-receipt.json', receipt)
    for copy in ('copy-a', 'copy-b'):
        atomic_json(base / copy / 'backup-receipt.json', receipt)
    public[PUBLIC_PREFIX + '/backup-receipt.json'] = LOCAL / 'backup-receipt.json'
    outbox = {'repository': 'ozelturktarkan/TurkTokenizer', 'branch': 'codex/s06e-e05-p1-phonology',
              'base_commit': '9db53259b6c88f5539fcf1ec867f1d5bef2507a4',
              'files': {name: {'local_path': str(p), 'sha256': digest(p), 'bytes': p.stat().st_size}
                        for name, p in public.items()}, 'raw_corpus_or_weights_published': False}
    atomic_json(LOCAL / 'github-outbox.json', outbox)
    print(json.dumps({'status': 'READY_FOR_GITHUB', 'public_files': len(public),
                      'snapshot_files_per_copy': len(hashes), 'selection': result['selection']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
