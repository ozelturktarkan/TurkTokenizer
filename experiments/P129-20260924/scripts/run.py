from common import *
import argparse,subprocess,msvcrt,signal,shutil,ctypes,time,traceback
STOP=False
def stop(sig,frame):
 global STOP
 STOP=True
 print("\nDurdurma istendi. Calisan egitimin kayit adimini tamamlamasi bekleniyor...",flush=True)
def verify_receipt(directory):
 r=read(directory/"release-receipt.json");assert r["status"]=="COMPLETE" and r["engineering"]=="PASS"
 for rel,h in r["files_sha256"].items():assert sha(directory/rel)==h,rel
 for p,h in r.get("external_files_sha256",{}).items():assert sha(p)==h,p
def preflight():
 assert os.name=="nt" and PYTHON.is_file()
 assert not read(BASE.parent/"completion-controller-v1/control.json")["enabled"],"Automatic controller must stay disabled"
 if shutil.disk_usage(BASE).free<4*1024**3:raise RuntimeError("V diskinde en az 4 GiB bos alan gerekiyor.")
 class Mem(ctypes.Structure):
  _fields_=[("length",ctypes.c_ulong),("load",ctypes.c_ulong)]+[(n,ctypes.c_ulonglong) for n in ("total_phys","avail_phys","total_page","avail_page","total_virtual","avail_virtual","avail_extended")]
 m=Mem();m.length=ctypes.sizeof(m);assert ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
 if m.avail_page<3*1024**3:raise RuntimeError("Windows bellek ayirma payi 3 GiB altinda. Uygulamalari kapatip ayni komutu yeniden calistir.")
 gpu=subprocess.check_output(["nvidia-smi","--query-gpu=name,memory.free","--format=csv,noheader,nounits"],text=True).strip()
 free=int(gpu.splitlines()[0].rsplit(",",1)[1])
 if free<5500:raise RuntimeError("GPU bos bellegi 5500 MiB altinda: "+gpu)
 model=read(MODEL/"download-receipt.json")
 for name,h in model["files_sha256"].items():assert sha(MODEL/name)==h,name
 verify_receipt(NATIVE);verify_receipt(BASE.parent/"P119-20260923")
 lock=read(ROOT/"releases/p21-stable/lock.json")
 for name,h in lock["files_sha256"].items():assert sha(ROOT/name)==h,name
 save(BASE/"tests/preflight.json",dict(status="PASS",at=now(),gpu=gpu,available_commit_bytes=m.avail_page,
  free_disk_bytes=shutil.disk_usage(BASE).free,model_snapshot_verified=True,native_receipts_verified=True,P21_locked_files_verified=True))
 log("PREFLIGHT PASS "+gpu)
def freeze():
 p=BASE/"controls/execution-freeze.json"
 candidates=[BASE/"protocol.json",BASE/"BASLAT.cmd",BASE/"README.md",*sorted((BASE/"scripts").glob("*.py"))]
 current={str(x.relative_to(BASE)).replace("\\","/"):sha(x) for x in candidates}
 ext={str(x):sha(x) for x in [MODEL/"download-receipt.json",RUNTIME/"install.json",NATIVE/"release-receipt.json",BASE.parent/"P119-20260923/release-receipt.json",ROOT/"releases/p21-stable/lock.json"]}
 if p.exists():
  old=read(p);assert old["sources"]==current and old["external_receipts"]==ext,"Frozen protocol/source/dependency changed; resume refused"
 else:save(p,dict(at=now(),sources=current,external_receipts=ext))
def execute(tag,script,args=()):
 path=BASE/"logs"/(tag+".log")
 log("START "+tag+" | "+str(path));state(tag,log=str(path))
 with path.open("a",encoding="utf8") as f:
  proc=subprocess.Popen([str(PYTHON),"-B","-X","utf8",str(BASE/"scripts"/script),*map(str,args)],
    cwd=BASE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding="utf8",errors="replace",bufsize=1)
  try:
   for line in proc.stdout:print(line,end="",flush=True);f.write(line);f.flush()
   code=proc.wait()
  except BaseException:
   if proc.poll() is None:proc.terminate();proc.wait()
   raise
 if STOP or code in (130,-1073741510):raise KeyboardInterrupt()
 if code:raise RuntimeError(f"{tag} durdu (exit={code}). Kayit: {path}. Protokol otomatik degistirilmedi.")
 log("END "+tag)
def complete_verified():
 if not (BASE/"release-receipt.json").exists():return False
 verify_receipt(BASE);return True
def main(check=False):
 # Same OS lock as historical controller: no overlapping heavy run, no queue/automation APIs.
 lock=(BASE.parent/"completion-controller-v1/worker.lock").open("a+b")
 lock.seek(0)
 if lock.read(1)==b"":lock.write(b"0");lock.flush()
 lock.seek(0)
 try:msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
 except OSError:raise RuntimeError("Baska deney calisiyor. Ikinci bir deney baslatilmadi.")
 try:
  signal.signal(signal.SIGINT,stop)
  if not check and complete_verified():
   state("COMPLETE",summary=str(BASE/"SONUC_OZETI.md"));log("Deney zaten tamam: "+str(BASE/"SONUC_OZETI.md"));return
  preflight()
  if check:
   execute("generator-check","generator_tests.py")
   execute("engineering-cpu","selftest.py")
   execute("engineering-gpu","selftest.py",["--gpu"])
   state("READY",main_training_started=False,command=str(BASE/"BASLAT.cmd"));log("ORTAM HAZIR. Ana egitim baslatilmadi.");return
  freeze()
  execute("generator-check","generator_tests.py")
  # Always check current environment, without choosing hyperparameters from eval.
  execute("engineering-cpu","selftest.py")
  execute("engineering-gpu","selftest.py",["--gpu"])
  execute("prepare-data","dataset.py")
  c=config();plan=[]
  for i,seed in enumerate(c["seeds"]):
   order=c["arms"][i:]+c["arms"][:i]
   if i%2:order=list(reversed(order))
   plan += [(a,seed) for a in order]
  for arm,seed in plan:
   done=BASE/f"results/train-{arm}-{seed}.json"
   if done.exists():
    r=read(done);assert r["status"]=="COMPLETE" and sha(BASE/f"models/{arm}-{seed}.pt")==r["checkpoint_sha256"]
    log(f"VERIFIED completed {arm}-{seed}")
   else:execute(f"train-{arm}-{seed}","worker.py",["train",arm,seed])
  # No evaluation until all 12 fixed trainings have completed.
  execute("eval-base-0","worker.py",["eval","base",0])
  for arm,seed in plan:execute(f"eval-{arm}-{seed}","worker.py",["eval",arm,seed])
  freeze();execute("report","report.py")
  assert complete_verified()
  state("COMPLETE",summary=str(BASE/"SONUC_OZETI.md"),review_bundle=str(BASE/"INCELEME-PAKETI.zip"))
  log("DENEY TAMAMLANDI. "+str(BASE/"SONUC_OZETI.md"))
 finally:
  lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1);lock.close()
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");p.add_argument("--status",action="store_true");a=p.parse_args()
 if a.status:
  print(json.dumps(read(BASE/"STATUS.json") if (BASE/"STATUS.json").exists() else dict(phase="PREPARED_NOT_STARTED"),ensure_ascii=False,indent=2));sys.exit(0)
 try:main(a.check)
 except KeyboardInterrupt:
  state("PAUSED",instruction="Ayni BASLAT.cmd komutuyla devam et; tamamlanan egitimler atlanir.");sys.exit(130)
 except Exception as e:
  save(BASE/"failure.json",dict(at=now(),error=repr(e),traceback=traceback.format_exc()))
  state("ERROR",error=str(e),details=str(BASE/"failure.json"))
  print("HATA: "+str(e),flush=True);sys.exit(1)
