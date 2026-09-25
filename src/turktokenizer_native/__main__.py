import argparse, json, sys
from pathlib import Path
from . import NativeTokenizer, __version__

def main():
    p=argparse.ArgumentParser(description='TürkTokenizer frozen Rust + conditional YÖNT client')
    p.add_argument('--version', action='version', version=__version__)
    p.add_argument('--runtime')
    p.add_argument('--op', choices=['analyze','baseline','encode','decode','bpe'], default='analyze')
    group=p.add_mutually_exclusive_group()
    group.add_argument('--text')
    group.add_argument('--file', type=Path)
    p.add_argument('--ids', help='JSON array for decode')
    a=p.parse_args()
    if a.op=='decode':
        if a.ids is None: p.error('--ids is required for decode')
        try: value=json.loads(a.ids)
        except ValueError: p.error('--ids must be a JSON array')
        if not isinstance(value,list):p.error('--ids must be a JSON array')
    else:
        value=a.text if a.text is not None else a.file.read_text(encoding='utf-8') if a.file else sys.stdin.read()
    with NativeTokenizer(a.runtime) as t:
        result=(t.analyze_sentence(value) if a.op=='baseline' else getattr(t,a.op)(value))
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
