"""Partial-label minibatch optimizer, with explicit complete-pass accounting."""
import array
import collections
import gzip
import json

import numpy as np
from scipy.sparse import csr_matrix


def records(path):
    with gzip.open(path, 'rt', encoding='utf-8') as src:
        for line in src: yield json.loads(line)


def vocabulary(path):
    frequencies = collections.Counter()
    for row in records(path):
        frequencies.update(set().union(*(set(f) for f in row['features'])))
    return {k: i for i, k in enumerate(sorted(k for k, n in frequencies.items() if n >= 2))}


def matrix(rows, vocab):
    data = array.array('d'); indices = array.array('i'); indptr = array.array('q', [0])
    starts = []; ends = []; labels = []; offsets = []
    for row in rows:
        if not any(row['good']) or all(row['good']): raise ValueError('NONCOMPETITIVE_EXAMPLE')
        starts.append(len(labels))
        for f, y, off in zip(row['features'], row['good'], row['offsets'], strict=True):
            for key, value in f.items():
                if key in vocab and value: indices.append(vocab[key]); data.append(value)
            indptr.append(len(data)); labels.append(y); offsets.append(off)
        ends.append(len(labels))
    X = csr_matrix((np.asarray(data), np.asarray(indices), np.asarray(indptr)), shape=(len(labels), len(vocab)))
    X.sort_indices()
    return X, np.asarray(starts), np.asarray(ends), np.asarray(labels, dtype=bool), np.asarray(offsets)


def objective(w, data, regularization=0., gradient=True):
    X, starts, ends, good, offsets = data
    scores = offsets + X @ w
    lengths = ends - starts
    maxima = np.maximum.reduceat(scores, starts)
    ex = np.exp(scores - np.repeat(maxima, lengths))
    sums = np.add.reduceat(ex, starts)
    masked = np.where(good, scores, -np.inf)
    gm = np.maximum.reduceat(masked, starts)
    ge = np.where(good, np.exp(masked - np.repeat(gm, lengths)), 0.)
    gs = np.add.reduceat(ge, starts)
    loss = float(np.mean(maxima + np.log(sums) - gm - np.log(gs)) + regularization * np.dot(w, w))
    if not gradient: return loss
    p = ex / np.repeat(sums, lengths); q = ge / np.repeat(gs, lengths)
    grad = np.asarray(X.T @ (p - q)).ravel() / len(starts) + 2 * regularization * w
    return loss, grad


def subset(data, examples):
    X, starts, ends, good, offsets = data
    lengths = ends[examples] - starts[examples]
    rows = np.concatenate([np.arange(starts[i], ends[i]) for i in examples])
    stops = np.cumsum(lengths)
    return X[rows], np.r_[0, stops[:-1]], stops, good[rows], offsets[rows]


def train_epoch(w, m, v, step, data, rng, config, progress=None):
    order = rng.permutation(len(data[1])); seen = 0
    for start in range(0, len(order), config['batch_size']):
        batch = order[start:start + config['batch_size']]
        loss, grad = objective(w, subset(data, batch), 1. / len(order))
        if not np.isfinite(loss) or not np.isfinite(grad).all(): raise ValueError('NONFINITE_TRAINING')
        step += 1
        m *= config['beta1']; m += (1 - config['beta1']) * grad
        v *= config['beta2']; v += (1 - config['beta2']) * grad * grad
        w -= config['learning_rate'] * (m / (1 - config['beta1'] ** step)) / (np.sqrt(v / (1 - config['beta2'] ** step)) + config['epsilon'])
        seen += len(batch)
        if progress and (start // config['batch_size']) % 50 == 0: progress(seen, len(order))
    if seen != len(order) or not np.isfinite(w).all(): raise ValueError('INCOMPLETE_EPOCH')
    return step, seen
