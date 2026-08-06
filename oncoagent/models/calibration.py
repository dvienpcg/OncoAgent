from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class IsotonicBin:
    lower: float
    upper: float
    value: float
    count: int


class IsotonicCalibrator:
    def __init__(self) -> None:
        self._thresholds: np.ndarray | None = None
        self._values: np.ndarray | None = None
        self._bins: tuple[IsotonicBin, ...] = ()

    @property
    def fitted(self) -> bool:
        return self._thresholds is not None and self._values is not None

    @property
    def bins(self) -> tuple[IsotonicBin, ...]:
        return self._bins

    def fit(self, scores: Sequence[float], labels: Sequence[int]) -> IsotonicCalibrator:
        if len(scores) != len(labels):
            raise ValueError("lengths differ")
        if not scores:
            raise ValueError("empty calibration data")
        array_scores = np.asarray(scores, dtype=np.float64)
        array_labels = np.asarray(labels, dtype=np.float64)
        if np.any(array_scores < 0.0) or np.any(array_scores > 1.0):
            raise ValueError("score outside [0, 1]")
        if np.any((array_labels != 0.0) & (array_labels != 1.0)):
            raise ValueError("label outside {0, 1}")
        order = np.argsort(array_scores, kind="stable")
        sorted_scores = array_scores[order]
        sorted_labels = array_labels[order]
        blocks: list[dict[str, float]] = []
        for score, label in zip(sorted_scores, sorted_labels, strict=True):
            blocks.append(
                {
                    "lower": float(score),
                    "upper": float(score),
                    "sum": float(label),
                    "count": 1.0,
                }
            )
            while len(blocks) >= 2:
                left = blocks[-2]
                right = blocks[-1]
                left_mean = left["sum"] / left["count"]
                right_mean = right["sum"] / right["count"]
                if left_mean <= right_mean:
                    break
                merged = {
                    "lower": left["lower"],
                    "upper": right["upper"],
                    "sum": left["sum"] + right["sum"],
                    "count": left["count"] + right["count"],
                }
                blocks[-2:] = [merged]
        thresholds = []
        values = []
        bins = []
        for block in blocks:
            value = block["sum"] / block["count"]
            thresholds.append(block["upper"])
            values.append(value)
            bins.append(
                IsotonicBin(
                    block["lower"],
                    block["upper"],
                    value,
                    int(block["count"]),
                )
            )
        self._thresholds = np.asarray(thresholds, dtype=np.float64)
        self._values = np.asarray(values, dtype=np.float64)
        self._bins = tuple(bins)
        return self

    def transform(self, scores: Sequence[float]) -> tuple[float, ...]:
        if self._thresholds is None or self._values is None:
            raise RuntimeError("calibrator is not fitted")
        array = np.asarray(scores, dtype=np.float64)
        if np.any(array < 0.0) or np.any(array > 1.0):
            raise ValueError("score outside [0, 1]")
        indices = np.searchsorted(self._thresholds, array, side="left")
        indices = np.minimum(indices, len(self._values) - 1)
        return tuple(float(value) for value in self._values[indices])

    def fit_transform(
        self,
        scores: Sequence[float],
        labels: Sequence[int],
    ) -> tuple[float, ...]:
        self.fit(scores, labels)
        return self.transform(scores)
