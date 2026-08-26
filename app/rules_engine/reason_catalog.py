"""Versioned deterministic labels and prose for application results."""

from app.models.results import ApplicationStatus

REASON_CATALOG_VERSION = "1.1"

RULE_EXPLANATIONS: dict[str, str] = {
    "ABITUR_COUNTRY_UNKNOWN": "The issuing country of the Abitur could not be established.",
    "ABITUR_NOT_GERMAN": "The submitted Abitur is outside the scope of the German Abitur rule.",
    "ADVANCED_VOCATIONAL_COUNTRY_UNKNOWN": "The qualification country could not be established.",
    "ADVANCED_VOCATIONAL_DIRECT_ACCESS": "A completed German advanced vocational qualification meets the direct-access level.",
    "ADVANCED_VOCATIONAL_LEVEL_UNCLEAR": "The advanced vocational qualification level requires human review.",
    "ADVANCED_VOCATIONAL_NOT_GERMAN": "The advanced vocational qualification is outside this German rule.",
    "ADVANCED_VOCATIONAL_REQUIREMENTS_NOT_MET": "The advanced vocational qualification does not meet the configured level requirements.",
    "CLOSE_TO_EXPERIENCE_THRESHOLD": "The professional experience total is within the configured review band.",
    "DACH_FACHGEBUNDENE_HZB_DIRECT_ACCESS": "A completed subject-restricted qualification from the DACH region establishes direct access.",
    "FACHGEBUNDENE_HZB_EVIDENCE_INCOMPLETE": "Required subject-restricted qualification evidence is incomplete.",
    "FACHGEBUNDENE_HZB_NOT_COMPLETED": "The subject-restricted qualification is explicitly incomplete.",
    "FACHGEBUNDENE_HZB_VALIDITY_RESTRICTION_NOT_ACCEPTED": "The stated territorial restriction is not accepted by this policy.",
    "FHR_APPLICABILITY_UNKNOWN": "The country or access scope needed for the general Fachhochschulreife rule is unknown.",
    "FOREIGN_FACHGEBUNDENE_HZB_TRIAL_STUDY": "The outside-DACH subject-restricted rule requires a trial study.",
    "GERMAN_ABITUR_DIRECT_ACCESS": "A completed German Abitur with accepted territorial validity establishes direct access.",
    "GERMAN_ABITUR_EVIDENCE_INCOMPLETE": "Required Abitur evidence is incomplete.",
    "GERMAN_ABITUR_REQUIREMENTS_NOT_MET": "The submitted German Abitur does not satisfy every configured requirement.",
    "GERMAN_GENERAL_FHR_DIRECT_ACCESS": "A complete German general Fachhochschulreife establishes direct access.",
    "GERMAN_GENERAL_FHR_EVIDENCE_INCOMPLETE": "Required general Fachhochschulreife evidence is incomplete.",
    "GERMAN_GENERAL_FHR_REQUIREMENTS_NOT_MET": "The general Fachhochschulreife requirements are proven not satisfied.",
    "NOT_GERMAN_GENERAL_FHR": "The qualification is outside the German general Fachhochschulreife rule.",
    "PROFESSIONAL_ACCESS_ENTRANCE_EXAMINATION": "The professional-access rule requires the professional entrance examination.",
    "PROFESSIONAL_ACCESS_TRIAL_STUDY": "The professional-access rule requires a trial study.",
    "PROFESSIONAL_EVIDENCE_INCOMPLETE": "Required training or employment evidence is incomplete.",
    "PROFESSIONAL_EXPERIENCE_BELOW_THRESHOLD": "The proven professional experience is below the configured threshold.",
    "SUBJECT_MATCH_REVIEW": "The subject relationship remains uncertain and requires human review.",
    "VOCATIONAL_TRAINING_COUNTRY_UNKNOWN": "The vocational training country could not be established.",
    "VOCATIONAL_TRAINING_REQUIREMENTS_NOT_MET": "The vocational training fails a required completion, recognition, duration, or level check.",
    "VOCATIONAL_TRAINING_NOT_GERMAN": "The vocational training is outside this German rule.",
}

FACT_LABELS: dict[str, str] = {
    "qualification.type": "Qualification type",
    "qualification.country": "Issuing country",
    "qualification.completed": "Proof that the qualification is complete",
    "qualification.access_scope": "Qualification access scope",
    "qualification.validity_restriction_present": "Territorial validity information",
    "qualification.validity_restriction_code": "Territorial validity restriction",
    "qualification.school_part_proven": "Proof of the school component",
    "qualification.vocational_part_proven": "Proof of the vocational component",
    "qualification.issuing_region": "Issuing region",
    "qualification.dqr_or_eqr_level": "DQR or EQR level",
    "qualification.teaching_hours": "Teaching hours",
    "qualification.builds_on_completed_training": "Proof of completed prior training",
    "qualification.builds_on_recognized_training": "Proof of recognized prior training",
    "candidate.training.type": "Vocational training type",
    "candidate.training.country": "Vocational training country",
    "candidate.training.completed": "Proof that vocational training is complete",
    "candidate.training.recognized": "Proof that vocational training is recognized",
    "candidate.training.duration_months": "Vocational training duration",
    "candidate.training.dqr_or_eqr_level": "Vocational training DQR or EQR level",
    "candidate.all_period_dates_known": "Complete employment dates",
    "candidate.all_weekly_hours_known": "Complete weekly working hours",
    "candidate.mini_job_classification_complete": "Complete mini-job classification",
    "candidate.full_time_equivalent_days_after_training": "Full-time-equivalent experience after training",
    "candidate.subject_relationship": "Subject relationship",
}

APPLICATION_REASON_CODES: dict[ApplicationStatus, str] = {
    ApplicationStatus.ELIGIBLE: "ACADEMIC_ACCESS_ELIGIBLE",
    ApplicationStatus.CONDITIONALLY_ELIGIBLE: "ACADEMIC_ACCESS_CONDITIONALLY_ELIGIBLE",
    ApplicationStatus.INELIGIBLE: "ACADEMIC_ACCESS_INELIGIBLE",
    ApplicationStatus.MISSING_INFORMATION: "ACADEMIC_ACCESS_MISSING_INFORMATION",
    ApplicationStatus.MANUAL_REVIEW: "ACADEMIC_ACCESS_MANUAL_REVIEW",
}

APPLICATION_HEADLINES: dict[ApplicationStatus, str] = {
    ApplicationStatus.ELIGIBLE: "Academic access is eligible",
    ApplicationStatus.CONDITIONALLY_ELIGIBLE: "Academic access is conditionally eligible",
    ApplicationStatus.INELIGIBLE: "Academic access requirements are not satisfied",
    ApplicationStatus.MISSING_INFORMATION: "Academic access needs more information",
    ApplicationStatus.MANUAL_REVIEW: "Academic access requires manual review",
}
