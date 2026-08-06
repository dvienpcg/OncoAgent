from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class ReportedResult:
    experiment: str
    metric: str
    value: float
    lower: float | None
    upper: float | None
    source: str


RESULT_001 = ReportedResult(
    experiment="main",
    metric="screening_auc",
    value=0.912,
    lower=0.891,
    upper=0.933,
    source="Table 1",
)

RESULT_002 = ReportedResult(
    experiment="main",
    metric="liver_dice",
    value=0.962,
    lower=0.954,
    upper=0.970,
    source="Table 1",
)

RESULT_003 = ReportedResult(
    experiment="main",
    metric="tumor_dice",
    value=0.788,
    lower=0.746,
    upper=0.830,
    source="Table 1",
)

RESULT_004 = ReportedResult(
    experiment="main",
    metric="staging_concordance",
    value=0.867,
    lower=0.844,
    upper=0.890,
    source="Table 1",
)

RESULT_005 = ReportedResult(
    experiment="main",
    metric="treatment_concordance",
    value=0.843,
    lower=0.817,
    upper=0.869,
    source="Table 1",
)

RESULT_006 = ReportedResult(
    experiment="main",
    metric="survival_c_index",
    value=0.763,
    lower=0.741,
    upper=0.785,
    source="Table 1",
)

RESULT_007 = ReportedResult(
    experiment="main",
    metric="composite",
    value=0.781,
    lower=0.760,
    upper=0.802,
    source="Table 1",
)

RESULT_008 = ReportedResult(
    experiment="without_acc",
    metric="composite",
    value=0.719,
    lower=0.696,
    upper=0.742,
    source="Table 2",
)

RESULT_009 = ReportedResult(
    experiment="without_btf",
    metric="composite",
    value=0.752,
    lower=None,
    upper=None,
    source="Table 2",
)

RESULT_010 = ReportedResult(
    experiment="without_vgn",
    metric="composite",
    value=0.747,
    lower=None,
    upper=None,
    source="Table 2",
)

RESULT_011 = ReportedResult(
    experiment="without_samr",
    metric="composite",
    value=0.733,
    lower=None,
    upper=None,
    source="Table 2",
)

RESULT_012 = ReportedResult(
    experiment="without_acc_btf",
    metric="composite",
    value=0.679,
    lower=None,
    upper=None,
    source="Table 2",
)

RESULT_013 = ReportedResult(
    experiment="gapsm_only",
    metric="composite",
    value=0.682,
    lower=None,
    upper=None,
    source="Table 2",
)

RESULT_014 = ReportedResult(
    experiment="lits",
    metric="liver_dice",
    value=0.963,
    lower=0.954,
    upper=0.972,
    source="Table 4",
)

RESULT_015 = ReportedResult(
    experiment="lits",
    metric="tumor_dice",
    value=0.791,
    lower=0.746,
    upper=0.836,
    source="Table 4",
)

RESULT_016 = ReportedResult(
    experiment="lits",
    metric="staging_concordance",
    value=0.872,
    lower=0.842,
    upper=0.902,
    source="Table 4",
)

RESULT_017 = ReportedResult(
    experiment="lits",
    metric="treatment_concordance",
    value=0.838,
    lower=0.803,
    upper=0.873,
    source="Table 4",
)

RESULT_018 = ReportedResult(
    experiment="lits",
    metric="composite",
    value=0.779,
    lower=0.747,
    upper=0.811,
    source="Table 4",
)

RESULT_019 = ReportedResult(
    experiment="tcga_lihc",
    metric="staging_concordance",
    value=0.873,
    lower=0.847,
    upper=0.899,
    source="Table 4",
)

RESULT_020 = ReportedResult(
    experiment="tcga_lihc",
    metric="treatment_concordance",
    value=0.851,
    lower=0.821,
    upper=0.881,
    source="Table 4",
)

RESULT_021 = ReportedResult(
    experiment="tcga_lihc",
    metric="survival_c_index",
    value=0.771,
    lower=0.747,
    upper=0.795,
    source="Table 4",
)

RESULT_022 = ReportedResult(
    experiment="tcga_lihc",
    metric="composite",
    value=0.788,
    lower=0.759,
    upper=0.817,
    source="Table 4",
)

RESULT_023 = ReportedResult(
    experiment="ircadb",
    metric="liver_dice",
    value=0.958,
    lower=0.939,
    upper=0.977,
    source="Table 4",
)

RESULT_024 = ReportedResult(
    experiment="ircadb",
    metric="tumor_dice",
    value=0.771,
    lower=0.710,
    upper=0.832,
    source="Table 4",
)

RESULT_025 = ReportedResult(
    experiment="ircadb",
    metric="staging_concordance",
    value=0.860,
    lower=0.804,
    upper=0.916,
    source="Table 4",
)

RESULT_026 = ReportedResult(
    experiment="ircadb",
    metric="treatment_concordance",
    value=0.828,
    lower=0.764,
    upper=0.892,
    source="Table 4",
)

RESULT_027 = ReportedResult(
    experiment="ircadb",
    metric="composite",
    value=0.776,
    lower=0.711,
    upper=0.841,
    source="Table 4",
)

RESULT_028 = ReportedResult(
    experiment="mimic_iv",
    metric="staging_concordance",
    value=0.854,
    lower=0.820,
    upper=0.888,
    source="Table 4",
)

RESULT_029 = ReportedResult(
    experiment="mimic_iv",
    metric="treatment_concordance",
    value=0.835,
    lower=0.800,
    upper=0.870,
    source="Table 4",
)

RESULT_030 = ReportedResult(
    experiment="mimic_iv",
    metric="survival_c_index",
    value=0.751,
    lower=0.720,
    upper=0.782,
    source="Table 4",
)

RESULT_031 = ReportedResult(
    experiment="mimic_iv",
    metric="composite",
    value=0.776,
    lower=0.746,
    upper=0.806,
    source="Table 4",
)

RESULT_032 = ReportedResult(
    experiment="claude_opus_4_6",
    metric="composite",
    value=0.781,
    lower=None,
    upper=None,
    source="Table 4",
)

RESULT_033 = ReportedResult(
    experiment="gpt_5",
    metric="composite",
    value=0.778,
    lower=None,
    upper=None,
    source="Table 4",
)

RESULT_034 = ReportedResult(
    experiment="llama_4_70b",
    metric="composite",
    value=0.774,
    lower=None,
    upper=None,
    source="Table 5",
)

RESULT_035 = ReportedResult(
    experiment="imaging_only",
    metric="composite",
    value=0.711,
    lower=None,
    upper=None,
    source="Table 5",
)

RESULT_036 = ReportedResult(
    experiment="genomics_only",
    metric="composite",
    value=0.684,
    lower=None,
    upper=None,
    source="Table 5",
)

RESULT_037 = ReportedResult(
    experiment="ehr_only",
    metric="composite",
    value=0.691,
    lower=None,
    upper=None,
    source="Table 24",
)

RESULT_038 = ReportedResult(
    experiment="imaging_genomics",
    metric="composite",
    value=0.742,
    lower=None,
    upper=None,
    source="Table 24",
)

RESULT_039 = ReportedResult(
    experiment="imaging_ehr",
    metric="composite",
    value=0.751,
    lower=None,
    upper=None,
    source="Table 24",
)

RESULT_040 = ReportedResult(
    experiment="genomics_ehr",
    metric="composite",
    value=0.724,
    lower=None,
    upper=None,
    source="Table 24",
)

RESULT_041 = ReportedResult(
    experiment="no_genomics",
    metric="composite",
    value=0.748,
    lower=0.724,
    upper=0.772,
    source="Table 24",
)

RESULT_042 = ReportedResult(
    experiment="no_ehr",
    metric="composite",
    value=0.739,
    lower=0.715,
    upper=0.763,
    source="Table 24",
)

RESULT_043 = ReportedResult(
    experiment="no_imaging",
    metric="composite",
    value=0.688,
    lower=0.660,
    upper=0.716,
    source="Table 26",
)

RESULT_044 = ReportedResult(
    experiment="no_omics_no_ehr",
    metric="composite",
    value=0.702,
    lower=0.676,
    upper=0.728,
    source="Table 26",
)

RESULT_045 = ReportedResult(
    experiment="ct_noise",
    metric="composite",
    value=0.768,
    lower=None,
    upper=None,
    source="Table 26",
)

RESULT_046 = ReportedResult(
    experiment="lab_masking",
    metric="composite",
    value=0.761,
    lower=None,
    upper=None,
    source="Table 26",
)

RESULT_047 = ReportedResult(
    experiment="omics_dropout",
    metric="composite",
    value=0.763,
    lower=None,
    upper=None,
    source="Table 27",
)

RESULT_048 = ReportedResult(
    experiment="ocr_noise",
    metric="composite",
    value=0.776,
    lower=None,
    upper=None,
    source="Table 27",
)

RESULT_049 = ReportedResult(
    experiment="ct_lab_noise",
    metric="composite",
    value=0.744,
    lower=None,
    upper=None,
    source="Table 27",
)

RESULT_050 = ReportedResult(
    experiment="year_2020",
    metric="composite",
    value=0.781,
    lower=0.724,
    upper=0.838,
    source="Table 27",
)

RESULT_051 = ReportedResult(
    experiment="year_2021",
    metric="composite",
    value=0.775,
    lower=0.718,
    upper=0.832,
    source="Table 27",
)

RESULT_052 = ReportedResult(
    experiment="year_2022",
    metric="composite",
    value=0.773,
    lower=0.714,
    upper=0.832,
    source="Table 28",
)

RESULT_053 = ReportedResult(
    experiment="bclc_0",
    metric="screening_auc",
    value=0.934,
    lower=None,
    upper=None,
    source="Table 28",
)

RESULT_054 = ReportedResult(
    experiment="bclc_A",
    metric="screening_auc",
    value=0.921,
    lower=None,
    upper=None,
    source="Table 28",
)

RESULT_055 = ReportedResult(
    experiment="bclc_B",
    metric="screening_auc",
    value=0.908,
    lower=None,
    upper=None,
    source="Table 3",
)

RESULT_056 = ReportedResult(
    experiment="bclc_C",
    metric="screening_auc",
    value=0.895,
    lower=None,
    upper=None,
    source="Table 3",
)

RESULT_057 = ReportedResult(
    experiment="bclc_D",
    metric="screening_auc",
    value=0.883,
    lower=None,
    upper=None,
    source="Table 3",
)

RESULT_058 = ReportedResult(
    experiment="bclc_0",
    metric="staging_concordance",
    value=0.922,
    lower=None,
    upper=None,
    source="Table 3",
)

RESULT_059 = ReportedResult(
    experiment="bclc_A",
    metric="staging_concordance",
    value=0.897,
    lower=None,
    upper=None,
    source="Table 3",
)

RESULT_060 = ReportedResult(
    experiment="bclc_B",
    metric="staging_concordance",
    value=0.841,
    lower=None,
    upper=None,
    source="Table 3",
)

RESULT_061 = ReportedResult(
    experiment="bclc_C",
    metric="staging_concordance",
    value=0.839,
    lower=None,
    upper=None,
    source="Table 3",
)

RESULT_062 = ReportedResult(
    experiment="bclc_D",
    metric="staging_concordance",
    value=0.890,
    lower=None,
    upper=None,
    source="Table 3",
)

RESULT_063 = ReportedResult(
    experiment="bclc_0",
    metric="treatment_concordance",
    value=0.891,
    lower=None,
    upper=None,
    source="Table 3",
)

RESULT_064 = ReportedResult(
    experiment="bclc_A",
    metric="treatment_concordance",
    value=0.872,
    lower=None,
    upper=None,
    source="Table 3",
)

RESULT_065 = ReportedResult(
    experiment="bclc_B",
    metric="treatment_concordance",
    value=0.820,
    lower=None,
    upper=None,
    source="Table 3",
)

RESULT_066 = ReportedResult(
    experiment="bclc_C",
    metric="treatment_concordance",
    value=0.808,
    lower=None,
    upper=None,
    source="Table 3",
)

RESULT_067 = ReportedResult(
    experiment="bclc_D",
    metric="treatment_concordance",
    value=0.862,
    lower=None,
    upper=None,
    source="Table 3",
)

RESULT_068 = ReportedResult(
    experiment="bclc_0",
    metric="survival_c_index",
    value=0.783,
    lower=None,
    upper=None,
    source="Table 3",
)

RESULT_069 = ReportedResult(
    experiment="bclc_A",
    metric="survival_c_index",
    value=0.771,
    lower=None,
    upper=None,
    source="Table 3",
)

RESULT_070 = ReportedResult(
    experiment="bclc_B",
    metric="survival_c_index",
    value=0.756,
    lower=None,
    upper=None,
    source="Table 3",
)

RESULT_071 = ReportedResult(
    experiment="bclc_C",
    metric="survival_c_index",
    value=0.749,
    lower=None,
    upper=None,
    source="Table 3",
)

RESULT_072 = ReportedResult(
    experiment="bclc_D",
    metric="survival_c_index",
    value=0.740,
    lower=None,
    upper=None,
    source="Table 3",
)

REPORTED_RESULTS: tuple[ReportedResult, ...] = (
    RESULT_001,
    RESULT_002,
    RESULT_003,
    RESULT_004,
    RESULT_005,
    RESULT_006,
    RESULT_007,
    RESULT_008,
    RESULT_009,
    RESULT_010,
    RESULT_011,
    RESULT_012,
    RESULT_013,
    RESULT_014,
    RESULT_015,
    RESULT_016,
    RESULT_017,
    RESULT_018,
    RESULT_019,
    RESULT_020,
    RESULT_021,
    RESULT_022,
    RESULT_023,
    RESULT_024,
    RESULT_025,
    RESULT_026,
    RESULT_027,
    RESULT_028,
    RESULT_029,
    RESULT_030,
    RESULT_031,
    RESULT_032,
    RESULT_033,
    RESULT_034,
    RESULT_035,
    RESULT_036,
    RESULT_037,
    RESULT_038,
    RESULT_039,
    RESULT_040,
    RESULT_041,
    RESULT_042,
    RESULT_043,
    RESULT_044,
    RESULT_045,
    RESULT_046,
    RESULT_047,
    RESULT_048,
    RESULT_049,
    RESULT_050,
    RESULT_051,
    RESULT_052,
    RESULT_053,
    RESULT_054,
    RESULT_055,
    RESULT_056,
    RESULT_057,
    RESULT_058,
    RESULT_059,
    RESULT_060,
    RESULT_061,
    RESULT_062,
    RESULT_063,
    RESULT_064,
    RESULT_065,
    RESULT_066,
    RESULT_067,
    RESULT_068,
    RESULT_069,
    RESULT_070,
    RESULT_071,
    RESULT_072,
)

RESULT_INDEX: Mapping[tuple[str, str], ReportedResult] = {
    (result.experiment, result.metric): result for result in REPORTED_RESULTS
}


def reported_result(experiment: str, metric: str) -> ReportedResult:
    try:
        return RESULT_INDEX[(experiment, metric)]
    except KeyError as error:
        raise ValueError(f"unreported result: {experiment}/{metric}") from error


def results_for_experiment(experiment: str) -> tuple[ReportedResult, ...]:
    return tuple(result for result in REPORTED_RESULTS if result.experiment == experiment)


def results_for_metric(metric: str) -> tuple[ReportedResult, ...]:
    return tuple(result for result in REPORTED_RESULTS if result.metric == metric)
