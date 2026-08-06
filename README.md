# OncoAgent

OncoAgent coordinates screening, diagnosis, staging, treatment selection, and follow-up for hepatocellular carcinoma through a guideline-anchored pathway state machine. The package contains the accumulated clinical context, bidirectional temporal feedback, verification gates, stage-adaptive modality routing, dataset harmonization, and statistical evaluation described in the manuscript.

## Scope

The implementation covers the computational methods that are specified in the manuscript:

- Five ordered clinical stages
- A 64-field typed accumulated clinical context
- Versioned context writes and rollback
- Five stage-specific modality budgets
- Four verification criteria
- Per-stage calibrated confidence thresholds
- A 27-label clinical conflict schema
- A normalized feedback trigger of 0.30
- Three feedback iterations
- A cooling parameter of 0.10
- BCLC-oriented staging and treatment guards
- Stratified bootstrap evaluation with 10,000 resamples
- Bonferroni adjustment across six primary metrics
- Per-site, subgroup, MCID, calibration, segmentation, and survival metrics

The manuscript does not report a trainable backbone specification, batch size, optimizer, learning rate, epoch count, scheduler, precision mode, weight decay, warmup schedule, gradient clipping, or EMA settings. These values are therefore not assigned synthetic defaults. The configuration records them as unreported.

The reported cross-backbone comparison names externally hosted language-model families but does not specify API revisions, request schemas, prompts, credentials, or deterministic decoding infrastructure. This package does not make external model calls.

## Architecture

The runtime follows this sequence:

1. The router selects available modalities within the budget for the active care stage.
2. The stage agent emits a prediction, calibrated distribution, uncertainty value, and typed findings.
3. The findings are checked for completeness, consistency, guideline agreement, and confidence.
4. A passing output is appended to the versioned clinical context.
5. A failing output requests another modality, invokes feedback, or escalates for human review.
6. After the forward pathway, downstream conflicts are traversed in reverse stage order.
7. Accepted revisions replace the affected context version and re-execute dependent stages.
8. Execution stops after convergence or three feedback iterations.

The stage order is screening, diagnosis, staging, treatment, and follow-up. Outputs are advisory and require clinical oversight.

## Installation

Python 3.11 is the supported interpreter.

### pip

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

### conda

```bash
conda env create -f environment.yml
conda activate oncoagent
python -m pip install -e .
```

### Docker

```bash
docker build -t oncoagent .
docker run --rm -v "$PWD/examples:/workspace/examples" oncoagent validate examples/case.json
```

The Docker image uses a CPU Python base because the manuscript does not provide a trainable local neural backbone whose CUDA runtime could be pinned faithfully.

## Data

Verified dataset landing pages are kept in `dataset_links.txt` and nowhere else in the repository.

### LiTS

The manuscript identifies the 2017 Liver Tumor Segmentation Challenge release and reports 131 CT cases. The legacy CodaLab competition address did not respond during release validation and is omitted from the verified link list. Automated acquisition is disabled. Users must obtain the release through an authorized current distributor, accept its terms, and place the acquired volumes in their own data directory.

Expected inputs include CT volumes and liver and lesion labels. The harmonizer consumes derived case records containing lesion count, maximum lesion diameter, enhancement features, liver volume, and tumor volume.

### TCGA-LIHC

The manuscript specifies GDC Data Release 40.0 and 377 cases. Access is through the Genomic Data Commons project portal. Data use is governed by GDC terms and any controlled-access conditions attached to selected files.

Expected inputs include molecular features, clinical fields, survival time, event status, stage annotations, and treatment annotations.

### MIMIC-IV

The manuscript specifies MIMIC-IV v3.1 and an approximately 350-case derived HCC cohort. Access requires a PhysioNet credential, required training, and acceptance of the credentialed health-data license. Derived data must remain subject to the source agreement.

Expected inputs include deidentified demographics, diagnoses, laboratory events, procedures, medication records, and longitudinal follow-up fields. No patient rows are distributed with this package.

### 3D-IRCADb-01

The manuscript specifies the 20-case release as an exploratory imaging consistency set. Access is through the IRCAD registration page and is governed by its displayed research-use terms.

Expected inputs include CT volumes and organ and lesion labels.

## Dataset preparation

A source record is converted into a `PatientBundle` with modality-specific dictionaries.

```python
from oncoagent.data.harmonize import harmonize_lits

bundle = harmonize_lits(
    {
        "case_id": "local-case",
        "arterial_enhancement": True,
        "washout": True,
        "capsule": True,
        "lesion_count": 1,
        "largest_lesion_mm": 18.0,
        "liver_volume_ml": 1400.0,
        "tumor_volume_ml": 12.0,
    }
)
```

Manifest generation calculates SHA-256 for each local source file. The output manifest contains only case identifiers, dataset names, relative paths, hashes, and byte sizes.

```python
from pathlib import Path
from oncoagent.data.harmonize import build_manifest, write_manifest

records = build_manifest(Path("data/lits"), "LiTS")
write_manifest(records, Path("data/lits-manifest.csv"))
```

No absolute source path is written to a manifest.

## Input format

The command line accepts one JSON object. Each modality key must be one of `imaging`, `genomics`, `ehr`, `laboratory`, or `clinical_note`.

```json
{
  "case_id": "local-case",
  "modalities": {
    "imaging": {
      "ct_arterial_enhancement": true,
      "ct_washout": true,
      "ct_capsule": true,
      "ct_lesion_count": 1,
      "ct_largest_lesion_mm": 18.0,
      "liver_volume_ml": 1400.0,
      "tumor_volume_ml": 12.0
    },
    "laboratory": {
      "afp_ng_ml": 42.0,
      "albumin_g_dl": 4.1,
      "bilirubin_mg_dl": 0.8,
      "inr": 1.0,
      "platelets_10e9_l": 170.0
    },
    "ehr": {
      "patient_age": 62.0,
      "patient_sex": "female",
      "etiology": "HBV",
      "cirrhosis": true,
      "viral_hepatitis": true,
      "portal_vein_invasion": false,
      "extrahepatic_spread": false,
      "ecog_status": 0,
      "child_pugh_class": "A",
      "resectable": true,
      "treatment_feasibility": 0.92
    }
  }
}
```

Validate input without running the pathway:

```bash
oncoagent validate case.json
```

Run the coordinated pathway and write an atomic JSON result:

```bash
oncoagent run case.json --output result.json
```

A completed pathway returns exit code zero. Human escalation returns exit code two.

## Configuration

`configs/main.yaml` records only values stated in the manuscript. The modality budgets are 1.0, 1.5, 3.0, 3.0, and 1.5 for screening through follow-up. Verification thresholds are 0.95 for completeness, 0.90 for consistency, and 1.0 for guideline agreement. Stage confidence thresholds are calibrated within the reported 0.62 to 0.78 interval.

The feedback trigger is 0.30. The depth cap is three. The cooling parameter is 0.10. Statistical evaluation uses seeds 1, 2, and 3 and 10,000 stratified bootstrap resamples.

## Evaluation

The result registry records values reported in the manuscript, including the main six metrics, composite accuracy, ablations, cross-site results, BCLC subgroup results, modality ablations, missing-modality results, perturbation analysis, and temporal stability.

```python
from oncoagent.evaluation.reported import reported_result

main = reported_result("main", "composite")
assert main.value == 0.781
assert main.lower == 0.760
assert main.upper == 0.802
```

The evaluator supports the six-metric weighted composite. The manuscript states that weights were fixed in a pre-analysis plan but does not disclose their numeric values. The library default is an explicit analysis convenience and must not be presented as the manuscript composite without an externally supplied weight vector.

Available metric functions include:

- Accuracy, sensitivity, specificity, precision, negative predictive value, and F1
- Balanced accuracy and multiclass macro F1
- ROC AUC and Brier score
- Expected calibration error and log loss
- Dice and Jaccard overlap
- Harrell-style concordance index
- Cohen kappa, Cohen d, and Cohen h
- Wilson score intervals
- Stratified bootstrap intervals and paired tests
- Bonferroni adjustment
- Per-case MCID crossing rates
- Maximum inter-site range

The stratification keys for the composite analysis are site, BCLC stage, and etiology. Single-stage analysis can use site-only strata.

## Reported compute profile

The manuscript reports inference on one NVIDIA A100 80 GB GPU:

- Mean end-to-end latency: 42.7 seconds per case
- Peak accelerator memory: 31.2 GB
- Single-device throughput: 84 cases per hour
- Two-device segmentation throughput: 132 cases per hour
- Screening: 4.1 seconds
- Diagnosis: 18.9 seconds
- Staging: 6.3 seconds
- Treatment: 8.4 seconds
- Follow-up: 3.1 seconds
- Verification overhead: 1.9 seconds
- Feedback trigger rate: 38.7 percent
- Median triggered-case overhead: 3.5 seconds

Training hardware, training wall-clock, storage footprint, parameter initialization, and optimization schedule are not reported.

## Quality checks

Run the regression suite:

```bash
pytest -q
```

Run static analysis:

```bash
ruff check .
mypy --strict oncoagent
```

The test suite covers schema invariants, stage agents, guideline routing, context rollback, modality budgets, feedback detection, calibration monotonicity, classification metrics, segmentation metrics, survival concordance, statistical intervals, data harmonization, perturbations, result registration, and gate behavior.

## Clinical safeguards

The software produces advisory recommendations. It does not execute treatment, alter an electronic health record, contact a patient, schedule a procedure, or replace review by qualified clinicians.

MIMIC-IV records and all derived cohorts remain governed by the PhysioNet agreement. Users must not place protected or identifiable health information in examples, logs, fixtures, issue reports, manifests, or committed artifacts.

The manuscript describes retrospective computational evidence. The package does not claim prospective validation, real-world workflow integration, clinical efficacy, or regulatory authorization.

## Limitations

Several manuscript sections contain headings without implementation details. In particular, the architecture and implementation sections omit the trainable model definitions needed to regenerate neural weights. The primary comparison also uses literature-calibrated anchor-delta projections for some values. These constraints limit exact regeneration of numerical results from raw data.

The BCLC rules included here cover the determinants and treatment classes explicitly used by the pathway. Clinical deployment requires validation against the complete licensed guideline text, local policy, formulary, transplant criteria, and multidisciplinary review.

The four public datasets support different stage-native labels. They do not form a naturally linked longitudinal cohort spanning all five stages. Harmonized cross-dataset evaluation must preserve this distinction.

## License

The software is distributed under the MIT License. Dataset licenses and access agreements remain independent and may be more restrictive.
