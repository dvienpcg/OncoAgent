from __future__ import annotations

from collections.abc import Mapping

from oncoagent.agents.base import ClinicalAgent
from oncoagent.agents.clinical import (
    DiagnosisAgent,
    FollowUpAgent,
    ScreeningAgent,
    StagingAgent,
    TreatmentAgent,
)
from oncoagent.coordination.context import AccumulatedClinicalContext
from oncoagent.coordination.feedback import BidirectionalTemporalFeedback
from oncoagent.coordination.gates import VerificationGateNetwork
from oncoagent.coordination.router import StageAdaptiveMultimodalRouter
from oncoagent.guidelines.bclc import BCLCRuleBase
from oncoagent.models.types import (
    ConflictSignal,
    GateAction,
    GateDecision,
    Modality,
    PathwayResult,
    PatientBundle,
    RefinementRecord,
    Stage,
    StageOutput,
)


class OncoAgentEngine:
    def __init__(
        self,
        agents: Mapping[Stage, ClinicalAgent] | None = None,
        router: StageAdaptiveMultimodalRouter | None = None,
        gates: VerificationGateNetwork | None = None,
        feedback: BidirectionalTemporalFeedback | None = None,
        rules: BCLCRuleBase | None = None,
    ) -> None:
        self.rules = rules or BCLCRuleBase()
        self.router = router or StageAdaptiveMultimodalRouter()
        self.gates = gates or VerificationGateNetwork()
        self.feedback = feedback or BidirectionalTemporalFeedback()
        self.agents = agents or {
            Stage.SCREENING: ScreeningAgent(),
            Stage.DIAGNOSIS: DiagnosisAgent(),
            Stage.STAGING: StagingAgent(self.rules),
            Stage.TREATMENT: TreatmentAgent(self.rules),
            Stage.FOLLOW_UP: FollowUpAgent(self.rules),
        }
        self.order = (
            Stage.SCREENING,
            Stage.DIAGNOSIS,
            Stage.STAGING,
            Stage.TREATMENT,
            Stage.FOLLOW_UP,
        )

    def run(self, bundle: PatientBundle) -> PathwayResult:
        context = AccumulatedClinicalContext()
        outputs: list[StageOutput] = []
        decisions: list[GateDecision] = []
        refinements: list[RefinementRecord] = []
        escalated = False
        for stage in self.order:
            output, decision = self._execute_stage(bundle, stage, context)
            decisions.append(decision)
            if not decision.passed:
                output, decision = self._retry(bundle, stage, context, output, decision)
                decisions.append(decision)
            if not decision.passed:
                escalated = True
                return PathwayResult(
                    bundle.case_id,
                    tuple(outputs),
                    context.values,
                    tuple(decisions),
                    tuple(refinements),
                    True,
                    False,
                )
            context.append(output)
            outputs.append(output)
        refinements.extend(self._refine(bundle, context, outputs, decisions))
        return PathwayResult(
            bundle.case_id,
            tuple(outputs),
            context.values,
            tuple(decisions),
            tuple(refinements),
            escalated,
            len(outputs) == len(self.order),
        )

    def _execute_stage(
        self,
        bundle: PatientBundle,
        stage: Stage,
        context: AccumulatedClinicalContext,
        requested: tuple[Modality, ...] = (),
        feedback: ConflictSignal | None = None,
    ) -> tuple[StageOutput, GateDecision]:
        plan = self.router.route(stage, bundle, requested)
        inputs = self.router.extract(bundle, plan)
        output = self.agents[stage].execute(bundle, inputs, context.values, plan, feedback)
        assessment = self.rules.assess(output, context.values)
        decision = self.gates.evaluate(output, context.values, assessment.score)
        return output, decision

    def _retry(
        self,
        bundle: PatientBundle,
        stage: Stage,
        context: AccumulatedClinicalContext,
        previous: StageOutput,
        decision: GateDecision,
    ) -> tuple[StageOutput, GateDecision]:
        if decision.action is GateAction.REQUERY_MODALITY:
            return self._execute_stage(bundle, stage, context, decision.requested_modalities)
        if decision.action is GateAction.INVOKE_BTF:
            assessment = self.rules.assess(previous, context.values)
            if assessment.expected is None:
                return previous, decision
            signal = ConflictSignal(
                stage,
                stage,
                "guideline_transition_violation",
                1.0,
                {"expected": assessment.expected},
            )
            return self._execute_stage(bundle, stage, context, feedback=signal)
        return previous, decision

    def _refine(
        self,
        bundle: PatientBundle,
        context: AccumulatedClinicalContext,
        outputs: list[StageOutput],
        decisions: list[GateDecision],
    ) -> list[RefinementRecord]:
        records: list[RefinementRecord] = []
        for iteration in range(1, self.feedback.depth_cap + 1):
            signals = self.feedback.detect(outputs, context.values)
            if not signals:
                break
            changed = False
            for signal in reversed(signals):
                cooled = self.feedback.cool(signal, iteration - 1)
                if cooled.magnitude <= self.feedback.threshold:
                    continue
                index = self.order.index(cooled.source_stage)
                old = outputs[index]
                rollback_version = index
                context.rollback(rollback_version)
                replacement, decision = self._execute_stage(
                    bundle,
                    cooled.source_stage,
                    context,
                    feedback=cooled,
                )
                decisions.append(decision)
                accepted = decision.passed and replacement.prediction != old.prediction
                records.append(
                    RefinementRecord(
                        iteration,
                        cooled,
                        accepted,
                        old.prediction,
                        replacement.prediction,
                    )
                )
                if not decision.passed:
                    self._restore(context, outputs[: index + 1])
                    continue
                outputs[index] = replacement
                context.append(replacement)
                for downstream_index in range(index + 1, len(outputs)):
                    downstream_stage = self.order[downstream_index]
                    revised, downstream_decision = self._execute_stage(
                        bundle,
                        downstream_stage,
                        context,
                    )
                    decisions.append(downstream_decision)
                    if not downstream_decision.passed:
                        self._restore(context, outputs)
                        break
                    outputs[downstream_index] = revised
                    context.append(revised)
                changed = changed or accepted
            if not changed:
                break
        return records

    def _restore(
        self,
        context: AccumulatedClinicalContext,
        outputs: list[StageOutput],
    ) -> None:
        context.clear()
        for output in outputs:
            context.append(output)
