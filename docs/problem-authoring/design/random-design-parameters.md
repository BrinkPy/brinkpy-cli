# Random Design Parameters Example: `Ji1Problem.py`

This page shows how to model a design problem where the design parameter is also a random variable. The usual case is a variable whose mean is chosen by the designer while its scatter stays random, for example a dimension or a material property with a fixed coefficient of variation.

!!! note "About the tables on this page"
    - Table values are rounded to 4 significant figures for readability. Very small/large values use scientific notation. Refer to the Excel/JSON result files for full precision.
    - Advanced solver diagnostics (for example `br_mult`, `lsf_mult`, and `bnds_mult` Lagrange multipliers) are included in the Excel/JSON result files and are not shown in the tables below.

## The Modeling Problem

In Brinkpy, design variables are deterministic. They are taken from `DeterministicVariables` and are not part of the stochastic variables vector (see the RBDO modeling assumption in [Design Keys Reference](design-keys.md#additional-keys-for-objective-optimization)). A random variable whose mean is a design variable therefore can't be defined directly.

## The Technique

Split the random design parameter `t` into a deterministic design variable and a normalized random variable:

1. Add a design variable, `Lambda`, to `DeterministicVariables` and list it in `DesignVariables`. `Lambda` plays the role of the mean of `t`.
2. Define `t` in `StochasticVariables` with a mean of 1 and a standard deviation equal to the coefficient of variation of `t`. Call this normalized variable `t0`.
3. In the limit state function, use `Lambda * t0` everywhere `t` appears. If the function returns its gradient and Hessian, they must include the factor `Lambda` too.

The physical random variable is `t = Lambda * t0`, with mean `Lambda` and standard deviation `Lambda` times the coefficient of variation.

### Why It Is Exact

The substitution is not an approximation. If `t0` is lognormal with mean 1 and coefficient of variation V, then multiplying it by a positive `Lambda` shifts `ln t` by `ln Lambda` and leaves the shape parameter unchanged. So `Lambda * t0` is lognormal with mean `Lambda` and the same coefficient of variation V, exactly the distribution of the original `t`.

The transformation to standard normal space gives the same result as well. A point in standard normal space maps to the same physical value of `t` whether `t` is defined directly, as lognormal with mean `Lambda`, or as `Lambda * t0`. The limit state surface in standard normal space, the reliability index, the design point and the sensitivities are therefore the same as if `t` could be defined directly, for every value of `Lambda`.

### Limitations and Exceptions

- **Fixed coefficient of variation.** Multiplying by `Lambda` keeps the coefficient of variation constant as the mean changes. This works for distributions that are closed under scaling: lognormal, normal, Weibull, gamma and exponential.
- **Fixed standard deviation.** If the standard deviation must stay constant instead, add rather than multiply: `t = Lambda + t0`, with `t0` having a mean of 0. This works only for distributions that are closed under shifting, such as normal and Gumbel. It does not work for lognormal, because shifting moves its lower bound away from 0.
- **`Lambda` must stay positive.** A negative `Lambda` flips the distribution of `t`, which has no physical meaning. Set a positive lower bound in `lb`. In this example, the reliability index is the same for `Lambda` and `-Lambda`, so without a positive bound the optimizer could converge to the mirror solution.
- **Results report `t0`, not `t`.** The stochastic variable tables and the design point show the normalized variable, with mean 1. Multiply by the optimized `Lambda` to obtain physical values of `t`. The same applies to plots of `t` from `analyze` or `simulate` runs.
- **Correlations carry over.** If `t` is correlated with other variables, give `t0` the same correlations. Multiplying by a positive constant does not change correlation coefficients.

## Run Context

Problem module:

- `problems/Ji1Problem.py`

Recorded result set:

- `results/2026-11-04/22-36-05/Ji_Example_1-8a722.xlsx`
- `results/2026-11-04/22-36-05/Ji_Example_1-8a722.json`
- `results/2026-11-04/22-36-05/Ji_Example_1-8a722.py`
- `results/2026-11-04/22-36-05/profile-8a722.yaml`

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

## Profile Customization

This example uses the `default` profile, where `design_xtol` and `design_gtol` are 0.001. Smaller values bring the reliability index closer to the target at the cost of more iterations. See [Design Optimization Settings](../../profiles/profile-reference.md#design-optimization-settings).

## Problem File Used

**Source:** Ji et al. (2023), *Robust reliability-based design approach by inverse FORM with adaptive conjugate search algorithm*, Problem 1. [→](https://onlinelibrary.wiley.com/doi/10.1002/nag.3524)

The random variables `x1` to `x4` are uncorrelated standard normal. `t` is lognormal with a coefficient of variation of 0.8, and its mean is the design parameter. The target reliability index is 2.0 and the starting value of the mean is 0.15. The limit state function is:

```text
g = exp(-t (x1 + 2 x2 + 3 x3)) - x4 + 1.5
```

### Keys That Implement the Technique

`Lambda` is the design variable and `t` is defined as the normalized variable `t0`, with mean 1 and standard deviation 0.8:

```python
"DeterministicVariables": {
    "name": ["Lambda"],
    "value": [0.15],
},
"StochasticVariables": {
    "name": ["x1", "x2", "x3", "x4", "t"],
    "type": ["normal", "normal", "normal", "normal", "lognormal"],
    "mean": [0, 0, 0, 0, 1],
    "std": [1, 1, 1, 1, 0.8],
},
```

The design problem starts at the paper's value of 0.15 and keeps `Lambda` positive:

```python
"DesignVariables": ["Lambda"],
"InitialGuess": [0.15],
"lb": [0.01],
"ub": [10.0],
"TargetBeta": 2.0,
```

In the limit state function, `t` is always multiplied by `Lambda`:

```python
x1, x2, x3, x4, t = X
Lambda = D

g = np.exp(-t * Lambda * (x1 + 2 * x2 + 3 * x3)) - x4 + 1.5
```

The gradient and Hessian in `Ji1Problem.py` are derived from this expression, so they also include `Lambda`.

The objective function is `DOF(d, D) = Lambda`. `DesignProblem.cases` is not defined, so Brinkpy creates a `default` case from `StochasticVariables`.

## Extracted Results Worksheet Tables

The tables below are transcribed from the `Results` worksheet in `Ji_Example_1-8a722.xlsx`. For the meaning of each column, see [Results Tables Reference](../results-tables.md#design).

### Header Information

| Field | Value |
|---|---|
| Problem | `Ji Example 1` |
| Request ID | `ee92706d2ba4449f84f527b08b18a722` |
| Run time | `00 min 00.11 sec` |

### Design Data (Default Case)

| obj_value | target_beta | actual_beta | target_pf | actual_pf | use_sorm | dof_count | beta_count | nit | min_tries | min_method |
|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---|
| 0.3993 | 2 | 2.001 | 0.02275 | 0.02271 | False | 3 | 8 | 6 | 2 | tr_interior_point |

### Design Variables Result

| var_name | opt_value | lb | ub |
|---|---:|---:|---:|
| Lambda | 0.3993 | 0.01 | 10 |

### Design Point Stochastic Variables Result

| var_name | x |
|---|---:|
| x1 | 0.2129 |
| x2 | 0.4258 |
| x3 | 0.6387 |
| x4 | 1.78 |
| t | 1.069 |

The value for `t` is the normalized variable `t0`. The physical design point value is 0.3993 × 1.069 ≈ 0.4268.

Partial factors are not calculated because `Ji1Problem.py` does not define `fractiles`.

### FORM Results (At Optimum)

| beta | pf | beta_count | hbeta_count | lsf_count | glsf_count | hlsf_count | min_method |
|---:|---:|---:|---:|---:|---:|---:|---|
| 2.001 | 0.02271 | 48 | 48 | 48 | 48 | 48 | equality_constrained_sqp |

### Notes Reported by Brinkpy

1. Validation: Stochastic variables definition and limit state function validation required 2 function calls.
2. Validation: Design problem validation required 2 calls to the design objective function.
3. Validation: Validation of the limit state function's analytic gradient and Hessian required 49 function calls.
4. Validation: Validation of the design objective function's analytic gradient and Hessian required 36 function calls.

## Interpretation Snapshot

- Starting from 0.15, the optimizer converged in `6` iterations and found `Lambda = 0.3993060389087408`, which is the mean of `t`.
- The reliability index is `2.000753109665796`, within the 0.001 tolerance of the target of 2.0.

!!! note "Comparison with the paper"
    The paper reports a mean of 0.400389 for `t`, which gives a reliability index just below 2.0. Brinkpy's 0.3993 gives a reliability index just above 2.0. Both are within the paper's convergence tolerance of 10⁻³.
