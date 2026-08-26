# Sample German admission documents — what each one is and conveys

Web research (2026-08-21, second pass 2026-08-22) grounding the per-document-
type extraction schemas. Local copies of the parsed PDFs are in `samples/` in
this directory. Each entry: what the document is (written so a reader who
doesn't know the German education system can follow), and what it conveys to
the screening pipeline.

## 1. Abiturzeugnis (Allgemeine Hochschulreife)

- **Official KMK nationwide template** (i.d.F. 06.06.2024):
  https://www.kmk.org/fileadmin/Dateien/veroeffentlichungen_beschluesse/1974/1974_01_08-Zeugnis-Allg-Hochschulreife.pdf
- Filled variants: Brandenburg
  (https://bravors.brandenburg.de/sixcms/media.php/andbb_lds_test_eval01.a.83.de/03-05-ZeugnisGOST-Abi-Zeugnis.pdf),
  BW Kolleg (asv.kultus-bw.de)

The German high-school diploma from a Gymnasium (the academic secondary
school) — comparable to A-levels or the IB, and _the_ classic
university-entrance qualification: 3–4 pages of grade tables (two-digit
points 00–15) ending in a total score and an average grade
(Durchschnittsnote, 1.0 = best), sealed and double-signed.
**What it conveys:** the holder has the allgemeine Hochschulreife —
the direct-access happy path of the `GERMAN_ABITUR` rule (`qualification.type =
ALLGEMEINE_HOCHSCHULREIFE`). The grades themselves don't matter for admission at IU;
what matters is the title string, the issuing school/Bundesland, and the date.
Subject naming varies per Bundesland; seals often overlap signatures.

## 2. Fachhochschulreife

- **BW full Zeugnis** (2 pages, "Muster" watermark):
  https://asv.kultus-bw.de/site/pbs-bw-rebrush2024/get/documents_E-2012870286/KULTUS.Dachmandant/KULTUS/Projekte/asv-bw/Zeugnisse/Zeugnis-Muster/BG/FH-Reife/Zeugnis_FHSR_BG.pdf
- **KMK "Bescheinigung über den schulischen Teil der Fachhochschulreife"**:
  https://www.kmk.org/fileadmin/Dateien/veroeffentlichungen_beschluesse/2008/2008_10_24-Zeugnis-FH-schul-Teil.pdf
- Bavaria variant: verkuendung-bayern.de (2236.7.2-UK-513-AE-001-A005.pdf)

The "applied-sciences entrance qualification" (colloquially _Fachabi_) — one
step below the Abitur; it opens universities of applied sciences (like IU)
rather than all universities. Uniquely, it consists of **two halves**: a
school part and a vocational part (an internship or completed
apprenticeship).

Two very different documents share this family. The **BW full Zeugnis** states
that _both_ the school part and the vocational part are fulfilled — it is a
complete FHR (`qualification.school_part_proven` and
`qualification.vocational_part_proven` both true), satisfying
`GERMAN_GENERAL_FACHHOCHSCHULREIFE` on its own. Its printed
footnote "…mit Ausnahme von Bayern und Sachsen" is exactly the validity
restriction the Leitfaden's L441–449 rule keys on. The **KMK Bescheinigung**
conveys only the _school half_: on its own it is NOT a
Hochschulzugangsberechtigung — the classifier must distinguish it from the
full Zeugnis by title, and a bundle containing only it must go down the
missing-vocational-part path (L467/L471).

## 3. Ausbildung completion certificates

"Ausbildung" is Germany's formal apprenticeship system: 2–3.5 years of
state-recognized vocational training ending in a chamber or state exam. A
completed Ausbildung is the foundation of the
`GERMAN_TRAINING_PLUS_PROFESSIONAL_EXPERIENCE` rule (training + work
experience).

### 3a. IHK Prüfungszeugnis (§ 37 BBiG) — commercial

- **Realistic filled specimen** (IHK Nord Westfalen; ihk.de needs a browser
  User-Agent, else 403):
  https://www.ihk.de/blueprint/servlet/resource/blob/5852182/529dc2f427c9ce6d441f7e0979fffae8/musterzeugnis-data.pdf
  → local copy `samples/ihk-musterzeugnis.pdf`

The exam certificate the IHK (Chamber of Commerce and Industry) issues when
an apprentice passes the final exam of a recognized occupation. **What it
conveys:** three professional-access inputs at once — the trained occupation,
the "bestanden" (passed) statement, and a printed **DQR/EQR line ("…dem Niveau 4
zugeordnet")** that feeds the `recognized_vocational_training` DQR ≥ 4
requirement directly
(DQR = the German Qualifications Framework, an 8-level scale for comparing
qualifications). Doubles as the vocational-part
proof next to a KMK school-part Bescheinigung.

### 3b. Pflege state exam (NOT IHK) — B.Sc. Pflege overlay documents

- **PflAPrV Anlage 8** (Zeugnis über die staatliche Prüfung):
  https://www.gesetze-im-internet.de/pflaprv/anlage_8.html
- **PflAPrV Anlage 13** (Erlaubnisurkunde zum Führen der Berufsbezeichnung):
  https://www.gesetze-im-internet.de/pflaprv/anlage_13.html

Pflege = nursing. Nursing training ends in a _state_ exam, not a chamber
exam. Anlage 8 is the exam certificate (word grades only, no points); Anlage
13 is the government license to carry the professional title
"Pflegefachfrau/-mann" (nurse). Applicants typically hold both. **What they
convey:** the Pflege-overlay allowlist match — and it is the **Urkunde
(Anlage 13)** that is legally decisive for the title, so the overlay's
`nursing_training_gate` should key on it, with Anlage 8 as supporting
evidence.

### 3c. Employer Ausbildungszeugnis / 3d. Gesellenbrief (HWK)

- IHK Muster (einfach/qualifiziert): ihk.de blobs 662860 / 662862 / 4165694 —
  prose letter, like an Arbeitszeugnis.
- HWK: the graded document is the **Prüfungszeugnis der Gesellenprüfung**
  (same structure as 3a); the **Gesellenbrief** proper is a decorative
  Schmuckurkunde.

Look-alike traps for the classifier. The employer's Ausbildungszeugnis is a
prose letter about _how_ the apprenticeship went — it conveys the training
period and occupation but not the pass. The Gesellenbrief (journeyman's
certificate, from the crafts chamber HWK) is an ornamental wall-hanger (name,
trade, chamber, date — no grades, no DQR line). **What they convey:** supporting
evidence only; the pipeline should expect the graded Prüfungszeugnis for the
actual training facts and not accept these substitutes silently.

## 4. Meister / Fachwirt (IHK Fortbildung, DQR 6)

- **BIBB/Europass Zeugniserläuterung Wirtschaftsfachwirt/-in**:
  https://www.bibb.de/dienst/berufesuche/de/index_berufesuche.php/certificate_supplement/de/wirtschaftsfachwirt_d.pdf
  → local copy `samples/bibb-wirtschaftsfachwirt.pdf`

The certificate for an _advanced_ professional qualification built on top of
an apprenticeship — Meister (master craftsman) or Fachwirt (certified
specialist/business administrator) — in the same IHK house format as 3a. In
the German framework these sit at **DQR level 6, the same level as a
Bachelor's degree**. **What it conveys:** one fact the whole
`GERMAN_MEISTER_OR_ADVANCED_VOCATIONAL` rule hangs on — that printed
**DQR/EQR Niveau 6 statement**, which grants direct Bachelor access. A
decorative Meisterbrief (A3, no grades) may be uploaded instead:
good for name/title/date, but the DQR line lives on the graded Zeugnis, so
its absence should yield `MANUAL_REVIEW` (`ADVANCED_VOCATIONAL_LEVEL_UNCLEAR`)
rather than eligibility.

## 5. Work-experience proofs

`GERMAN_TRAINING_PLUS_PROFESSIONAL_EXPERIENCE` requires three years (1,095
full-time days) of work experience after the apprenticeship — so the pipeline
needs documents proving _when_ and _how much_ someone worked.

### 5a. Qualifiziertes Arbeitszeugnis (prose — usually NO hours/week)

- Muster: https://www.arbeitsrechte.de/wp-content/uploads/muster-qualifiziertes-arbeitszeugnis.pdf
  and Minijob-Zentrale Muster (both in `samples/`)

The standard German employer reference letter, which every employee is
legally entitled to: 1–2 pages of famously coded evaluation prose ("stets zu
unserer vollsten Zufriedenheit" = top marks), no tables. **What it conveys:** employment period (vom–bis) and
position — but **almost never the weekly hours**, so on its own it usually
cannot evidence the 32 h/week full-time test (L766). Expect
EXPERIENCE_EVIDENCE_UNCLEAR often when this is the only experience proof; the
evaluation prose itself is irrelevant to eligibility.

### 5b. Arbeitsbescheinigung (§ 312 SGB III form — HAS hours/week)

- **Official BA form** (BA II 2, 08/2023, 9 pages):
  https://www.arbeitsagentur.de/datei/arbeitsbescheinigung_ba032120.pdf
  → local copy `samples/ba-arbeitsbescheinigung.pdf`

A numbered official form employers fill in for the Federal Employment Agency
(Arbeitsagentur) when an employment ends. **What it
conveys:** the one thing 5a lacks — field 71 certifies the **agreed weekly
hours**, plus exact employment period (field 30). This is the only standard
document that makes the 1,095-day full-time arithmetic computable without
human help; free-form employer letters modeled on its fields also occur.

## 6. German language certificates (B2)

Foreign applicants must prove German at CEFR level B2 (upper-intermediate;
C1 for a few programs). Three exam providers dominate, each with its own
score system — which is why language certificates need per-provider
extraction schemas.

### 6a. Goethe-Zertifikat B2

- Durchführungsbestimmungen (defines the Zeugnis contents):
  https://www.goethe.de/pro/relaunch/prf/de/Durchfuehrungsbestimmungen_B2.pdf
  → local copies `samples/goethe-db-b2.pdf`, `samples/goethe-b2-flyer.pdf`

The Goethe-Institut's B2 certificate. **What it conveys:** proof of the
language requirement — four modules (reading, listening, writing, speaking),
each 0–100 with pass ≥ 60 per module. **Modular trap:** a candidate may hold up to
four single-module Zeugnisse with different dates, so the engine must check
all four modules ≥ 60 possibly _across documents_, and apply the 5-year age
rule per module date.

### 6b. telc Deutsch B2

- Handbuch (scoring/weighting): telc.net → `samples/telc-b2-handbuch.pdf`

telc's equivalent certificate, one document with subtest points and a total
(pass ≥ 60 %). **What it conveys:** the same B2 proof with a different score
system (0–300 total, not per-module 0–100) — a reason language certs need
per-provider extraction schemas. telc also issues an "Ergebnismitteilung"
results letter: same content, no hologram; the classifier should treat it as
the same doc type.

### 6c. TestDaF

The university-oriented German exam. Reports **TDN levels 3/4/5 per
section** (4 sections), not points. **What it
conveys:** TDN 3 in all sections = the Leitfaden's B2 bar, TDN 4 = the C1 bar
— a third score system needing its own enum. Post-2020 certificates are
digital-only; no public Muster exists (see synthesize list).

## 7. Fachgebundene Hochschulreife (BOS Bayern)

- **Bavarian official template (Anlage 17)**, 3 pages:
  https://www.verkuendung-bayern.de/files/kwmbl/2011/07/anhang/2236.7.2-UK-513-AE-002-A002.pdf
  → local copy `samples/bos-bayern-fachgebundene-hzb.pdf`
- **xBildung Anlage 26 example** ("für andere Bewerber", 4 pages, the clearer
  of the two):
  https://xbildung.de/def/rep/by/example/Zeugnis_der_fachgebundenen_Hochschulreife_der_Beruflichen_Oberschule_fuer_andere_Bewerber.pdf
  → local copy `samples/xbildung-fachgebundene-hzb-beispiel.pdf`

The certificate of the Berufsoberschule — a vocational upper school for
people who already completed an apprenticeship — granting
_subject-restricted_ university access: the holder may study only programs
related to their training field. **What it conveys:** `hzb.type =
fachgebundene_hzb` plus the **Ausbildungsrichtung** (field of training:
Technik / Wirtschaft / Sozialwesen / Agrarwirtschaft / Gestaltung) that
decides _which_ programs the holder may study. No rule reads the
Richtung: the Leitfaden calls the DACH fachgebundene HZB uncritical (L459)
and attaches the subject-match condition only to the fachgebundene FHR
(L475). The permitted-programs catalog is printed
template prose on page 1, not a filled field (same pattern as the BW
restriction footnote). Caveat: both files are still **blank templates**
(«Profilfach 1» placeholders) — a fill script is needed before they can serve
as extraction inputs.

## 8. Gewerbeanmeldung (GewA 1) — self-employment evidence

- **Filled IHK Muster** (browser User-Agent needed):
  https://www.ihk.de/blueprint/servlet/resource/blob/2502380/5451192a5d7cae8dc3f9d7e19d983cdf/muster-gewerbeanmeldung-data.pdf
  → local copy `samples/ihk-gewerbeanmeldung.pdf`

The business-registration form every self-employed tradesperson files with
their municipality — the closest thing Germany has to a "proof of
self-employment". **What it conveys:** that a trade
was registered, by whom, and from when — the objective half of the
professional-experience rule's self-employment evidence (paired with the
affidavit, per L778–779). It says
nothing about weekly workload, which is why the affidavit is required
alongside. The Muster is already filled ("Mara Mustermann") — usable as-is.

## 9. Exmatrikulationsbescheinigung

- **Uni Saarland Muster** (real university output, "MUSTER" watermark):
  https://www.uni-saarland.de/fileadmin/upload/studieren/sim/Musterbescheinigungen/Exmatrikulationsbescheinigung_Muster_de.pdf
  → local copy `samples/uni-saarland-exmatrikulation.pdf`

A short letter confirming a student was de-registered from a university as of
a date. **What it conveys:** that prior enrollment has ended — required for
applicants who studied before (L2090; the submission-completeness checklist
was cut from prototype scope). The decision-relevant fact is just the
effective date.

## 10. Feststellungsprüfung Zeugnis

- **StudienkollegVO 2022** (Sachsen-Anhalt; scanned, OCR-noisy) contains
  "Muster des Zeugnisses über die Feststellungsprüfung" as **Anlage 2** plus
  an Ergänzungsprüfung Zeugnis Muster:
  https://www.hs-anhalt.de/fileadmin/Dateien/Studienkolleg/Downloads/StudienkollegVO_2022.pdf
  → local copy `samples/studienkollegvo-2022.pdf`

The exit-exam certificate of a Studienkolleg — the preparatory college
international students attend when their home-country school diploma alone
doesn't qualify them for German universities. **What it conveys:** the language rule's Feststellungsprüfung branch — a grade ≤ 4
counts as German proof, but only in combination with the origin-country
certificates it builds on (L572).

## 11. Reference-only finds (no visual certificate)

- `samples/at-berufsreifepruefung-db.pdf` — Austrian ministry rules for the
  Berufsreifeprüfung (Austria's vocational path to university access);
  conveys the rules and expected content, no certificate specimen.
- `samples/eu-lu-diplomes.pdf` — EU Careers 1-pager listing Luxembourg diploma
  types by grade; naming reference for the `luxembourg_diplomas` list.

## Not publicly available — synthesize

No public specimen exists for: the **Bavaria/Saxony exception addendum**
(L449), a **TestDaF Zeugnis** (digital-only since 2020), an actual
**Luxembourg diplôme de fin d'études secondaires**, and the
**self-employment affidavit** (no standard form by nature). These get
synthesized, consistent with the degrade/edit approach used for fail-path
variants. Still open, low priority: fachgebundene FHR Zeugnis (rare, nothing
surfaced), CV and Personalausweis (national ID card) specimens (CV trivially
synthesizable; the interior ministry publishes ID-card Muster images if
needed).

## Filled specimens

Blank templates are turned into filled test documents by the overlay scripts
in `scripts/` (currently `fill_kmk_fhr.py`, `fill_bw_fhr.py`). Applicant data
lives in `samples/filled-documents/<slug>.yaml`; output lands in
`samples/filled-documents/<slug>/` as a vector PDF plus a 150 dpi rasterized `-scan.pdf`
(the extraction-test input). All personal data is invented.

## Cross-cutting schema observations

1. **Identity block is universal**: Vorname/Nachname, Geburtsdatum, Geburtsort
   on every document — the join key for bundle assembly (plus fuzzy matching:
   name spellings vary across documents).
2. **Grade systems differ per family**: 0–15 points + Durchschnittsnote
   (Abitur/FHR); 0–100 + Note 1–6 with IHK band boundaries (IHK certificates);
   word grades only (Pflege); 0–100 per module (Goethe); 0–300 (telc);
   TDN 3–5 (TestDaF). One generic "grade" field would destroy information —
   per-type schemas are justified.
3. **The eligibility-critical fields** are a small subset: document title
   string (classifies HZB type, incl. "schulischer Teil" trap), **DQR-Niveau
   line** (4 = Ausbildung rule, 6 = Meister/Fachwirt rule), Ausbildungsberuf
   - "bestanden", employment vom/bis + **Stunden pro Woche** (only on
     5b-type docs), language module scores + dates, "valid for…" restriction
     strings on school certificates.
4. **OCR-relevant**: seals frequently overlap signatures/text; Arbeitszeugnis
   payloads are prose, not fields; hologram/stamp presence is a
   document-property flag, not extractable text.
5. **Fetch notes**: ihk.de, goethe.de, arbeitsagentur.de reject default HTTP
   clients (403) — use a browser User-Agent; kmk.org, gesetze-im-internet.de,
   asv.kultus-bw.de, telc.net are openly fetchable.
