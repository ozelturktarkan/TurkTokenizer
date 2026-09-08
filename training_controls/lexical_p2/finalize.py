"""Verified P2 delivery: separate representation/selection effects and backups."""
import gzip
import json
import shutil
from pathlib import Path
from bootstrap import ROOT
from training_controls.e70p9.epoch_control import read,digest,atomic_json
from training_controls.a2_calibration.calibrate import verify_freeze,require
from .fit import DEST,LOCAL,PARENT,HERE
from .evaluate import records

PREFIX='training-runs/a1-large-20260908-v1/P2-lexical-v1'


def pair(a,b,key):
    return {'fixed':sum(not x[key] and y[key] for x,y in zip(a,b,strict=True)),
            'regressed':sum(x[key] and not y[key] for x,y in zip(a,b,strict=True)),
            'net':sum(y[key]-x[key] for x,y in zip(a,b,strict=True))}


def main():
    require(not (LOCAL/'backup-receipt.json').exists(),'P2_REFUSE_OVERWRITE_DELIVERY')
    mixed=read(LOCAL/'comparison.json'); policy=read(LOCAL/'policy-imst/comparison.json')
    require(mixed['status']==policy['status']=='EXPERIMENT_COMPLETE','P2_INCOMPLETE')
    require(read(LOCAL/'runtime-contracts.json')['status']=='PASS','P2_API_FAILED')
    require(read(LOCAL/'policy-imst/runtime-contracts.json')['status']=='API_CONTRACTS_PASS','P2_POLICY_API_FAILED')
    verify_freeze(PARENT/'A2',read(PARENT/'A2/freeze.json'))
    for path,key in [('freeze.json','sources'),('runtime-contracts.json','sources'),('unit-contracts.json','sources'),
                     ('policy-imst/freeze.json','sources'),('policy-imst/runtime-contracts.json','source_sha256')]:
        require(all(digest(ROOT/n)==h for n,h in read(LOCAL/path)[key].items()),'P2_VERIFIED_SOURCE_CHANGED:'+path)
    for path in ['evaluation-freeze.json','policy-imst/evaluation-freeze.json']:
        require(all(digest(ROOT/n)==h for n,h in read(LOCAL/path).items()),'P2_EVALUATED_SOURCE_CHANGED')
    for tag,res,folder in [('mixed',mixed,DEST/'evaluation'),('policy',policy,DEST/'policy-imst/evaluation')]:
        expected_head=read(LOCAL/('model-location.json' if tag=='mixed' else 'policy-imst/model-location.json'))
        require(digest(expected_head['path'])==expected_head['sha256'],'P2_HEAD_CHANGED')
        for strength,splits in res['arms'].items():
            for split,data in splits.items():
                for n,h in data['artifact_sha256'].items():
                    require(digest(folder/strength/split/n)==h,'P2_RESULT_CHANGED:'+n)
                for rec in records(folder/strength/split/'outputs.jsonl.gz'):
                    require(rec['output']['experiment']['lexical_head_sha256']==expected_head['sha256'],'P2_OUTPUT_USED_WRONG_HEAD')
    chosen=f"{policy['selected_strength']:.2f}"; review={}
    for split in ('dev','calib'):
        base=DEST/'policy-imst/evaluation/0.00'/split
        new=DEST/'policy-imst/evaluation'/chosen/split
        bn=list(records(base/'native-words.jsonl.gz')); nn=list(records(new/'native-words.jsonl.gz'))
        bv=list(records(base/'view-words.jsonl.gz')); nv=list(records(new/'view-words.jsonl.gz'))
        require([(r['id'],r['start'],r['end']) for r in bn]==[(r['id'],r['start'],r['end']) for r in nn],'P2_PAIRED_IDS')
        changes=[]
        for a,b,x,y in zip(bn,nn,bv,nv,strict=True):
            if x['native_analysis_id']!=y['native_analysis_id'] or x['predicted_view']!=y['predicted_view']:
                changes.append({'id':a['id'],'start':a['start'],'end':a['end'],'surface':a['surface'],
                    'gold':a['gold'],'native_before':a['preferred'],'native_after':b['preferred'],
                    'view_before':x['predicted_view'],'view_after':y['predicted_view'],
                    'legacy_correct_before':a['preferred_lemma_pos'],'legacy_correct_after':b['preferred_lemma_pos'],
                    'view_correct_before':x['predicted_view_lemma_pos'],'view_correct_after':y['predicted_view_lemma_pos']})
        with gzip.open(DEST/f'{split}-reviewed-changes.jsonl.gz','wt',encoding='utf-8') as f:
            for r in changes:f.write(json.dumps(r,ensure_ascii=False)+'\n')
        review[split]={'native_lemma_pos':pair(bn,nn,'preferred_lemma_pos'),
            'native_features':pair(bn,nn,'preferred_declared_features'),
            'view_lemma_pos':pair(bv,nv,'predicted_view_lemma_pos'),
            'view_features':pair(bv,nv,'predicted_view_features'),
            'changed_native_analysis_ids':sum(x['native_analysis_id']!=y['native_analysis_id'] for x,y in zip(bv,nv)),
            'representation_only':{'fixed':sum(not a['preferred_lemma_pos'] and b['predicted_view_lemma_pos'] for a,b in zip(bn,bv)),
                                   'regressed':sum(a['preferred_lemma_pos'] and not b['predicted_view_lemma_pos'] for a,b in zip(bn,bv))}}
    atomic_json(LOCAL/'change-review.json',review)
    hist=read(ROOT/'results_phonology_p1/comparison.json')['arms']['baseline']
    lines=['# S06E E05 P2: kök, türemiş lemma ve kaynak politikası', '',
        'P1 morfolojisi ve E05 ağırlıkları sabitken, ayrı bir sözlüksel görünüm puanlayıcısı geliştirildi. Morfolojik aday, ek yolu, başlangıç kökü ve BPE kimliği değiştirilmedi. Yeni bilgi, eski adayın üzerine ayrı lexical_analyses / lexical_decision alanlarıyla eklendi.', '',
        '## Eski ölçütle aynı koşullarda sonuç', '',
        '| Kol | DEV kök+tür /4070 | DEV özellik | DEV yanlış kesin | CALIB kök+tür /2266 | CALIB özellik | CALIB yanlış kesin |',
        '|---|---:|---:|---:|---:|---:|---:|']
    hd,hc=hist['dev']['counts'],hist['calib']['counts']
    lines.append(f"| Önceki seçili E05 | {hd['preferred_lemma_pos']} | {hd['preferred_declared_features']} | {hd['legacy_selected_lemma_wrong']} | {hc['preferred_lemma_pos']} | {hc['preferred_declared_features']} | {hc['legacy_selected_lemma_wrong']} |")
    for label,res in [('Karma TRAIN',mixed),('IMST TRAIN',policy)]:
        for strength,splits in res['arms'].items():
            vals=[]
            for split in ('dev','calib'):
                if split in splits:
                    c=splits[split]['legacy'];vals += [str(c[k]) for k in ('preferred_lemma_pos','preferred_declared_features','legacy_selected_lemma_wrong')]
                else: vals+=['—']*3
            lines.append('| '+label+' ×'+strength+' | '+' | '.join(vals)+' |')
    lines += ['', 'Karma eğitimde DEV seçimi 0 oldu; diğer katsayılar CALIB’de çalıştırılmadı. IMST başlığı ayrı ve açıkça keşif amaçlı bir uzantıdır. Kendi DEV seçimi mühürlendikten sonra CALIB kontrolü yapıldı; CALIB’ye göre katsayı değiştirilmedi. Referanslar ve tarihsel ölçüm kodu değiştirilmedi.', '',
        '## Tek tahmin edilen sözlüksel lemma+tür', '',
        '| Kol | DEV /4070 | CALIB /2266 |', '|---|---:|---:|']
    for label,res,strength in [('Karma başlık; eski P1 tercihi',mixed,'0.00'),('IMST başlığı; eski P1 tercihi',policy,'0.00'),('IMST başlığı + seçim katkısı',policy,chosen)]:
        lines.append(f"| {label} | {res['arms'][strength]['dev']['views']['predicted_view_lemma_pos']} | {res['arms'][strength]['calib']['views']['predicted_view_lemma_pos']} |")
    for split in ('dev','calib'):
        data=policy['arms'][chosen][split]; v=data['views']; r=review[split]; reprr=r['representation_only']
        lines += ['',f"### {split.upper()}",'',
            f"Son sözlüksel lemma+tür: {v['predicted_view_lemma_pos']}/{v['words']} = %{100*v['predicted_view_lemma_pos']/v['words']:.4f}. Beyan edilen sekiz özellik alanıyla birlikte {v['predicted_view_features']}/{v['words']}.",'',
            f"Yalnız temsil katmanı: {reprr['fixed']} eşleşme düzeldi, {reprr['regressed']} gerileme oldu; net {reprr['fixed']-reprr['regressed']:+d}. Aynı IMST başlığıyla aday seçimi açılınca ilave {r['view_lemma_pos']['fixed']} düzelen / {r['view_lemma_pos']['regressed']} bozulan sözlüksel tercih var; net {r['view_lemma_pos']['net']:+d}.",'',
            f"Eski kök+tür ölçütünde P1’e göre {r['native_lemma_pos']['fixed']} düzelen / {r['native_lemma_pos']['regressed']} bozulan kayıt; net {r['native_lemma_pos']['net']:+d}. {r['changed_native_analysis_ids']} sözcüğün seçilen morfolojik aday kimliği değişti.",'',
            f"Doğru cevap herhangi bir görünümde {v['oracle_view_lemma_pos']}/{v['words']} sözcük için bulunuyor. Bu seçilmiş doğruluk değildir; görünüm havuzunun kapsamasıdır. Yeni morfolojik yol üretilmedi."]
    lines += ['', '## Sonucun kapsamı', '',
        'Eski lemma alanı başlangıç köküdür; yeni görünüm türemiş sözlüksel lemmayı ayrıca bildirebilir. Bu iki çıktı türündeki puanları tek bir morfolojik doğruluk artışı gibi toplamak doğru değildir. Görünüm başlığı tek bir seçenek tahmin eder; bütün seçeneklerden referansa uyanı sonradan seçerek başarı hesaplanmadı.', '',
        'Yeni özellik ölçüsü VerbForm, Polarity, Voice, Person[psor], Number[psor], Case, Number ve Person alanlarını denetler. Case/Number/Person yeni ölçüde ADJ/NUM üzerinde de denetlenir. Bu kapsam eski özellik ölçüsünden farklıdır; tam ek yolu, Tense/Aspect/Mood kapsamı veya bütün anlam doğruluğu değildir.', '',
        'IMST politikası, bu veri kaynağındaki lemma/tür geleneğine yönelik açık bir çıktı politikasıdır. Bütün Türkçe metinlerde evrensel tür doğruluğu gibi sunulmaz. DEV ve CALIB geliştirmede görülmüştür; yeni bağımsız test değildir. TEST bu çalışmada açılmadı. %92 morfolojik doğruluk veya <%8 fallback hedefi bu sonuçla sağlanmış sayılmaz.', '',
        '## Eğitim ve kontroller', '']
    for label,path in [('Karma',LOCAL/'fit-summary.json'),('IMST',LOCAL/'policy-imst/fit-summary.json')]:
        fit=read(path)
        lines += [f"- {label}: {fit['TRAIN_sentences'] if 'TRAIN_sentences' in fit else fit['training_sentences']} TRAIN cümlesi, {fit['counts']['examples']} karşılaştırmalı örnek, {fit['iterations']} optimizasyon adımı. Yakınsama durumu: {fit['optimizer_success']}; {fit['optimizer_message']}. Eğitim kaybı {fit['initial_loss']:.6f} → {fit['final_loss']:.6f}."]
    roundtrips=sum(d['BPE_roundtrips'] for res in [mixed,policy] for splits in res['arms'].values() for d in splits.values())
    probes=read(LOCAL/'policy-imst/runtime-contracts.json')
    lines += ['', f"{roundtrips} cümle çıktısında BPE geri kurma doğrulandı; 224.309 ID ve 256 bayt davranışı korundu. Beş şema testi ve API kontrolleri geçti. IMST başlığına ait elle yazılmış {probes['authored_probes']} bağlam tanısının {probes['authored_probes_matched']} tanesi beklenen lemma+türle eşleşti; bunlar bağımsız test değildir.", '',
        'Her yeni çözücü çıktısının toplam puanı ayrı yordamla yeniden hesaplandı; aday ve ham metin değişmezliği denetlendi. Sıfır katkılı IMST kontrolü, önceden doğrulanmış P1 kararlarını yeniden kullandı; onun için yeni bir çözücü koşusu yapılmış gibi sayı verilmedi.', '',
        '## Teslim ve tercih', '',
        f"IMST DEV seçimi: **{policy['selected_strength']}**. Tarihsel E05’e göre her iki havuzdaki eski kök+tür, özellik ve yanlış kesin karar gerilememe denetimi: **{policy['historical_E05_nonregression']}**. Yeni sürümün açık kullanım girişi `s06e_p2_policy.Tokenizer(strength={policy['selected_strength']})`; eski proje varsayılanı değiştirilmedi.", '',
        'Kaynak, modeller ve yeni özel çıktılar V üzerinde iki ek kopyaya kaydedilir. Aynı fiziksel sürücüdeler; önceki dondurulmuş proje tabanı gerekir. GitHub kapsamı kod, test, toplu rapor ve hash kayıtlarıdır. Model ağırlıkları ve ham kaynak cümleleri yayımlanmaz.', '',
        '## Kaynaklar', '',
        '- [UD Türkçe](https://universaldependencies.org/tr/): kaynaklar arasında tür politikası farklılıkları.',
        '- [IMST](https://universaldependencies.org/treebanks/tr_imst/index.html): referans etiket sözleşmesi.',
        '- [Bedir ve arkadaşları, 2021](https://aclanthology.org/2021.law-1.12/): Türkçe türetim ve sıfır biçimbirimlerin temsil sorunları.',
        '- [Hakkani-Tür ve arkadaşları, 2000](https://aclanthology.org/C00-1042/): türetim sınırlarıyla çekim grupları. Buradaki model o makalenin birebir uygulaması değildir.', '']
    text='\n'.join(lines)
    (LOCAL/'final-report.md').write_text(text,encoding='utf-8',newline='\n')
    (ROOT/'S06E-E05-P2-degerlendirmesi.md').write_text(text,encoding='utf-8',newline='\n')
    source=['analysis_schema_p2.py','s06e_p2.py','s06e_p2bpe.py','s06e_p2_policy.py','S06E-E05-P2-degerlendirmesi.md']
    source += [p.relative_to(ROOT).as_posix() for p in sorted(HERE.iterdir()) if p.suffix in {'.py','.json','.md'}]
    public={n:ROOT/n for n in source}
    reports=['comparison.json','fit-summary.json','freeze.json','evaluation-freeze.json','dev-selection-seal.json',
        'unit-contracts.json','runtime-contracts.json','change-review.json','final-report.md',
        'policy-imst/comparison.json','policy-imst/fit-summary.json','policy-imst/freeze.json',
        'policy-imst/evaluation-freeze.json','policy-imst/dev-selection-seal.json','policy-imst/runtime-contracts.json']
    public.update({PREFIX+'/'+n:LOCAL/n for n in reports})
    for n in ['model-location.json','policy-imst/model-location.json']:
        public['results_lexical_p2/'+n]=LOCAL/n
    payload={'source/'+n:p for n,p in public.items()}
    payload.update({'private/'+p.relative_to(DEST).as_posix():p for p in DEST.rglob('*') if p.is_file()})
    payload.update({'reports/'+p.relative_to(LOCAL).as_posix():p for p in LOCAL.rglob('*') if p.is_file()})
    payload['models/a1-e05-ranker.json']=PARENT/'A1/selected-ranker.json'
    payload['models/a3-e00-ranking.json']=PARENT/'A3/selected-ranking.json'
    hashes={n:digest(p) for n,p in payload.items()}
    require(shutil.disk_usage(DEST).free>2*sum(p.stat().st_size for p in payload.values())+5*1024**3,'P2_BACKUP_SPACE')
    base=DEST/'snapshots'; require(not base.exists(),'P2_BACKUPS_ALREADY_EXIST')
    for copy in ['copy-a','copy-b']:
        for n,p in payload.items():
            target=base/copy/n; require(target.resolve().is_relative_to((base/copy).resolve()),'P2_UNSAFE_COPY')
            target.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(p,target)
            require(digest(target)==hashes[n],'P2_COPY_HASH_MISMATCH')
        atomic_json(base/copy/'sha256.json',hashes)
    receipt={'status':'TWO_V_INCREMENTAL_COPIES_VERIFIED','files_per_copy':len(hashes),'directory':str(base),
        'same_physical_drive':True,'requires_frozen_project_base':True,'sha256':hashes}
    atomic_json(LOCAL/'backup-receipt.json',receipt); atomic_json(DEST/'backup-receipt.json',receipt)
    for copy in ['copy-a','copy-b']: atomic_json(base/copy/'backup-receipt.json',receipt)
    public[PREFIX+'/backup-receipt.json']=LOCAL/'backup-receipt.json'
    outbox={'repository':'ozelturktarkan/TurkTokenizer','branch':'codex/s06e-e05-p1-phonology',
        'base_commit':'d6ac73c55e4fc3603b8cbb3cd69cfa4df1f6e69d',
        'files':{n:{'local_path':str(p),'sha256':digest(p),'bytes':p.stat().st_size} for n,p in public.items()},
        'raw_corpus_or_model_weights_published':False}
    atomic_json(LOCAL/'github-outbox.json',outbox)
    print(json.dumps({'status':'P2_READY_FOR_GITHUB','public_files':len(public),'backup_files_per_copy':len(hashes),
        'selected_strength':policy['selected_strength'],'historical_E05_nonregression':policy['historical_E05_nonregression']},ensure_ascii=False),flush=True)


if __name__=='__main__': main()
