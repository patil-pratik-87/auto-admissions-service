# PROTOTYPE — one-off run: propose Master (M.Sc.) admission rules for human review.
# Same pipeline as rule_extractor_demo.ipynb, arms B and C only. The engine cannot
# compile Master rules (study_level domain = {BACHELOR}, fixed Bachelor rule ids),
# so generation may PROPOSE new vocabulary and the compile step documents the
# rejection instead of repairing.
import json
import os
import re
import shutil
import sys
from pathlib import Path

from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

RULES_DIR = PROJECT_ROOT / "rules"
HANDBOOK = PROJECT_ROOT / "case-study" / "IU-FS-LF-Leitfaden-Hochschulzugangsberechtigung-Stand-Januar2025.md"
OUT_DIR = Path(__file__).resolve().parent
ARTIFACTS_DIR = OUT_DIR / "master-artifacts"
ARTIFACTS_DIR.mkdir(exist_ok=True)

env_file = PROJECT_ROOT / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip('"'))

from openai import OpenAI

MODEL = os.environ.get("ADMISSIONS_OPENAI_MODEL", "gpt-5.4-mini")
client = OpenAI()

PROGRAM_DESCRIPTION = (
    "Master's degree program (M.Sc.) Computer Science at IU International University of "
    "Applied Sciences, distance learning. Extract the admission eligibility rules that "
    "determine whether an applicant may access this Master's study program."
)


def ask(instructions: str, user_input: str, schema: type[BaseModel]) -> BaseModel:
    response = client.responses.parse(
        model=MODEL, instructions=instructions, input=user_input,
        text_format=schema, store=False,
    )
    if response.status != "completed":
        raise RuntimeError(f"model response status: {response.status}")
    return response.output_parsed


def save_artifact(name: str, payload) -> None:
    (ARTIFACTS_DIR / name).write_text(json.dumps(payload, indent=2, ensure_ascii=False))


# ---------- stage 0: ToC ----------
if not HANDBOOK.exists():
    raise SystemExit(f"{HANDBOOK}\nPut the English markdown handbook at this path. It is IU material and is not in the repository: see case-study/README.md.")
handbook_lines = HANDBOOK.read_text().splitlines()
sections = []
for line_no, line in enumerate(handbook_lines):
    match = re.match(r"^(#{2,3}) (.+)$", line)
    if match:
        sections.append({"id": len(sections), "level": len(match.group(1)),
                         "title": match.group(2).strip(), "start": line_no})
for index, section in enumerate(sections):
    section["end"] = len(handbook_lines)
    for later in sections[index + 1:]:
        if later["level"] <= section["level"]:
            section["end"] = later["start"]
            break


def section_text(section_id: int) -> str:
    section = sections[section_id]
    return "\n".join(handbook_lines[section["start"]:section["end"]])


toc_listing = "\n".join(
    f"[{s['id']:>3}] {'    ' * (s['level'] - 2)}{s['title']}  ({s['end'] - s['start']} lines)"
    for s in sections
)

# ---------- stage 1: navigation ----------
class NavigationTurn(BaseModel):
    rationale: str
    open_section_ids: list[int]
    coverage_complete: bool


NAV_INSTRUCTIONS = (
    "You are the retrieval stage of an admissions rule extraction engine. "
    "You navigate a policy handbook using only its table of contents — no chunking, no embeddings. "
    "Goal: open exactly the sections needed to author machine-readable admission eligibility "
    "rules for the described study program. Each turn, request section ids to open; you will see "
    "the full text of every opened section on the next turn. Set coverage_complete=true only when "
    "the opened sections fully cover admission eligibility for the described program. "
    "Do not open sections irrelevant to eligibility (change logs, other study levels, formalities)."
)

opened: dict[int, str] = {}
navigation_trace = []
for turn in range(1, 4):
    opened_blob = "\n\n".join(
        f"=== [{sid}] {sections[sid]['title']} ===\n{text}" for sid, text in opened.items()
    ) or "(none yet)"
    nav = ask(
        NAV_INSTRUCTIONS,
        f"PROGRAM DESCRIPTION:\n{PROGRAM_DESCRIPTION}\n\n"
        f"TABLE OF CONTENTS:\n{toc_listing}\n\n"
        f"OPENED SECTIONS SO FAR:\n{opened_blob}",
        NavigationTurn,
    )
    new_ids = [i for i in nav.open_section_ids if 0 <= i < len(sections) and i not in opened]
    for sid in new_ids:
        opened[sid] = section_text(sid)
    navigation_trace.append({"turn": turn, "rationale": nav.rationale,
                             "opened": [sections[i]["title"] for i in new_ids],
                             "coverage_complete": nav.coverage_complete})
    print(f"— turn {turn} —\n  rationale: {nav.rationale}")
    for sid in new_ids:
        print(f"  opened [{sid}] {sections[sid]['title']}")
    if nav.coverage_complete and opened:
        print("  coverage declared complete")
        break

retrieved_blob = "\n\n".join(
    f"=== [{sid}] {sections[sid]['title']} ===\n{text}" for sid, text in opened.items()
)
save_artifact("navigation-trace.json", navigation_trace)
print(f"\nretrieved {len(opened)} sections, {len(retrieved_blob.splitlines())} lines total\n")

# ---------- stage 2: requirements ----------
class Citation(BaseModel):
    section_title: str
    quote: str


class Requirement(BaseModel):
    requirement_id: str
    summary: str
    conditions: str
    outcome: str
    blocking_information: str
    citations: list[Citation]


class RequirementSet(BaseModel):
    requirements: list[Requirement]


EXTRACT_INSTRUCTIONS = (
    "You extract admission eligibility requirements from policy text for later conversion into "
    "machine-readable rules. For every distinct admission path or requirement in the provided "
    "sections, record: an UPPER_SNAKE_CASE requirement_id; a one-sentence summary; the exact "
    "conditions, thresholds, and exceptions; the outcome the source prescribes when met; "
    "the information whose absence or uncertainty prevents a decision; and verbatim quotes with "
    "their section titles. Extract only what the source states — do not invent policy. "
    "Cover every admission path in the sections, and note requirements that apply only in special cases."
)

requirement_set = ask(
    EXTRACT_INSTRUCTIONS,
    f"PROGRAM DESCRIPTION:\n{PROGRAM_DESCRIPTION}\n\nRETRIEVED SECTIONS:\n{retrieved_blob}",
    RequirementSet,
)
requirements_json = requirement_set.model_dump()
save_artifact("requirements.json", requirements_json)
print(f"{len(requirement_set.requirements)} requirements extracted:")
for req in requirement_set.requirements:
    print(f"  • {req.requirement_id}: {req.summary}")
print()

# ---------- stage 3: vocabulary + mapping ----------
from app.models.results import RULE_ORDER, ApplicationStatus, RuleStatus
from app.rules_engine.compiler import _APPLICATION_FACTS, _SOURCE_ALIAS, _SOURCE_FACTS
from app.rules_engine.reason_catalog import RULE_EXPLANATIONS


def fact_entry(spec) -> dict:
    return {"type": spec.kind.__name__,
            "allowed_values": sorted(spec.domain) if spec.domain else None}


VOCAB = {
    "rule_ids": [rule.value for rule in RULE_ORDER],
    "rule_ids_note": "current engine constraint: a policy must define exactly these five BACHELOR rule ids",
    "collections": {
        name: {"select_alias": _SOURCE_ALIAS[name], "facts": {k: fact_entry(v) for k, v in facts.items()}}
        for name, facts in _SOURCE_FACTS.items()
    },
    "application_facts": {k: fact_entry(v) for k, v in _APPLICATION_FACTS.items()},
    "operators": ["eq", "in", "gte", "lt", "all_of", "any_of", "ref"],
    "rule_statuses": [status.value for status in RuleStatus],
    "application_statuses": [status.value for status in ApplicationStatus],
    "reason_codes": {code: RULE_EXPLANATIONS[code] for code in sorted(RULE_EXPLANATIONS)},
}
VOCAB_TEXT = json.dumps(VOCAB, indent=1)


class RequirementMapping(BaseModel):
    requirement_id: str
    supported: bool
    target_rule_id: str | None
    facts_used: list[str]
    notes: str
    unsupported_reason: str | None


class MappingReport(BaseModel):
    mappings: list[RequirementMapping]


MAPPING_INSTRUCTIONS = (
    "You decide, for each extracted admission requirement, whether the deterministic rule engine "
    "can express it with its FIXED vocabulary (given below as JSON). The vocabulary was built for "
    "BACHELOR admissions, so expect most MASTER requirements to be unsupported. For unsupported "
    "requirements set supported=false and state precisely which engine extension would be needed. "
    "Never force a requirement onto facts that do not actually capture its meaning."
)

mapping_report = ask(
    MAPPING_INSTRUCTIONS,
    f"ENGINE VOCABULARY (JSON):\n{VOCAB_TEXT}\n\n"
    f"EXTRACTED REQUIREMENTS (JSON):\n{json.dumps(requirements_json, indent=1)}",
    MappingReport,
)
mapping_json = mapping_report.model_dump()
save_artifact("mapping.json", mapping_json)
unsupported = [m for m in mapping_report.mappings if not m.supported]
print(f"mapping: {len(mapping_report.mappings) - len(unsupported)} supported, "
      f"{len(unsupported)} unsupported (see master-artifacts/mapping.json)\n")

# ---------- stage 4: generation, arms B and C ----------
class GeneratedFile(BaseModel):
    path: str
    content: str


class ProposedRulePackage(BaseModel):
    files: list[GeneratedFile]
    proposed_extensions: list[str]


SPEC_TEXT = (PROJECT_ROOT / "rules" / "README.md").read_text()
SCAFFOLD_FILES = {
    name: (RULES_DIR / name).read_text()
    for name in ("rule-statuses.yaml", "application-statuses.yaml")
}
FEWSHOT_FILES = {
    name: (RULES_DIR / name).read_text()
    for name in ("bachelors-access.yaml", "school-access-rules.yaml",
                 "professional-access-rules.yaml", "common/requirements.yaml",
                 "common/conditions.yaml")
}
EXPECTED_FILES = {"masters-access.yaml", "master-access-rules.yaml",
                  "common/requirements.yaml", "common/conditions.yaml"}
POLICY_SKELETON = r"""
# ============ SKELETON 1: policy entry file ============
dsl_version: "1.3"

policy:
  id: <POLICY_ID>
  version: "<version-string>"

  applies_when:
    fact: application.study_level
    eq: <STUDY_LEVEL_VALUE>

  sources:
    - file: <relative-path-to-source-document>
      section: <SECTION TITLE>
      subsections:
        - <Subsection title>

  imports:
    - namespace: rule_statuses
      file: rule-statuses.yaml
    - namespace: application_statuses
      file: application-statuses.yaml
    - namespace: requirements
      file: common/requirements.yaml
    - namespace: <module_namespace>
      file: <rule-module-file.yaml>

  evaluation:
    rule_groups:
      - include: <module_namespace>.<EXPORTED_RULE_GROUP_NAME>

  resolution:
    first_match:
      - when_any_rule:
          ref: rule_statuses.<RULE_STATUS>
        application_status:
          ref: application_statuses.<APPLICATION_STATUS>
      # ...one case per resolution priority, in order...
      - when_all_applicable_rules:
          ref: rule_statuses.<RULE_STATUS>
        application_status:
          ref: application_statuses.<APPLICATION_STATUS>
      - when_no_recognized_rule: true
        application_status:
          ref: application_statuses.<APPLICATION_STATUS>

# ============ SKELETON 2: rule module file (imported by the policy) ============
dsl_version: "1.3"

module:
  id: <MODULE_ID>
  version: "<version-string>"
  imports:
    - namespace: rule_statuses
      file: rule-statuses.yaml
    - namespace: conditions
      file: common/conditions.yaml
  requires_namespaces:
    - requirements

  exports:
    <RULE_GROUP_NAME>:
      id: <RULE_GROUP_NAME>
      rules:
        # body form 1: require + result
        - id: <RULE_ID>
          select:
            from: <collection_name>
            as: <collection_alias>
            where:
              fact: <alias>.<fact_name>
              eq: <VALUE>
          applicability:            # optional
            require:
              ref: requirements.<exported_requirement_name>
            result:
              not_applicable:
                status:
                  ref: rule_statuses.<RULE_STATUS>
                reason_code: <REASON_CODE>
              unknown:
                status:
                  ref: rule_statuses.<RULE_STATUS>
                reason_code: <REASON_CODE>
          require:
            all_of:
              - ref: requirements.<exported_requirement_name>
              - fact: <alias>.<fact_name>
                eq: <VALUE>
          result:
            satisfied:
              status:
                ref: rule_statuses.<RULE_STATUS>
              reason_code: <REASON_CODE>
            not_satisfied:
              status:
                ref: rule_statuses.<RULE_STATUS>
              reason_code: <REASON_CODE>
            unknown:
              status:
                ref: rule_statuses.<RULE_STATUS>
              reason_code: <REASON_CODE>

        # body form 2: ordered branches
        - id: <RULE_ID>
          select:
            from: <collection_name>
            as: <collection_alias>
            where:
              fact: <alias>.<fact_name>
              eq: <VALUE>
          branches:
            first_match:
              - when:
                  all_of:
                    - fact: <alias>.<fact_name>
                      eq: <VALUE>
                    - ref: requirements.<exported_requirement_name>
                result:
                  status:
                    ref: rule_statuses.<RULE_STATUS>
                  reason_code: <REASON_CODE>
                  condition: conditions.<CONDITION_NAME>   # only on conditional results
            unknown:
              result:
                status:
                  ref: rule_statuses.<RULE_STATUS>
                reason_code: <REASON_CODE>
            otherwise:
              result:
                status:
                  ref: rule_statuses.<RULE_STATUS>
                reason_code: <REASON_CODE>

# ============ SKELETON 3: shared definitions module (common/requirements.yaml and common/conditions.yaml) ============
dsl_version: "1.3"

module:
  id: <MODULE_ID>
  version: "<version-string>"

  exports:
    # in common/requirements.yaml: exported names are lowercase expressions
    <exported_requirement_name>:
      fact: <alias>.<fact_name>
      eq: <VALUE>
    <another_requirement_name>:
      any_of:
        - fact: <alias>.<fact_name>
          eq: <VALUE>
        - fact: <alias>.<fact_name>
          in:
            - <VALUE>
            - <VALUE>
    # in common/conditions.yaml: exported names are UPPERCASE, free-form parameter mappings
    # <CONDITION_NAME>:
    #   <parameter>: <value>
"""


def build_instructions(arm: str) -> str:
    scaffold_blob = "\n\n".join(
        f"--- {name} (provided verbatim) ---\n{text}" for name, text in SCAFFOLD_FILES.items()
    )
    parts = [
        "You are the rule authoring stage of an admissions rule extraction engine. From the "
        "extracted requirements and their vocabulary mapping, author a PROPOSED DSL 1.3 rule "
        "package for MASTER admissions. The current engine only supports BACHELOR vocabulary, "
        "so this package is for HUMAN REVIEW, not compilation.",
        f"THE DSL SPECIFICATION:\n{SPEC_TEXT}",
        f"THE CURRENT (BACHELOR-ERA) ENGINE VOCABULARY (JSON):\n{VOCAB_TEXT}",
        f"SCAFFOLD FILES ALREADY PRESENT IN THE PACKAGE — import them, never regenerate them:\n{scaffold_blob}",
        "REQUIREMENTS FOR THE PROPOSED PACKAGE:\n"
        "- Produce exactly these files: " + ", ".join(sorted(EXPECTED_FILES)) + "\n"
        "- The policy file is masters-access.yaml with policy id IU_MASTER_ACCESS, "
        "applies_when application.study_level eq MASTER, and version \"0.1.0-proposed\".\n"
        "- You MAY propose new rule ids, facts, collections, enum values, and reason codes where "
        "MASTER admissions need them — follow the naming style of the existing vocabulary.\n"
        "- Every proposed vocabulary item that does not exist in the current engine must appear in "
        "proposed_extensions as one line each: '<kind>: <name> — <why needed>' (kinds: rule_id, "
        "collection, fact, enum_value, reason_code, condition, operator).\n"
        "- Keep every structural DSL rule: explicit satisfied/not_satisfied/unknown results, "
        "unknown and otherwise in every branch group, resolution first_match ending with "
        "when_no_recognized_rule, sources recorded with file/section/subsections.\n"
        "- Encode only what the handbook states; unclear or conflicting source text becomes "
        "MANUAL_REVIEW outcomes, not invented policy.",
    ]
    if arm == "B":
        fewshot_blob = "\n\n".join(f"--- {name} ---\n{text}" for name, text in FEWSHOT_FILES.items())
        parts.append(
            "REFERENCE IMPLEMENTATION (hand-authored BACHELOR files; a different program — "
            f"use only as structure and style examples):\n{fewshot_blob}"
        )
    if arm == "C":
        parts.append(
            "FILE STRUCTURE SKELETON — structure only. Every <...> placeholder must be replaced "
            "using the vocabulary, the DSL spec, and the extracted requirements; the skeleton "
            f"carries no policy content:\n{POLICY_SKELETON}"
        )
    return "\n\n".join(parts)


def write_package(arm_dir: Path, package: ProposedRulePackage) -> None:
    if arm_dir.exists():
        shutil.rmtree(arm_dir)
    (arm_dir / "common").mkdir(parents=True)
    for name, text in SCAFFOLD_FILES.items():
        (arm_dir / name).write_text(text)
    for file in package.files:
        if file.path not in EXPECTED_FILES:
            print(f"    skipping unexpected file: {file.path}")
            continue
        (arm_dir / file.path).write_text(file.content)


from app.rules_engine import RulesEngine

for arm in ("B", "C"):
    print(f"=== Arm {arm} (master) ===")
    package = ask(
        build_instructions(arm),
        f"PROGRAM DESCRIPTION:\n{PROGRAM_DESCRIPTION}\n\n"
        f"EXTRACTED REQUIREMENTS (JSON):\n{json.dumps(requirements_json, indent=1)}\n\n"
        f"VOCABULARY MAPPING (JSON):\n{json.dumps(mapping_json, indent=1)}",
        ProposedRulePackage,
    )
    arm_dir = OUT_DIR / f"generated-rules-master-{arm.lower()}"
    write_package(arm_dir, package)
    save_artifact(f"proposed-extensions-{arm.lower()}.json", package.proposed_extensions)
    print(f"  wrote {len(package.files)} files -> {arm_dir.name}/")
    print(f"  {len(package.proposed_extensions)} proposed engine extensions")
    # Documented compile attempt — expected to fail on Master vocabulary.
    try:
        RulesEngine.activate(arm_dir)
        print("  UNEXPECTED: package compiled against the current engine")
    except Exception as error:
        code = getattr(error, "code", type(error).__name__)
        message = getattr(error, "safe_message", str(error))
        print(f"  compile attempt (expected rejection): [{code}] {message}")
    print()

print("done — review the generated-rules-master-b/ and -c/ folders and master-artifacts/")
