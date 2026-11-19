---
title: "Stochastic Variable Constraints Example: PipecorrProblem.py"
description: "How to keep the design point search inside the valid range of a limit state function with constraints on the stochastic variables, shown on corroded pipelines."
---

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

- Design: `results/2026-11-14/22-29-27/Pipe_Corrosion-45372.xlsx`, `.json`, `.py`, and `profile-45372.yaml`
- Monte Carlo: `results/2026-11-17/18-30-35/Pipe_Corrosion-a94bc.xlsx`, `.json`, `.py`, `.pickle`, `.pdf`, and `profile-a94bc.yaml`

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

One constraint function, `ratios`, returns both ratios. `lb` and `ub` give one limit for each of its two outputs, in the same order:

```python
"StochasticVariables": {
    "name": ["Xm", "Y", "t", "Do", "d", "l", "Po"],
    ...
    "constraints": [
        {"fun": ratios, "lb": [0.1, 0.0], "ub": [0.8, 1.5], "jac": ratios_jacobian, "hess": ratios_hessian},
    ],
},
```

Each constraint function receives the stochastic variables `X` and the deterministic variables `D`, as the limit state function does. `ratios_jacobian` returns the gradient of each output with respect to `X`, one row per output, so a 2 × 7 matrix. `ratios_hessian` also receives `v`, which holds one Lagrange multiplier per output, and returns the 7 × 7 Hessian of `v[0] (d / t) + v[1] (l / Do)`:

```python
def ratios(X, D):
    # X is a nxs matrix where n is the number of stochastic variables and s is the number of samples
    # D is a (m,) array where m is the number of deterministic variables
    _, _, t, Do, d, l, _ = X

    g = np.array([d / t, l / Do])

    return g  # (2,) or (2,s)


def ratios_jacobian(X, D):
    # Jacobian of the ratios constraint with respect to the stochastic variables
    # X is a (n,) array of stochastic variables
    # D is a (m,) deterministic variable array where m is the number of deterministic variables
    _, _, t, Do, d, l, _ = X

    gg = np.array([[0.0, 0.0, -d / (t**2), 0.0, 1.0 / t, 0.0, 0.0], [0.0, 0.0, 0.0, -l / (Do**2), 0.0, 1.0 / Do, 0.0]])

    return gg  # (2,7)


def ratios_hessian(X, v, D):
    # Hessian of np.dot(ratios, v)
    # X is a (n,) array of stochastic variables
    # v is a (p,) Lagrange multiplier array where p is the number of outputs of the constraint (here 2)
    # D is a (m,) deterministic variable array where m is the number of deterministic variables
    _, _, t, Do, d, l, _ = X

    H = np.zeros((7, 7))
    H[2, 2] = v[0] * 2 * d / (t**3)
    H[2, 4] = -v[0] / (t**2)
    H[4, 2] = -v[0] / (t**2)
    H[3, 3] = v[1] * 2 * l / (Do**3)
    H[3, 5] = -v[1] / (Do**2)
    H[5, 3] = -v[1] / (Do**2)

    return H  # (7,7)
```

Without `jac`, SciPy would approximate the Jacobian with finite differences, which takes extra constraint calls for each of the 7 variables. Without `hess`, it would approximate the Hessian with a quasi-Newton (BFGS) update. The results and notes identify each output of `ratios` by its number: output 1 is `d / t` and output 2 is `l / Do`.

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

The tables below are transcribed from the `Results` worksheet in `Pipe_Corrosion-45372.xlsx`, with the two cases combined. For the meaning of each column, see [Results Tables Reference](../results-tables.md#design).

### Header Information

| Field | Value |
|---|---|
| Problem | `Pipe Corrosion` |
| Request ID | `b0b9efde143a4aca93ebfd1411f45372` |
| Run time | `00 min 01.89 sec` |

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
| Low Grade | 2.470 | 0.006760 | 146 | 146 | 140 | 140 | 0 | tr_interior_point |
| Medium Grade | 2.470 | 0.006756 | 192 | 192 | 186 | 186 | 0 | tr_interior_point |

### Stochastic Variables Constraints

See [Stochastic Variables Constraints](../results-tables.md#stochastic-variables-constraints) for the columns. Each output of `ratios` has its own row. `constr_count` counts calls to the function, so it appears only on the first row.

| case | constr_name | constr_row | lb | ub | value | constr_count |
|---|---|---:|---:|---:|---:|---:|
| Low Grade | ratios | 1 | 0.1 | 0.8 | 0.1608 | 140 |
| Low Grade | ratios | 2 | 0 | 1.5 | 0.2831 | |
| Medium Grade | ratios | 1 | 0.1 | 0.8 | 0.1627 | 186 |
| Medium Grade | ratios | 2 | 0 | 1.5 | 0.1786 | |

### Notes Reported by Brinkpy

1. Validation: Stochastic variables definition and limit state function validation required 2 function calls.
2. Validation: Design problem validation required 2 calls to the design objective function.
3. Validation: Validation of the limit state function analytic gradient required 4 function calls.
4. Validation: Validation of stochastic variables constraint function 'ratios' analytic gradient and Hessian required 624 function calls.
5. Validation: Validation of the design objective function analytic gradient and Hessian required 37 function calls.

## Monte Carlo Results

The `analyze` run uses the top-level `StochasticVariables`, which hold the Low Grade data, and the value of `Xr` in `DeterministicVariables`, 1.0. The tables below are transcribed from the `Results` worksheet in `Pipe_Corrosion-a94bc.xlsx`.

### Header Information

| Field | Value |
|---|---|
| Problem | `Pipe Corrosion` |
| Request ID | `998481a2283f4488ac59c231dd8a94bc` |
| Run time | `00 min 02.08 sec` |

### FORM Results

| beta | pf | beta_count | hbeta_count | lsf_count | glsf_count | hlsf_count | nit | min_tries | min_method |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 2.555 | 0.005316 | 26 | 26 | 25 | 25 | 0 | 31 | 2 | tr_interior_point |

### Stochastic Variables Constraints

| constr_name | constr_row | lb | ub | value | constr_count |
|---|---:|---:|---:|---:|---:|
| ratios | 1 | 0.1 | 0.8 | 0.1609 | 25 |
| ratios | 2 | 0 | 1.5 | 0.2836 | |

### Monte Carlo Results

| beta | pf | cv | max_cv | size | %_removed | cycles | auto_size | mc_with_is |
|---:|---:|---:|---:|---:|---:|---:|---|---|
| 2.540 | 0.005541 | 0.04533 | 0.05 | 90000 | 2.947 | 3 | True | False |

### Notes Reported by Brinkpy

1. Validation: Stochastic variables definition and limit state function validation required 2 function calls.
2. Validation: Validation of the limit state function analytic gradient required 4 function calls.
3. Validation: Validation of stochastic variables constraint function 'ratios' analytic gradient and Hessian required 624 function calls.
4. Monte Carlo: Completed 3 cycles with 3.00e+04 samples per cycle.
5. Monte Carlo: 2.88% and 0.07% of samples violated the following constraints: 'ratios' (output 1) and 'ratios' (output 2) out of 9.00e+04 total samples. In total, 2.95% of the samples violated the constraints and were excluded from the Monte Carlo statistics.
6. Monte Carlo: If a large fraction of samples were not finite, out of bounds or violated constraints, consider adjusting the statistical distributions of the variables, truncating them to finite lower (lb) and upper (ub) bounds, and reviewing any constraints on the variables to make sure they are valid.

The PDF result file for this run is saved as `results/2026-11-17/18-30-35/Pipe_Corrosion-a94bc.pdf`.

## Interpretation Snapshot

- Both steel grades reach the target reliability index of 2.47 within the 0.001 tolerance, with `Xr = 0.9867` for the Low Grade and `Xr = 1.033` for the Medium Grade.
- At both design points, `d / t` and `l / Do` lie well inside the range of the model, so the reliability index comes from a region where the limit state function is valid. No limit is active, so Brinkpy reports no note about the constraints.
- `ratios` provides its Jacobian and Hessian, so the design search needed one call to `ratios` per call to the limit state function (140 for the Low Grade). Checking both against finite differences before the run took 624 calls (note 4).
- Monte Carlo agrees with FORM (`beta = 2.540` against `2.555`) with `cv = 0.04533`, below the target of 0.05.
- Monte Carlo removed 2.95% of the samples, almost all for output 1 of `ratios`, `d / t` (2.88%). With a mean wall thickness of 6.45 mm, a `d / t` below 0.1 means a defect shallower than about 0.65 mm, outside the range of the model. The statistics describe only the samples inside the range.
