from common import *
import argparse,signal,math,random,time
import numpy as np
import torch
from torch.nn import functional as F
from relation_model import build,batch,weights_hash
STOP=False
def stop(signum,frame):
 global STOP
 STOP=True
 print("Durdurma istendi; mevcut optimizer adimindan sonra kaydedilecek.",flush=True)
def atomic_torch(path,payload):
 tmp=path.with_suffix(".tmp.pt")
 with tmp.open("wb") as f:torch.save(payload,f);f.flush();os.fsync(f.fileno())
 os.replace(tmp,path)
def get_plan(n,seed):
 plan=[]
 for epoch in range(config()["epochs"]):
  order=list(range(n));random.Random(seed+epoch*100003).shuffle(order)
  plan.extend([order[i:i+config()["batch_size"]] for i in range(0,n,config()["batch_size"])])
 return plan
def train(arm,seed):
 signal.signal(signal.SIGINT,stop)
 torch.set_num_threads(4);torch.set_num_interop_threads(2)
 torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
 c=config();tag=f"{arm}-{seed}";done=BASE/f"results/train-{tag}.json";ckpt=BASE/f"models/{tag}.pt"
 if done.exists():
  d=read(done);assert d["status"]=="COMPLETE" and sha(ckpt)==d["checkpoint_sha256"];log("REUSE "+tag);return
 data=rows("train");manifest=read(BASE/"data/manifest.json");schema=read(BASE/"data/schema.json")["features"]
 model=build(seed,len(schema),manifest["label_token_ids"]);model.train()
 params=list(model.trainable().values());opt=torch.optim.AdamW(params,lr=c["lr"],weight_decay=.01)
 initial=weights_hash(model.snapshot());plan=get_plan(len(data),seed);orderhash=digest(plan);start=0;elapsed_before=0;history=[]
 if ckpt.exists():
  z=torch.load(ckpt,map_location="cpu",weights_only=False)
  assert z["protocol"]==sha(BASE/"protocol.json") and z["data"]==sha(BASE/"data/manifest.json") and z["order"]==orderhash
  assert z["arm"]==arm and z["seed"]==seed and z["initial"]==initial
  model.restore(z["state"]);opt.load_state_dict(z["optimizer"]);start=z["step"];history=z["history"];elapsed_before=z["elapsed"]
  torch.set_rng_state(z["rng"]);torch.cuda.set_rng_state_all(z["cuda_rng"])
 torch.cuda.reset_peak_memory_stats();torch.cuda.synchronize();began=time.perf_counter()
 def checkpoint(step):
  torch.cuda.synchronize()
  z=dict(arm=arm,seed=seed,step=step,state=model.snapshot(),optimizer=opt.state_dict(),rng=torch.get_rng_state(),
   cuda_rng=torch.cuda.get_rng_state_all(),protocol=sha(BASE/"protocol.json"),data=sha(BASE/"data/manifest.json"),
   order=orderhash,initial=initial,history=history,elapsed=elapsed_before+time.perf_counter()-began)
  atomic_torch(ckpt,z)
 for step in range(start,len(plan)):
  indices=plan[step];opt.zero_grad(set_to_none=True);total=correct=0.
  warm=max(1,int(len(plan)*.05));fraction=(step+1)/warm if step<warm else .1+.9*.5*(1+math.cos(math.pi*(step-warm)/max(1,len(plan)-warm)))
  for g in opt.param_groups:g["lr"]=c["lr"]*fraction
  for k in range(0,len(indices),c["microbatch"]):
   items=[data[i] for i in indices[k:k+c["microbatch"]]]
   b=batch(items,"cuda");logits=model(b,arm);loss=F.cross_entropy(logits,b["labels"],reduction="sum")/len(indices)
   assert torch.isfinite(loss),"Nonfinite loss"
   loss.backward();total+=float(loss.detach());correct+=float(logits.argmax(-1).eq(b["labels"]).sum())
  norm=torch.nn.utils.clip_grad_norm_(params,1.)
  assert torch.isfinite(norm),"Nonfinite gradient"
  opt.step()
  history.append(dict(step=step+1,loss=total,correct=int(correct),rows=len(indices),lr=opt.param_groups[0]["lr"]))
  if (step+1)%10==0 or step+1==len(plan):
   torch.cuda.synchronize();spent=time.perf_counter()-began;eta=(len(plan)-step-1)*spent/max(1,step+1-start)
   log(f"{tag} {step+1}/{len(plan)} loss={total:.4f} run_remaining~{eta/60:.1f} min")
   state("TRAIN",arm=arm,seed=seed,step=step+1,total_steps=len(plan),estimated_run_remaining_seconds=eta)
  if (step+1)%c["checkpoint_every"]==0 or STOP or step+1==len(plan):checkpoint(step+1)
  if STOP:log("PAUSED checkpoint saved");sys.exit(130)
 assert all(p.grad is None for p in model.parameters() if not p.requires_grad)
 z=torch.load(ckpt,map_location="cpu",weights_only=False)
 save(done,dict(status="COMPLETE",arm=arm,seed=seed,steps=len(plan),examples=len(data)*c["epochs"],
  order_sha256=orderhash,initial_sha256=initial,final_sha256=weights_hash(model.snapshot()),parameters=model.counts(),
  checkpoint_sha256=sha(ckpt),training_seconds=z["elapsed"],peak_cuda_allocated=torch.cuda.max_memory_allocated(),
  protocol_sha256=sha(BASE/"protocol.json"),data_manifest_sha256=sha(BASE/"data/manifest.json"),
  evaluation_seen=False,history=history))
def evaluate(arm,seed):
 torch.set_num_threads(4);torch.set_num_interop_threads(2)
 c=config();tag=f"{arm}-{seed}";out=BASE/f"results/eval-{tag}.json"
 if out.exists():assert read(out)["status"]=="COMPLETE";return
 data=rows("eval");m=read(BASE/"data/manifest.json");schema=read(BASE/"data/schema.json")["features"]
 model=build(seed if seed else c["seeds"][0],len(schema),m["label_token_ids"]);runtime_arm=arm
 if arm!="base":
  ckpt=BASE/f"models/{tag}.pt";d=read(BASE/f"results/train-{tag}.json");assert sha(ckpt)==d["checkpoint_sha256"]
  z=torch.load(ckpt,map_location="cpu",weights_only=False);model.restore(z["state"])
 else:runtime_arm="plain"
 model.eval();pred=[];started=time.perf_counter()
 with torch.no_grad():
  for i in range(0,len(data),c["microbatch"]):
   rr=data[i:i+c["microbatch"]];b=batch(rr,"cuda");logits=model(b,runtime_arm);pr=logits.softmax(-1).cpu().tolist()
   for r,p in zip(rr,pr):
    chosen=max(range(4),key=p.__getitem__)
    pred.append(dict(id=r["id"],group=r["group"],split=r["split"],role=r["role"],target=r["target"],
     prediction=chosen,probabilities=p,correct=chosen==r["target"],has_edges=bool(r["edges"])))
   if i%200==0:log(f"EVAL {tag} {i}/{len(data)}");state("EVALUATE",arm=arm,seed=seed,rows=i,total_rows=len(data))
 save(out,dict(status="COMPLETE",arm=arm,seed=seed,seconds=time.perf_counter()-started,predictions=pred,
  protocol_sha256=sha(BASE/"protocol.json"),data_manifest_sha256=sha(BASE/"data/manifest.json")))
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("mode",choices=["train","eval"]);p.add_argument("arm");p.add_argument("seed",type=int)
 a=p.parse_args();(train if a.mode=="train" else evaluate)(a.arm,a.seed)
