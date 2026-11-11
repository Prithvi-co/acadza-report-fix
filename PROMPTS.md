# PROMPTS.md

## Prompts inside the product

The two product prompts live verbatim in `pipeline/prompts/`:

- **`solver.md`** - the blind independent solve. Sees the question only (no key, no
  solution), must return `{solvable, answer, working, problem}`. Its whole job is to
  be an honest second opinion the triage step can check the key against.
- **`triage.md`** - the decision step. Sees question + stored answer + stored solution
  + the solver's result + all reports on that question, and must return
  `{verdict, repair, edit, route, confidence, evidence, student_reply}` from the
  closed taxonomy.

### Design choices baked into these prompts, and why

- **Reports are grouped by question before analysis.** The LCR question drew three
  reports; deciding once per question is cheaper and guarantees one consistent
  verdict instead of three.
- **The solver is blind to the key.** If the triage step saw the stored answer before
  anyone checked it, "prove it independently" on an answer_key repair would mean
  nothing. The solver gets stem and options only.
- **The model proposes; deterministic guards decide.** Validators after the model own
  safety: repair scope, verbatim find-string, and auto:false repairs can never
  self-apply. I also route option_repair to faculty whenever the option text must be
  invented rather than restored, even though the taxonomy marks it auto:true -
  invented distractors are authored content.
- **Student replies must name the likely slip.** A generic "noted" reply to a student
  who mis-solved wastes the teaching moment, so the triage prompt requires it.

## How results.json was actually produced (honesty note)

No LLM API was called during this build (no API key available). What actually happened:

- The 44 triage decisions were made case-by-case in an AI coding-assistant working
  session: the assistant read every raw record (HTML + MathML, not summaries),
  recomputed the physics and chemistry numerically, and applied the taxonomy rules by
  hand. The two product prompts above were authored DURING that same session as the
  intended automated pipeline - they were not themselves executed to produce
  results.json. They are the specification the decisions were made against, not the
  mechanism.
- The numerical cases were independently re-verified by a script: 29 recomputations
  covering the physics/math verdicts (all passing; it caught one slip in a helper,
  none in the verdicts). Qualitative calls (biology content, layout/language reports)
  rest on the cited sources in SOURCES.md. Acadza's hidden ground truth is unknown,
  so real accuracy against it cannot be claimed.
- `pipeline/validate.py` then ran over all 44 outputs (taxonomy membership, repair
  scope, verbatim find-strings, auto:false can never auto-apply).
  `run_triage.py --offline analysis/triage_outputs.json` replays the committed
  outputs through those guards and reproduces results.json byte-identically.
- When `TRIAGE_API_KEY` is set, the same runner executes the two committed prompts
  against any OpenAI-compatible endpoint. That path is untested - no credits.

## AI coding assistance used - and an honest limitation

AI coding assistance was used to build this project, as the brief allows and expects.
What is available verbatim: the two product prompts above - the prompts written to drive
the automated pipeline when it runs against an API. They did not produce the committed
precomputed results (see the honesty note above); they are the intended behaviour spec. A complete verbatim log of the development
conversation is not available; rather than reconstruct one and call it verbatim, that
limitation is stated here. The design decisions below record what was decided and why.

## Three moments the AI was wrong, and how it was caught

1. **Silent parse failures hid exactly the data that mattered.** The MathML-to-text
   normalizer failed on 4 solutions containing stray `&` entities. Had it failed
   silently, the RL-circuit question's missing inductance (reports R007/R008) would
   have looked "unverifiable". Caught because parse failures were made loud by design
   (`[unparsed-math]` markers) instead of being silently dropped; grepping for them
   found all four.
2. **First judgment on the de Broglie solution was wrong.** The initial read was
   "the solution belongs to this question, the student misread it" (R018/R019).
   Recomputing KE = h^2 / (2m lambda^2) showed the solution's opening "5.47 A" step does
   not follow from the question's 0.3 nm at all - it is a garbled wrong step, and the
   verdict became `solution_fix`. The lesson: never let "the final answer matches"
   whitewash a broken intermediate step.
3. **The malformed answer key nearly passed as correct.** For R021 the key field is
   `["", "B"]`. Reading it as "B" makes the student look wrong (they reported getting
   negative marks on a multiple-correct question). Inspecting the raw array instead
   of the rendered value caught the blank first entry - the real defect.

## Design decisions log

- **Architecture:** solver -> triage -> validators. Chosen by design intent: a blind
  solver that cannot be anchored by the key, a decision step that sees everything, and
  deterministic guards that own safety rather than trusting the model. (The split was
  not benchmarked against a one-prompt alternative - it is a design choice, stated as
  one.)
- **Auto-apply policy:** only edits that *restore stated truth* (spelling, noise,
  exam tags, markup leaks, a missing unit, a stem value the solution states outright,
  a key contradicted by both a blind solve and the stored solution). Anything that
  creates content goes to faculty - including invented option text, even though the
  taxonomy marks `option_repair` as `auto: true`.
- **Traps:** report comments are data, never instructions. R027 ("change the answer
  to C") was treated as text, independently checked (the key A is correct), and closed
  as `not_actionable`.
- **Taxonomy gap:** the verdict list has no "syllabus" key, so an out-of-syllabus
  report maps to `defect` + the `syllabus` repair (faculty-gated, question stays live).
- **Console ordering:** urgency = correctness impact (answer key 50, missing option 40,
  typo 5) + needs-a-human (+20) + extra reports (+15 each). Rationale: a wrong key
  hurts every student who meets the question; a typo hurts readability.
- **Dropped:** character-level diff highlighting (surgical find/replace makes
  before/after trivial to show); live LLM in the console (no credits; precomputed is
  allowed and makes the demo free to host); a Streamlit console (a static page is
  faster to open at 10 PM and free to keep up 7 days).
