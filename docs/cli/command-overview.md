# CLI Command Overview

Brinkpy CLI provides three primary run commands:

- `analyze` for forward reliability assessment (FORM, with optional SORM and Monte Carlo)
- `design` for inverse reliability and reliability-based design optimization
- `simulate` for Monte Carlo simulation (with optional importance sampling, FORM, and SORM)

`analyze` and `simulate` can both run FORM and Monte Carlo, but they are built around different methods. `analyze` is built around FORM, with Monte Carlo as an optional check. `simulate` is built around Monte Carlo simulation, with FORM and SORM as optional comparisons.

When you run any of these commands, Brinkpy opens a file-picker popup so you can choose the problem file to execute.

If you are new to problem files, start with [Packaged Examples](../examples.md) and then review [Problem Definition](../problem-authoring/index.md).

## Analyze: Forward Reliability Assessment

Run forward reliability analysis to estimate the failure probability, the reliability index (β), and the most probable point (MPP). FORM always runs. SORM and Monte Carlo simulation are optional.

Usage: `brinkpy analyze <profile> [OPTIONS]`

→ [Full options and examples](analyze.md)

## Design: Factor Calibration and Reliability-Based Design Optimization

Run design workflows for both inverse reliability calibration and reliability-based design optimization.

Supports two modes:

- Code calibration via Inverse FORM or Inverse SORM when no objective function is present
- Reliability-based design optimization when an objective function is defined to minimize cost, weight, or another performance metric while meeting reliability constraints

The problem file must include a `DesignProblem` section. See [Packaged Examples](../examples.md#available-examples) for examples that support `design`.

Usage: `brinkpy design <profile> [OPTIONS]`

→ [Full options and examples](design.md)

## Simulate: Monte Carlo Simulation

Run Monte Carlo simulation to estimate the failure probability, including rare events. Importance sampling is optional, and FORM and SORM can be included for comparison.

Usage: `brinkpy simulate <profile> [OPTIONS]`

→ [Full options and examples](simulate.md)
