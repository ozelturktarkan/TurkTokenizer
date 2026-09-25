"""Experimental P7 scoped residual; P6.1 selected codec remains separate."""
import json
import bootstrap
from bootstrap import ROOT
from s06e_p5 import Tokenizer as P5
from r5.engine import fingerprint
from formulas_p7 import Formulas, VERSION as FEATURE_VERSION, FAMILIES

VERSION = 'S06E-P7-ScopedFormulas-v0.1.0'


class FormulaRanker:
    def __init__(self, base, formulas, weights, family, strength):
        self.base, self.formulas, self.residual_weights = base, formulas, weights
        self.family, self.strength = family, strength
        self.model, self.weights, self.segmenter = base.model, base.weights, base.segmenter

    def residual(self, tokens, i, a):
        fs = self.formulas.features(tokens, i, a, self.family)
        return sum(self.residual_weights.get(k, 0.) * x for k, x in fs.items())

    def token(self, tokens, i):
        scores = self.base.token(tokens, i)
        if not self.strength:
            return scores
        scores = {a['analysis_id']: scores[a['analysis_id']] + self.strength * self.residual(tokens, i, a)
                  for a in tokens[i]['analysis']['analyses']}
        peak = max(scores.values(), default=0.)
        return {k: v - peak for k, v in scores.items()}


class Tokenizer(P5):
    def __init__(self, model=None, family='combined', strength=1.):
        super().__init__()
        if model is None:
            model = json.loads((ROOT / 'results_formulas_p7/model.json').read_text(encoding='utf-8'))
        if model['feature_version'] != FEATURE_VERSION or family not in (*FAMILIES, 'combined'):
            raise ValueError('P7_MODEL_SCHEMA')
        self.p7_model, self.family, self.strength = model, family, strength
        self.formulas = Formulas(model['frames'])
        s = self.context_selector
        s.ranker = FormulaRanker(s.ranker, self.formulas, model['weights'][family], family, strength)
        self.p7_hash = fingerprint(model)
        s.context_fingerprint = fingerprint([s.context_fingerprint, self.p7_hash, family, strength])
        s.a123_models['p7_formulas'] = self.p7_hash

    def _finish(self, out):
        result = super()._finish(out)
        result['tokenizer_version'] = VERSION
        result['experiment'].update(P7_family=self.family, P7_strength=self.strength, P7_model=self.p7_hash,
                                    P7_feature_version=FEATURE_VERSION, P7_confidence_calibrated=False)
        return result
