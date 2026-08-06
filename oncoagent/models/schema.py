from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FieldSpec:
    name: str
    python_type: type[Any]
    group: str
    required: bool
    validator: Callable[[Any], bool]


def _any(value: Any) -> bool:
    return value is not None


def _probability(value: Any) -> bool:
    return isinstance(value, (int, float)) and 0.0 <= float(value) <= 1.0


def _nonnegative(value: Any) -> bool:
    return isinstance(value, (int, float)) and float(value) >= 0.0


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _boolean(value: Any) -> bool:
    return isinstance(value, bool)


def _integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


PATIENT_AGE = FieldSpec(
    name="patient_age",
    python_type=float,
    group="demographics",
    required=False,
    validator=_nonnegative,
)

PATIENT_SEX = FieldSpec(
    name="patient_sex",
    python_type=str,
    group="demographics",
    required=False,
    validator=_text,
)

RACE_ETHNICITY = FieldSpec(
    name="race_ethnicity",
    python_type=str,
    group="demographics",
    required=False,
    validator=_text,
)

ETIOLOGY = FieldSpec(
    name="etiology",
    python_type=str,
    group="demographics",
    required=False,
    validator=_text,
)

SURVEILLANCE_ELIGIBLE = FieldSpec(
    name="surveillance_eligible",
    python_type=bool,
    group="screening",
    required=False,
    validator=_boolean,
)

AFP_NG_ML = FieldSpec(
    name="afp_ng_ml",
    python_type=float,
    group="screening",
    required=False,
    validator=_nonnegative,
)

AFP_L3_PERCENT = FieldSpec(
    name="afp_l3_percent",
    python_type=float,
    group="screening",
    required=False,
    validator=_nonnegative,
)

DCP_MAU_ML = FieldSpec(
    name="dcp_mau_ml",
    python_type=float,
    group="screening",
    required=False,
    validator=_nonnegative,
)

ULTRASOUND_NODULE = FieldSpec(
    name="ultrasound_nodule",
    python_type=bool,
    group="screening",
    required=False,
    validator=_boolean,
)

ULTRASOUND_SIZE_MM = FieldSpec(
    name="ultrasound_size_mm",
    python_type=float,
    group="screening",
    required=False,
    validator=_nonnegative,
)

SCREENING_INTERVAL_MONTHS = FieldSpec(
    name="screening_interval_months",
    python_type=float,
    group="screening",
    required=False,
    validator=_nonnegative,
)

SCREENING_RISK_SCORE = FieldSpec(
    name="screening_risk_score",
    python_type=float,
    group="screening",
    required=False,
    validator=_probability,
)

CT_ARTERIAL_ENHANCEMENT = FieldSpec(
    name="ct_arterial_enhancement",
    python_type=bool,
    group="diagnosis",
    required=False,
    validator=_boolean,
)

CT_WASHOUT = FieldSpec(
    name="ct_washout",
    python_type=bool,
    group="diagnosis",
    required=False,
    validator=_boolean,
)

CT_CAPSULE = FieldSpec(
    name="ct_capsule",
    python_type=bool,
    group="diagnosis",
    required=False,
    validator=_boolean,
)

CT_LESION_COUNT = FieldSpec(
    name="ct_lesion_count",
    python_type=int,
    group="diagnosis",
    required=False,
    validator=_integer,
)

CT_LARGEST_LESION_MM = FieldSpec(
    name="ct_largest_lesion_mm",
    python_type=float,
    group="diagnosis",
    required=False,
    validator=_nonnegative,
)

MRI_ARTERIAL_ENHANCEMENT = FieldSpec(
    name="mri_arterial_enhancement",
    python_type=bool,
    group="diagnosis",
    required=False,
    validator=_boolean,
)

MRI_WASHOUT = FieldSpec(
    name="mri_washout",
    python_type=bool,
    group="diagnosis",
    required=False,
    validator=_boolean,
)

LIRADS_CATEGORY = FieldSpec(
    name="lirads_category",
    python_type=str,
    group="diagnosis",
    required=False,
    validator=_text,
)

LIVER_VOLUME_ML = FieldSpec(
    name="liver_volume_ml",
    python_type=float,
    group="diagnosis",
    required=False,
    validator=_nonnegative,
)

TUMOR_VOLUME_ML = FieldSpec(
    name="tumor_volume_ml",
    python_type=float,
    group="diagnosis",
    required=False,
    validator=_nonnegative,
)

LIVER_DICE = FieldSpec(
    name="liver_dice",
    python_type=float,
    group="diagnosis",
    required=False,
    validator=_probability,
)

TUMOR_DICE = FieldSpec(
    name="tumor_dice",
    python_type=float,
    group="diagnosis",
    required=False,
    validator=_probability,
)

PORTAL_VEIN_INVASION = FieldSpec(
    name="portal_vein_invasion",
    python_type=bool,
    group="staging",
    required=False,
    validator=_boolean,
)

EXTRAHEPATIC_SPREAD = FieldSpec(
    name="extrahepatic_spread",
    python_type=bool,
    group="staging",
    required=False,
    validator=_boolean,
)

ECOG_STATUS = FieldSpec(
    name="ecog_status",
    python_type=int,
    group="staging",
    required=False,
    validator=_integer,
)

CHILD_PUGH_CLASS = FieldSpec(
    name="child_pugh_class",
    python_type=str,
    group="staging",
    required=False,
    validator=_text,
)

CHILD_PUGH_SCORE = FieldSpec(
    name="child_pugh_score",
    python_type=int,
    group="staging",
    required=False,
    validator=_integer,
)

ALBUMIN_G_DL = FieldSpec(
    name="albumin_g_dl",
    python_type=float,
    group="staging",
    required=False,
    validator=_nonnegative,
)

BILIRUBIN_MG_DL = FieldSpec(
    name="bilirubin_mg_dl",
    python_type=float,
    group="staging",
    required=False,
    validator=_nonnegative,
)

INR = FieldSpec(
    name="inr",
    python_type=float,
    group="staging",
    required=False,
    validator=_nonnegative,
)

ASCITES_GRADE = FieldSpec(
    name="ascites_grade",
    python_type=str,
    group="staging",
    required=False,
    validator=_text,
)

ENCEPHALOPATHY_GRADE = FieldSpec(
    name="encephalopathy_grade",
    python_type=str,
    group="staging",
    required=False,
    validator=_text,
)

PLATELETS_10E9_L = FieldSpec(
    name="platelets_10e9_l",
    python_type=float,
    group="staging",
    required=False,
    validator=_nonnegative,
)

BCLC_STAGE = FieldSpec(
    name="bclc_stage",
    python_type=str,
    group="staging",
    required=False,
    validator=_text,
)

RESECTABLE = FieldSpec(
    name="resectable",
    python_type=bool,
    group="treatment",
    required=False,
    validator=_boolean,
)

TRANSPLANT_ELIGIBLE = FieldSpec(
    name="transplant_eligible",
    python_type=bool,
    group="treatment",
    required=False,
    validator=_boolean,
)

ABLATION_ELIGIBLE = FieldSpec(
    name="ablation_eligible",
    python_type=bool,
    group="treatment",
    required=False,
    validator=_boolean,
)

TACE_ELIGIBLE = FieldSpec(
    name="tace_eligible",
    python_type=bool,
    group="treatment",
    required=False,
    validator=_boolean,
)

SYSTEMIC_THERAPY_ELIGIBLE = FieldSpec(
    name="systemic_therapy_eligible",
    python_type=bool,
    group="treatment",
    required=False,
    validator=_boolean,
)

BEST_SUPPORTIVE_CARE = FieldSpec(
    name="best_supportive_care",
    python_type=bool,
    group="treatment",
    required=False,
    validator=_boolean,
)

TREATMENT_CLASS = FieldSpec(
    name="treatment_class",
    python_type=str,
    group="treatment",
    required=False,
    validator=_text,
)

TREATMENT_FEASIBILITY = FieldSpec(
    name="treatment_feasibility",
    python_type=float,
    group="treatment",
    required=False,
    validator=_probability,
)

PRIOR_RESECTION = FieldSpec(
    name="prior_resection",
    python_type=bool,
    group="treatment",
    required=False,
    validator=_boolean,
)

PRIOR_ABLATION = FieldSpec(
    name="prior_ablation",
    python_type=bool,
    group="treatment",
    required=False,
    validator=_boolean,
)

PRIOR_TACE = FieldSpec(
    name="prior_tace",
    python_type=bool,
    group="treatment",
    required=False,
    validator=_boolean,
)

PRIOR_SYSTEMIC_THERAPY = FieldSpec(
    name="prior_systemic_therapy",
    python_type=bool,
    group="treatment",
    required=False,
    validator=_boolean,
)

RECURRENCE_RISK_6M = FieldSpec(
    name="recurrence_risk_6m",
    python_type=float,
    group="follow_up",
    required=False,
    validator=_probability,
)

RECURRENCE_RISK_12M = FieldSpec(
    name="recurrence_risk_12m",
    python_type=float,
    group="follow_up",
    required=False,
    validator=_probability,
)

RECURRENCE_RISK_24M = FieldSpec(
    name="recurrence_risk_24m",
    python_type=float,
    group="follow_up",
    required=False,
    validator=_probability,
)

FOLLOW_UP_INTERVAL_MONTHS = FieldSpec(
    name="follow_up_interval_months",
    python_type=float,
    group="follow_up",
    required=False,
    validator=_nonnegative,
)

FOLLOW_UP_MODALITY = FieldSpec(
    name="follow_up_modality",
    python_type=str,
    group="follow_up",
    required=False,
    validator=_text,
)

NEXT_AFP_DATE = FieldSpec(
    name="next_afp_date",
    python_type=str,
    group="follow_up",
    required=False,
    validator=_text,
)

NEXT_IMAGING_DATE = FieldSpec(
    name="next_imaging_date",
    python_type=str,
    group="follow_up",
    required=False,
    validator=_text,
)

OVERALL_SURVIVAL_RISK = FieldSpec(
    name="overall_survival_risk",
    python_type=float,
    group="follow_up",
    required=False,
    validator=_probability,
)

GENOMIC_RISK_SCORE = FieldSpec(
    name="genomic_risk_score",
    python_type=float,
    group="genomics",
    required=False,
    validator=_probability,
)

TP53_STATUS = FieldSpec(
    name="tp53_status",
    python_type=str,
    group="genomics",
    required=False,
    validator=_text,
)

CTNNB1_STATUS = FieldSpec(
    name="ctnnb1_status",
    python_type=str,
    group="genomics",
    required=False,
    validator=_text,
)

TERT_STATUS = FieldSpec(
    name="tert_status",
    python_type=str,
    group="genomics",
    required=False,
    validator=_text,
)

MOLECULAR_SUBTYPE = FieldSpec(
    name="molecular_subtype",
    python_type=str,
    group="genomics",
    required=False,
    validator=_text,
)

CALIBRATED_CONFIDENCE = FieldSpec(
    name="calibrated_confidence",
    python_type=float,
    group="coordination",
    required=False,
    validator=_probability,
)

UNCERTAINTY_FLAG = FieldSpec(
    name="uncertainty_flag",
    python_type=float,
    group="coordination",
    required=False,
    validator=_probability,
)

HUMAN_REVIEW_REQUIRED = FieldSpec(
    name="human_review_required",
    python_type=bool,
    group="coordination",
    required=False,
    validator=_boolean,
)

ACC_FIELDS: tuple[FieldSpec, ...] = (
    PATIENT_AGE,
    PATIENT_SEX,
    RACE_ETHNICITY,
    ETIOLOGY,
    SURVEILLANCE_ELIGIBLE,
    AFP_NG_ML,
    AFP_L3_PERCENT,
    DCP_MAU_ML,
    ULTRASOUND_NODULE,
    ULTRASOUND_SIZE_MM,
    SCREENING_INTERVAL_MONTHS,
    SCREENING_RISK_SCORE,
    CT_ARTERIAL_ENHANCEMENT,
    CT_WASHOUT,
    CT_CAPSULE,
    CT_LESION_COUNT,
    CT_LARGEST_LESION_MM,
    MRI_ARTERIAL_ENHANCEMENT,
    MRI_WASHOUT,
    LIRADS_CATEGORY,
    LIVER_VOLUME_ML,
    TUMOR_VOLUME_ML,
    LIVER_DICE,
    TUMOR_DICE,
    PORTAL_VEIN_INVASION,
    EXTRAHEPATIC_SPREAD,
    ECOG_STATUS,
    CHILD_PUGH_CLASS,
    CHILD_PUGH_SCORE,
    ALBUMIN_G_DL,
    BILIRUBIN_MG_DL,
    INR,
    ASCITES_GRADE,
    ENCEPHALOPATHY_GRADE,
    PLATELETS_10E9_L,
    BCLC_STAGE,
    RESECTABLE,
    TRANSPLANT_ELIGIBLE,
    ABLATION_ELIGIBLE,
    TACE_ELIGIBLE,
    SYSTEMIC_THERAPY_ELIGIBLE,
    BEST_SUPPORTIVE_CARE,
    TREATMENT_CLASS,
    TREATMENT_FEASIBILITY,
    PRIOR_RESECTION,
    PRIOR_ABLATION,
    PRIOR_TACE,
    PRIOR_SYSTEMIC_THERAPY,
    RECURRENCE_RISK_6M,
    RECURRENCE_RISK_12M,
    RECURRENCE_RISK_24M,
    FOLLOW_UP_INTERVAL_MONTHS,
    FOLLOW_UP_MODALITY,
    NEXT_AFP_DATE,
    NEXT_IMAGING_DATE,
    OVERALL_SURVIVAL_RISK,
    GENOMIC_RISK_SCORE,
    TP53_STATUS,
    CTNNB1_STATUS,
    TERT_STATUS,
    MOLECULAR_SUBTYPE,
    CALIBRATED_CONFIDENCE,
    UNCERTAINTY_FLAG,
    HUMAN_REVIEW_REQUIRED,
)

FIELD_INDEX: Mapping[str, FieldSpec] = {field.name: field for field in ACC_FIELDS}


def validate_field(name: str, value: Any) -> bool:
    spec = FIELD_INDEX.get(name)
    return spec is not None and spec.validator(value)


def validate_context(values: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(name for name, value in values.items() if not validate_field(name, value))


def fields_for_group(group: str) -> tuple[FieldSpec, ...]:
    return tuple(field for field in ACC_FIELDS if field.group == group)


def empty_context() -> dict[str, Any]:
    return {field.name: None for field in ACC_FIELDS}
