"""Add the bounded question experiment without altering the frozen P2 snapshot."""
import hashlib
import json
import shutil
from pathlib import Path
from bootstrap import ROOT
from training_controls.e70p9.epoch_control import read,digest,atomic_json
from training_controls.a2_calibration.calibrate import require
from .fit import DEST,LOCAL

PREFIX='training-runs/a1-large-20260908-v1/P2-lexical-v1'


def main():
    q=read(LOCAL/'question-aligned-r2/comparison.json')
    require(q['status']=='EXPERIMENT_COMPLETE','Q_NOT_COMPLETE')
    outbox=read(LOCAL/'github-outbox.json')
    require(all(digest(Path(v['local_path']))==v['sha256'] for v in outbox['files'].values()),'P2_PUBLIC_CHANGED')
    base=read(LOCAL/'backup-receipt.json')
    for side in ('copy-a','copy-b'):
        require(all(digest(DEST/'snapshots'/side/n)==h for n,h in base['sha256'].items()),'P2_BACKUP_CHANGED')
    frozen=read(LOCAL/'question-aligned-r2/freeze.json')
    require(all(digest(ROOT/n)==h for n,h in frozen.items()),'Q_SOURCE_CHANGED')
    policy=read(LOCAL/'policy-imst/comparison.json')['arms']['1.00']
    gain=any(q['results'][s]['views']['predicted_view_lemma_pos']>policy[s]['views']['predicted_view_lemma_pos'] or
             q['results'][s]['legacy']['preferred_lemma_pos']>policy[s]['legacy']['preferred_lemma_pos'] or
             q['results'][s]['legacy']['preferred_declared_features']>policy[s]['legacy']['preferred_declared_features'] or
             q['results'][s]['legacy']['legacy_selected_lemma_wrong']<policy[s]['legacy']['legacy_selected_lemma_wrong'] for s in ('dev','calib'))
    keep_q=gain and q['nonregression_against_policy'] and all(q['results'][s]['views']['predicted_view_lemma_pos']>=policy[s]['views']['predicted_view_lemma_pos'] for s in ('dev','calib'))
    entry='s06e_p2_question' if keep_q else 's06e_p2_policy'
    lines=['# P2 soru eki hizalaması: ek deney','',
        'Soru okumalarının PART etiketi yalnız n-gram puanlamasında AUX ile hizalandı. Dört lisanslı soru sözlük kaydı başlangıçta doğrulandı; nota adı olan NOUN okuması değiştirilmedi. Yeni eğitim, aday veya eşik araması yapılmadı.', '',
        '| Kol | DEV kök+tür | DEV özellik | DEV yanlış kesin | DEV sözlüksel çıktı | CALIB kök+tür | CALIB özellik | CALIB yanlış kesin | CALIB sözlüksel çıktı |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for label,arm in [('P2 IMST',policy),('Soru hizalama',q['results'])]:
        vals=[]
        for s in ('dev','calib'):
            vals.extend(arm[s]['legacy'][k] for k in ('preferred_lemma_pos','preferred_declared_features','legacy_selected_lemma_wrong'))
            vals.append(arm[s]['views']['predicted_view_lemma_pos'])
        lines.append('| '+label+' | '+' | '.join(map(str,vals))+' |')
    lines+=['',f"Önceden tanımlanan eski ölçütlerde gerilememe kontrolü: **{q['nonregression_against_policy']}**. Ölçülen ek kazanç var mı: **{gain}**. Gerilememe tek başına ek katmanı önerme nedeni sayılmadı. Teslim önerisi: `{entry}.Tokenizer(strength=1.0)`. Genel proje varsayılanı değiştirilmedi.", '',
        f"Elle yazılmış bağlam tanılarında eşleşme **{q['authored_probes_matched']}/8**. “Sen geldin mi?” örneği hâlâ mi/NOUN seçiyor. Bu nedenle etiketi hizalamak tek başına bu anlam seçimi sorununu çözmüş sayılmaz.", '',
        'İlk koşu iki DEV cümlesinden sonra durdu: aday sırası testi, çözümleyicinin paylaşılan önbellek listesini ters çevirmişti. Taze çalışma aynı adayları ve sırayı verdi; yanlışlık yalnız testin yan etkisiydi. Test girdisi derin kopyalanarak ayrı klasörde baştan çalıştırıldı. Adayların sırası ve içeriği için eşitlik kontrolü gevşetilmedi; ilk başarısız koşu korundu.', '',
        'Tamamlanan ek koşuda 293 DEV + 382 CALIB cümlesinin morfolojik adayları P2 ile birebir karşılaştırıldı; toplam puan bağımsız yordamla, BPE ile geri kurma her çıktıda doğrulandı. DEV/CALIB geliştirmede görülmüş verilerdir; bağımsız test değildir. TEST açılmadı.', '',
        'Ana P2 sonuçları ve temsil/seçim katkısı ayrı ana rapordadır. Bu ek deney onun dondurulmuş kaynaklarını veya 106 dosyalık çift yedeğini değiştirmez. Ek dosyalar snapshots/question-addendum altında ayrıca iki kez hash doğrulamasıyla saklanır.','']
    (LOCAL/'question-report.md').write_text('\n'.join(lines),encoding='utf-8',newline='\n')
    note=['# TürkTokenizer: P2 sonrası devam noktası','',
        f'Geliştirme için önerilen açık giriş: `{entry}.Tokenizer(strength=1.0)`. E05 ana varsayılanı korunuyor.', '',
        'P2 IMST kolunda eski kök+tür: DEV 3174/4070, CALIB 1751/2266; önceki E05 toplamına göre net +14. Yanlış kesin karar toplamı 978 → 962. Yeni sözlüksel çıktı 3350/4070 ve 1876/2266; aynı çıktı sözleşmesiyle puanlayıcı katkısı net +144. Temsil katmanının ayrı katkısı net +171. Bunlar aynı tür doğruluk artışı olarak birleştirilmez.', '',
        'Ana rapor: `S06E-E05-P2-degerlendirmesi.md`. Ek soru deneyi: `results_lexical_p2/question-report.md`. Deneylerin protokol, eğitim, DEV seçimi ve CALIB kayıtları `results_lexical_p2` ile `training_controls/lexical_p2` içindedir.', '',
        'Kalan somut açık: “Sen geldin mi?” sorusundaki mi nota adı seçilebiliyor. Sonraki inceleme, soru ve nota okumalarının E05 UA, sözlüksel başlık ve cümle geçiş puanlarını aynı sabit adaylar üzerinde ayırmaktır. Yeni kuralı yalnız bir cümleye göre zorlamadan soru/nota karşıt kullanımlarıyla sınamak gerekir.', '',
        'Eski 270 vakalık lemma+tür tanısını, yeni görünüm ölçümüyle yeniden yorumlamak gerekir; temsil uyuşmazlığı ve gerçek analiz eksikliği ayrı tutulmalıdır. %92 morfolojik doğruluk veya <%8 BPE hedefi henüz sağlanmadı. TEST açılmadı.', '',
        f'Özel deney kökü: `{DEST}`. İlk çift yedek: `snapshots/copy-a`, `snapshots/copy-b`; ek deney yedeği: `snapshots/question-addendum/copy-a`, `copy-b`. Aynı fiziksel V sürücüsündeler; önceki proje tabanı gereklidir.', '',
        'GitHub hedefi: `ozelturktarkan/TurkTokenizer`, dal `codex/s06e-e05-p1-phonology`. Doğrulanmış önceki commit: `d6ac73c55e4fc3603b8cbb3cd69cfa4df1f6e69d`. Bu P2 tesliminin uzak doğrulama kaydı yerelde `results_lexical_p2/publication-receipt.json` olarak tutulur; kaydın yokluğu gönderimin henüz doğrulanmadığı anlamına gelir.','']
    (ROOT/'DEVAM-NOKTASI-P2.md').write_text('\n'.join(note),encoding='utf-8',newline='\n')
    public={n:ROOT/n for n in ['s06e_p2_question.py','training_controls/lexical_p2/evaluate_question.py','training_controls/lexical_p2/question-protocol.json','training_controls/lexical_p2/finalize_question.py','DEVAM-NOKTASI-P2.md']}
    reports=['question-report.md','question-aligned/failure-receipt.json','question-aligned/freeze.json',
             'question-aligned-r2/comparison.json','question-aligned-r2/freeze.json','question-aligned-r2/runtime-contracts.json']
    public.update({PREFIX+'/'+n:LOCAL/n for n in reports})
    payload={'source/'+n:p for n,p in public.items()}
    for name in ('question-aligned','question-aligned-r2'):
        payload.update({'private/'+p.relative_to(DEST).as_posix():p for p in (DEST/name).rglob('*') if p.is_file()})
        payload.update({'reports/'+p.relative_to(LOCAL).as_posix():p for p in (LOCAL/name).rglob('*') if p.is_file()})
    hashes={n:digest(p) for n,p in payload.items()}
    backup=DEST/'snapshots/question-addendum'
    require(not backup.exists(),'Q_BACKUP_EXISTS')
    for side in ('copy-a','copy-b'):
        for n,p in payload.items():
            target=backup/side/n
            require(target.resolve().is_relative_to((backup/side).resolve()),'Q_UNSAFE_COPY')
            target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
            require(digest(target)==hashes[n],'Q_COPY_CHANGED')
        atomic_json(backup/side/'sha256.json',hashes)
    receipt={'status':'TWO_V_ADDENDUM_COPIES_VERIFIED','files_per_copy':len(hashes),'path':str(backup),
             'original_P2_106_files_per_copy_reverified':True,'same_physical_drive':True,'sha256':hashes}
    atomic_json(LOCAL/'question-backup-receipt.json',receipt)
    for p in [DEST/'question-backup-receipt.json',backup/'copy-a/backup-receipt.json',backup/'copy-b/backup-receipt.json']:atomic_json(p,receipt)
    public[PREFIX+'/question-backup-receipt.json']=LOCAL/'question-backup-receipt.json'
    outbox['files'].update({n:{'local_path':str(p),'sha256':digest(p),'bytes':p.stat().st_size} for n,p in public.items()})
    outbox['base_outbox_sha256']=digest(LOCAL/'github-outbox.json')
    atomic_json(LOCAL/'github-outbox-final.json',outbox)
    print(json.dumps({'status':'P2_AND_Q_READY','recommended_entry':entry,'public_files':len(outbox['files']),
                      'addon_backup_files_per_copy':len(hashes)}),flush=True)


if __name__=='__main__': main()
