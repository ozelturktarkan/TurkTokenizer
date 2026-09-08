"""Aggregate transparent results and make two verified incremental V snapshots."""
import json
import shutil
from pathlib import Path
from s06e_p3 import load_selected,Codec
from .common import ROOT,DEST,LOCAL,HERE,read,digest,atomic_json,require,original_freeze
from .evaluate import clear


def main():
    require(not (DEST/'snapshots').exists(),'P3_REFUSE_OVERWRITE_SNAPSHOTS')
    comp=read(LOCAL/'comparison.json');a2=read(LOCAL/'calibration.json');selected=read(LOCAL/'selection.json')
    require(comp['status']=='EXPERIMENT_COMPLETE' and a2['status']=='A2_VERIFIED','P3_INCOMPLETE')
    frozen=read(LOCAL/'evaluation-freeze.json')
    require(all(digest(ROOT/n)==h for n,h in frozen['source_sha256'].items()),'P3_FINAL_SOURCE_CHANGED')
    require(digest(DEST/'model.json')==selected['model_sha256'],'P3_FINAL_MODEL_CHANGED')
    original=original_freeze();rt=load_selected();codec=Codec(selected['configuration'],a2=selected['A2_config']);codec.native=rt
    smoke=['Sen geliyor musun?','Mi notasını çaldım.','Okula doğru yürüdü.','Kod: `x = 1`\nYabancı: qzx_123 😊']
    for text in smoke:
        out=rt.analyze_sentence(text)
        require(codec.decode(codec.encode_from_analysis(out)['input_ids'])==text,'P3_SELECTED_API_ROUNDTRIP')
    clear(rt)
    names=read(HERE/'protocol.json')['DEV_arms'];name=selected['configuration'];devchosen=comp['DEV_selected']
    def pct(n,d):return f'{100*n/d:.2f}'.replace('.',',')
    lines=['# S06E P3: YÖNT / 5N1K dilbilgisel özellik deneyi','',
           f"DEV seçimi **{devchosen}**; CALIB denetimi sonrası korunan yapı **{name}**. Varsayılan sürüm otomatik değiştirilmedi.",
           '', '## Sabit adaylarla DEV karşılaştırması', '',
           '| Koşul | Yerel kök+tür | Yerel özellik | Yanlış kesin kök+tür | Sözcüksel görünüm kök+tür | Görünüm özellik | P2 koruma koşulu |',
           '|---|---:|---:|---:|---:|---:|---|']
    for n in names:
        r=comp['arms'][n]['dev'];l=r['legacy'];v=r['views']
        lines.append(f"| {n} | {l['preferred_lemma_pos']} | {l['preferred_declared_features']} | {l['legacy_selected_lemma_wrong']} | {v['predicted_view_lemma_pos']} | {v['predicted_view_features']} | {'Geçti' if n=='C0_P2' or r['P2_nonregression'] else 'Geçmedi'} |")
    lines+=['','Payda: 4.070 sözcük / 293 cümle. Sözcüksel görünüm UD_IMST çıktı politikasını kullanır; yerel kök ile ayrı bir ölçüttür.',
            'GOV: istem/edat; AGR: kişi/iyelik/soru; LOCAL_COMBINED: birlikte yerel puan; JOINT_HALF ve JOINT_FULL: seçilmiş adaylar arasındaki etkileşimlerle yarım/tam katkı.',
            '', '## CALIB ve kalan hata', '',
            '| Koşul | Yerel kök+tür | Yerel özellik | Yanlış kesin kök+tür | Görünüm kök+tür | Görünüm özellik |',
            '|---|---:|---:|---:|---:|---:|']
    for n in dict.fromkeys(['C0_P2',devchosen]):
        r=comp['arms'][n]['calib'];l=r['legacy'];v=r['views']
        lines.append(f"| {n} | {l['preferred_lemma_pos']} | {l['preferred_declared_features']} | {l['legacy_selected_lemma_wrong']} | {v['predicted_view_lemma_pos']} | {v['predicted_view_features']} |")
    base=comp['arms']['C0_P2'];final=comp['arms'][name]
    n=sum(final[s]['views']['words'] for s in ('dev','calib'));correct=sum(final[s]['views']['predicted_view_lemma_pos'] for s in ('dev','calib'))
    old=sum(base[s]['views']['predicted_view_lemma_pos'] for s in ('dev','calib'));oracle=sum(final[s]['views']['oracle_view_lemma_pos'] for s in ('dev','calib'))
    reach=read(LOCAL/'reachable-output-audit.json')['combined']
    lines+=['',f'CALIB paydası 2.266 sözcük / 382 cümle. Korunan yapının iki havuzdaki görünüm kök+tür başarısı **{correct}/{n} = %{pct(correct,n)}**; P2 {old}/{n}.',
            f'Doğru görünüm adayda mevcut fakat seçilememiş: **{oracle-correct}**. Görünüm eşleşmesi bulunmayan veya çözülemeyen referans: **{n-oracle}**. Sabit çıktı sözleşmesinde aday kapsamı {oracle}/{n}; bu oran dilbilgisi motorunun fiziksel tavanı değildir.',
            f"Ek çıktı denetimi: **{reach.get('wrong_but_reachable_by_native_reranking',0)}** yanlış, başka bir yerel aday seçilerek doğru görünüme ulaşabilir. **{reach.get('view_exists_but_fixed_head_blocks_every_native_choice',0)}** örnekte doğru görünüm vardır fakat dondurulmuş görünüm başlığı hiçbir adayda onu tepeye koymaz. Bu ikinci grup yalnız yerel adayları yeniden sıralamakla çözülemez. Sabit başlıkla erişilebilir çıktı kapsamı **{reach['fixed_head_reachable_oracle']}/{n} = %{pct(reach['fixed_head_reachable_oracle'],n)}**.",
            '', '## A2: karar verme doğruluğu ve kapsamı ayrı', '']
    for key,r in a2['arms'].items():
        b=r['selected']
        if b:
            lines.append(f"- {key}: {b['accepted']}/{b['words']} kabul (%{pct(b['accepted'],b['words'])} kapsam), kabul edilenlerde yerel kök+tür %{b['lemma_precision_pct']:.2f}, tanımlı özellik %{b['feature_precision_pct']:.2f}; eşikler {b['thresholds']}.")
        else:lines.append(f'- {key}: önceden belirlenmiş 121 eşik çiftinde iki ölçütte birlikte %92 hedefi sağlanamadı.')
    lines+=['','Bu kalibrasyon, kabul edilen alt kümenin CALIB üzerindeki ampirik doğruluğudur. Tüm sözcüklerin %92’sini doğru çözme, tam morfem yolu doğruluğu veya görünüm başlığının kalibre edilmiş güveni anlamına gelmez. DEV ve CALIB daha önce görülmüş havuzlardır; bağımsız genelleme kanıtı değildir. TEST bu deneyde açılmadı.',
            '', '## Eğitim ve doğrulama', '']
    prep=read(LOCAL/'prepare-summary.json');rank=read(LOCAL/'ranking-summary.json');local=read(LOCAL/'local-fit-summary.json')
    lines += [f"- 3.260 IMST TRAIN cümlesi; {prep['counts']['local_examples']} rekabetçi yerel örnek. Yeni insan etiketlemesi yapılmadı; mevcut referansla uyumlu alternatifler birlikte pozitif tutuldu.",
              f"- A3: {rank['TRAIN_contexts']} sabit TRAIN bağlamı, {rank['TRAIN_targets']} hedef; her üç aile için iki madencilik/eğitim turu. Eski UA/AB04/N-gram beşli ağırlıkları 1 olarak sabit kaldı.",
              '- İstem tercihleri, TRAIN’de gözlenen fiil/ses çatısı ve tümleç durumlarından öğrenildi; kapsamlı anlam bazlı istem sözlüğü oldukları varsayılmadı. Aday silme yapılmadı.',
              '- Uzun bağlantılar yalnızca önceki planlayıcının tuttuğu kısmi planlar üzerinde puanlandı. Bu çalışma, daha önce budanmış planları geri getirmez; tam cümle sözdizimi çözümleyicisi değildir.',
              '- Yedi birim testi, küçük zincirde kaba kuvvetle tam DP/marj eşitliği, 15 cümlede sıfır katkının P2’ye eşitliği ve aday sırası değişmezliği kontrol edildi.',
              '- Her yeni değerlendirme çıktısında aday havuzu, bağımsız puan toplamı, ham metin ve BPE geri dönüşü denetlendi. 224.309 eski ID korundu. Seçilen API ile ek dört geri dönüş kontrolü geçti.',
              '- Vurgu/sözcük sırası paketi bu ilk dar deneyin kapsamı dışında tutuldu.']
    post=read(LOCAL/'postfit-probes.json')
    post['arms'].update(read(LOCAL/'exploratory-probes.json')['arms'])
    diagnosis=read(LOCAL/'feature-diagnostics.json')['arms']['JOINT_FULL']
    lines += ['',f"Birleşik kolun son eğitimden önceki 338 sabit karşıtında {diagnosis['wrong_at_round_1_mining']} yanlış tercih vardı; bunların {diagnosis['wrong_and_indistinguishable']} tanesinde yeni özellik farkı tamamen sıfırdı. Bu karşıtlarda yalnız bu 26 bileşenin ağırlığını değiştirmek ayrım üretemez. Bu bir TRAIN tanısıdır, test doğruluğu değildir."]
    lines+=['', 'Tanısal, bağımsız olmayan 15 örnek: '+', '.join(f"{k} {v['matched']}/15" for k,v in post['arms'].items())+'. Bu sonuçlar seçim veya yeniden eğitim için kullanılmadı.',
            '', '## Dosyalar ve devam', '',
            '- `results_grammar_p3/comparison.json`: tüm karşılaştırmalar ve düzelme/gerileme sayıları.',
            '- `results_grammar_p3/calibration.json`: eşikler, kabul kapsamı, Wilson aralıkları ve çevrimiçi doğrulama.',
            '- `results_grammar_p3/model-location.json`: V üzerindeki model ve SHA256.',
            '- `results_grammar_p3/backup-receipt.json`: iki artımlı V kopyasının doğrulama kaydı.',
            '- Kullanım: `from s06e_p3 import load_selected; rt = load_selected(); rt.analyze_sentence("Sen geliyor musun?")`.',
            '- Eski P2 kodu/modeli ile önceki dondurulmuş 47 dosya değişmedi. Bu P3 paketi eski proje tabanına ihtiyaç duyan artımlı bir deneydir.',
            '- GitHub’a yeni yayın yapılmadı; önceki P2 dosya paketi için otomatik onay denetiminin istediği kapsam onayı hâlâ bekliyor.',
            '', 'Kaynak ve araştırma gerekçesi: `research/2026-09-09-yont-5n1k/arastirma.md`.']
    question=read(LOCAL/'question-score-audit.json')
    gaps=question['arms']
    lines+=['','## Soru/nota örneğinde puan kanıtı','',
            f"`Sen geldin mi?` cümlesinde doğru soru adayı mevcut. Tutulan aramadaki en iyi soru yolunun kazanana uzaklığı P2’de {gaps['C0_P2']['best_question_gap_below_winner']:.4f}, yarım katkıda {gaps['JOINT_HALF']['best_question_gap_below_winner']:.4f}, tam katkıda {gaps['JOINT_FULL']['best_question_gap_below_winner']:.4f} puan. Yeni katkı farkı daralttı fakat tercihi çevirmedi. Bu örnek için adayın atlanması açıklaması desteklenmiyor. Ayrıntı: `results_grammar_p3/question-score-audit.json`."]
    (ROOT/'S06E-P3-YONT-degerlendirmesi.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    (ROOT/'DEVAM-NOKTASI-P3.md').write_text(f'''# P3 devam noktası

Tamamlandı: A1 yerel dilbilgisi, A3 iki tur sıralama, altı DEV kolu, DEV sonrası mühürlenmiş CALIB denetimi ve A2.
DEV seçimi: {devchosen}. Korunan yapı: {name}. Varsayılan yükseltme yok. TEST açılmadı.
Özet: S06E-P3-YONT-degerlendirmesi.md; sayısal kayıt: results_grammar_p3/comparison.json.
Çalışma dizini: {DEST}
API: s06e_p3.load_selected(with_a2=True); kalibrasyonsuz sıralama için False.
GitHub P2 yayın onayı ayrı ve beklemede; P3 henüz yayımlanmadı. Eski dosyaları yeniden yazma.
Sonraki ilerlemede bu sonuçları sakla; aynı DEV/CALIB tekrarlarını bağımsız test diye sunma.
''',encoding='utf-8')
    sources=[ROOT/n for n in ('grammar_p3.py','decoder_p3.py','s06e_p3.py','S06E-P3-YONT-degerlendirmesi.md','DEVAM-NOKTASI-P3.md')]
    sources += [p for p in HERE.iterdir() if p.suffix in {'.py','.json','.md'}]
    sources += [p for p in (ROOT/'research/2026-09-09-yont-5n1k').iterdir() if p.is_file()]
    sources += [p for p in LOCAL.iterdir() if p.is_file()]
    for p in sources:
        dest=DEST/'source'/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
        require(digest(p)==digest(dest),'P3_SOURCE_COPY_FAILED')
    files=[p for p in DEST.rglob('*') if p.is_file()]
    required=2*sum(p.stat().st_size for p in files)+1_000_000_000
    require(shutil.disk_usage(DEST).free>required,'P3_BACKUP_SPACE_LOW')
    hashes={p.relative_to(DEST).as_posix():digest(p) for p in files}
    for name_ in ('copy-a','copy-b'):
        folder=DEST/'snapshots'/name_
        for p in files:
            dest=folder/p.relative_to(DEST);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
        require(all(digest(folder/n)==h for n,h in hashes.items()),'P3_SNAPSHOT_HASH_FAILED')
        atomic_json(folder/'snapshot-sha256.json',hashes)
    receipt={'status':'DOUBLE_SNAPSHOT_SHA256_VERIFIED','files_per_copy':len(hashes),'sha256':hashes,
             'copies':[str(DEST/'snapshots'/n) for n in ('copy-a','copy-b')],'same_physical_drive':True,
             'incremental_requires_parent_project':True,'original_freeze':original,'selected_API_roundtrips':len(smoke)}
    atomic_json(LOCAL/'backup-receipt.json',receipt);atomic_json(DEST/'backup-receipt.json',receipt)
    print(json.dumps({k:v for k,v in receipt.items() if k!='sha256'}),flush=True)


if __name__=='__main__':main()
