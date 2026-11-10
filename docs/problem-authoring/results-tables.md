# Results Tables Reference

This page explains the columns of the tables in the `Results` worksheet of the Excel result file. The worked example pages in this section show these tables for specific runs and link here for the column meanings.

For where result files are saved and what each file contains, see [Result Files](../cli/results-files.md).

The example pages omit some columns to keep their tables readable: `lb`, `ub`, and `truncated` of the stochastic variables, `param1`, `param2`, and `z` in the FORM tables, and the `bnds_mult` and `constr_mult` columns. Your own result files always include them.

## How to Use This Page

The `Results` worksheet starts each table with a heading. Find the heading in the table below, or search this page for the column name.

<div class="wrap-first-column" markdown>

| Heading in the worksheet | Section on this page |
|---|---|
| `Deterministic variables data:` | The names and values of the deterministic variables |
| `FORM results:` | [FORM Results](#form-results), also used for the FORM results at the optimum of a design |
| `Stochastic variables data and most probable point (failure point) results from FORM:` | [Stochastic Variable Inputs and FORM Failure Point Outputs](#stochastic-variable-inputs-and-form-failure-point-outputs), followed by [Correlations](#correlations) when the problem defines them |
| `Stochastic variables constraints results from FORM:` | [Stochastic Variables Constraints](#stochastic-variables-constraints) |
| `SORM results:` | [SORM Results](#sorm-results) |
| `SORM limit state function fit parameters:` | Values that depend on the SORM method (see [SORM Results](#sorm-results)) |
| `Monte Carlo results:` or `Monte Carlo results (with importance sampling):` | [Monte Carlo Results](#monte-carlo-results), followed by [Monte Carlo Variable Statistics and Correlations](#monte-carlo-variable-statistics-and-correlations) |
| `Stochastic variables data:` | [Stochastic Variables Definition](#stochastic-variables-definition) |
| `Importance sampling method-specific results (...):` | [Importance Sampling Method-Specific Results](#importance-sampling-method-specific-results) |
| `Design results:` | [Design Results](#design-results). The tables of each design case follow under `Design case '...':`. |
| `Inverse FORM results:` | [Inverse FORM Results](#inverse-form-results) |
| `Design point stochastic variables result:` | [Design Point Stochastic Variables](#design-point-stochastic-variables) |
| `Stochastic variables data and most probable point (failure point) results from Inverse FORM:` | [Inverse FORM Stochastic Variables](#inverse-form-stochastic-variables) |
| `Stochastic variables constraints results from Inverse FORM:` | [Inverse FORM Stochastic Variables Constraints](#inverse-form-stochastic-variables-constraints) |
| `Load and resistance partial factors:` | [Load and Resistance Partial Factors](#load-and-resistance-partial-factors) |
| `Design data:` | [Objective Optimization: Design Data](#objective-optimization-design-data) |
| `Design variables result:` | [Objective Optimization: Design Variables Result](#objective-optimization-design-variables-result) |
| `Design constraints result:` | [Objective Optimization: Design Constraints Result](#objective-optimization-design-constraints-result) |

</div>

The `bnds_mult` and `constr_mult` columns appear in several tables, with a different scaling in each. See [Lagrange Multipliers for Bounds and Constraints](#lagrange-multipliers-for-bounds-and-constraints).

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
| `min_tries` | Number of attempts to find a solution. When an attempt fails, a new random starting point is tried. When the problem has bounds and the optimizer is SciPy's `trust-constr`, Brinkpy restarts it once from its first result to make the solution accurate near the bounds. The restart also counts as an attempt. |
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
| `bnds_mult` | For an active bound, about how much the reliability index changes per unit change in the bound, in the variable's own units. See [Lagrange Multipliers for Bounds and Constraints](#lagrange-multipliers-for-bounds-and-constraints). |

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

### Stochastic Variables Constraints

This table appears when `StochasticVariables` defines `constraints` (see [Constraints on Stochastic Variables](index.md#constraints-on-stochastic-variables)). It has one row per output of each constraint function, evaluated at the failure point.

| Column | Meaning |
|---|---|
| `constr_name` | Name of the constraint function |
| `constr_row` | Output number within the constraint function, starting at 1. A function that returns one value has only row 1. |
| `lb`, `ub` | Lower and upper limits of that output, from the problem file. If the constraint leaves one out, the default is `-inf` or `inf`. |
| `value` | Value of that output at the failure point |
| `constr_count` | Number of calls to the constraint function. It appears once per function, on its first row. |
| `constr_mult` | For an active limit, about how much the reliability index changes per unit change in the limit, in the units of the constraint's output. See [Lagrange Multipliers for Bounds and Constraints](#lagrange-multipliers-for-bounds-and-constraints). |

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

The worksheet also includes a table titled `SORM limit state function fit parameters:`. It holds intermediate values that depend on the SORM method (profile option `sor_method`), for users who want to examine a method in detail. They are not described on this page. See the references in [SORM References](../profiles/profile-reference.md#sorm-references) for their meaning.

## Monte Carlo

### Monte Carlo Results

| Column | Meaning |
|---|---|
| `beta` | Reliability index (β) corresponding to the estimated probability of failure |
| `pf` | Estimated probability of failure |
| `cv` | Coefficient of variation of the estimated probability of failure |
| `max_cv` | Target coefficient of variation (profile option `mc_max_cv`) |
| `size` | Total number of samples |
| `%_removed` | Percentage of samples removed from the statistics. A sample is removed when the limit state function returns a value that is not a finite real number (NaN, Inf or complex), which can happen when a sampled variable becomes NaN or Inf during the transformation from standard normal space to real space. When the profile option `mc_remove_oob` is `true`, a sample is also removed when it falls outside the bounds (`lb`, `ub`) of a stochastic variable or violates a constraint on the stochastic variables. Brinkpy reports the share removed by each constraint in a note. |
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
| `bnds_mult` | For an active bound, about how much the limit state function at the design point changes per unit change in the bound, in the variable's own units. See [Lagrange Multipliers for Bounds and Constraints](#lagrange-multipliers-for-bounds-and-constraints). |

### Inverse FORM Stochastic Variables Constraints

When `StochasticVariables` defines `constraints`, the Excel file also includes a constraints table for the Inverse FORM design point. It has the same columns as [Stochastic Variables Constraints](#stochastic-variables-constraints), evaluated at the design point. Only the meaning of `constr_mult` differs:

| Column | Meaning |
|---|---|
| `constr_mult` | For an active limit, about how much the limit state function at the design point changes per unit change in the limit, in the units of the constraint's output. See [Lagrange Multipliers for Bounds and Constraints](#lagrange-multipliers-for-bounds-and-constraints). |

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
| `bnds_mult` | For an active bound, about how much the design objective function changes per unit change in the bound. See [Lagrange Multipliers for Bounds and Constraints](#lagrange-multipliers-for-bounds-and-constraints). |

### Objective Optimization: Design Constraints Result

This table appears when `DesignProblem` defines `DesignConstraints` (see [Design Constraints](design/design-keys.md#design-constraints)). It has one row per output of each design constraint function, evaluated at the optimum.

| Column | Meaning |
|---|---|
| `constr_name`, `constr_row`, `lb`, `ub`, `value`, `constr_count` | Same as in [Stochastic Variables Constraints](#stochastic-variables-constraints), evaluated at the optimal design |
| `constr_mult` | For an active limit, about how much the design objective function changes per unit change in the limit, in the units of the constraint's output. See [Lagrange Multipliers for Bounds and Constraints](#lagrange-multipliers-for-bounds-and-constraints). |

The **FORM Results (At Optimum)** table uses the same columns as [FORM Results](#form-results), evaluated at the optimal design.

## Lagrange Multipliers for Bounds and Constraints

The `bnds_mult` and `constr_mult` columns show how strongly each bound or constraint limit affects the result. Both come from the Lagrange multipliers that SciPy's `trust-constr` optimizer reports, but Brinkpy scales them differently in each table, so that each value is a change in the quantity being minimized per unit change in the bound or limit:

| Table | Column | Value | Change in, per unit change in the bound or limit |
|---|---|---|---|
| [Stochastic Variable Inputs and FORM Failure Point Outputs](#stochastic-variable-inputs-and-form-failure-point-outputs) | `bnds_mult` | Multiplier divided by 2\|β\|, since FORM minimizes β², and converted from standard normal space to the variable's units | Reliability index |
| [Stochastic Variables Constraints](#stochastic-variables-constraints) | `constr_mult` | Multiplier divided by 2\|β\| | Reliability index |
| [Inverse FORM Stochastic Variables](#inverse-form-stochastic-variables) | `bnds_mult` | Multiplier converted from standard normal space to the variable's units | Limit state function at the design point |
| [Inverse FORM Stochastic Variables Constraints](#inverse-form-stochastic-variables-constraints) | `constr_mult` | Multiplier as SciPy reports it | Limit state function at the design point |
| [Objective Optimization: Design Variables Result](#objective-optimization-design-variables-result) | `bnds_mult` | Multiplier as SciPy reports it | Design objective function |
| [Objective Optimization: Design Constraints Result](#objective-optimization-design-constraints-result) | `constr_mult` | Multiplier as SciPy reports it | Design objective function |

FORM and Inverse FORM search in standard normal space, so the multiplier of a bound on a stochastic variable is converted to the variable's units. A constraint limit applies to the output of the constraint function, in its own units, and design variables are deterministic, so the other values need no conversion.

The same rules apply in every table:

- **Sign.** Negative for an active lower bound or limit, positive for an active upper one. Relaxing an active bound or limit lowers the quantity being minimized: the design objective function, the limit state function at the Inverse FORM design point, or a positive reliability index in FORM. A negative reliability index rises toward zero instead.
- **Active or inactive.** Brinkpy decides from the distance to the bound, not from the size of the multiplier. A bound counts as active when the point lies within 1% of it, or within 0.01 when the bound is between −1 and 1 (see [Bounds and Truncation](index.md#bounds-and-truncation)). For a constraint, the same rule applies to the constraint's `value`. For an inactive bound or limit, the value is close to zero but not exactly zero. Brinkpy lists the active bounds and limits, with these values, in a note.
- **Equalities.** A design constraint whose `lb` equals its `ub` is always active, so its multiplier is usually not zero. The note does not list it.
- **Empty values.** The values are empty when the optimizer is not `trust-constr` (for example, FORM when `LSFisSmooth` is `False`), in FORM when β is zero, for a stochastic variable with no bounds other than the natural limits of its distribution, and for design variables when none has a finite bound.
