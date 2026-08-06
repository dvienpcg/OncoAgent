from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass

import numpy as np

from oncoagent.models.types import ConfidenceInterval, EvaluationRow


@dataclass(frozen=True)
class BootstrapConfig:
    resamples: int = 10000
    confidence: float = 0.95
    seed: int = 1


@dataclass(frozen=True)
class PairedBootstrapResult:
    observed_difference: float
    interval: ConfidenceInterval
    p_value: float
    samples: tuple[float, ...]


def stratified_indices(
    strata: Sequence[tuple[str, ...]],
    rng: np.random.Generator,
) -> np.ndarray:
    groups: dict[tuple[str, ...], list[int]] = {}
    for index, key in enumerate(strata):
        groups.setdefault(key, []).append(index)
    sampled: list[int] = []
    for indices in groups.values():
        draw = rng.choice(indices, size=len(indices), replace=True)
        sampled.extend(int(value) for value in draw)
    return np.asarray(sampled, dtype=np.int64)


def percentile_interval(
    values: Sequence[float],
    confidence: float = 0.95,
) -> ConfidenceInterval:
    if not values:
        raise ValueError("empty bootstrap distribution")
    alpha = (1.0 - confidence) / 2.0
    array = np.asarray(values, dtype=np.float64)
    estimate = float(np.mean(array))
    lower = float(np.quantile(array, alpha))
    upper = float(np.quantile(array, 1.0 - alpha))
    return ConfidenceInterval(estimate, lower, upper, confidence)


def bootstrap_metric(
    rows: Sequence[EvaluationRow],
    metric: Callable[[Sequence[int], Sequence[float]], float],
    config: BootstrapConfig | None = None,
) -> ConfidenceInterval:
    settings = config or BootstrapConfig()
    if not rows:
        raise ValueError("empty rows")
    rng = np.random.default_rng(settings.seed)
    strata = [(row.site, row.bclc_stage, row.etiology) for row in rows]
    samples: list[float] = []
    for _ in range(settings.resamples):
        indices = stratified_indices(strata, rng)
        labels = [rows[index].y_true for index in indices]
        scores = [rows[index].y_score for index in indices]
        samples.append(metric(labels, scores))
    observed = metric([row.y_true for row in rows], [row.y_score for row in rows])
    interval = percentile_interval(samples, settings.confidence)
    return ConfidenceInterval(observed, interval.lower, interval.upper, settings.confidence)


def paired_bootstrap(
    labels: Sequence[int],
    first: Sequence[float],
    second: Sequence[float],
    metric: Callable[[Sequence[int], Sequence[float]], float],
    strata: Sequence[tuple[str, ...]],
    config: BootstrapConfig | None = None,
) -> PairedBootstrapResult:
    settings = config or BootstrapConfig()
    if not (len(labels) == len(first) == len(second) == len(strata)):
        raise ValueError("lengths differ")
    rng = np.random.default_rng(settings.seed)
    differences: list[float] = []
    for _ in range(settings.resamples):
        indices = stratified_indices(strata, rng)
        sampled_labels = [labels[index] for index in indices]
        first_score = metric(sampled_labels, [first[index] for index in indices])
        second_score = metric(sampled_labels, [second[index] for index in indices])
        differences.append(first_score - second_score)
    observed = metric(labels, first) - metric(labels, second)
    interval = percentile_interval(differences, settings.confidence)
    nonpositive = sum(value <= 0.0 for value in differences)
    nonnegative = sum(value >= 0.0 for value in differences)
    p_value = min(1.0, 2.0 * min(nonpositive, nonnegative) / settings.resamples)
    return PairedBootstrapResult(
        observed,
        ConfidenceInterval(observed, interval.lower, interval.upper, settings.confidence),
        p_value,
        tuple(differences),
    )


def bonferroni(p_values: Sequence[float]) -> tuple[float, ...]:
    count = len(p_values)
    return tuple(min(1.0, value * count) for value in p_values)


def cohen_d(first: Sequence[float], second: Sequence[float]) -> float:
    if len(first) < 2 or len(second) < 2:
        raise ValueError("at least two observations per group are required")
    left = np.asarray(first, dtype=np.float64)
    right = np.asarray(second, dtype=np.float64)
    pooled = np.sqrt(
        ((len(left) - 1) * left.var(ddof=1) + (len(right) - 1) * right.var(ddof=1))
        / (len(left) + len(right) - 2)
    )
    if pooled == 0.0:
        return 0.0
    return float((left.mean() - right.mean()) / pooled)


def cohen_h(first: float, second: float) -> float:
    if not 0.0 <= first <= 1.0 or not 0.0 <= second <= 1.0:
        raise ValueError("proportions outside [0, 1]")
    return float(2.0 * (np.arcsin(np.sqrt(first)) - np.arcsin(np.sqrt(second))))


def site_range(values: Mapping[str, float]) -> float:
    if not values:
        raise ValueError("empty site values")
    return max(values.values()) - min(values.values())


def mcid_crossing_rate(differences: Sequence[float], threshold: float) -> float:
    if not differences:
        raise ValueError("empty differences")
    return sum(value >= threshold for value in differences) / len(differences)
