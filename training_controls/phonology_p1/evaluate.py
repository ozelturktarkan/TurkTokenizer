"""Fresh-candidate, frozen-scorer DEV/CALIB ablations; never opens TEST."""
import os
for variable in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[variable] = '1'
import collections
import copy
import gzip
import json
import shutil
import time
from pathlib import Path

from bootstrap import ROOT
from common import Runtime, compatible
from a123_measurement import measure, summarize, a2_summary
from s06e_p1 import Tokenizer, E05_SHA256
from s06e_p1bpe import Tokenizer as Codec
from s06e_r5bpe import Tokenizer as OldCodec
from training_controls.a2_calibration.calibrate import verify_freeze, require
from training_controls.a3_epoch.train import check_output
from training_controls.e70p9.epoch_control import read, digest, atomic_json
from .test_phonology import PAIRS, matches

HERE = Path(__file__).resolve().parent
PARENT = Path(r'V:\TurkTokenizer\Yedekler\A123-E70-P9-OF3\runs\a1-large-20260908-v1')
DEST = PARENT / 'P1-phonology-v1'
LOCAL = ROOT / 'results_phonology_p1'
SOURCES = ['analyzer_s06e_p1.py', 's06e_p1.py', 's06e_p1bpe.py', 'data/s06e-p1/pronunciations.json']
SOURCES += [p.relative_to(ROOT).as_posix() for p in sorted(HERE.glob('*')) if p.suffix in ('.py', '.json', '.md')]


def records(path):
    opener = gzip.open if str(path).endswith('.gz') else open
    with opener(path, 'rt', encoding='utf-8') as stream:
        for line in stream:
            yield json.loads(line)


def emit(stream, value):
    stream.write(json.dumps(value, ensure_ascii=False, allow_nan=False) + '\n')


def inventory(out):
    return [(t['raw'], t['start'], t['end'], t['analysis']['analyses']) for t in out['tokens']]


def candidate_delta(ref, old, new):
    require([(t['raw'], t['start'], t['end']) for t in old['tokens']] ==
            [(t['raw'], t['start'], t['end']) for t in new['tokens']], 'TOKEN_SPANS_CHANGED')
    units = {(u['start'], u['end']): u for u in ref['units']}
    counts = collections.Counter(); changes = []
    for a, b in zip(old['tokens'], new['tokens'], strict=True):
        aa = {v['analysis_id']: v for v in a['analysis']['analyses']}
        bb = {v['analysis_id']: v for v in b['analysis']['analyses']}
        require(len(bb) == len(b['analysis']['analyses']), 'DUPLICATE_CANDIDATE_ID')
        common = aa.keys() & bb.keys()
        require(all(aa[k] == bb[k] for k in common), 'RETAINED_CANDIDATE_CONTENT_CHANGED')
        counts['retained_candidate_ids'] += len(common)
        added = [bb[k] for k in sorted(bb.keys() - aa.keys())]
        removed = [aa[k] for k in sorted(aa.keys() - bb.keys())]
        counts['added_candidates'] += len(added); counts['removed_candidates'] += len(removed)
        if not (added or removed):
            continue
        counts['changed_tokens'] += 1
        unit = units.get((a['start'], a['end']), {})
        gold = unit.get('gold')
        if gold:
            counts['added_reference_matching_candidates'] += sum(compatible(v, gold, False) for v in added)
            counts['added_reference_mismatching_candidates'] += sum(not compatible(v, gold, False) for v in added)
            counts['removed_reference_matching_candidates'] += sum(compatible(v, gold, False) for v in removed)
        else:
            counts['added_candidates_without_projectable_reference'] += len(added)
        changes.append({'id': ref['id'], 'surface': a['raw'], 'start': a['start'], 'end': a['end'],
                        'gold': gold, 'added': added, 'removed': removed})
    return counts, changes


def paired(before, after):
    keys = ('candidate_lemma_pos', 'candidate_declared_features', 'preferred_lemma_pos',
            'preferred_declared_features', 'legacy_selected_lemma_correct')
    result = {}; changed = []
    for a, b in zip(before, after, strict=True):
        require((a['id'], a['start'], a['end']) == (b['id'], b['start'], b['end']), 'PAIRED_UNIT_MISMATCH')
        if any(a[k] != b[k] for k in keys):
            changed.append({'id': b['id'], 'surface': b['surface'], 'start': b['start'], 'end': b['end'],
                            'gold': b['gold'], 'before': a, 'after': b})
    for k in keys:
        fixed = sum(not a[k] and b[k] for a, b in zip(before, after))
        regressed = sum(a[k] and not b[k] for a, b in zip(before, after))
        result[k] = {'fixed': fixed, 'regressed': regressed, 'net': fixed - regressed}
    return result, changed


def main():
    config = read(HERE / 'protocol.json')
    require(not DEST.exists() and not LOCAL.exists(), 'REFUSING_TO_OVERWRITE_P1_EXPERIMENT')
    require(DEST.resolve().is_relative_to(PARENT.resolve()), 'P1_UNSAFE_OUTPUT_DIRECTORY')
    old_freeze = read(PARENT / 'A2/freeze.json')
    verify_freeze(PARENT / 'A2', old_freeze)
    require(digest(PARENT / 'A1/selected-ranker.json') == E05_SHA256, 'P1_A1_CHANGED')
    require(digest(PARENT / 'A3/selected-ranking.json') == config['A3_model_sha256'], 'P1_A3_CHANGED')
    require(shutil.disk_usage(PARENT).free > 5 * 1024 ** 3, 'P1_OUTPUT_SPACE_LOW')
    DEST.mkdir(); LOCAL.mkdir()
    frozen = {'new_sources': {n: digest(ROOT / n) for n in SOURCES},
              'historical_source_count': len(old_freeze['source_sha256']),
              'parent_freeze_sha256': digest(PARENT / 'A2/freeze.json'),
              'A1_model_sha256': E05_SHA256, 'A3_model_sha256': config['A3_model_sha256'],
              'references': {s: digest(ROOT / f'training/a1-large-v1/{s}.jsonl') for s in config['splits']},
              'TEST_opened': False}
    atomic_json(DEST / 'freeze.json', frozen); atomic_json(LOCAL / 'freeze.json', frozen)
    started = time.monotonic(); results = {}; baselines = {}; contract_rows = []
    old_codec = OldCodec()
    id_fingerprint = digest(ROOT / 'models/s06e-r5/roots.json')

    def progress(**row):
        row.update(seconds=round(time.monotonic() - started, 2))
        atomic_json(DEST / 'progress.json', row)
        print(json.dumps(row, ensure_ascii=False), flush=True)

    for arm in config['arms']:
        progress(arm=arm, stage='LOAD_FROZEN_SCORER')
        rt = Tokenizer(arm)
        codec = Codec(arm); codec.native = rt
        require(codec.entries == old_codec.entries and codec.surfaces == old_codec.surfaces and
                codec.lookup == old_codec.lookup, 'P1_BPE_ID_DRIFT')
        require(codec.decode_bytes(codec.encode_bytes(bytes(range(256)))) == bytes(range(256)), 'P1_BYTE_ROUNDTRIP')
        arm_results = {}
        for good, bad, lemma, mid in PAIRS:
            yes, no = rt.analyzer.analyze(good), rt.analyzer.analyze(bad)
            contract_rows.append({'arm': arm, 'good': good, 'bad': bad, 'lemma': lemma, 'mid': mid,
                'good_path_present': bool(matches(yes, lemma, mid)), 'bad_path_absent': not matches(no, lemma, mid)})
        for split, expected in config['splits'].items():
            folder = DEST / arm / split; folder.mkdir(parents=True)
            refs = list(records(ROOT / f'training/a1-large-v1/{split}.jsonl'))
            require(len(refs) == expected['sentences'], 'P1_SENTENCE_COUNT')
            reference_cache = (PARENT / 'A1/inputs/dev-raw.jsonl.gz' if split == 'dev' else PARENT / 'A2/inputs/calib-raw.jsonl.gz')
            historical = records(reference_cache)
            baseline_outputs = records(DEST / 'baseline' / split / 'outputs.jsonl.gz') if arm != 'baseline' else None
            rows = []; counts = collections.Counter(); blocks = 0; roundtrips = 0; bpe_routes = collections.Counter()
            with gzip.open(folder / 'outputs.jsonl.gz', 'wt', encoding='utf-8') as outputs, \
                 gzip.open(folder / 'candidate-changes.jsonl.gz', 'wt', encoding='utf-8') as deltafile:
                for index, ref in enumerate(refs, 1):
                    raw = rt._raw_schema_sentence(ref['text'])
                    previous = next(historical)
                    require(previous['id'] == ref['id'] and previous['raw_output']['raw'] == ref['text'], 'P1_REFERENCE_CACHE_MISMATCH')
                    if arm == 'baseline':
                        require(inventory(raw) == inventory(previous['raw_output']), 'P1_BASELINE_INVENTORY_MISMATCH')
                    else:
                        prev = next(baseline_outputs)
                        require(prev['id'] == ref['id'], 'P1_BASELINE_ORDER_CHANGED')
                        c, changes = candidate_delta(ref, prev['output'], raw)
                        counts.update(c)
                        for change in changes:
                            emit(deltafile, change)
                    out = rt.analyze_prepared(raw)
                    blocks += check_output(rt, raw, out)
                    measured = measure(ref, out); rows.extend(measured)
                    # Losslessness and immutable vocabulary checked on every sentence.
                    encoded = codec.encode_from_analysis(out)
                    require(codec.decode(encoded['input_ids']) == ref['text'], 'P1_SENTENCE_ROUNDTRIP')
                    roundtrips += 1
                    for item in encoded['spans']:
                        if item.get('token_index') is not None:
                            bpe_routes[item['route']] += 1
                    emit(outputs, {'id': ref['id'], 'output': out})
                    if index % 50 == 0 or index == len(refs):
                        progress(arm=arm, split=split, stage='FULL_DECODER', sentences=index, total=len(refs))
                require(next(historical, None) is None, 'P1_EXTRA_REFERENCE_CACHE')
                if baseline_outputs is not None:
                    require(next(baseline_outputs, None) is None, 'P1_EXTRA_BASELINE_OUTPUT')
            require(len(rows) == expected['words'], 'P1_WORD_DENOMINATOR')
            summary = summarize(rows)
            if arm == 'baseline':
                require(all(summary[k] == v for k, v in config['baseline_counts'][split].items()), 'P1_BASELINE_SCORE_MISMATCH')
                baselines[split] = rows
            changes, changed_rows = paired(baselines[split], rows)
            with gzip.open(folder / 'word-metrics.jsonl.gz', 'wt', encoding='utf-8') as f:
                for row in rows: emit(f, row)
            with gzip.open(folder / 'selection-changes.jsonl.gz', 'wt', encoding='utf-8') as f:
                for row in changed_rows: emit(f, row)
            grid = [a2_summary(rows, {'lemma_threshold': lm, 'feature_threshold': fm})
                    for lm in [0, .25, .5, 1, 2, 3, 4, 6, 8, 12, 20]
                    for fm in [0, .25, .5, 1, 2, 3, 4, 6, 8, 12, 20]] if split == 'calib' else []
            arm_results[split] = {'counts': summary, 'paired': changes, 'candidate_delta': dict(counts),
                'objective_blocks_verified': blocks, 'BPE_roundtrips': roundtrips,
                'BPE_token_routes_including_punctuation': dict(bpe_routes),
                'A2_feasible_grid_pairs_diagnostic_only': sum(r['accepted'] > 0 and r['lemma_precision_pct'] >= 92 and r['feature_precision_pct'] >= 92 for r in grid) if grid else None,
                'artifact_sha256': {p.name: digest(p) for p in folder.iterdir() if p.is_file()}}
            atomic_json(folder / 'summary.json', arm_results[split])
            progress(arm=arm, split=split, stage='SPLIT_COMPLETE', counts=summary)
        results[arm] = arm_results
        # Release all per-sentence caches before loading the next arm.
        del codec, rt
    verify_freeze(PARENT / 'A2', old_freeze)
    require(all(digest(ROOT / n) == h for n, h in frozen['new_sources'].items()), 'P1_SOURCE_CHANGED_DURING_RUN')
    require(digest(ROOT / 'models/s06e-r5/roots.json') == id_fingerprint, 'P1_ROOT_IDS_CHANGED')
    require(digest(PARENT / 'A1/selected-ranker.json') == E05_SHA256, 'P1_MODEL_CHANGED_DURING_RUN')
    final_contracts = [r for r in contract_rows if r['arm'] == 'combined']
    passed = all(r['good_path_present'] and r['bad_path_absent'] for r in final_contracts)
    safe = all(results['combined'][s]['counts']['preferred_lemma_pos'] >= results['baseline'][s]['counts']['preferred_lemma_pos'] and
               results['combined'][s]['counts']['preferred_declared_features'] >= results['baseline'][s]['counts']['preferred_declared_features'] and
               results['combined'][s]['counts']['legacy_selected_lemma_wrong'] <= results['baseline'][s]['counts']['legacy_selected_lemma_wrong']
               for s in config['splits'])
    final = {'id': config['id'], 'status': 'EXPERIMENT_COMPLETE', 'arms': results,
             'selection': 'COMBINED_OPT_IN_EXPERIMENTAL' if safe and passed else 'REVIEW_REQUIRED_KEEP_E05',
             'default_promoted': False, 'TEST_opened': False, 'new_training': False,
             'historical_freeze_verified': True, 'focused_contrasts': contract_rows,
             'combined_contrasts_passed': sum(r['good_path_present'] and r['bad_path_absent'] for r in final_contracts),
             'combined_contrasts_total': len(final_contracts), 'seconds': round(time.monotonic() - started, 2)}
    atomic_json(DEST / 'comparison.json', final); atomic_json(LOCAL / 'comparison.json', final)
    progress(stage='COMPLETE', selection=final['selection'])


if __name__ == '__main__':
    main()
