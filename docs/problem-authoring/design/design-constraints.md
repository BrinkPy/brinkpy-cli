# Design Constraints Example: `CantileverBeamProblem.py`

This page shows a design optimization with two failure modes in one limit state function, and then adds a constraint on the design variables. The example finds the cross section of a cantilever beam with the smallest volume for a target probability of failure, first as Hu and Du (2019) define the problem and then with the height at least twice the width. A Monte Carlo run then checks the probability of failure of the optimal design.

!!! note "About the tables on this page"
    - Table values are rounded to 4 significant figures for readability. Very small/large values use scientific notation. Refer to the Excel/JSON result files for full precision.
    - Advanced solver diagnostics (for example `br_mult`, `lsf_mult`, `bnds_mult`, and `constr_mult` Lagrange multipliers) are included in the Excel/JSON result files and are not shown in the tables below.

## The Modeling Problem

Hu and Du (2019) use this cantilever beam as an example of reliability-based design optimization, in which the design must reach a target probability of failure. They compare several methods, some based on FORM and some on second-order approximations. This page compares Brinkpy with their FORM results. The full reference is in [Problem File Used](#problem-file-used).

A cantilever beam of length `L` carries a horizontal load `Px` and a vertical load `Py` at its free end. The beam fails if the bending stress at the fixed end exceeds the yield strength `Sy`, or if the deflection at the free end exceeds the allowed deflection `Do`. The design variables are the mean width `mb` and the mean height `mh` of the cross section, and the objective is the volume `mb mh L`. Hu and Du (2019) call it the weight, which for a given material is proportional to the volume.

Hu and Du (2019) treat the two failure modes as two separate reliability constraints. Brinkpy takes one limit state function, and a failure in either mode is a failure of the beam, so the beam is a series system. The limit state function returns the smaller of the two limit states, `g = min(g1, g2)`, written `numpy.minimum(g1, g2)` in the problem file (see [Series and Parallel Systems](../index.md#series-and-parallel-systems)). This has two consequences:

- `g` has a kink where `g1 = g2`, so the problem sets `LSFisSmooth` to `False`. FORM then uses COBYQA, which does not need derivatives (see [Smooth and Non-Smooth Functions](../index.md#smooth-and-non-smooth-functions)).
- `min` compares the values of `g1` and `g2`, so both must have similar scales. The problem file divides the stress limit state by `Sy` and the deflection limit state by `Do`, so that both are fractions of the capacity. Without the division, `g1` would be in psi and `g2` in inches, and `min` would pick a failure mode by its units instead of by how close it is to failure.

As in any series system, FORM gives the reliability index of the weakest mode only. The [Monte Carlo Results](#monte-carlo-results) section shows what this means for the probability of failure of the beam.

## Run Context

Problem module:

- `problems/CantileverBeamProblem.py`

Recorded result sets:

- Design as defined by Hu and Du (2019): `results/2026-11-16/14-04-19/Cantilever_Beam-98cf1.xlsx`, `.json`, `.py`, and `profile-98cf1.yaml`
- Design with the `h_over_b` constraint: `results/2026-11-16/14-04-36/Cantilever_Beam-14d53.xlsx`, `.json`, `.py`, and `profile-14d53.yaml`
- Monte Carlo at the optimal design: `results/2026-11-17/18-30-27/Cantilever_Beam-19a15.xlsx`, `.json`, `.py`, `.pickle`, `.pdf`, and `profile-19a15.yaml`

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

This example uses the `default` profile, where `design_xtol` and `design_gtol` are 0.001. See [Design Optimization Settings](../../profiles/profile-reference.md#design-optimization-settings).

## Problem File Used

The problem file follows Hu and Du (2019), the source of the variables, the target probability of failure, and the bounds of the design variables:

**Source:** Hu, Z. and Du, X., "Efficient reliability-based design with second order approximations," *Engineering Optimization*, vol. 51, no. 1, 2019, pp. 101–119. [→](https://doi.org/10.1080/0305215X.2018.1440292)

The stochastic variables are the deviations `b` and `h` of the width and height from their means (in), the loads `Px` and `Py` (lb), the modulus of elasticity `E` (psi), and the yield strength `Sy` (psi). All are normal and uncorrelated. Hu and Du (2019) give `b` and `h` a standard deviation of 0.01 in around the design values, so the problem file models them as deviations with a mean of 0 and adds them to `mb` and `mh`. The length `L` is 100 in and the allowed deflection `Do` is 2.25 in. With the actual width `mb + b` and height `mh + h`, written `B` and `H`, the limit state functions are:

```text
g1 = (Sy - (6 L / (B H)) (Px / B + Py / H)) / Sy
g2 = (Do - (4 L^3 / E) sqrt((Px / (B^3 H))^2 + (Py / (B H^3))^2)) / Do
g  = min(g1, g2)
```

### Design Keys

`mb` and `mh` are deterministic variables, listed first in `DeterministicVariables`, and the design variables. `TargetPf` and the bounds `lb` and `ub` are those of Hu and Du (2019). A target probability of failure of 1.35e-3 corresponds to a reliability index of 3:

```python
"DesignProblem": {
    "DesignObjectiveFunction": DOF,
    "DOFisVectorized": True,
    "DOFisSmooth": True,
    "DOFreturnsGradient": True,
    "DOFreturnsHessian": True,
    "DesignVariables": ["mb", "mh"],
    "InitialGuess": [1.5, 3.0],
    "lb": [1.0, 1.0],
    "ub": [4.0, 4.0],
    "TargetPf": 1.35e-3,
},
```

The volume is smooth, and `DOF` returns its gradient and Hessian, so `DOFisSmooth` is `True` and the design search uses the trust-region interior point method (`tr_interior_point`).

## Design Results

The tables below are transcribed from the `Results` worksheet in `Cantilever_Beam-98cf1.xlsx`. For the meaning of each column, see [Results Tables Reference](../results-tables.md#design).

### Header Information

| Field | Value |
|---|---|
| Problem | `Cantilever Beam` |
| Request ID | `e46fff3d1bfa43b390f46ee5edc98cf1` |
| Run time | `00 min 40.17 sec` |

### Design Data (Default Case)

| obj_value | target_beta | actual_beta | target_pf | actual_pf | use_sorm | dof_count | beta_count | nit | min_tries | min_method |
|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---|
| 891.0 | 3.000 | 2.999 | 0.00135 | 0.001353 | False | 70 | 213 | 97 | 1 | tr_interior_point |

### Design Variables Result

| var_name | opt_value | lb | ub |
|---|---:|---:|---:|
| mb | 2.261 | 1 | 4 |
| mh | 3.940 | 1 | 4 |

### Design Point Stochastic Variables Result

| var_name | x |
|---|---:|
| b | -0.003195 |
| h | -0.001932 |
| Px | 595.5 |
| Py | 1219 |
| E | 2.900e+07 |
| Sy | 38680 |

### FORM Results (At Optimum)

| beta | pf | beta_count | hbeta_count | lsf_count | glsf_count | hlsf_count | min_method |
|---:|---:|---:|---:|---:|---:|---:|---|
| 2.999 | 0.001353 | 48 | 0 | 13192 | 0 | 0 | COBYQA |

### Notes Reported by Brinkpy

1. Validation: Stochastic variables definition and limit state function validation required 2 function calls.
2. Validation: Design problem validation required 2 calls to the design objective function.
3. Validation: Validation of the design objective function analytic gradient and Hessian required 37 function calls.

!!! note "Comparison with the paper"
    Hu and Du (2019) require a reliability index of 3 for each failure mode. A FORM reliability index of 3 for `min(g1, g2)` means the same thing, since it is the reliability index of the weakest mode. With FORM, they report a volume of 890.77 at `mb = 2.2507` and `mh = 3.9577`. Brinkpy finds 890.96 at `mb = 2.2612` and `mh = 3.9402`, 0.02% more. At the published optimum, both failure modes have a reliability index of 3, so the optimum lies on the kink of `min(g1, g2)`. Brinkpy stops near it, where only the stress mode is at the target. Near the kink the gradient of the reliability constraint changes direction, which slows the design search. The exact stopping point can differ slightly between computers, and so can the results that depend on it, including the Lagrange multipliers in the Excel and JSON result files. Near the kink, the multiplier of a bound can be far from zero even when the bound is not active. In this run, `bnds_mult` for `mh` is −539, and on another computer the same problem gives −10.4.

## Adding a Design Constraint

The constraint in this section is not part of Hu and Du (2019), who do not limit the shape of the cross section. It was chosen arbitrarily, only to show how `DesignConstraints` works, and its results can't be compared with the paper. To require the height to be at least twice the width, add a `DesignConstraints` key to `DesignProblem` with the function `h_over_b`, which returns `mh / mb`, and raise the upper bounds so that they do not stop the search first. These are the only changes to the problem file:

```python
"ub": [10.0, 10.0],
"TargetPf": 1.35e-3,
"DesignConstraints": [{"fun": h_over_b, "lb": [2.0], "jac": h_over_b_jacobian, "hess": h_over_b_hessian}],
```

The constraint functions, already in the problem file, take the design variables `d` and the remaining deterministic variables `D`, as the design objective function does. `h_over_b_jacobian` returns a 1 × 2 matrix, one row per output. `h_over_b_hessian` also receives `v`, which holds one Lagrange multiplier per output, and returns the 2 × 2 Hessian of `v[0] (mh / mb)`:

```python
def h_over_b(d, D):
    mb, mh = d
    return mh / mb


def h_over_b_jacobian(d, D):
    mb, mh = d
    return np.array([[-mh / (mb**2), 1.0 / mb]])


def h_over_b_hessian(d, v, D):
    mb, mh = d
    return v * np.array([[2 * mh / (mb**3), -1.0 / (mb**2)], [-1.0 / (mb**2), 0.0]])
```

See [Design Constraints](design-keys.md#design-constraints) for the keys.

### Results With the Constraint

The tables below are transcribed from the `Results` worksheet in `Cantilever_Beam-14d53.xlsx`. The run took `00 min 04.28 sec`.

| obj_value | target_beta | actual_beta | target_pf | actual_pf | use_sorm | dof_count | beta_count | nit | min_tries | min_method |
|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---|
| 927.7 | 3.000 | 2.999 | 0.00135 | 0.001354 | False | 9 | 27 | 11 | 2 | tr_interior_point |

| var_name | opt_value | lb | ub |
|---|---:|---:|---:|
| mb | 2.154 | 1 | 10 |
| mh | 4.307 | 1 | 10 |

See [Design Constraints Result](../results-tables.md#objective-optimization-design-constraints-result) for the columns:

| constr_name | constr_row | lb | ub | value | constr_count |
|---|---:|---:|---:|---:|---:|
| h_over_b | 1 | 2 | inf | 2.000 | 9 |

| var_name | x |
|---|---:|
| b | -0.005476 |
| h | -0.001296 |
| Px | 644.1 |
| Py | 1059 |
| E | 2.899e+07 |
| Sy | 39000 |

| beta | pf | beta_count | hbeta_count | lsf_count | glsf_count | hlsf_count | min_method |
|---:|---:|---:|---:|---:|---:|---:|---|
| 2.999 | 0.001354 | 48 | 0 | 1285 | 0 | 0 | COBYQA |

The notes repeat notes 1 to 3 of the first run and add:

4. Validation: Validation of design constraint function 'h_over_b' analytic gradient and Hessian required 104 function calls.
5. Design case 'default': The lower limit of design constraint 'h_over_b' is active. Relaxing it would reduce the design objective function by about 166 per unit change in the limit. If values beyond this limit are acceptable, widen it.

## Monte Carlo Results

To check the probability of failure of the optimal design, set `mb` and `mh` in `DeterministicVariables` to the optimal values of the first run, rounded to 4 decimals, and run `analyze` with Monte Carlo:

```python
"DeterministicVariables": {
    "name": ["mb", "mh", "L", "Do"],
    "value": [2.2612, 3.9402, 100.0, 2.25],
},
```

The tables below are transcribed from the `Results` worksheet in `Cantilever_Beam-19a15.xlsx`. The run took `00 min 01.79 sec`.

### FORM Results

| beta | pf | beta_count | hbeta_count | lsf_count | glsf_count | hlsf_count | nit | min_tries | min_method |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 2.999 | 0.001352 | 48 | 0 | 48 | 0 | 0 | 43 | 1 | COBYQA |

### Monte Carlo Results

| beta | pf | cv | max_cv | size | %_removed | cycles | auto_size | mc_with_is |
|---:|---:|---:|---:|---:|---:|---:|---|---|
| 2.866 | 0.002077 | 0.04002 | 0.05 | 300000 | 0 | 3 | True | False |

### Notes Reported by Brinkpy

1. Validation: Stochastic variables definition and limit state function validation required 2 function calls.
2. Monte Carlo: Completed 3 cycles with 1.00e+05 samples per cycle.
3. Monte Carlo: Load and resistance histograms are not available since the limit state function does not return load and resistance values.

## Interpretation Snapshot

- The design reaches the target reliability index of 3 within the 0.001 tolerance, with a volume within 0.02% of the one Hu and Du (2019) report.
- At the optimum, the most probable failure point is a stress failure: `Px` and `Py` are about 2 standard deviations above their means and `Sy` is below its mean, while `E` stays at its mean.
- With the `h_over_b` constraint, the deeper section shifts the most probable failure to the deflection mode: `Sy` stays at its mean, because the stress limit state plays no part, and `Px` rises to almost 3 standard deviations above its mean. The constraint is active, and the volume rises from 891.0 to 927.7. Relaxing the limit of 2 by 0.1 would save about 17 (note 5).
- The constrained run took 4 seconds instead of 40, because its optimum lies away from the kink of `min(g1, g2)`.
- Monte Carlo gives a probability of failure of 0.002077 (`beta = 2.866`), about 1.5 times the FORM value. At this design the deflection mode also has a reliability index close to 3, and FORM leaves it out. To reach the target probability of failure for the whole beam, the design would need a higher target reliability index, checked with a simulation.
