"""Add the licensed adjectival branch of possessive participles.

The nominal branch and all S01 registry paths remain available. Ordinary
possessive adjectives are not reclassified. CASE still nominalizes the branch.
The bundled TurkishMorphotactics.java documents 'okuduğum kitap' (Adj, Noun).
"""
import hashlib
from pathlib import Path
import bootstrap
from r2_analyzer import CoverageAnalyzer
from r5.engine import fingerprint

class S02Analyzer(CoverageAnalyzer):
    def _transition(self, node, lexeme, record, mid):
        outputs = super()._transition(node, lexeme, record, mid)
        if (outputs and node.pos == "ADJ" and node.phase == "N"
                and dict(node.feats).get("VerbForm") == "Part"
                and mid.startswith("POSS_")
                and node.mids and node.mids[-1] in {"PART_DIK", "PART_FUT"}):
            outputs = list(outputs) + [
                ("ADJ", phase, dict(feats), par, num, poss, cop, deriv)
                for _, phase, feats, par, num, poss, cop, deriv in outputs
            ]
        return outputs

    def manifest(self):
        base = super().manifest()
        source = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        return {**base, "engine_version": "AB00-R1-S02-v0.1.0",
                "possessive_participle_adjective_branch": True,
                "grammar_sha256": fingerprint([base["grammar_sha256"], source])}
