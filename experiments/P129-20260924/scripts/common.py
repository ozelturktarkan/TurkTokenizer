from pathlib import Path
import os,sys,json,hashlib,datetime,tempfile
BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parent.parent
RUNTIME=BASE.parent/"hf-runtime-v1"
MODEL=RUNTIME/"Qwen3-0.6B-Base"
NATIVE=BASE.parent/"P128-20260924"
PYTHON=Path(sys.executable)
for folder in ("tmp","logs"):(BASE/folder).mkdir(exist_ok=True)
os.environ.update(TEMP=str(BASE/"tmp"),TMP=str(BASE/"tmp"),TMPDIR=str(BASE/"tmp"),
 HF_HOME=str(RUNTIME/"hf-cache"),HF_HUB_OFFLINE="1",TRANSFORMERS_OFFLINE="1",
 TOKENIZERS_PARALLELISM="false",PYTHONDONTWRITEBYTECODE="1",PYTHONUTF8="1",
 OMP_NUM_THREADS="4",MKL_NUM_THREADS="4",OPENBLAS_NUM_THREADS="1",CUBLAS_WORKSPACE_CONFIG=":4096:8",
 TURKTOKENIZER_LOOKUP_INDEX=str(BASE.parent/"P111-20260923/data/lookup-index.bin"))
sys.dont_write_bytecode=True
def read(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def save(p,x):
 p=Path(p);tmp=p.with_name(p.name+".tmp")
 with tmp.open("w",encoding="utf8") as f:json.dump(x,f,ensure_ascii=False,indent=2);f.flush();os.fsync(f.fileno())
 os.replace(tmp,p)
def sha(p):
 with Path(p).open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def log(s):print(now(),s,flush=True)
def config():return read(BASE/"protocol.json")
def rows(name):
 with (BASE/"data"/(name+".jsonl")).open(encoding="utf8") as f:return [json.loads(line) for line in f]
def state(phase,**kw):save(BASE/"STATUS.json",dict(at=now(),phase=phase,**kw))
def versions():
 import torch,transformers,peft
 assert transformers.__version__=="4.57.6" and peft.__version__=="0.18.1"
 return dict(torch=torch.__version__,transformers=transformers.__version__,peft=peft.__version__)
