---
description: "A worked inverse FORM example, AT624, that computes design point values and partial factors for a target reliability index in four design cases with brinkpy design."
---

# Inverse FORM Example

This page documents an inverse reliability design example based on a saved `design` run.

!!! note "About the tables on this page"
    - Table values are rounded to 4 significant figures for readability. Very small/large values use scientific notation. Refer to the Excel/JSON result files for full precision.
    - Advanced solver diagnostics (for example `bsr_mult` and `bnds_mult` Lagrange multipliers) are included in the Excel/JSON result files and are not shown in the tables below.

**Inverse SORM:** Pass `--use-sorm` (or `-s`) to the `design` command to switch the solution algorithm from Inverse FORM to Inverse SORM. The example on this page was run without this flag (Inverse FORM). The problem file structure is identical for both methods.

## Plot Behavior For `design` Runs

Brinkpy does not generate plots as part of `design` runs (including Inverse FORM).
This keeps outputs manageable when multiple design cases are included in one run.

If you need plots, use the resulting design parameters in a follow-up `analyze` or `simulate` run and enable plot/report options there.

## Profile Customization

This example uses the `default` profile. Inverse FORM behavior can be adjusted in a custom profile through `reliability_options.form_xtol`, `form_gtol`, `form_maxiter`, and `form_random_start`. See [FORM and Inverse FORM Settings](../../profiles/profile-reference.md#form-and-inverse-form-settings). When using Inverse SORM (`--use-sorm`), the [SORM Settings](../../profiles/profile-reference.md#sorm-settings) also apply.

## Example: `AT624Problem.py` (Multiple Cases)

### Run Context

Problem module:

- `problems/AT624Problem.py`

Recorded result set:

- `results/2026-11-04/22-33-27/Ang_and_Tang_6_24-bb301.xlsx`
- `results/2026-11-04/22-33-27/Ang_and_Tang_6_24-bb301.json`
- `results/2026-11-04/22-33-27/Ang_and_Tang_6_24-bb301.py`
- `results/2026-11-04/22-33-27/profile-bb301.yaml`

Profile and run mode from saved profile:

- Profile used: `default`
- `run_type: design`
- `include_sorm: false`
- `include_mc: false`

For results-folder and filename conventions, see [CLI Result Files](../../cli/results-files.md).

Equivalent command:

```bash
brinkpy design
```

### Problem File Used

**Source:** Ang, A. H-S. and Tang, W. H., *Probability Concepts in Engineering Planning and Design, Vol. II*, Wiley, 1990, p. 428, Problem 6.24.

### Extracted Results Worksheet Tables

For the meaning of each column, see [Results Tables Reference](../results-tables.md#design).

Run summary:

| Field | Value |
|---|---|
| Request ID | `88e8e39280bf4724a24c4ef8de7bb301` |
| Target beta | `2.000` |
| Target pf | `0.02275` |
| Cases | `1`, `2`, `3`, `4` |

The workbook repeats the following tables for each design case. On this page, the cases are combined into one table with a `case` column.

Case-by-case inverse FORM results:

| case | beta | pf | lsf_value | lsf_count | glsf_count | hlsf_count | beta_count | hbeta_count | nit | min_tries | min_method |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 2.000 | 0.02275 | −0.001177 | 6 | 6 | 6 | 6 | 6 | 6 | 1 | equality_constrained_sqp |
| 2 | 2.000 | 0.02275 | −0.0003227 | 5 | 6 | 6 | 5 | 5 | 6 | 1 | equality_constrained_sqp |
| 3 | 2.000 | 0.02275 | −0.001776 | 6 | 6 | 6 | 5 | 5 | 6 | 1 | equality_constrained_sqp |
| 4 | 2.000 | 0.02275 | −0.0008712 | 6 | 6 | 6 | 5 | 5 | 6 | 1 | equality_constrained_sqp |

Design point stochastic variables result (all cases):

| case | var_name | x | fractile | char_value | partial_factor |
|---|---|---:|---:|---:|---:|
| 1 | N | 1.07 | 0.5 | 1 | 1.07 |
| 1 | M | 0.01259 | 0.5 | 0.01 | 1.259 |
| 1 | Y | 172.3 | 0.5 | 126 | 1.367 |
| 2 | N | 1.07 | 0.5 | 1 | 1.07 |
| 2 | M | 0.06278 | 0.5 | 0.05 | 1.256 |
| 2 | Y | 35.35 | 0.5 | 25.8 | 1.37 |
| 3 | N | 1.071 | 0.5 | 1 | 1.071 |
| 3 | M | 0.1252 | 0.5 | 0.1 | 1.252 |
| 3 | Y | 18.26 | 0.5 | 13.3 | 1.373 |
| 4 | N | 1.075 | 0.5 | 1 | 1.075 |
| 4 | M | 0.6145 | 0.5 | 0.5 | 1.229 |
| 4 | Y | 4.477 | 0.5 | 3.22 | 1.39 |

Load and resistance partial factors:

- The workbook has no load and resistance partial factors table, because `AT624` sets `LSFreturnsLandR = False`. When the limit state function returns the load and resistance, the design results also include their partial factors (see [Load and Resistance Partial Factors](../results-tables.md#load-and-resistance-partial-factors)).

Notes:

- This example demonstrates the `DesignProblem.cases` structure for running multiple reliability design scenarios in one command.
- Every case uses different case-level input statistics. `lsf_value` is close to zero in every case, so each design meets the target reliability (β = 2.0) exactly.

## Recommended Authoring Pattern

1. Start with a single case, without `cases`, to validate setup and derivatives. Brinkpy then runs one case named `default`.
2. Add `cases` when you need scenario sweeps under a common target reliability.
