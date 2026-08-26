"""Deep deterministic rules engine seam."""

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from app.models.artifacts import ApplicationFactsArtifact
from app.models.compiled_policy import CompiledPolicy
from app.models.failures import FailureStage, ProcessingFailureReport
from app.models.outcomes import EvaluationFailed, EvaluationOutcome, EvaluationSucceeded
from app.rules_engine.compiler import compile_policy_package
from app.rules_engine.errors import EvaluationInputError
from app.rules_engine.evaluator import evaluate_policy


@dataclass(frozen=True, slots=True)
class RulesEngine:
    """Pure activated admissions policy evaluator."""

    _policies: Mapping[str, CompiledPolicy]

    @classmethod
    def activate(cls, rules_root: Path) -> "RulesEngine":
        """Eagerly load and compile every executable policy definition.

        Args:
            rules_root: Trusted directory containing the DSL 1.3 policy package.

        Returns:
            A fully activated deterministic rules engine.

        Raises:
            PolicyActivationError: If any authored definition is invalid.
        """
        return cls(_policies=compile_policy_package(rules_root))

    def has_policy(self, policy_id: str, version: str) -> bool:
        """Report whether one exact policy identity was activated."""
        policy = self._policies.get(policy_id)
        return policy is not None and policy.version == version

    def evaluate(self, artifact: ApplicationFactsArtifact) -> EvaluationOutcome:
        """Evaluate one complete saved facts artifact without I/O or model calls."""
        try:
            result = evaluate_policy(self._select(artifact), artifact)
        except EvaluationInputError as error:
            return EvaluationFailed(
                kind="EVALUATION_FAILED",
                failure=ProcessingFailureReport(
                    kind="PROCESSING_FAILURE",
                    report_version="1.0",
                    run_id=artifact.run_id,
                    stage=FailureStage.EVALUATION,
                    code=error.code,
                    safe_message=error.safe_message,
                    retryable=False,
                ),
            )
        return EvaluationSucceeded(kind="EVALUATION_SUCCEEDED", result=result)

    def _select(self, artifact: ApplicationFactsArtifact) -> CompiledPolicy:
        policy = self._policies.get(artifact.program.policy.id)
        if policy is None:
            raise EvaluationInputError(
                "POLICY_NOT_ACTIVATED", "The saved facts reference a policy this deployment did not activate"
            )
        return policy
