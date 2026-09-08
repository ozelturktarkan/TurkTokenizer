"""A3 on selected A1 E05, isolated from historical trainers and model defaults."""
import os
for variable in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[variable] = '1'
import argparse
import collections
import gzip
import hashlib
import json
import re
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / '.deps-s06'), str(ROOT / '.deps-s05six')]
import bootstrap
import numpy as np
from common import Runtime, compatible
from s06e_a123 import Tokenizer, WeightedRanker, CHANNELS
from s06e_r5 import Tokenizer as RawTokenizer
from s05_ua_features import UARanker
from r5.engine import fingerprint
from a123_ranking import contrast
from a123_measurement import measure, summarize
from a1_corpus import norm
from audit_s05_ua_scores import capture_configurations
from evaluate_global import validate_graph
from validate_s06 import verify_objective
from training_controls.e70p9.epoch_control import read, digest, atomic_json
from training_controls.e70p9.runtime import open_run
from training_controls.a1_epoch.train import saved_artifacts
from .numerics import loss, train_epoch


def key(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def records(path):
    with gzip.open(path, 'rt', encoding='utf-8') as stream:
        for line in stream:
            yield json.loads(line)


def save_records(path, rows):
    temporary = path.with_name(path.name + '.writing')
    with gzip.open(temporary, 'wt', encoding='utf-8', compresslevel=6) as out:
        for row in rows:
            out.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + '\n')
    os.replace(temporary, path)


def install_a1(rt, model, model_hash):
    def visit(selector):
        if isinstance(getattr(selector, 'ranker', None), UARanker):
            selector.ranker = WeightedRanker(model, rt.weights[0])
            selector.context_fingerprint = fingerprint(model)
        for attr in ('reference_selector', 'reference_ua'):
            child = getattr(selector, attr, None)
            if child is not None:
                visit(child)
    visit(rt.context_selector)
    rt.context_selector.a123_models['ranker.json'] = model_hash
    if hasattr(rt.context_selector.reference_selector, 'ranker'):
        raise ValueError('LEGACY_REFERENCE_MUST_NOT_GAIN_UA')


def runtime(theta, model, model_hash):
    rt = Tokenizer('large', theta.tolist())
    install_a1(rt, model, model_hash)
    capture_configurations(rt)
    return rt


def freeze(folder, parent, config):
    manifest = folder / 'freeze.json'
    if manifest.exists():
        frozen = read(manifest)
        for n, expected in frozen['copies'].items():
            if digest(folder / n) != expected:
                raise ValueError('A3_FROZEN_INPUT_CHANGED:' + n)
        for n, expected in frozen['source_code'].items():
            if digest(ROOT / n) != expected:
                raise ValueError('A3_SOURCE_CODE_CHANGED:' + n)
        return frozen
    selection = read(parent / 'selection.json')
    expected = config['parent_model_sha256']
    if selection['status'] != 'STOPPED_WITH_BEST' or selection['selected_epoch'] != 5 or selection['selected_model_sha256'] != expected:
        raise ValueError('EXPECTED_SELECTED_A1_E05')
    if digest(parent / 'selected-ranker.json') != expected:
        raise ValueError('A1_SELECTED_WEIGHT_HASH_MISMATCH')
    original = read(parent / 'inputs/freeze.json')
    for n, h in original['source_code'].items():
        if digest(ROOT / n) != h:
            raise ValueError('A1_FROZEN_SOURCE_CHANGED:' + n)
    sources = {
        'a1-ranker.json': parent / 'selected-ranker.json',
        'a1-audit.json': parent / 'copy-a/epoch-000005/audit.checkpoint',
        'dev.jsonl': parent / 'inputs/dev.jsonl',
        'dev-raw.jsonl.gz': parent / 'inputs/dev-raw.jsonl.gz',
        'replay.json': ROOT / 'training/a1-large-v1/a3-replay.json',
        'hard-negatives.jsonl': ROOT / 'training/a1a2a3-v0.1/hard-negatives.jsonl',
        'documents.jsonl': ROOT / 'training/a1a2a3-v0.1/documents.jsonl',
        'epoch-protocol.json': Path(__file__).with_name('protocol.json'),
        'control-protocol.json': ROOT / 'training_controls/e70p9/protocol.json',
    }
    data_manifest = read(ROOT / 'training/a1-large-v1/manifest.json')
    train_path = ROOT / 'training/a1-large-v1/train.jsonl'
    if digest(train_path) != data_manifest['files']['train.jsonl']:
        raise ValueError('TRAIN_SPLIT_CHANGED')
    train_ids = {json.loads(line)['id'] for line in train_path.read_text(encoding='utf-8').splitlines()}
    replay = read(sources['replay.json'])
    if replay['training_cache_sha256'] != original['train_candidate_sha256']:
        raise ValueError('REPLAY_CACHE_MISMATCH')
    if not {r['context_id'] for r in replay['examples']} <= train_ids:
        raise ValueError('REPLAY_OUTSIDE_TRAIN')
    for n in ('dev.jsonl', 'dev-raw.jsonl.gz'):
        if digest(sources[n]) != original['copied'][n]:
            raise ValueError('A1_DEV_CHANGED')
    copied = {}
    for n, source in sources.items():
        shutil.copyfile(source, folder / n)
        copied[n] = digest(folder / n)
        if copied[n] != digest(source):
            raise ValueError('INPUT_COPY_FAILED')
    code = dict(original['source_code'])
    for n in ('a123_ranking.py', 'a1_corpus.py', 'tools/audit_s05_ua_scores.py',
              'training_controls/a3_epoch/__init__.py', 'training_controls/a3_epoch/train.py',
              'training_controls/a3_epoch/numerics.py', 'training_controls/a3_epoch/protocol.json'):
        code[n] = digest(ROOT / n)
    frozen = {'copies': copied, 'source_code': code, 'parent_model_sha256': expected,
              'train_sha256': data_manifest['files']['train.jsonl'], 'TEST_CALIB_opened': False}
    atomic_json(manifest, frozen)
    return frozen


def train_targets(inputs, refs):
    rows = read(inputs / 'replay.json')['examples']
    docs = {r['document_id']: r['raw'] for r in
            (json.loads(line) for line in (inputs / 'documents.jsonl').read_text(encoding='utf-8').splitlines())}
    for line in (inputs / 'hard-negatives.jsonl').read_text(encoding='utf-8').splitlines():
        row = json.loads(line)
        rows.append({**{k: row[k] for k in ('id', 'start', 'end', 'surface', 'positive_analysis_ids', 'gold', 'label_scope')},
                     'context_id': 'MAIN:' + row['document_id'], 'raw': docs[row['document_id']], 'source': 'MAIN_252'})
    if dict(collections.Counter(r['source'] for r in rows)) != {'BROAD_TRAIN_REPLAY': 512, 'MAIN_252': 252}:
        raise ValueError('TRAIN_TARGET_COUNTS')
    if len({r['id'] for r in rows}) != 764:
        raise ValueError('DUPLICATE_TRAIN_TARGET')
    dev_norms = {norm(r['text']) for r in refs}
    if any(norm(r['raw']) in dev_norms for r in rows):
        raise ValueError('TRAIN_DEV_EXACT_TEXT_OVERLAP')
    grouped = collections.defaultdict(list)
    for row in rows:
        grouped[row['context_id']].append(row)
    if len(grouped) != 584:
        raise ValueError('TRAIN_CONTEXT_COUNTS')
    return grouped


def dev_targets(refs, raws):
    result = {}
    for ref, rec in zip(refs, raws, strict=True):
        if ref['id'] != rec['id']:
            raise ValueError('DEV_ID_MISMATCH')
        spans = {(t['start'], t['end']): t for t in rec['raw_output']['tokens']}
        options = []
        for unit in ref['units']:
            t = spans.get((unit['start'], unit['end']))
            if not t or unit['punctuation'] or not unit['gold']:
                continue
            aa = t['analysis']['analyses']
            positive = [a['analysis_id'] for a in aa if compatible(a, unit['gold'], False)]
            if positive and len(positive) < len(aa):
                options.append({'id': ref['id'] + ':' + str(unit['start']) + ':' + str(unit['end']),
                                'context_id': ref['id'], 'start': unit['start'], 'end': unit['end'],
                                'surface': t['raw'], 'positive_analysis_ids': positive,
                                'source': 'FIXED_DEV_PROBE', 'label_scope': 'LEMMA_POS'})
        if options:
            result[ref['id']] = [min(options, key=lambda r: key(r['id']))]
    return result


def check_output(rt, raw, out):
    if [t['analysis']['analyses'] for t in out['tokens']] != [t['analysis']['analyses'] for t in raw['tokens']]:
        raise ValueError('CANDIDATES_CHANGED')
    if Runtime.reconstruct(out) != raw['raw']:
        raise ValueError('RECONSTRUCTION_FAILED')
    if not all(t['analysis']['search_complete'] for t in out['tokens']):
        raise ValueError('INCOMPLETE_SEARCH')
    validate_graph(out)
    return verify_objective(rt.context_selector, out)


def mine(rt, raws, grouped, progress, phase, epoch):
    mined = []
    wanted = set(grouped)
    for count, rec in enumerate(raws, 1):
        context = rec['id']
        if context not in grouped:
            continue
        wanted.remove(context)
        raw = rec['raw_output']
        rt.context_selector.audit_captured.clear()
        out = rt.analyze_prepared(raw)
        check_output(rt, raw, out)
        spans = {(t['start'], t['end']): i for i, t in enumerate(out['tokens'])}
        for target in grouped[context]:
            index = spans.get((target['start'], target['end']))
            if index is None or out['tokens'][index]['raw'] != target['surface']:
                raise ValueError('TARGET_SPAN_MISMATCH')
            ids = {a['analysis_id'] for a in out['tokens'][index]['analysis']['analyses']}
            positive = set(target['positive_analysis_ids'])
            if not positive or not positive < ids:
                raise ValueError('TARGET_CANDIDATES_CHANGED')
            value = contrast(rt, out, index, positive)
            if value['status'] != 'OK':
                raise ValueError('NO_VALID_STRUCTURED_CONTRAST')
            value.update(id=target['id'], source=target['source'], label_scope=target['label_scope'])
            mined.append(value)
        if count % 25 == 0:
            progress(phase, epoch=epoch, contexts=count, total_contexts=len(raws), targets=len(mined))
    if wanted or len(mined) != sum(map(len, grouped.values())):
        raise ValueError('INCOMPLETE_MINING_PASS')
    return mined


def matrix(rows):
    X = np.asarray([r['x'] for r in rows]); b = np.asarray([r['constant'] for r in rows])
    if X.shape != (len(rows), 5) or not np.isfinite(X).all() or not np.isfinite(b).all():
        raise ValueError('INVALID_CONTRAST_MATRIX')
    return X, b


def evaluate(rt, refs, raws, progress, epoch):
    rows = []; blocks = 0
    for n, (ref, rec) in enumerate(zip(refs, raws, strict=True), 1):
        if ref['id'] != rec['id'] or rec['raw_output']['raw'] != ref['text']:
            raise ValueError('DEV_CACHE_MISMATCH')
        rt.context_selector.audit_captured.clear()
        out = rt.analyze_prepared(rec['raw_output'])
        blocks += check_output(rt, rec['raw_output'], out)
        rows.extend(measure(ref, out))
        if n % 25 == 0:
            progress('DEV_EVALUATION', epoch=epoch, sentences=n, total_sentences=len(refs))
    return {'counts': summarize(rows), 'verified_objective_blocks': blocks}


def checkpoint(work, inputs, theta, m, v, step, rng, epoch, freeze_hash, audit):
    model = {'version': 'A3-epoch-E05-v1', 'epoch': epoch, 'weights': theta.tolist(), 'channels': list(CHANNELS),
             'A1_model_sha256': digest(inputs / 'a1-ranker.json'), 'freeze_sha256': freeze_hash,
             'MAIN_training_exposed': epoch > 0, 'A2_started': False, 'default_promoted': False}
    atomic_json(work / 'ranking.json', model)
    temporary = work / 'trainer-state.writing'
    with temporary.open('wb') as f:
        np.savez_compressed(f, theta=theta, adam_m=m, adam_v=v, step=np.asarray(step),
                            metadata=np.asarray(json.dumps({'epoch': epoch, 'rng': rng.bit_generator.state,
                                                            'freeze_sha256': freeze_hash})))
        f.flush(); os.fsync(f.fileno())
    os.replace(temporary, work / 'trainer-state.npz')
    atomic_json(work / 'audit.json', audit)
    return {'weights': work / 'ranking.json', 'a1_ranker': inputs / 'a1-ranker.json',
            'trainer_state': work / 'trainer-state.npz', 'audit': work / 'audit.json',
            'fixed_probes': inputs / 'fixed-probes.npz'}


def publish_ready(run, epoch, synced):
    outbox = run.root / 'github-outbox' / f'epoch-{epoch:06d}'
    if not (outbox / 'ready.json').exists():
        outbox.mkdir(parents=True, exist_ok=True)
        for n, source in run._journal_files().items():
            shutil.copyfile(source, outbox / n)
        atomic_json(outbox / 'ready.json', {'epoch': epoch, 'files': {n: digest(outbox / n) for n in run._journal_files()},
                                           'cli_synced': bool(synced)})
    return outbox


def publication_acknowledged(outbox):
    ready = read(outbox / 'ready.json')
    if any(digest(outbox / n) != h for n, h in ready['files'].items()):
        raise ValueError('PUBLICATION_OUTBOX_CHANGED')
    if ready['cli_synced']:
        return True
    acknowledgement = outbox / 'published.json'
    if not acknowledgement.exists():
        return False
    ack = read(acknowledgement)
    return (ack.get('epoch') == ready['epoch'] and ack.get('files') == ready['files']
            and ack.get('repository') == 'ozelturktarkan/TurkTokenizer'
            and ack.get('verified') is True and re.fullmatch(r'[0-9a-f]{40}', ack.get('commit', '')) is not None)


def main(run_id, through_epoch):
    if not 1 <= through_epoch <= 70:
        raise ValueError('EPOCH_LIMIT')
    run = open_run(run_id, 'A3')
    lock = run.root / '.trainer.lock'
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    with os.fdopen(fd, 'w') as f:
        f.write(str(os.getpid()))
    def progress(status, **values):
        message = {'status': status, 'run_id': run_id, 'pid': os.getpid(), 'time_unix': time.time(), **values}
        atomic_json(run.root / 'progress.json', message)
        print(json.dumps(message, ensure_ascii=False, allow_nan=False), flush=True)
    def select(status):
        chosen = run.best_checkpoint()
        if chosen is None:
            raise ValueError('NO_SAFE_CHECKPOINT')
        shutil.copyfile(chosen['weights'], run.root / 'selected-ranking.json')
        atomic_json(run.root / 'selection.json', {'status': status, 'selected_epoch': run.state['best_epoch'],
                    'selected_model_sha256': digest(run.root / 'selected-ranking.json'), 'latest_epoch': run.state['epoch'],
                    'A1_model_sha256': digest(chosen['a1_ranker']), 'A2_started': False, 'default_promoted': False})
    def publication_gate():
        outbox = publish_ready(run, run.state['epoch'], read(run.root / 'github-sync.json')['synced'])
        if publication_acknowledged(outbox):
            return True
        progress('WAITING_FOR_GITHUB_ACK', epoch=run.state['epoch'], best_epoch=run.state['best_epoch'])
        deadline = time.monotonic() + config['publication_wait_seconds']
        while time.monotonic() < deadline:
            if publication_acknowledged(outbox):
                return True
            time.sleep(1)
        select('PAUSED_FOR_PUBLICATION')
        progress('PAUSED_FOR_PUBLICATION', epoch=run.state['epoch'], best_epoch=run.state['best_epoch'])
        return False
    try:
        config = read(Path(__file__).with_name('protocol.json'))
        parent = run.root.parent / 'A1'
        if run_id != config['parent_run']:
            raise ValueError('EXPECTED_PARENT_RUN')
        inputs = run.root / 'inputs'; inputs.mkdir(exist_ok=True)
        work = run.root / 'work'; work.mkdir(exist_ok=True)
        if shutil.disk_usage(run.root).free < 6 * 1024 ** 3:
            raise OSError('INSUFFICIENT_V_SPACE')
        progress('PREPARING')
        freeze(inputs, parent, config)
        model = read(inputs / 'a1-ranker.json'); model_hash = digest(inputs / 'a1-ranker.json')
        refs = [json.loads(line) for line in (inputs / 'dev.jsonl').read_text(encoding='utf-8').splitlines()]
        dev_raws = list(records(inputs / 'dev-raw.jsonl.gz'))
        grouped = train_targets(inputs, refs)
        raw_path = inputs / 'train-raw.jsonl.gz'
        if not raw_path.exists():
            raw_rt = RawTokenizer(context_enabled=False)
            def raw_records():
                for n, (context, targets) in enumerate(grouped.items(), 1):
                    out = raw_rt.analyze_sentence(targets[0]['raw'])
                    yield {'id': context, 'raw_output': out}
                    if n % 25 == 0:
                        progress('PREPARING_TRAIN_CANDIDATES', contexts=n, total_contexts=len(grouped))
            save_records(raw_path, raw_records())
        raw_hash_path = inputs / 'train-raw-sha256.json'
        if not raw_hash_path.exists():
            atomic_json(raw_hash_path, {'sha256': digest(raw_path)})
        if digest(raw_path) != read(raw_hash_path)['sha256']:
            raise ValueError('TRAIN_RAW_CACHE_CHANGED')
        train_raws = list(records(raw_path))
        theta = np.ones(5); m = np.zeros(5); v = np.zeros(5); step = 0
        rng = np.random.default_rng(config['optimizer']['seed'])
        probe_path = inputs / 'fixed-probes.npz'
        if not probe_path.exists():
            rt = runtime(theta, model, model_hash)
            train_probe = mine(rt, train_raws, grouped, progress, 'E00_TRAIN_PROBE', 0)
            dev_probe = mine(rt, dev_raws, dev_targets(refs, dev_raws), progress, 'E00_DEV_PROBE', 0)
            train_X, train_b = matrix(train_probe); dev_X, dev_b = matrix(dev_probe)
            save_records(inputs / 'train-probe.jsonl.gz', train_probe)
            save_records(inputs / 'dev-probe.jsonl.gz', dev_probe)
            with probe_path.open('wb') as f:
                np.savez_compressed(f, train_X=train_X, train_b=train_b, dev_X=dev_X, dev_b=dev_b)
            del rt
        generated_path = inputs / 'generated-sha256.json'
        if not generated_path.exists():
            atomic_json(generated_path, {n: digest(inputs / n) for n in
                ('train-raw.jsonl.gz', 'train-probe.jsonl.gz', 'dev-probe.jsonl.gz', 'fixed-probes.npz')})
        for n, h in read(generated_path).items():
            if digest(inputs / n) != h:
                raise ValueError('A3_FIXED_DIAGNOSTICS_CHANGED')
        freeze_hash = key(digest(inputs / 'freeze.json') + digest(generated_path))
        with np.load(probe_path, allow_pickle=False) as z:
            train_X, train_b, dev_X, dev_b = (z[n].copy() for n in ('train_X', 'train_b', 'dev_X', 'dev_b'))
        baseline = read(inputs / 'a1-audit.json')['counts']
        if run.state is None:
            rt = runtime(theta, model, model_hash)
            audit = evaluate(rt, refs, dev_raws, progress, 0)
            if audit['counts'] != baseline or baseline['words'] != 4070:
                raise ValueError('A1_E05_BASELINE_NOT_REPRODUCED')
            audit.update(train_loss=loss(theta, train_X, train_b)[0], dev_loss=loss(theta, dev_X, dev_b)[0],
                         train_probe_examples=len(train_b), dev_probe_examples=len(dev_b))
            artifacts = checkpoint(work, inputs, theta, m, v, step, rng, 0, freeze_hash, audit)
            run.seed_baseline(train_loss=audit['train_loss'], dev_loss=audit['dev_loss'],
                              dev_correct=baseline['preferred_lemma_pos'], dev_total=4070, artifacts=artifacts)
            del rt
        else:
            saved = saved_artifacts(run, run.state['epoch'])
            with np.load(saved['trainer_state'], allow_pickle=False) as z:
                metadata = json.loads(str(z['metadata']))
                if metadata['freeze_sha256'] != freeze_hash or metadata['epoch'] != run.state['epoch']:
                    raise ValueError('RESUME_METADATA_MISMATCH')
                theta, m, v = (z[n].copy() for n in ('theta', 'adam_m', 'adam_v'))
                step = int(z['step']); rng.bit_generator.state = metadata['rng']
            if run.state['epoch'] > 0 and not publication_gate():
                return
        if not run.state['stop']:
            for epoch in range(run.state['epoch'] + 1, through_epoch + 1):
                freeze(inputs, parent, config)
                if epoch == 1 and np.array_equal(theta, np.ones(5)):
                    # E00 mining used the exact E01 starting weights; no update intervened.
                    mined = list(records(inputs / 'train-probe.jsonl.gz'))
                    X0, b0 = matrix(mined)
                    if not np.allclose(b0 + X0 @ theta, [r['current_gap'] for r in mined], atol=1e-8, rtol=1e-10):
                        raise ValueError('E01_INITIAL_MINING_MISMATCH')
                    progress('TRAIN_MINING_REUSED_E00_IDENTICAL_WEIGHTS', epoch=1, targets=len(mined))
                else:
                    rt = runtime(theta, model, model_hash)
                    mined = mine(rt, train_raws, grouped, progress, 'TRAIN_MINING', epoch)
                    del rt
                X, b = matrix(mined)
                mined_path = run.root / 'mined'; mined_path.mkdir(exist_ok=True)
                save_records(mined_path / f'epoch-{epoch:06d}.jsonl.gz', mined)
                before = loss(theta, X, b, config['regularization'])[0]
                progress('TRAINING', epoch=epoch, targets=len(b))
                step, seen = train_epoch(theta, m, v, step, X, b, rng, config['optimizer'],
                                         config['regularization'], config['bounds'])
                train_loss = loss(theta, train_X, train_b)[0]; dev_loss = loss(theta, dev_X, dev_b)[0]
                rt = runtime(theta, model, model_hash)
                audit = evaluate(rt, refs, dev_raws, progress, epoch)
                del rt
                c = audit['counts']
                if c['words'] != 4070:
                    raise ValueError('DEV_DENOMINATOR_CHANGED')
                safe = (c['preferred_declared_features'] >= baseline['preferred_declared_features']
                        and c['legacy_selected_lemma_wrong'] <= baseline['legacy_selected_lemma_wrong'])
                audit.update(epoch=epoch, train_loss=train_loss, dev_loss=dev_loss, safety_passed=safe,
                             train_examples_seen=seen, train_probe_examples=len(train_b), dev_probe_examples=len(dev_b),
                             remine_preferred_correct=sum(r['current_preferred_correct'] for r in mined),
                             ranking_surrogate_before=before,
                             ranking_surrogate_after=loss(theta, X, b, config['regularization'])[0],
                             weights=theta.tolist(), safety_reference='A1_E05', TEST_CALIB_opened=False)
                artifacts = checkpoint(work, inputs, theta, m, v, step, rng, epoch, freeze_hash, audit)
                freeze(inputs, parent, config)
                for n, h in read(generated_path).items():
                    if digest(inputs / n) != h:
                        raise ValueError('A3_FIXED_DIAGNOSTICS_CHANGED')
                result = run.complete_epoch(epoch, train_loss=train_loss, dev_loss=dev_loss,
                                            dev_correct=c['preferred_lemma_pos'], dev_total=4070, safe=bool(safe), artifacts=artifacts)
                publish_ready(run, epoch, result['github_synced'])
                select('EPOCH_COMPLETE' if not result['stop'] else 'STOPPED_WITH_BEST')
                progress('EPOCH_COMPLETE', epoch=epoch, best_epoch=result['best_epoch'],
                         dev_correct=c['preferred_lemma_pos'], patience=result['patience_count'])
                if not publication_gate():
                    return
                if result['stop']:
                    break
        status = 'STOPPED_WITH_BEST' if run.state['stop'] else 'PAUSED_AT_REQUESTED_EPOCH'
        select(status)
        progress(status, epoch=run.state['epoch'], best_epoch=run.state['best_epoch'])
    except Exception as exc:
        atomic_json(run.root / 'failure.json', {'type': type(exc).__name__, 'message': str(exc),
                                               'last_committed_epoch': run.state['epoch'] if run.state else None})
        progress('FAILED', epoch=run.state['epoch'] if run.state else None, error_type=type(exc).__name__)
        raise
    finally:
        lock.unlink()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--through-epoch', type=int, default=1)
    args = parser.parse_args()
    main(args.run_id, args.through_epoch)
