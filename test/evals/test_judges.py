import pytest
from pydantic import ValidationError

from evals.judges.judges import JudgeVerdict


def test_judge_verdict_is_binary_and_requires_a_detailed_critique() -> None:
    """The semantic diagnostic cannot manufacture confidence with a third label."""
    with pytest.raises(ValidationError):
        JudgeVerdict.model_validate(
            {
                "critique": "",
                "affected_claims": [],
                "affected_pages": [],
                "result": "UNCERTAIN",
            }
        )
