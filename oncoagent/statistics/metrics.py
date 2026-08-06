from __future__ import annotations

import math
from collections import Counter
from collections.abc import Sequence

import numpy as np

from oncoagent.models.types import ConfidenceInterval, MetricResult


def accuracy(y_true: Sequence[int], y_pred: Sequence[int]) -> float:
    _equal_lengths(y_true, y_pred)
    if not y_true:
        raise ValueError("empty input")
    return sum(int(left == right) for left, right in zip(y_true, y_pred, strict=True)) / len(y_true)


def sensitivity(y_true: Sequence[int], y_pred: Sequence[int]) -> float:
    tp, _, _, fn = confusion_counts(y_true, y_pred)
    return _safe_divide(tp, tp + fn)


def specificity(y_true: Sequence[int], y_pred: Sequence[int]) -> float:
    _, fp, tn, _ = confusion_counts(y_true, y_pred)
    return _safe_divide(tn, tn + fp)


def precision(y_true: Sequence[int], y_pred: Sequence[int]) -> float:
    tp, fp, _, _ = confusion_counts(y_true, y_pred)
    return _safe_divide(tp, tp + fp)


def negative_predictive_value(y_true: Sequence[int], y_pred: Sequence[int]) -> float:
    _, _, tn, fn = confusion_counts(y_true, y_pred)
    return _safe_divide(tn, tn + fn)


def f1_score(y_true: Sequence[int], y_pred: Sequence[int]) -> float:
    p = precision(y_true, y_pred)
    r = sensitivity(y_true, y_pred)
    return _safe_divide(2.0 * p * r, p + r)


def balanced_accuracy(y_true: Sequence[int], y_pred: Sequence[int]) -> float:
    return (sensitivity(y_true, y_pred) + specificity(y_true, y_pred)) / 2.0


def confusion_counts(y_true: Sequence[int], y_pred: Sequence[int]) -> tuple[int, int, int, int]:
    _equal_lengths(y_true, y_pred)
    tp = sum(int(left == 1 and right == 1) for left, right in zip(y_true, y_pred, strict=True))
    fp = sum(int(left == 0 and right == 1) for left, right in zip(y_true, y_pred, strict=True))
    tn = sum(int(left == 0 and right == 0) for left, right in zip(y_true, y_pred, strict=True))
    fn = sum(int(left == 1 and right == 0) for left, right in zip(y_true, y_pred, strict=True))
    return tp, fp, tn, fn


def roc_auc(y_true: Sequence[int], y_score: Sequence[float]) -> float:
    _equal_lengths(y_true, y_score)
    positives = [score for label, score in zip(y_true, y_score, strict=True) if label == 1]
    negatives = [score for label, score in zip(y_true, y_score, strict=True) if label == 0]
    if not positives or not negatives:
        raise ValueError("both classes are required")
    wins = 0.0
    for positive in positives:
        for negative in negatives:
            if positive > negative:
                wins += 1.0
            elif positive == negative:
                wins += 0.5
    return wins / (len(positives) * len(negatives))


def brier_score(y_true: Sequence[int], y_score: Sequence[float]) -> float:
    _equal_lengths(y_true, y_score)
    if not y_true:
        raise ValueError("empty input")
    return sum(
        (float(label) - score) ** 2 for label, score in zip(y_true, y_score, strict=True)
    ) / len(y_true)


def log_loss(y_true: Sequence[int], y_score: Sequence[float], epsilon: float = 1e-12) -> float:
    _equal_lengths(y_true, y_score)
    if not y_true:
        raise ValueError("empty input")
    total = 0.0
    for label, score in zip(y_true, y_score, strict=True):
        clipped = min(1.0 - epsilon, max(epsilon, score))
        total -= label * math.log(clipped) + (1 - label) * math.log(1.0 - clipped)
    return total / len(y_true)


def dice_score(y_true: np.ndarray, y_pred: np.ndarray, epsilon: float = 1e-8) -> float:
    if y_true.shape != y_pred.shape:
        raise ValueError("shapes differ")
    left = np.asarray(y_true, dtype=bool)
    right = np.asarray(y_pred, dtype=bool)
    intersection = np.logical_and(left, right).sum()
    return float((2.0 * intersection + epsilon) / (left.sum() + right.sum() + epsilon))


def jaccard_score(y_true: np.ndarray, y_pred: np.ndarray, epsilon: float = 1e-8) -> float:
    if y_true.shape != y_pred.shape:
        raise ValueError("shapes differ")
    left = np.asarray(y_true, dtype=bool)
    right = np.asarray(y_pred, dtype=bool)
    intersection = np.logical_and(left, right).sum()
    union = np.logical_or(left, right).sum()
    return float((intersection + epsilon) / (union + epsilon))


def concordance_index(
    times: Sequence[float], events: Sequence[int], risks: Sequence[float]
) -> float:
    if not (len(times) == len(events) == len(risks)):
        raise ValueError("lengths differ")
    concordant = 0.0
    comparable = 0
    for first in range(len(times)):
        for second in range(first + 1, len(times)):
            if times[first] == times[second]:
                continue
            if times[first] < times[second] and events[first] == 1:
                comparable += 1
                concordant += _risk_order(risks[first], risks[second])
            elif times[second] < times[first] and events[second] == 1:
                comparable += 1
                concordant += _risk_order(risks[second], risks[first])
    if comparable == 0:
        raise ValueError("no comparable pairs")
    return concordant / comparable


def expected_calibration_error(
    y_true: Sequence[int],
    y_score: Sequence[float],
    bins: int = 10,
) -> float:
    _equal_lengths(y_true, y_score)
    if bins < 1:
        raise ValueError("bins must be positive")
    total = len(y_true)
    if total == 0:
        raise ValueError("empty input")
    error = 0.0
    for index in range(bins):
        lower = index / bins
        upper = (index + 1) / bins
        members = [
            position
            for position, score in enumerate(y_score)
            if lower <= score < upper or index == bins - 1 and score == upper
        ]
        if not members:
            continue
        observed = sum(y_true[position] for position in members) / len(members)
        confidence = sum(y_score[position] for position in members) / len(members)
        error += len(members) / total * abs(observed - confidence)
    return error


def multiclass_accuracy(y_true: Sequence[str], y_pred: Sequence[str]) -> float:
    _equal_lengths(y_true, y_pred)
    if not y_true:
        raise ValueError("empty input")
    return sum(int(left == right) for left, right in zip(y_true, y_pred, strict=True)) / len(y_true)


def macro_f1(y_true: Sequence[str], y_pred: Sequence[str]) -> float:
    labels = sorted(set(y_true) | set(y_pred))
    if not labels:
        raise ValueError("empty input")
    values = []
    for label in labels:
        binary_true = [int(item == label) for item in y_true]
        binary_pred = [int(item == label) for item in y_pred]
        values.append(f1_score(binary_true, binary_pred))
    return sum(values) / len(values)


def cohen_kappa(y_true: Sequence[str], y_pred: Sequence[str]) -> float:
    _equal_lengths(y_true, y_pred)
    if not y_true:
        raise ValueError("empty input")
    observed = multiclass_accuracy(y_true, y_pred)
    true_counts = Counter(y_true)
    pred_counts = Counter(y_pred)
    expected = float(
        sum(
            true_counts[label] * pred_counts[label]
            for label in set(true_counts) | set(pred_counts)
        )
    )
    expected /= len(y_true) ** 2
    return _safe_divide(observed - expected, 1.0 - expected)


def wilson_interval(successes: int, total: int, level: float = 0.95) -> ConfidenceInterval:
    if total <= 0 or successes < 0 or successes > total:
        raise ValueError("invalid counts")
    z = 1.959963984540054 if level == 0.95 else 1.6448536269514722
    proportion = successes / total
    denominator = 1.0 + z * z / total
    center = (proportion + z * z / (2.0 * total)) / denominator
    margin = (
        z
        * math.sqrt(proportion * (1.0 - proportion) / total + z * z / (4.0 * total * total))
        / denominator
    )
    return ConfidenceInterval(
        proportion, max(0.0, center - margin), min(1.0, center + margin), level
    )


def metric_result(
    name: str, value: float, sample_size: int, interval: ConfidenceInterval | None = None
) -> MetricResult:
    return MetricResult(name, value, interval, sample_size)


def _equal_lengths(left: Sequence[object], right: Sequence[object]) -> None:
    if len(left) != len(right):
        raise ValueError("lengths differ")


def _safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0.0:
        return 0.0
    return numerator / denominator


def _risk_order(earlier: float, later: float) -> float:
    if earlier > later:
        return 1.0
    if earlier == later:
        return 0.5
    return 0.0
