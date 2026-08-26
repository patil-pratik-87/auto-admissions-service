# Retrieval quality — compile-time section selection vs ground truth

Ground truth: 10 sections opened by the rule-extractor (`rule-extractor/artifacts/navigation-trace.json`).

## ARM_TOC

- opened 10 sections over 3 turn(s), coverage_complete=True
- recall vs ground truth: **0.7** (7/10)
- precision (opened sections inside ground-truth chapters): **1.0** (10/10)
- missed ground-truth sections: ['PROOF OF LANGUAGE PROFICIENCY - GERMAN LANGUAGE SKILLS', 'MATRICULATION AFTER COMPULSORY DE-REGISTRATION IN GERMANY', 'SPECIAL REQUIREMENTS IN BA STUDY PROGRAMS - LANGUAGE PROOF - ENGLISH']

## ARM_RAG

- opened 12 sections over 3 turn(s), coverage_complete=False
- recall vs ground truth: **0.7** (7/10)
- precision (opened sections inside ground-truth chapters): **0.833** (10/12)
- missed ground-truth sections: ['PROOF OF LANGUAGE PROFICIENCY - GERMAN LANGUAGE SKILLS', 'MATRICULATION AFTER COMPULSORY DE-REGISTRATION IN GERMANY', 'SPECIAL REQUIREMENTS IN BA STUDY PROGRAMS - LANGUAGE PROOF - ENGLISH']
