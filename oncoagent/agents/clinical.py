from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

from oncoagent.agents.base import ClinicalAgent
from oncoagent.coordination.router import RoutePlan
from oncoagent.guidelines.bclc import BCLCRuleBase
from oncoagent.models.types import (
    ConflictSignal,
    Distribution,
    PatientBundle,
    Stage,
    StageOutput,
)


def _sigmoid(value: float) -> float:
    if value >= 0.0:
        return 1.0 / (1.0 + math.exp(-value))
    exponential = math.exp(value)
    return exponential / (1.0 + exponential)


def _binary_distribution(positive: float, yes: str, no: str) -> Distribution:
    probability = min(0.999, max(0.001, positive))
    return Distribution((no, yes), (1.0 - probability, probability))


def _categorical_distribution(
    labels: tuple[str, ...], selected: str, confidence: float
) -> Distribution:
    bounded = min(0.999, max(1.0 / len(labels) + 0.001, confidence))
    remainder = (1.0 - bounded) / (len(labels) - 1)
    values = tuple(bounded if label == selected else remainder for label in labels)
    return Distribution(labels, values)


class ScreeningAgent(ClinicalAgent):
    stage = Stage.SCREENING

    def execute(
        self,
        bundle: PatientBundle,
        inputs: Mapping[str, Any],
        context: Mapping[str, Any],
        route: RoutePlan,
        feedback: ConflictSignal | None = None,
    ) -> StageOutput:
        age = float(inputs.get("patient_age", bundle.metadata.get("patient_age", 60.0)))
        afp = float(inputs.get("afp_ng_ml", 5.0))
        cirrhosis = bool(inputs.get("cirrhosis", False))
        viral = bool(inputs.get("viral_hepatitis", False))
        nodule = bool(inputs.get("ultrasound_nodule", False))
        score = _sigmoid(
            -4.0
            + 0.025 * age
            + 0.018 * min(afp, 200.0)
            + 1.4 * cirrhosis
            + 0.8 * viral
            + 1.6 * nodule
        )
        distribution = _binary_distribution(score, "screen_positive", "screen_negative")
        findings = {
            "surveillance_eligible": cirrhosis or viral,
            "afp_ng_ml": max(0.0, afp),
            "ultrasound_nodule": nodule,
            "screening_risk_score": score,
        }
        return StageOutput(
            stage=self.stage,
            prediction=distribution.prediction,
            distribution=distribution,
            uncertainty=min(1.0, route.uncertainty + abs(0.5 - score) * 0.2),
            findings=findings,
            rationale_codes=("AFP", "CIRRHOSIS", "ULTRASOUND"),
        )


class DiagnosisAgent(ClinicalAgent):
    stage = Stage.DIAGNOSIS

    def execute(
        self,
        bundle: PatientBundle,
        inputs: Mapping[str, Any],
        context: Mapping[str, Any],
        route: RoutePlan,
        feedback: ConflictSignal | None = None,
    ) -> StageOutput:
        enhancement = bool(inputs.get("ct_arterial_enhancement", False))
        washout = bool(inputs.get("ct_washout", False))
        capsule = bool(inputs.get("ct_capsule", False))
        count = max(0, int(inputs.get("ct_lesion_count", 0)))
        size = max(0.0, float(inputs.get("ct_largest_lesion_mm", 0.0)))
        if enhancement and washout and size >= 10.0:
            lirads = "LR-5"
            confidence = 0.90 + 0.03 * capsule
        elif enhancement and size >= 10.0:
            lirads = "LR-4"
            confidence = 0.76
        elif count > 0:
            lirads = "LR-3"
            confidence = 0.68
        else:
            lirads = "LR-1"
            confidence = 0.91
        labels = ("LR-1", "LR-2", "LR-3", "LR-4", "LR-5")
        distribution = _categorical_distribution(labels, lirads, confidence)
        liver_volume = max(0.0, float(inputs.get("liver_volume_ml", 1400.0)))
        tumor_volume = max(0.0, float(inputs.get("tumor_volume_ml", count * size**3 / 6000.0)))
        findings = {
            "ct_arterial_enhancement": enhancement,
            "ct_washout": washout,
            "ct_capsule": capsule,
            "ct_lesion_count": count,
            "ct_largest_lesion_mm": size,
            "lirads_category": lirads,
            "liver_volume_ml": liver_volume,
            "tumor_volume_ml": tumor_volume,
        }
        return StageOutput(
            self.stage,
            distribution.prediction,
            distribution,
            min(1.0, route.uncertainty + (1.0 - confidence) * 0.5),
            findings,
            ("ARTERIAL_ENHANCEMENT", "WASHOUT", "CAPSULE"),
        )


class StagingAgent(ClinicalAgent):
    stage = Stage.STAGING

    def __init__(self, rules: BCLCRuleBase | None = None) -> None:
        self.rules = rules or BCLCRuleBase()

    def execute(
        self,
        bundle: PatientBundle,
        inputs: Mapping[str, Any],
        context: Mapping[str, Any],
        route: RoutePlan,
        feedback: ConflictSignal | None = None,
    ) -> StageOutput:
        merged = dict(context)
        merged.update(inputs)
        if feedback is not None:
            merged.update(feedback.evidence)
        stage = self.rules.infer_stage(merged)
        confidence = 0.84
        if stage.value in {"B", "C"}:
            confidence = 0.79
        if stage.value == "unknown":
            confidence = 0.35
        distribution = _categorical_distribution(
            ("0", "A", "B", "C", "D", "unknown"), stage.value, confidence
        )
        findings = {
            "portal_vein_invasion": bool(merged.get("portal_vein_invasion", False)),
            "extrahepatic_spread": bool(merged.get("extrahepatic_spread", False)),
            "ecog_status": max(0, int(merged.get("ecog_status", 0))),
            "child_pugh_class": str(merged.get("child_pugh_class", "A")),
            "bclc_stage": stage.value,
        }
        return StageOutput(
            self.stage,
            distribution.prediction,
            distribution,
            min(1.0, route.uncertainty + (1.0 - confidence) * 0.4),
            findings,
            ("BCLC", "TUMOR_BURDEN", "LIVER_FUNCTION", "ECOG"),
        )


class TreatmentAgent(ClinicalAgent):
    stage = Stage.TREATMENT

    def __init__(self, rules: BCLCRuleBase | None = None) -> None:
        self.rules = rules or BCLCRuleBase()

    def execute(
        self,
        bundle: PatientBundle,
        inputs: Mapping[str, Any],
        context: Mapping[str, Any],
        route: RoutePlan,
        feedback: ConflictSignal | None = None,
    ) -> StageOutput:
        merged = dict(context)
        merged.update(inputs)
        stage_value = str(merged.get("bclc_stage", "unknown"))
        from oncoagent.models.types import BCLCStage

        stage = BCLCStage(stage_value)
        treatment = self.rules.treatment_for(stage, merged)
        labels = (
            "resection",
            "transplant",
            "ablation",
            "tace",
            "systemic_therapy",
            "best_supportive_care",
            "human_review",
        )
        feasibility = float(merged.get("treatment_feasibility", 0.88))
        confidence = min(0.94, max(0.51, feasibility))
        distribution = _categorical_distribution(labels, treatment, confidence)
        findings = {
            "resectable": bool(merged.get("resectable", treatment == "resection")),
            "transplant_eligible": bool(
                merged.get("transplant_eligible", treatment == "transplant")
            ),
            "ablation_eligible": bool(merged.get("ablation_eligible", treatment == "ablation")),
            "tace_eligible": bool(merged.get("tace_eligible", treatment == "tace")),
            "systemic_therapy_eligible": bool(
                merged.get("systemic_therapy_eligible", treatment == "systemic_therapy")
            ),
            "best_supportive_care": treatment == "best_supportive_care",
            "treatment_class": treatment,
            "treatment_feasibility": feasibility,
        }
        return StageOutput(
            self.stage,
            distribution.prediction,
            distribution,
            min(1.0, route.uncertainty + (1.0 - confidence) * 0.4),
            findings,
            ("BCLC_TREATMENT", "FEASIBILITY"),
        )


class FollowUpAgent(ClinicalAgent):
    stage = Stage.FOLLOW_UP

    def __init__(self, rules: BCLCRuleBase | None = None) -> None:
        self.rules = rules or BCLCRuleBase()

    def execute(
        self,
        bundle: PatientBundle,
        inputs: Mapping[str, Any],
        context: Mapping[str, Any],
        route: RoutePlan,
        feedback: ConflictSignal | None = None,
    ) -> StageOutput:
        treatment = str(context.get("treatment_class", "human_review"))
        interval = self.rules.follow_up_interval(treatment)
        tumor_volume = float(context.get("tumor_volume_ml", 0.0))
        invasion = bool(context.get("portal_vein_invasion", False))
        recurrence = _sigmoid(-2.3 + 0.01 * min(tumor_volume, 200.0) + 0.9 * invasion)
        modality = "contrast_ct_or_mri"
        if treatment == "best_supportive_care":
            modality = "symptom_directed"
        labels = ("standard_surveillance", "intensive_surveillance")
        selected = labels[1] if recurrence >= 0.5 else labels[0]
        confidence = 0.82 if abs(recurrence - 0.5) > 0.15 else 0.68
        distribution = _categorical_distribution(labels, selected, confidence)
        findings = {
            "recurrence_risk_6m": recurrence * 0.55,
            "recurrence_risk_12m": recurrence * 0.78,
            "recurrence_risk_24m": recurrence,
            "follow_up_interval_months": interval,
            "follow_up_modality": modality,
            "overall_survival_risk": min(1.0, recurrence * 0.8),
        }
        return StageOutput(
            self.stage,
            distribution.prediction,
            distribution,
            min(1.0, route.uncertainty + (1.0 - confidence) * 0.4),
            findings,
            ("RECURRENCE_RISK", "TREATMENT_RESPONSE"),
        )
