from common import *
import random,itertools,sqlite3,subprocess,collections
PEOPLE=[("çocuk","çocuğun"),("öğretmen","öğretmenin"),("öğrenci","öğrencinin"),("doktor","doktorun"),
 ("hemşire","hemşirenin"),("komşu","komşunun"),("yazar","yazarın"),("ressam","ressamın"),
 ("şair","şairin"),("işçi","işçinin"),("adam","adamın"),("kadın","kadının"),
 ("müdür","müdürün"),("memur","memurun"),("asker","askerin"),("şoför","şoförün")]
OBJECTS={
 "oku":[("kitap","kitabı","kitabını"),("mektup","mektubu","mektubunu"),("dergi","dergiyi","dergisini"),("roman","romanı","romanını")],
 "aç":[("kapı","kapıyı","kapısını"),("pencere","pencereyi","penceresini"),("dolap","dolabı","dolabını"),("kutu","kutuyu","kutusunu")],
 "al":[("bardak","bardağı","bardağını"),("kalem","kalemi","kalemini"),("çanta","çantayı","çantasını"),("şişe","şişeyi","şişesini")],
 "sil":[("resim","resmi","resmini"),("yazı","yazıyı","yazısını"),("tahta","tahtayı","tahtasını"),("çizgi","çizgiyi","çizgisini")]}
PAST={"oku":"okudu","aç":"açtı","al":"aldı","sil":"sildi"}
ORDERS=list(itertools.permutations(("s","o","v")))
def cap(s):return s[0].replace("i","İ").upper()+s[1:]
def episodes(split,count,used):
 rng=random.Random(1292409+["train","iid","lexical","order","composition"].index(split))
 pp=PEOPLE[12:] if split=="lexical" else PEOPLE[:12]
 for i in range(count):
  while True:
   n=3 if split=="composition" else 2
   verbs=rng.sample(list(PAST),n);subjects=rng.sample(pp,n);ev=[]
   for j,v in enumerate(verbs):
    pool=OBJECTS[v][3:] if split=="lexical" else OBJECTS[v][:3]
    o=rng.choice(pool);owner=rng.choice([p for p in pp if p!=subjects[j]]) if rng.random()<.75 else None
    order=rng.choice(ORDERS[4:] if split=="order" else ORDERS[:4])
    chunks={"s":[subjects[j][0]],"o":([owner[1],o[2]] if owner else [o[1]]),"v":[PAST[v]]}
    words=[w for unit in order for w in chunks[unit]]
    spans=[];at=0
    for w in words:spans.append((at,at+len(w)));at+=len(w)+1
    text=cap(" ".join(words))+"."
    identity=[v,subjects[j][0],o[0],owner[0] if owner else None]
    ev.append(dict(text=text,subject=subjects[j][0],object=o[0],owner=owner[0] if owner else None,
       object_phrase=" ".join(chunks["o"]),possacc=o[2],verb=v,past=PAST[v],identity=identity,
       # Surface word identities are for diagnostic rule-only upper bound, never model features.
       word_identity=[subjects[j][0] if w==subjects[j][0] else owner[0] if owner and w==owner[1] else o[0] if w in o[1:] else v for w in words]))
   ident=digest(sorted([e["identity"] for e in ev],key=str))
   if ident not in used:used.add(ident);break
  rng.shuffle(ev)
  yield dict(id=split+":"+str(i),split=split,group=ident,events=ev,context=" ".join(e["text"] for e in ev),choice_seed=rng.randrange(1<<30))
class Native:
 def __init__(self,cache_path=None):
  self.db=sqlite3.connect(cache_path or BASE/"data/native-cache.sqlite")
  self.db.execute("CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY,v TEXT)")
  h=sha(NATIVE/"bin/binding.exe")
  old=self.db.execute("SELECT v FROM meta WHERE k='binary'").fetchone()
  if old and old[0]!=h:raise RuntimeError("Native annotation cache binary mismatch")
  self.db.execute("INSERT OR IGNORE INTO meta VALUES('binary',?)",(h,))
  self.db.execute("CREATE TABLE IF NOT EXISTS cache(text TEXT PRIMARY KEY,payload TEXT)")
  self.db.commit()
  self.err=(BASE/"logs/native-stderr.log").open("ab")
  self.p=subprocess.Popen([str(NATIVE/"bin/binding.exe"),str(BASE.parent/"P81-20260916/data"),
    str(NATIVE/"data/frames.json"),str(BASE.parent/"P84-20260916/data/bpe.bin")],
    stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.err,creationflags=subprocess.CREATE_NO_WINDOW)
 def get(self,text):
  cached=self.db.execute("SELECT payload FROM cache WHERE text=?",(text,)).fetchone()
  if cached:return json.loads(cached[0])
  self.p.stdin.write((json.dumps(dict(op="analyze",text=text),ensure_ascii=False)+"\n").encode());self.p.stdin.flush()
  line=self.p.stdout.readline()
  if not line:raise RuntimeError("P128 native exited")
  r=json.loads(line);assert r["ok"],r
  r=r["result"];g=r["binding"]
  assert g["status"]!="SIDECAR_ERROR",g
  words=[]
  for t in g["tokens"]:
   f=set()
   for c in t["candidates"]:
    root,rp,events,fp=json.loads(c["key"]);f.update(["ROOTPOS:"+rp,"FINALPOS:"+fp])
    f.update("MORPH:"+m for m,b in events)
   words.append(dict(start=t["start"],end=t["end"],features=sorted(f)))
  edges=[];a=g["conditional_role_answer"]
  if a:
   for d,h,rid in [(a["subject"],a["predicate"],1),(a["object"],a["predicate"],2)]:
    edges.extend([(d,h,rid),(h,d,rid+3)])
   if a["possessor"] is not None:
    d,h=a["possessor"],a["possessed"];edges.extend([(d,h,3),(h,d,6)])
  out=dict(words=words,edges=edges,status=g["status"],role_answer=a,
    baseline_sha256=digest(r["baseline"]),trace_sha256=digest(r["baseline_trace"]),
    binding=g)
  self.db.execute("INSERT INTO cache VALUES(?,?)",(text,json.dumps(out,ensure_ascii=False)));self.db.commit()
  return out
 def close(self):
  self.p.stdin.close();self.p.wait(timeout=30);self.err.close();self.db.close()
def questions(ep):
 rng=random.Random(ep["choice_seed"])
 for role in ("subject","object","owner"):
  target=rng.randrange(len(ep["events"]));e=ep["events"][target]
  question=({"subject":f'{cap(e["object_phrase"])} kim {e["past"]}?',
    "object":f'{cap(e["subject"])} neyi {e["past"]}?',
    "owner":f'{cap(e["subject"])} kimin {e["possacc"]} {e["past"]}?'}[role])
  answer=e[role] or "Belirtilmedi"
  pp=PEOPLE[12:] if ep["split"]=="lexical" else PEOPLE[:12]
  pool=[p[0] for p in pp] if role!="object" else [o[0] for oo in OBJECTS.values() for o in (oo[3:] if ep["split"]=="lexical" else oo[:3])]
  pool=[x for x in pool if x!=answer]
  choices=[answer]+rng.sample(pool,3) if answer=="Belirtilmedi" else [answer,"Belirtilmedi"]+rng.sample(pool,2)
  rng.shuffle(choices)
  yield role,target,question,answer,choices
def pack(ep,annotations,tok,schema):
 words=[];edges=[];start=0
 for e,a in zip(ep["events"],annotations):
  shift=len(words);words += [dict(start=w["start"]+start,end=w["end"]+start,features=w["features"]) for w in a["words"]]
  edges += [[d+shift,h+shift,r] for d,h,r in a["edges"]]
  start+=len(e["text"])+1
 assert len(words)<=16 and len(edges)<=24
 for role,target,q,answer,choices in questions(ep):
  prompt=ep["context"]+"\nSoru: "+q+"\n"+"\n".join(f"{chr(65+i)}) {c}" for i,c in enumerate(choices))+"\nCevap:"
  enc=tok(prompt,add_special_tokens=False,return_offsets_mapping=True)
  assert len(enc["input_ids"])<=config()["max_tokens"],("sequence too long",len(enc["input_ids"]))
  word_ids=[]
  for lo,hi in enc["offset_mapping"]:
   hits=[i for i,w in enumerate(words) if min(hi,w["end"])>max(lo,w["start"])]
   assert len(hits)<=1,("cross-word BPE token",prompt,lo,hi)
   word_ids.append(hits[0] if hits else -1)
  assert set(range(len(words)))<=set(word_ids),("word alignment",ep["id"])
  features=[[schema.get(f,0) for f in w["features"]] for w in words]
  assert max(map(len,features),default=0)<=48,"feature capacity"
  a=annotations[target]["role_answer"];rule=None
  if a:
   idx=a[role if role!="owner" else "possessor"]
   if idx is not None:rule=ep["events"][target]["word_identity"][idx]
  # Oracle query-to-clause routing is supplied by generator; not a natural-language rule QA baseline.
  yield dict(id=ep["id"]+":"+role,group=ep["group"],split=ep["split"],role=role,
   prompt=prompt,answer=answer,choices=choices,target=choices.index(answer),ids=enc["input_ids"],
   word_ids=word_ids,features=features,edges=edges,
   teacher_status=[a["status"] for a in annotations],
   structured_query_rule_correct=(rule==answer) if rule is not None else None,
   shuffle_seed=int(digest(ep["id"])[:8],16))
def prepare():
 from transformers import AutoTokenizer
 if (BASE/"data/manifest.json").exists():
  m=read(BASE/"data/manifest.json")
  for p,h in m["files_sha256"].items():assert sha(BASE/"data"/p)==h,p
  log("DATA verified, reused");return
 c=config();used=set();all_ep=[]
 for split,count in c["contexts"].items():all_ep.extend(episodes(split,count,used))
 # Episode identity ignores word order: no same episode can cross train/eval boundaries.
 assert len({e["group"] for e in all_ep})==len(all_ep)
 native=Native();annotations={};vocab=set();counts=collections.Counter()
 try:
  for i,ep in enumerate(all_ep):
   aa=[native.get(e["text"]) for e in ep["events"]];annotations[ep["id"]]=aa
   for a in aa:
    counts[a["status"]]+=1
    if ep["split"]=="train":
     for w in a["words"]:vocab.update(w["features"])
   if i%100==0:log(f"ANNOTATE {i}/{len(all_ep)}");state("PREPARE",contexts_done=i,contexts_total=len(all_ep))
 finally:native.close()
 schema={s:i+1 for i,s in enumerate(sorted(vocab))}
 save(BASE/"data/schema.json",dict(features=schema,source="TRAIN-only union of frozen native candidate POS/morphemes; no answer labels"))
 tok=AutoTokenizer.from_pretrained(str(MODEL),local_files_only=True,trust_remote_code=False)
 letters=[tok.encode(" "+a,add_special_tokens=False) for a in "ABCD"]
 assert all(len(x)==1 for x in letters) and len(set(x[0] for x in letters))==4,letters
 counts_rows=collections.Counter();coverage=collections.Counter();lengths=[]
 paths={s:BASE/"data"/(s+".jsonl") for s in ("train","eval")}
 files={s:p.with_suffix(".jsonl.tmp").open("w",encoding="utf8") for s,p in paths.items()}
 try:
  for ep in all_ep:
   for row in pack(ep,annotations[ep["id"]],tok,schema):
    files["train" if ep["split"]=="train" else "eval"].write(json.dumps(row,ensure_ascii=False)+"\n")
    counts_rows[ep["split"]]+=1;coverage[ep["split"]]+=bool(row["edges"]);lengths.append(len(row["ids"]))
 finally:
  for f in files.values():f.close()
 for s,p in paths.items():os.replace(p.with_suffix(".jsonl.tmp"),p)
 save(BASE/"data/episodes.json",all_ep)
 names=["train.jsonl","eval.jsonl","schema.json","episodes.json","native-cache.sqlite"]
 save(BASE/"data/manifest.json",dict(status="PASS",files_sha256={n:sha(BASE/"data"/n) for n in names},
    rows=dict(counts_rows),contexts=c["contexts"],edge_present_rows=dict(coverage),native_statuses=dict(counts),
    max_length=max(lengths),mean_length=sum(lengths)/len(lengths),label_token_ids=[x[0] for x in letters],
    source="Deterministic agent-authored synthetic Turkish episodes, not human gold or independent general Turkish benchmark",
    closed_test_accessed=False,train_eval_episode_overlap=0,feature_schema_train_only=True))
 log("DATA complete "+str(dict(counts_rows)))
if __name__=="__main__":prepare()
