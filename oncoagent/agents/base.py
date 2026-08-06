from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any

from oncoagent.coordination.router import RoutePlan
from oncoagent.models.types import ConflictSignal, PatientBundle, Stage, StageOutput


class ClinicalAgent(ABC):
    stage: Stage

    @abstractmethod
    def execute(
        self,
        bundle: PatientBundle,
        inputs: Mapping[str, Any],
        context: Mapping[str, Any],
        route: RoutePlan,
        feedback: ConflictSignal | None = None,
    ) -> StageOutput:
        raise NotImplementedError
