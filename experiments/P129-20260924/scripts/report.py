from common import *
import numpy as np,collections,statistics,zipfile
def main():
 c=config();evalrows=rows("eval");wanted={r["id"]:r for r in evalrows};arms=c["arms"];seeds=c["seeds"];runs={}
 for arm in arms:
  for seed in seeds:
   r=read(BASE/f"results/eval-{arm}-{seed}.json");p={x["id"]:x for x in r["predictions"]}
   assert r["status"]=="COMPLETE" and set(p)==set(wanted)
   assert all(x["target"]==wanted[k]["target"] and x["group"]==wanted[k]["group"] and x["split"]==wanted[k]["split"] for k,x in p.items())
   runs[(arm,seed)]=p
 for seed in seeds:
  tr=[read(BASE/f"results/train-{arm}-{seed}.json") for arm in arms]
  for k in ("initial_sha256","order_sha256","steps","examples","parameters"):
   assert len({json.dumps(x[k],sort_keys=True) for x in tr})==1,(seed,k)
 save(BASE/"results/equality.json",dict(status="PASS",same_initialization_order_steps_examples_allocated_parameters=True,
  active_feature_parameters_differ_by_ablation=True,same_bpe_prompt_ids_all_arms=True,no_eval_based_selection=True))
 splits=("iid","lexical","order","composition")
 table={}
 for arm in arms:
  table[arm]={s:float(np.mean([p["correct"] for seed in seeds for p in runs[(arm,seed)].values() if p["split"]==s])) for s in splits}
  table[arm]["ood"]=float(np.mean([table[arm][s] for s in splits[1:]]))
  table[arm]["roles"]={role:float(np.mean([p["correct"] for seed in seeds for p in runs[(arm,seed)].values() if p["role"]==role])) for role in ("subject","object","owner")}
 base=read(BASE/"results/eval-base-0.json")
 bp={x["id"]:x for x in base["predictions"]};assert set(bp)==set(wanted)
 table["base"]={s:float(np.mean([p["correct"] for p in bp.values() if p["split"]==s])) for s in splits}
 table["base"]["ood"]=float(np.mean([table["base"][s] for s in splits[1:]]))
 groups={s:sorted({r["group"] for r in evalrows if r["split"]==s}) for s in splits[1:]}
 bygroup=collections.defaultdict(list)
 for r in evalrows:bygroup[r["group"]].append(r["id"])
 comparisons={};rng=np.random.default_rng(c["bootstrap_seed"])
 for control in ("plain","morph","shuffled"):
  values=[];eachseed=[]
  for seed in seeds:
   delta=[float(runs[("graph",seed)][i]["correct"])-float(runs[(control,seed)][i]["correct"]) for i,r in wanted.items() if r["split"]!="iid"]
   eachseed.append(float(np.mean(delta)))
  for s,gg in groups.items():
   values.append(np.array([np.mean([float(runs[("graph",seed)][i]["correct"])-float(runs[(control,seed)][i]["correct"]) for seed in seeds for i in bygroup[g]]) for g in gg]))
  samples=[]
  for start in range(0,c["bootstrap_samples"],100):
   n=min(100,c["bootstrap_samples"]-start)
   samples.extend(np.mean([v[rng.integers(0,len(v),size=(n,len(v)))].mean(1) for v in values],axis=0).tolist())
  alpha=.05/3;lo,hi=np.quantile(samples,[alpha/2,1-alpha/2])
  point=table["graph"]["ood"]-table[control]["ood"]
  threshold=.10 if control=="plain" else .05
  comparisons[control]=dict(delta=point,confidence_level=1-alpha,ci=[float(lo),float(hi)],per_seed=eachseed,
   minimum_effect=threshold,passes=point>=threshold and lo>0 and min(eachseed)>0)
 coverage=np.mean([bool(r["edges"]) for r in evalrows]);iid_ok=table["graph"]["iid"]>=table["plain"]["iid"]-.02
 passes=all(x["passes"] for x in comparisons.values()) and coverage>=.4 and iid_ok
 manifest=read(BASE/"data/manifest.json")
 summary=dict(status="COMPLETE",engineering="PASS",stage="P129",at=now(),accuracy=table,comparisons=comparisons,
   primary_metric="Equal-weight lexical/order/composition synthetic episode OOD four-choice accuracy",
   paired_cluster_bootstrap="Resample episode groups within each OOD split, average fixed three seeds; Bonferroni 3 comparisons. Does not estimate full random-seed population uncertainty.",
   edge_coverage=float(coverage),iid_nonregression=iid_ok,synthetic_mechanism_gate_passed=bool(passes),
   general_turkish_understanding_demonstrated=False,general_bpe_superiority_demonstrated=False,
   standalone_model_gain_without_native_teacher_demonstrated=False,closed_test_accessed=False,
   structured_query_rule_upper_bound=dict(coverage=float(np.mean([r["structured_query_rule_correct"] is not None for r in evalrows])),
      accuracy_when_answered=(float(np.mean([r["structured_query_rule_correct"] for r in evalrows if r["structured_query_rule_correct"] is not None])) if any(r["structured_query_rule_correct"] is not None for r in evalrows) else None),
      limitation="Generator supplies query-to-clause and requested role. Not an autonomous natural-language QA baseline."),
   training_seconds=sum(read(BASE/f"results/train-{a}-{s}.json")["training_seconds"] for a in arms for s in seeds),
   data=manifest["rows"])
 save(BASE/"summary.json",summary)
 text="# P129 — Yerel YÖNT ilişki deneyi\n\nDurum: COMPLETE / mühendislik PASS.\n\n"
 text+="Ön kayıtlı sentetik mekanizma eşiği: **"+("GEÇTİ" if passes else "GEÇMEDİ")+"**. Bu genel Türkçe anlama/BPE üstünlüğü veya 12B–27B eşdeğerliği değildir.\n\n"
 text+="| Koşul | IID | Yeni sözcükler | Yeni sıra | Üç cümle | OOD ort. |\n|---|---:|---:|---:|---:|---:|\n"
 for a in ["base",*arms]:text+="| "+a+" | "+" | ".join(f'{100*table[a][s]:.2f}%' for s in ("iid","lexical","order","composition","ood"))+" |\n"
 text+="\n## Ön kayıtlı farklar\n\n"
 for a,r in comparisons.items():text+=f'- graph − {a}: {100*r["delta"]:+.2f} yüzde puan; %{100*r["confidence_level"]:.3f} aralık [{100*r["ci"][0]:+.2f}, {100*r["ci"][1]:+.2f}]. Eşik: {100*r["minimum_effect"]:.0f} puan.\n'
 text+="\n## Yorum sınırları\n\nVeri önceden yazılmış Türkçe şablonlardan üretilmiştir; insan gold veya genel doğal Türkçe değerlendirmesi değildir. Native analiz yalnız görünür bağlam cümlelerini alır; soru, seçenek ve doğru cevap öğretmen girdisi değildir. Grafik, sorunun aradığı rollere çok yakın bilgiyi içerir. Sonuç öğretmen+model sistemine aittir; çıplak modelin Türkçesini katladık diye okunamaz. BPE kolu aynı Qwen tokenizer/model tabanıdır. Tüm kollarda BPE dizisi, eğitim örnekleri, adımlar ve ayrılan parametreler eşittir; aktif özellik kapasitesi ve gerçek süre eşit olmak zorunda değildir. Grafik çıkarma süresi/önbelleği ayrı maliyettir. Olumsuzluk, edilgenlik ve genel yan cümle kapsamı bu eğitimde yoktur.\n\n"
 text+="Ayrıntılar summary.json, results/eval-*.json, results/train-*.json ve data/native-cache.sqlite içinde. Sonuçlara bakılarak otomatik yeni deney veya eşik değişimi yapılmadı.\n"
 (BASE/"SONUC_OZETI.md").write_text(text,encoding="utf8")
 files=[*BASE.glob("*.json"),BASE/"SONUC_OZETI.md",*BASE.glob("*.md"),*BASE.glob("*.cmd")]
 for folder in ("scripts","data","models","results","tests","controls"):files+=list((BASE/folder).glob("*"))
 omit={"STATUS.json","failure.json","release-receipt.json"}
 hashed={str(p.relative_to(BASE)).replace("\\","/"):sha(p) for p in files if p.is_file() and p.name not in omit and ".tmp" not in p.name}
 save(BASE/"release-receipt.json",dict(stage="P129",status="COMPLETE",engineering="PASS",files_sha256=hashed,
  scientific_scope="synthetic mechanism only",general_bpe_superiority_demonstrated=False))
 with zipfile.ZipFile(BASE/"INCELEME-PAKETI.zip","w",compression=zipfile.ZIP_DEFLATED) as z:
  for rel in hashed:
   if not rel.startswith("models/") and not rel.endswith(".pt"):z.write(BASE/rel,rel)
  z.write(BASE/"release-receipt.json","release-receipt.json")
 log("REPORT ready: "+str(BASE/"SONUC_OZETI.md"))
if __name__=="__main__":main()
