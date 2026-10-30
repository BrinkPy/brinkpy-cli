# Results Tables Reference

This page explains the columns of the tables in the `Results` worksheet of the Excel result file. The worked example pages in this section show these tables for specific runs and link here for the column meanings.

For where result files are saved and what each file contains, see [Result Files](../cli/results-files.md).

## FORM

### FORM Results

| Column | Meaning |
|---|---|
| `beta` | Reliability index (β) |
| `pf` | Probability of failure |
| `beta_count` | Number of calls to the function that calculates β |
| `hbeta_count` | Number of calculations of the Hessian of β |
| `lsf_count` | Number of limit state function calls |
| `glsf_count` | Number of limit state function gradient calculations |
| `hlsf_count` | Number of limit state function Hessian calculations |
| `nit` | Number of iterations used by SciPy's `minimize` function |
| `min_tries` | Number of attempts to find a solution. When an attempt fails, a new random starting point is tried. |
| `min_method` | SciPy `minimize` method used |
| `lsf_mult` | Lagrange multiplier for the limit state function |

### Stochastic Variable Inputs and FORM Failure Point Outputs

| Column | Meaning |
|---|---|
| `var_name` | Stochastic variable name |
| `var_type` | Distribution type |
| `mean` | Mean value |
| `std` | Standard deviation |
| `x` | Failure point in real space |
| `u` | Failure point in standard normal space |
| `alpha` | Direction cosines of the failure point (the alpha vector) |
| `importance` | Importance factors: the alpha vector transformed to real space and normalized to unit length (the γ vector in Equation 10 of Kim and Song, 2018, [→](https://doi.org/10.1016/j.ress.2018.01.005)) |

### User-Defined Correlation Inputs

| Column | Meaning |
|---|---|
| `var 1`, `var 2` | The pair of correlated variables |
| `cor_x` | The correlation you defined, in real space |
| `cor_z` | The equivalent correlation in standard normal space, from the Nataf transformation |

## SORM

### SORM Results

| Column | Meaning |
|---|---|
| `beta` | Reliability index (β) from SORM |
| `pf` | Probability of failure from SORM |
| `minR`, `Ravg`, `maxR` | Minimum, average, and maximum radius of curvature of the limit state surface at the design point |
| `minabsR` | Smallest absolute radius of curvature |
| `Ks` | Sum of the curvatures |
| `lsf_class` | Shape classification of the limit state surface (for example, `Convex ellipsoid`) |
| `sor_method` | SORM method used (profile option `sor_method`) |
| `sor_approx` | SORM approximation used (profile option `sor_approximation`) |
| `sor_fit_meth` | Fit method used (profile option `sor_fit_method`) |
| `fit_radius` | Distance from the most probable point to the sampled points, in every direction, when fitting the limit state surface by points. Used when `sor_fit_method` is `Kiureghian` or `ZhaoPF`. |
| `lsf_count` | Number of limit state function calls during SORM |

## Monte Carlo

### Monte Carlo Results

| Column | Meaning |
|---|---|
| `beta` | Reliability index (β) corresponding to the estimated probability of failure |
| `pf` | Estimated probability of failure |
| `cv` | Coefficient of variation of the estimated probability of failure |
| `max_cv` | Target coefficient of variation (profile option `mc_max_cv`) |
| `size` | Total number of samples |
| `%_removed` | Percentage of samples removed as out of bounds (profile option `mc_remove_oob`) |
| `cycles` | Number of sampling cycles |
| `auto_size` | Whether the sample size was chosen automatically (profile option `mc_n` is `null`) |
| `mc_with_is` | Whether importance sampling was used |

## Design

### Design Case Results

| Column | Meaning |
|---|---|
| `case` | Design case name (`default` when `DesignProblem` defines no `cases`) |
| `beta`, `pf` | Reliability index (β) and probability of failure reached at the design point |
| `lsf_count`, `glsf_count`, `hlsf_count`, `nit` | Same as in [FORM Results](#form-results) |

### Design Point Stochastic Variables

| Column | Meaning |
|---|---|
| `case` | Design case name (shown when the problem defines several cases) |
| `var_name` | Stochastic variable name |
| `x` | Design point value |
| `fractile` | Fractile used for the characteristic value (from `fractiles`) |
| `char_value` | Characteristic value, the variable's value at that fractile |
| `partial_factor` | Partial factor: `x` divided by `char_value` |

!!! note "Partial factor convention"
    Brinkpy computes every partial factor as the design point value divided by the characteristic value, for loads and resistances alike. Some textbooks (for example, Sørensen) divide the characteristic value by the design value for resistance variables, so a resistance factor reported by Brinkpy is the reciprocal of the textbook value.

### Load and Resistance Partial Factors

This table appears only when the limit state function returns load and resistance values (`LSFreturnsLandR = True`). Brinkpy evaluates the load and resistance at the design point values and at the characteristic values.

| Column | Meaning |
|---|---|
| `Load` | Load at the design point divided by load at the characteristic values |
| `Resistance` | Resistance at the design point divided by resistance at the characteristic values |

### Objective Optimization: Design Data

These tables appear when `DesignProblem` defines a `DesignObjectiveFunction`.

| Column | Meaning |
|---|---|
| `obj_value` | Value of the design objective function at the optimum |
| `target_beta`, `target_pf` | The reliability target (`TargetBeta` or `TargetPf`) |
| `actual_beta`, `actual_pf` | The reliability reached at the optimum |
| `use_sorm` | Whether SORM was used for the reliability constraint (`--use-sorm`) |
| `dof_count` | Number of design objective function calls |
| `beta_count`, `nit`, `min_tries`, `min_method` | Same as in [FORM Results](#form-results) |
| `br_mult` | Lagrange multiplier for the beta residual constraint. The optimizer requires the reliability index to match the target by driving the squared residual, `(beta - target_beta)^2`, to zero. |

### Objective Optimization: Design Variables Result

| Column | Meaning |
|---|---|
| `var_name` | Design variable name (from `DesignVariables`) |
| `opt_value` | Optimal value of the design variable |
| `lb`, `ub` | Lower and upper bounds of the design variable (from `DesignProblem`) |

The **FORM Results (At Optimum)** table uses the same columns as [FORM Results](#form-results), evaluated at the optimal design.
