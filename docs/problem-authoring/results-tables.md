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
