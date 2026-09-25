"""Only fabricated fixture results in tests/report-fixture; never main measurements."""
from common import *
import ast,copy
import report
def main():
 for p in (BASE/"scripts").glob("*.py"):ast.parse(p.read_text(encoding="utf8"),filename=str(p))
 testroot=BASE/"tests/report-fixture";testroot.mkdir(exist_ok=True)
 for d in ("results","data","models","scripts","controls","tests"):(testroot/d).mkdir(exist_ok=True)
 c=copy.deepcopy(config());c["bootstrap_samples"]=200
 samples=[]
 for split in ("iid","lexical","order","composition"):
  for j in range(3):
   for role in ("subject","object","owner"):
    samples.append(dict(id=f"{split}:{j}:{role}",group=f"{split}:{j}",split=split,role=role,target=0,edges=[[0,1,1]],structured_query_rule_correct=True))
 def evaluation(correct):
  return dict(status="COMPLETE",predictions=[dict(id=r["id"],group=r["group"],split=r["split"],role=r["role"],target=0,correct=correct) for r in samples])
 save(testroot/"data/manifest.json",dict(rows={"fixture":len(samples)}))
 for arm in c["arms"]:
  for seed in c["seeds"]:
   save(testroot/f"results/eval-{arm}-{seed}.json",evaluation(arm=="graph"))
   save(testroot/f"results/train-{arm}-{seed}.json",dict(initial_sha256=str(seed),order_sha256=str(seed),steps=1,examples=1,parameters={},training_seconds=1))
 save(testroot/"results/eval-base-0.json",evaluation(False))
 report.BASE=testroot;report.config=lambda:c;report.rows=lambda name:samples
 report.main()
 positive=read(testroot/"summary.json");assert positive["synthetic_mechanism_gate_passed"] and not positive["general_bpe_superiority_demonstrated"]
 for seed in c["seeds"]:save(testroot/f"results/eval-graph-{seed}.json",evaluation(False))
 report.main()
 negative=read(testroot/"summary.json");assert not negative["synthetic_mechanism_gate_passed"]
 save(BASE/"tests/report-harness.json",dict(status="PASS",fixtures_only=True,all_python_sources_parse=True,positive_gate_passes=True,
  zero_gain_gate_fails=True,general_superiority_never_inferred=True,main_training_started=False))
 log("REPORT FIXTURE PASS; not experiment evidence")
if __name__=="__main__":main()
