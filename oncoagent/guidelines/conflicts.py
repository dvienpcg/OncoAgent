from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from oncoagent.models.types import Stage


@dataclass(frozen=True)
class ConflictDefinition:
    label: str
    source: Stage
    target: Stage
    default_magnitude: float
    evidence_keys: tuple[str, ...]


PORTAL_INVASION_DETECTED = ConflictDefinition(
    label="portal_invasion_detected",
    source=Stage.STAGING,
    target=Stage.TREATMENT,
    default_magnitude=0.31,
    evidence_keys=("patient_age", "patient_sex"),
)

EXTRAHEPATIC_SPREAD_DETECTED = ConflictDefinition(
    label="extrahepatic_spread_detected",
    source=Stage.STAGING,
    target=Stage.TREATMENT,
    default_magnitude=0.38,
    evidence_keys=("race_ethnicity", "etiology"),
)

ECOG_UPGRADED_TO_TWO = ConflictDefinition(
    label="ecog_upgraded_to_two",
    source=Stage.STAGING,
    target=Stage.TREATMENT,
    default_magnitude=0.45,
    evidence_keys=("surveillance_eligible", "afp_ng_ml"),
)

ECOG_UPGRADED_TO_THREE = ConflictDefinition(
    label="ecog_upgraded_to_three",
    source=Stage.STAGING,
    target=Stage.TREATMENT,
    default_magnitude=0.52,
    evidence_keys=("afp_l3_percent", "dcp_mau_ml"),
)

HEPATIC_RESERVE_CHILD_PUGH_B = ConflictDefinition(
    label="hepatic_reserve_child_pugh_b",
    source=Stage.STAGING,
    target=Stage.TREATMENT,
    default_magnitude=0.59,
    evidence_keys=("ultrasound_nodule", "ultrasound_size_mm"),
)

HEPATIC_RESERVE_CHILD_PUGH_C = ConflictDefinition(
    label="hepatic_reserve_child_pugh_c",
    source=Stage.STAGING,
    target=Stage.TREATMENT,
    default_magnitude=0.66,
    evidence_keys=("screening_interval_months", "screening_risk_score"),
)

TREATMENT_INFEASIBLE_RESECTION = ConflictDefinition(
    label="treatment_infeasible_resection",
    source=Stage.TREATMENT,
    target=Stage.FOLLOW_UP,
    default_magnitude=0.73,
    evidence_keys=("ct_arterial_enhancement", "ct_washout"),
)

TREATMENT_INFEASIBLE_TRANSPLANT = ConflictDefinition(
    label="treatment_infeasible_transplant",
    source=Stage.TREATMENT,
    target=Stage.FOLLOW_UP,
    default_magnitude=0.31,
    evidence_keys=("ct_capsule", "ct_lesion_count"),
)

TREATMENT_INFEASIBLE_ABLATION = ConflictDefinition(
    label="treatment_infeasible_ablation",
    source=Stage.TREATMENT,
    target=Stage.FOLLOW_UP,
    default_magnitude=0.38,
    evidence_keys=("ct_largest_lesion_mm", "mri_arterial_enhancement"),
)

TREATMENT_INFEASIBLE_TACE = ConflictDefinition(
    label="treatment_infeasible_tace",
    source=Stage.TREATMENT,
    target=Stage.FOLLOW_UP,
    default_magnitude=0.45,
    evidence_keys=("mri_washout", "lirads_category"),
)

TREATMENT_INFEASIBLE_SYSTEMIC = ConflictDefinition(
    label="treatment_infeasible_systemic",
    source=Stage.TREATMENT,
    target=Stage.FOLLOW_UP,
    default_magnitude=0.52,
    evidence_keys=("liver_volume_ml", "tumor_volume_ml"),
)

TUMOR_BURDEN_EXCEEDS_EARLY_STAGE = ConflictDefinition(
    label="tumor_burden_exceeds_early_stage",
    source=Stage.DIAGNOSIS,
    target=Stage.STAGING,
    default_magnitude=0.59,
    evidence_keys=("liver_dice", "tumor_dice"),
)

MULTIFOCAL_DISEASE_DETECTED = ConflictDefinition(
    label="multifocal_disease_detected",
    source=Stage.DIAGNOSIS,
    target=Stage.STAGING,
    default_magnitude=0.66,
    evidence_keys=("portal_vein_invasion", "extrahepatic_spread"),
)

VASCULAR_INVASION_STAGING_MISMATCH = ConflictDefinition(
    label="vascular_invasion_staging_mismatch",
    source=Stage.STAGING,
    target=Stage.STAGING,
    default_magnitude=0.73,
    evidence_keys=("ecog_status", "child_pugh_class"),
)

METASTATIC_DISEASE_STAGING_MISMATCH = ConflictDefinition(
    label="metastatic_disease_staging_mismatch",
    source=Stage.STAGING,
    target=Stage.STAGING,
    default_magnitude=0.31,
    evidence_keys=("child_pugh_score", "albumin_g_dl"),
)

LIRADS_DIAGNOSIS_MISMATCH = ConflictDefinition(
    label="lirads_diagnosis_mismatch",
    source=Stage.DIAGNOSIS,
    target=Stage.STAGING,
    default_magnitude=0.38,
    evidence_keys=("bilirubin_mg_dl", "inr"),
)

AFP_IMAGING_MISMATCH = ConflictDefinition(
    label="afp_imaging_mismatch",
    source=Stage.SCREENING,
    target=Stage.STAGING,
    default_magnitude=0.45,
    evidence_keys=("ascites_grade", "encephalopathy_grade"),
)

SEGMENTATION_VOLUME_MISMATCH = ConflictDefinition(
    label="segmentation_volume_mismatch",
    source=Stage.DIAGNOSIS,
    target=Stage.STAGING,
    default_magnitude=0.52,
    evidence_keys=("platelets_10e9_l", "bclc_stage"),
)

PERFORMANCE_STATUS_TREATMENT_MISMATCH = ConflictDefinition(
    label="performance_status_treatment_mismatch",
    source=Stage.STAGING,
    target=Stage.TREATMENT,
    default_magnitude=0.59,
    evidence_keys=("resectable", "transplant_eligible"),
)

HEPATIC_RESERVE_TREATMENT_MISMATCH = ConflictDefinition(
    label="hepatic_reserve_treatment_mismatch",
    source=Stage.STAGING,
    target=Stage.TREATMENT,
    default_magnitude=0.66,
    evidence_keys=("ablation_eligible", "tace_eligible"),
)

RECURRENCE_RISK_FOLLOWUP_MISMATCH = ConflictDefinition(
    label="recurrence_risk_followup_mismatch",
    source=Stage.TREATMENT,
    target=Stage.TREATMENT,
    default_magnitude=0.73,
    evidence_keys=("systemic_therapy_eligible", "best_supportive_care"),
)

SURVEILLANCE_INTERVAL_MISMATCH = ConflictDefinition(
    label="surveillance_interval_mismatch",
    source=Stage.FOLLOW_UP,
    target=Stage.TREATMENT,
    default_magnitude=0.31,
    evidence_keys=("treatment_class", "treatment_feasibility"),
)

PRIOR_TREATMENT_RESPONSE_MISMATCH = ConflictDefinition(
    label="prior_treatment_response_mismatch",
    source=Stage.TREATMENT,
    target=Stage.TREATMENT,
    default_magnitude=0.38,
    evidence_keys=("prior_resection", "prior_ablation"),
)

GENOMIC_RISK_STAGE_MISMATCH = ConflictDefinition(
    label="genomic_risk_stage_mismatch",
    source=Stage.STAGING,
    target=Stage.TREATMENT,
    default_magnitude=0.45,
    evidence_keys=("prior_tace", "prior_systemic_therapy"),
)

MISSING_REQUIRED_LABORATORY_PANEL = ConflictDefinition(
    label="missing_required_laboratory_panel",
    source=Stage.SCREENING,
    target=Stage.TREATMENT,
    default_magnitude=0.52,
    evidence_keys=("recurrence_risk_6m", "recurrence_risk_12m"),
)

MISSING_REQUIRED_IMAGING_PHASE = ConflictDefinition(
    label="missing_required_imaging_phase",
    source=Stage.DIAGNOSIS,
    target=Stage.TREATMENT,
    default_magnitude=0.59,
    evidence_keys=("recurrence_risk_24m", "follow_up_interval_months"),
)

GUIDELINE_TRANSITION_VIOLATION = ConflictDefinition(
    label="guideline_transition_violation",
    source=Stage.TREATMENT,
    target=Stage.TREATMENT,
    default_magnitude=0.66,
    evidence_keys=("follow_up_modality", "next_afp_date"),
)

CLINICAL_CONFLICTS: tuple[ConflictDefinition, ...] = (
    PORTAL_INVASION_DETECTED,
    EXTRAHEPATIC_SPREAD_DETECTED,
    ECOG_UPGRADED_TO_TWO,
    ECOG_UPGRADED_TO_THREE,
    HEPATIC_RESERVE_CHILD_PUGH_B,
    HEPATIC_RESERVE_CHILD_PUGH_C,
    TREATMENT_INFEASIBLE_RESECTION,
    TREATMENT_INFEASIBLE_TRANSPLANT,
    TREATMENT_INFEASIBLE_ABLATION,
    TREATMENT_INFEASIBLE_TACE,
    TREATMENT_INFEASIBLE_SYSTEMIC,
    TUMOR_BURDEN_EXCEEDS_EARLY_STAGE,
    MULTIFOCAL_DISEASE_DETECTED,
    VASCULAR_INVASION_STAGING_MISMATCH,
    METASTATIC_DISEASE_STAGING_MISMATCH,
    LIRADS_DIAGNOSIS_MISMATCH,
    AFP_IMAGING_MISMATCH,
    SEGMENTATION_VOLUME_MISMATCH,
    PERFORMANCE_STATUS_TREATMENT_MISMATCH,
    HEPATIC_RESERVE_TREATMENT_MISMATCH,
    RECURRENCE_RISK_FOLLOWUP_MISMATCH,
    SURVEILLANCE_INTERVAL_MISMATCH,
    PRIOR_TREATMENT_RESPONSE_MISMATCH,
    GENOMIC_RISK_STAGE_MISMATCH,
    MISSING_REQUIRED_LABORATORY_PANEL,
    MISSING_REQUIRED_IMAGING_PHASE,
    GUIDELINE_TRANSITION_VIOLATION,
)

CONFLICT_INDEX: Mapping[str, ConflictDefinition] = {item.label: item for item in CLINICAL_CONFLICTS}


def known_conflict(label: str) -> bool:
    return label in CONFLICT_INDEX


def conflict_for(label: str) -> ConflictDefinition:
    try:
        return CONFLICT_INDEX[label]
    except KeyError as error:
        raise ValueError(f"unknown clinical conflict: {label}") from error


def eligible_conflicts(values: Mapping[str, Any]) -> tuple[ConflictDefinition, ...]:
    return tuple(
        item for item in CLINICAL_CONFLICTS if all(key in values for key in item.evidence_keys)
    )
