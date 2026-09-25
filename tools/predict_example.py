"""Offline end-to-end reproduction of ONE saved P129 example; no training."""
from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'experiments/P129-20260924/scripts'))
from common import BASE,MODEL,read,sha,rows

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--index',type=int,default=0)
    p.add_argument('--arm',choices=['plain','morph','graph','shuffled'],default='graph')
    p.add_argument('--seed',type=int,choices=[12911,12923,12937],default=12937)
    p.add_argument('--device',default='cuda',choices=['cuda','cpu'])
    a=p.parse_args()
    import torch
    from transformers import AutoTokenizer
    from dataset import Native,pack
    from relation_model import build,batch
    torch.set_num_threads(4);torch.set_num_interop_threads(2)
    if a.device=='cuda' and not torch.cuda.is_available():
        raise RuntimeError('CUDA unavailable; install the stated CUDA PyTorch build or use --device cpu (slow).')
    allrows=rows('eval')
    if not 0<=a.index<len(allrows):raise ValueError('Index must be in [0,4799]')
    saved=allrows[a.index];episode_id=saved['id'].rsplit(':',1)[0]
    ep=next(x for x in read(BASE/'data/episodes.json') if x['id']==episode_id)
    schema=read(BASE/'data/schema.json')['features']
    manifest=read(BASE/'data/manifest.json')
    tok=AutoTokenizer.from_pretrained(MODEL,local_files_only=True)
    output=ROOT/'output';output.mkdir(exist_ok=True)
    native=Native(cache_path=output/'demo-native-cache.sqlite')
    try: annotations=[native.get(x['text']) for x in ep['events']]
    finally:native.close()
    rebuilt=next(x for x in pack(ep,annotations,tok,schema) if x['id']==saved['id'])
    assert rebuilt==saved,'Native/BPE/features/edge reconstruction differs from frozen record'
    tag=f'{a.arm}-{a.seed}'
    receipt=read(BASE/f'results/train-{tag}.json')
    ckpt=BASE/f'models/{tag}.pt'
    assert sha(ckpt)==receipt['checkpoint_sha256'],'Checkpoint checksum mismatch'
    model=build(a.seed,len(schema),manifest['label_token_ids'],device=a.device)
    # Only the local checkpoint verified above is read; it contains optimizer RNG metadata.
    z=torch.load(ckpt,map_location='cpu',weights_only=False)
    assert z['arm']==a.arm and z['seed']==a.seed
    assert z['protocol']==sha(BASE/'protocol.json') and z['data']==sha(BASE/'data/manifest.json')
    model.restore(z['state']);model.eval()
    with torch.no_grad():probs=model(batch([rebuilt],a.device),a.arm).softmax(-1)[0].cpu().tolist()
    choice=max(range(4),key=probs.__getitem__)
    old=next(x for x in read(BASE/f'results/eval-{tag}.json')['predictions'] if x['id']==saved['id'])
    report=dict(status='PASS' if choice==old['prediction'] else 'PREDICTION_DIFF',checkpoint=tag,
      example_id=saved['id'],prompt=saved['prompt'],probabilities=probs,choice=chr(65+choice),
      answer=saved['choices'][choice],reference_answer=saved['answer'],correct=choice==saved['target'],
      native_bpe_features_edges_equal=True,original_prediction_equal=choice==old['prediction'],
      maximum_probability_difference=max(abs(x-y) for x,y in zip(probs,old['probabilities'])),
      parameters=model.counts(),device=a.device,scope='Single existing example installation check, not a new quality experiment')
    (output/'last-demo.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if report['status']!='PASS':raise SystemExit(1)

if __name__=='__main__':main()
