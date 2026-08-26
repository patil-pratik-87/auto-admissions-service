# Walkthrough — every intermediate state

## Compile step (once per arm)

### ARM_TOC

coverage_complete=False, 43 sections opened, 22 criteria compiled

**Nav turn 1** — The core Bachelor-access rules are in the Bachelor access chapter, foreign-qualification chapter, Austria and Ukraine country-specific chapters, and the Bachelor entrance-examination chapter. Compulsory de-registration and programme-specific BA requirements may impose distinct academic eligibility conditions, so they must also be reviewed. The English-language-proof section is included only to determine whether it creates any academic route rather than a separate language/document condition.
- requested: ['s003', 's006', 's011', 's017', 's018', 's020', 's023', 's048']
- retrieved: ['ACCESS TO THE BACHELOR STUDY PROGRAM', 'GENERAL SPECIAL FEATURES OF FOREIGN QUALIFICATIONS', "ACCESS TO THE BACHELOR'S DEGREE PROGRAM FOR APPLICANTS FROM AUSTRIA", 'ADMISSION OF APPLICANTS FROM UKRAINE', 'BACHELOR ENTRANCE EXAMINATION (BACHELOR ZUGANGSPRÜFUNG)', 'MATRICULATION AFTER COMPULSORY DE-REGISTRATION IN GERMANY', 'SPECIAL REQUIREMENTS IN BA DEGREE PROGRAMS', 'SPECIAL REQUIREMENTS IN BA STUDY PROGRAMS - LANGUAGE PROOF - ENGLISH']
- coverage_complete: False

**Nav turn 2** — The remaining core Bachelor-qualification routes are the domestic school-leaving and vocational/non-Abitur routes; the operational foreign-qualification rules (Anabin and equivalence certificate); and the specific Austrian qualification classifications. The individual BA-program special-requirements sections must also be reviewed because they may impose or recognize program-specific academic/professional qualifications beyond the general HZB routes. Language-proof and document/authentication sections are excluded by the task.
- requested: ['s004', 's005', 's007', 's008', 's012', 's013', 's014', 's015', 's016', 's024', 's025', 's026', 's027', 's028', 's029', 's030', 's031', 's032', 's033', 's034', 's035', 's036', 's037', 's038', 's039', 's040', 's041', 's042', 's043', 's044', 's045', 's046', 's047']
- retrieved: ['Studying with the (Fach-) Abitur (general or subject-restricted school-leaving qualification)', 'Studying without the (Fach-)Abitur (general or subject-restricted school-leaving qualification)', 'Anabin', 'Certificate of equivalence (Äquivalenzbescheinigung)', 'General higher education entrance qualification / Matura', 'Austrian school-leaving qualifications with direct access', 'Austrian school-leaving qualifications with subject-restricted access', 'Austrian school-leaving qualifications WITHOUT entitlement to study', 'Addition in certificates from Austria', 'Degree program B.A. Betriebswirtschaftslehre – Industrial Management (Business Administration – Industrial Management)', 'Degree program B.A. Betriebswirtschaftslehre – Office Management (Business Administration – Office Management)', 'Degree program B.Sc. Diätetik (Dietetics)', 'Degree program B.Sc. Ergotherapie (Occupational Therapy)', 'Degree program B.A. Finanzmanagement für Bankkaufleute (Financial Management for Bank Clerks)', 'Degree program B.A. Gesundheitspädagogik (Health Education)', 'Degree program B.A. Heilpädagogik und Inklusion (Curative Education and Inclusion)', 'Degree program B.A. Immobilienmanagement für Immobilienkaufleute (Real Estate Management for Real Estate Clerks)', 'Degree program B.A. Kindheitspädagogik für Erzieher:innen (Childhood Education for Educators)', 'Degree program B.A. Kommunikationsdesign (Communication Design)', 'Degree program B.Sc. Logopädie (Speech Therapy)', 'Degree program B.Eng. Maschinenbau (Mechanical Engineering)', 'Degree program B.Eng. Mechatronik (Mechatronics)', 'Degree program B.A. Mediendesign (Media Design)', 'Degree program B.Sc. Pflege (Nursing)', 'Degree program B.A. Pflegepädagogik (Nursing Education)', 'Degree program B.Sc. Physician Assistant', 'Study Program B.Sc. Physiotherapie', 'Study Program B.A. Produktdesign', 'Study Program B.A. Public Management für Verwaltungsfachangestellte', 'Study Program B.A. Sozialpädagogik und Inklusion', 'Study Program B.Eng. Wirtschaftsingenieurwesen Elektrotechnik', 'Study Program B.Eng. Wirtschaftsingenieurwesen Maschinenbau', 'Study Program B.Eng. Wirtschaftsingenieurwesen Medizintechnik']
- coverage_complete: False

**Nav turn 3** — The core Bachelor-access routes, foreign-qualification rules (including Anabin/equivalence), Austria, Ukraine, the Bachelor entrance examination, and the program-specific Bachelor requirements are already covered. The only remaining country-specific Bachelor-admission-adjacent material is the Luxembourg subsection nested under German-language proficiency; opening it and its parent confirms whether it contains any academic-qualification rule rather than language evidence alone.
- requested: ['s009', 's010']
- retrieved: ['PROOF OF LANGUAGE PROFICIENCY - GERMAN LANGUAGE SKILLS', 'Luxembourg']
- coverage_complete: False

**Compiled criteria:**
- `school-hzb-general-or-subject-restricted` (s004): Qualify through a general higher education entrance qualification (Allgemeine Hochschulreife/Abitur) or a subject-restricted higher education entrance qualification (Fachgebundene Hochschulreife). A German/Austrian/Swiss subject-restricted qualification is directly acceptable; its subject restriction must be observed. A certificate marked "valid for all federal states" or "valid for Thuringia" is acceptable. A qualification annotated as recognized in all federal states except Bavaria and Saxony is also acceptable because it is valid in Thuringia.
- `foreign-subject-restricted-hzb-trial-study` (s004, s005): An applicant presenting a subject-restricted higher education entrance qualification from outside the German-speaking legal area (Germany, Austria, Switzerland) must complete a trial study program (Probestudium).
- `fachhochschulreife-general` (s004): A general Fachhochschulreife (FHR) provides direct access. Both its school-based part and vocational/job-related part must be established where they are not combined in one overall certificate.
- `fachhochschulreife-subject-restricted` (s004, s005): A subject-restricted Fachhochschulreife permits direct entry only where its school-based subject focus corresponds to the intended Bachelor program. If the intended program is outside that subject area, a trial study program is required; it may be ended early by passing the entrance examination.
- `baden-wuerttemberg-fhr-special-routes` (s004): For the Baden-Württemberg general FHR issued by upper secondary Gymnasium or general/vocational Gymnasium, direct access to all IU Bachelor programs requires certificate annotations confirming both the school-based and job-related parts and citing either the KMK Gymnasium upper-secondary/Abitur agreement of 07.07.1972 (version 18.02.2021) or the KMK vocational-program FHR agreement of 05.06.1998 (version 09.03.2001). For Berufskolleg II FHR, require the school-based qualification, assistant qualification obtained in parallel, and one of: a relevant 6-month placement; at least 2 years of relevant employment; or completed vocational training of at least 2 years outside the FHR program. For Freie Waldorfschule FHR, require the school- and job-related FHR certificate bearing the specified 30.07.2013 Baden-Württemberg Ministry ordinance annotation, plus either at least 9 months of extracurricular vocational-practical activity, or a 1-year FSJ, 1-year military/alternative service, 1-year Federal Voluntary Service, or completed vocational training/equivalent professional experience under §5(1) sentence 1 no. 2 1BKFHVO. Services of less than 1 year and continuous vocational training may count toward the practical period if practical-activity rules are met. Both Berufskolleg II and Waldorfschule routes additionally require a confirmation issued by the Baden-Württemberg Kultusministerium for an individual equivalence decision outside Baden-Württemberg.
- `rheinland-pfalz-fhr-practical-part` (s004): For a Rhineland-Palatinate general FHR, a separate Ministry recognition letter is not required if the practical part is evidenced by one of: 12 months' company placement; 12 months' FSJ or Federal Voluntary Service; completed vocational training; or 18 months' military service. Any other vocational-practical qualification requires Ministry examination of both the school-based and vocational-practical parts and a recognition letter.
- `feststellungspruefung` (s004): A successfully completed Feststellungsprüfung from another German higher education institution/university is equivalent to a subject-restricted higher education entrance qualification. It is valid only together with the underlying school certificates from the country of origin. If German was an examination subject and was passed with at least grade 4, it also evidences German at C1.
- `austria-matura-and-restricted-routes` (s011, s012, s013, s014, s015, s016): Direct access is available with an Austrian Matura from a general or vocational higher school (including HAK, HTL, BAKIP, HLWB and HBLA), an equivalent prior education recognized by the competent state authority, or one of: Diplomprüfungszeugnis, Reife- und Diplomprüfungszeugnis, general-education or vocational-education Reifeprüfungszeugnis, or Externistenreifeprüfungszeugnis. A Berufsreifeprüfungszeugnis provides subject-restricted access only with at least 2 successfully completed semesters at a higher education institution; a Studienberechtigungszeugnis also provides subject-restricted access. A Berufsreifeprüfungszeugnis with no study period does not confer study entitlement, except where it bears the quoted §1(1)–(2) Berufsreifeprüfung Act annotation confirming acquisition of rights associated with a higher-school Reifeprüfung.
- `foreign-qualification-equivalence` (s007, s008, s017, s018): For foreign admission qualifications, the educational institution and specific qualification must be evaluated in Anabin. H+ establishes equivalence; H- precludes admission; H+/- may require a trial study program at the decision of the Head of Guidelines Management. If the institution is unlisted, an equivalence letter from the competent district government may establish equivalence to a German/European qualification. Foreign vocational training may similarly be established by an equivalence certificate, for example from the IHK; Austria and Switzerland are generally recognisable as equivalent under the DACH framework. Ukrainian applicants remain subject to Anabin HZB rules; war-related unavailable accreditation evidence or non-original school/higher-education documents require individual case review. Applicants with an Anabin-confirmed indirect or indirectly subject-restricted HZB, requiring Feststellungsprüfung/Studienkolleg, may use the Bachelor entrance examination.
- `foreign-indirect-hzb-bachelor-exam` (s018): Applicants with foreign educational qualifications and Anabin-confirmed indirect or indirectly subject-restricted HZB (Feststellungsprüfung/Studienkolleg) may qualify for the intended program through the Bachelor entrance examination. They must pass, within 1 year, two Bachelor-program modules: Academic Work and a program-defined subject course. The passed course achievements are credited.
- `meister-direct-access` (s005): A German Meister examination at least DQR level 6 gives direct Bachelor access. Comparable Austrian or Swiss Meister qualifications may be accepted if equivalent to, or higher than, the German Meister at DQR 6 under the bilateral recognition agreement; no separate German professional-recognition/equivalence certificate is required.
- `advanced-vocational-qualification-direct` (s005): Direct Bachelor access is available for: (1) a German advanced vocational qualification assigned at least DQR 6; (2) a German further-training program of at least 400 teaching hours that builds on a regular training occupation; (3) a comparable Austrian/Swiss advanced qualification equivalent to or higher than German DQR 6; (4) an EU or other foreign qualification assigned at least equivalent to German DQR 6 on the EQR; or (5) a German further-training qualification regulated under BBiG §§53/54 or HwO §§42/42a with at least 400 teaching hours, which gives a general higher education entrance qualification. Subject area is irrelevant and professional experience is not required. A qualification from a non-EQR country requires individual review.
- `thuringian-equated-advanced-qualifications` (s005): Direct access is available under ThürHG §60(1) sentence 1 no. 3(d)–(e) for: specified state-recognized/certified Fachschule qualifications (educator, curative education specialist, curative education nurse, motopedic therapist, medical educator, social-work specialist, optician, family carer, business-informatics specialist, logistics specialist, home-economics operations manager, or designer), provided the applicant completed at least 2 years' vocational training before attendance and the certificate confirms conformity with the KMK Fachschulen framework agreement; auditor or tax adviser, followed by at least 2 years' relevant work; qualification for higher intermediate civil service/equivalent public-service employee education, followed by at least 2 years' relevant work; a further-training qualification of at least 400 teaching hours preceded by completed training in a recognized occupation (including the listed Fachkaufmann/Fachwirt/Betriebswirt, IT, retail, motopedagogy and pharmaceutical-representative qualifications); and the listed Verwaltungs- und Wirtschaftsakademie qualifications, provided a recognized vocational training of at least 2 years was completed before VWA study.
- `professional-training-experience-conditional-access` (s005): Applicants without a direct-access advancement qualification qualify conditionally if they have a recognized vocational training of at least 2 years at least DQR 4 and subsequently 3 years of full-time professional experience. The specified German dual-system occupations at DQR 3, each with training duration of at least 2 years, may also be considered. Comparable Austrian/Swiss training may be accepted as at least German DQR 4; EU training may be accepted when EQR-equivalent to at least German DQR 4. Full time is normally 32 hours/week; employment below 32 hours/week is counted pro rata. Contractually stipulated collective-agreement full-time employment counts as full time, subject to review where below 32 hours/week. Marginal jobs and mini-jobs normally do not count. Self-employment counts only at at least 32 hours/week.
- `professional-trial-study` (s005): The trial study route requires a recognized vocational training of at least 2 years at least DQR 4 followed by at least 3 years of full-time professional experience, and a subject-corresponding intended program. It lasts the first 2 subject semesters; part-time duration is extended proportionately. The applicant must earn at least 15 ECTS during that period. Recognised/transfer ECTS do not reduce the 15-ECTS threshold. The trial study can end early on successful completion of the entrance examination.
- `professional-entrance-examination` (s005): Applicants with a recognized vocational training of at least 2 years at least DQR 4 and subsequently at least 3 years of full-time professional experience, whose intended program does not correspond to the training/experience, must pass the entrance examination. It has 10–15 ECTS and consists of Academic Work, a program-defined subject course, and a study-aptitude test. All three must be successfully completed within 1 year. The two course achievements other than the aptitude test are credited.
- `target-group-programs-professional-eligibility` (s024, s025, s026, s027, s028, s029, s030, s031, s032, s034, s038, s039, s040, s041, s043, s044): The following programs require the stated German vocational qualification in addition to an otherwise valid entry route: Business Administration–Industrial Management requires Industriekaufmann/-frau; Business Administration–Office Management requires Kauffrau/Kaufmann für Büromanagement; Financial Management for Bank Clerks requires Bankkauffrau/-mann; Real Estate Management for Real Estate Clerks requires Immobilienkauffrau/-mann; Public Management for Administrative Clerks requires Verwaltungsfachangestellte:r; Dietetics requires Diätassistent:in; Occupational Therapy requires Ergotherapeut:in; Speech Therapy requires Logopäd:in; Physiotherapy requires Physiotherapeut:in; Nursing requires health care and nursing professional, health care and pediatric nursing professional, geriatric nurse, or Pflegefachfrau/-mann; Health Education requires occupational therapist, speech therapist, physiotherapist, dietetic assistant, medical-technical assistant, podologist, or paramedic; Nursing Education requires the listed nursing professions (including midwife), with foreign equivalent training subject to individual examination; and Physician Assistant requires at least 3 years' completed German vocational training in one of its listed eligible health professions. For these programs, either (a) Abitur/subject-restricted Abitur/FHR/subject-restricted FHR plus the required training, or (b) the required qualified training plus at least 3 years of corresponding full-time activity, is required. Route (b) still requires trial study. Subject-noncorresponding vocational training is not acceptable. Curative Education and Inclusion requires German training and further training as state-recognized Heilerziehungspfleger:in at DQR 6; Childhood Education for Educators and Social Pedagogy and Inclusion each require German training and further training as state-recognized Erzieher:in at DQR 6.
- `design-program-aptitude-examination` (s033, s037, s042): For B.A. Kommunikationsdesign, B.A. Mediendesign, and B.A. Produktdesign, applicants must successfully take and pass the design aptitude examination in addition to their HZB. It must be completed before studies begin and before any trial study or entrance examination.
- `engineering-preliminary-internship` (s035, s036, s045, s046, s047): Before study begins, B.Eng. Mechanical Engineering, B.Eng. Mechatronics, B.Eng. Industrial Engineering–Electrical Engineering, B.Eng. Industrial Engineering–Mechanical Engineering, and B.Eng. Industrial Engineering–Medical Technology require a relevant preliminary internship of 6 weeks/30 days in a subject-specific company, covering at least 3 program-relevant activity fields. Mechanical Engineering and Industrial Engineering–Mechanical Engineering use machining; assembly/testing; primary shaping/forming; and joining/separating. Mechatronics uses machining; assembly/testing; technical drawing/documentation; joining/separating; and electrical engineering/information technology. Industrial Engineering–Electrical Engineering uses its 11 listed electrical-engineering fields. Industrial Engineering–Medical Technology uses its 10 listed medical-technology fields. Equivalent preliminary internships, relevant prior knowledge from subject-appropriate vocational training, or comparable relevant professional activity may substitute; this applies also to equivalent DACH, EU, and international evidence.
- `german-language-proficiency` (s009, s010): Foreign applicants require German at least B2, normally evidenced by a certificate no more than 5 years old: TestDaF TDN3 with at least 3 points in every subsection; DSH-1; telc Deutsch B2; or ÖSD B2. B.Sc. Applied Psychology, Communication Psychology, Health Psychology, Psychology, and B.A. Applied German Studies require C1: TestDaF TDN4 with at least 4 points in every subsection; DSH-2; telc C1; or ÖSD C1. Other language evidence requires individual assessment and must state scope and level and be no more than 5 years old. German proof is waived for Luxembourg Diplôme de Fin d'Études Secondaires, Diplôme de Fin d'Études Secondaires Techniques, and Diplôme de Technicien.
- `english-language-program-proficiency` (s048): Non-native speakers entering any listed English-language Bachelor program require English at least CEFR B2 before study starts. Accepted evidence, each no more than 5 years old, is TOEFL at least 80 points, IELTS at least 6.0/10, Duolingo English Test at least 95 points, or Cambridge Certificate at least overall grade B.
- `prior-compulsory-deregistration` (s004, s020): An applicant compulsorily de-registered by another German higher education institution for violations of study/examination rules, including definitively failed examination, cannot be admitted to a program with identical academic content. The comparison is of the entire former and intended curricula; degree title and the individual failed module are not determinative.

### ARM_RAG

coverage_complete=False, 12 sections opened, 14 criteria compiled

**Nav turn 1** — The task requires an exhaustive map of undergraduate academic-access routes, so the first retrieval should seek the handbook’s core Bachelor entrance-qualification rule, its treatment of German and foreign school qualifications, and any alternative vocational/examination pathways.
- requested: ['Bachelor undergraduate academic entrance qualification all routes university entrance qualification German school leaving certificate vocational qualification entrance examination handbook', 'foreign school qualifications Bachelor entrance qualification country-specific requirements recognition direct admission preparatory course handbook', 'vocationally qualified applicants Bachelor university entrance examination entrance assessment special admission routes handbook']
- retrieved: ['Studying without the (Fach-)Abitur (general or subject-restricted school-leaving qualification)', 'General higher education entrance qualification / Matura', 'Austrian school-leaving qualifications with direct access', 'Austrian school-leaving qualifications with subject-restricted access', 'Austrian school-leaving qualifications WITHOUT entitlement to study', 'BACHELOR ENTRANCE EXAMINATION (BACHELOR ZUGANGSPRÜFUNG)', 'DOCUMENTS TO BE SUBMITTED FOR BA STUDY PROGRAMS', 'Master Zugangsprüfung (Master entrance examination)', 'ADMISSION CRITERIA MASTER APTITUDE EXAMINATION']
- coverage_complete: False

**Nav turn 2** — The retrieved material covers vocational pathways, Austrian Matura variants, and the foreign-qualification entrance examination, but not the ordinary German school-leaving routes or the handbook’s general treatment and country-specific classification of foreign school credentials. These searches target those missing academic routes and any additional non-school entrance qualification provisions.
- requested: ['Bachelor admission higher education entrance qualification German Abitur Fachabitur Fachhochschulreife subject-restricted higher education entrance qualification', 'Foreign school-leaving qualifications Bachelor direct access indirect access country-specific admission requirements Anabin Studienkolleg Feststellungsprüfung', 'Bachelor university entrance qualification alternative routes gifted examination Begabtenprüfung school qualifications international baccalaureate']
- retrieved: ['Anabin', 'General higher education entrance qualification / Matura', 'Austrian school-leaving qualifications with direct access', 'Austrian school-leaving qualifications with subject-restricted access', 'BACHELOR ENTRANCE EXAMINATION (BACHELOR ZUGANGSPRÜFUNG)', 'ADMISSION CRITERIA MASTER APTITUDE EXAMINATION']
- coverage_complete: False

**Nav turn 3** — The opened material covers vocational routes, Austrian qualifications, the foreign indirect-HZB examination, and the general Anabin principle, but not the ordinary German school-based HZB routes nor the handbook’s country-specific foreign-qualification rules. These queries seek those remaining qualification routes and the treatment of direct versus indirect/subject-restricted foreign access.
- requested: ['German school-leaving qualifications that grant direct or subject-restricted Bachelor higher-education entrance qualification: Abitur, Fachabitur, Fachhochschulreife, fachgebundene Hochschulreife', 'Foreign school-leaving qualifications for Bachelor admission: direct higher education entrance qualification, indirect higher education entrance qualification, Studienkolleg or Feststellungsprüfung, Anabin', 'Country-specific Bachelor entrance qualification requirements for foreign school certificates, including India, China, Turkey, United States, United Kingdom, International Baccalaureate and European Baccalaureate']
- retrieved: ['GENERAL SPECIAL FEATURES OF FOREIGN QUALIFICATIONS', 'Anabin', 'General higher education entrance qualification / Matura', 'Austrian school-leaving qualifications with direct access', 'Austrian school-leaving qualifications with subject-restricted access', 'Austrian school-leaving qualifications WITHOUT entitlement to study', 'BACHELOR ENTRANCE EXAMINATION (BACHELOR ZUGANGSPRÜFUNG)', 'Certifications from abroad']
- coverage_complete: False

**Compiled criteria:**
- `general-matura-or-equivalent` (s012): Qualify directly with a Matura from a general-education or vocational higher school (including HAK, HTL, BAKIP, HLWB, or HBLA), or prior education recognized as equivalent by the competent state authority.
- `austrian-direct-school-leaving` (s013): The following Austrian qualifications provide direct access: Diplomprüfungszeugnis; Reife- und Diplomprüfungszeugnis; general-education Reifeprüfungszeugnis; vocational-education Reifeprüfungszeugnis; and Externistenreifeprüfungszeugnis.
- `austrian-subject-restricted-access` (s014, s015): Berufsreifeprüfungszeugnis qualifies only where the applicant also has at least 2 successfully completed semesters at a higher-education institution. A Studienberechtigungszeugnis also provides subject-restricted access. A Berufsreifeprüfungszeugnis with no period of higher-education study does not itself confer entitlement to study.
- `foreign-anabin-equivalence` (s007): For an admission qualification obtained abroad, equivalence exists where both the higher-education institution and, especially, the specific qualification are classified H+ in Anabin. H- does not permit admission. For H+/-, the Head of Guidelines Management for Matriculation and Recognition decides whether a trial study program may be required. If the institution is not listed, consultation with that Head is required.
- `foreign-indirect-hzb-bachelor-exam` (s018): An applicant with a foreign indirect or indirectly subject-restricted HZB may qualify for the intended IU Bachelor program by passing the Bachelor entrance examination, provided Anabin evidences and confirms the indirect/indirectly subject-restricted HZB through Feststellungsprüfung (assessment examination)/Studienkolleg. The examination comprises 2 Bachelor-program modules: Academic Work and a fixed subject course for the intended program. Both must be taken and passed within 1 year.
- `meister-direct-access` (s005): A German Meister examination at at least DQR level 6 is equal to the German Abitur and gives direct Bachelor access. Comparable Meister titles from Austria or Switzerland may qualify where, under the bilateral mutual-recognition agreement, they are equivalent to or higher than the German DQR-6 Meister qualification. No additional German professional-recognition proof or EU equivalence certificate is required.
- `advanced-vocational-dqr6-direct` (s005): Direct access is available for: (1) a German advanced vocational further-training qualification assigned at least DQR level 6; (2) a German further-training program of at least 400 teaching hours that builds on a regular training occupation; (3) a comparable Austrian or Swiss further-training qualification accepted as equivalent to or higher than a German DQR-6 qualification; or (4) a comparable qualification from another EU country or elsewhere abroad whose assigned EQF level is equivalent to or higher than German DQR 6. Foreign qualifications that cannot be assigned to EQF require an individual case examination by Guidelines Management. Subject area is irrelevant, and professional experience is not required.
- `statutory-equated-further-training` (s005): The following routes are equivalent or equated to a Meister qualification under §60(1) sentence 1 no. 3(d)–(e) ThürHG: (a) state-recognized educator, curative education specialist, curative education nurse, motopedic therapist, medical educator, social-work specialist, optician, family carer, business-informatics specialist, state-certified logistics specialist, home-economics operations manager, or designer, provided a vocational training of at least 2 years was successfully completed before attendance and the qualification conforms to the Framework Agreement on Fachschulen (including the pertinent certificate annotation); (b) auditor or tax advisor, followed by at least 2 years of relevant professional activity; (c) qualification for a career in higher intermediate public service (gehobener Dienst), or equivalent employee education in public service, followed by at least 2 years of relevant professional activity; (d) a further-training qualification of at least 400 teaching hours, preceded by successfully completed vocational training in a recognized training occupation—especially Fachkaufmann, Fachwirt, Betriebswirt, Technischer Betriebswirt, certified IT business administrator, Informatiker, Betriebsinformatiker, Wirtschaftsinformatiker, retail-trade assistant, Motopädagoge, Pharmareferent, IT developer, IT project leader, IT consultant, or IT economist; or (e) a VWA qualification as Verwaltungs-Betriebswirt, Verwaltungs-Diplom-Inhaber, Betriebswirt, or Betriebswirt in a specialist-focus subject, where a recognized vocational training of at least 2 years was successfully completed before VWA training.
- `bbig-hwo-400h-general-hzb` (s005): A holder of a further-training qualification governed by examination regulations under §§53 or 54 BBiG or §§42 or 42a HwO receives a general higher-education entrance qualification if the courses comprise at least 400 teaching hours.
- `vocational-training-and-experience-eligibility` (s005): An applicant is professionally qualified for Bachelor access with a recognized vocational training of at least 2 years at at least DQR level 4, followed by 3 years of professional activity. The designated German DQR-3 dual-system occupations of at least 2 years may also be taken into account: alterations tailor; interior-construction skilled worker; mining and machinery worker; junior chemical laboratory worker; vending-machine-service specialist; gastronomy specialist; wood/building-protection specialist; courier, express and postal-services specialist; leather-processing specialist; metal-technology specialist; kitchen specialist; warehouse specialist; bicycle mechanic; building-construction skilled worker; industrial electrician; insulation skilled worker; machine and plant operator; upholstery and decoration sewer; production specialist chemistry; textile product inspector; dialogue-marketing service specialist; service driver; protection and security service worker; textile and fashion sewer; civil-engineering skilled worker; salesperson; and pre-polisher in jewelry and small-appliance manufacturing. Comparable Austrian/Swiss training may be accepted if equivalent to German DQR 4; training from other EU countries may be accepted if assigned an EQF level equivalent to German DQR 4. The route then requires either subject-corresponding trial study or a successful entrance examination for a non-corresponding program.
- `professional-experience-counting` (s005): For the vocational-training-and-experience route, full time is normally 32 hours per week; work below 32 hours per week is part time and counts proportionately. Contractually collective-agreement full-time work counts as full time; a stated full-time amount below 32 hours requires review by the Head of Guidelines Management. Marginal employment and mini-jobs normally do not count. Working-student activity and internships after completing a Bachelor may count only case by case after Guidelines Management review. Professional self-employment counts only at a scope of at least 32 hours per week.
- `subject-corresponding-trial-study` (s005): Applicants without an advancement qualification who seek a subject-corresponding program may enter through a trial study program if they have a recognized vocational training of at least 2 years at at least DQR level 4 and subsequently at least 3 years of full-time professional experience. The trial study is limited to the first 2 subject semesters and is passed only by earning at least 15 ECTS during that period. For part-time students, the maximum duration is extended proportionately. Recognized ECTS do not reduce the 15-ECTS requirement. The trial study may end early by passing the entrance examination.
- `subject-foreign-fachhochschulreife-trial-study` (s005): An applicant holding a subject-restricted Fachhochschulreife who seeks a program in a subject-foreign area must complete the trial study program; the trial study can be ended early by taking the entrance examination.
- `subject-noncorresponding-entrance-exam` (s005): An applicant with recognized vocational training of at least 2 years at at least DQR level 4 and subsequently at least 3 years of full-time professional experience may qualify for a degree program not corresponding to the vocational subject by passing the entrance examination. It has 10–15 ECTS and consists of Academic Work, a fixed subject course for the intended program, and a study-aptitude test. All 3 courses must be taken and passed within 1 year. Apart from the study-aptitude test, examination achievements are recognized.

---

# Applicant runs

## erika-musterfrau — rules engine (baseline)

final: **ELIGIBLE** (`ACADEMIC_ACCESS_ELIGIBLE`)
- headline: Academic access is eligible

---

## erika-musterfrau — ARM_RAG (repeat 0, `rag-erika-musterfrau-r0-b4cec774`)

final: **MISSING_INFORMATION** · critic: approved first pass

### 1 · evaluator (draft decision)
- status: **MISSING_INFORMATION**
- rationale: The document establishes a German Fachhochschulreife obtained at a Wirtschaftsgymnasium in Baden-Württemberg. It is not a Matura/Abitur or one of the listed Austrian direct-access certificates. The applicable policy pathway for a subject-restricted Fachhochschulreife requires trial study where the intended Bachelor program is subject-foreign, but the applied-for program is provided only as “Bachelor Study Program,” without a subject area. The certificate also does not expressly identify its Fachhochschulreife as subject-restricted. Therefore, direct eligibility or a required trial-study condition cannot be determined from the supplied evidence.
- missing_information: ['The specific intended Bachelor program/subject area, needed to assess whether it corresponds to the Wirtschaftsgymnasium/Fachhochschulreife subject area or is subject-foreign.', 'Clarification or authoritative evidence whether this Baden-Württemberg Fachhochschulreife is to be treated as a subject-restricted Fachhochschulreife under the policy.']
- assessments:
  - `NOT_FULFILLED` general-matura-or-equivalent: The submitted certificate is a Fachhochschulreife, not a Matura or documented state-recognized equivalent to a Matura.
    - evidence: Certificate heading: “Zeugnis der Fachhochschulreife”; it states access “für das Studium an Fachhochschulen in Baden-Württemberg.”
  - `NOT_RELEVANT` austrian-direct-school-leaving: The document is issued in Baden-Württemberg, Germany, rather than an Austrian school-leaving certificate of a listed type.
    - evidence: Certificate bears “Baden-Württemberg” and names Wirtschaftsgymnasium der Johann-Friedrich-Cotta-Schule Stuttgart.
  - `NOT_RELEVANT` austrian-subject-restricted-access: No Austrian Berufsreifeprüfungszeugnis or Studienberechtigungszeugnis is submitted.
    - evidence: Only a Baden-Württemberg “Zeugnis der Fachhochschulreife” is provided.
  - `NOT_RELEVANT` foreign-anabin-equivalence: This is a German school certificate, not a foreign admission qualification requiring Anabin assessment under this criterion.
    - evidence: Issuer/location shown as Baden-Württemberg, Stuttgart.
  - `NOT_RELEVANT` foreign-indirect-hzb-bachelor-exam: No foreign indirect HZB, Anabin determination, Studienkolleg/Feststellungsprüfung evidence, or Bachelor entrance-examination results are provided.
    - evidence: Submitted document is a German Fachhochschulreife certificate.
  - `NOT_RELEVANT` meister-direct-access: No Meister qualification is documented.
    - evidence: Only school-leaving certificate submitted.
  - `NOT_RELEVANT` advanced-vocational-dqr6-direct: No advanced vocational further-training qualification or DQR/EQF-level evidence is submitted.
    - evidence: Only school-leaving certificate submitted.
  - `NOT_RELEVANT` statutory-equated-further-training: No listed Meister-equated professional qualification or attached prerequisite evidence is submitted.
    - evidence: Only school-leaving certificate submitted.
  - `NOT_RELEVANT` bbig-hwo-400h-general-hzb: No BBiG/HwO-regulated further-training qualification or evidence of 400 teaching hours is submitted.
    - evidence: Only school-leaving certificate submitted.
  - `NOT_RELEVANT` vocational-training-and-experience-eligibility: No recognized vocational training or subsequent three years of professional experience is documented.
    - evidence: Only school-leaving certificate submitted.
  - `NOT_RELEVANT` professional-experience-counting: This counting rule applies only if the vocational-training-and-experience route is pursued; no employment evidence is submitted.
    - evidence: No employment contracts, references, or self-employment evidence provided.
  - `NOT_RELEVANT` subject-corresponding-trial-study: This route requires qualifying vocational training and three years of subsequent experience, neither of which is documented.
    - evidence: Only Fachhochschulreife certificate submitted.
  - `UNCLEAR` subject-foreign-fachhochschulreife-trial-study: The document proves Fachhochschulreife, but does not expressly establish that it is subject-restricted for policy purposes. Further, the intended program’s subject area is unspecified, so subject-foreign status and any resulting trial-study requirement cannot be assessed.
    - evidence: Certificate: “Fachhochschulreife für das Studium an Fachhochschulen in Baden-Württemberg”; school named “Wirtschaftsgymnasium.”
  - `NOT_RELEVANT` subject-noncorresponding-entrance-exam: This route requires qualifying vocational training and three years of subsequent professional experience; no such evidence is submitted.
    - evidence: Only Fachhochschulreife certificate submitted.

### 2 · critic lookup
- rationale: The draft assumes that the German Baden-Württemberg Fachhochschulreife may be subject-restricted and that only a subject-foreign certificate triggers trial study. The compiled criterion only states the subject-foreign rule, so the original handbook text is needed to establish the baseline admission effect of Fachhochschulreife, whether Baden-Württemberg/Wirtschaftsgymnasium qualifications are subject-restricted, and how subject correspondence is determined.
- requested: ['Bachelor admission requirements Fachhochschulreife direct admission subject-restricted Fachhochschulreife Baden-Württemberg Wirtschaftsgymnasium', '"subject-restricted Fachhochschulreife" "trial study program" subject-foreign Bachelor admission', 'Fachhochschulreife subject correspondence intended degree program trial study entrance examination handbook']

### 3 · critic review
- approve: **True**

---

## erika-musterfrau — ARM_TOC (repeat 0, `toc-erika-musterfrau-r0-37fd82b2`)

final: **MANUAL_REVIEW** · critic: approved first pass

### 1 · evaluator (draft decision)
- status: **MANUAL_REVIEW**
- rationale: The applicant presents a Baden-Württemberg Zeugnis der Fachhochschulreife that expressly confirms both the school-based and vocational components, which would ordinarily establish general Fachhochschulreife. However, the policy’s special Baden-Württemberg route requires the prescribed KMK-agreement annotation. The certificate cites the 07.07.1972 agreement in the version effective from 16.03.2023, whereas the compiled policy specifically names the version of 18.02.2021. The policy directs state clarification where the required annotation is not clearly established. A human review is therefore required to confirm that this later-version annotation satisfies the policy requirement.
- manual_review_reasons: ['Confirm whether the Baden-Württemberg certificate’s annotation citing the KMK agreement of 07.07.1972 “in der ab dem 16.03.2023 jeweils geltenden Fassung” meets the policy’s specified Baden-Württemberg FHR annotation requirement, which refers to the 18.02.2021 version.']
- assessments:
  - `NOT_RELEVANT` school-hzb-general-or-subject-restricted: The submitted certificate is a Fachhochschulreife, not an Allgemeine Hochschulreife/Abitur or Fachgebundene Hochschulreife.
    - evidence: Document title: “Zeugnis der Fachhochschulreife”.
  - `FULFILLED` fachhochschulreife-general: The certificate expressly establishes both required components of a general FHR in one overall certificate.
    - evidence: “hat die Voraussetzungen für den schulischen Teil und den berufsbezogenen Teil der Fachhochschulreife ... erfüllt” and “Fachhochschulreife ... erworben.”
  - `NOT_RELEVANT` fachhochschulreife-subject-restricted: The certificate does not state that the FHR is subject-restricted.
    - evidence: It awards “Fachhochschulreife für das Studium an Fachhochschulen in Baden-Württemberg,” without a stated subject restriction.
  - `UNCLEAR` baden-wuerttemberg-fhr-special-routes: This is a Baden-Württemberg FHR from a Wirtschaftsgymnasium and it confirms both school and vocational components. It cites the required 07.07.1972 KMK agreement, but gives a version effective 16.03.2023 rather than the 18.02.2021 version specified in the compiled criterion. Policy-directed clarification is needed.
    - evidence: “Wirtschaftsgymnasium der Johann-Friedrich-Cotta-Schule Stuttgart”; “schulischen Teil und den berufsbezogenen Teil”; KMK agreement “vom 07.07.1972 ... ab dem 16.03.2023 jeweils geltenden Fassung.”
  - `NOT_RELEVANT` rheinland-pfalz-fhr-practical-part: The certificate was issued in Baden-Württemberg, not Rhineland-Palatinate.
    - evidence: Certificate heading: “Baden-Württemberg.”
  - `NOT_RELEVANT` german-language-proficiency: This requirement applies to foreign applicants; the supplied documents do not establish that the applicant is a foreign applicant or that this condition applies.
    - evidence: The only submitted document is a German Baden-Württemberg school certificate.
  - `NOT_RELEVANT` english-language-program-proficiency: The program context does not identify this as an English-language Bachelor program.
    - evidence: Program context states only: “Bachelor Study Program.”
  - `NOT_RELEVANT` target-group-programs-professional-eligibility: No target-group-restricted Bachelor program is identified in the program context.
    - evidence: Program context states only: “Bachelor Study Program.”
  - `NOT_RELEVANT` design-program-aptitude-examination: No design program is identified in the program context.
    - evidence: Program context states only: “Bachelor Study Program.”
  - `NOT_RELEVANT` engineering-preliminary-internship: No affected engineering program is identified in the program context.
    - evidence: Program context states only: “Bachelor Study Program.”

### 2 · critic lookup
- rationale: The draft’s manual-review conclusion turns entirely on whether the Baden-Württemberg Fachhochschulreife annotation citing a later version of the 07.07.1972 KMK agreement satisfies the policy’s exact special Baden-Württemberg FHR requirement. The original text of the cited school-qualification section is needed to verify whether the 18.02.2021 reference is mandatory, illustrative, or accommodates subsequently applicable versions.
- requested: ['s004']

### 3 · critic review
- approve: **True**

---

## felix-brandt — rules engine (baseline)

final: **ELIGIBLE** (`ACADEMIC_ACCESS_ELIGIBLE`)
- headline: Academic access is eligible

---

## felix-brandt — ARM_RAG (repeat 0, `rag-felix-brandt-r0-de585a22`)

final: **ELIGIBLE** · critic: approved first pass

### 1 · evaluator (draft decision)
- status: **ELIGIBLE**
- rationale: The applicant has a German Zeugnis der Allgemeinen Hochschulreife (general Abitur) from Lessing-Gymnasium, Düsseldorf, dated 28.06.2024. It states that Felix Brandt successfully took the Abitur examination and acquired entitlement to study at a higher-education institution in Germany. This is a general higher-education entrance qualification and provides direct access to the Bachelor Study Program, with no academic conditions outstanding.
- assessments:
  - `FULFILLED` general-matura-or-equivalent: The document establishes a general German higher-education entrance qualification (Allgemeine Hochschulreife/Abitur), which is a Matura-equivalent qualifying directly for Bachelor admission.
    - evidence: Page 1: “Zeugnis der Allgemeinen Hochschulreife”; page 5: “Herr Felix Brandt hat die Berechtigung zum Studium an einer Hochschule in der Bundesrepublik Deutschland erworben.”
  - `NOT_RELEVANT` austrian-direct-school-leaving: The submitted certificate is German, issued by Lessing-Gymnasium, Düsseldorf, rather than one of the specified Austrian school-leaving qualifications.
    - evidence: Page 1 identifies “Lessing-Gymnasium, Düsseldorf”; page 5 is dated “Düsseldorf, den 28.06.2024.”
  - `NOT_RELEVANT` austrian-subject-restricted-access: No Austrian Berufsreifeprüfungszeugnis or Studienberechtigungszeugnis is submitted; the applicant instead holds a general Abitur.
    - evidence: Page 1: “Zeugnis der Allgemeinen Hochschulreife.”
  - `NOT_RELEVANT` foreign-anabin-equivalence: The qualification is a German Allgemeine Hochschulreife, not a foreign qualification requiring Anabin assessment.
    - evidence: Page 5 confirms higher-education study entitlement in the “Bundesrepublik Deutschland.”
  - `NOT_RELEVANT` foreign-indirect-hzb-bachelor-exam: There is no foreign indirect or subject-restricted HZB in the evidence; the general Abitur already confers direct access.
    - evidence: Page 1: “Zeugnis der Allgemeinen Hochschulreife”; page 5 confirms entitlement to study at a German higher-education institution.
  - `NOT_RELEVANT` meister-direct-access: No Meister qualification is evidenced, and direct eligibility is already established through the general Abitur.
    - evidence: Submitted document is an Abitur certificate.
  - `NOT_RELEVANT` advanced-vocational-dqr6-direct: No advanced vocational further-training qualification is evidenced, and direct eligibility is already established through the general Abitur.
    - evidence: Submitted document is an Abitur certificate.
  - `NOT_RELEVANT` statutory-equated-further-training: No ThürHG-equated professional qualification is evidenced, and direct eligibility is already established through the general Abitur.
    - evidence: Submitted document is an Abitur certificate.
  - `NOT_RELEVANT` bbig-hwo-400h-general-hzb: No regulated 400-hour vocational further-training qualification is evidenced, and direct eligibility is already established through the general Abitur.
    - evidence: Submitted document is an Abitur certificate.
  - `NOT_RELEVANT` vocational-training-and-experience-eligibility: No vocational-training-and-work-experience route is needed because the applicant holds a direct general higher-education entrance qualification.
    - evidence: Page 1: “Zeugnis der Allgemeinen Hochschulreife.”
  - `NOT_RELEVANT` professional-experience-counting: Professional-experience counting applies only to the vocational-training-and-experience route, which is not being relied upon.
    - evidence: Direct Abitur qualification evidenced on page 1.
  - `NOT_RELEVANT` subject-corresponding-trial-study: Trial study is not required because the applicant has direct general higher-education access.
    - evidence: Page 5: “hat die Berechtigung zum Studium an einer Hochschule in der Bundesrepublik Deutschland erworben.”
  - `NOT_RELEVANT` subject-foreign-fachhochschulreife-trial-study: The document is an Allgemeine Hochschulreife, not a subject-restricted Fachhochschulreife.
    - evidence: Page 1: “Zeugnis der Allgemeinen Hochschulreife.”
  - `NOT_RELEVANT` subject-noncorresponding-entrance-exam: The entrance-examination pathway for professionally qualified applicants is not required because direct general higher-education access is established.
    - evidence: Page 1: “Zeugnis der Allgemeinen Hochschulreife.”

### 2 · critic lookup
- rationale: The decision turns entirely on whether a German Zeugnis der Allgemeinen Hochschulreife (Abitur) is an accepted direct Bachelor entrance qualification under the original handbook. The compiled criterion describes Matura or a state-recognized equivalent but does not quote the handbook’s treatment of German Abitur, so the original language should be checked before confirming direct eligibility.
- requested: ['Bachelor admission requirements German Zeugnis der Allgemeinen Hochschulreife Abitur direct admission', 'Hochschulzugangsberechtigung Allgemeine Hochschulreife Bachelor Studium Zulassung handbook', 'Matura state-recognized equivalent Allgemeine Hochschulreife admission Bachelor']

### 3 · critic review
- approve: **True**

---

## felix-brandt — ARM_TOC (repeat 0, `toc-felix-brandt-r0-af537f2d`)

final: **MISSING_INFORMATION** · critic: retried, resolved (status before retry: ELIGIBLE)

### 1 · evaluator (draft decision)
- status: **ELIGIBLE**
- rationale: The submitted certificate establishes that Felix Brandt successfully passed the German Abitur and holds a general higher-education entrance qualification (Allgemeine Hochschulreife). It expressly states that he acquired entitlement to study at a higher education institution in Germany. This provides unrestricted direct Bachelor entry; no subject restriction or outstanding academic condition is shown for the generic Bachelor Study Program.
- assessments:
  - `FULFILLED` school-hzb-general-or-subject-restricted: The document is a German certificate of Allgemeine Hochschulreife, which is a general, unrestricted higher-education entrance qualification.
    - evidence: Certificate heading: "Zeugnis der Allgemeinen Hochschulreife"; final statement: "Herr Felix Brandt hat die Berechtigung zum Studium an einer Hochschule in der Bundesrepublik Deutschland erworben." Dated Düsseldorf, 28.06.2024.
  - `NOT_RELEVANT` fachhochschulreife-general: The applicant qualifies through the higher direct route of a general Abitur; no Fachhochschulreife route is needed.
    - evidence: "Zeugnis der Allgemeinen Hochschulreife".
  - `NOT_RELEVANT` fachhochschulreife-subject-restricted: No subject-restricted Fachhochschulreife is presented; the general Abitur independently establishes entry qualification.
    - evidence: "Zeugnis der Allgemeinen Hochschulreife" and unrestricted study entitlement statement.
  - `NOT_RELEVANT` foreign-subject-restricted-hzb-trial-study: The submitted qualification is a German general Abitur, not a foreign subject-restricted HZB.
    - evidence: Lessing-Gymnasium, Düsseldorf; "Zeugnis der Allgemeinen Hochschulreife".
  - `NOT_RELEVANT` foreign-qualification-equivalence: No foreign admission qualification requiring Anabin or equivalence assessment is relied upon.
    - evidence: German Abitur issued in Düsseldorf.
  - `NOT_RELEVANT` feststellungspruefung: No Feststellungsprüfung is presented or required because direct entry is established by the Abitur.
    - evidence: General Abitur certificate and unrestricted study entitlement statement.
  - `NOT_RELEVANT` meister-direct-access: No Meister qualification is relied upon; a direct school-HZB route is established.
    - evidence: "Zeugnis der Allgemeinen Hochschulreife".
  - `NOT_RELEVANT` advanced-vocational-qualification-direct: No advanced vocational qualification is relied upon; the applicant already holds a direct general school HZB.
    - evidence: "Zeugnis der Allgemeinen Hochschulreife".
  - `NOT_RELEVANT` professional-training-experience-conditional-access: The conditional vocational route is not needed because the applicant has a direct general Abitur.
    - evidence: Final certificate statement confirms entitlement to study at a German higher education institution.
  - `NOT_RELEVANT` target-group-programs-professional-eligibility: The stated program is a generic "Bachelor Study Program," not one of the listed target-group-restricted programs.
    - evidence: Program context: "Bachelor Study Program".
  - `NOT_RELEVANT` design-program-aptitude-examination: The program is not identified as Kommunikationsdesign, Mediendesign, or Produktdesign.
    - evidence: Program context: "Bachelor Study Program".
  - `NOT_RELEVANT` engineering-preliminary-internship: The program is not identified as one of the specified engineering programs requiring a preliminary internship.
    - evidence: Program context: "Bachelor Study Program".
  - `NOT_RELEVANT` german-language-proficiency: This criterion is expressly limited to foreign applicants. No foreign-applicant status is evidenced, and the applicant holds a German Abitur from a Düsseldorf Gymnasium.
    - evidence: Lessing-Gymnasium, Düsseldorf; German Abitur dated 28.06.2024.
  - `NOT_RELEVANT` english-language-program-proficiency: The supplied program context does not identify an English-language Bachelor program. In any event, the certificate records English at CEFR C1.
    - evidence: Page 5 language table: "Englisch 5–13 C1".
  - `NOT_RELEVANT` prior-compulsory-deregistration: There is no evidence of prior study or compulsory de-registration, and the direct Abitur route is established.
    - evidence: No prior higher-education or de-registration information appears in the submitted certificate.

### 2 · critic lookup
- rationale: The eligibility determination hinges on whether a German Allgemeine Hochschulreife provides unrestricted direct Bachelor access and whether any stated restrictions affect it. Section s004 contains the governing rule cited for that route.
- requested: ['s004']

### 3 · critic review
- approve: **False**
- objection: The ELIGIBLE conclusion with no missing information/manual review is overbroad because it treats the absence of information in the Abitur certificate as establishing that independent academic bars/prerequisites do not apply. In particular, the prior-compulsory-de-registration assessment says there is no such history merely because none appears on the school certificate. A direct Abitur establishes the HZB, but does not resolve a possible prior-study compulsory-de-registration bar. Likewise, the German-language criterion is marked NOT_RELEVANT based only on no foreign-applicant status being evidenced; a German Abitur from Düsseldorf does not itself establish that the applicant is not a foreign applicant. If foreign-applicant status applies, the policy requires the applicable German-language proof. These matters should at minimum remain unverified/missing or be referred for review rather than being affirmatively treated as inapplicable while issuing an unconditional eligibility decision.
- policy evidence: [s004], §6 ("In the case of discontinued studies at another higher education institution or when changing higher education institution to the IU") states that only applicants for whom "no admission/matriculation obstacle exists can be accepted" and directs "utmost attention" to the reason for de-registration. This is an independent limitation; [s004] also makes the general Abitur "uncritical," but that supports only the HZB route and does not eliminate the separate de-registration inquiry. For language, the compiled official criterion cites [s009]–[s010] and states that foreign applicants require B2 German (or C1 for specified programs); the draft provides no affirmative basis to determine that this applicant is outside that applicant class.

### 4 · evaluator retry (after objection)
- status: **MISSING_INFORMATION**
- rationale: The certificate proves a German Allgemeine Hochschulreife and therefore an unrestricted direct higher-education entrance qualification for the stated generic Bachelor program. However, it does not establish two independent matters that may affect admission: whether the applicant has a prior compulsory de-registration from a German higher education institution for an academically identical program, and whether the applicant is a foreign applicant subject to the German-language requirement. Absence of those facts from a school certificate cannot establish that the requirements or bar are inapplicable.
- missing_information: ['Prior higher-education-study and de-registration information sufficient to determine whether any compulsory de-registration creates the academic admission bar for an identical-content program.', 'Information establishing whether the applicant is a foreign applicant for purposes of the German-language rule. If so, German-language evidence at the applicable level (normally B2; C1 for the specified psychology/German-studies programs), or material for individual assessment of alternative German evidence, is required.']
- assessments:
  - `FULFILLED` school-hzb-general-or-subject-restricted: The document is a German general higher-education entrance qualification, with no stated subject or territorial restriction, and expressly confers entitlement to study at a German higher education institution.
    - evidence: "Zeugnis der Allgemeinen Hochschulreife" issued by Lessing-Gymnasium, Düsseldorf; page 5: "Herr Felix Brandt hat die Berechtigung zum Studium an einer Hochschule in der Bundesrepublik Deutschland erworben." Dated 28.06.2024.
  - `NOT_RELEVANT` foreign-subject-restricted-hzb-trial-study: The relied-on qualification is a German general Abitur, not a foreign subject-restricted higher-education qualification.
    - evidence: Certificate identifies Lessing-Gymnasium, Düsseldorf and is headed "Zeugnis der Allgemeinen Hochschulreife."
  - `NOT_RELEVANT` fachhochschulreife-general: The applicant relies on a general Abitur rather than a Fachhochschulreife.
    - evidence: "Zeugnis der Allgemeinen Hochschulreife."
  - `NOT_RELEVANT` fachhochschulreife-subject-restricted: No subject-restricted Fachhochschulreife is presented or needed because the general Abitur establishes the HZB route.
    - evidence: "Zeugnis der Allgemeinen Hochschulreife" and unrestricted university-study entitlement statement.
  - `NOT_RELEVANT` baden-wuerttemberg-fhr-special-routes: The certificate is a general Abitur issued in Düsseldorf, not a Baden-Württemberg FHR.
    - evidence: Lessing-Gymnasium, Düsseldorf; certificate heading "Zeugnis der Allgemeinen Hochschulreife."
  - `NOT_RELEVANT` rheinland-pfalz-fhr-practical-part: No Rhineland-Palatinate Fachhochschulreife is relied upon.
    - evidence: Submitted document is a general Abitur from Düsseldorf.
  - `NOT_RELEVANT` feststellungspruefung: No Feststellungsprüfung is presented or required because the German general Abitur establishes direct HZB.
    - evidence: Page 5 confirms university-study entitlement on the basis of the Abitur certificate.
  - `NOT_RELEVANT` austria-matura-and-restricted-routes: No Austrian qualification is presented or relied upon.
    - evidence: German Abitur certificate issued by Lessing-Gymnasium, Düsseldorf.
  - `NOT_RELEVANT` foreign-qualification-equivalence: The admission qualification relied upon is German and does not require Anabin or foreign-equivalence evaluation.
    - evidence: "Zeugnis der Allgemeinen Hochschulreife," Lessing-Gymnasium, Düsseldorf.
  - `NOT_RELEVANT` foreign-indirect-hzb-bachelor-exam: There is no foreign indirect HZB or Anabin confirmation requiring the Bachelor entrance examination.
    - evidence: Direct German general Abitur is submitted.
  - `NOT_RELEVANT` meister-direct-access: No Meister qualification is relied upon; direct access is established through the general Abitur.
    - evidence: "Zeugnis der Allgemeinen Hochschulreife."
  - `NOT_RELEVANT` advanced-vocational-qualification-direct: No advanced vocational qualification is relied upon; the applicant has a direct school-HZB route.
    - evidence: "Zeugnis der Allgemeinen Hochschulreife."
  - `NOT_RELEVANT` thuringian-equated-advanced-qualifications: No statutorily equated advanced professional qualification is presented or needed for the established Abitur route.
    - evidence: Submitted document is solely the general Abitur certificate.
  - `NOT_RELEVANT` professional-training-experience-conditional-access: The vocational-training-and-experience route is not relied upon because the general Abitur establishes direct HZB.
    - evidence: Page 5 states entitlement to study at a higher education institution in Germany.
  - `NOT_RELEVANT` professional-trial-study: No qualifying vocational-training-and-experience route is relied upon; the applicant has direct HZB through Abitur.
    - evidence: "Zeugnis der Allgemeinen Hochschulreife."
  - `NOT_RELEVANT` professional-entrance-examination: No subject-noncorresponding professional-qualification route is relied upon because direct HZB is established.
    - evidence: "Zeugnis der Allgemeinen Hochschulreife."
  - `NOT_RELEVANT` target-group-programs-professional-eligibility: The supplied program context is "Bachelor Study Program" and does not identify any target-group-restricted program listed in this criterion.
    - evidence: Program context: "Bachelor Study Program."
  - `NOT_RELEVANT` design-program-aptitude-examination: The stated program is not identified as B.A. Kommunikationsdesign, Mediendesign, or Produktdesign.
    - evidence: Program context: "Bachelor Study Program."
  - `NOT_RELEVANT` engineering-preliminary-internship: The stated program is not identified as one of the specified engineering programs requiring a preliminary internship.
    - evidence: Program context: "Bachelor Study Program."
  - `UNCLEAR` german-language-proficiency: The criterion applies to foreign applicants, but the documents do not establish whether the applicant belongs to that class. A German Abitur from Düsseldorf proves the HZB but does not itself establish applicant-status classification. If the criterion applies, the certificate shows German was an advanced-level examination subject, but it does not state a CEFR German level or one of the listed German-language certificates; alternative evidence requires individual assessment.
    - evidence: Certificate shows "Deutsch (eA)" as an Abitur examination subject (page 4), but provides CEFR levels only for English (C1) and French (B1) on page 5; no applicant-status information is provided.
  - `NOT_RELEVANT` english-language-program-proficiency: The supplied program context does not identify an English-language Bachelor program. The English-language-program criterion therefore is not shown to apply.
    - evidence: Program context: "Bachelor Study Program." Page 5 additionally records English at CEFR C1.
  - `UNCLEAR` prior-compulsory-deregistration: A direct Abitur establishes HZB but does not resolve the separate academic bar arising from a prior compulsory de-registration for an identical-content program. The school certificate contains no prior-study, de-registration, or curriculum information, so it cannot establish that no bar exists.
    - evidence: The five-page Abitur certificate records school and examination results only; it contains no information about prior higher-education study or de-registration.

### 5 · critic review of the retry
- approve: **True**

---

## jonas-krause — rules engine (baseline)

final: **MISSING_INFORMATION** (`ACADEMIC_ACCESS_MISSING_INFORMATION`)
- headline: Academic access needs more information
- missing: ['Territorial validity restriction', 'Territorial validity information', 'Proof of the vocational component']

---

## jonas-krause — ARM_RAG (repeat 0, `rag-jonas-krause-r0-4235048b`)

final: **MISSING_INFORMATION** · critic: approved first pass

### 1 · evaluator (draft decision)
- status: **MISSING_INFORMATION**
- rationale: The submitted document certifies only the school-based component of the German Fachhochschulreife ("schulischen Teil der Fachhochschulreife"). It does not establish a completed Matura/Abitur, a complete Fachhochschulreife, or another qualifying route under the supplied policy. Further academic-qualification evidence is required before eligibility can be determined.
- missing_information: ['A complete higher-education entrance qualification, such as a Matura/Abitur or complete Fachhochschulreife certificate (including any required non-school/practical component), if the applicant relies on school-leaving access.', 'If relying on subject-restricted Fachhochschulreife, evidence of its awarded subject scope and the intended program\'s subject area; the program is identified only generically as "Bachelor Study Program."', 'Alternatively, evidence for another policy route, if applicable (for example, qualifying vocational training and professional experience, Meister/further-training qualification, or a passed required entrance examination/trial study).']
- assessments:
  - `UNCLEAR` general-matura-or-equivalent: The document is not a Matura or an official recognition of equivalence. It establishes only the school-based part of Fachhochschulreife and does not establish whether the applicant holds a complete qualifying school-leaving credential through another document.
    - evidence: Page 1: "Bescheinigung über den schulischen Teil der Fachhochschulreife" and "Der Erwerb dieses Teiles der Fachhochschulreife wird bescheinigt."
  - `NOT_RELEVANT` austrian-direct-school-leaving: No Austrian school-leaving qualification is submitted.
    - evidence: The submitted certificate is from "Gesamtschule Neustadt" and is a German KMK-form certificate.
  - `NOT_RELEVANT` austrian-subject-restricted-access: No Austrian Berufsreifeprüfungszeugnis or Studienberechtigungszeugnis is submitted.
  - `NOT_RELEVANT` foreign-anabin-equivalence: The submitted document is a German school certificate; no foreign qualification or Anabin classification is submitted.
    - evidence: Page 1 cites a "Beschluss der KMK" and identifies a German-style gymnasiale Oberstufe certificate.
  - `NOT_RELEVANT` foreign-indirect-hzb-bachelor-exam: No foreign indirect HZB, Anabin confirmation, or Bachelor entrance-examination results are submitted.
  - `NOT_RELEVANT` meister-direct-access: No Meister qualification is submitted.
  - `NOT_RELEVANT` advanced-vocational-dqr6-direct: No advanced vocational further-training qualification, DQR/EQF level, or course-hour evidence is submitted.
  - `NOT_RELEVANT` statutory-equated-further-training: No listed Meister-equated professional qualification or its required prerequisites are submitted.
  - `NOT_RELEVANT` bbig-hwo-400h-general-hzb: No BBiG/HwO-regulated further-training qualification or 400-hour evidence is submitted.
  - `NOT_RELEVANT` vocational-training-and-experience-eligibility: No recognized vocational-training certificate or evidence of three years of subsequent professional activity is submitted.
  - `NOT_RELEVANT` professional-experience-counting: No employment or self-employment evidence has been submitted for counting professional experience.
  - `NOT_RELEVANT` subject-corresponding-trial-study: The vocational-training and professional-experience prerequisites for this pathway are not evidenced, and no trial-study record is submitted.
  - `UNCLEAR` subject-foreign-fachhochschulreife-trial-study: The document does not establish a complete subject-restricted Fachhochschulreife, its subject restriction, or whether the intended Bachelor program is subject-foreign. No trial-study or entrance-examination result is provided.
    - evidence: Page 1 certifies only the "schulischen Teil der Fachhochschulreife"; program context states only "Bachelor Study Program."
  - `NOT_RELEVANT` subject-noncorresponding-entrance-exam: No qualifying vocational training, three years of professional experience, or passed three-part entrance examination is submitted.

### 2 · critic lookup
- rationale: The draft turns on whether a certificate for only the school-based component of the German Fachhochschulreife is insufficient for Bachelor admission, and whether a completed Fachhochschulreife (including any practical component) gives direct or only subject-restricted access. The compiled criteria do not expressly state the handbook’s treatment of complete German Fachhochschulreife or its components, so the original provisions are needed to verify the missing-information determination and proposed pathway.
- requested: ['German Fachhochschulreife schulischer Teil praktischer Teil vollständige Fachhochschulreife Bachelor Hochschulzugang', 'Fachhochschulreife unmittelbare Zulassung Bachelor Studiengang fachgebunden fachfremd Probestudium', 'Bescheinigung über den schulischen Teil der Fachhochschulreife Hochschulzugangsberechtigung Zulassung']

### 3 · critic review
- approve: **True**

---

## jonas-krause — ARM_TOC (repeat 0, `toc-jonas-krause-r0-e8ddc548`)

final: **MISSING_INFORMATION** · critic: retried, resolved (status before retry: MISSING_INFORMATION)

### 1 · evaluator (draft decision)
- status: **MISSING_INFORMATION**
- rationale: The uploaded document establishes only the school-based part of a Fachhochschulreife. A general Fachhochschulreife provides direct access only when both the school-based and vocational/job-related components are established. No overall Fachhochschulreife certificate or evidence of the required vocational/job-related component has been supplied. The document also does not establish an Abitur or Fachgebundene Hochschulreife.
- missing_information: ['Evidence of the vocational/job-related (practical) component of the Fachhochschulreife, or an overall Fachhochschulreife certificate combining both components.', 'Alternatively, evidence of another qualifying academic entrance route, if relied upon.']
- assessments:
  - `NOT_FULFILLED` school-hzb-general-or-subject-restricted: The document is expressly a certificate for the school-based part of the Fachhochschulreife, not a general Abitur or Fachgebundene Hochschulreife.
    - evidence: "Bescheinigung über den schulischen Teil der Fachhochschulreife".
  - `UNCLEAR` fachhochschulreife-general: The school-based component is evidenced, but the required vocational/job-related component is not documented. Therefore a complete general Fachhochschulreife cannot be established.
    - evidence: The certificate states that the applicant fulfilled requirements for "den schulischen Teil der Fachhochschulreife"; no vocational/job-related component or overall FHR certificate is included.
  - `NOT_RELEVANT` fachhochschulreife-subject-restricted: The submitted certificate does not identify a subject-restricted Fachhochschulreife or state a school-based subject focus that could be matched to the intended program.
    - evidence: The document is titled "Fachhochschulreife (schulischer Teil)" and contains no subject restriction or subject-area authorization.
  - `NOT_RELEVANT` baden-wuerttemberg-fhr-special-routes: There is no indication that this is a Baden-Württemberg FHR route, Berufskolleg II qualification, or Waldorfschule qualification.
    - evidence: The document identifies "Gesamtschule Neustadt, Neustadt an der Beispiel" and contains no Baden-Württemberg-specific annotation.
  - `NOT_RELEVANT` rheinland-pfalz-fhr-practical-part: The certificate does not identify a Rhineland-Palatinate FHR route, and no practical-component evidence is submitted.
    - evidence: Only the school-based FHR certificate is provided; no practical-placement, service, vocational-training, or Ministry-recognition evidence is present.
  - `NOT_RELEVANT` feststellungspruefung: No Feststellungsprüfung certificate or underlying foreign school certificates were submitted.
  - `NOT_RELEVANT` professional-training-experience-conditional-access: No evidence of a qualifying vocational training and subsequent professional experience has been submitted.
  - `NOT_RELEVANT` professional-trial-study: No qualifying vocational training, professional experience, or evidence of subject correspondence is provided.
  - `NOT_RELEVANT` professional-entrance-examination: No qualifying vocational training/professional experience or entrance-examination results are provided.

### 2 · critic lookup
- rationale: The decision hinges on whether a certificate for only the school-based part of a Fachhochschulreife is insufficient for direct admission and whether the stated general/subject-restricted school-HZB distinctions are applied correctly. Those rules, including the relevant FHR special handling, are in the cited school-qualification section.
- requested: ['s004']

### 3 · critic review
- approve: **False**
- objection: The decision improperly treats alternative eligibility routes as NOT_FULFILLED or NOT_RELEVANT solely because the uploaded document does not evidence them. In particular, the school-based FHR certificate does not establish that the applicant lacks an Abitur/Fachgebundene Hochschulreife, a Feststellungsprüfung, or a qualifying professional route. This is internally inconsistent with the general-FHR assessment, which correctly labels the missing vocational component UNCLEAR, and with the overall MISSING_INFORMATION disposition. Absence of supporting documents may justify MISSING_INFORMATION, but not a negative or inapplicability finding about an applicant’s potential alternative route. These assessments should be UNCLEAR (or omitted pending the applicant's asserted route), rather than NOT_FULFILLED/NOT_RELEVANT on the stated reasoning.
- policy evidence: s004 §1 separately recognizes proof of Allgemeine Hochschulreife and Fachgebundene Hochschulreife as admission routes; it does not make a school-based FHR certificate evidence that either qualification is absent. s004 §2 provides that an FHR route requires proof of both the school-based and vocational parts, supporting an UNCLEAR/missing-proof conclusion for that route, not a conclusion that unrelated routes fail. s004 §5 likewise recognizes a passed Feststellungsprüfung combined with underlying foreign school certificates as another route. None of these provisions makes the nonproduction of those documents proof that the applicant does not hold them.

### 4 · evaluator retry (after objection)
- status: **MISSING_INFORMATION**
- rationale: The submitted certificate proves only that Jonas Krause fulfilled the requirements for, and acquired, the school-based part of the Fachhochschulreife. The policy requires both the school-based and vocational/practical parts to establish a Fachhochschulreife route. No overall Fachhochschulreife certificate or evidence of the vocational/practical part is supplied. The certificate also does not prove or disprove any separate entrance-qualification route; therefore those possible routes cannot be negatively decided on this record.
- missing_information: ['Evidence of the vocational/job-related (practical) component of the Fachhochschulreife, or an overall Fachhochschulreife certificate establishing both components.', 'If the applicant relies on another route, the relevant qualification evidence: e.g., an Abitur/Fachgebundene Hochschulreife certificate, a Feststellungsprüfung together with underlying foreign school certificates, or vocational qualification and employment evidence.', 'If the FHR was obtained in Baden-Württemberg or Rhineland-Palatinate, information and evidence needed for the applicable state-specific FHR recognition route.']
- assessments:
  - `UNCLEAR` school-hzb-general-or-subject-restricted: The uploaded document is not an Abitur or Fachgebundene Hochschulreife certificate. It does not, however, establish that the applicant lacks either qualification; no separate certificate is provided.
    - evidence: The document is headed “Bescheinigung über den schulischen Teil der Fachhochschulreife.”
  - `UNCLEAR` fachhochschulreife-general: The school-based component is established, but the policy requires proof of both the school-based and vocational/job-related components where no combined overall certificate is presented. The vocational/job-related component is absent from the upload.
    - evidence: “hat ... die Voraussetzungen für die Zuerkennung des schulischen Teiles der Fachhochschulreife erfüllt. Der Erwerb dieses Teiles der Fachhochschulreife wird bescheinigt.”
  - `UNCLEAR` fachhochschulreife-subject-restricted: The document does not establish a completed subject-restricted FHR, its vocational component, or a subject focus that could be compared with the intended program. It also does not prove that the applicant lacks a separate subject-restricted FHR.
    - evidence: The certificate identifies only the “schulischen Teil der Fachhochschulreife” and gives no subject-area authorization.
  - `UNCLEAR` baden-wuerttemberg-fhr-special-routes: The submitted generic KMK-form certificate does not identify the issuing federal state or contain the Baden-Württemberg-specific annotations, combined-component confirmation, or other route-specific evidence. The record does not establish whether this special route applies.
    - evidence: The certificate refers generically to “Rechtsgrundlagen des jeweiligen Landes” and contains no Baden-Württemberg Kultusministerium annotation.
  - `UNCLEAR` rheinland-pfalz-fhr-practical-part: The issuing federal state and practical component are not established. Accordingly, it cannot be determined whether a listed Rhineland-Palatinate practical alternative or a Ministry recognition letter is required and satisfied.
    - evidence: Only the school-based FHR certificate is supplied; no placement, service, vocational-training, or recognition evidence is included.
  - `UNCLEAR` feststellungspruefung: No Feststellungsprüfung certificate or underlying country-of-origin school certificates are supplied. Their absence does not prove that the applicant has not passed a Feststellungsprüfung.
  - `UNCLEAR` foreign-subject-restricted-hzb-trial-study: The record contains no foreign subject-restricted higher-education qualification and no trial-study results. It therefore cannot establish this alternative route or exclude that the applicant may rely on it.
  - `UNCLEAR` foreign-qualification-equivalence: No foreign qualification, Anabin result, or equivalence determination is supplied. The German school-based FHR certificate neither establishes nor rules out a separate foreign-equivalence route.
  - `UNCLEAR` foreign-indirect-hzb-bachelor-exam: There is no Anabin confirmation of an indirect HZB and no results for the two required Bachelor entrance-examination modules. This route is not established on the supplied record.
  - `UNCLEAR` meister-direct-access: No Meister qualification evidence is submitted. The school-based FHR certificate does not establish that the applicant does not hold a qualifying Meister certificate.
  - `UNCLEAR` advanced-vocational-qualification-direct: No advanced vocational qualification certificate, DQR/EQR assignment, or relevant course-hour evidence is supplied. A failure of this separate route cannot be inferred from the school certificate.
  - `UNCLEAR` thuringian-equated-advanced-qualifications: No evidence of one of the listed statutorily equated professional qualifications or its route-specific prerequisites is supplied. The available document does not rule out this route.
  - `UNCLEAR` professional-training-experience-conditional-access: No recognized vocational-training certificate or evidence of three full-time-year equivalents of subsequent professional experience is supplied. This prevents establishing, but does not disprove, this conditional route.
  - `UNCLEAR` professional-trial-study: The record contains no evidence of qualifying vocational training, subsequent experience, subject correspondence, or trial-study achievement. The route cannot be assessed as met or failed.
  - `UNCLEAR` professional-entrance-examination: The record contains no evidence of qualifying vocational training/experience, subject non-correspondence, or completion of the required entrance examination. The route is not established.

### 5 · critic review of the retry
- approve: **True**

---

## stefan-brenner — rules engine (baseline)

final: **MANUAL_REVIEW** (`ACADEMIC_ACCESS_MANUAL_REVIEW`)
- headline: Academic access requires manual review
- missing: ['Proof of completed prior training', 'Proof of recognized prior training', 'DQR or EQR level', 'Teaching hours']
- manual review: ['ADVANCED_VOCATIONAL_LEVEL_UNCLEAR']

---

## stefan-brenner — ARM_RAG (repeat 0, `rag-stefan-brenner-r0-f96c3360`)

final: **ELIGIBLE** · critic: approved first pass

### 1 · evaluator (draft decision)
- status: **ELIGIBLE**
- rationale: The applicant has submitted a German Handwerkskammer Meisterbrief confirming that he passed the Meister examination and is authorized to use the title “Elektrotechnikermeister.” This establishes a German Meister qualification and therefore direct Bachelor entrance access under the Meister route.
- assessments:
  - `NOT_RELEVANT` general-matura-or-equivalent: The submitted document is a Meisterbrief, not a Matura or an official recognition of a school qualification as equivalent.
    - evidence: Handwerkskammer Dortmund, “Meisterbrief.”
  - `NOT_RELEVANT` austrian-direct-school-leaving: No Austrian school-leaving qualification is submitted.
    - evidence: The sole document is issued by Handwerkskammer Dortmund and records a German Meister examination.
  - `NOT_RELEVANT` austrian-subject-restricted-access: No Austrian Berufsreifeprüfungszeugnis or Studienberechtigungszeugnis is submitted.
    - evidence: Handwerkskammer Dortmund Meisterbrief.
  - `NOT_RELEVANT` foreign-anabin-equivalence: The submitted qualification is a German Handwerkskammer Meister qualification, not a foreign school qualification requiring Anabin assessment.
    - evidence: “Handwerkskammer Dortmund”; “auf Grund der bestandenen Meisterprüfung.”
  - `NOT_RELEVANT` foreign-indirect-hzb-bachelor-exam: There is no foreign indirect HZB or Anabin/Studienkolleg evidence in the documents.
    - evidence: Handwerkskammer Dortmund Meisterbrief.
  - `FULFILLED` meister-direct-access: The certificate establishes that the applicant passed a German Meister examination and holds the title Elektrotechnikermeister. A German Meister qualification at the required level provides direct Bachelor access under this route.
    - evidence: “auf Grund der bestandenen Meisterprüfung die Befugnis, den Titel Elektrotechnikermeister zu führen”; Meisterbrief issued by Handwerkskammer Dortmund, 12 November 2021.
  - `NOT_RELEVANT` advanced-vocational-dqr6-direct: The applicable direct-access route is the specific German Meister route; no separate advanced vocational further-training qualification is submitted for assessment under this criterion.
    - evidence: Meisterbrief for “Elektrotechnikermeister.”
  - `NOT_RELEVANT` statutory-equated-further-training: This route concerns qualifications equated to a Meister qualification. The applicant has evidenced an actual Meister qualification, so the direct Meister route applies.
    - evidence: “Meisterbrief”; “bestandenen Meisterprüfung.”
  - `NOT_RELEVANT` bbig-hwo-400h-general-hzb: No documentation of a separate regulated 400-hour further-training course and its statutory examination-regulation basis is submitted; direct access is already established through the Meister route.
    - evidence: The document records a Meister examination but does not identify a 400-hour course.
  - `NOT_RELEVANT` vocational-training-and-experience-eligibility: This conditional professional-qualification route is not needed because the applicant qualifies directly through the Meister route.
    - evidence: Handwerkskammer Dortmund Meisterbrief establishing a passed Meister examination.
  - `NOT_RELEVANT` professional-experience-counting: Professional-experience counting is relevant only to the vocational-training-and-experience route, which is not required where direct Meister access is established.
    - evidence: Direct Meister qualification evidenced by the Meisterbrief.
  - `NOT_RELEVANT` subject-corresponding-trial-study: Trial study is not required because the applicant has direct access through the Meister qualification.
    - evidence: “bestandenen Meisterprüfung”; title “Elektrotechnikermeister.”
  - `NOT_RELEVANT` subject-foreign-fachhochschulreife-trial-study: No subject-restricted Fachhochschulreife is submitted, and direct Meister access applies.
    - evidence: Handwerkskammer Dortmund Meisterbrief.
  - `NOT_RELEVANT` subject-noncorresponding-entrance-exam: An entrance examination based on vocational training and experience is not required because direct Meister access is established.
    - evidence: Handwerkskammer Dortmund Meisterbrief confirming passed Meister examination.

### 2 · critic lookup
- rationale: The draft treats a German Handwerkskammer Meisterbrief for Elektrotechnikermeister as automatically meeting the Meister direct-access route, but the compiled criterion states a German Meister examination must be at least DQR level 6. Retrieve the original rule to confirm whether a standard German Meisterbrief/title alone establishes that level or whether DQR-6 evidence/verification is required, and whether any scope or program restrictions apply.
- requested: ['Bachelor admission direct access German Meisterprüfung Handwerkskammer Meisterbrief DQR level 6 Elektrotechnikermeister', '§60 ThürHG Meisterprüfung DQR Niveau 6 Hochschulzugang Handwerkskammer', 'admission guidelines Meister qualification direct university entrance DQR 6 evidence Meisterurkunde']

### 3 · critic review
- approve: **True**

---

## stefan-brenner — ARM_TOC (repeat 0, `toc-stefan-brenner-r0-6ed0f6e5`)

final: **ELIGIBLE** · critic: approved first pass

### 1 · evaluator (draft decision)
- status: **ELIGIBLE**
- rationale: The applicant has supplied a German Handwerkskammer Meisterbrief confirming that he passed the Meister examination and is entitled to use the title Elektrotechnikermeister. This meets the direct-access Meister route for a German Meister qualification at DQR level 6 or above. No program-specific restriction is stated for the generic Bachelor Study Program context.
- assessments:
  - `FULFILLED` meister-direct-access: A German Meister examination provides direct Bachelor access under this route. The Meisterbrief issued by Handwerkskammer Dortmund confirms the passed Meisterprüfung and the Elektrotechnikermeister title.
    - evidence: "auf Grund der bestandenen Meisterprüfung die Befugnis, den Titel Elektrotechnikermeister zu führen"; Handwerkskammer Dortmund, 12 November 2021.
  - `NOT_RELEVANT` advanced-vocational-qualification-direct: The applicant is already directly eligible through the specific Meister route; a separate assessment under the general advanced-vocational-qualification route is not needed.
    - evidence: Handwerkskammer Dortmund Meisterbrief for Elektrotechnikermeister.
  - `NOT_RELEVANT` professional-training-experience-conditional-access: This conditional route is for applicants without a direct-access advancement qualification. The documented Meister qualification supplies direct access.
    - evidence: Meisterbrief confirms a passed Meisterprüfung.
  - `NOT_RELEVANT` professional-trial-study: Trial study for vocational training and professional experience is not required because direct access is established through the Meister qualification.
    - evidence: Meisterbrief confirms a passed Meisterprüfung.
  - `NOT_RELEVANT` professional-entrance-examination: The vocational entrance-examination route is not required because the applicant has direct access through the Meister qualification.
    - evidence: Meisterbrief confirms a passed Meisterprüfung.
  - `NOT_RELEVANT` target-group-programs-professional-eligibility: The stated program context is a generic Bachelor Study Program, not one of the target-group-restricted programs listed in the policy.
    - evidence: Program context: "Bachelor Study Program".
  - `NOT_RELEVANT` design-program-aptitude-examination: The stated program is not identified as Kommunikationsdesign, Mediendesign, or Produktdesign.
    - evidence: Program context: "Bachelor Study Program".
  - `NOT_RELEVANT` engineering-preliminary-internship: The stated program is not identified as one of the specified engineering programs requiring a preliminary internship.
    - evidence: Program context: "Bachelor Study Program".
  - `NOT_RELEVANT` german-language-proficiency: This requirement applies to foreign applicants. The supplied academic qualification is a German Handwerkskammer Meisterbrief, and there is no evidence that the applicant is a foreign applicant to whom this criterion applies.
    - evidence: Handwerkskammer Dortmund Meisterbrief.
  - `NOT_RELEVANT` english-language-program-proficiency: There is no indication that the generic stated program is an English-language Bachelor program or that the applicant is a non-native English speaker.
    - evidence: Program context: "Bachelor Study Program".
  - `NOT_RELEVANT` prior-compulsory-deregistration: No prior compulsory de-registration or prior higher-education study information is present in the supplied document.
    - evidence: Only supplied document is the Meisterbrief.

### 2 · critic lookup
- rationale: The eligibility decision hinges on whether a German Handwerkskammer Meisterprüfung (Elektrotechnikermeister) independently confers direct Bachelor access, which must be verified in the original vocational-access rules. The rationale for treating German-language proficiency as not relevant is also questionable: holding a German Meisterbrief does not itself establish that the applicant is not a foreign applicant, so the foreign-applicant language rule should be checked. The draft also dismisses the compulsory-de-registration bar based only on absent information, so its governing section may be needed to assess whether that treatment is policy-consistent.
- requested: ['s005', 's009', 's020']

### 3 · critic review
- approve: **True**

---

## tobias-falk — rules engine (baseline)

final: **INELIGIBLE** (`ACADEMIC_ACCESS_INELIGIBLE`)
- headline: Academic access requirements are not satisfied

---

## tobias-falk — ARM_RAG (repeat 0, `rag-tobias-falk-r0-25c5cd00`)

final: **MISSING_INFORMATION** · critic: approved first pass

### 1 · evaluator (draft decision)
- status: **MISSING_INFORMATION**
- rationale: The documents establish a completed, state-recognized 36-month vocational qualification at DQR/EQF level 4. They also establish full-time employment after completion, but only from 01.09.2021 to 05.10.2022 (approximately 13 months after the 02.07.2021 qualification). They do not establish the required total of three years of subsequent professional activity, nor do they establish another direct academic entrance qualification or a completed entrance-examination/trial-study route. Absence of evidence of further employment cannot be treated as proof of ineligibility.
- missing_information: ['Employment evidence covering a total of at least three years of qualifying professional activity after completion of the vocational training, including dates and weekly hours/full-time status.', 'If relying on the vocational training and experience route: information/evidence whether the intended Bachelor program corresponds to the vocational subject, or results for the required entrance examination if it does not correspond.', 'If relying on any other route: the relevant school-leaving, higher-education entrance, advanced vocational, Meister, or foreign-qualification evidence.']
- assessments:
  - `UNCLEAR` general-matura-or-equivalent: No Matura, equivalent school-leaving certificate, or state recognition decision is provided.
  - `NOT_RELEVANT` austrian-direct-school-leaving: The submitted documents concern German IHK vocational training and employment, not an Austrian school-leaving qualification.
    - evidence: IHK Nord Westfalen documents identify a German BBiG training occupation.
  - `NOT_RELEVANT` austrian-subject-restricted-access: No Austrian Berufsreifeprüfungszeugnis or Studienberechtigungszeugnis is submitted.
  - `NOT_RELEVANT` foreign-anabin-equivalence: No foreign admission qualification or Anabin classification is submitted.
  - `NOT_RELEVANT` foreign-indirect-hzb-bachelor-exam: No foreign indirect HZB, Anabin confirmation, Studienkolleg/Feststellungsprüfung evidence, or Bachelor entrance-examination results are submitted.
  - `NOT_RELEVANT` meister-direct-access: No Meister examination certificate is submitted.
  - `NOT_RELEVANT` advanced-vocational-dqr6-direct: The submitted qualification is a regular vocational training at DQR/EQF level 4, not an advanced further-training qualification at DQR 6 or above.
    - evidence: IHK Prüfungszeugnis: "Dieser Abschluss ist im Deutschen und Europäischen Qualifikationsrahmen dem Niveau 4 zugeordnet."
  - `NOT_RELEVANT` statutory-equated-further-training: No listed Meister-equated Fachschule, professional, public-service, 400-hour further-training, or VWA qualification is documented.
  - `NOT_RELEVANT` bbig-hwo-400h-general-hzb: The documents establish a BBiG initial vocational training, not a further-training qualification governed by the specified BBiG/HwO examination regulations with at least 400 teaching hours.
    - evidence: IHK confirmation describes a "Berufsausbildungsverhältnis" from 01.08.2018 to 31.07.2021; no 400-hour further-training evidence is provided.
  - `UNCLEAR` vocational-training-and-experience-eligibility: The training prerequisite is established: it was state-recognized, lasted 36 months, and is DQR/EQF 4. The supplied employment certificate establishes only about 13 months of full-time work after qualification, not the required total of three years. Further qualifying employment is not evidenced or disproved.
    - evidence: IHK confirmation: "Ausbildungsdauer: 36 Monate" and "Abschlussprüfung bestanden am: 02.07.2021"; IHK certificate: "staatlich anerkannten Ausbildungsberuf" and "Niveau 4"; employment certificate: 01.09.2021–05.10.2022, "39,00" hours per week.
  - `UNCLEAR` professional-experience-counting: The documented employment is countable as full time because it was 39 hours weekly, but the file does not document enough subsequent employment to calculate three qualifying years.
    - evidence: Arbeitsbescheinigung, section C: employment 01.09.2021–05.10.2022; section F, field 71: "39,00" hours per week.
  - `UNCLEAR` subject-corresponding-trial-study: This route requires qualifying vocational training plus three years of subsequent full-time work and a subject-corresponding intended program. The program is only identified generically as "Bachelor Study Program"; subject correspondence and the three-year work threshold are not evidenced. No trial-study result is provided.
    - evidence: Training is DQR/EQF 4, but the only supplied post-qualification employment period is 01.09.2021–05.10.2022 at 39 hours weekly.
  - `NOT_RELEVANT` subject-foreign-fachhochschulreife-trial-study: No subject-restricted Fachhochschulreife is submitted.
  - `UNCLEAR` subject-noncorresponding-entrance-exam: The qualifying vocational training is evidenced, but three years of subsequent professional activity, a determination that the intended program is non-corresponding, and passed results for all three entrance-examination components are not provided.
    - evidence: IHK certificate establishes DQR/EQF level 4; no entrance-examination results are submitted, and the employment certificate documents only 01.09.2021–05.10.2022.

### 2 · critic lookup
- rationale: The draft correctly identifies the basic vocational-training-plus-experience route as potentially applicable, but verification requires the handbook’s precise rules on whether the three-year work period must be strictly subsequent to completion, how elapsed employment dates/hours are counted, and whether subject correspondence affects trial study versus entrance examination. The generic program label also makes the route classification uncertain.
- requested: ['Bachelor admission vocational training DQR level 4 three years professional activity after completion calculation full-time 32 hours subsequent professional experience', 'Trial study subject-corresponding vocational qualification three years professional experience Bachelor entrance examination subject-non-corresponding intended program', 'Professional qualification Bachelor admission recognized vocational training at least two years DQR 4 three years work experience entrance examination trial study']

### 3 · critic review
- approve: **True**

---

## tobias-falk — ARM_TOC (repeat 0, `toc-tobias-falk-r0-0642cf6c`)

final: **MISSING_INFORMATION** · critic: approved first pass

### 1 · evaluator (draft decision)
- status: **MISSING_INFORMATION**
- rationale: The documents establish a completed, state-recognized three-year German apprenticeship as Kaufmann für Büromanagement at DQR/EQR level 4. They also establish subsequent full-time employment in that profession from 01.09.2021 to 05.10.2022 (about 13 months at 39 hours/week). This is insufficient evidence for the vocational-access route, which requires three years of subsequent full-time-equivalent professional experience. No school higher-education entrance qualification or other direct-access qualification has been submitted. The exact intended Bachelor program is also needed to determine whether any professional route is subject-corresponding and whether a target-group restriction applies.
- missing_information: ['A school-leaving higher-education entrance qualification (e.g., Abitur, Fachgebundene Hochschulreife, or complete Fachhochschulreife), or evidence of another direct-access qualification such as a Meister or DQR-6 advanced vocational qualification.', 'Employment evidence covering at least three years of full-time-equivalent professional experience after completion of the vocational training. The submitted evidence covers only 01.09.2021–05.10.2022 at 39 hours/week.', 'The exact intended Bachelor degree program, to assess subject correspondence for the vocational route and any program-specific professional-entry requirement.']
- assessments:
  - `UNCLEAR` school-hzb-general-or-subject-restricted: No general or subject-restricted higher-education entrance certificate has been submitted.
  - `UNCLEAR` fachhochschulreife-general: No Fachhochschulreife overall certificate, or evidence of both its school-based and vocational components, has been submitted.
  - `UNCLEAR` meister-direct-access: No Meister qualification or Meister examination certificate is provided.
  - `UNCLEAR` advanced-vocational-qualification-direct: The submitted qualification is an initial vocational apprenticeship at DQR/EQR 4, not evidence of a DQR-6 or other qualifying advanced vocational qualification.
    - evidence: IHK Prüfungszeugnis: “staatlich anerkannten Ausbildungsberuf Kaufmann für Büromanagement” and “dem Niveau 4 zugeordnet.”
  - `UNCLEAR` professional-training-experience-conditional-access: The recognized training requirement is evidenced, but the documents do not establish the required three years of subsequent full-time-equivalent professional experience. The intended program is also unspecified, so the appropriate trial-study versus entrance-examination route cannot be determined.
    - evidence: IHK confirmation: training 01.08.2018–31.07.2021, “Ausbildungsdauer: 36 Monate,” examination passed 02.07.2021. Employment certificate: employment 01.09.2021–05.10.2022 as “Kaufmann für Büromanagement,” with “39,00” weekly hours.
  - `UNCLEAR` professional-trial-study: This route could apply only if the intended program corresponds to the training and subsequent experience and the applicant has three years of qualifying experience. Neither point is established on the current record.
    - evidence: Training and employment are both stated as “Kaufmann für Büromanagement”; the submitted employment period is 01.09.2021–05.10.2022.
  - `UNCLEAR` professional-entrance-examination: This route could apply if the intended program does not correspond to the training/experience, but the required three years of qualifying experience, the intended program, and a passed entrance examination are not evidenced.
    - evidence: The apprenticeship certificate establishes DQR/EQR level 4; no evidence of three years' subsequent experience or examination results is submitted.
  - `UNCLEAR` target-group-programs-professional-eligibility: The applicant holds the profession required for the specific program Business Administration–Office Management, but the supplied program context does not identify that program or any other target-group-restricted program. The further applicable route cannot therefore be assessed.
    - evidence: IHK documents identify the applicant's profession as “Kaufmann für Büromanagement”; program context states only “Bachelor Study Program.”
  - `NOT_RELEVANT` german-language-proficiency: There is no evidence that the applicant is a foreign applicant, and the intended program is not identified as one requiring C1 German.
  - `NOT_RELEVANT` english-language-program-proficiency: The supplied program context does not identify an English-language Bachelor program.
  - `NOT_RELEVANT` prior-compulsory-deregistration: No prior higher-education enrollment or compulsory de-registration is evidenced.

### 2 · critic lookup
- rationale: The decisive conclusion is that the applicant’s DQR-4 initial vocational training plus roughly 13 months of subsequent full-time work does not meet the vocational-access threshold, and that the eventual route depends on subject correspondence; these rules, including direct advanced-qualification alternatives, need verification in s005. The decision also treats school HZB/FHR as potential alternative direct-access routes, requiring s004. Because the qualification is Kaufmann für Büromanagement and the draft specifically identifies the potentially relevant target-group program Business Administration–Office Management, s025 is needed to verify that program’s additional professional-entry rule and route requirements.
- requested: ['s004', 's005', 's025']

### 3 · critic review
- approve: **True**

---
