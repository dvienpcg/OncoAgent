from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from oncoagent.guidelines.conflicts import CONFLICT_INDEX
from oncoagent.models.types import ConflictSignal, StageOutput


class BidirectionalTemporalFeedback:
    def __init__(self, threshold: float = 0.30, depth_cap: int = 3, cooling: float = 0.10) -> None:
        if threshold < 0.0 or threshold > 1.0:
            raise ValueError("threshold outside [0, 1]")
        if depth_cap < 1:
            raise ValueError("depth cap must be positive")
        self.threshold = threshold
        self.depth_cap = depth_cap
        self.cooling = cooling

    def detect(
        self,
        outputs: Sequence[StageOutput],
        context: Mapping[str, Any],
    ) -> tuple[ConflictSignal, ...]:
        signals: list[ConflictSignal] = []
        stage = str(context.get("bclc_stage", "unknown"))
        treatment = str(context.get("treatment_class", "human_review"))
        invasion = bool(context.get("portal_vein_invasion", False))
        spread = bool(context.get("extrahepatic_spread", False))
        ecog = int(context.get("ecog_status", 0))
        child = str(context.get("child_pugh_class", "A"))
        if invasion and stage not in {"C", "D"}:
            signals.append(self._signal("vascular_invasion_staging_mismatch", {"bclc_stage": "C"}))
        if spread and stage not in {"C", "D"}:
            signals.append(self._signal("metastatic_disease_staging_mismatch", {"bclc_stage": "C"}))
        if ecog >= 3 and stage != "D":
            signals.append(
                self._signal("ecog_upgraded_to_three", {"ecog_status": ecog, "bclc_stage": "D"})
            )
        if child.upper() == "C" and treatment != "best_supportive_care":
            signals.append(
                self._signal("hepatic_reserve_treatment_mismatch", {"child_pugh_class": "C"})
            )
        if treatment == "resection" and invasion:
            signals.append(
                self._signal("treatment_infeasible_resection", {"portal_vein_invasion": True})
            )
        return tuple(signal for signal in signals if signal.magnitude > self.threshold)

    def _signal(self, label: str, evidence: Mapping[str, Any]) -> ConflictSignal:
        definition = CONFLICT_INDEX[label]
        return ConflictSignal(
            source_stage=definition.source,
            target_stage=definition.target,
            label=label,
            magnitude=definition.default_magnitude,
            evidence=evidence,
        )

    def cool(self, signal: ConflictSignal, iteration: int) -> ConflictSignal:
        magnitude = max(0.0, signal.magnitude - self.cooling * iteration)
        return ConflictSignal(
            signal.source_stage,
            signal.target_stage,
            signal.label,
            magnitude,
            signal.evidence,
        )
