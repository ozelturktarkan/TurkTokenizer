"""Run resumable A1 epochs in a new V: directory; never overwrite historical models."""
import os
for variable in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[variable] = '1'
import argparse
import copy
import gzip
import json
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / '.deps-s06'), str(ROOT / '.deps-s05six')]
import bootstrap
import numpy as np
from common import Runtime
from context_ranker import canonical, features as prior_features
from s05_ua_features import features, Segmenter, UARanker
from s06e_a123 import Tokenizer, WeightedRanker
from r5.engine import fingerprint
from a123_measurement import measure, summarize, strict_match
from evaluate_global import validate_graph
from validate_s06 import verify_objective
from training_controls.e70p9.epoch_control import read, digest, atomic_json
from training_controls.e70p9.runtime import open_run
from .numerics import vocabulary, matrix, records, objective, train_epoch


def log(stage, **values):
    print(json.dumps({'stage': stage, **values}, ensure_ascii=False, allow_nan=False), flush=True)


def feature_rows(refs, raws, prior):
    segmenter = Segmenter('e')
    for ref, rec in zip(refs, raws, strict=True):
        if ref['id'] != rec['id']: raise ValueError('DEV_CACHE_ID_MISMATCH')
        ts = rec['raw_output']['tokens']
        spans = {(t['start'], t['end']): i for i, t in enumerate(ts)}
        for unit in ref['units']:
            index = spans.get((unit['start'], unit['end']))
            if index is None or not unit['gold']: continue
            unique = {}
            for analysis in ts[index]['analysis']['analyses']:
                key = canonical(analysis); positive = strict_match(analysis, unit)
                if key not in unique: unique[key] = (analysis, positive)
                elif positive: unique[key] = (unique[key][0], True)
            aa = [x[0] for x in unique.values()]; good = [x[1] for x in unique.values()]
            if not any(good) or all(good): continue
            offsets = [sum(prior.get(k, 0.) * v for k, v in prior_features(ts, index,
                       {**a, 'features': {k: v for k, v in a['features'].items() if k != 'VoiceChain'}}).items()) for a in aa]
            yield {'features': [features(ts, index, a, segmenter) for a in aa], 'good': good, 'offsets': offsets}


def install(rt, model, model_hash):
    def visit(selector):
        if isinstance(getattr(selector, 'ranker', None), UARanker):
            selector.ranker = WeightedRanker(model, 1.)
            selector.context_fingerprint = fingerprint(model)
        for attr in ('reference_selector', 'reference_ua'):
            child = getattr(selector, attr, None)
            if child is not None: visit(child)
    visit(rt.context_selector)
    rt.context_selector.a123_models['ranker.json'] = model_hash
    if hasattr(rt.context_selector.reference_selector, 'ranker'):
        raise ValueError('LEGACY_REFERENCE_MUST_NOT_GAIN_UA')


def evaluate(rt, refs, raws, epoch):
    rows = []; blocks = 0
    for n, (ref, rec) in enumerate(zip(refs, raws, strict=True), 1):
        raw = rec['raw_output']
        if ref['id'] != rec['id'] or raw['raw'] != ref['text']: raise ValueError('DEV_RAW_MISMATCH')
        out = rt.analyze_prepared(raw)
        if [t['analysis']['analyses'] for t in out['tokens']] != [t['analysis']['analyses'] for t in raw['tokens']]:
            raise ValueError('CANDIDATE_INVENTORY_CHANGED')
        if Runtime.reconstruct(out) != ref['text']: raise ValueError('RECONSTRUCTION_FAILED')
        if not all(t['analysis']['search_complete'] for t in out['tokens']): raise ValueError('INCOMPLETE_SEARCH')
        validate_graph(out); blocks += verify_objective(rt.context_selector, out)
        rows.extend(measure(ref, out))
        if n % 50 == 0: log('A1_DEV', epoch=epoch, sentences=n, total=len(refs))
    return {'counts': summarize(rows), 'verified_objective_blocks': blocks}


def freeze_inputs(folder):
    manifest = folder / 'freeze.json'
    if manifest.exists():
        frozen = read(manifest)
        for local, expected in frozen['copied'].items():
            if digest(folder / local) != expected: raise ValueError('FROZEN_INPUT_CHANGED')
        for name, expected in frozen['source_code'].items():
            if digest(ROOT / name) != expected: raise ValueError('SOURCE_CODE_CHANGED')
        return frozen
    sources = {
        'train-features.jsonl.gz': 'results_a123/fit/large/features.jsonl.gz',
        'dev.jsonl': 'training/a1-large-v1/dev.jsonl',
        'dev-raw.jsonl.gz': 'results_a123/raw/dev.jsonl.gz',
        'prior.json': 'models/context-ranker.json',
        'initial-ranker.json': 'models/a123/large/ranker.json',
        'views.json': 'models/a123/large/views.json',
        'ngram.json': 'models/a123/large/ngram.json',
        'old-fit.json': 'results_a123/fit/large/summary.json',
        'old-dev.json': 'results_a123/eval/a1-large/dev/summary.json',
        'epoch-protocol.json': 'training_controls/a1_epoch/protocol.json',
        'control-protocol.json': 'training_controls/e70p9/protocol.json',
    }
    data_manifest = read(ROOT / 'training/a1-large-v1/manifest.json')
    for split in ('train', 'dev'):
        if digest(ROOT / 'training/a1-large-v1' / (split + '.jsonl')) != data_manifest['files'][split + '.jsonl']:
            raise ValueError('SOURCE_SPLIT_HASH_MISMATCH')
    prep = read(ROOT / 'results_a123/fit/prepare-summary.json')
    if digest(ROOT / 'results_a123/fit/train-candidates.jsonl.gz') != prep['cache_sha256']:
        raise ValueError('TRAIN_CANDIDATE_HASH_MISMATCH')
    raw_meta = read(ROOT / 'results_a123/raw/dev-receipt.json')
    if digest(ROOT / sources['dev-raw.jsonl.gz']) != raw_meta['sha256'] or data_manifest['files']['dev.jsonl'] != raw_meta['reference_sha256']:
        raise ValueError('DEV_CACHE_HASH_MISMATCH')
    previous = read(ROOT / sources['old-fit.json'])
    for name, expected in previous['source_hashes'].items():
        if digest(ROOT / name) != expected: raise ValueError('PREVIOUS_FEATURE_IMPLEMENTATION_CHANGED')
    if digest(ROOT / sources['initial-ranker.json']) != previous['model_sha256']:
        raise ValueError('INITIAL_MODEL_CHANGED')
    copied = {}
    for name, source in sources.items():
        shutil.copyfile(ROOT / source, folder / name)
        copied[name] = digest(folder / name)
        if copied[name] != digest(ROOT / source): raise ValueError('INPUT_COPY_FAILED')
    code = {str(Path(m.__file__).resolve().relative_to(ROOT)).replace('\\', '/'): digest(m.__file__)
            for m in list(sys.modules.values()) if getattr(m, '__file__', None)
            and Path(m.__file__).suffix == '.py' and Path(m.__file__).resolve().is_relative_to(ROOT)
            and not Path(m.__file__).resolve().relative_to(ROOT).parts[0].startswith('.deps')}
    frozen = {'copied': copied, 'sources': sources, 'source_code': code,
              'train_sha256': data_manifest['files']['train.jsonl'], 'train_candidate_sha256': prep['cache_sha256'],
              'TEST_or_CALIB_opened': False}
    atomic_json(manifest, frozen)
    return frozen


def checkpoint(work, prior, vocab, w, m, v, step, rng, epoch, freeze_hash, audit):
    weights = dict(prior)
    for name, index in vocab.items(): weights[name] = weights.get(name, 0.) + float(w[index])
    model = {'version': f'A1-epoch-large-v1-E{epoch:02d}', 'weights': weights,
             'inference_scale': 1., 'freeze_sha256': freeze_hash, 'epoch': epoch,
             'TRAIN_only_weight_updates': True, 'DEV_used_for_selection': True}
    atomic_json(work / 'ranker.json', model)
    temporary = work / 'trainer-state.tmp'
    with temporary.open('wb') as f:
        np.savez_compressed(f, residual=w, adam_m=m, adam_v=v, step=np.asarray(step),
                            metadata=np.asarray(json.dumps({'epoch': epoch, 'rng': rng.bit_generator.state,
                                'freeze_sha256': freeze_hash}, ensure_ascii=False)))
        f.flush(); os.fsync(f.fileno())
    os.replace(temporary, work / 'trainer-state.npz')
    atomic_json(work / 'audit.json', audit)
    return model, {'weights': work / 'ranker.json', 'trainer_state': work / 'trainer-state.npz', 'audit': work / 'audit.json'}


def saved_artifacts(run, epoch):
    for copy_name in ('copy-a', 'copy-b'):
        folder = run.root / copy_name / f'epoch-{epoch:06d}'
        try:
            meta = read(folder / 'manifest.json')
            if digest(folder / 'state.json') != meta['state_sha256']: continue
            if all(digest(folder / x['file']) == x['sha256'] for x in meta['artifacts'].values()):
                return {k: folder / x['file'] for k, x in meta['artifacts'].items()}
        except (OSError, ValueError, KeyError): pass
    raise ValueError('NO_VALID_RESUME_COPY')


def main(run_id, through_epoch):
    if not 1 <= through_epoch <= 70: raise ValueError('EPOCH_LIMIT')
    run = open_run(run_id, 'A1')
    lock = run.root / '.trainer.lock'
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    with os.fdopen(fd, 'w') as f: f.write(str(os.getpid()))
    try:
        work = run.root / 'work'; work.mkdir(exist_ok=True)
        inputs = run.root / 'inputs'; inputs.mkdir(exist_ok=True)
        progress_path = run.root / 'progress.json'
        def progress(status, **values):
            atomic_json(progress_path, {'status': status, 'run_id': run_id, 'pid': os.getpid(),
                                       'time_unix': time.time(), **values})
        progress('PREPARING'); log('A1_PREPARING', run_id=run_id, through_epoch=through_epoch)
        if shutil.disk_usage(run.root).free < 6 * 1024**3: raise OSError('INSUFFICIENT_PREPARATION_SPACE')
        freeze_inputs(inputs); freeze_hash = digest(inputs / 'freeze.json')
        config = read(inputs / 'epoch-protocol.json')
        vocab = vocabulary(inputs / 'train-features.jsonl.gz')
        train = matrix(records(inputs / 'train-features.jsonl.gz'), vocab)
        prior = read(inputs / 'prior.json')['weights']; initial = read(inputs / 'initial-ranker.json')
        if (len(train[1]), len(vocab), train[0].shape[0], train[0].nnz) != (55129, 243304, 208402, 9289727):
            raise ValueError('TRAIN_MATRIX_CONTRACT')
        refs = [json.loads(line) for line in (inputs / 'dev.jsonl').read_text(encoding='utf-8').splitlines()]
        raws = list(records(inputs / 'dev-raw.jsonl.gz'))
        dev = matrix(feature_rows(refs, raws, prior), vocab)
        atomic_json(work / 'vocabulary.json', vocab)
        log('A1_MATRIX_READY', examples=len(train[1]), features=len(vocab), dev_loss_examples=len(dev[1]))
        rng = np.random.default_rng(config['optimizer']['seed'])
        w = np.asarray([initial['weights'].get(k, 0.) - prior.get(k, 0.) for k in vocab])
        m = np.zeros_like(w); v = np.zeros_like(w); step = 0
        rt = Tokenizer('large')
        if any(rt.context_selector.a123_models[n] != digest(inputs / ('initial-ranker.json' if n == 'ranker.json' else n))
               for n in ('ranker.json', 'views.json', 'ngram.json')):
            raise ValueError('FIXED_INFERENCE_MODEL_CHANGED')
        if run.state is None:
            reproduced = objective(w, train, 1. / len(train[1]), gradient=False) * len(train[1])
            if not np.isclose(reproduced, read(inputs / 'old-fit.json')['loss'], rtol=1e-10, atol=1e-6):
                raise ValueError('INITIAL_OBJECTIVE_NOT_REPRODUCED')
            progress('BASELINE_E00_EVALUATION')
            initial_audit = evaluate(rt, refs, raws, 0)
            if initial_audit['counts'] != read(inputs / 'old-dev.json')['counts']:
                raise ValueError('BASELINE_DEV_NOT_REPRODUCED')
            initial_audit.update(train_loss=objective(w, train, gradient=False), dev_loss=objective(w, dev, gradient=False))
            _, artifacts = checkpoint(work, prior, vocab, w, m, v, step, rng, 0, freeze_hash, initial_audit)
            run.seed_baseline(train_loss=initial_audit['train_loss'], dev_loss=initial_audit['dev_loss'],
                              dev_correct=initial_audit['counts']['preferred_lemma_pos'], dev_total=4070, artifacts=artifacts)
            log('A1_BASELINE_VERIFIED', **initial_audit['counts'])
        else:
            if run.state['stop']: raise ValueError('A1_ALREADY_STOPPED')
            saved = saved_artifacts(run, run.state['epoch'])
            with np.load(saved['trainer_state'], allow_pickle=False) as state:
                metadata = json.loads(str(state['metadata']))
                if metadata['freeze_sha256'] != freeze_hash or metadata['epoch'] != run.state['epoch']:
                    raise ValueError('RESUME_METADATA_MISMATCH')
                w = state['residual'].copy(); m = state['adam_m'].copy(); v = state['adam_v'].copy()
                step = int(state['step']); rng.bit_generator.state = metadata['rng']
        baseline = read(saved_artifacts(run, 0)['audit'])['counts']
        for epoch in range(run.state['epoch'] + 1, through_epoch + 1):
            freeze_inputs(inputs)
            progress('TRAINING', epoch=epoch)
            log('A1_EPOCH_BEGIN', epoch=epoch, max_epochs=70)
            step, seen = train_epoch(w, m, v, step, train, rng, config['optimizer'],
                lambda seen, total: log('A1_BATCH', epoch=epoch, examples_seen=seen, total=total))
            train_loss = objective(w, train, gradient=False); dev_loss = objective(w, dev, gradient=False)
            model, artifacts = checkpoint(work, prior, vocab, w, m, v, step, rng, epoch, freeze_hash, {})
            install(rt, model, digest(artifacts['weights']))
            progress('DEV_EVALUATION', epoch=epoch, train_examples_seen=seen)
            audit = evaluate(rt, refs, raws, epoch)
            c = audit['counts']
            if c['words'] != 4070: raise ValueError('DEV_DENOMINATOR_CHANGED')
            safe = (c['preferred_declared_features'] >= baseline['preferred_declared_features']
                    and c['legacy_selected_lemma_wrong'] <= baseline['legacy_selected_lemma_wrong'])
            audit.update(epoch=epoch, train_examples_seen=seen, train_loss=train_loss, dev_loss=dev_loss,
                         safety_passed=safe, safety_reference_epoch=0)
            atomic_json(work / 'audit.json', audit)
            freeze_inputs(inputs)
            result = run.complete_epoch(epoch, train_loss=train_loss, dev_loss=dev_loss,
                dev_correct=c['preferred_lemma_pos'], dev_total=4070, safe=safe, artifacts=artifacts)
            # Keep exact aggregate publication files per epoch for connector-assisted delivery.
            outbox = run.root / 'github-outbox' / f'epoch-{epoch:06d}'
            outbox.mkdir(parents=True, exist_ok=False)
            for name, source in run._journal_files().items(): shutil.copyfile(source, outbox / name)
            atomic_json(outbox / 'ready.json', {'epoch': epoch, 'files': {n: digest(outbox / n) for n in run._journal_files()},
                                               'cli_synced': result['github_synced']})
            log('A1_EPOCH_COMPLETE', **{k: result[k] for k in ('epoch', 'dev_correct', 'dev_total', 'patience_count', 'overfit_count', 'best_epoch', 'safe', 'stop', 'github_synced')})
            progress('EPOCH_COMPLETE', epoch=epoch, best_epoch=result['best_epoch'])
            if result['stop']: break
        chosen = run.best_checkpoint()
        if chosen is None: raise ValueError('NO_SAFE_CHECKPOINT')
        selected_model = read(chosen['weights'])
        install(rt, selected_model, digest(chosen['weights']))
        selected_path = run.root / 'selected-ranker.json'
        shutil.copyfile(chosen['weights'], selected_path)
        final_status = 'STOPPED_WITH_BEST' if run.state['stop'] else 'PAUSED_AT_REQUESTED_EPOCH'
        atomic_json(run.root / 'selection.json', {'status': final_status, 'selected_epoch': run.state['best_epoch'],
                    'selected_model_sha256': digest(selected_path), 'latest_epoch': run.state['epoch'],
                    'A3_started': False, 'A2_started': False, 'default_promoted': False})
        progress(final_status, epoch=run.state['epoch'], best_epoch=run.state['best_epoch'])
        log('A1_INVOCATION_COMPLETE', status=final_status, epoch=run.state['epoch'], best_epoch=run.state['best_epoch'])
    except Exception as exc:
        atomic_json(run.root / 'failure.json', {'type': type(exc).__name__, 'message': str(exc),
                    'last_committed_epoch': run.state['epoch'] if run.state else None})
        raise
    finally:
        lock.unlink()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--through-epoch', type=int, default=1)
    args = parser.parse_args(); main(args.run_id, args.through_epoch)
