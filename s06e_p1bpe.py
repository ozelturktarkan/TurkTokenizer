"""P1 native analysis with the unchanged R5 byte/BPE/root/suffix ID tables."""
from s06e_a123bpe import Tokenizer as A123Codec
from s06e_a123 import VERSION as A123_VERSION
from s06e_p1 import Tokenizer as Native, VERSION as NATIVE_VERSION, E05_SHA256

VERSION = 'S06E-E05-P1BPE-v0.1.0'


class _LazyNative:
    def __init__(self, arm, ranker_path):
        self.arm = arm; self.ranker_path = ranker_path; self.runtime = None

    def analyze_sentence(self, text):
        if self.runtime is None:
            self.runtime = Native(self.arm, self.ranker_path)
        return self.runtime.analyze_sentence(text)


class Tokenizer(A123Codec):
    def __init__(self, arm='combined', ranker_path=None, policy='selective'):
        super().__init__('large', [1.] * 5, None, policy)
        self.p1_arm = arm
        self.native = _LazyNative(arm, ranker_path)

    def manifest(self):
        return {**super().manifest(), 'id': VERSION, 'morphology_base': NATIVE_VERSION,
                'phonology_arm': self.p1_arm, 'A1_model_sha256': E05_SHA256,
                'historical_R5_ids_unchanged': True, 'A2': None}

    def encode_from_analysis(self, output, policy=None):
        if output.get('tokenizer_version') != NATIVE_VERSION or output.get('experiment', {}).get('phonology_arm') != self.p1_arm:
            raise ValueError('P1_CODEC_REQUIRES_MATCHING_NATIVE_OUTPUT')
        # This adapter changes only the legacy router's envelope discriminator.
        # The original output and candidates are untouched; no grammar is bypassed.
        result = super().encode_from_analysis({**output, 'tokenizer_version': A123_VERSION}, policy)
        result['tokenizer_version'] = VERSION
        return result

    def analyze_sentence(self, text, include_native=False):
        result = super().analyze_sentence(text, include_native)
        result['tokenizer_version'] = VERSION
        return result
