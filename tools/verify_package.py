from pathlib import Path
import hashlib,json,sys
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'PACKAGE-MANIFEST.json').read_text(encoding='utf-8'))
errors=[]
for rel,v in manifest['files'].items():
    p=root/rel
    if not p.is_file():errors.append((rel,'MISSING'));continue
    with p.open('rb') as f:h=hashlib.file_digest(f,'sha256').hexdigest()
    if h!=v['sha256'] or p.stat().st_size!=v['bytes']:errors.append((rel,'MISMATCH'))
print(json.dumps({'status':'FAIL' if errors else 'PASS','checked':len(manifest['files']),'errors':errors},indent=2))
sys.exit(bool(errors))
