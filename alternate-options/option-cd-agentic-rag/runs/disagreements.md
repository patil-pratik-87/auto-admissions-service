# Disagreements — manual adjudication

Generated 2026-08-26T18:03:47.348957+00:00 · model gpt-5.4-mini

## anna-beispiel

- expected: **MISSING_INFORMATION** (derived)
- rules engine: **MISSING_INFORMATION** — Academic access needs more information
- full policy workflow: **MISSING_INFORMATION**
- ARM_TOC: **ELIGIBLE** across ['ELIGIBLE', 'MISSING_INFORMATION', 'ELIGIBLE'] (retries 3, unresolved 2)
  - rationale (latest): The applicant proves a direct academic entrance qualification by submitting an Abitur certificate from a Gymnasium / gymnasiale Oberstufe. The school document is not merely a Fachhochschulreife-school-part certificate: it includes the standard Abitur/gymnasiale-Oberstufe performance sheet with an overall average of 1.8 and the KMK reference to the gymnasiale Oberstufe agreement. Under the policy, a general higher education entrance qualification is sufficient and uncritical, while the separate Fachhochschulreife route would require both school-based and vocational parts only if that were the route being used. Here, the evidence supports the general Abitur route directly, so no extra conditions apply.
- ARM_RAG: **ELIGIBLE** across ['ELIGIBLE', 'INELIGIBLE', 'ELIGIBLE'] (retries 3, unresolved 3)
  - rationale (latest): The applicant documents show a completed German vocational qualification at DQR level 4 ('Kaufmann für Büromanagement') and a separate certificate for the school-based part of the Fachhochschulreife. Under s004, the general Fachhochschulreife is an uncritical route; if it is not an overall certificate, the school-based and vocational parts must both be proven. The uploaded school certificate explicitly states the school-based FHR part was earned, and the policy does not make the absence of the vocational part an ineligibility finding. Because the applicant already has an acceptable academic entrance route via the general FHR evidence, and there is no affirmative proof of failure under any route, the applicant is eligible for academic entrance qualification assessment purposes.
- adjudication: _(fill in: which system is right, and why)_

## claudia-siebert

- expected: **ELIGIBLE** (core)
- rules engine: **ELIGIBLE** — Academic access is eligible
- full policy workflow: **MISSING_INFORMATION**
- ARM_TOC: **ELIGIBLE** across ['ELIGIBLE', 'ELIGIBLE', 'ELIGIBLE'] (retries 2, unresolved 2)
  - rationale (latest): The applicant’s document is a German recognized further-training certificate: "Geprüfte Wirtschaftsfachwirtin". The certificate itself states that this qualification is assigned to DQR/EQR level 6. Under the policy, advanced vocational further training assigned to at least DQR level 6 directly enables admission to the Bachelor’s degree program. The reviewer’s objection does not defeat eligibility because the document shows exactly the policy-recognized route: a German advanced vocational further-training qualification at DQR 6, not merely an unlabeled vocational certificate.
- ARM_RAG: **MANUAL_REVIEW** across ['MISSING_INFORMATION', 'MANUAL_REVIEW', 'MANUAL_REVIEW'] (retries 3, unresolved 3)
  - rationale (latest): The document proves a German advanced vocational further-training qualification ('Geprüfte Wirtschaftsfachwirtin') at DQR/EQR level 6, which normally fits the general direct-access route for professionally qualified applicants. However, the retrieved policy also contains program-specific target-group restrictions for certain Bachelor programs that can override the general route, and the applicant’s exact intended Bachelor program is only given as the generic label 'Bachelor Study Program'. Because the policy excerpts with restrictions apply to specific degree programs and the available documents do not identify whether the applicant has applied to one of those restricted programs, I cannot confidently decide eligibility from the supplied evidence alone.
- adjudication: _(fill in: which system is right, and why)_

## daniel-roth

- expected: **nan** (nan)
- rules engine: **MISSING_INFORMATION** — Academic access needs more information
- full policy workflow: **MISSING_INFORMATION**
- ARM_TOC: **CONDITIONALLY_ELIGIBLE** across ['CONDITIONALLY_ELIGIBLE', 'MISSING_INFORMATION', 'CONDITIONALLY_ELIGIBLE'] (retries 3, unresolved 3)
  - rationale (latest): The applicant does not show a direct academic school-leaving qualification, but does show the professional-route prerequisite in the policy: a recognized vocational training of at least two years at DQR level 4 ('Kaufmann für Büromanagement' with DQR/EQR level 4) and subsequent full-time professional activity from 01.08.2019 to 31.05.2023. Under the cited policy, that route does not yield unconditional direct admission; for a subject-corresponding Bachelor's program it supports admission via a successful trial study program (Probestudium), and for a non-subject-corresponding program it supports admission via the entrance examination. Because the program context is only 'Bachelor Study Program' and no subject correspondence is specified, the applicant cannot be marked plainly ELIGIBLE on the documents alone. The proper decision is conditional eligibility via the professionally qualified pathway, with the applicable conditions depending on whether the intended program is subject-corresponding or not.
- ARM_RAG: **CONDITIONALLY_ELIGIBLE** across ['CONDITIONALLY_ELIGIBLE', 'MANUAL_REVIEW', 'CONDITIONALLY_ELIGIBLE'] (retries 3, unresolved 3)
  - rationale (latest): The documents prove a recognized vocational training at DQR level 4 (Kaufmann für Büromanagement) and more than three years of subsequent full-time professional activity (01.08.2019 to 31.05.2023 at 39 hours/week). Under the policy, that route does not grant unconditional direct HZB; it allows admission only via the trial study program for a subject-corresponding Bachelor program or via the entrance examination for a non-subject-corresponding program. Since the application file does not show completion of the trial study program or the entrance examination, the applicant is not yet unconditionally eligible, but the academic route exists subject to those policy conditions.
- adjudication: _(fill in: which system is right, and why)_

## erika-musterfrau

- expected: **ELIGIBLE** (core)
- rules engine: **ELIGIBLE** — Academic access is eligible
- full policy workflow: **MANUAL_REVIEW**
- ARM_TOC: **ELIGIBLE** across ['ELIGIBLE', 'ELIGIBLE', 'ELIGIBLE'] (retries 3, unresolved 3)
  - rationale (latest): The applicant proves a qualifying academic entrance qualification for the Bachelor program: a Baden-Württemberg Fachhochschulreife. The certificate states that she fulfilled both the school-based and vocational-related parts and acquired the Fachhochschulreife for study at universities of applied sciences in Baden-Württemberg. It also contains the cited Baden-Württemberg/KMK annotations and the acceptance note that the certificate is recognized in all federal states except Bavaria and Saxony, which the policy expressly accepts as valid for Thuringia. No additional academic condition is shown in the documents.
- ARM_RAG: **ELIGIBLE** across ['ELIGIBLE', 'MANUAL_REVIEW', 'ELIGIBLE'] (retries 3, unresolved 3)
  - rationale (latest): The document proves a Baden-Württemberg general Fachhochschulreife. The certificate explicitly states that the applicant fulfilled the school-based and vocationally related parts and thereby acquired the Fachhochschulreife for study at universities of applied sciences in Baden-Württemberg. Under the compiled policy, a general Fachhochschulreife is accepted directly, and the Baden-Württemberg-specific form is accepted when the certificate confirms both parts and includes the listed KMK references, which this certificate does. The added note that it is recognized in all federal states except Bavaria and Saxony is also accepted by the policy, so no further condition is needed.
- adjudication: _(fill in: which system is right, and why)_

## katrin-vogel

- expected: **MANUAL_REVIEW** (core)
- rules engine: **MISSING_INFORMATION** — Academic access needs more information
- full policy workflow: **MISSING_INFORMATION**
- ARM_TOC: **INELIGIBLE** across ['CONDITIONALLY_ELIGIBLE', 'INELIGIBLE', 'INELIGIBLE'] (retries 3, unresolved 2)
  - rationale (latest): The documents do not prove a direct academic entrance qualification for the Bachelor program. The applicant’s vocational certificate shows a recognized apprenticeship, but it is explicitly assigned to DQR level 4, not a direct-access qualification such as Meister/DQR 6 or advanced vocational training at DQR 6. Under the policy, a DQR 4 vocational qualification with subsequent professional experience is only a basis for access via Probestudium or entrance examination; it is not itself direct eligibility. The submitted work history ends on 24.01.2023 and begins on 01.03.2020, which is about 2 years and 11 months, so the required 'at least three years' of subsequent full-time professional activity is not affirmatively proven. Because the decisive route is therefore not satisfied by the evidence, the applicant cannot be admitted on the basis of the supplied documents.
- ARM_RAG: **MANUAL_REVIEW** across ['MANUAL_REVIEW', 'MANUAL_REVIEW', 'MISSING_INFORMATION'] (retries 3, unresolved 3)
  - rationale (latest): The applicant’s documents show a recognized German vocational training at DQR level 4 and a subsequent employment period, but the record does not prove the full-time professional experience required for the direct professionally qualified route. The Arbeitsbescheinigung gives only dates and a weekly hours figure of 39.00; it does not clearly establish that the entire relevant period was full-time under the policy’s standard or how any non-work intervals were handled. Because the direct route requires at least three years of professional experience in full-time, and the evidence on duration/coverage is not sufficient to confirm that threshold, the case cannot be approved on the current record. At the same time, the documents do not positively disprove eligibility, so the correct status is missing information rather than ineligible.
- adjudication: _(fill in: which system is right, and why)_

## lena-schmidt-weber

- expected: **MISSING_INFORMATION** (derived)
- rules engine: **MISSING_INFORMATION** — Academic access needs more information
- full policy workflow: **MISSING_INFORMATION**
- ARM_TOC: **ELIGIBLE** across ['MISSING_INFORMATION', 'ELIGIBLE', 'ELIGIBLE'] (retries 3, unresolved 3)
  - rationale (latest): The submitted document proves the school-based part of the Fachhochschulreife from a Gymnasiale Oberstufe in Baden-Württemberg, and it contains the required KMK reference. Under the Baden-Württemberg FHR-from-Gymnasium route, this is a direct academic entrance qualification for Bachelor study. The document itself does not prove a full general Abitur, but that is not necessary because the Baden-Württemberg Fachhochschulreife route is independently sufficient here. No additional vocational part is evidenced on this page, but the policy route used here requires the Baden-Württemberg certificate with the proper annotation as submitted.
- ARM_RAG: **MISSING_INFORMATION** across ['MISSING_INFORMATION', 'MISSING_INFORMATION', 'MISSING_INFORMATION'] (retries 3, unresolved 3)
  - rationale (latest): The uploaded document proves only the school-based part of a Fachhochschulreife from a Gymnasiale Oberstufe. Under the cited policy, a general Fachhochschulreife is direct-access only if it is an overall certificate; if not, both the school-based and vocational parts must be submitted. Since no overall Fachhochschulreife certificate and no vocational part are visible, the academic entrance qualification cannot be confirmed on the current file. There is also no evidence of any alternative qualifying route such as Abitur, foreign equivalence, Austrian qualification, Feststellungsprüfung, or a professionally qualified access route.
- adjudication: _(fill in: which system is right, and why)_

## melina-sturm

- expected: **MISSING_INFORMATION** (derived)
- rules engine: **MISSING_INFORMATION** — Academic access needs more information
- full policy workflow: **MISSING_INFORMATION**
- ARM_TOC: **CONDITIONALLY_ELIGIBLE** across ['CONDITIONALLY_ELIGIBLE', 'MISSING_INFORMATION', 'INELIGIBLE'] (retries 3, unresolved 3)
  - rationale (latest): The supplied documents do not show any direct academic entrance qualification such as Abitur, Fachhochschulreife, foreign-equivalent higher education entrance qualification, or Meister/advanced vocational qualification at DQR 6. The only academic route evidenced is professionally qualified access: the applicant has a recognized vocational qualification at DQR level 4 ('Kaufmann für Büromanagement'), but the policy requires, for that route, both at least two years of vocational training and three years of subsequent full-time professional experience. The employment certificate shows employment from 15.02.2020 to 31.01.2023, while the vocational qualification is dated 21.06.2023, so the documented employment is not subsequent to completion. Because the policy requires subsequent experience and the evidence affirmatively shows the opposite chronology, the professionally qualified route is not satisfied. No other qualifying route is evidenced.
- ARM_RAG: **MISSING_INFORMATION** across ['INELIGIBLE', 'MISSING_INFORMATION', 'MISSING_INFORMATION'] (retries 3, unresolved 3)
  - rationale (latest): The documents do prove a completed German vocational training at DQR level 4 ('Kaufmann für Büromanagement ... dem Niveau 4 zugeordnet'). However, under the policy that alone is not a direct-access qualification. The only potentially applicable academic route is the professionally qualified route, which requires not only at least 2 years of recognized vocational training at minimum DQR level 4, but also 3 years of subsequent full-time professional activity for Probestudium or entrance examination. The uploaded employment certificate shows employment from 15.02.2020 to 31.01.2023 and 39 hours/week, which suggests relevant professional activity, but the evidence is incomplete/unreadable for the exact end date on page 2/9 and does not clearly establish whether the full 3-year post-training professional activity requirement is met and applicable in the required form. Because the decisive qualification route depends on that missing evidence, the case cannot be decided as eligible on the current record.
- adjudication: _(fill in: which system is right, and why)_

## oemer-yilmaz

- expected: **ELIGIBLE** (derived)
- rules engine: **ELIGIBLE** — Academic access is eligible
- full policy workflow: **MISSING_INFORMATION**
- ARM_TOC: **ELIGIBLE** across ['ELIGIBLE', 'ELIGIBLE', 'ELIGIBLE'] (retries 2, unresolved 2)
  - rationale (latest): The applicant has a Baden-Württemberg Fachhochschulreife certificate that expressly states both the school-based and vocational-related parts were fulfilled and that the qualification was acquired for study at universities of applied sciences in Baden-Württemberg. The certificate also contains the required annotation reference and the accepted validity wording: it says it meets recognition requirements in all states except Bavaria and Saxony, which the policy explicitly accepts as valid for Thuringia. This directly satisfies the Fachhochschulreife route for Bachelor admission.
- ARM_RAG: **ELIGIBLE** across ['ELIGIBLE', 'ELIGIBLE', 'ELIGIBLE'] (retries 3, unresolved 3)
  - rationale (latest): The uploaded document is a Baden-Württemberg Fachhochschulreife certificate. Under the policy, this qualification is accepted directly for Bachelor admission when the Baden-Württemberg FHR certificate shows the required annotations confirming the school-based and vocational-related parts and the stated KMK/Baden-Württemberg basis. The certificate text does show both that the applicant "hat die Voraussetzungen für den schulischen Teil und den berufsbezogenen Teil" and that the certificate is based on the named KMK and Kultusministerium provisions. It also states that it fulfills the requirements for recognition in all states except Bavaria and Saxony, which the policy explicitly accepts as sufficient national validity including Thuringia. No further HZB condition is required on this route, and no other criterion is more applicable than the Baden-Württemberg FHR route.
- adjudication: _(fill in: which system is right, and why)_

## stefan-brenner

- expected: **MANUAL_REVIEW** (core)
- rules engine: **MANUAL_REVIEW** — Academic access requires manual review
- full policy workflow: **MISSING_INFORMATION**
- ARM_TOC: **ELIGIBLE** across ['ELIGIBLE', 'ELIGIBLE', 'ELIGIBLE'] (retries 0, unresolved 0)
  - rationale (latest): The uploaded document is a German Meisterbrief from the Handwerkskammer Dortmund confirming a passed Meisterprüfung and the title Elektrotechnikermeister. Under the policy, a Meister qualification at least at DQR level 6 grants direct admission to the Bachelor study program. No additional conditions are stated for this route, and the document itself is sufficient evidence.
- ARM_RAG: **ELIGIBLE** across ['MISSING_INFORMATION', 'ELIGIBLE', 'ELIGIBLE'] (retries 1, unresolved 0)
  - rationale (latest): The applicant has proven a directly qualifying academic entrance route for a Bachelor program: a German Meister examination/title. The submitted Meisterbrief states that the applicant was granted the title 'Elektrotechnikermeister' on the basis of a passed Meisterprüfung. Under the policy, Meister examinations from Germany at least at DQR level 6 are treated as equivalent to the Abitur and entitle the holder to direct Bachelor admission. No additional academic conditions are stated for this route in the compiled criteria.
- adjudication: _(fill in: which system is right, and why)_

## tobias-falk

- expected: **INELIGIBLE** (core)
- rules engine: **INELIGIBLE** — Academic access requirements are not satisfied
- full policy workflow: **MISSING_INFORMATION**
- ARM_TOC: **MISSING_INFORMATION** across ['MISSING_INFORMATION', 'MISSING_INFORMATION', 'MISSING_INFORMATION'] (retries 3, unresolved 3)
  - rationale (latest): The documents prove a recognized vocational training in a recognized occupation and that the final examination was passed at DQR/EQR level 4. That satisfies the first part of the professionally qualified access route. However, for direct admission under the professionally qualified routes, the policy also requires three years of subsequent full-time professional experience, which is not evidenced here. The documents do not establish any alternative direct academic entrance qualification such as Abitur, Fachhochschulreife, Feststellungsprüfung, Meister, or DQR 6 further training. Because the applicant may still be able to qualify through a trial study program or entrance examination if the missing experience and subject-fit requirements are met, the case is not ineligible; it is incomplete.
- ARM_RAG: **MISSING_INFORMATION** across ['INELIGIBLE', 'MISSING_INFORMATION', 'MISSING_INFORMATION'] (retries 3, unresolved 2)
  - rationale (latest): The documents prove a recognized 2-year vocational training and a passed final examination, but they do not prove the additional 3 years of subsequent full-time professional experience required for the professionally qualified access routes in s005. The employment document only shows about 13 months of work after training (01.09.2021 to 05.10.2022), which is far below the policy threshold. No direct school-leaving qualification, Meister qualification, advanced vocational further training, foreign-equivalence route, or other qualifying academic entrance qualification is evidenced. Therefore academic entrance qualification cannot be established on the current file.
- adjudication: _(fill in: which system is right, and why)_

## tobias-renner

- expected: **MISSING_INFORMATION** (core)
- rules engine: **MISSING_INFORMATION** — Academic access needs more information
- full policy workflow: **MISSING_INFORMATION**
- ARM_TOC: **CONDITIONALLY_ELIGIBLE** across ['CONDITIONALLY_ELIGIBLE', 'MANUAL_REVIEW', 'MISSING_INFORMATION'] (retries 3, unresolved 3)
  - rationale (latest): The documents show a completed recognized vocational training at DQR level 4 and subsequent full-time employment, but the policy does not make that route a direct academic entrance qualification. Under the retrieved policy, such applicants are professionally qualified and may access a Bachelor's program only via a trial study program for a subject-corresponding program or via an entrance examination for a non-subject-corresponding program. Because the application file does not state the intended subject or show that one of those two access routes has been completed, academic entrance qualification cannot be confirmed from the supplied evidence.
- ARM_RAG: **CONDITIONALLY_ELIGIBLE** across ['MANUAL_REVIEW', 'CONDITIONALLY_ELIGIBLE', 'MISSING_INFORMATION'] (retries 3, unresolved 3)
  - rationale (latest): The documents prove a completed vocational training at DQR level 4 ('Kaufmann für Büromanagement') and subsequent professional activity from 01.08.2019 to 31.10.2023, so the applicant meets the basic professional-qualification inputs for the professionally qualified access routes. However, the policy requires determining whether the intended Bachelor program is subject-corresponding or subject-foreign to know whether the trial study program (Probestudium) or the entrance examination (Eingangsprüfung) applies. Because the program is only identified generically as 'Bachelor Study Program' and no subject is given, I cannot decide between those routes or conclude a completed admissible route under the policy.
- adjudication: _(fill in: which system is right, and why)_
