# Bonus: defects nobody reported

A full sweep of all 43 questions (not just the 39 reported ones) found these:

1. **61ee6c9d (Peyer's patches) - solution typos.** The reported defect was option D
   ("plexux"), but the solution also contains "prominant folds" (-> prominent) and
   "Maceus membrane" (-> mucous membrane). Repair: `spelling` (solution field).

2. **Stray "&" artifacts inside MathML in three solutions** - 6956d797 ("& P = ..."),
   622f08d7 ("& = ..."), 68c801bc ("K & = ..."). A literal ampersand renders in the
   solution text. Repair: `noise`.

3. **68dea657 (lenses) - garbled variable names in solution.** "P_eqcu" and "P_eqch"
   where "P_each" was meant; the derivation and key (5 D) are correct. Repair: `notation`.

4. **695ede2a (dialysis) - self-contradictory solution.** The verdict (D) is right,
   but the solution first asserts "Statement-II is incorrect" and then argues dialysis
   IS supportive when transplant is infeasible - which is precisely why II is false.
   Reads as if it argues against its own answer. Repair: `solution_fix` (clarity
   rewrite, faculty-gated in my routing).

5. **68c9ae5a (photoelectric) - angstrom rendered as "A ∘".** The stem shows
   "wavelength 4000 A ∘" (a degree sign orphaned after A). Key D is correct. Repair:
   `notation`.

Not defects, checked and cleared: the four questions with no reports at all
(68dea87d capacitor, 68dea657 lenses, 695ede2a dialysis, 68dea6e6 displacement
method) all re-solve to their stored keys; the items above are presentation-layer
issues in the two that have them.
