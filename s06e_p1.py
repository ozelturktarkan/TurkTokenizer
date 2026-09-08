"""E05 frozen scorer with opt-in P1 morphology; independent of the old default."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

from analyzer_s06e_p1 import PhonologyAnalyzer, VERSION, ARMS
from s06e_a123 import Tokenizer as A123Tokenizer, WeightedRanker
from s05_ua_features import UARanker
from runtime_s02 import S02Runtime
from r5.engine import fingerprint

DEFAULT_RANKER = Path(r'V:\TurkTokenizer\Yedekler\A123-E70-P9-OF3\runs\a1-large-20260908-v1\A1\selected-ranker.json')
E05_SHA256 = 'eed03755d0026c36b055f68ba18daf7188037cbac85265b24add5c2c7a182ff2'


class Tokenizer(A123Tokenizer):
    def __init__(self, arm='combined', ranker_path=None):
        path = Path(ranker_path) if ranker_path is not None else DEFAULT_RANKER
        contents = path.read_bytes()
        if hashlib.sha256(contents).hexdigest() != E05_SHA256:
            raise ValueError('P1_REQUIRES_FROZEN_A1_E05')
        model = json.loads(contents)
        super().__init__('large', [1.] * 5)
        self.p1_arm = arm
        self.analyzer = PhonologyAnalyzer(arm)
        self._raw_runtime = S02Runtime(analyzer=self.analyzer, context_enabled=False)

        def visit(selector):
            if isinstance(getattr(selector, 'ranker', None), UARanker):
                selector.ranker = WeightedRanker(model, 1.)
                selector.context_fingerprint = fingerprint(model)
            for attr in ('reference_selector', 'reference_ua'):
                child = getattr(selector, attr, None)
                if child is not None:
                    visit(child)
        visit(self.context_selector)
        self.context_selector.a123_models['ranker.json'] = E05_SHA256

    def _raw_schema_sentence(self, text):
        out = super()._raw_schema_sentence(text)
        out['tokenizer_version'] = VERSION
        return out

    def _finish(self, out):
        out = super()._finish(out)
        out['tokenizer_version'] = VERSION
        out['experiment'].update(id=VERSION, phonology_arm=self.p1_arm, same_R5_candidates=self.p1_arm == 'baseline',
                                 new_training=False, scoring_weights_frozen=True, A1_selected_epoch=5,
                                 A3_selected_epoch=0, A2_config=None, default_promoted=False)
        if 'context_selector' in out:
            out['context_selector'].update(candidate_coverage_changed=self.p1_arm != 'baseline',
                                          new_training=False, additional_model_fit=False,
                                          morphology_repair=VERSION)
        return out

    def analyze_word(self, word, n_best=None):
        out = super().analyze_word(word, n_best)
        out['tokenizer_version'] = VERSION
        return out

    def analyze_prepared(self, raw):
        if raw.get('tokenizer_version') != VERSION or raw.get('manifest', {}).get('phonology_arm') != self.p1_arm:
            raise ValueError('P1_REPLAY_REQUIRES_MATCHING_INVENTORY')
        if raw['manifest']['grammar_sha256'] != self.analyzer.manifest()['grammar_sha256']:
            raise ValueError('P1_REPLAY_GRAMMAR_CHANGED')
        return self._finish(self.context_selector.apply(copy.deepcopy(raw)))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description='S06E E05 P1 ses bilgisi onarımı')
    p.add_argument('text'); p.add_argument('--arm', choices=ARMS, default='combined')
    p.add_argument('--ranker', type=Path); p.add_argument('--word', action='store_true')
    args = p.parse_args(); rt = Tokenizer(args.arm, args.ranker)
    out = rt.analyze_word(args.text) if args.word else rt.analyze_sentence(args.text)
    print(json.dumps(out, ensure_ascii=False, indent=2))
