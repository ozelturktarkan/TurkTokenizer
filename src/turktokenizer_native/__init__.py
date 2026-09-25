"""Small standard-library client for the separate frozen Rust runtime."""
from pathlib import Path
import json, os, queue, subprocess, tempfile, threading

__version__ = '0.1.0rc1'

class NativeError(RuntimeError):
    pass

class NativeTokenizer:
    """Persistent JSONL process. Calls are serialized; Rust owns model memory.

    runtime_dir is the extracted research release root. The optional Python
    wrapper has its own process overhead; the standalone Rust CLI needs no Python.
    """
    def __init__(self, runtime_dir=None, timeout=120):
        if timeout <= 0: raise ValueError('timeout must be positive')
        candidate = runtime_dir or os.environ.get('TURKTOKENIZER_RUNTIME')
        if candidate is None:
            roots = [Path.cwd(), Path(__file__).resolve().parents[2]]
            candidate = next((p for p in roots if (p/'bin/turktokenizer.exe').is_file()), roots[0])
        self.root = Path(candidate).resolve()
        self.timeout = timeout
        self._lock = threading.RLock()
        self._closed = False
        exp = self.root/'experiments'
        files = [self.root/'bin/turktokenizer.exe', exp/'P81-20260916/data',
                 exp/'P128-20260924/data/frames.json', exp/'P84-20260916/data/bpe.bin',
                 exp/'P111-20260923/data/lookup-index.bin']
        for f in files:
            if not f.exists():
                raise FileNotFoundError(f'Missing runtime file: {f}. Extract the Windows research release and set TURKTOKENIZER_RUNTIME to its root.')
        env = dict(os.environ, TURKTOKENIZER_LOOKUP_INDEX=str(files[-1]))
        self._stderr = tempfile.TemporaryFile()
        try:
            self._process = subprocess.Popen([str(p) for p in files[:4]], stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=self._stderr, env=env,
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        except BaseException:
            self._stderr.close(); raise
        self._responses = queue.Queue()
        def reader():
            try:
                for line in self._process.stdout:
                    self._responses.put(line)
            finally:
                self._responses.put(None)
        self._reader = threading.Thread(target=reader, daemon=True)
        self._reader.start()

    def _request(self, value):
        with self._lock:
            if self._closed: raise NativeError('Tokenizer is closed')
            try:
                self._process.stdin.write((json.dumps(value, ensure_ascii=False)+'\n').encode('utf-8'))
                self._process.stdin.flush()
                line = self._responses.get(timeout=self.timeout)
            except queue.Empty:
                self.close()
                raise TimeoutError('Native request timed out; process closed to prevent response misalignment') from None
            except (OSError, ValueError) as e:
                self.close(); raise NativeError('Native input failed') from e
            if line is None:
                self._stderr.seek(0)
                detail = self._stderr.read(4096).decode('utf-8', 'replace')
                self.close(); raise NativeError('Native process ended: '+detail)
            try: result = json.loads(line)
            except (ValueError, UnicodeError) as e:
                self.close(); raise NativeError('Invalid native JSON response') from e
            if not result.get('ok'): raise NativeError(result.get('error', 'Native request failed'))
            return result['result']

    @staticmethod
    def _text(text):
        if not isinstance(text, str): raise TypeError('text must be str')
        return text

    def analyze(self, text, *, node_budget=200000):
        if type(node_budget) is not int or not 0 <= node_budget <= 2000000:
            raise ValueError('node_budget must be an integer between 0 and 2000000')
        return self._request(dict(op='analyze',text=self._text(text),node_budget=node_budget))

    def analyze_sentence(self, text):
        """P21-compatible baseline result; use analyze() for the YONT sidecar."""
        return self._request(dict(op='baseline',text=self._text(text)))

    def encode(self, text):
        return self.analyze_sentence(text)['input_ids']

    def decode(self, ids):
        ids = list(ids)
        if any(type(i) is not int or not 0 <= i <= 0xffffffff for i in ids):
            raise ValueError('Token IDs must be unsigned 32-bit integers')
        return self._request(dict(op='decode',ids=ids))['text']

    def bpe(self, text):
        """Historical standalone BPE comparison, not Qwen BPE."""
        return self._request(dict(op='bpe',text=self._text(text)))

    def close(self):
        with self._lock:
            if self._closed: return
            self._closed = True
            try:
                self._process.stdin.close()
                self._process.wait(timeout=2)
            except (OSError, subprocess.TimeoutExpired):
                self._process.kill(); self._process.wait(timeout=5)
            finally:
                self._reader.join(timeout=1)
                self._process.stdout.close()
                self._stderr.close()

    def __enter__(self): return self
    def __exit__(self, *args): self.close()

def load_selected(runtime_dir=None, **kwargs):
    return NativeTokenizer(runtime_dir, **kwargs)
