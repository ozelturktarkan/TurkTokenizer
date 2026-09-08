"""Small-file Git journal in its own bare repository. Never touches project Git."""
import os
import re
import subprocess
from pathlib import Path, PurePosixPath


JOURNAL_FILES = {'state.json', 'metrics.jsonl', 'training.log', 'checkpoint-sha256.json'}


class GitJournal:
    def __init__(self, git_dir, remote, branch, prefix, allowed_files=None):
        if not branch.startswith('codex/') or not re.fullmatch(r'[A-Za-z0-9_./-]+', branch):
            raise ValueError('DEDICATED_CODEX_BRANCH_REQUIRED')
        self.directory = Path(git_dir).resolve()
        self.remote = remote
        self.branch = branch
        self.ref = 'refs/heads/' + branch
        self.prefix = str(PurePosixPath(prefix))
        if self.prefix.startswith('/') or '..' in PurePosixPath(prefix).parts or '\\' in prefix:
            raise ValueError('INVALID_PUBLISH_PREFIX')
        self.allowed = set(allowed_files) if allowed_files is not None else JOURNAL_FILES
        self.env = dict(os.environ, GIT_TERMINAL_PROMPT='0', GCM_INTERACTIVE='Never',
                        GIT_AUTHOR_NAME='TurkTokenizer training log',
                        GIT_AUTHOR_EMAIL='turktokenizer-log@users.noreply.github.com',
                        GIT_COMMITTER_NAME='TurkTokenizer training log',
                        GIT_COMMITTER_EMAIL='turktokenizer-log@users.noreply.github.com')
        # Do not inherit an index or checkout from a parent shell.
        for key in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE'):
            self.env.pop(key, None)
        self.env['GIT_INDEX_FILE'] = str(self.directory / 'journal.index')

    def _git(self, *args, check=True):
        result = subprocess.run(['git', '--git-dir', str(self.directory), *args],
                                env=self.env, capture_output=True, text=True, encoding='utf-8',
                                errors='replace', timeout=60)
        if check and result.returncode:
            # stderr can contain credential-bearing URLs. Keep it out of published logs.
            raise RuntimeError('GIT_' + args[0].upper().replace('-', '_') + '_FAILED')
        return result

    def _prepare(self):
        self.directory.parent.mkdir(parents=True, exist_ok=True)
        if not (self.directory / 'HEAD').is_file():
            if self.directory.exists() and any(self.directory.iterdir()):
                raise ValueError('GIT_DIRECTORY_NOT_EMPTY')
            self._git('init', '--bare', str(self.directory))
            self._git('remote', 'add', 'origin', self.remote)
        if self._git('remote', 'get-url', 'origin').stdout.strip() != self.remote:
            raise ValueError('GIT_REMOTE_CHANGED')
        self._git('check-ref-format', self.ref)
        local = self._git('rev-parse', '--verify', self.ref, check=False)
        if local.returncode == 0: return local.stdout.strip()
        remote_ref = self._git('ls-remote', '--heads', 'origin', self.ref).stdout.strip()
        target = self.ref if remote_ref else 'HEAD'
        self._git('fetch', '--depth=1', '--filter=blob:none', 'origin', target)
        parent = self._git('rev-parse', 'FETCH_HEAD').stdout.strip()
        self._git('update-ref', self.ref, parent, '0' * 40)
        return parent

    def publish(self, files, message):
        if not files or not set(files) <= self.allowed:
            raise ValueError('PUBLISH_FILE_ALLOWLIST')
        for name, path in files.items():
            if not re.fullmatch(r'[A-Za-z0-9_.-]+', name) or not Path(path).is_file():
                raise ValueError('INVALID_PUBLISH_FILE')
        self.directory.parent.mkdir(parents=True, exist_ok=True)
        lock = self.directory.with_name(self.directory.name + '.publisher.lock')
        descriptor = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
        os.close(descriptor)
        try:
            parent = self._prepare()
            self._git('read-tree', parent)
            for name, path in sorted(files.items()):
                blob = self._git('hash-object', '-w', str(Path(path).resolve())).stdout.strip()
                self._git('update-index', '--add', '--cacheinfo', '100644', blob, self.prefix + '/' + name)
            tree = self._git('write-tree').stdout.strip()
            previous_tree = self._git('rev-parse', parent + '^{tree}').stdout.strip()
            commit = parent
            if tree != previous_tree:
                body = self.directory / 'commit-message.txt'
                body.write_text(message.strip() + '\n', encoding='utf-8')
                commit = self._git('commit-tree', tree, '-p', parent, '-F', str(body)).stdout.strip()
                self._git('update-ref', self.ref, commit, parent)
            # A failed push leaves all local commits intact. No force push or history rewrite.
            self._git('push', 'origin', self.ref + ':' + self.ref)
            published = self._git('ls-remote', '--heads', 'origin', self.ref).stdout.split()
            if not published or published[0] != commit:
                raise RuntimeError('GIT_REMOTE_VERIFICATION_FAILED')
            return commit
        finally:
            lock.unlink()
