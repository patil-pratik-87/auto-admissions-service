#!/bin/bash
# Regenerate the rule-based baseline for THIS experiment: one fresh `admissions screen`
# run per persona (digital PDFs only), written to baseline/<persona>/ with full logs.
# Idempotent: personas with an existing application-result.json are skipped.
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
BASE="$ROOT/alternate-options/option-cd-agentic-rag/baseline"
cd "$ROOT" || exit 1

run_one() {
  p="$1"
  out="$BASE/$p"
  if [ -f "$out/application-result.json" ]; then
    echo "$p: cached"
    return 0
  fi
  rm -rf "$out"
  mkdir -p "$out"
  pdfs=()
  while IFS= read -r f; do pdfs+=("$f"); done < <(find "samples/filled-documents/$p" -name '*.pdf' ! -name '*-scan.pdf' | sort)
  uv run admissions screen "${pdfs[@]}" --program BACHELOR --output-dir "$out" --overwrite \
    > "$out/run.stdout.log" 2> "$out/run.stderr.log"
  echo "$p: exit $?"
}
export -f run_one
export BASE

find samples/filled-documents -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort \
  | xargs -P 3 -I{} bash -c 'run_one "$@"' _ {}
echo "baseline done"
