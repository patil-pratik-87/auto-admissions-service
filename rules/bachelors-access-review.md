# Review of the Bachelor access demo policy

## Conclusion

`bachelors-access.yaml` is the policy entry point and composes five
representative access rules from namespaced modules. It covers
both groups required for the case study:

1. Applicants with a general or subject restricted Hochschulreife, or a
   general Fachhochschulreife.
2. Applicants without either qualification who rely on a Meister or advanced
   vocational qualification, or on vocational training plus professional
   experience.

The retained thresholds agree with the January 2025 IU guide. The policy is a
demo and does not define behavior for unsupported rules.

The split keeps shared evidence checks and conditions reusable while keeping
the school and professional rule groups independently reviewable. Only the
entry policy selects the active rule groups and defines final resolution.

## Retained guide rules

| Demo rule | Guide basis | Result |
| --- | --- | --- |
| German general Abitur | Page 15 | Direct access after completion and any stated territorial restriction are verified |
| Subject restricted Hochschulreife | Page 15 | Direct access for DACH qualifications and trial study outside DACH |
| German general Fachhochschulreife | Pages 15 to 16 | Direct access when both parts and any stated territorial restriction are verified |
| German Meister or advanced vocational qualification | Pages 21-24 | Direct access with an official certificate and a qualifying level or 400-hour alternative |
| German vocational training plus experience | Pages 25 and 28-30 | At least two years at DQR 4 plus three years of verified subsequent experience; trial study or entrance examination depends on subject match |

The trial-study details retained in the demo are two subject semesters and at
least 15 newly earned ECTS. The professional entrance examination is modeled as
12 months and 10-15 ECTS.

## Not implemented

Other foreign qualifications, subject restricted Fachhochschulreife,
Feststellungsprüfung, other state specific exceptions, DQR level 3 occupation
lists, and self employment evidence are not implemented. The policy does not
contain rules that detect these cases.

The outside DACH subject restricted Hochschulreife branch does not implement
the separate Anabin recognition checks for foreign qualifications.

Languages, previous study, document readiness, and program-specific conditions
are also not implemented. An academic access result from this policy is not a
final matriculation decision.

## Representative-case safety checks

- A missing average grade does not block an otherwise verified Abitur. This
  preserves the `sofia-lorenz` negative control.
- An FHR school part without a verified vocational part returns
  `MISSING_INFORMATION`, preserving the `jonas-krause` behavior.
- A DQR-6 advanced vocational certificate is directly eligible, preserving
  `claudia-siebert`.
- A decorative Meister document without evidence that it is an official
  qualifying certificate returns `MANUAL_REVIEW`, preserving `stefan-brenner`.
- At least 1,095 verified full-time-equivalent days reaches subject matching,
  preserving `daniel-roth`.
- The demo adds a review band from 1,020 through 1,094 verified days, preserving
  the required human review for `katrin-vogel`. This band is a prototype safety
  control, not a threshold stated in the guide.
- Fewer than 1,020 verified days fails the professional rule, preserving the
  decisive failure for `tobias-falk` when no other rule exists.
- Illegible dates or missing weekly hours return `MISSING_INFORMATION`,
  preserving `melina-sturm` and `tobias-renner`.

## Activation decision

Do not activate this file as production policy. Production use still requires a
schema and executable evaluator, controlled qualification lists, the deferred
rules and overlays, versioned test fixtures, and approval by policy owners.
