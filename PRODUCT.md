> DRAFT - prepared by Prithvi's AI assistant as a working prototype. Prithvi reviews and adopts (or edits) before submission; first-person voice is his once approved.

# PRODUCT.md

## Who loses the most when a question is broken

Not the student who reports it - the hundreds who never do. 43 questions drew 44
reports; at Acadza's scale a wrong answer key is met by thousands of students, and
most of them just learn the wrong physics, lose marks in a test series, and quietly
stop trusting the app. The design reflects this:

- **Correctness-affecting defects outrank everything.** The queue score puts a wrong
  answer key (+50) and a missing/blank option (+40) above typos (+5), and multi-report
  questions float up. A faculty member at 10 PM fixes what hurts the most students first.
- **Every report gets a teaching reply, not a receipt.** When the student was wrong
  (most reports), the reply shows the likely slip ("you got 22 V - that is the
  potential at P; the question asks P minus S"). A dismissed report with no explanation
  is how you lose a student; a kind correction is how you keep one.
- **Duplicate reports are one case, not three.** Faculty attention is the scarce
  resource; grouping by question means one decision closes all three.

## What I would never let the AI auto-apply

Anything that **authors new content**: new distractors for identical/missing options,
diagrams, chapter refiles, solution rewrites where the stored one contradicts itself.
The taxonomy agrees (those are `auto: false`) - and I went one step stricter: even
`option_repair` (marked `auto: true`) goes to faculty when the option text has to be
*invented* rather than restored. An auto-applied wrong distractor teaches wrong
chemistry to every student who picks it; a typo fix teaches nothing new. That is the
line: edits that restore stated truth can be automatic, edits that create content
cannot. And no `answer_key` change applies without an independent blind solve agreeing
with the stored solution.

## One metric for week 1

**Faculty override rate on auto-applied edits** (target < 5%). It is the honest
measure of whether the engine's judgment can be trusted - every override is a case
where the AI wrote something a human disagreed with. Secondary: median
report-to-close time, which is the metric students actually feel.

## One idea beyond the brief

**Corrective re-serving.** When a question is fixed, Acadza knows every student who
attempted it while it was broken. Re-serve the corrected question to them and notify
the reporter ("you were right - it's fixed"). A defect becomes a trust-building
moment, test-series scores stop carrying phantom errors, and the report button starts
feeling worth pressing.
