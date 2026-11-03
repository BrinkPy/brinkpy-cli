# Results Tables Reference

This page explains the columns of the tables in the `Results` worksheet of the Excel result file. The worked example pages in this section show these tables for specific runs and link here for the column meanings.

For where result files are saved and what each file contains, see [Result Files](../cli/results-files.md).

The example pages omit some columns to keep their tables readable: `lb`, `ub`, and `truncated`, because none of the examples define bounds, and `param1`, `param2`, `z`, and `bnds_mult` in the FORM tables. Your own result files always include them.

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
| `mean`, `std` | Mean and standard deviation of the distribution |
| `param1`, `param2` | Natural parameters of the distribution |
| `lb`, `ub` | Lower and upper bounds of the variable. If the problem does not define them, the defaults are `-inf` and `inf`. |
| `truncated` | Whether the distribution is truncated to `[lb, ub]`. If the problem does not define it, the default is `False`. |
| `x` | Failure point in real space |
| `z` | Failure point in correlated standard normal space, the intermediate step between `x` and `u` in the Nataf transformation |
| `u` | Failure point in (uncorrelated) standard normal space |
| `alpha` | Direction cosines of the failure point (the alpha vector) |
| `importance` | Importance factors: the alpha vector transformed to real space and normalized to unit length (the γ vector in Equation 10 of Kim and Song, 2018, [→](https://doi.org/10.1016/j.ress.2018.01.005)) |
| `bnds_mult` | For an active bound, about how much the reliability index changes when the bound moves by one standard deviation: the Lagrange multiplier of the bound divided by 2|β|, since FORM minimizes β². Negative for an active lower bound, positive for an active upper bound. Empty when the bound is inactive (the value is below `1e-3`), when the variable has no bounds other than the natural limits of its distribution, or when FORM does not use the `trust-constr` optimizer (for example, when `LSFisSmooth` is `False`). |

### Correlations

The problem defines the correlations between stochastic variables in real space, with one of two keys of `StochasticVariables` (see [`StochasticVariables` Keys](index.md#stochasticvariables-keys)):

- `cor_list`: a list of `[var_1, var_2, value]` entries, for example `"cor_list": [["Y", "Z", 0.4]]` in `AT610Problem.py`.
- `cor`: the full n × n correlation matrix, in the same variable order as `name`, as in `Chan2Problem.py`.

FORM transforms the variables to standard normal space with the Nataf transformation, which changes the correlations. The result file reports both:

| Column | Meaning |
|---|---|
| `var 1`, `var 2` | The pair of correlated variables |
| `cor_x` | The correlation defined in the problem, in real space (an input) |
| `cor_z` | The equivalent correlation in standard normal space, calculated by the Nataf transformation (a result) |

When all the variables are normal, `cor_z` equals `cor_x`, so Brinkpy does not calculate it. The correlation matrix then appears instead as columns of the variable table: a `cor_x` column with the row variable's name, followed by one column per variable.

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
| `%_removed` | Percentage of samples removed because the limit state function returned NaN or Inf. This can happen when a sampled variable becomes NaN or Inf during the transformation from standard normal space to real space. |
| `cycles` | Number of sampling cycles |
| `auto_size` | Whether the sample size was chosen automatically (profile option `mc_n` is `null`) |
| `mc_with_is` | Whether importance sampling was used |

With importance sampling, more columns appear. Which ones depend on the proposal method (profile option `is_method`):

| Column | Shown for | Meaning |
|---|---|---|
| `method` | All methods | Importance sampling proposal method: `kde`, `mixture`, `mpp_normal`, or for Markov chain Monte Carlo (MCMC) `mcmc+kde` or `mcmc+mixture`, which adds the fitting method (profile option `is_mcmc_fit_method`) |
| `bandwidth` | `kde`, `mcmc+kde` | Kernel density estimation (KDE) bandwidth used for the proposal distribution (profile option `is_kde_bandwidth`) |
| `fit_samples` | `kde`, `mixture` | Number of samples used to fit the proposal distribution (profile option `is_fit_samples`) |
| `components` | `mixture` | Number of Gaussian mixture components (profile option `is_mixture_components`) |
| `chains` | `mcmc` | Number of MCMC chains (profile option `is_mcmc_chains`) |
| `length` | `mcmc` | Number of samples kept from each chain, after burn-in and thinning (profile option `is_mcmc_chain_length`) |
| `burn_in` | `mcmc` | Number of initial steps discarded from each chain (profile option `is_mcmc_burnin`) |
| `thinning` | `mcmc` | Thinning interval: after burn-in, every `thinning`-th step of each chain is kept (profile option `is_mcmc_thinning`) |

With `mpp_normal`, Brinkpy first runs FORM to find the most probable point (MPP), so the worksheet also includes a [FORM Results](#form-results) table.

### Stochastic Variables Definition

| Column | Meaning |
|---|---|
| `var_name`, `var_type` | Stochastic variable name and distribution type |
| `mean`, `std` | Mean and standard deviation of the distribution |
| `param1`, `param2` | Natural parameters of the distribution |
| `lb`, `ub` | Lower and upper bounds of the variable. If the problem does not define them, the defaults are `-inf` and `inf`. |
| `truncated` | Whether the distribution is truncated to `[lb, ub]`. If the problem does not define it, the default is `False`. |

### Monte Carlo Variable Statistics and Correlations

| Column | Meaning |
|---|---|
| `var_name` | Stochastic variable name |
| `mean`, `std` | Mean and standard deviation of the samples |
| `%_oob` | Percentage of that variable's samples outside its bounds |
| `cor_x` and the columns after it | The sample correlation matrix, in real space. `cor_x` repeats the row variable's name, and each following column is named after a variable. Each cell is the sample correlation between the row variable and the column variable. |

With importance sampling, these statistics describe the samples drawn from the proposal distribution, so they do not match the original input distributions.

### Importance Sampling Method-Specific Results

For the `mixture` and `mcmc` methods, the worksheet adds a section titled **Importance sampling method-specific results**, followed by the method name. The `kde` and `mpp_normal` methods do not add this section.

#### Gaussian Mixture Components

With `mixture`, the section describes the fitted Gaussian mixture. Columns `1`, `2`, and so on are the mixture components.

| Table | Meaning |
|---|---|
| Weight (per mixture component) | Weight of each component in the mixture. The weights add up to 1. Components with very small weights contribute almost nothing to the proposal distribution. |
| Mean on the u-space | Mean of each component for each variable, in standard normal space (u-space) |
| Std on the u-space | Standard deviation of each component for each variable, in u-space |
| Mean on the x-space, Std on the x-space | The same values transformed to the original variable space (x-space), for diagnostics |

#### MCMC Diagnostics

With `mcmc`, the section has one table of statistics for the norm of the MCMC samples in u-space, that is, each sample's distance from the origin. The statistics are calculated with [ArviZ](https://www.arviz.org/), and the convergence measures follow [Vehtari et al. (2021)](https://doi.org/10.1214/20-BA1221).

| Column | Meaning |
|---|---|
| `mean`, `sd` | Mean and standard deviation of the sample norms |
| `eti89_lb`, `eti89_ub` | Lower and upper limits of the 89% equal-tailed interval of the sample norms |
| `ess_bulk` | Effective sample size for the center of the distribution: the number of independent samples that would give the same precision as the correlated MCMC samples |
| `ess_tail` | Effective sample size for the tails of the distribution |
| `r_hat` | Convergence measure that compares the variation within each chain to the variation between chains. Values close to 1 mean the chains agree. Values below 1.01 are often recommended. |
| `mcse_mean`, `mcse_sd` | Monte Carlo standard errors of `mean` and `sd` |

Brinkpy reports these values but does not enforce a limit. If `r_hat` is too high or the effective sample sizes are too low, increase `is_mcmc_chain_length`, `is_mcmc_burnin`, or `is_mcmc_chains` in the profile and run again. For a worked example, see [MCMC Importance Sampling](simulate/importance-sampling-mcmc.md).

## Design

### Design Results

| Column | Meaning |
|---|---|
| `target_beta`, `target_pf` | The reliability target. The problem defines one (`TargetBeta` or `TargetPf`), and Brinkpy calculates the other. |

For Inverse FORM, the workbook then repeats the tables below for each design case, under a heading with the case name (`Design case 'default'` when `DesignProblem` defines no `cases`). The example pages combine the cases into one table with a `case` column.

### Inverse FORM Results

| Column | Meaning |
|---|---|
| `beta`, `pf` | Distance of the design point from the origin in standard normal space, and the corresponding probability of failure. Inverse FORM constrains this distance to the target, so `beta` equals `target_beta`. It is the reliability index of the design only when `lsf_value` is close to zero. |
| `lsf_value` | Limit state function value at the design point. Inverse FORM finds the lowest value of the limit state function among all points at the target reliability index, so the sign shows whether the design meets the target. A value close to zero means the design meets the target exactly. A positive value means it exceeds the target, and a negative value means it falls short. |
| `bsr_mult` | Lagrange multiplier for the beta squared residual constraint. The optimizer requires the reliability index to match the target by driving the residual `beta`² − `target_beta`² to zero. |

The table also has the columns `lsf_count`, `glsf_count`, `hlsf_count`, `beta_count`, `hbeta_count`, `nit`, `min_tries`, and `min_method`, with the same meaning as in [FORM Results](#form-results).

### Design Point Stochastic Variables

| Column | Meaning |
|---|---|
| `var_name` | Stochastic variable name |
| `x` | Design point value |
| `fractile` | Fractile used for the characteristic value (from `fractiles`) |
| `char_value` | Characteristic value, the variable's value at that fractile |
| `partial_factor` | Partial factor: `x` divided by `char_value` |

!!! note "Partial factor convention"
    Brinkpy computes every partial factor as the design point value divided by the characteristic value, for loads and resistances alike. Some textbooks (for example, Sørensen) divide the characteristic value by the design value for resistance variables, so a resistance factor reported by Brinkpy is the reciprocal of the textbook value.

### Inverse FORM Stochastic Variables

The Excel file also includes a table of the stochastic variables and the Inverse FORM design point. It has the same columns as [Stochastic Variable Inputs and FORM Failure Point Outputs](#stochastic-variable-inputs-and-form-failure-point-outputs), plus the correlation matrix when the problem defines correlations (see [Correlations](#correlations)). Only the meaning of `bnds_mult` differs:

| Column | Meaning |
|---|---|
| `bnds_mult` | For an active bound, about how much the limit state function at the design point changes when the bound moves by one standard deviation, expressed in standard deviations. Inverse FORM minimizes the limit state function, so its Lagrange multipliers have the units of the limit state function. Brinkpy divides them by the norm of the limit state function's gradient in standard normal space, which puts them on the same scale as the reliability index. The sign and the cases where the value is empty are the same as in FORM. |

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
| `br_mult` | Lagrange multiplier for the beta residual constraint. The optimizer requires the reliability index to match the target by driving the squared residual, (`beta` − `target_beta`)², to zero. |

### Objective Optimization: Design Variables Result

| Column | Meaning |
|---|---|
| `var_name` | Design variable name (from `DesignVariables`) |
| `opt_value` | Optimal value of the design variable |
| `lb`, `ub` | Lower and upper bounds of the design variable (from `DesignProblem`) |
| `bnds_mult` | For an active bound, about the relative change in the design objective function when the bound moves by one unit of the design variable: the Lagrange multiplier of the bound divided by the absolute value of `obj_value`. The value depends on the units of the design variable. Negative for an active lower bound, positive for an active upper bound. Empty when the bound is inactive (the value is below `1e-3`), when no design variable has a finite bound, or when the design optimization does not use the `trust-constr` optimizer. |

The **FORM Results (At Optimum)** table uses the same columns as [FORM Results](#form-results), evaluated at the optimal design.
