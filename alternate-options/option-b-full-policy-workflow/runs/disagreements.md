# Disagreements — manual adjudication

Generated 2026-08-25T20:57:35.443614+00:00 · model gpt-5.6-terra · critic=False

## anna-beispiel

- expected: **MISSING_INFORMATION** (derived)
- rules engine: **INELIGIBLE** (`ACADEMIC_ACCESS_INELIGIBLE`) — Academic access requirements are not satisfied
  - missing: []  manual: []
- prototype: **MISSING_INFORMATION** across repeats ['MISSING_INFORMATION', 'MISSING_INFORMATION', 'MISSING_INFORMATION']
  - rationale (latest run): The submitted document certifies only the school-based part of a German Fachhochschulreife. It does not establish the required vocational/practical part, so it does not yet prove a complete Fachhochschulreife that grants direct access to the B.Sc. Computer Science programme.
  - missing: ['Evidence of the vocational/practical part of the Fachhochschulreife (or a combined overall Fachhochschulreife certificate).', 'If the practical part is based on a route subject to a state-specific rule, the corresponding practical-placement/training evidence and any required recognition confirmation.']  manual: []  conditions: []
  - adjudication: _(fill in: which system is right, and why)_

## claudia-siebert

- expected: **ELIGIBLE** (core)
- rules engine: **ELIGIBLE** (`ACADEMIC_ACCESS_ELIGIBLE`) — Academic access is eligible
  - missing: []  manual: []
- prototype: **MISSING_INFORMATION** across repeats ['MISSING_INFORMATION', 'MANUAL_REVIEW', 'MISSING_INFORMATION']
  - rationale (latest run): The applicant has proven a direct academic entrance qualification through a German recognized advanced vocational qualification at DQR level 6. This route is not restricted to a subject area and therefore permits access to B.Sc. Computer Science. However, Computer Science is a listed English-language Bachelor program. The file contains neither accepted English B2 evidence nor information establishing that the applicant is exempt as a native English speaker. The academic-access decision cannot be completed until this is clarified.
  - missing: ['For the English-language B.Sc. Computer Science program: an accepted English B2 certificate issued/tested within the last 5 years (for example TOEFL 80, IELTS 6.0, Duolingo 95, or Cambridge overall grade B), unless the applicant establishes that they are a native English speaker and therefore not subject to this requirement.']  manual: []  conditions: []
  - adjudication: _(fill in: which system is right, and why)_

## daniel-roth

- expected: **nan** (nan)
- rules engine: **MISSING_INFORMATION** (`ACADEMIC_ACCESS_MISSING_INFORMATION`) — Academic access needs more information
  - missing: ['Vocational training duration']  manual: []
- prototype: **MISSING_INFORMATION** across repeats ['CONDITIONALLY_ELIGIBLE', 'MISSING_INFORMATION', 'MISSING_INFORMATION']
  - rationale (latest run): The documents establish the baseline vocational-access requirements: Daniel Roth completed the state-recognized DQR-4 training as Kaufmann für Büromanagement and subsequently worked full-time for more than three years. Because this office-management qualification is not subject-corresponding to B.Sc. Computer Science, the applicable route is IU's subject-noncorresponding professional entrance examination. No evidence shows that the required three examination courses have been passed within one year. In addition, no evidence establishes the required B2 English proficiency for this English-language Computer Science program (or that the applicant is a native speaker).
  - missing: ['Results showing successful completion within one year of all three required IU professional entrance-examination components for B.Sc. Computer Science: Academic Work, the prescribed program-specific subject course, and the study-aptitude test.', 'Valid CEFR B2 English evidence for the English-language B.Sc. Computer Science program, unless native-speaker status or another accepted exemption/alternative is evidenced.']  manual: []  conditions: []
  - adjudication: _(fill in: which system is right, and why)_

## erika-musterfrau

- expected: **ELIGIBLE** (core)
- rules engine: **MANUAL_REVIEW** (`NO_RECOGNIZED_ADMISSIONS_RULE`) — Academic access requires manual review
  - missing: []  manual: ['NO_RECOGNIZED_ADMISSIONS_RULE']
- prototype: **MANUAL_REVIEW** across repeats ['MANUAL_REVIEW', 'ELIGIBLE', 'MANUAL_REVIEW']
  - rationale (latest run): The applicant has documented a directly qualifying Baden-Württemberg general Fachhochschulreife: the certificate expressly confirms both the school-based and job-related components and contains the required KMK upper-secondary agreement reference. Its territorial note (“all Länder except Bavaria and Saxony”) is treated as valid for Thuringia under the policy, so the academic HZB itself provides direct Bachelor access. However, the supplied context does not establish whether this B.Sc. Computer Science intake is English-taught or whether the applicant is a non-native English speaker. If the English-language gate applies, the submitted school certificate records English at B2 but is not one of the expressly listed English test certificates; acceptance as alternative evidence requires an individual determination. A human review is therefore needed solely for that language-gate applicability/evidence issue.
  - missing: []  manual: ['Confirm whether the applied B.Sc. Computer Science programme/intake is an English-taught Bachelor programme under the policy and whether the applicant is subject to the non-native-speaker English requirement.', "If the English requirement applies, individually assess whether the school certificate notation “Englisch – Niveau B2 (GER)” is an acceptable alternative to the policy's listed TOEFL/IELTS/Duolingo/Cambridge evidence."]  conditions: []
  - adjudication: _(fill in: which system is right, and why)_

## katharina-berger

- expected: **nan** (nan)
- rules engine: **MISSING_INFORMATION** (`ACADEMIC_ACCESS_MISSING_INFORMATION`) — Academic access needs more information
  - missing: ['Vocational training DQR or EQR level', 'Vocational training duration']  manual: []
- prototype: **MISSING_INFORMATION** across repeats ['MISSING_INFORMATION', 'MISSING_INFORMATION', 'MISSING_INFORMATION']
  - rationale (latest run): The uploaded documents prove that the applicant passed the German state examination in professional nursing and is authorised to use the title "Pflegefachfrau". They do not prove a general/school higher-education entrance qualification, nor do they establish all requirements for the vocational-access route to B.Sc. Computer Science. In particular, there is no evidence of the training's required duration/DQR level and no evidence of three years of subsequent qualifying professional experience. If the vocational route is pursued, its subject correspondence to Computer Science must also be assessed; nursing is not evidenced as subject-corresponding, so the entrance-examination route may be relevant rather than direct or trial-study access.
  - missing: ['A school-leaving higher-education entrance qualification (e.g. Abitur, Fachhochschulreife) or foreign-equivalence/Anabin evidence, if the applicant relies on a school/foreign HZB route.', 'For vocational access: evidence that the completed Pflegefachfrau training lasted at least two years and meets at least DQR 4 (or applicable recognised-equivalent level).', 'Employment records after completion of vocational training showing exact employment dates, weekly hours, and duties sufficient to calculate three years of qualifying professional experience.', "Information/evidence needed to determine whether the vocational background and professional activity are subject-corresponding to B.Sc. Computer Science; if subject-foreign, successful completion of IU's required professional entrance examination would be needed before matriculation.", 'If the applicant is a foreign applicant, applicable German-language evidence at B2 level (unless an established policy waiver applies).']  manual: []  conditions: []
  - adjudication: _(fill in: which system is right, and why)_

## katrin-vogel

- expected: **MANUAL_REVIEW** (core)
- rules engine: **MISSING_INFORMATION** (`ACADEMIC_ACCESS_MISSING_INFORMATION`) — Academic access needs more information
  - missing: ['Vocational training duration']  manual: []
- prototype: **MISSING_INFORMATION** across repeats ['MISSING_INFORMATION', 'MISSING_INFORMATION', 'MISSING_INFORMATION']
  - rationale (latest run): The submitted IHK certificate proves a state-recognized DQR/EQF-4 vocational qualification as Kauffrau für Büromanagement. The employment certificate proves full-time work (39 hours/week) in that occupation from 01.03.2020 through 24.01.2023, which is just under the required three years of subsequent full-time professional experience. Moreover, Computer Science is not shown to correspond in subject matter to office management, so the vocational route would require the IU entrance examination after the training-and-experience baseline is met. No qualifying later employment, school higher-education entrance qualification, or passed IU entrance examination is provided. As Computer Science is an English-taught Bachelor program, evidence of English B2 is also needed if the applicant is not a native English speaker.
  - missing: ['Evidence that the vocational training lasted at least two years (the IHK certificate confirms recognized DQR 4 status but does not state the training duration).', 'Employment evidence for sufficient additional qualifying work after 24.01.2023 to reach at least three years of subsequent full-time-equivalent professional experience; records must show dates, duties/field, and weekly hours.', 'A passed IU vocational entrance examination for the subject-foreign route to B.Sc. Computer Science, after the vocational baseline has been established.', 'Alternatively, a valid school higher-education entrance qualification (e.g., Abitur or complete Fachhochschulreife) if the applicant seeks direct admission through a school route.', 'If the applicant is not a native English speaker, an accepted English B2 certificate dated within the required five-year validity period, or other accepted English-language evidence.']  manual: []  conditions: []
  - adjudication: _(fill in: which system is right, and why)_

## lena-schmidt-weber

- expected: **MISSING_INFORMATION** (derived)
- rules engine: **INELIGIBLE** (`ACADEMIC_ACCESS_INELIGIBLE`) — Academic access requirements are not satisfied
  - missing: []  manual: []
- prototype: **MISSING_INFORMATION** across repeats ['MISSING_INFORMATION', 'MISSING_INFORMATION', 'MISSING_INFORMATION']
  - rationale (latest run): The submitted certificate proves only the school-based part of the Fachhochschulreife. For direct Bachelor admission on a German Fachhochschulreife that is not issued as an overall certificate, IU requires proof of both the school-based and vocational/practical components. No evidence of the required practical/vocational component or an overall Fachhochschulreife certificate has been submitted. Computer Science has no programme-specific target-group, design-aptitude, or engineering-internship restriction in the supplied policy.
  - missing: ['Evidence of the vocational/practical part required to complete the Fachhochschulreife, or an overall Fachhochschulreife certificate showing that both the school-based and practical components have been recognized.']  manual: []  conditions: []
  - adjudication: _(fill in: which system is right, and why)_

## oemer-yilmaz

- expected: **ELIGIBLE** (derived)
- rules engine: **MANUAL_REVIEW** (`NO_RECOGNIZED_ADMISSIONS_RULE`) — Academic access requires manual review
  - missing: []  manual: ['NO_RECOGNIZED_ADMISSIONS_RULE']
- prototype: **MISSING_INFORMATION** across repeats ['MISSING_INFORMATION', 'MISSING_INFORMATION', 'MANUAL_REVIEW']
  - rationale (latest run): The applicant holds a Baden-Württemberg Fachhochschulreife certificate that expressly confirms completion of both the school-based and vocational components and states that it is recognizable in all Länder except Bavaria and Saxony (therefore including Thuringia). However, the Baden-Württemberg-specific rule requires a particular KMK annotation in the version dated 18.02.2021. The certificate instead cites the same 07.07.1972 KMK agreement in the version effective 16.03.2023. The supplied policy does not clearly establish whether this newer version satisfies the specified-annotation condition, so direct academic access cannot be decided confidently without review. Separately, Computer Science is an English-language Bachelor program and the documents do not establish the required English B2 proof if the applicant is a non-native speaker.
  - missing: ['For the English-language B.Sc. Computer Science program: evidence of English at CEFR B2 (or an accepted alternative), unless the applicant is established to be a native English speaker. The certificate records only English at GER/CEFR B1.']  manual: ["The Baden-Württemberg FHR certificate confirms both required components and territorial recognition outside Bavaria and Saxony, but cites the KMK agreement of 07.07.1972 in the version effective 16.03.2023 rather than the policy's expressly named version of 18.02.2021. A reviewer must determine whether the newer cited version fulfills the Baden-Württemberg-specific annotation requirement."]  conditions: []
  - adjudication: _(fill in: which system is right, and why)_

## stefan-brenner

- expected: **MANUAL_REVIEW** (core)
- rules engine: **MANUAL_REVIEW** (`ACADEMIC_ACCESS_MANUAL_REVIEW`) — Academic access requires manual review
  - missing: ['Proof of completed prior training', 'Proof of recognized prior training', 'DQR or EQR level', 'Teaching hours']  manual: ['ADVANCED_VOCATIONAL_LEVEL_UNCLEAR']
- prototype: **MISSING_INFORMATION** across repeats ['MISSING_INFORMATION', 'ELIGIBLE', 'MISSING_INFORMATION']
  - rationale (latest run): The applicant has proven a direct academic entrance-qualification route through a German Meister examination (Elektrotechnikermeister). However, B.Sc. Computer Science is listed as an English-language Bachelor programme. The documents contain neither qualifying B2 English evidence nor evidence that the applicant is a native English speaker, so eligibility for study start cannot be fully established.
  - missing: ['Proof of English proficiency at CEFR B2 or above for the English-language B.Sc. Computer Science programme (for example, TOEFL iBT at least 80, IELTS at least 6.0, Duolingo English Test at least 95, Cambridge overall grade B, or an accepted alternative), unless evidence is provided that the applicant is a native English speaker.']  manual: []  conditions: []
  - adjudication: _(fill in: which system is right, and why)_

## tobias-falk

- expected: **INELIGIBLE** (core)
- rules engine: **MISSING_INFORMATION** (`ACADEMIC_ACCESS_MISSING_INFORMATION`) — Academic access needs more information
  - missing: ['Vocational training duration']  manual: []
- prototype: **MISSING_INFORMATION** across repeats ['MISSING_INFORMATION', 'MISSING_INFORMATION', 'MISSING_INFORMATION']
  - rationale (latest run): The documents prove a German state-recognized DQR/EQR level-4 vocational qualification as Kaufmann für Büromanagement and one full-time employment period of about 13 months. They do not prove the three years of qualifying full-time-equivalent professional activity required for the professionally qualified access route. No school-based higher-education entrance qualification, FHR, Meister/DQR-6 advanced qualification, or other direct-access qualification is provided. Therefore, academic eligibility cannot yet be established.
  - missing: ['Evidence of at least three years of qualifying full-time-equivalent professional activity after the completed vocational training (employer certificates showing dates, role/field, and weekly hours). The submitted employment certificate proves only 01.09.2021 to 05.10.2022 at 39 hours per week.', 'Alternatively, a school-leaving higher-education entrance qualification (e.g., Abitur, Fachhochschulreife including practical part where applicable) or another direct Bachelor-access qualification, if available.', 'If relying on professionally qualified access: evidence allowing IU to determine whether the vocational training and subsequent work correspond to B.Sc. Computer Science, or—if not corresponding—subsequent IU entrance-examination results after vocational-base eligibility is established.']  manual: []  conditions: []
  - adjudication: _(fill in: which system is right, and why)_
