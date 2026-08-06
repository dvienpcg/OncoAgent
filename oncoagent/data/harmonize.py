from __future__ import annotations

import csv
import hashlib
import json
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from oncoagent.models.types import Modality, PatientBundle


@dataclass(frozen=True)
class ManifestRecord:
    case_id: str
    dataset: str
    relative_path: str
    sha256: str
    size_bytes: int


@dataclass(frozen=True)
class DatasetDescriptor:
    name: str
    version: str
    access: str
    restricted: bool
    modalities: tuple[Modality, ...]


DATASETS = (
    DatasetDescriptor("LiTS", "2017", "challenge registration", False, (Modality.IMAGING,)),
    DatasetDescriptor(
        "TCGA-LIHC", "GDC Data Release 40.0", "GDC portal", False, (Modality.GENOMICS, Modality.EHR)
    ),
    DatasetDescriptor(
        "MIMIC-IV",
        "3.1",
        "PhysioNet credentialed access",
        True,
        (Modality.EHR, Modality.LABORATORY),
    ),
    DatasetDescriptor("3D-IRCADb-01", "1.0", "IRCAD registration", False, (Modality.IMAGING,)),
)


def file_sha256(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(chunk_size):
            digest.update(block)
    return digest.hexdigest()


def build_manifest(root: Path, dataset: str) -> tuple[ManifestRecord, ...]:
    records: list[ManifestRecord] = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        case_id = path.stem
        records.append(
            ManifestRecord(
                case_id=case_id,
                dataset=dataset,
                relative_path=relative,
                sha256=file_sha256(path),
                size_bytes=path.stat().st_size,
            )
        )
    return tuple(records)


def write_manifest(records: Iterable[ManifestRecord], path: Path) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=("case_id", "dataset", "relative_path", "sha256", "size_bytes"),
        )
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "case_id": record.case_id,
                    "dataset": record.dataset,
                    "relative_path": record.relative_path,
                    "sha256": record.sha256,
                    "size_bytes": record.size_bytes,
                }
            )
    temporary.replace(path)


def read_json(path: Path) -> Mapping[str, Any]:
    with path.open(encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError("expected JSON object")
    return value


def iter_csv(path: Path) -> Iterator[Mapping[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        yield from csv.DictReader(stream)


def harmonize_lits(record: Mapping[str, Any]) -> PatientBundle:
    imaging = {
        "ct_arterial_enhancement": bool(record.get("arterial_enhancement", False)),
        "ct_washout": bool(record.get("washout", False)),
        "ct_capsule": bool(record.get("capsule", False)),
        "ct_lesion_count": int(record.get("lesion_count", 0)),
        "ct_largest_lesion_mm": float(record.get("largest_lesion_mm", 0.0)),
        "liver_volume_ml": float(record.get("liver_volume_ml", 0.0)),
        "tumor_volume_ml": float(record.get("tumor_volume_ml", 0.0)),
    }
    return PatientBundle(str(record["case_id"]), {Modality.IMAGING: imaging}, {"site": "LiTS"})


def harmonize_tcga(record: Mapping[str, Any]) -> PatientBundle:
    genomics = {
        "genomic_risk_score": float(record.get("genomic_risk_score", 0.5)),
        "tp53_status": str(record.get("tp53_status", "unknown")),
        "ctnnb1_status": str(record.get("ctnnb1_status", "unknown")),
        "tert_status": str(record.get("tert_status", "unknown")),
        "molecular_subtype": str(record.get("molecular_subtype", "unknown")),
    }
    clinical = {
        "patient_age": float(record.get("age", 60.0)),
        "patient_sex": str(record.get("sex", "unknown")),
        "race_ethnicity": str(record.get("race_ethnicity", "not_reported")),
        "etiology": str(record.get("etiology", "unknown")),
        "ecog_status": int(record.get("ecog_status", 0)),
        "child_pugh_class": str(record.get("child_pugh_class", "A")),
    }
    return PatientBundle(
        str(record["case_id"]),
        {Modality.GENOMICS: genomics, Modality.EHR: clinical},
        {"site": "TCGA-LIHC"},
    )


def harmonize_mimic(record: Mapping[str, Any]) -> PatientBundle:
    laboratory = {
        "afp_ng_ml": float(record.get("afp_ng_ml", 5.0)),
        "albumin_g_dl": float(record.get("albumin_g_dl", 4.0)),
        "bilirubin_mg_dl": float(record.get("bilirubin_mg_dl", 1.0)),
        "inr": float(record.get("inr", 1.0)),
        "platelets_10e9_l": float(record.get("platelets_10e9_l", 180.0)),
    }
    clinical = {
        "patient_age": float(record.get("age", 60.0)),
        "patient_sex": str(record.get("sex", "unknown")),
        "etiology": str(record.get("etiology", "unknown")),
        "ecog_status": int(record.get("ecog_status", 0)),
        "child_pugh_class": str(record.get("child_pugh_class", "A")),
        "cirrhosis": bool(record.get("cirrhosis", False)),
        "viral_hepatitis": bool(record.get("viral_hepatitis", False)),
    }
    return PatientBundle(
        str(record["case_id"]),
        {Modality.LABORATORY: laboratory, Modality.EHR: clinical},
        {"site": "MIMIC-IV"},
    )


def harmonize_ircad(record: Mapping[str, Any]) -> PatientBundle:
    bundle = harmonize_lits(record)
    return PatientBundle(bundle.case_id, bundle.modalities, {"site": "3D-IRCADb-01"})


def descriptor(name: str) -> DatasetDescriptor:
    for item in DATASETS:
        if item.name == name:
            return item
    raise KeyError(name)
