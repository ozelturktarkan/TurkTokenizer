"""Bounded minibatch ranking updates; diagnostic probes never change."""
import numpy as np


def loss(theta, X, b, regularization=0.0):
    if X.shape != (len(b), 5) or len(b) == 0:
        raise ValueError('RANKING_DATA_SHAPE')
    slack = np.maximum(0.0, 1.0 - b - X @ theta)
    value = np.mean(slack ** 2) + regularization * np.sum((theta - 1.0) ** 2)
    grad = -2.0 * (X.T @ slack) / len(b) + 2.0 * regularization * (theta - 1.0)
    if not np.isfinite(value) or not np.isfinite(grad).all():
        raise ValueError('NONFINITE_RANKING_LOSS')
    return float(value), grad


def train_epoch(theta, m, v, step, X, b, rng, config, regularization, bounds):
    order = rng.permutation(len(b))
    seen = 0
    for start in range(0, len(order), config['batch_size']):
        batch = order[start:start + config['batch_size']]
        _, grad = loss(theta, X[batch], b[batch], regularization)
        step += 1
        m *= config['beta1']; m += (1 - config['beta1']) * grad
        v *= config['beta2']; v += (1 - config['beta2']) * grad ** 2
        theta -= config['learning_rate'] * (m / (1 - config['beta1'] ** step)) / (np.sqrt(v / (1 - config['beta2'] ** step)) + config['epsilon'])
        np.clip(theta, *bounds, out=theta)
        seen += len(batch)
    if seen != len(b) or not np.isfinite(theta).all():
        raise ValueError('INCOMPLETE_RANKING_EPOCH')
    return step, seen
