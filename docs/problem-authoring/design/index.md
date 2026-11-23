---
title: "Design Problem Definition"
description: "How to define a Brinkpy design problem, for partial factor calibration with inverse FORM or inverse SORM, or for reliability-based design optimization with an objective."
---

# Design Problem Definition

This section covers problem definition for the `design` command. Design problems extend the base problem dictionary with `DesignProblem` keys. The `design` command has two workflows, and Brinkpy chooses one automatically from the `DesignProblem` keys. See [Design Keys Reference](design-keys.md) for the keys each workflow requires.

| | Calibration with Inverse FORM or Inverse SORM | Objective optimization |
|---|---|---|
| Brinkpy runs it when | `DesignProblem` has no `DesignObjectiveFunction` | `DesignProblem` defines a `DesignObjectiveFunction` |
| Computes | Partial factors and design point values that reach the target reliability | Design variable values that minimize the objective while reaching the target reliability |
| Use it for | Code calibration, load and resistance factor calibration, or back-calculating characteristic values | Minimizing cost, weight, or another performance measure, with reliability as a constraint |
| Target reliability | `TargetBeta` or `TargetPf` | `TargetBeta` or `TargetPf`, as a constraint |
| With `--use-sorm` | Inverse SORM instead of Inverse FORM | SORM instead of FORM for the reliability constraint |
| Packaged examples | `AT624Problem`, `AT625Problem` | `AT622Problem`, `CantileverBeamProblem`, `Ji1Problem`, `Ji2Problem`, `PipecorrProblem`, `Sorensen81Problem` |
| Worked example | [Inverse FORM Examples](inverse-form.md) | [Objective Optimization Example](optimization.md) |

See [Packaged Examples](../../examples.md) for how to copy the examples into your project folder.

## Design Documentation Layout

- [Design Keys Reference](design-keys.md): full `DesignProblem` dictionary reference and validation rules.
- [Inverse FORM Examples](inverse-form.md): worked Inverse FORM examples (`AT625Problem` single-case and `AT624Problem` multi-case).
- [Objective Optimization Example](optimization.md): worked objective optimization example (`Sorensen81Problem`) including additional optimization keys.
- [Random Design Parameters Example](random-design-parameters.md): how to model a design parameter that is also a random variable (`Ji1Problem`), with limitations and exceptions.
- [Stochastic Variable Constraints Example](stochastic-constraints.md): how to keep the search for the design point inside the range where the limit state function is valid, with constraints on the stochastic variables (`PipecorrProblem`), including a Monte Carlo run.
- [Design Constraints Example](design-constraints.md): a design with two failure modes in one limit state function, and a constraint on the design variables (`CantileverBeamProblem`), including a Monte Carlo run.

## Notes On Cases

- A design problem can define a single default case or multiple named cases.
- This applies to both workflows: Inverse FORM and objective optimization.
- If `DesignProblem.cases` is omitted, Brinkpy creates a `default` case from the top-level `StochasticVariables` definition.
- Multi-case definitions are useful when target reliability remains fixed but statistical definitions or design context vary per scenario.
- Packaged examples with multiple cases: `AT624Problem` (Inverse FORM) and `PipecorrProblem` (objective optimization).
