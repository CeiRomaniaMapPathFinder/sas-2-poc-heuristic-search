# The briefs

The two design documents this project worked from.

- `creative_heuristic_function_guide.md` — what the assignment asks for, what
  "creative" has to mean, which of our earlier assumptions were too strict, and the
  tests a candidate heuristic should pass.
- `football_analysis_heuristic_methods.md` — the football ideas: Expected Goal
  Threat, progressive passing, press resistance, route redundancy, packing, pitch
  control, passing-network centrality, and how to combine them.

Both have been edited for readability since they were first written: the structure
is tighter, the repetition is gone, and so are the passages addressed at the tooling
rather than at a reader. The rules, formulas, methods and worked examples are
unchanged — nothing was added to them after the fact to make the project's decisions
look better.

Experiments 01 to 08 come from the second document, in the order it builds them up.
Experiments 09 and 10 are ours.

Where a brief and the experiments disagree, the experiments are the later word. Two
cases worth knowing: the first xGT formulation here has no pass-completion
probability and turns out to be degenerate (see
`../../experiments/01_expected_goal_threat/performance.md`), and the combined model
recommended at the end of the football brief scored worse than its own first
ingredient (`../../experiments/08_combined_model/performance.md`).
