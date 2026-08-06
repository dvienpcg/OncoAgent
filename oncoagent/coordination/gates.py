from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from oncoagent.models.types import (
    GateAction,
    GateDecision,
    GateScores,
    Modality,
    Stage,
    StageOutput,
)


@dataclass(frozen=True)
class GateThresholds:
    completeness: float = 0.95
    consistency: float = 0.90
    guideline: float = 1.0


class VerificationGateNetwork:
    def __init__(
        self,
        thresholds: GateThresholds | None = None,
        confidence_thresholds: Mapping[Stage, float] | None = None,
    ) -> None:
        self.thresholds = thresholds or GateThresholds()
        self.confidence_thresholds = confidence_thresholds or {
            Stage.SCREENING: 0.62,
            Stage.DIAGNOSIS: 0.68,
            Stage.STAGING: 0.78,
            Stage.TREATMENT: 0.78,
            Stage.FOLLOW_UP: 0.65,
        }
        self.required_fields = {
            Stage.SCREENING: ("surveillance_eligible", "screening_risk_score"),
            Stage.DIAGNOSIS: ("lirads_category", "ct_lesion_count", "ct_largest_lesion_mm"),
            Stage.STAGING: (
                "portal_vein_invasion",
                "extrahepatic_spread",
                "ecog_status",
                "child_pugh_class",
                "bclc_stage",
            ),
            Stage.TREATMENT: ("treatment_class", "treatment_feasibility"),
            Stage.FOLLOW_UP: ("follow_up_interval_months", "follow_up_modality"),
        }
        self.modality_requirements = {
            Stage.SCREENING: (Modality.LABORATORY,),
            Stage.DIAGNOSIS: (Modality.IMAGING,),
            Stage.STAGING: (Modality.IMAGING, Modality.EHR),
            Stage.TREATMENT: (Modality.EHR,),
            Stage.FOLLOW_UP: (Modality.EHR,),
        }

    def evaluate(
        self,
        output: StageOutput,
        context: Mapping[str, Any],
        guideline_score: float,
    ) -> GateDecision:
        required = self.required_fields[output.stage]
        available = sum(
            1 for key in required if key in output.findings or context.get(key) is not None
        )
        completeness = available / len(required)
        consistency = self._consistency(output, context)
        confidence = output.distribution.confidence
        scores = GateScores(
            completeness=completeness,
            consistency=consistency,
            guideline=guideline_score,
            confidence=confidence,
        )
        margins = {
            "completeness": completeness - self.thresholds.completeness,
            "consistency": consistency - self.thresholds.consistency,
            "guideline": guideline_score - self.thresholds.guideline,
            "confidence": confidence - self.confidence_thresholds[output.stage],
        }
        failed = tuple(name for name, margin in margins.items() if margin < 0.0)
        if not failed:
            return GateDecision(True, GateAction.ADVANCE, scores)
        worst = min(failed, key=margins.__getitem__)
        if worst in {"completeness", "consistency"}:
            return GateDecision(
                False,
                GateAction.REQUERY_MODALITY,
                scores,
                worst,
                self.modality_requirements[output.stage],
            )
        if worst == "guideline":
            return GateDecision(False, GateAction.INVOKE_BTF, scores, worst)
        return GateDecision(False, GateAction.HUMAN_ESCALATION, scores, worst)

    def _consistency(self, output: StageOutput, context: Mapping[str, Any]) -> float:
        contradictions = 0
        comparisons = 0
        for key, value in output.findings.items():
            if key in context and context[key] is not None:
                comparisons += 1
                if context[key] != value:
                    contradictions += 1
        if comparisons == 0:
            return 1.0
        return 1.0 - contradictions / comparisons
