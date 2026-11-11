# Acadza - Report to Fix

AI triage of student error reports on JEE/NEET questions, plus a faculty review
console. Built for the Acadza AI Intern build round.

## Layout

- `pipeline/` - the triage engine
  - `prompts/solver.md` - blind independent solve (no key, no solution)
  - `prompts/triage.md` - verdict / repair / edit / route / evidence / student reply
  - `run_triage.py` - groups reports by question, runs solver then triage, validates
  - `validate.py` - hard guards: taxonomy, repair scope, verbatim find-string,
    `auto:false` can never auto-apply
  - `normalize.py` - renders production HTML+MathML to text for the LLM steps
- `console/` - static faculty review console (open `index.html` or serve the folder)
  - queue grouped by question, ordered by urgency (correctness impact + needs-human
    + report count); question rendered with native MathML; before/after diff of the
    proposed edit; approve / edit / reject with a local audit trail
- `results.json` - triage output for all 44 reports (produced offline - see PROMPTS.md)
- `analysis/triage_outputs.json` - raw per-report outputs the offline run replays

The raw assignment dataset (`data/`) is NOT committed: the brief asks for code +
`results.json`, not redistribution of the raw dataset. The console reads a generated
`console/data.json` (also gitignored); regenerate it locally with:

```
python pipeline/build_console_data.py --data /path/to/assignment/data --results results.json
```

The brief expressly asks for a live public console displaying the supplied questions,
so a deployment serves that generated bundle; only the raw dataset files stay out of
the repo.
- `bonus.md` - defects found that nobody reported
- `PRODUCT.md`, `PROMPTS.md`

## Run

```
cd pipeline
python run_triage.py --data /path/to/assignment/data --out results.json      # needs TRIAGE_BASE_URL/KEY/MODEL
TRIAGE_TAXONOMY=/path/to/assignment/data/taxonomy.json \
  python run_triage.py --data /path/to/assignment/data --offline analysis/triage_outputs.json --out /tmp/r.json
python verify_checks.py    # 29 independent recomputations behind the numeric verdicts
```

## Console

```
cd console && python -m http.server 8000   # http://localhost:8000
```

No build step, no dependencies; deploys as-is to any static host.
