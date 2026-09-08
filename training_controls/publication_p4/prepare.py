"""Build a hash-verified public source/report allowlist; emit bounded API chunks."""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / 'results_publication_p4'
MANIFEST = DEST / 'github-outbox.json'
SOURCE_MANIFEST = DEST / 'github-source-outbox.json'
PREFIX = 'training-runs/a1-large-20260908-v1/'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def inspect(path):
    path = path.resolve()
    assert path.is_relative_to(ROOT) and path.suffix in {'.py', '.json', '.md'}
    assert not any(p in path.parts for p in ('backups', 'training', 'models', '.git'))
    data = path.read_bytes()
    assert not re.search(rb'(?:gh[pousr]_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{40,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY)', data)
    text = data.decode('utf-8')
    if path.suffix == '.json':
        json.loads(text)
    return {'local_path': str(path), 'sha256': sha(data), 'bytes': len(data),
            'git_blob_sha1': hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()}


def prepare():
    assert not SOURCE_MANIFEST.exists(), 'PUBLICATION_SOURCE_MANIFEST_ALREADY_EXISTS'
    files = {}
    old = json.loads((ROOT / 'results_lexical_p2/github-outbox-final.json').read_text(encoding='utf-8'))
    for remote, saved in old['files'].items():
        entry = inspect(Path(saved['local_path']))
        assert entry['sha256'] == saved['sha256'] and entry['bytes'] == saved['bytes']
        files[remote] = entry

    def add(relative, remote=None):
        entry = inspect(ROOT / relative)
        if remote is None:
            remote = relative
        if remote in files:
            assert files[remote]['sha256'] == entry['sha256']
        files[remote] = entry

    for n in ('grammar_p3.py', 'decoder_p3.py', 's06e_p3.py', 'features_p4.py', 's06e_p4.py',
              'S06E-P3-YONT-degerlendirmesi.md', 'DEVAM-NOKTASI-P3.md',
              'S06E-P4-Iki-Secim-Katmani-degerlendirmesi.md', 'DEVAM-NOKTASI-P4.md',
              'S06E-P4-GitHub-Yayin.md', 'training_controls/publication_p4/prepare.py',
              'results_lexical_p2/model-location.json', 'results_lexical_p2/policy-imst/model-location.json'):
        add(n)
    for part in ('grammar_p3', 'layers_p4'):
        for path in sorted((ROOT / 'training_controls' / part).iterdir()):
            if path.suffix in {'.py', '.json', '.md'}:
                add(path.relative_to(ROOT).as_posix())
    for part in ('grammar_p3', 'layers_p4'):
        for path in sorted((ROOT / ('results_' + part)).glob('*.json')):
            if 'progress' not in path.name:
                add(path.relative_to(ROOT).as_posix())
        receipt = json.loads((ROOT / ('results_' + part) / 'backup-receipt.json').read_text(encoding='utf-8'))
        for remote, entry in files.items():
            relative = Path(entry['local_path']).relative_to(ROOT).as_posix()
            frozen = receipt['sha256'].get('source/' + relative)
            if frozen:
                assert entry['sha256'] == frozen, ('FROZEN_SOURCE_CHANGED', relative)
    # Keep P2/P3/P4 historical records immutable; publication has its own folder.
    result = {'repository': old['repository'], 'branch': old['branch'], 'base_commit': old['base_commit'],
              'files': files, 'public_files': len(files), 'bytes': sum(e['bytes'] for e in files.values()),
              'raw_corpus_or_full_model_weights_published': False,
              'user_authorization': "tamam dostum Github'a yayın yapalım.",
              'old_P2_manifest_sha256': sha((ROOT / 'results_lexical_p2/github-outbox-final.json').read_bytes())}
    DEST.mkdir(exist_ok=True)
    SOURCE_MANIFEST.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    # Public reports retain numbers and code/model identities, but do not expose
    # private corpus, split, lattice, cache or per-sentence output fingerprints.
    safe_hashes = {e['sha256'] for n, e in files.items() if n.endswith('.py')}
    for n, e in files.items():
        if n.endswith('model-location.json'):
            safe_hashes.add(json.loads(Path(e['local_path']).read_text(encoding='utf-8'))['sha256'])
    redactions = []
    def clean(value, where):
        if isinstance(value, dict):
            return {k: clean(v, where + '/' + k) for k, v in value.items()}
        if isinstance(value, list):
            return [clean(v, where + '/' + str(i)) for i, v in enumerate(value)]
        if isinstance(value, str):
            def replace(m):
                if m.group() in safe_hashes:
                    return m.group()
                redactions.append(where)
                return '[PRIVATE_HASH_OMITTED]'
            return re.sub(r'(?<![a-fA-F0-9])[a-fA-F0-9]{64}(?![a-fA-F0-9])', replace, value)
        return value
    for remote, source in list(files.items()):
        path = Path(source['local_path'])
        if path.suffix == '.json' and not remote.endswith('model-location.json'):
            data = json.loads(path.read_text(encoding='utf-8'))
            public_data = clean(data, remote)
            if public_data != data:
                assert isinstance(public_data, dict)
                public_data['_publication'] = {'private_hashes_omitted': True, 'aggregate_metrics_unchanged': True,
                    'full_original_retained_locally': True, 'not_a_runtime_freeze_manifest': True}
                target = DEST / 'public' / remote
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(json.dumps(public_data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
                files[remote] = inspect(target)
    result['files'] = files
    result['bytes'] = sum(e['bytes'] for e in files.values())
    result['public_report_hash_redactions'] = len(redactions)
    result['public_report_copies_redacted'] = sum('/public/' in Path(e['local_path']).as_posix() for e in files.values())
    MANIFEST.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    public = {k: v for k, v in result.items() if k != 'files'}
    public['files'] = {k: {a: b for a, b in e.items() if a != 'local_path'} for k, e in files.items()}
    (DEST / 'public-manifest.json').write_text(json.dumps(public, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (DEST / 'redaction-audit.json').write_text(json.dumps({'paths': redactions}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'files'}, ensure_ascii=False))


def payload(chunk):
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    items = []
    for remote, saved in manifest['files'].items():
        path = Path(saved['local_path'])
        assert inspect(path) == saved, ('PAYLOAD_CHANGED', remote)
        items.append({'path': remote, 'mode': '100644', 'type': 'blob', 'content': path.read_bytes().decode('utf-8')})
    extra = DEST / 'public-manifest.json'
    items.append({'path': PREFIX + 'P4-two-layer-v1/github-manifest.json', 'mode': '100644', 'type': 'blob', 'content': extra.read_text(encoding='utf-8')})
    chunks = []; current = []; size = 0
    for item in items:
        count = len(json.dumps(item, ensure_ascii=False).encode('utf-8'))
        if current and size + count > 100_000:
            chunks.append(current); current = []; size = 0
        current.append(item); size += count
    if current:
        chunks.append(current)
    if chunk < 0:
        print(json.dumps({'chunks': len(chunks), 'entries': len(items), 'chunk_sizes': [len(c) for c in chunks]}))
    else:
        print(json.dumps({'index': chunk, 'chunks': len(chunks), 'tree_elements': chunks[chunk]}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--chunk', type=int)
    args = parser.parse_args()
    prepare() if args.chunk is None else payload(args.chunk)
