"""Output contracts for every LLM call, plus the on-disk criteria artifact.

The fairness line from the earlier experiments runs through this module:
- `application_status` shares the rules engine's 5-value vocabulary (answer vocabulary).
- The rule taxonomy (GERMAN_ABITUR, ...) and reason codes are deliberately absent —
  the policy analyst must rediscover the routes from the handbook itself.
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field

ApplicationStatus = Literal[
    "ELIGIBLE",
    "CONDITIONALLY_ELIGIBLE",
    "INELIGIBLE",
    "MISSING_INFORMATION",
    "MANUAL_REVIEW",
]


# --- Compile step: navigation turns (arm-specific) --------------------------------
class TocNavigationTurn(BaseModel):
    """ARM_TOC: the analyst picks sections from the table of contents by ID."""

    rationale: str = Field(description="Why these sections are the right ones to open next")
    open_section_ids: list[str] = Field(description="Section IDs from the table of contents to open in full")
    coverage_complete: bool = Field(description="True once the opened sections cover every route relevant to the task")


class RagNavigationTurn(BaseModel):
    """ARM_RAG: the analyst has no table of contents and searches semantically."""

    rationale: str = Field(description="Why these queries target the still-uncovered parts of the policy")
    search_queries: list[str] = Field(description="Up to 3 natural-language search queries against the policy document")
    coverage_complete: bool = Field(description="True once the retrieved sections cover every route relevant to the task")


# --- Compile step: the criteria the policy analyst produces -----------------------
class CompiledCriterion(BaseModel):
    criterion_id: str = Field(description="Short stable slug the analyst chooses itself, e.g. 'abitur-direct'")
    name: str
    summary: str = Field(description="The condition in the analyst's own words, with exact thresholds")
    source_excerpts: list[str] = Field(description="Exact verbatim excerpts from the cited policy sections stating the criterion's conditions and their consequences for admission")
    citations: list[str] = Field(description="Section IDs of the policy sections this criterion is derived from")


class PolicyCriteria(BaseModel):
    policy_title: str
    scope_notes: str = Field(description="What the analyst treated as in/out of scope and why")
    criteria: list[CompiledCriterion]


class CriteriaArtifact(BaseModel):
    """On-disk cache entry: compiled criteria plus everything needed to validate the cache."""

    arm: str
    model: str
    policy_sha256: str
    instructions_sha256: str
    compiled_at: str
    coverage_complete: bool
    unverified_excerpts: list[str]  # criterion_ids with an excerpt that failed verbatim verification
    opened_section_ids: list[str]
    opened_section_titles: list[str]
    nav_trace: list[dict]
    criteria: PolicyCriteria


# --- Per-applicant graph: evaluator ----------------------------------------------
class CriterionAssessment(BaseModel):
    criterion_id: str = Field(description="Must reference a criterion_id from the compiled criteria")
    verdict: Literal["FULFILLED", "NOT_FULFILLED", "UNCLEAR", "NOT_RELEVANT"]
    reasoning: str
    evidence: str = Field(description="Short quotation or concrete reference from the applicant's documents; empty string if none")


class AdmissionDecision(BaseModel):
    application_status: ApplicationStatus
    rationale: str = Field(description="The decisive chain of reasoning, in plain language")
    conditions: list[str] = Field(description="Conditions attached to a CONDITIONALLY_ELIGIBLE outcome; else empty")
    missing_information: list[str] = Field(description="Evidence that is absent/incomplete/unreadable; else empty")
    manual_review_reasons: list[str] = Field(description="Why a human must look at this; else empty")
    criteria_assessments: list[CriterionAssessment]


# --- Per-applicant graph: critic --------------------------------------------------
class TocCriticLookup(BaseModel):
    """ARM_TOC: which policy sections the critic wants to verify the verdict against."""

    rationale: str
    open_section_ids: list[str] = Field(description="Section IDs to open; empty list if no policy lookup is needed")


class RagCriticLookup(BaseModel):
    """ARM_RAG: what the critic wants to search the policy for."""

    rationale: str
    search_queries: list[str] = Field(description="Up to 3 search queries; empty list if no policy lookup is needed")


class CriticReview(BaseModel):
    approve: bool = Field(description="True if the draft verdict survives the review")
    objection: str = Field(description="When approve is false: what is wrong with the draft; empty string otherwise")
    policy_evidence: str = Field(description="When approve is false: the retrieved policy passages that support the objection, quoted or paraphrased with section references; empty string otherwise")


class CriticOutcome(BaseModel):
    """Aggregated critic result attached to each run record (not an LLM output)."""

    approved_first: bool
    retried: bool
    resolved: Optional[bool] = Field(default=None, description="After a retry: did the second review approve? None if no retry happened")
    critic_unresolved: bool = False
    status_before_retry: Optional[ApplicationStatus] = None
