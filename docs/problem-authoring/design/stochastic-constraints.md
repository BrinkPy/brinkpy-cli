# Stochastic Variable Constraints Example: `PipecorrProblem.py`

This page shows how to keep the search for the design point inside the range where a limit state function is valid, with constraints on the stochastic variables. The example finds the model strength factor of corroded pipelines of two steel grades for a target reliability index, and then checks the reliability with Monte Carlo simulation.

!!! note "About the tables on this page"
    - Table values are rounded to 4 significant figures for readability. Very small/large values use scientific notation. Refer to the Excel/JSON result files for full precision.
    - Advanced solver diagnostics (for example `br_mult`, `lsf_mult`, `bnds_mult`, and `constr_mult` Lagrange multipliers) are included in the Excel/JSON result files and are not shown in the tables below.

## The Modeling Problem

The limit state function uses the burst pressure model of Netto et al. (2005) for a pipeline with a corrosion defect. Netto et al. fitted the model to a numerical parametric study that covered ratios of defect depth to wall thickness, `d / t`, from 0.1 to 0.8, and ratios of defect length to outer diameter, `l / Do`, up to 1.5 (p. 1200). Outside this range the model is an extrapolation.

Bhardwaj et al. (2023), who provide the data for this example, do not limit the variables to this range. In Brinkpy, constraints on the stochastic variables keep the search for the design point inside it. The results then show where the design point lies within the range, and a note reports any limit that stops the search. An active limit would mean that the most probable failure lies at the edge of the range where the model is valid. See [Constraints on Stochastic Variables](../index.md#constraints-on-stochastic-variables) for the keys and their effect on each method.

## Run Context

Problem module:

- `problems/PipecorrProblem.py`

Recorded result sets:

- Design: `results/2026-11-07/15-57-10/Pipe_Corrosion-3d4f9.xlsx`, `.json`, `.py`, and `profile-3d4f9.yaml`
- Monte Carlo: `results/2026-11-07/15-57-45/Pipe_Corrosion-4f358.xlsx`, `.json`, `.py`, `.pickle`, `.pdf`, and `profile-4f358.yaml`

Profile and run modes from the saved profiles:

- Profile used: `default`
- Design: `run_type: design`, `include_sorm: false`, `include_mc: false`
- Monte Carlo: `run_type: analyze`, `include_sorm: false`, `include_mc: true`

For results-folder and filename conventions, see [CLI Result Files](../../cli/results-files.md).

Equivalent commands:

```bash
brinkpy design
brinkpy analyze -m
```

`-m` enables Monte Carlo simulation.

## Profile Customization

This example uses the `default` profile, where `design_xtol` and `design_gtol` are 0.001 and `mc_remove_oob` is `true`, so Monte Carlo removes the samples that violate a constraint. See [Design Optimization Settings](../../profiles/profile-reference.md#design-optimization-settings) and [Monte Carlo Settings](../../profiles/profile-reference.md#monte-carlo-settings).

## Problem File Used

**Sources:**

- Limit state function and the range of the model: Netto, T. A., Ferraz, U. S. and Estefen, S. F., "The effect of corrosion defects on the burst pressure of pipelines," *Journal of Constructional Steel Research*, vol. 61, no. 8, 2005, pp. 1185–1204. [→](https://doi.org/10.1016/j.jcsr.2005.02.010)
- Variables, steel grades, and target reliability index: Bhardwaj, U., Teixeira, A. P. and Guedes Soares, C., "Uncertainty in the estimation of partial safety factors for different steel-grade corroded pipelines," *Journal of Marine Science and Engineering*, vol. 11, no. 1, 2023, art. 177. [→](https://doi.org/10.3390/jmse11010177)

The stochastic variables are the model uncertainty factor `Xm`, the yield strength `Y` (MPa), the wall thickness `t` (mm), the outer diameter `Do` (mm), the defect depth `d` (mm), the defect length `l` (mm), and the operating pressure `Po` (MPa). They are uncorrelated. The model strength factor `Xr` is deterministic. The limit state function is:

```text
g = Xr Xm (2.2 Y t / Do) (1 - 0.9435 (d / t)^1.6 (l / Do)^0.4) - Po
```

The resistance is the burst pressure, and the load is the operating pressure.

### Keys That Implement the Constraints

The two ratios are limited to the range of the model:

```python
"StochasticVariables": {
    "name": ["Xm", "Y", "t", "Do", "d", "l", "Po"],
    ...
    "constraints": [
        {"fun": d_over_t, "lb": [0.1], "ub": [0.8], "jac": d_over_t_gradient},
        {"fun": l_over_Do, "lb": [0.0], "ub": [1.5]},
    ],
},
```

Each constraint function receives the stochastic variables `X` and the deterministic variables `D`, as the limit state function does:

```python
def d_over_t(X, D):
    Xm, Y, t, Do, d, l, Po = X
    return d / t


def d_over_t_gradient(X, D):
    Xm, Y, t, Do, d, l, Po = X
    return np.array([0.0, 0.0, -d / (t**2), 0.0, 1.0 / t, 0.0, 0.0])
```

`d_over_t` provides its gradient with `jac`, and `l_over_Do` does not, so SciPy approximates the gradient of `l_over_Do` with finite differences.

### Design Keys

Bhardwaj et al. ran several FORM analyses to find the value of `Xr` that gives the target reliability index of 2.47. Brinkpy finds it in one run instead: `Xr` is the design variable and the objective function is `DOF(d, D) = Xr`, so the optimizer looks for the smallest `Xr` that meets the target. The two steel grades are design cases:

```python
"DesignProblem": {
    "DesignVariables": ["Xr"],
    "InitialGuess": [0.5],
    "lb": [0.0],
    "ub": [10.0],
    "TargetBeta": 2.47,
    "fractiles": [0.05, 0.05, 0.5, 0.5, 0.5, 0.5, 0.95],
    "cases": {
        "Low Grade": {
            "mean": [1.0, 328.8, 6.450, 324, 1.00, 100, 9.10],
            "std": [0.17, 26.30, 0.064, 3.24, 0.17, 57, 0.64],
        },
        "Medium Grade": {
            "mean": [1.0, 429.6, 6.350, 508, 1.00, 100, 7.44],
            "std": [0.22, 34.40, 0.063, 5.08, 0.17, 57, 0.52],
        },
    },
},
```

`fractiles` defines a characteristic value for every stochastic variable: the 5% fractile for `Xm` and `Y`, the median for the dimensions, and the 95% fractile for `Po`. Bhardwaj et al. define characteristic values only for the resistance (5%) and the load (95%), so the partial factors on this page are not comparable with theirs.

## Design Results

The tables below are transcribed from the `Results` worksheet in `Pipe_Corrosion-3d4f9.xlsx`, with the two cases combined. For the meaning of each column, see [Results Tables Reference](../results-tables.md#design).

### Header Information

| Field | Value |
|---|---|
| Problem | `Pipe Corrosion` |
| Request ID | `bbe20757c2d4412580f9f28021a3d4f9` |
| Run time | `00 min 01.69 sec` |

### Design Data

| case | obj_value | target_beta | actual_beta | target_pf | actual_pf | use_sorm | dof_count | beta_count | nit | min_tries | min_method |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---|
| Low Grade | 0.9867 | 2.47 | 2.470 | 0.006756 | 0.006760 | False | 2 | 6 | 5 | 2 | tr_interior_point |
| Medium Grade | 1.033 | 2.47 | 2.470 | 0.006756 | 0.006756 | False | 2 | 6 | 3 | 1 | tr_interior_point |

### Design Variables Result

| case | var_name | opt_value | lb | ub |
|---|---|---:|---:|---:|
| Low Grade | Xr | 0.9867 | 0 | 10 |
| Medium Grade | Xr | 1.033 | 0 | 10 |

### Design Point Stochastic Variables Result

| var_name | fractile | Low Grade x | Low Grade char_value | Low Grade partial_factor | Medium Grade x | Medium Grade char_value | Medium Grade partial_factor |
|---|---:|---:|---:|---:|---:|---:|---:|
| Xm | 0.05 | 0.8266 | 0.8087 | 1.022 | 0.7690 | 0.7633 | 1.007 |
| Y | 0.05 | 296.5 | 287.4 | 1.032 | 389.1 | 375.5 | 1.036 |
| t | 0.5 | 6.440 | 6.45 | 0.9984 | 6.340 | 6.35 | 0.9985 |
| Do | 0.5 | 324.5 | 324 | 1.002 | 508.8 | 508 | 1.001 |
| d | 0.5 | 1.036 | 1.014 | 1.021 | 1.032 | 1.014 | 1.017 |
| l | 0.5 | 91.86 | 86.88 | 1.057 | 90.87 | 86.88 | 1.046 |
| Po | 0.95 | 10.24 | 10.29 | 0.9943 | 8.254 | 8.410 | 0.9814 |

### Load and Resistance Partial Factors

| case | Load | Resistance |
|---|---:|---:|
| Low Grade | 0.9943 | 1.049 |
| Medium Grade | 0.9814 | 1.039 |

### FORM Results (At Optimum)

| case | beta | pf | beta_count | hbeta_count | lsf_count | glsf_count | hlsf_count | min_method |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Low Grade | 2.470 | 0.006760 | 156 | 156 | 150 | 150 | 0 | tr_interior_point |
| Medium Grade | 2.470 | 0.006756 | 120 | 120 | 114 | 114 | 0 | tr_interior_point |

### Stochastic Variables Constraints

See [Stochastic Variables Constraints](../results-tables.md#stochastic-variables-constraints) for the columns.

| case | constr_name | constr_row | lb | ub | value | constr_count |
|---|---|---:|---:|---:|---:|---:|
| Low Grade | d_over_t | 1 | 0.1 | 0.8 | 0.1608 | 150 |
| Low Grade | l_over_Do | 1 | 0 | 1.5 | 0.2831 | 1200 |
| Medium Grade | d_over_t | 1 | 0.1 | 0.8 | 0.1627 | 114 |
| Medium Grade | l_over_Do | 1 | 0 | 1.5 | 0.1786 | 912 |

### Notes Reported by Brinkpy

1. Validation: Stochastic variables definition and limit state function validation required 2 function calls.
2. Validation: Design problem validation required 2 calls to the design objective function.
3. Validation: Validation of the limit state function analytic gradient required 4 function calls.
4. Validation: Validation of stochastic variables constraint function 'd_over_t' analytic gradient required 106 function calls.
5. Validation: Validation of the design objective function analytic gradient and Hessian required 16 function calls.

## Monte Carlo Results

The `analyze` run uses the top-level `StochasticVariables`, which hold the Low Grade data, and the value of `Xr` in `DeterministicVariables`, 1.0. The tables below are transcribed from the `Results` worksheet in `Pipe_Corrosion-4f358.xlsx`.

### Header Information

| Field | Value |
|---|---|
| Problem | `Pipe Corrosion` |
| Request ID | `1032c8bde91e4bc9958ef8087084f358` |
| Run time | `00 min 01.31 sec` |

### FORM Results

| beta | pf | beta_count | hbeta_count | lsf_count | glsf_count | hlsf_count | nit | min_tries | min_method |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 2.555 | 0.005316 | 17 | 17 | 16 | 16 | 0 | 22 | 2 | tr_interior_point |

### Stochastic Variables Constraints

| constr_name | constr_row | lb | ub | value | constr_count |
|---|---:|---:|---:|---:|---:|
| d_over_t | 1 | 0.1 | 0.8 | 0.1609 | 16 |
| l_over_Do | 1 | 0 | 1.5 | 0.2836 | 128 |

### Monte Carlo Results

| beta | pf | cv | max_cv | size | %_removed | cycles | auto_size | mc_with_is |
|---:|---:|---:|---:|---:|---:|---:|---|---|
| 2.549 | 0.005399 | 0.02516 | 0.05 | 300000 | 3.000 | 3 | True | False |

### Notes Reported by Brinkpy

1. Validation: Stochastic variables definition and limit state function validation required 2 function calls.
2. Validation: Validation of the limit state function analytic gradient required 4 function calls.
3. Validation: Validation of stochastic variables constraint function 'd_over_t' analytic gradient required 106 function calls.
4. Monte Carlo: Completed 3 cycles with 1.00e+05 samples per cycle.
5. Monte Carlo: 2.94% and 0.06% of samples violated the following constraints: 'd_over_t' and 'l_over_Do' out of 3.00e+05 total samples. In total, 3.00% of the samples violated the constraints and were excluded from the Monte Carlo statistics.
6. Monte Carlo: If a large fraction of samples were not finite, out of bounds or violated constraints, consider adjusting the statistical distributions of the variables, truncating them to finite lower (lb) and upper (ub) bounds, and reviewing any constraints on the variables to make sure they are valid.

The PDF result file for this run is saved as `results/2026-11-07/15-57-45/Pipe_Corrosion-4f358.pdf`.

## Interpretation Snapshot

- Both steel grades reach the target reliability index of 2.47 within the 0.001 tolerance, with `Xr = 0.9867` for the Low Grade and `Xr = 1.033` for the Medium Grade.
- At both design points, `d / t` and `l / Do` lie well inside the range of the model, so the reliability index comes from a region where the limit state function is valid. No limit is active, so Brinkpy reports no note about the constraints.
- `l_over_Do` was called 8 times as often as `d_over_t` (1200 against 150 for the Low Grade), because SciPy approximates its gradient with finite differences over the 7 variables. Providing `jac` saves these calls.
- Monte Carlo agrees with FORM (`beta = 2.549` against `2.555`) with `cv = 0.02516`, below the target of 0.05.
- Monte Carlo removed 3.00% of the samples, almost all for `d_over_t`. With a mean wall thickness of 6.45 mm, a `d / t` below 0.1 means a defect shallower than about 0.65 mm, outside the range of the model. The statistics describe only the samples inside the range.
