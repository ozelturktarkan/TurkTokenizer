"""Report both layers, preserve prior runs, verify two incremental snapshots."""
import json
import shutil
from s06e_p4 import load_selected,Codec
from .common import ROOT,DEST,LOCAL,HERE,read,digest,atomic_json,require,original_freeze


def main():
    require(not (DEST/'snapshots').exists(),'P4_REFUSE_OVERWRITE_SNAPSHOTS')
    comp=read(LOCAL/'comparison.json');a2=read(LOCAL/'calibration.json');selection=read(LOCAL/'selection.json')
    require(comp['status']=='EXPERIMENT_COMPLETE' and a2['status']=='A2_VERIFIED','P4_INCOMPLETE')
    frozen=read(LOCAL/'evaluation-freeze.json')
    require(all(digest(ROOT/n)==h for n,h in frozen['source_sha256'].items()),'P4_FINAL_SOURCE_CHANGED')
    cache_freeze=read(LOCAL/'cache-freeze-r1.json')
    require(all(digest(ROOT/n)==h for n,h in cache_freeze['source_sha256'].items()),'P4_REGISTERED_PROTOCOL_OR_CACHE_SOURCE_CHANGED')
    require(digest(DEST/'model.json')==selection['model_sha256'],'P4_FINAL_MODEL_CHANGED');parents=original_freeze()
    rt=load_selected();codec=Codec(**selection['configuration'],a2=selection['A2_config']);codec.native=rt
    smoke=['Sen geliyor musun?','Mi notasını çaldım.','Okula doğru yürüdü.','Kod: `x = 1`\nqzx_123 😊']
    for text in smoke:
        out=rt.analyze_sentence(text);require(codec.decode(codec.encode_from_analysis(out)['input_ids'])==text,'P4_SELECTED_API_ROUNDTRIP')
    head=read(LOCAL/'head-selection.json');hf=read(LOCAL/'head-fit-summary.json');rf=read(LOCAL/'rank-fit-summary.json')
    name=comp['retained'];devname=comp['DEV_selected'];final=comp['arms'][name];base=comp['arms']['P2']
    def pct(k,n):return f'{100*k/n:.2f}'.replace('.',',')
    lines=['# S06E P4: iki seçim katmanının ayrı onarımı','',
           f"DEV seçimi **{devname}**; CALIB koruma denetimi sonrası tutulan yapı **{name}**. Varsayılan eski sürüm otomatik değiştirilmedi.",
           '', '## Ne değişti?', '',
           'Çıktı başlığı, aynı morfolojik adayın görünümleri arasında koşullu bir seçim öğreniyor. Bu başlık tek başına değiştiğinde morfolojik aday, cümle puanı, eski güven kararı ve BPE ID’leri aynı kalıyor.',
           'Sıralayıcı, eski P2 tam cümle max-marjinal puanlarını eğitimde sabit başlangıç puanı olarak kullanıyor. Pozitif etiket yalnızca başlığın gerçekten yayımladığı görünüm referansla uyumluysa veriliyor; aday içindeki seçilmeyen gizli bir doğru görünüm yeterli sayılmıyor.',
           'Eski ve yeni başlık için aynı rekabetçi TRAIN sözcüklerinde ayrı sıralayıcılar eğitildi. Yeni sıralama katkısı yalnız son ana geçişe ekleniyor; Q0 ve UA referans geçişleri, eski P2 puan başlığı, AB04 ve n-gram ağırlıkları korunuyor.',
           '', '## Çıktı başlığı tek başına: DEV', '',
           '| Başlık katkısı | Görünüm kök+tür /4070 | Görünüm özellik |', '|---|---:|---:|']
    for key,r in head['arms'].items():lines.append(f"| {key} | {r['views']['predicted_view_lemma_pos']} | {r['views']['predicted_view_features']} |")
    lines += ['',f"Başlık seçimi {head['head_strength']}; bu koşullarda yerel kök+tür 3174, yerel özellik 3045, yanlış kesin karar 595 olarak aynen kaldı.",
              '', '## Tam çözücü: DEV', '',
              '| Koşul | Yerel kök+tür | Yerel özellik | Yanlış kesin | Görünüm kök+tür | Görünüm özellik | Koruma |',
              '|---|---:|---:|---:|---:|---:|---|']
    for key,runs in comp['arms'].items():
        r=runs['dev'];l=r['legacy'];v=r['views']
        lines.append(f"| {key} | {l['preferred_lemma_pos']} | {l['preferred_declared_features']} | {l['legacy_selected_lemma_wrong']} | {v['predicted_view_lemma_pos']} | {v['predicted_view_features']} | {'Geçti' if key=='P2' or r['P2_nonregression'] else 'Geçmedi'} |")
    lines+=['','H: yalnız yeni başlık. R: eski başlıkla hizalı yeni sıralayıcı. HR: yeni başlıkla hizalı yeni sıralayıcı. R/HR sonundaki sayı, öğrenilen sıralama katkısının katsayısıdır.',
            'DEV paydası 4.070 sözcük / 293 cümle. Başlık seçimi ve sıralama seçimleri DEV ile yapıldı. Yeni bağımsız test sonucu değildir.',
            '', '## Mühürlenmiş CALIB denetimi', '',
            'CALIB’de yalnız P2 kontrolü ve DEV’de seçilmiş tek yapı karşılaştırıldı; diğer kollar CALIB’ye göre yeniden seçilmedi.',
            '', '| Koşul | Yerel kök+tür /2266 | Yerel özellik | Yanlış kesin | Görünüm kök+tür | Görünüm özellik |',
            '|---|---:|---:|---:|---:|---:|']
    for key in dict.fromkeys(['P2',devname]):
        r=comp['arms'][key]['calib'];l=r['legacy'];v=r['views']
        lines.append(f"| {key} | {l['preferred_lemma_pos']} | {l['preferred_declared_features']} | {l['legacy_selected_lemma_wrong']} | {v['predicted_view_lemma_pos']} | {v['predicted_view_features']} |")
    n=sum(final[s]['views']['words'] for s in ('dev','calib'));v=sum(final[s]['views']['predicted_view_lemma_pos'] for s in ('dev','calib'))
    native=sum(final[s]['legacy']['preferred_lemma_pos'] for s in ('dev','calib'));bv=sum(base[s]['views']['predicted_view_lemma_pos'] for s in ('dev','calib'))
    lines += ['',f"Korunan yapının DEV+CALIB görünüm kök+tür başarısı **{v}/{n} = %{pct(v,n)}**; P2 {bv}/{n}. Ayrı yerel başlangıç kökü+tür ölçütü **{native}/{n} = %{pct(native,n)}**. Bu iki ölçüt birbirinin yerine kullanılmamalı."]
    committed=sum(final[s]['legacy']['legacy_selected'] for s in ('dev','calib'));oldcommitted=sum(base[s]['legacy']['legacy_selected'] for s in ('dev','calib'))
    wrong=sum(final[s]['legacy']['legacy_selected_lemma_wrong'] for s in ('dev','calib'));oldwrong=sum(base[s]['legacy']['legacy_selected_lemma_wrong'] for s in ('dev','calib'))
    lines += [f"Eski kesin karar sayısı {oldcommitted}, yeni {committed}; yanlış kesin karar {oldwrong} → {wrong}. Karar vermekten kaçınma da değişebildiği için yanlış kesin karardaki azalmanın tamamı düzeltilen hata olarak sayılmıyor. Gerçek tercih düzeltmeleri aşağıdaki eşlenmiş karşılaştırmada ayrı gösteriliyor."]
    paired={}
    if name!='P2':
        for metric in ('preferred_lemma_pos','preferred_declared_features','predicted_view_lemma_pos','predicted_view_features'):
            paired[metric]={k:sum(final[s]['paired'][metric][k] for s in ('dev','calib')) for k in ('fixed','regressed')}
        lines+=['','| Ölçüt | Düzeltilen eski hata | Yeni gerileme |','|---|---:|---:|']
        for k,r in paired.items():lines.append(f"| {k} | {r['fixed']} | {r['regressed']} |")
    reach=read(LOCAL/'reachable-output-audit.json')['combined']
    lines += ['', '## Kalan iki seçim katmanı', '',
              f"- Yeniden sıralamayla erişilebilir yanlış çıktı: **{reach.get('wrong_but_reachable_by_native_reranking',0)}** (P2: 518).",
              f"- Doğru görünüm var, fakat hiçbir adayda başlığın tepe seçimi değil: **{reach.get('view_exists_but_fixed_head_blocks_every_native_choice',0)}** (P2: 55).",
              f"- Eşleşen görünüm yok veya referans çözülemiyor: **{reach.get('no_matching_view_or_unresolved',0)}** (P2: 537).",
              f"- Sabit adaylarda herhangi bir görünüm kapsamı {reach['inventory_view_oracle']}/{n}; seçili başlıkla erişilebilir kapsam {reach['fixed_head_reachable_oracle']}/{n}. Bunlar motorun fiziksel veya evrensel doğruluk tavanı değildir.",
              '',
              'Başlığın bütün adaylarda doğru görünümü geri plana attığı hata grubundaki artış bir gerilemedir. Sıralamayla erişilebilir yanlışlar grubundaki azalmanın tamamı çözülmüş hata değildir; bazı vakalar başlık engeli grubuna geçmiştir. Toplam tercih kazanımı eşlenmiş karşılaştırmayla ölçülmelidir. P4 iki katmanı tamamen onarmış sayılmaz.',
              'Sonraki başlık deneyinde yalnız seçilmiş çıktı başarısını değil, doğru görünümün adaylar arasında erişilebilir kalmasını da koruyan bir eğitim hedefi sınanmalı. Bu tanıya göre mevcut DEV/CALIB seçimi veya ağırlıkları yeniden ayarlanmadı.',
              '', '## A2 ve doğrulama', '']
    for key,r in a2['arms'].items():
        b=r['selected']
        lines.append(f"- {key}: kabul {b['accepted']}/{b['words']}, yerel kök+tür %{b['lemma_precision_pct']:.2f}, tanımlı özellik %{b['feature_precision_pct']:.2f}." if b else f'- {key}: önceden belirlenen 121 eşik çiftinde iki ölçütte birlikte %92 sağlanamadı.')
    lines += ['',f"Başlık: {hf['counts']['competitive_words']} sözcük, {hf['fit']['examples']} aday içi örnek. Sıralama: her iki modelde aynı {rf['counts']['common_competitive_words']} TRAIN sözcüğü. Toplam TRAIN 3.260 IMST cümlesi. DEV/CALIB/TEST etiketleri kayıp fonksiyonuna girmedi.",
              'Başlıkta her sözcüğün toplam eğitim ağırlığı eşit tutuldu. Sıralama kaybı, dondurulmuş cümle marjinal puanları üzerinde yerel bir yaklaştırmadır; ortak CRF azami olabilirlik eğitimi olarak sunulmuyor. Son kararlar gerçek tam çözücüyle tekrar ölçüldü.',
              'Sıfır katkı ve başlık-only ayrımı 18 cümlede, BPE geri dönüşü 19 kontrolde doğrulandı. Aday sırası, etiket sızıntısı, yayımlanan görünümle pozitif etiket uyumu ve A2’nin tek geçişte uygulanması kontrol edildi. Ağırlıklı kaybın türevi sayısal sonlu farkla ve puan kaydırma değişmezliğiyle doğrulandı.',
              'Her yeni tam çözücü çıktısında bağımsız puan toplamı, aday havuzu ve metin geri dönüşü doğrulandı. 224.309 BPE/morfoloji ID’si aynı kaldı.',
              'İlk puan önbelleği denemesi boş bilinmeyen işaretini gerçek adayla karşılaştıran kontrol hatasında durdu; kayıt ve betik saklandı. Düzeltmeden sonra 3.260 cümlenin tamamı cache-r1 içinde yeniden doğrulandı.',
              'Tam morfem yolu doğruluğu ve görünüm başlığının kalibre güveni bu ölçümlerle kanıtlanmıyor. TEST açılmadı; %92 morfolojik kapsama ve <%8 fallback hedefleri otomatik sağlanmış sayılmaz.']
    probes=read(LOCAL/'postfit-probes.json')
    lines+=['','Tanısal 15 örnek (seçim veya yeniden eğitimde kullanılmadı): '+', '.join(f"{k}: {r['matched']}/15" for k,r in probes['arms'].items())+'.',
            f"“Sen geldin mi?” örneğinde doğru soru adayının kazanana puan uzaklığı P2'de {probes['arms']['P2']['question_scores']['gap_below_winner']:.2f}, seçili yapıda {probes['arms'][name]['question_scores']['gap_below_winner']:.2f}. Uzaklığın azalması doğru seçimin yapıldığı anlamına gelmez; bu örnek hâlâ çözülemedi.",
            '', '## Kullanım ve kayıtlar', '',
            '`from s06e_p4 import load_selected; rt = load_selected(); out = rt.analyze_sentence("Sen geldin mi?")`',
            '', 'Model: `results_layers_p4/model-location.json`. Seçim: `results_layers_p4/selection.json`. Tam karşılaştırma: `results_layers_p4/comparison.json`. Yedek doğrulaması: `results_layers_p4/backup-receipt.json`.',
            'İki V kopyası artımlıdır ve aynı fiziksel sürücüdedir; eski proje tabanına ihtiyaç duyar. P2/P3 kaynakları ve sonuçları değişmedi. Yeni GitHub yayını yapılmadı; önceki P2 paketinin kapsam onayı ayrı olarak bekliyor.']
    report=ROOT/'S06E-P4-Iki-Secim-Katmani-degerlendirmesi.md';report.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    continuation=ROOT/'DEVAM-NOKTASI-P4.md'
    continuation.write_text(f'''# P4 devam noktası

İki seçim katmanı ayrı eğitildi ve tam çözücüde ölçüldü.
DEV seçimi: {devname}. CALIB sonrası tutulan: {name}. Varsayılan yükseltme yok; TEST açılmadı.
Başlık-only H, eski başlıkla R ve yeni başlıkla HR ayrı karşılaştırıldı.
Model ve sonuç dizini: {DEST}
Özet: S06E-P4-Iki-Secim-Katmani-degerlendirmesi.md
API: s06e_p4.load_selected(with_a2=True). Seçim: results_layers_p4/selection.json.
Başarısız ilk önbellek kaydı korunuyor; geçerli tam cache cache-r1 altında.
P2/P3 dondurulmuş kodu, modelleri ve raporları değişmedi. GitHub P2 kapsam onayı hâlâ bekliyor; P4 yayımlanmadı.
''',encoding='utf-8')
    sources=[ROOT/'features_p4.py',ROOT/'s06e_p4.py',report,continuation]
    sources += [p for p in HERE.iterdir() if p.suffix in {'.py','.json','.md'}]
    sources += [p for p in LOCAL.iterdir() if p.is_file()]
    for p in sources:
        dest=DEST/'source'/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
        require(digest(p)==digest(dest),'P4_SOURCE_COPY_FAILED')
    files=[p for p in DEST.rglob('*') if p.is_file()];hashes={p.relative_to(DEST).as_posix():digest(p) for p in files}
    require(shutil.disk_usage(DEST).free>2*sum(p.stat().st_size for p in files)+1_000_000_000,'P4_BACKUP_SPACE_LOW')
    for copy_name in ('copy-a','copy-b'):
        target=DEST/'snapshots'/copy_name
        for p in files:
            dest=target/p.relative_to(DEST);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
        require(all(digest(target/n)==h for n,h in hashes.items()),'P4_BACKUP_HASH_MISMATCH')
        atomic_json(target/'snapshot-sha256.json',hashes)
    receipt={'status':'DOUBLE_SNAPSHOT_SHA256_VERIFIED','files_per_copy':len(hashes),'sha256':hashes,
             'copies':[str(DEST/'snapshots'/n) for n in ('copy-a','copy-b')],'same_physical_drive':True,
             'incremental_requires_parent_project':True,'parent_freezes':parents,'selected_API_roundtrips':len(smoke)}
    atomic_json(LOCAL/'backup-receipt.json',receipt);atomic_json(DEST/'backup-receipt.json',receipt)
    print(json.dumps({k:v for k,v in receipt.items() if k!='sha256'}),flush=True)


if __name__=='__main__':main()
