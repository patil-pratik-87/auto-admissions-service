"""Typed activation errors for deterministic policy definitions."""


class PolicyActivationError(RuntimeError):
    """Reject an invalid policy package before applicant evaluation."""

    def __init__(self, code: str, safe_message: str) -> None:
        """Initialize a stable policy activation error."""
        super().__init__(safe_message)
        self.code = code
        self.safe_message = safe_message


class EvaluationInputError(ValueError):
    """Reject an inconsistent saved facts artifact at the rules engine seam."""

    def __init__(self, code: str, safe_message: str) -> None:
        """Initialize a stable evaluation-input error."""
        super().__init__(safe_message)
        self.code = code
        self.safe_message = safe_message
