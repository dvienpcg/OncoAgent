from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from oncoagent.models.types import EvaluationRow, MetricResult, SiteResult
from oncoagent.statistics.bootstrap import BootstrapConfig, bootstrap_metric, site_range
from oncoagent.statistics.metrics import accuracy, metric_result, roc_auc


@dataclass(frozen=True)
class CompositeWeights:
    screening: float
    liver_segmentation: float
    tumor_segmentation: float
    staging: float
    treatment: float
    survival: float

    def __post_init__(self) -> None:
        if abs(sum(self.values()) - 1.0) > 1e-8:
            raise ValueError("composite weights must sum to one")
        if any(value < 0.0 for value in self.values()):
            raise ValueError("composite weight is negative")

    def values(self) -> tuple[float, ...]:
        return (
            self.screening,
            self.liver_segmentation,
            self.tumor_segmentation,
            self.staging,
            self.treatment,
            self.survival,
        )


class PathwayEvaluator:
    def __init__(
        self,
        weights: CompositeWeights,
        bootstrap: BootstrapConfig | None = None,
    ) -> None:
        self.weights = weights
        self.bootstrap = bootstrap or BootstrapConfig()

    def composite(self, metrics: Mapping[str, float]) -> float:
        names = (
            "screening",
            "liver_segmentation",
            "tumor_segmentation",
            "staging",
            "treatment",
            "survival",
        )
        missing = tuple(name for name in names if name not in metrics)
        if missing:
            raise ValueError(f"missing composite metrics: {missing}")
        return sum(
            metrics[name] * weight
            for name, weight in zip(names, self.weights.values(), strict=True)
        )

    def binary_metric(
        self,
        name: str,
        rows: Sequence[EvaluationRow],
        score_based: bool = False,
    ) -> MetricResult:
        if score_based:
            value = roc_auc([row.y_true for row in rows], [row.y_score for row in rows])
            interval = bootstrap_metric(rows, roc_auc, self.bootstrap)
        else:
            value = accuracy([row.y_true for row in rows], [row.y_pred for row in rows])
            transformed = tuple(
                EvaluationRow(
                    row.case_id,
                    row.site,
                    row.bclc_stage,
                    row.etiology,
                    row.y_true,
                    float(row.y_pred),
                    row.y_pred,
                )
                for row in rows
            )
            interval = bootstrap_metric(
                transformed,
                lambda labels, scores: accuracy(labels, [int(score) for score in scores]),
                self.bootstrap,
            )
        return metric_result(name, value, len(rows), interval)

    def per_site(
        self,
        rows: Sequence[EvaluationRow],
        name: str,
        score_based: bool = False,
    ) -> tuple[SiteResult, ...]:
        grouped: dict[str, list[EvaluationRow]] = defaultdict(list)
        for row in rows:
            grouped[row.site].append(row)
        return tuple(
            SiteResult(site, (self.binary_metric(name, values, score_based),))
            for site, values in sorted(grouped.items())
        )

    def maximum_site_range(self, results: Sequence[SiteResult], metric_name: str) -> float:
        values: dict[str, float] = {}
        for result in results:
            for metric in result.metrics:
                if metric.name == metric_name:
                    values[result.site] = metric.value
        return site_range(values)


def default_weights() -> CompositeWeights:
    return CompositeWeights(0.15, 0.10, 0.15, 0.25, 0.25, 0.10)
