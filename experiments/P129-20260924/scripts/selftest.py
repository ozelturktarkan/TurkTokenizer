from common import *
import argparse,copy,random
import torch
from torch.nn import functional as F
from relation_model import build,batch,weights_hash
from dataset import Native,pack
def main(gpu=False):
 from transformers import AutoTokenizer
 torch.set_num_threads(4);torch.set_num_interop_threads(2)
 versions()
 tok=AutoTokenizer.from_pretrained(str(MODEL),local_files_only=True,trust_remote_code=False)
 native=Native(BASE/"tests/native-cache.sqlite")
 text="Çocuk öğretmenin kitabını okudu."
 try:a=native.get(text)
 finally:native.close()
 assert a["status"]=="G0_CONSENSUS"
 ep=dict(id="engineering",split="train",group="engineering-only",choice_seed=129,context=text,
  events=[dict(text=text,subject="çocuk",object="kitap",owner="öğretmen",object_phrase="öğretmenin kitabını",
    possacc="kitabını",verb="oku",past="okudu",word_identity=["çocuk","öğretmen","kitap","oku"])])
 schema={f:i+1 for i,f in enumerate(sorted({f for w in a["words"] for f in w["features"]}))}
 rr=list(pack(ep,[a],tok,schema))
 assert len(rr)==3 and all(r["edges"] for r in rr)
 label_ids=[tok.encode(" "+c,add_special_tokens=False) for c in "ABCD"]
 assert all(len(x)==1 for x in label_ids)
 if not gpu:
  rr=copy.deepcopy(rr)
  for r in rr:r["ids"]=[i%40 for i in r["ids"]]
  # Tiny model context can be extended for this engineering fixture.
 dev="cuda" if gpu else "cpu"
 model=build(12999,len(schema),[x[0] for x in label_ids] if gpu else [1,2,3,4],device=dev,tiny=not gpu)
 model.eval()
 b=batch(rr[:1],dev) # no padding in single fixture, tiny vocabulary remains valid.
 initial=model.snapshot();counts=model.counts()
 logits=[model(b,arm).detach() for arm in ("plain","morph","graph","shuffled")]
 assert all(torch.allclose(logits[0],x,atol=1e-5,rtol=1e-5) for x in logits[1:]),"initial equality"
 with torch.no_grad():model.up.weight.normal_(std=.1)
 graph=model(b,"graph");plain=model(b,"plain");wrong=model(b,"shuffled")
 assert not torch.allclose(graph,plain,atol=1e-6,rtol=1e-6),"features inactive"
 assert not torch.allclose(graph,wrong,atol=1e-6,rtol=1e-6),"edge endpoints inactive"
 model.restore(initial)
 def frozen_digest():
  import hashlib
  h=hashlib.sha256()
  for n,p in model.named_parameters():
   if not p.requires_grad:h.update(n.encode());h.update(p.detach().contiguous().view(torch.uint8).cpu().numpy().tobytes())
  return h.hexdigest()
 frozen=frozen_digest()
 model.train();opt=torch.optim.AdamW(model.trainable().values(),lr=.001)
 loss=F.cross_entropy(model(b,"graph"),b["labels"]);loss.backward()
 assert torch.isfinite(loss) and model.up.weight.grad.abs().sum()>0
 opt.step()
 assert all(p.grad is None for p in model.parameters() if not p.requires_grad)
 assert frozen_digest()==frozen
 changed=model.snapshot();assert weights_hash(changed)!=weights_hash(initial)
 path=BASE/"tests"/("gpu-resume.pt" if gpu else "cpu-resume.pt")
 torch.save(dict(state=changed,optimizer=opt.state_dict()),path)
 z=torch.load(path,map_location="cpu",weights_only=False)
 model.eval();expected=model(b,"graph").detach()
 model.restore(initial);model.restore(z["state"]);opt.load_state_dict(z["optimizer"])
 assert torch.allclose(model(b,"graph"),expected,atol=1e-5,rtol=1e-5),"checkpoint restore"
 # Gold labels cannot influence predictions through collate/input annotations.
 other={k:v.clone() for k,v in b.items()};other["labels"]=(other["labels"]+1)%4
 assert torch.equal(model(b,"graph"),model(other,"graph"))
 # Topology corruption preserves relation counts and changes all edge endpoints.
 live=b["edges"][0,:,2]>0
 assert torch.equal(b["edges"][0,live,2],b["wrong"][0,live,2])
 assert torch.all((b["edges"][0,live,:2]!=b["wrong"][0,live,:2]).all(-1))
 save(BASE/"tests"/("gpu.json" if gpu else "cpu.json"),dict(status="PASS",device=dev,at=now(),
  versions=versions(),parameters=counts,initial_all_arms_equal=True,edges_affect_predictions=True,
  answer_labels_not_input=True,frozen_tensors_unchanged=True,gradient_and_optimizer_pass=True,
  checkpoint_restore_pass=True,loss=float(loss.detach()),main_experiment_started=False))
 log("GPU ENGINEERING PASS" if gpu else "CPU ENGINEERING PASS")
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--gpu",action="store_true");a=p.parse_args();main(a.gpu)
