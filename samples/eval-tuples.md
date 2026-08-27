# Synthetic evaluation tuples for the Bachelor prototype

> Initial implementation gate: use the 15 representative cases selected in
> `test/rules_engine/test_gold_scenarios.py`. The other tuples below remain source
> material for later expansion and are not required for the first working demo.

This file describes the first synthetic evaluation set for policy
`IU_BACHELOR_ACCESS` version `0.0.22`. It covers the rules that are executable
today. It does not describe rules that exist only in the source guide.

The existing documents are enough to start document classification, extraction,
and basic rule integration. They do not yet cover every result branch in the
current policy. The table below separates existing cases from cases that still
need a fact variant, a new document, or a combined bundle.

## Current scope

The prototype evaluates five rules:

1. `GERMAN_ABITUR`
2. `FACHGEBUNDENE_HOCHSCHULREIFE`
3. `GERMAN_GENERAL_FACHHOCHSCHULREIFE`
4. `GERMAN_MEISTER_OR_ADVANCED_VOCATIONAL`
5. `GERMAN_TRAINING_PLUS_PROFESSIONAL_EXPERIENCE`

The first evaluation set also checks how rule results become one application
result. Language checks, nursing requirements, other foreign qualifications,
subject restricted Fachhochschulreife, self employment, DQR level 3
exceptions, prior study checks, and matriculation documents are outside the
current policy.

## Dimensions

Each tuple has three dimensions:

`(rule, decision_case, input_condition)`

| Dimension | What it tests | Values used in this set |
| --- | --- | --- |
| `rule` | The rule group and facts that the evaluator must use. | The five rules above, plus `APPLICATION_RESOLUTION`. |
| `decision_case` | The policy branch that should run. | `SATISFIED`, `PROVEN_FALSE`, `REQUIRED_FACT_UNKNOWN`, `NOT_APPLICABLE`, `NEAR_THRESHOLD`, `SUBJECT_MATCH`, `SUBJECT_NO_MATCH`, `SUBJECT_UNCERTAIN`, `MULTIPLE_RULES`, `NO_RECOGNIZED_RULE`. |
| `input_condition` | The document or normalized fact condition that may cause a pipeline error. | `CLEAN`, `IRRELEVANT_FIELD_ABSENT`, `REQUIRED_FIELD_ABSENT`, `REQUIRED_FIELD_ILLEGIBLE`, `SUPPORTED_FACT_VARIANT`, `MIXED_BUNDLE`. |

The dimensions target expected failures. The extractor may miss a required
field, the fact builder may combine two documents incorrectly, the evaluator
may treat unknown as false, or final resolution may reject an application even
though another rule succeeds.

## Core tuples 1 to 20

`Existing` means that the repository already contains the required document
bundle. `Fact variant needed` means that the documents exist, but the prototype
still needs an application fact fixture. `Proposed` means that a document or
combined bundle still needs to be created. The proposed rows should be confirmed
before new documents are generated.

| # | Rule | Decision case | Input condition | Sample | Expected rule result | Expected application result | State |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `GERMAN_ABITUR` | `SATISFIED` | `CLEAN` | `felix-brandt` | `ELIGIBLE`, `GERMAN_ABITUR_DIRECT_ACCESS` | `ELIGIBLE` | Existing |
| 2 | `GERMAN_ABITUR` | `SATISFIED` | `IRRELEVANT_FIELD_ABSENT` | `sofia-lorenz` | `ELIGIBLE`, `GERMAN_ABITUR_DIRECT_ACCESS`, although the average grade is absent | `ELIGIBLE` | Existing |
| 3 | `GERMAN_ABITUR` | `PROVEN_FALSE` | `SUPPORTED_FACT_VARIANT` | `lukas-fischer`, Abitur with a known unsupported validity restriction | `NOT_SATISFIED`, `GERMAN_ABITUR_REQUIREMENTS_NOT_MET` | `INELIGIBLE`, when this is the only applicable rule | Existing |
| 4 | `GERMAN_ABITUR` | `REQUIRED_FACT_UNKNOWN` | `REQUIRED_FIELD_ILLEGIBLE` | `sarah-koenig`, Abitur with a stated but unreadable validity restriction (scan only) | `MISSING_INFORMATION`, `GERMAN_ABITUR_EVIDENCE_INCOMPLETE` | `MISSING_INFORMATION` | Existing |
| 5 | `GERMAN_GENERAL_FACHHOCHSCHULREIFE` | `SATISFIED` | `CLEAN` | `erika-musterfrau` | `ELIGIBLE`, using the Bavaria and Saxony exception annotation | `ELIGIBLE` | Existing |
| 6 | `GERMAN_GENERAL_FACHHOCHSCHULREIFE` | `SATISFIED` | `MIXED_BUNDLE` | `anna-beispiel`, KMK school part plus IHK vocational-part proof, with no validity restriction | `ELIGIBLE`, `GERMAN_GENERAL_FHR_DIRECT_ACCESS` | `ELIGIBLE` | Existing |
| 7 | `GERMAN_GENERAL_FACHHOCHSCHULREIFE` | `REQUIRED_FACT_UNKNOWN` | `REQUIRED_FIELD_ABSENT` | `jonas-krause` | `MISSING_INFORMATION`, `GERMAN_GENERAL_FHR_EVIDENCE_INCOMPLETE`, because the vocational part is not proven | `MISSING_INFORMATION` | Existing |
| 8 | `GERMAN_GENERAL_FACHHOCHSCHULREIFE` | `PROVEN_FALSE` | `SUPPORTED_FACT_VARIANT` | `miriam-albrecht`, complete BW FHR with a known unsupported validity restriction | `NOT_SATISFIED`, `GERMAN_GENERAL_FHR_REQUIREMENTS_NOT_MET` | `INELIGIBLE`, when this is the only applicable rule | Existing |
| 9 | `GERMAN_MEISTER_OR_ADVANCED_VOCATIONAL` | `SATISFIED` | `CLEAN` | `claudia-siebert` | `ELIGIBLE`, because the completed qualification is DQR level 6 | `ELIGIBLE` | Existing |
| 10 | `GERMAN_MEISTER_OR_ADVANCED_VOCATIONAL` | `SATISFIED` | `SUPPORTED_FACT_VARIANT` | `bernd-keller`, completed qualification without a printed DQR level, with 560 teaching hours building on completed recognized training | `ELIGIBLE`, `ADVANCED_VOCATIONAL_DIRECT_ACCESS` | `ELIGIBLE` | Existing |
| 11 | `GERMAN_MEISTER_OR_ADVANCED_VOCATIONAL` | `PROVEN_FALSE` | `CLEAN` | `frank-seidel`, completed qualification stating DQR level 5 and 220 teaching hours | `NOT_SATISFIED`, `ADVANCED_VOCATIONAL_REQUIREMENTS_NOT_MET` | `INELIGIBLE`, when this is the only applicable rule | Existing |
| 12 | `GERMAN_MEISTER_OR_ADVANCED_VOCATIONAL` | `REQUIRED_FACT_UNKNOWN` | `REQUIRED_FIELD_ABSENT` | `stefan-brenner` | `MANUAL_REVIEW`, `ADVANCED_VOCATIONAL_LEVEL_UNCLEAR` | `MANUAL_REVIEW` | Existing |
| 13 | `GERMAN_TRAINING_PLUS_PROFESSIONAL_EXPERIENCE` | `SUBJECT_MATCH` | `SUPPORTED_FACT_VARIANT` | `daniel-roth`, with a matching program subject | `CONDITIONALLY_ELIGIBLE`, `PROFESSIONAL_ACCESS_TRIAL_STUDY` | `CONDITIONALLY_ELIGIBLE` | Fact variant needed |
| 14 | `GERMAN_TRAINING_PLUS_PROFESSIONAL_EXPERIENCE` | `SUBJECT_NO_MATCH` | `SUPPORTED_FACT_VARIANT` | `daniel-roth`, with a nonmatching program subject | `CONDITIONALLY_ELIGIBLE`, `PROFESSIONAL_ACCESS_ENTRANCE_EXAMINATION` | `CONDITIONALLY_ELIGIBLE` | Fact variant needed |
| 15 | `GERMAN_TRAINING_PLUS_PROFESSIONAL_EXPERIENCE` | `SUBJECT_UNCERTAIN` | `SUPPORTED_FACT_VARIANT` | `daniel-roth`, with an uncertain subject relationship | `MANUAL_REVIEW`, `SUBJECT_MATCH_REVIEW` | `MANUAL_REVIEW` | Fact variant needed |
| 16 | `GERMAN_TRAINING_PLUS_PROFESSIONAL_EXPERIENCE` | `NEAR_THRESHOLD` | `CLEAN` | `katrin-vogel` | `MANUAL_REVIEW`, `CLOSE_TO_EXPERIENCE_THRESHOLD` | `MANUAL_REVIEW` | Existing |
| 17 | `GERMAN_TRAINING_PLUS_PROFESSIONAL_EXPERIENCE` | `PROVEN_FALSE` | `CLEAN` | `tobias-falk` | `NOT_SATISFIED`, `PROFESSIONAL_EXPERIENCE_BELOW_THRESHOLD` | `INELIGIBLE`, when this is the only applicable rule | Existing |
| 18 | `GERMAN_TRAINING_PLUS_PROFESSIONAL_EXPERIENCE` | `REQUIRED_FACT_UNKNOWN` | `REQUIRED_FIELD_ABSENT` | `tobias-renner` | `MISSING_INFORMATION`, `PROFESSIONAL_EVIDENCE_INCOMPLETE`, because weekly hours and full-time-equivalent days cannot be established | `MISSING_INFORMATION` | Existing |
| 19 | `APPLICATION_RESOLUTION` | `MULTIPLE_RULES` | `MIXED_BUNDLE` | `felix-brandt-kombi`, Abitur plus IHK training proof plus a prose Arbeitszeugnis without weekly hours | Abitur is `ELIGIBLE`, and the professional rule is `MISSING_INFORMATION` | `ELIGIBLE`, because the ordered resolution keeps the proven successful rule | Existing |
| 20 | `APPLICATION_RESOLUTION` | `NO_RECOGNIZED_RULE` | `CLEAN` | `nora-weiss`, only a VHS Teilnahmebescheinigung without an exam — no document any rule selector recognizes | No rule applies | `MANUAL_REVIEW` | Existing |

Tuple 13 must include the `TRIAL_STUDY` condition with two first subject
semesters and at least 15 newly earned ECTS. Tuple 14 must include the
`PROFESSIONAL_ENTRANCE_EXAMINATION` condition with a limit of 12 months, 10 to 15
ECTS, and the three required courses defined in `rules/common/conditions.yaml`.

## Added subject restricted Hochschulreife tuples

The new rule needs the following evaluation cases:

| # | Rule | Decision case | Input condition | Sample | Expected rule result | Expected application result | State |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 21 | `FACHGEBUNDENE_HOCHSCHULREIFE` | `SATISFIED` | `CLEAN` | `julia-hartmann`, Bayern BOS Zeugnis (Anlage 17) with no validity restriction | `ELIGIBLE`, `DACH_FACHGEBUNDENE_HZB_DIRECT_ACCESS` | `ELIGIBLE` | Existing |
| 22 | `FACHGEBUNDENE_HOCHSCHULREIFE` | `SATISFIED` | `CLEAN` | `laura-beck`, Liechtenstein Berufsmaturitätszeugnis — German-language, but the stated issuing state is outside DACH | `CONDITIONALLY_ELIGIBLE`, `FOREIGN_FACHGEBUNDENE_HZB_TRIAL_STUDY` | `CONDITIONALLY_ELIGIBLE` | Existing |
| 23 | `FACHGEBUNDENE_HOCHSCHULREIFE` | `PROVEN_FALSE` | `SUPPORTED_FACT_VARIANT` | `marco-lang`, BOS Zeugnis explicitly marked "nicht bestanden" / "nicht verliehen" | `NOT_SATISFIED`, `FACHGEBUNDENE_HZB_NOT_COMPLETED` | `INELIGIBLE`, when no other rule applies | Existing |
| 24 | `FACHGEBUNDENE_HOCHSCHULREIFE` | `REQUIRED_FACT_UNKNOWN` | `REQUIRED_FIELD_ILLEGIBLE` | `elif-demir`, completed BOS Zeugnis with the school and issue-place lines blotted (scan only) | `MISSING_INFORMATION`, `FACHGEBUNDENE_HZB_EVIDENCE_INCOMPLETE` | `MISSING_INFORMATION` | Existing |
| 25 | `FACHGEBUNDENE_HOCHSCHULREIFE` | `PROVEN_FALSE` | `SUPPORTED_FACT_VARIANT` | `patrick-koenig`, completed BOS Zeugnis with a printed restriction to Bavarian Hochschulen, normalized as `OTHER` | `NOT_SATISFIED`, `FACHGEBUNDENE_HZB_VALIDITY_RESTRICTION_NOT_ACCEPTED` | `INELIGIBLE`, when no other rule applies | Existing |

Tuple 22 must include the `TRIAL_STUDY` condition. The normalized facts for
these tuples must include `qualification.issuing_region`,
`qualification.validity_restriction_present`, and
`qualification.validity_restriction_code`.

## Existing variants outside the core tuples

Several generated samples remain useful, but they should not count as separate
policy branches in the first set:

| Sample | Use |
| --- | --- |
| `oemer-yilmaz` | A second complete FHR case with a non-ASCII name. It checks extraction and identity handling. |
| `max-mustermann` and `lena-schmidt-weber` | More school-part-only FHR documents. They repeat tuple 7 until a vocational part is added. |
| `melina-sturm` | An alternate form of tuple 18 where the employment end date is illegible. The evaluator must not calculate a threshold result from a partial date. |

Note for tuple 20: a nursing-qualification bundle (removed `katharina-berger`)
cannot serve as the `NO_RECOGNIZED_RULE` case — a state-exam training
certificate still enters `GERMAN_TRAINING_PLUS_PROFESSIONAL_EXPERIENCE` as
vocational training. The tuple-20 bundle must contain no document any rule
selector recognizes.

## Coverage assessment

The samples now cover every document bundle in the first tuple set: clean
Abitur, rejected and unreadable territorial validity, complete one- and
two-document FHR, an FHR with rejected validity, DQR level 6 advanced
training, the 400 teaching-hour alternative, a proven advanced vocational
failure, an unclear Meister document, three employment thresholds, missing
weekly hours, an illegible employment date, a mixed-rule bundle for the
ordered resolution, a bundle no rule selector recognizes, and all five
subject restricted Hochschulreife cases (including the outside DACH
Liechtenstein variant).

The full draft contains 25 tuples. Every tuple that needs a document bundle
has one; tuples 13 to 15 reuse the `daniel-roth` documents and still need
their application fact variants.

What remains is gold data, not documents: the application fact fixtures
described below, including the three semantic subject results for tuples 13
to 15. The rule engine cannot be called correct until those fixtures exist
and the bundles have run through the full pipeline.

## Required gold data

Each bundle folder under `samples/filled-documents/<slug>/` contains the
persona YAML next to the PDFs generated from it, so a reviewer can verify a
bundle in one place. The YAML files contain values used to generate PDFs.
They are not direct rule-engine inputs. Each evaluation case also needs a gold
application fact fixture with:

1. The normalized facts used by the selected rule, including fact quality and
   source evidence.
2. The expected result for every applicable rule, including its reason code
   and condition when present.
3. The expected final application result after the ordered resolution.

For example, the FHR cases need explicit values for
`qualification.school_part_proven`, `qualification.vocational_part_proven`,
`qualification.validity_restriction_present`, and
`qualification.validity_restriction_code`. The professional cases need
normalized `candidate.training` facts, usable employment inputs,
`candidate.full_time_equivalent_days_after_training`, and
`candidate.subject_relationship`. Document verification enums are not part of
the current policy fact model.

The subject restricted Hochschulreife cases also need `qualification.completed`
and `qualification.issuing_region`. The fact builder derives `DACH` for Germany, Austria, and
Switzerland, and `OUTSIDE_DACH` for every other known issuing country.

## Build order

First, create gold fact fixtures for the existing samples. The fixtures make
tuples 1, 2, 5, 7, 9, 12, and 16 to 18 executable without generating more
PDFs.

Second, add the three `daniel-roth` subject variants. They can reuse the same
documents, because only the application program and expected semantic outcome
differ.

Third (done): the validity restriction, two-part FHR, 400 teaching-hour,
advanced vocational failure, mixed-rule, and no-recognized-rule bundles are
generated (`lukas-fischer`, `sarah-koenig`, `anna-beispiel` + IHK part,
`miriam-albrecht`, `bernd-keller`, `frank-seidel`, `felix-brandt-kombi`,
`nora-weiss`). After these cases run through the full pipeline, review the
traces before adding more dimensions.

Fourth (done): the subject restricted Hochschulreife bundles are generated
from the Bayern Anlage 17 template (`julia-hartmann`, `marco-lang`,
`elif-demir`, `patrick-koenig`) plus the outside DACH variant (`laura-beck`).

## Rule applicability tuples

These cases verify that rule discovery does not hide an unknown or proven
false applicability fact:

| # | Candidate rule | Input | Expected rule behavior | Expected application result |
| --- | --- | --- | --- | --- |
| 26 | `GERMAN_ABITUR` | Abitur type known; country unreadable | `MISSING_INFORMATION`, `ABITUR_COUNTRY_UNKNOWN` | `MISSING_INFORMATION` |
| 27 | `GERMAN_ABITUR` | Abitur type known; country known and not Germany | Internal `NOT_APPLICABLE`, `ABITUR_NOT_GERMAN` | `MANUAL_REVIEW` when no other rule applies |
| 28 | `GERMAN_GENERAL_FACHHOCHSCHULREIFE` | FHR type known; access scope unreadable | `MISSING_INFORMATION`, `FHR_APPLICABILITY_UNKNOWN` | `MISSING_INFORMATION` |
| 29 | `GERMAN_TRAINING_PLUS_PROFESSIONAL_EXPERIENCE` | German vocational training explicitly not completed | `NOT_SATISFIED`, `VOCATIONAL_TRAINING_REQUIREMENTS_NOT_MET` | `INELIGIBLE` when no other rule applies |
| 30 | `GERMAN_TRAINING_PLUS_PROFESSIONAL_EXPERIENCE` | Vocational training type known; completion unreadable | `MISSING_INFORMATION`, `PROFESSIONAL_EVIDENCE_INCOMPLETE` | `MISSING_INFORMATION` |
| 31 | `GERMAN_TRAINING_PLUS_PROFESSIONAL_EXPERIENCE` | Vocational training type known; country unreadable | `MISSING_INFORMATION`, `VOCATIONAL_TRAINING_COUNTRY_UNKNOWN` | `MISSING_INFORMATION` |

`NOT_APPLICABLE` is exported by the rule-status enum (`rules/rule-statuses.yaml`),
but the ordered resolution never matches on it. A known scope mismatch uses
`NOT_APPLICABLE`; an unknown scope fact emits a normal `MISSING_INFORMATION`
rule result.
