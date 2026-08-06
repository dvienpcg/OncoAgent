from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from dataclasses import dataclass
from threading import RLock
from typing import Any

from oncoagent.models.schema import FIELD_INDEX, validate_context
from oncoagent.models.types import ContextVersion, Stage, StageOutput


@dataclass(frozen=True)
class ContextSnapshot:
    version: int
    values: Mapping[str, Any]
    history_size: int


class AccumulatedClinicalContext:
    def __init__(self) -> None:
        self._values: dict[str, Any] = {}
        self._versions: list[ContextVersion] = []
        self._lock = RLock()

    @property
    def version(self) -> int:
        with self._lock:
            return len(self._versions)

    @property
    def values(self) -> Mapping[str, Any]:
        with self._lock:
            return deepcopy(self._values)

    @property
    def history(self) -> tuple[ContextVersion, ...]:
        with self._lock:
            return tuple(self._versions)

    def append(self, output: StageOutput) -> ContextVersion:
        unknown = tuple(key for key in output.findings if key not in FIELD_INDEX)
        if unknown:
            raise ValueError(f"unknown ACC fields: {unknown}")
        invalid = validate_context(output.findings)
        if invalid:
            raise ValueError(f"invalid ACC values: {invalid}")
        with self._lock:
            merged = deepcopy(self._values)
            merged.update(output.findings)
            merged["calibrated_confidence"] = output.distribution.confidence
            merged["uncertainty_flag"] = output.uncertainty
            invalid_merged = validate_context(merged)
            if invalid_merged:
                raise ValueError(f"invalid merged ACC values: {invalid_merged}")
            version = ContextVersion(
                version=len(self._versions) + 1,
                stage=output.stage,
                values=merged,
                output=output,
            )
            self._values = merged
            self._versions.append(version)
            return version

    def replace_from(self, stage: Stage, output: StageOutput) -> ContextVersion:
        with self._lock:
            retained = [item for item in self._versions if item.stage.value < stage.value]
            self._values = {}
            self._versions = []
            for item in retained:
                self.append(item.output)
            return self.append(output)

    def rollback(self, version: int) -> ContextSnapshot:
        with self._lock:
            if version < 0 or version > len(self._versions):
                raise ValueError("rollback version outside history")
            retained = self._versions[:version]
            self._values = {}
            self._versions = []
            for item in retained:
                self.append(item.output)
            return self.snapshot()

    def snapshot(self) -> ContextSnapshot:
        with self._lock:
            return ContextSnapshot(
                version=len(self._versions),
                values=deepcopy(self._values),
                history_size=len(self._versions),
            )

    def output_for(self, stage: Stage) -> StageOutput:
        with self._lock:
            for item in reversed(self._versions):
                if item.stage is stage:
                    return item.output
        raise KeyError(stage.value)

    def contains(self, field_name: str) -> bool:
        with self._lock:
            return field_name in self._values and self._values[field_name] is not None

    def completeness(self, required: tuple[str, ...]) -> float:
        if not required:
            return 1.0
        with self._lock:
            present = sum(
                1 for name in required if name in self._values and self._values[name] is not None
            )
        return present / len(required)

    def clear(self) -> None:
        with self._lock:
            self._values = {}
            self._versions = []
