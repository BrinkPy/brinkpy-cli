# Inverse FORM Examples

This page documents two inverse reliability design examples based on saved `design` runs.

!!! note "About the tables on this page"
    - Table values are rounded to 4 significant figures for readability. Very small/large values use scientific notation. Refer to the Excel/JSON result files for full precision.
    - Advanced solver diagnostics (for example `bsr_mult` and `bnds_mult` Lagrange multipliers) are included in the Excel/JSON result files and are not shown in the tables below.

**Inverse SORM:** Pass `--use-sorm` (or `-s`) to the `design` command to switch the solution algorithm from Inverse FORM to Inverse SORM. All examples on this page were run without this flag (Inverse FORM). The problem file structure is identical for both methods.

## Plot Behavior For `design` Runs

Brinkpy does not generate plots as part of `design` runs (including Inverse FORM).
This keeps outputs manageable when multiple design cases are included in one run.

If you need plots, use the resulting design parameters in a follow-up `analyze` or `simulate` run and enable plot/report options there.

## Profile Customization

These examples use the `default` profile. Inverse FORM behavior can be adjusted in a custom profile through `reliability_options.form_xtol`, `form_gtol`, `form_maxiter`, and `form_random_start`. See [FORM and Inverse FORM Settings](../../profiles/profile-reference.md#form-and-inverse-form-settings). When using Inverse SORM (`--use-sorm`), the [SORM Settings](../../profiles/profile-reference.md#sorm-settings) also apply.

## Example A: `AT625Problem.py` (Single Default Case)

### Run Context

Problem module:

- `problems/AT625Problem.py`

Recorded result set:

- `results/2026-11-02/12-37-06/Ang_and_Tang_6_25-19c5b.xlsx`
- `results/2026-11-02/12-37-06/Ang_and_Tang_6_25-19c5b.json`
- `results/2026-11-02/12-37-06/Ang_and_Tang_6_25-19c5b.py`
- `results/2026-11-02/12-37-06/profile-19c5b.yaml`

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

**Source:** Ang, A. H-S. and Tang, W. H., *Probability Concepts in Engineering Planning and Design, Vol. II*, Wiley, 1990, p. 431, Problem 6.25.

### Extracted Results Worksheet Tables

For the meaning of each column, see [Results Tables Reference](../results-tables.md#design).

Run summary:

| Field | Value |
|---|---|
| Request ID | `88e31f31ef144fe89b2f7c3d2a319c5b` |
| Target beta | `1.28` |
| Target pf | `0.1003` |
| Cases | `default` |

Default-case inverse FORM result:

| case | beta | pf | lsf_value | lsf_count | glsf_count | hlsf_count | beta_count | hbeta_count | nit | min_tries | min_method |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| default | 1.28 | 0.1003 | −109.5 | 8 | 7 | 7 | 7 | 7 | 8 | 1 | equality_constrained_sqp |

Design point stochastic variables result (`default`):

| var_name | x | fractile | char_value | partial_factor |
|---|---:|---:|---:|---:|
| f | 2.52 | 0.5 | 2.46 | 1.024 |
| N | 10.31 | 0.5 | 11 | 0.9374 |
| Y | 9.6 | 0.5 | 9.76 | 0.9836 |
| Q | 1.268e+04 | 0.5 | 9589 | 1.322 |

Load and resistance partial factors (`default`):

| Load | Resistance |
|---:|---:|
| 1.322 | 0.9109 |

Notes:

- This is the canonical single-case inverse FORM setup.
- `lsf_value` is negative (−109.5), so this design falls slightly short of the target. FORM gives β = 1.252 for the same problem.
- `AT625` also reports load and resistance partial factors in the design output.

## Example B: `AT624Problem.py` (Multi-Case)

### Run Context

Problem module:

- `problems/AT624Problem.py`

Recorded result set:

- `results/2026-11-02/12-33-53/Ang_and_Tang_6_24-3deac.xlsx`
- `results/2026-11-02/12-33-53/Ang_and_Tang_6_24-3deac.json`
- `results/2026-11-02/12-33-53/Ang_and_Tang_6_24-3deac.py`
- `results/2026-11-02/12-33-53/profile-3deac.yaml`

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
| Request ID | `1f72e3830fb147dab3b3db12c263deac` |
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

- No dedicated "Load and resistance partial factors" table was written in this `AT624` results workbook, because `LSFreturnsLandR = False` and therefore no load/resistance partial factors were calculated or reported.

Notes:

- This example demonstrates the `DesignProblem.cases` structure for running multiple reliability design scenarios in one command.
- Every case uses different case-level input statistics. `lsf_value` is close to zero in every case, so each design meets the target reliability (β = 2.0) exactly.

## Recommended Authoring Pattern

1. Start with a single-case definition (`default`) to validate setup and derivatives.
2. Add `cases` when you need scenario sweeps under a common target reliability.
