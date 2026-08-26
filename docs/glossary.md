# Admissions screening

This context covers the terms used to evaluate academic access for a study
application.

## Language

**Application**:
A request by one applicant for admission to one selected study program. Academic
access is evaluated for an application, not as a person-wide property.
_Avoid_: Applicant, when referring to the applicant-program pair

**Study program**:
The configured degree offering selected for an application. Its study level and
subject are trusted application context rather than applicant evidence.
_Avoid_: Admissions rule, applicant qualification

**Academic access**:
The determination that an application meets the academic requirements for its
selected study program. It does not imply that enrollment can proceed.
_Avoid_: Enrollment readiness, admission completion

**Enrollment readiness**:
The state in which academic and administrative requirements are complete enough
for enrollment to proceed. It is outside the current academic-access policy.
_Avoid_: Academic access, eligibility

**Admissions rule**:
A recognized set of requirements that can establish academic access, such as
an Abitur rule or a professional qualification rule.
_Avoid_: Pathway

**Rule result**:
The result of evaluating one admissions rule for an application.
_Avoid_: Pathway status, final result

**Application result**:
The result produced after all applicable rule results have been combined.
_Avoid_: Rule result, pathway result

**Application fact**:
A typed value or explicit unknown state reported by the extraction model for an
application. It may include an explanatory source pointer. A missing observation
is not a negative fact.
_Avoid_: Raw document text, unsupported value

**Evidence state**:
The explicit condition of an application fact: known, missing from the supplied
bundle, unreadable, or conflicting. Only a known fact has one accepted value;
known false is different from missing.
_Avoid_: Nullable value, confidence score

**Professional access candidate**:
One vocational training together with the submitted employment periods assessed
relative to that training and the selected study program. Employment duration
and subject relationship are candidate-specific rather than applicant-wide.
_Avoid_: Global work-experience summary

**Subject relationship**:
The candidate-scoped classification of how one training and its professional
experience relate to the selected study program. The extraction model reports it
as match, no match, or uncertain in the same structured response as all other facts.
_Avoid_: Program subject, training subject

**Evidence reference**:
An optional document, page, and excerpt pointer associated with an application
fact for explanation. It is a reported source location, not verified support.
_Avoid_: Verified evidence, accepted citation

**Territorial validity restriction**:
A statement on a school qualification certificate that limits the German
federal states in which the qualification is recognized.
_Avoid_: Access territory, validity area
