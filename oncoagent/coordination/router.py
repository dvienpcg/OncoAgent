from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from oncoagent.models.types import Modality, PatientBundle, Stage


@dataclass(frozen=True)
class RoutePlan:
    stage: Stage
    active: tuple[Modality, ...]
    missing: tuple[Modality, ...]
    cost: float
    uncertainty: float


class StageAdaptiveMultimodalRouter:
    def __init__(self, budgets: Mapping[Stage, float] | None = None) -> None:
        self._budgets = budgets or {
            Stage.SCREENING: 1.0,
            Stage.DIAGNOSIS: 1.5,
            Stage.STAGING: 3.0,
            Stage.TREATMENT: 3.0,
            Stage.FOLLOW_UP: 1.5,
        }
        self._preferences = {
            Stage.SCREENING: (
                Modality.LABORATORY,
                Modality.IMAGING,
                Modality.EHR,
            ),
            Stage.DIAGNOSIS: (
                Modality.IMAGING,
                Modality.LABORATORY,
                Modality.EHR,
            ),
            Stage.STAGING: (
                Modality.IMAGING,
                Modality.EHR,
                Modality.GENOMICS,
                Modality.LABORATORY,
            ),
            Stage.TREATMENT: (
                Modality.EHR,
                Modality.IMAGING,
                Modality.LABORATORY,
                Modality.GENOMICS,
            ),
            Stage.FOLLOW_UP: (
                Modality.EHR,
                Modality.LABORATORY,
                Modality.IMAGING,
            ),
        }
        self._costs = {
            Modality.LABORATORY: 0.5,
            Modality.EHR: 0.5,
            Modality.CLINICAL_NOTE: 0.5,
            Modality.IMAGING: 1.0,
            Modality.GENOMICS: 1.5,
        }

    def route(
        self,
        stage: Stage,
        bundle: PatientBundle,
        requested: tuple[Modality, ...] = (),
    ) -> RoutePlan:
        available = bundle.available_modalities()
        budget = self._budgets[stage]
        selected: list[Modality] = []
        spent = 0.0
        ordered = requested + tuple(
            modality for modality in self._preferences[stage] if modality not in requested
        )
        for modality in ordered:
            cost = self._costs[modality]
            if modality in available and modality not in selected and spent + cost <= budget:
                selected.append(modality)
                spent += cost
        missing = tuple(modality for modality in ordered if modality not in available)
        expected = min(3, len(self._preferences[stage]))
        uncertainty = max(0.0, 1.0 - len(selected) / expected)
        return RoutePlan(
            stage=stage,
            active=tuple(selected),
            missing=missing,
            cost=spent,
            uncertainty=uncertainty,
        )

    def extract(self, bundle: PatientBundle, plan: RoutePlan) -> Mapping[str, object]:
        merged: dict[str, object] = {}
        for modality in plan.active:
            for key, value in bundle.modalities.get(modality, {}).items():
                merged[key] = value
        return merged

    def budget_for(self, stage: Stage) -> float:
        return self._budgets[stage]
