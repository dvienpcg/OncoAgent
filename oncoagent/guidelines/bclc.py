from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from oncoagent.models.types import BCLCStage, Stage, StageOutput


@dataclass(frozen=True)
class GuidelineAssessment:
    score: float
    codes: tuple[str, ...]
    expected: str | None


class BCLCRuleBase:
    def infer_stage(self, values: Mapping[str, Any]) -> BCLCStage:
        ecog = int(values.get("ecog_status", 0))
        child = str(values.get("child_pugh_class", "A")).upper()
        spread = bool(values.get("extrahepatic_spread", False))
        invasion = bool(values.get("portal_vein_invasion", False))
        count = int(values.get("ct_lesion_count", 1))
        size = float(values.get("ct_largest_lesion_mm", 0.0))
        if ecog > 2 or child == "C":
            return BCLCStage.D
        if spread or invasion or ecog in {1, 2}:
            return BCLCStage.C
        if count == 1 and size <= 20.0 and ecog == 0:
            return BCLCStage.ZERO
        if (count == 1 or count <= 3 and size <= 30.0) and ecog == 0:
            return BCLCStage.A
        if count > 1 and ecog == 0:
            return BCLCStage.B
        return BCLCStage.UNKNOWN

    def treatment_for(self, stage: BCLCStage, values: Mapping[str, Any]) -> str:
        if stage is BCLCStage.ZERO:
            if bool(values.get("resectable", True)):
                return "resection"
            return "ablation"
        if stage is BCLCStage.A:
            if bool(values.get("transplant_eligible", False)):
                return "transplant"
            if bool(values.get("resectable", True)):
                return "resection"
            return "ablation"
        if stage is BCLCStage.B:
            return "tace"
        if stage is BCLCStage.C:
            return "systemic_therapy"
        if stage is BCLCStage.D:
            return "best_supportive_care"
        return "human_review"

    def follow_up_interval(self, treatment: str) -> float:
        intervals = {
            "resection": 3.0,
            "transplant": 3.0,
            "ablation": 3.0,
            "tace": 3.0,
            "systemic_therapy": 2.0,
            "best_supportive_care": 1.0,
            "human_review": 1.0,
        }
        return intervals.get(treatment, 3.0)

    def assess(self, output: StageOutput, context: Mapping[str, Any]) -> GuidelineAssessment:
        merged = dict(context)
        merged.update(output.findings)
        if output.stage is Stage.STAGING:
            expected = self.infer_stage(merged).value
            match = output.prediction == expected
            return GuidelineAssessment(
                float(match), (() if match else ("BCLC_MISMATCH",)), expected
            )
        if output.stage is Stage.TREATMENT:
            stage = BCLCStage(str(merged.get("bclc_stage", "unknown")))
            expected = self.treatment_for(stage, merged)
            match = output.prediction == expected
            return GuidelineAssessment(
                float(match), (() if match else ("TREATMENT_MISMATCH",)), expected
            )
        if output.stage is Stage.FOLLOW_UP:
            treatment = str(merged.get("treatment_class", "human_review"))
            expected_value = self.follow_up_interval(treatment)
            observed = float(merged.get("follow_up_interval_months", -1.0))
            match = abs(expected_value - observed) < 1e-6
            return GuidelineAssessment(
                float(match), (() if match else ("FOLLOWUP_MISMATCH",)), str(expected_value)
            )
        return GuidelineAssessment(1.0, (), None)
