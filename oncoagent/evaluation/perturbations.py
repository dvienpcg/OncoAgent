from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class PerturbationResult:
    values: Mapping[str, Any]
    changed_fields: tuple[str, ...]
    severity: float


def gaussian_ct_noise(
    values: Mapping[str, Any],
    sigma_hu: float = 10.0,
    seed: int = 1,
) -> PerturbationResult:
    if sigma_hu < 0.0:
        raise ValueError("sigma must be nonnegative")
    rng = np.random.default_rng(seed)
    output = dict(values)
    changed: list[str] = []
    image = output.get("ct_volume")
    if isinstance(image, np.ndarray):
        output["ct_volume"] = image.astype(np.float32) + rng.normal(0.0, sigma_hu, image.shape)
        changed.append("ct_volume")
    return PerturbationResult(output, tuple(changed), sigma_hu)


def mask_laboratory_values(
    values: Mapping[str, Any],
    fraction: float = 0.20,
    seed: int = 1,
) -> PerturbationResult:
    if fraction < 0.0 or fraction > 1.0:
        raise ValueError("fraction outside [0, 1]")
    keys = tuple(
        key
        for key in values
        if key in {"afp_ng_ml", "albumin_g_dl", "bilirubin_mg_dl", "inr", "platelets_10e9_l"}
    )
    rng = np.random.default_rng(seed)
    count = int(round(len(keys) * fraction))
    selected = (
        tuple(str(value) for value in rng.choice(keys, size=count, replace=False)) if count else ()
    )
    output = dict(values)
    for key in selected:
        output.pop(key, None)
    return PerturbationResult(output, selected, fraction)


def dropout_omics(
    values: Mapping[str, Any],
    fraction: float = 0.30,
    seed: int = 1,
) -> PerturbationResult:
    if fraction < 0.0 or fraction > 1.0:
        raise ValueError("fraction outside [0, 1]")
    output = dict(values)
    changed: list[str] = []
    features = output.get("omics_features")
    if isinstance(features, np.ndarray):
        rng = np.random.default_rng(seed)
        mask = rng.random(features.shape) >= fraction
        output["omics_features"] = features * mask
        changed.append("omics_features")
    return PerturbationResult(output, tuple(changed), fraction)


def ocr_noise(
    values: Mapping[str, Any],
    fraction: float = 0.05,
    seed: int = 1,
) -> PerturbationResult:
    if fraction < 0.0 or fraction > 1.0:
        raise ValueError("fraction outside [0, 1]")
    output = dict(values)
    note = output.get("clinical_note")
    if not isinstance(note, str):
        return PerturbationResult(output, (), fraction)
    rng = np.random.default_rng(seed)
    alphabet = np.asarray(list("abcdefghijklmnopqrstuvwxyz0123456789"))
    characters = list(note)
    eligible = [index for index, value in enumerate(characters) if not value.isspace()]
    count = int(round(len(eligible) * fraction))
    selected = rng.choice(eligible, size=count, replace=False) if count else ()
    for index in selected:
        characters[int(index)] = str(rng.choice(alphabet))
    output["clinical_note"] = "".join(characters)
    return PerturbationResult(output, ("clinical_note",), fraction)


def apply_two_channel(
    values: Mapping[str, Any],
    seed: int = 1,
) -> PerturbationResult:
    ct_result = gaussian_ct_noise(values, 10.0, seed)
    lab_result = mask_laboratory_values(ct_result.values, 0.20, seed + 1)
    changed = tuple(dict.fromkeys(ct_result.changed_fields + lab_result.changed_fields))
    return PerturbationResult(lab_result.values, changed, 0.20)
