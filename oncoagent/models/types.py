from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class Stage(StrEnum):
    SCREENING = "screening"
    DIAGNOSIS = "diagnosis"
    STAGING = "staging"
    TREATMENT = "treatment"
    FOLLOW_UP = "follow_up"


class Modality(StrEnum):
    IMAGING = "imaging"
    GENOMICS = "genomics"
    EHR = "ehr"
    LABORATORY = "laboratory"
    CLINICAL_NOTE = "clinical_note"


class GateAction(StrEnum):
    ADVANCE = "advance"
    REQUERY_MODALITY = "requery_modality"
    INVOKE_BTF = "invoke_btf"
    HUMAN_ESCALATION = "human_escalation"


class BCLCStage(StrEnum):
    ZERO = "0"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Distribution:
    labels: tuple[str, ...]
    probabilities: tuple[float, ...]

    def __post_init__(self) -> None:
        if len(self.labels) != len(self.probabilities):
            raise ValueError("labels and probabilities differ in length")
        if not self.labels:
            raise ValueError("distribution is empty")
        if any(value < 0.0 or value > 1.0 for value in self.probabilities):
            raise ValueError("probability outside [0, 1]")
        if abs(sum(self.probabilities) - 1.0) > 1e-6:
            raise ValueError("probabilities do not sum to one")

    @property
    def confidence(self) -> float:
        return max(self.probabilities)

    @property
    def prediction(self) -> str:
        index = max(range(len(self.probabilities)), key=self.probabilities.__getitem__)
        return self.labels[index]


@dataclass(frozen=True)
class StageOutput:
    stage: Stage
    prediction: str
    distribution: Distribution
    uncertainty: float
    findings: Mapping[str, Any]
    rationale_codes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.uncertainty < 0.0 or self.uncertainty > 1.0:
            raise ValueError("uncertainty outside [0, 1]")
        if self.prediction != self.distribution.prediction:
            raise ValueError("prediction differs from distribution mode")


@dataclass(frozen=True)
class PatientBundle:
    case_id: str
    modalities: Mapping[Modality, Mapping[str, Any]]
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def available_modalities(self) -> frozenset[Modality]:
        return frozenset(key for key, value in self.modalities.items() if value)


@dataclass(frozen=True)
class GateScores:
    completeness: float
    consistency: float
    guideline: float
    confidence: float

    def values(self) -> tuple[float, float, float, float]:
        return self.completeness, self.consistency, self.guideline, self.confidence


@dataclass(frozen=True)
class GateDecision:
    passed: bool
    action: GateAction
    scores: GateScores
    failed_criterion: str | None = None
    requested_modalities: tuple[Modality, ...] = ()


@dataclass(frozen=True)
class ConflictSignal:
    source_stage: Stage
    target_stage: Stage
    label: str
    magnitude: float
    evidence: Mapping[str, Any]

    def __post_init__(self) -> None:
        if self.magnitude < 0.0 or self.magnitude > 1.0:
            raise ValueError("conflict magnitude outside [0, 1]")


@dataclass(frozen=True)
class ContextVersion:
    version: int
    stage: Stage
    values: Mapping[str, Any]
    output: StageOutput


@dataclass(frozen=True)
class RefinementRecord:
    iteration: int
    conflict: ConflictSignal
    accepted: bool
    old_prediction: str
    new_prediction: str


@dataclass(frozen=True)
class PathwayResult:
    case_id: str
    outputs: tuple[StageOutput, ...]
    context: Mapping[str, Any]
    gates: tuple[GateDecision, ...]
    refinements: tuple[RefinementRecord, ...]
    escalated: bool
    completed: bool

    def output_for(self, stage: Stage) -> StageOutput:
        for output in self.outputs:
            if output.stage is stage:
                return output
        raise KeyError(stage.value)

    def predictions(self) -> Mapping[str, str]:
        return {output.stage.value: output.prediction for output in self.outputs}


@dataclass(frozen=True)
class EvaluationRow:
    case_id: str
    site: str
    bclc_stage: str
    etiology: str
    y_true: int
    y_score: float
    y_pred: int


@dataclass(frozen=True)
class ConfidenceInterval:
    estimate: float
    lower: float
    upper: float
    level: float = 0.95


@dataclass(frozen=True)
class MetricResult:
    name: str
    value: float
    interval: ConfidenceInterval | None
    sample_size: int


@dataclass(frozen=True)
class SiteResult:
    site: str
    metrics: Sequence[MetricResult]
