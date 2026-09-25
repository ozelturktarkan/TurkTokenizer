from common import *
import random,torch
from torch import nn
from torch.nn import functional as F
from pretrained_model import load_pretrained,tiny_model
ARMS=("plain","morph","graph","shuffled")
def batch(records,device):
 b=len(records);t=max(len(r["ids"]) for r in records);w=16;e=24;nf=48
 ids=torch.full((b,t),151643,dtype=torch.long)
 mask=torch.zeros(b,t,dtype=torch.bool);wi=torch.full((b,t),-1,dtype=torch.long)
 features=torch.zeros(b,w,nf,dtype=torch.long);edges=torch.zeros(b,e,3,dtype=torch.long)
 wrong=torch.zeros_like(edges);labels=torch.tensor([r["target"] for r in records],dtype=torch.long)
 for i,r in enumerate(records):
  n=len(r["ids"]);ids[i,:n]=torch.tensor(r["ids"]);mask[i,:n]=True;wi[i,:n]=torch.tensor(r["word_ids"])
  for j,f in enumerate(r["features"]):features[i,j,:len(f)]=torch.tensor(f)
  if r["edges"]:
   ed=torch.tensor(r["edges"]);edges[i,:len(ed)]=ed
   # Rotate every endpoint by nonzero offset: degree/edge/label counts preserved.
   shift=1+r["shuffle_seed"]%(len(r["features"])-1);ed=ed.clone()
   ed[:,:2]=(ed[:,:2]+shift)%len(r["features"]);wrong[i,:len(ed)]=ed
 return {k:v.to(device) for k,v in dict(ids=ids,mask=mask,word_ids=wi,features=features,edges=edges,wrong=wrong,labels=labels).items()}
class BoundLM(nn.Module):
 def __init__(self,language,feature_count,label_ids,rank=32):
  super().__init__();self.language=language
  self.language.aux_head.requires_grad_(False)
  h=language.config.hidden_size
  self.feature=nn.Embedding(feature_count+1,rank,padding_idx=0,dtype=torch.float32)
  self.relation=nn.Embedding(7,rank,padding_idx=0,dtype=torch.float32)
  self.down=nn.Linear(h,rank,bias=False,dtype=torch.float32)
  self.up=nn.Linear(rank,h,bias=False,dtype=torch.float32)
  nn.init.zeros_(self.up.weight)
  self.register_buffer("label_ids",torch.tensor(label_ids,dtype=torch.long),persistent=False)
 def forward(self,b,arm):
  assert arm in ARMS
  base=self.language.causal_model
  emb=base.get_input_embeddings()(b["ids"])
  assign=F.one_hot(b["word_ids"]+1,num_classes=17)[:,:,1:].transpose(1,2).float()
  word=(assign@emb.float())/assign.sum(-1,keepdim=True).clamp_min(1)
  normalized=F.layer_norm(word,(word.shape[-1],))
  f=self.feature(b["features"]).sum(2)/b["features"].ne(0).sum(2).clamp_min(1).sqrt().unsqueeze(-1)
  edges=b["wrong"] if arm=="shuffled" else b["edges"]
  src,dst,rel=edges.unbind(-1)
  down=self.down(normalized)
  msg=torch.tanh(down.gather(1,src.unsqueeze(-1).expand(-1,-1,down.shape[-1]))+self.relation(rel))
  msg=msg*rel.ne(0).unsqueeze(-1)
  aggregate=torch.zeros_like(down).scatter_add(1,dst.unsqueeze(-1).expand_as(msg),msg)
  degree=torch.zeros((*down.shape[:2],1),device=down.device).scatter_add(1,dst.unsqueeze(-1),rel.ne(0).float().unsqueeze(-1))
  aggregate=aggregate/degree.clamp_min(1).sqrt()
  correction=self.up((0.0 if arm=="plain" else 1.0)*f+(1.0 if arm in ("graph","shuffled") else 0.0)*aggregate)
  inputs=emb+(assign.transpose(1,2)@correction).to(emb.dtype)
  pos=(b["mask"].long().cumsum(-1)-1).clamp_min(0)
  hidden=base.model(inputs_embeds=inputs,attention_mask=b["mask"],position_ids=pos,use_cache=False,return_dict=True).last_hidden_state
  last=hidden[torch.arange(len(hidden),device=hidden.device),b["mask"].sum(-1)-1]
  # Conditional four-choice likelihood, not a full-vocabulary language-model perplexity.
  weight=base.get_output_embeddings().weight.index_select(0,self.label_ids)
  return F.linear(last,weight).float()
 def trainable(self):return {n:p for n,p in self.named_parameters() if p.requires_grad}
 def snapshot(self):return {n:p.detach().cpu().clone() for n,p in self.trainable().items()}
 def restore(self,state):
  pp=self.trainable();assert set(pp)==set(state)
  with torch.no_grad():
   for n,p in pp.items():
    assert p.shape==state[n].shape and torch.isfinite(state[n]).all(),n
    p.copy_(state[n].to(p.device))
 def counts(self):return dict(trainable=sum(p.numel() for p in self.trainable().values()),frozen=sum(p.numel() for p in self.parameters() if not p.requires_grad))
def build(seed,feature_count,label_ids,device="cuda",tiny=False):
 torch.manual_seed(seed)
 lm=tiny_model(seed=seed,aux_labels=1,device=device) if tiny else load_pretrained(MODEL,seed,aux_labels=1,device=device)
 result=BoundLM(lm,feature_count,label_ids,rank=config()["adapter_rank"]).to(device)
 return result
def weights_hash(state):
 import hashlib
 h=hashlib.sha256()
 for n,p in sorted(state.items()):h.update(n.encode());h.update(p.contiguous().view(torch.uint8).numpy().tobytes())
 return h.hexdigest()
