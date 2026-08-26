"""Build one markdown report from the verdicts a judge run left on disk.

Reads whatever `runs/judges-live/<persona>/` contains, so it works after a full run, after a
filtered one, and standalone.

Usage:
    uv run python -m evals.judges.report [runs/judges-live]
"""

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

DEFAULT_ROOT = Path("runs/judges-live")


def _load(path: Path) -> dict[str, object]:
    return dict(json.loads(path.read_text()))


def build_report(root: Path = DEFAULT_ROOT) -> Path:
    """Write report.md summarising every screening and verdict under root.

    Args:
        root: Directory holding one subdirectory per persona.

    Returns:
        Path of the written report.

    Raises:
        FileNotFoundError: If root does not exist.
    """
    if not root.is_dir():
        raise FileNotFoundError(f"No judge run at {root}")

    personas = sorted(p for p in root.iterdir() if p.is_dir())
    verdicts: dict[str, dict[str, dict[str, object]]] = {}
    screenings: dict[str, dict[str, object]] = {}
    judges: set[str] = set()

    for folder in personas:
        name = folder.name
        screening = folder / "screening.json"
        if screening.is_file():
            screenings[name] = _load(screening)
        for verdict_path in sorted(folder.glob("judge-*.json")):
            record = _load(verdict_path)
            judge = str(record["judge"])
            judges.add(judge)
            verdicts.setdefault(name, {})[judge] = record

    ordered_judges = sorted(judges)
    models = {str(r["model"]) for by_judge in verdicts.values() for r in by_judge.values()}
    lines = [
        "# Judge run report",
        "",
        f"Generated {datetime.now(UTC).isoformat(timespec='seconds')}, "
        f"model {', '.join(sorted(models)) or 'unknown'}.",
        "",
        "Not calibrated. No domain-expert labels exist, so a verdict here reports what the judge "
        "said and not whether it was right.",
        "",
        "## Screening",
        "",
        "| Persona | Expected | Actual | Match |",
        "| --- | --- | --- | --- |",
    ]
    for name in sorted(screenings):
        row = screenings[name]
        actual = str(row.get("actual", "screen failed"))
        expected = str(row.get("expected", ""))
        lines.append(f"| {name} | {expected} | {actual} | {'yes' if expected == actual else 'no'} |")

    lines += ["", "## Verdicts", "", "| Persona | " + " | ".join(ordered_judges) + " |",
              "| --- |" + " --- |" * len(ordered_judges)]
    for name in sorted(verdicts):
        cells = [str(verdicts[name].get(judge, {}).get("result", "not run")) for judge in ordered_judges]
        lines.append(f"| {name} | " + " | ".join(cells) + " |")

    failures = [
        (name, judge, record)
        for name, by_judge in sorted(verdicts.items())
        for judge, record in sorted(by_judge.items())
        if record.get("result") == "FAIL"
    ]
    if failures:
        lines += ["", "## What the judges objected to", ""]
        for name, judge, record in failures:
            lines += [f"**{name}, {judge}.** {record.get('critique', '')}", ""]

    flat = [r for by_judge in verdicts.values() for r in by_judge.values()]
    def total(field: str) -> int:
        return sum(value for r in flat if isinstance(value := r.get(field), int))

    tokens = total("input_tokens")
    output = total("output_tokens")
    duration = total("duration_ms")
    lines += [
        "",
        "## Cost",
        "",
        f"{len(flat)} judge calls, {tokens:,} input tokens, {output:,} output tokens, "
        f"{duration / 1000:.0f} s of provider time.",
        "",
    ]

    path = root / "report.md"
    path.write_text("\n".join(lines))
    return path


if __name__ == "__main__":
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_ROOT
    print(f"wrote {build_report(root)}")
