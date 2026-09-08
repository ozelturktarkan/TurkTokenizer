"""Freeze completed A1/A3, select A2 on CALIB, verify and double-back up on V."""
import os
for variable in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[variable] = '1'
import argparse
import copy
import gzip
import json
import math
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / '.deps-s06'), str(ROOT / '.deps-s05six')]
import bootstrap
from common import Runtime
from s06e_a123 import Tokenizer, apply_a2
from a123_measurement import measure, summarize, a2_accept, a2_summary
from training_controls.a3_epoch.train import install_a1, check_output
from training_controls.e70p9.epoch_control import read, digest, atomic_json

BASE = Path(r'V:\TurkTokenizer\Yedekler\A123-E70-P9-OF3\runs')
HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def choose(rows, grid, target):
    for row in rows:
        for field in ('lemma_margin', 'feature_margin'):
            value = row[field]
            require(value is None or math.isfinite(value), 'NONFINITE_MARGIN')
    results = [a2_summary(rows, {'lemma_threshold': lm, 'feature_threshold': fm})
               for lm in grid for fm in grid]
    feasible = [r for r in results if r['accepted'] > 0
                and r['lemma_precision_pct'] >= target and r['feature_precision_pct'] >= target]
    best = min(feasible, key=lambda r: (-r['accepted'], -r['feature_precision_pct'],
               -r['lemma_precision_pct'], sum(r['thresholds'].values()),
               r['thresholds']['lemma_threshold'])) if feasible else None
    return results, best


def validate_application(ref, original, config):
    # Always apply to an untouched output: the historical gate retains legacy state.
    rows = measure(ref, original)
    result = apply_a2(copy.deepcopy(original), config)
    require([t['context_decision'].get('preferred_analysis') for t in original['tokens']] ==
            [t['context_decision'].get('preferred_analysis') for t in result['tokens']],
            'A2_CHANGED_PREFERRED_CANDIDATES')
    require([t['analysis']['analyses'] for t in original['tokens']] ==
            [t['analysis']['analyses'] for t in result['tokens']], 'A2_CHANGED_INVENTORY')
    require(Runtime.reconstruct(result) == ref['text'], 'A2_RECONSTRUCTION_FAILED')
    spans = {(t['start'], t['end']): t for t in result['tokens']}
    accepted = 0
    for row in rows:
        token = spans.get((row['start'], row['end']))
        live = bool(token and token.get('decision_layers', {}).get('A2', {}).get('accepted'))
        require(live == a2_accept(row, config), 'ONLINE_OFFLINE_ACCEPTANCE_MISMATCH')
        if live:
            decision = token['context_decision']
            require(decision['selected_analysis'] == decision['preferred_analysis'], 'WRONG_A2_SELECTION')
        accepted += live
    return result, accepted


def verify_freeze(folder, frozen):
    for name, expected in frozen['input_sha256'].items():
        require(digest(folder / 'inputs' / name) == expected, 'FROZEN_INPUT_CHANGED:' + name)
    for name, expected in frozen['source_sha256'].items():
        require(digest(ROOT / name) == expected, 'SOURCE_CHANGED:' + name)
        require(digest(folder / 'source' / name) == expected, 'SOURCE_COPY_CHANGED:' + name)
    for name, expected in frozen['runtime_model_sha256'].items():
        require(digest(ROOT / name) == expected, 'RUNTIME_MODEL_CHANGED:' + name)


def freeze(folder, config):
    parent = folder.parent
    a1, a3 = parent / 'A1', parent / 'A3'
    for stage, epoch, file in ((a1, 5, 'selected-ranker.json'), (a3, 0, 'selected-ranking.json')):
        selection = read(stage / 'selection.json')
        expected = config[stage.name + '_model_sha256']
        require(selection['status'] == 'STOPPED_WITH_BEST' and selection['selected_epoch'] == epoch,
                'PARENT_SELECTION_CHANGED')
        require(selection['selected_model_sha256'] == expected and digest(stage / file) == expected,
                'PARENT_WEIGHT_CHANGED')
    require(read(a3 / 'selected-ranking.json')['weights'] == [1] * 5, 'EXPECTED_IDENTITY_A3')
    original = read(a1 / 'inputs/freeze.json')
    runtime_models = {original['sources'][n]: original['copied'][n]
                      for n in ('initial-ranker.json', 'views.json', 'ngram.json', 'prior.json')}
    for name, expected in runtime_models.items():
        require(digest(ROOT / name) == expected, 'PARENT_RUNTIME_CHANGED:' + name)
    sources = dict(read(a3 / 'inputs/freeze.json')['source_code'])
    for file in HERE.iterdir():
        if file.suffix in ('.py', '.json', '.md'):
            sources[file.relative_to(ROOT).as_posix()] = digest(file)
    sources['A1-A2-A3-kosu-v1.json'] = digest(ROOT / 'A1-A2-A3-kosu-v1.json')
    require(read(ROOT / 'A1-A2-A3-kosu-v1.json')['A2_threshold_grid'] == config['threshold_grid'],
            'PREDECLARED_GRID_CHANGED')
    paths = {
        'a1-ranker.json': a1 / 'selected-ranker.json',
        'a3-ranking.json': a3 / 'selected-ranking.json',
        'a1-selection.json': a1 / 'selection.json', 'a3-selection.json': a3 / 'selection.json',
        'a1-freeze.json': a1 / 'inputs/freeze.json', 'a3-freeze.json': a3 / 'inputs/freeze.json',
        'calib.jsonl': ROOT / 'training/a1-large-v1/calib.jsonl',
        'calib-raw.jsonl.gz': ROOT / 'results_a123/raw/calib.jsonl.gz',
        'calib-receipt.json': ROOT / 'results_a123/raw/calib-receipt.json',
        'protocol.json': HERE / 'protocol.json',
    }
    for name in ('initial-ranker.json', 'views.json', 'ngram.json', 'prior.json'):
        paths[name] = ROOT / original['sources'][name]
    receipt = read(paths['calib-receipt.json'])
    require(receipt['contains_reference_labels'] is False and receipt['sentences'] == config['sentences'],
            'INVALID_CALIB_RECEIPT')
    require(digest(paths['calib.jsonl']) == receipt['reference_sha256'] == config['calib_reference_sha256'],
            'CALIB_REFERENCE_CHANGED')
    require(digest(paths['calib-raw.jsonl.gz']) == receipt['sha256'] == config['calib_raw_sha256'],
            'CALIB_RAW_CHANGED')
    require(shutil.disk_usage(folder).free > config['minimum_free_bytes'] +
            3 * sum(p.stat().st_size for p in paths.values()) + 100_000_000, 'BACKUP_SPACE_LOW')
    (folder / 'inputs').mkdir()
    for name, path in paths.items():
        shutil.copyfile(path, folder / 'inputs' / name)
        require(digest(path) == digest(folder / 'inputs' / name), 'INPUT_COPY_FAILED')
    for name, expected in sources.items():
        require(digest(ROOT / name) == expected, 'PARENT_SOURCE_CHANGED:' + name)
        dest = folder / 'source' / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, dest)
    frozen = {'input_sha256': {n: digest(folder / 'inputs' / n) for n in paths},
              'source_sha256': sources, 'runtime_model_sha256': runtime_models,
              'frozen_at_unix': time.time(), 'TEST_opened': False, 'default_promoted': False}
    atomic_json(folder / 'freeze.json', frozen)
    verify_freeze(folder, frozen)
    return frozen


def main():
    config = read(HERE / 'protocol.json')
    folder = BASE / config['parent_run'] / 'A2'
    require(not folder.exists(), 'REFUSING_TO_OVERWRITE_A2_RUN')
    require(folder.parent.is_dir() and folder.resolve().is_relative_to(BASE.resolve()), 'UNSAFE_RUN_PATH')
    folder.mkdir()
    started = time.monotonic()

    def progress(status, **extra):
        value = {'stage': 'A2', 'status': status, 'time_unix': time.time(),
                 'seconds': round(time.monotonic() - started, 2), **extra}
        atomic_json(folder / 'progress.json', value)
        with (folder / 'calibration.log').open('a', encoding='utf-8') as log:
            log.write(json.dumps(value, ensure_ascii=False) + '\n')
        print(json.dumps(value, ensure_ascii=False), flush=True)

    try:
        progress('FREEZING_INPUTS')
        frozen = freeze(folder, config)
        refs = [json.loads(line) for line in (folder / 'inputs/calib.jsonl').read_text(encoding='utf-8').splitlines()]
        require(len(refs) == config['sentences'] and len({r['id'] for r in refs}) == len(refs), 'CALIB_COUNT_OR_IDS')
        rt = Tokenizer('large', [1.] * 5)
        install_a1(rt, read(folder / 'inputs/a1-ranker.json'), config['A1_model_sha256'])
        verify_freeze(folder, frozen)
        rows = []; blocks = 0; candidates = 0
        with gzip.open(folder / 'inputs/calib-raw.jsonl.gz', 'rt', encoding='utf-8') as rawstream, \
             gzip.open(folder / 'outputs.jsonl.gz', 'wt', encoding='utf-8') as outputs:
            for index, ref in enumerate(refs, 1):
                rec = json.loads(next(rawstream))
                require(rec['id'] == ref['id'] and rec['raw_output']['raw'] == ref['text'], 'CALIB_CACHE_ALIGNMENT')
                out = rt.analyze_prepared(rec['raw_output'])
                blocks += check_output(rt, rec['raw_output'], out)
                candidates += sum(len(t['analysis']['analyses']) for t in out['tokens'])
                rows.extend(measure(ref, out))
                outputs.write(json.dumps({'id': ref['id'], 'output': out}, ensure_ascii=False, allow_nan=False) + '\n')
                if index % 25 == 0 or index == len(refs):
                    progress('CALIB_FULL_DECODER', sentences=index, total_sentences=len(refs))
            require(next(rawstream, None) is None, 'EXTRA_CALIB_RAW_RECORDS')
        require(len(rows) == config['all_words'], 'CALIB_DENOMINATOR_CHANGED')
        with gzip.open(folder / 'word-metrics.jsonl.gz', 'wt', encoding='utf-8') as stream:
            for row in rows:
                stream.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + '\n')
        grid, best = choose(rows, config['threshold_grid'], config['target_precision_pct'])
        atomic_json(folder / 'threshold-grid.json', grid)
        zero = a2_summary(rows, {'lemma_threshold': 0, 'feature_threshold': 0})
        chosen = best['thresholds'] if best else None
        checks = [zero['thresholds']]
        if chosen and chosen != checks[0]:
            checks.append(chosen)
        online_counts = [0] * len(checks)
        progress('VERIFYING_ONLINE_A2', threshold_pairs=len(checks))
        with gzip.open(folder / 'outputs.jsonl.gz', 'rt', encoding='utf-8') as outputs:
            for ref in refs:
                rec = json.loads(next(outputs))
                require(ref['id'] == rec['id'], 'OUTPUT_ORDER_CHANGED')
                for i, thresholds in enumerate(checks):
                    _, count = validate_application(ref, rec['output'], thresholds)
                    online_counts[i] += count
            require(next(outputs, None) is None, 'EXTRA_OUTPUT_RECORDS')
        require(online_counts == [a2_summary(rows, c)['accepted'] for c in checks], 'A2_COUNT_MISMATCH')
        verify_freeze(folder, frozen)
        selection = {'status': 'CALIBRATED_EXPERIMENTAL' if best else 'TARGET_INFEASIBLE_ON_PREDECLARED_GRID',
                     'config': chosen, 'A1_model_sha256': config['A1_model_sha256'],
                     'A3_model_sha256': config['A3_model_sha256'], 'freeze_sha256': digest(folder / 'freeze.json'),
                     'TEST_opened': False, 'default_promoted': False, 'ranking_changed': False}
        atomic_json(folder / 'selection.json', selection)
        summary = {'run_id': config['parent_run'], 'stage': 'A2', 'selection': selection,
                   'sentences': len(refs), 'baseline_counts': summarize(rows), 'zero_threshold': zero,
                   'selected': best, 'grid_pairs': len(grid),
                   'feasible_pairs': sum(r['accepted'] > 0 and r['lemma_precision_pct'] >= 92 and r['feature_precision_pct'] >= 92 for r in grid),
                   'checks': {'objective_blocks': blocks, 'candidate_records': candidates,
                              'online_offline_configs': checks, 'online_accepted': online_counts,
                              'all_preferred_candidates_unchanged': True, 'reconstruction_passed': True,
                              'input_source_and_model_hashes_passed': True},
                   'private_outputs_sha256': digest(folder / 'outputs.jsonl.gz'),
                   'private_word_metrics_sha256': digest(folder / 'word-metrics.jsonl.gz'),
                   'limitations': config['limitations'], 'seconds': round(time.monotonic() - started, 2)}
        atomic_json(folder / 'summary.json', summary)
        progress('CALIBRATION_VERIFIED', status_result=selection['status'])
        files = [p for p in folder.rglob('*') if p.is_file()]
        require(shutil.disk_usage(folder).free > config['minimum_free_bytes'] + 2 * sum(p.stat().st_size for p in files),
                'BACKUP_SPACE_LOW')
        hashes = {p.relative_to(folder).as_posix(): digest(p) for p in files}
        for name in ('copy-a', 'copy-b'):
            for file in files:
                dest = folder / name / file.relative_to(folder)
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(file, dest)
            for relative, expected in hashes.items():
                require(digest(folder / name / relative) == expected, 'SNAPSHOT_VERIFICATION_FAILED')
            atomic_json(folder / name / 'snapshot-sha256.json', hashes)
        atomic_json(folder / 'backup-receipt.json', {'status': 'DOUBLE_SNAPSHOT_SHA256_VERIFIED',
                    'files_per_copy': len(hashes), 'copies': ['copy-a', 'copy-b'],
                    'same_physical_drive': True, 'sha256': hashes})
        progress('COMPLETE', status_result=selection['status'], files_per_copy=len(hashes))
    except BaseException as exc:
        atomic_json(folder / 'failure.json', {'type': type(exc).__name__, 'message': str(exc)})
        progress('FAILED', error_type=type(exc).__name__)
        raise


if __name__ == '__main__':
    main()
