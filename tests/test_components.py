from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from oncoagent.agents.clinical import DiagnosisAgent, ScreeningAgent
from oncoagent.coordination.context import AccumulatedClinicalContext
from oncoagent.coordination.feedback import BidirectionalTemporalFeedback
from oncoagent.coordination.gates import VerificationGateNetwork
from oncoagent.coordination.router import RoutePlan, StageAdaptiveMultimodalRouter
from oncoagent.data.harmonize import descriptor, file_sha256, harmonize_lits, harmonize_mimic
from oncoagent.evaluation.evaluator import PathwayEvaluator, default_weights
from oncoagent.evaluation.perturbations import mask_laboratory_values, ocr_noise
from oncoagent.evaluation.reported import reported_result, results_for_metric
from oncoagent.guidelines.bclc import BCLCRuleBase
from oncoagent.guidelines.conflicts import CLINICAL_CONFLICTS, known_conflict
from oncoagent.models.calibration import IsotonicCalibrator
from oncoagent.models.schema import ACC_FIELDS, validate_context
from oncoagent.models.types import (
    BCLCStage,
    Distribution,
    Modality,
    PatientBundle,
    Stage,
    StageOutput,
)
from oncoagent.statistics.bootstrap import (
    BootstrapConfig,
    bonferroni,
    cohen_d,
    mcid_crossing_rate,
    percentile_interval,
)
from oncoagent.statistics.metrics import (
    accuracy,
    balanced_accuracy,
    brier_score,
    cohen_kappa,
    concordance_index,
    dice_score,
    expected_calibration_error,
    f1_score,
    jaccard_score,
    log_loss,
    macro_f1,
    precision,
    roc_auc,
    sensitivity,
    specificity,
    wilson_interval,
)


def route(stage: Stage) -> RoutePlan:
    return RoutePlan(stage, (Modality.IMAGING,), (), 1.0, 0.0)


def complete_bundle() -> PatientBundle:
    return PatientBundle(
        "case-001",
        {
            Modality.IMAGING: {
                "ct_arterial_enhancement": True,
                "ct_washout": True,
                "ct_capsule": True,
                "ct_lesion_count": 1,
                "ct_largest_lesion_mm": 18.0,
                "liver_volume_ml": 1400.0,
                "tumor_volume_ml": 12.0,
                "ultrasound_nodule": True,
            },
            Modality.LABORATORY: {
                "afp_ng_ml": 42.0,
                "albumin_g_dl": 4.1,
                "bilirubin_mg_dl": 0.8,
                "inr": 1.0,
                "platelets_10e9_l": 170.0,
            },
            Modality.EHR: {
                "patient_age": 62.0,
                "patient_sex": "female",
                "etiology": "HBV",
                "cirrhosis": True,
                "viral_hepatitis": True,
                "portal_vein_invasion": False,
                "extrahepatic_spread": False,
                "ecog_status": 0,
                "child_pugh_class": "A",
                "resectable": True,
                "treatment_feasibility": 0.92,
            },
            Modality.GENOMICS: {
                "genomic_risk_score": 0.44,
                "tp53_status": "wild_type",
            },
        },
    )


def test_distribution_validation() -> None:
    distribution = Distribution(("negative", "positive"), (0.25, 0.75))
    assert distribution.prediction == "positive"
    assert distribution.confidence == 0.75


@pytest.mark.parametrize(
    ("probabilities", "message"),
    [
        ((0.5,), "labels"),
        ((-0.1, 1.1), "probability"),
        ((0.4, 0.4), "sum"),
    ],
)
def test_distribution_rejects_invalid(probabilities: tuple[float, ...], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        Distribution(("a", "b"), probabilities)


def test_schema_has_sixty_four_fields() -> None:
    assert len(ACC_FIELDS) == 64
    assert not validate_context({"patient_age": 50.0, "bclc_stage": "A"})


def test_conflict_schema_has_twenty_seven_labels() -> None:
    assert len(CLINICAL_CONFLICTS) == 27
    assert known_conflict("portal_invasion_detected")
    assert not known_conflict("unregistered")


def test_screening_agent_uses_clinical_risk() -> None:
    bundle = complete_bundle()
    plan = RoutePlan(Stage.SCREENING, (Modality.LABORATORY, Modality.EHR), (), 1.0, 0.0)
    inputs = dict(bundle.modalities[Modality.LABORATORY])
    inputs.update(bundle.modalities[Modality.EHR])
    output = ScreeningAgent().execute(bundle, inputs, {}, plan)
    assert output.stage is Stage.SCREENING
    assert output.prediction == "screen_positive"
    assert output.findings["surveillance_eligible"] is True


def test_diagnosis_agent_assigns_lr5() -> None:
    bundle = complete_bundle()
    output = DiagnosisAgent().execute(
        bundle,
        bundle.modalities[Modality.IMAGING],
        {},
        route(Stage.DIAGNOSIS),
    )
    assert output.prediction == "LR-5"
    assert output.findings["ct_largest_lesion_mm"] == 18.0


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        ({"ecog_status": 3, "child_pugh_class": "A"}, BCLCStage.D),
        ({"ecog_status": 0, "child_pugh_class": "C"}, BCLCStage.D),
        ({"extrahepatic_spread": True}, BCLCStage.C),
        ({"portal_vein_invasion": True}, BCLCStage.C),
        ({"ct_lesion_count": 1, "ct_largest_lesion_mm": 18.0}, BCLCStage.ZERO),
        ({"ct_lesion_count": 1, "ct_largest_lesion_mm": 40.0}, BCLCStage.A),
        ({"ct_lesion_count": 4, "ct_largest_lesion_mm": 35.0}, BCLCStage.B),
    ],
)
def test_bclc_stage_rules(values: dict[str, object], expected: BCLCStage) -> None:
    defaults: dict[str, object] = {"ecog_status": 0, "child_pugh_class": "A"}
    defaults.update(values)
    assert BCLCRuleBase().infer_stage(defaults) is expected


@pytest.mark.parametrize(
    ("stage", "expected"),
    [
        (BCLCStage.ZERO, "resection"),
        (BCLCStage.A, "resection"),
        (BCLCStage.B, "tace"),
        (BCLCStage.C, "systemic_therapy"),
        (BCLCStage.D, "best_supportive_care"),
    ],
)
def test_bclc_treatment_rules(stage: BCLCStage, expected: str) -> None:
    assert BCLCRuleBase().treatment_for(stage, {"resectable": True}) == expected


def test_acc_versions_and_rollback() -> None:
    context = AccumulatedClinicalContext()
    distribution = Distribution(("no", "yes"), (0.1, 0.9))
    first = StageOutput(
        Stage.SCREENING,
        "yes",
        distribution,
        0.1,
        {"surveillance_eligible": True, "screening_risk_score": 0.9},
    )
    context.append(first)
    assert context.version == 1
    assert context.contains("screening_risk_score")
    snapshot = context.rollback(0)
    assert snapshot.version == 0
    assert not context.contains("screening_risk_score")


def test_router_respects_budget() -> None:
    router = StageAdaptiveMultimodalRouter()
    plan = router.route(Stage.SCREENING, complete_bundle())
    assert plan.cost <= router.budget_for(Stage.SCREENING)
    assert Modality.LABORATORY in plan.active


def test_feedback_detects_invasion_mismatch() -> None:
    feedback = BidirectionalTemporalFeedback()
    signals = feedback.detect(
        (),
        {
            "bclc_stage": "A",
            "treatment_class": "resection",
            "portal_vein_invasion": True,
            "extrahepatic_spread": False,
            "ecog_status": 0,
            "child_pugh_class": "A",
        },
    )
    labels = {signal.label for signal in signals}
    assert "vascular_invasion_staging_mismatch" in labels
    assert "treatment_infeasible_resection" in labels


def test_isotonic_calibration_is_monotone() -> None:
    scores = (0.1, 0.2, 0.3, 0.4, 0.8, 0.9)
    labels = (0, 1, 0, 1, 1, 1)
    calibrated = IsotonicCalibrator().fit_transform(scores, labels)
    assert all(left <= right for left, right in zip(calibrated, calibrated[1:], strict=False))


def test_binary_metrics() -> None:
    labels = [0, 0, 1, 1]
    predictions = [0, 1, 1, 1]
    assert accuracy(labels, predictions) == 0.75
    assert sensitivity(labels, predictions) == 1.0
    assert specificity(labels, predictions) == 0.5
    assert precision(labels, predictions) == pytest.approx(2.0 / 3.0)
    assert f1_score(labels, predictions) == pytest.approx(0.8)
    assert balanced_accuracy(labels, predictions) == 0.75


def test_probability_metrics() -> None:
    labels = [0, 0, 1, 1]
    scores = [0.1, 0.4, 0.6, 0.9]
    assert roc_auc(labels, scores) == 1.0
    assert brier_score(labels, scores) == pytest.approx(0.085)
    assert log_loss(labels, scores) > 0.0
    assert expected_calibration_error(labels, scores, 2) >= 0.0


def test_segmentation_metrics() -> None:
    left = np.array([[1, 1], [0, 0]])
    right = np.array([[1, 0], [1, 0]])
    assert dice_score(left, right) == pytest.approx(0.5)
    assert jaccard_score(left, right) == pytest.approx(1.0 / 3.0)


def test_survival_concordance() -> None:
    assert concordance_index([1.0, 2.0, 3.0], [1, 1, 0], [0.9, 0.5, 0.1]) == 1.0


def test_multiclass_metrics() -> None:
    true = ["A", "A", "B", "C"]
    predicted = ["A", "B", "B", "C"]
    assert macro_f1(true, predicted) > 0.7
    assert cohen_kappa(true, predicted) > 0.6


def test_intervals_and_adjustments() -> None:
    interval = wilson_interval(8, 10)
    assert interval.lower < 0.8 < interval.upper
    percentile = percentile_interval([0.1, 0.2, 0.3])
    assert percentile.lower < percentile.upper
    assert bonferroni([0.01, 0.20]) == (0.02, 0.4)
    assert cohen_d([1.0, 2.0, 3.0], [0.0, 1.0, 2.0]) > 0.0
    assert mcid_crossing_rate([0.01, 0.06, 0.08], 0.05) == pytest.approx(2.0 / 3.0)


def test_harmonizers() -> None:
    lits = harmonize_lits({"case_id": "L1", "lesion_count": 2, "largest_lesion_mm": 30})
    mimic = harmonize_mimic({"case_id": "M1", "age": 70, "afp_ng_ml": 25})
    assert lits.metadata["site"] == "LiTS"
    assert mimic.metadata["site"] == "MIMIC-IV"
    assert descriptor("MIMIC-IV").restricted


def test_sha256(tmp_path: Path) -> None:
    path = tmp_path / "sample.bin"
    path.write_bytes(b"oncoagent")
    assert len(file_sha256(path)) == 64


def test_perturbations_are_deterministic() -> None:
    values = {
        "afp_ng_ml": 1.0,
        "albumin_g_dl": 4.0,
        "bilirubin_mg_dl": 1.0,
        "inr": 1.0,
        "platelets_10e9_l": 180.0,
    }
    first = mask_laboratory_values(values, 0.2, 7)
    second = mask_laboratory_values(values, 0.2, 7)
    assert first == second
    note = ocr_noise({"clinical_note": "stable clinical text"}, 0.2, 7)
    assert note.values["clinical_note"] != "stable clinical text"


def test_reported_results_registry() -> None:
    result = reported_result("main", "composite")
    assert result.value == 0.781
    assert len(results_for_metric("composite")) > 10


def test_pathway_composite() -> None:
    evaluator = PathwayEvaluator(default_weights(), BootstrapConfig(resamples=20))
    value = evaluator.composite(
        {
            "screening": 0.912,
            "liver_segmentation": 0.962,
            "tumor_segmentation": 0.788,
            "staging": 0.867,
            "treatment": 0.843,
            "survival": 0.763,
        }
    )
    assert 0.80 < value < 0.90


def test_gate_rejects_incomplete_stage() -> None:
    distribution = Distribution(("no", "yes"), (0.2, 0.8))
    output = StageOutput(Stage.STAGING, "yes", distribution, 0.2, {"bclc_stage": "A"})
    decision = VerificationGateNetwork().evaluate(output, {}, 1.0)
    assert not decision.passed
