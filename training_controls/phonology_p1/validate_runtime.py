"""Public API, codec, objective and cached-output contracts for the P1 delivery."""
import copy
import json
import tempfile
from pathlib import Path

from bootstrap import ROOT
from common import Runtime
from s06e_p1 import Tokenizer, E05_SHA256
from s06e_p1bpe import Tokenizer as Codec
from s06e_r5bpe import Tokenizer as OldCodec
from training_controls.a3_epoch.train import check_output
from training_controls.e70p9.epoch_control import atomic_json, digest


def main():
    rt = Tokenizer()
    codec = Codec(); codec.native = rt
    old = OldCodec()
    assert codec.entries == old.entries and codec.lookup == old.lookup and codec.surfaces == old.surfaces
    # Written x is not the final sound of Fox; -ki introduces a new harmonic
    # vowel that must override Taylor's lexical pronunciation for the next suffix.
    for good, bad in [("Fox'ta", "Fox'da"), ("Taylor'dakinin", "Taylor'dakının")]:
        assert rt.analyzer.analyze(good)['analyses']
        assert not rt.analyzer.analyze(bad)['analyses']
    tests = ["Taylor'ın sözünü İMKB'ye ilettim.", 'Vicahîye çevrildi.', 'Zekâya güveniyorum.',
             "Ben Taylor'ım.", "İMKB'nin değeri arttı.", 'Koşa koşa geldi.',
             '  I\u0307zmir’e\t gittim.\r\n', 'vicahi\u0302ye', '', '😀\x00',
             'Taylor konuştu.\n```python\nx = "İMKB"\n```\nBitti.',
             '`print("î")` https://example.com/İMKB?q=1']
    objectives = 0; roundtrips = 0
    for text in tests:
        raw = rt._raw_schema_sentence(text)
        cached = copy.deepcopy(raw)
        output = rt.analyze_prepared(raw)
        assert raw == cached
        assert Runtime.reconstruct(output) == text
        objectives += check_output(rt, raw, output)
        assert output['analysis_schema']['scoring_model_hashes']['ranker.json'] == E05_SHA256
        assert output['tokens'] == rt.analyze_sentence(text)['tokens']
        snapshot = copy.deepcopy(output)
        for policy in ('selective', 'available'):
            encoded = codec.encode_from_analysis(output, policy)
            assert codec.decode(encoded['input_ids']) == text
            roundtrips += 1
        assert output == snapshot
        assert codec.decode(codec.encode(text)) == text
        roundtrips += 1
    original = copy.deepcopy(rt.analyze_sentence(tests[0]))
    rt.analyze_sentence(tests[1])
    assert rt.analyze_sentence(tests[0]) == original
    # Reordering candidates may not alter the selected reading.
    raw = rt._raw_schema_sentence(tests[0])
    expected = rt.analyze_prepared(raw)
    for token in raw['tokens']:
        token['analysis']['analyses'].reverse()
    reordered = rt.analyze_prepared(raw)
    assert [t['context_decision']['preferred_analysis'] for t in expected['tokens']] == [
        t['context_decision']['preferred_analysis'] for t in reordered['tokens']]
    for invalid in [{}, {'tokenizer_version': 'S06E-A123-v1'},
                    {**rt._raw_schema_sentence('test'), 'manifest': {'phonology_arm': 'baseline'}}]:
        try:
            rt.analyze_prepared(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError('Foreign inventory accepted')
    # Verify hash rejection before any model is installed.
    with tempfile.TemporaryDirectory() as directory:
        p = Path(directory) / 'ranker.json'; p.write_text('{}', encoding='utf-8')
        try:
            Tokenizer(ranker_path=p)
        except ValueError as exc:
            assert str(exc) == 'P1_REQUIRES_FROZEN_A1_E05'
        else:
            raise AssertionError('Wrong E05 file accepted')
    class Forbidden:
        def analyze_sentence(self, text):
            raise AssertionError('Protected code reached native analysis')
    codec.native = Forbidden()
    code = '```python\nx = "Taylor’ın"\n```'
    assert codec.decode(codec.encode(code)) == code
    all_bytes = bytes(range(256))
    assert codec.encode_bytes(all_bytes) == old.encode_bytes(all_bytes)
    assert codec.decode_bytes(codec.encode_bytes(all_bytes)) == all_bytes
    result = {'status': 'PASS', 'native_texts': len(tests), 'roundtrips': roundtrips + 1,
              'independent_objective_blocks': objectives, 'vocabulary_ids_preserved': len(codec.entries),
              'byte_values_roundtrip': 256, 'protected_code_bypasses_morphology': True,
              'pronounced_devoicing_and_post_derivation_harmony_pairs': 2,
              'gold_free_replay_and_cache_checks': True, 'A1_model_sha256': E05_SHA256,
              'implementation_sha256': {n: digest(ROOT / n) for n in
                 ('s06e_p1.py', 's06e_p1bpe.py', 'analyzer_s06e_p1.py',
                  'training_controls/phonology_p1/validate_runtime.py')}}
    atomic_json(ROOT / 'results_phonology_p1/runtime-contracts.json', result)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
