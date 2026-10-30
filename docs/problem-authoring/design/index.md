# Design Problem Definition

This section covers problem definition for the `design` command. Design problems extend the base problem dictionary with `DesignProblem` keys and can follow two distinct workflows:

1. Inverse FORM (or Inverse SORM with `--use-sorm`): compute partial factors and design point values that satisfy a target reliability (`TargetBeta` or `TargetPf`).
2. Objective optimization: compute design variable values that minimize an objective while satisfying reliability constraints.

Brinkpy chooses the workflow automatically. If `DesignProblem` defines a `DesignObjectiveFunction`, it runs objective optimization. Otherwise, it runs Inverse FORM, or Inverse SORM when `--use-sorm` is used. See [Design Keys Reference](design-keys.md) for the keys each workflow requires.

## When To Use Which Design Type

- Use Inverse FORM when code calibration, load/resistance factor calibration, or characteristic-value back-calculation is the goal.
- Use objective optimization when the goal is to minimize cost, weight, or another performance metric and reliability is one of the constraints.

Packaged examples for each workflow (see [Packaged Examples](../../examples.md)):

- Inverse FORM: `AT624Problem`, `AT625Problem`
- Objective optimization: `AT622Problem`, `Ji1Problem`, `Ji2Problem`, `PipecorrProblem`, `Sorensen81Problem`

## Design Documentation Layout

- [Design Keys Reference](design-keys.md): full `DesignProblem` dictionary reference and validation rules.
- [Inverse FORM Examples](inverse-form.md): worked Inverse FORM examples (`AT625Problem` single-case and `AT624Problem` multi-case).
- [Objective Optimization Example](optimization.md): worked objective optimization example (`Sorensen81Problem`) including additional optimization keys.

## Notes On Cases

- A design problem can define a single default case or multiple named cases.
- This applies to both workflows: Inverse FORM and objective optimization.
- If `DesignProblem.cases` is omitted, Brinkpy creates a `default` case from the top-level `StochasticVariables` definition.
- Multi-case definitions are useful when target reliability remains fixed but statistical definitions or design context vary per scenario.
- Packaged examples with multiple cases: `AT624Problem` (Inverse FORM) and `PipecorrProblem` (objective optimization).
