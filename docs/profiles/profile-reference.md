---
description: "A reference of every option in a Brinkpy YAML profile: the analysis, design, and simulation settings, plotting options, and reporting settings."
---

# Profile Options Reference

This page provides a complete reference for all options available in YAML profile files. Profiles control configuration for analysis, design, and simulation runs, including plotting options and reporting settings.

## Profile Structure

A profile YAML file starts with two identifying fields, followed by four option sections:

- `name`: The profile name
- `description`: A short description of the profile
- `reliability_options`: Reliability analysis, SORM, Monte Carlo, importance sampling, and optimization settings
- `lsf_plot_options`: Limit state function (LSF) plot settings
- `rfad_plot_options`: Reliability-based failure assessment diagram (RFAD) settings
- `reporting_options`: Report generation settings

---

## Reliability Options

Options for reliability calculations and related numerical settings. This section collects tolerances, algorithm choices, finite-difference settings, plotting flags, Monte Carlo controls and various checks used across FORM, SORM, inverse problems and design optimization routines.

### General Reliability Settings

| Option | Type | Default | Values | Description |
|--------|------|---------|--------|-------------|
| `alpha_direction` | str | `"outward"` | `"outward"`, `"inward"` | Sign convention for the alpha vector (see [Alpha Direction](#alpha-direction)) |
| `use_nearest_correlation` | bool | `false` | - | Controls fallback behavior when Cholesky decomposition of the correlation matrix fails. If `false`, the run stops with an error. If `true`, Brinkpy replaces the matrix with a nearby positive definite correlation matrix, using the spectral method of [Rebonato and Jäckel (2000)](https://doi.org/10.21314/JOR.2000.023). See also [Correlation Matrix Conditioning](../problem-authoring/recommended-texts.md#correlation-matrix-conditioning). |
| `max_minimize_attempts` | int | `8` | [1, 12] | Maximum number of attempts for each FORM, Inverse FORM, and design optimization. An attempt that fails is followed by a new one from a random starting point, and a result that is not yet accurate enough is refined by a restart. Both count as attempts. The FORM, Inverse FORM, and design results report the attempts used as [`min_tries`](../problem-authoring/results-tables.md#form-results). |

#### Alpha Direction

The alpha vector is the unit vector normal to the limit state surface at the failure point in standard normal space (see [FORM Results](../problem-authoring/results-tables.md#form-results)). Authors define it with either sign. The choice is a convention and does not depend on how the limit state function is written.

- `"outward"`: alpha is the negative gradient of the limit state function divided by its length. It points from the origin toward the failure point, so the failure point is β times alpha. Tvedt (1990, Equation 6) uses this definition.
- `"inward"`: alpha is the gradient divided by its length. It points from the failure point back toward the origin, so the failure point is −β times alpha. Ang and Tang (1990, Equation 6.16b) use this definition.

The setting changes the signs of the alpha values and the importance factors only. It does not change β, the probability of failure, or the failure point.

References:

- Ang, A. H.-S., and Tang, W. H. (1990). *Probability Concepts in Engineering Planning and Design, Vol. II*. John Wiley and Sons.
- Tvedt, L. (1990). "Distribution of quadratic forms in normal space—application to structural reliability." *J. Eng. Mech.*, ASCE, 116(6), 1183–1197. [→](https://ascelibrary.org/doi/10.1061/%28ASCE%290733-9399%281990%29116%3A6%281183%29)

### FORM and Inverse FORM Settings

These settings apply to both FORM and Inverse FORM.

Used by: `analyze`, `design`, and `simulate` when FORM runs.

!!! info "Optimization algorithm"
    Brinkpy CLI does not use the traditional Hasofer-Lind Rackwitz-Fiessler (HL-RF) algorithm found in many reliability textbooks and commercial tools. Instead, FORM and Inverse FORM use SciPy's [`minimize`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html), which handles bounds and constraints that the classical HL-RF algorithm cannot. The problem's `LSFisSmooth` key chooses the optimizer (see [Smooth and Non-Smooth Functions](../problem-authoring/index.md#smooth-and-non-smooth-functions)).

| Option | Type | Default | Range | Description |
|--------|------|---------|-------|-------------|
| `form_xtol` | float | `0.0001` | [1e-8, 1e-2] | Tolerance for FORM termination (variable changes) |
| `form_gtol` | float | `0.0001` | [1e-8, 1e-2] | Tolerance for FORM termination (Lagrangian gradient norm changes) |
| `form_maxiter` | int | `1000` | [1, 10000] | Maximum iterations for FORM |
| `form_random_start` | bool | `false` | - | Starting point of the first FORM and Inverse FORM attempt. If `false`, the search starts at the median of every variable (u = 0 in standard normal space). If `true`, it starts at a random point drawn from the standard normal distribution. Either way, a start outside the variable bounds is moved just inside them. Later attempts always start from random points (see `max_minimize_attempts`). |
| `form_seed` | int or null | `null` | - | Random seed for FORM/Inverse FORM random starts |

### Design Optimization Settings

Used by: `design` when the problem defines an objective function.

| Option | Type | Default | Range | Description |
|--------|------|---------|-------|-------------|
| `design_xtol` | float | `0.001` | [1e-8, 1e-2] | Tolerance for design optimization termination (variable changes) |
| `design_gtol` | float | `0.001` | [1e-8, 1e-2] | Tolerance for design optimization termination (Lagrangian gradient norm changes) |
| `design_maxiter` | int | `1000` | [1, 10000] | Maximum iterations for design optimization |
| `design_random_start` | bool | `false` | - | Starting point of the first design optimization attempt. If `false`, the optimization starts at the problem's [`InitialGuess`](../problem-authoring/design/design-keys.md). If `true`, Brinkpy adds a small random step to each value of `InitialGuess`, with a standard deviation of 10% of the range between the variable's bounds, or 10% of the value (at least 0.1) when the variable is not bounded on both sides. Either way, the start is moved inside the bounds and, if needed, to a point that satisfies the design constraints. |
| `design_seed` | int or null | `null` | - | Random seed for design optimization random starts |

!!! note "Later attempts"
    After an attempt fails, the next one starts from a random point farther from `InitialGuess`, whatever `design_random_start` is: anywhere between the bounds, or with steps five times larger when a variable is not bounded on both sides (see `max_minimize_attempts`). `design_random_start` also makes the starting values of the Inverse SORM search random.

### SORM Settings

Used by: `analyze --include-sorm`, `simulate --include-sorm`, and `design --use-sorm`.

| Option | Type | Default | Values | Description |
|--------|------|---------|--------|-------------|
| `sor_method` | str | `"SOSPA_H"` | `"Breitung"`, `"Tvedt3T"`, `"TvedtSI"`, `"TvedtDI"`, `"Hohenbichler"`, `"Koyluoglu"`, `"ZhaoEmpirical"`, `"SOSPA_L"`, `"SOSPA_H"`, `"IFFT"` | SORM method to use |
| `sor_approximation` | str | `"Paraboloid"` | `"Paraboloid"`, `"Taylor2"` | SORM approximation type |
| `sor_fit_method` | str or null | `null` | `"FiniteDiff"`, `"ZhaoPF"`, `"Kiureghian"`, `"SR1"`, `"AnalyticAll"`, `null` (auto) | Method for SORM limit state function fitting |
| `sor_fit_delta_factor` | float | `1.0` | [0.1, 10.0] | Factor used to scale the method-recommended delta when numerically estimating SORM fit parameters for ZhaoPF and Kiureghian methods |
| `sor_fdm` | str | `"forward"` | `"central"`, `"forward"`, `"backward"` | Finite-difference method for gradient and Hessian (used when `sor_fit_method` is `FiniteDiff` and `LSFisVectorized` is `False`) |
| `sor_fdm_hess_form` | str | `"full"` | `"full"`, `"diagonal"` | Hessian form for finite-difference approximation (used when `sor_fit_method` is `FiniteDiff`) |
| `force_curvatures` | bool | `false` | - | Force curvature computations even if not strictly required by selected SORM options, for example with `ZhaoEmpirical`. Set it to `true` to have the curvatures and the minimum and maximum radii of curvature reported in the Excel file. |
| `qn_epsilon` | float | `1e-8` | [1e-8, 1e-2] | Tolerance used by the quasi-Newton SR1 (Symmetric Rank 1) update when `sor_fit_method` is set to `SR1` |

#### SORM References

Use these references as starting points for method details and derivation nuances. Keep in mind that explanations on this page are intentionally brief and implementation-focused.

**`sor_method`**

- `"Breitung"`: Breitung, K. (1984). "Asymptotic approximations for multinormal integrals." *J. Eng. Mech.*, ASCE, 110(3), 357–366. [→](https://ascelibrary.org/doi/10.1061/%28ASCE%290733-9399%281984%29110%3A3%28357%29)
- `"Tvedt3T"`, `"TvedtSI"`, `"TvedtDI"`: Although not the original reference, Der Kiureghian, A., Lin, H.-Z., and Hwang, S.-J. (1987) provides a thorough description of these methods in Appendix I — "Second-order reliability approximations." *J. Eng. Mech.*, ASCE, 113(8), 1208–1225. [→](https://ascelibrary.org/doi/10.1061/%28ASCE%290733-9399%281987%29113%3A8%281208%29)
- `"Hohenbichler"`: Hohenbichler, M., and Rackwitz, R. (1988). "Improvement of second-order reliability estimates by importance sampling." *J. Eng. Mech.*, ASCE, 114(12), 2195–2199. [→](https://ascelibrary.org/doi/10.1061/%28ASCE%290733-9399%281988%29114%3A12%282195%29)
- `"Koyluoglu"`: Köylüoğlu, H. U., and Nielsen, S. R. K. (1994). "New approximations for SORM integrals." *Structural Safety*, 13(4), 235–246. [→](https://www.sciencedirect.com/science/article/pii/0167473094900310)
- `"ZhaoEmpirical"`: Zhao, Y.-G., and Ono, T. (1999a). "New approximations for SORM: Part 1." *J. Eng. Mech.*, ASCE, 125(1), 79–85. [→](https://ascelibrary.org/doi/10.1061/%28ASCE%290733-9399%281999%29125%3A1%2879%29)
- `"SOSPA_L"`, `"SOSPA_H"`:
    - Hu, Z., and Du, X. (2018). "Saddlepoint approximation reliability method for quadratic functions in normal variables." *Structural Safety*, 71, 24–32. [→](https://www.sciencedirect.com/science/article/pii/S0167473017301169)
    - Du, X., and Sudjianto, A. (2004). "A saddlepoint approximation method for uncertainty analysis." *Proc. ASME IDETC/CIE 2004*, Paper DETC2004-57269, pp. 445–452. [→](https://asmedigitalcollection.asme.org/IDETC-CIE/proceedings-abstract/IDETC-CIE2004/46946/445/308224)
    - Daniels, H. E. (1987). "Tail probability approximations." *International Statistical Review*, 55(1), 37–48. [→](https://doi.org/10.2307/1403269)
    - Chen, Q., and Giles, D. E. (2008). "General saddlepoint approximations: Application to the Anderson-Darling test statistic." *Communications in Statistics – Simulation and Computation*, 37(4), 789–804. [→](https://doi.org/10.1080/03610910701730141)
- `"IFFT"`:
    - Zhao, Y.-G., and Ono, T. (1999b). "New approximations for SORM: Part 2." *J. Eng. Mech.*, ASCE, 125(1), 86–93. [→](https://ascelibrary.org/doi/10.1061/%28ASCE%290733-9399%281999%29125%3A1%2886%29)
    - Tvedt, L. (1990). "Distribution of quadratic forms in normal space—application to structural reliability." *J. Eng. Mech.*, ASCE, 116(6), 1183–1197. [→](https://ascelibrary.org/doi/10.1061/%28ASCE%290733-9399%281990%29116%3A6%281183%29)
    - Der Kiureghian, A., Lin, H.-Z., and Hwang, S.-J. (1987). "Second-order reliability approximations." *J. Eng. Mech.*, ASCE, 113(8), 1208–1225. [→](https://ascelibrary.org/doi/10.1061/%28ASCE%290733-9399%281987%29113%3A8%281208%29)

**`sor_approximation`**

- `Paraboloid`: Local quadratic fit of the failure surface at the design point, using principal curvatures.
- `Taylor2`: Second-order Taylor expansion of the limit-state function at the design point.
- Reference: Tvedt, L. (1990). "Distribution of quadratic forms in normal space—application to structural reliability." *J. Eng. Mech.*, ASCE, 116(6), 1183–1197. [→](https://ascelibrary.org/doi/10.1061/%28ASCE%290733-9399%281990%29116%3A6%281183%29)

**`sor_fit_method`**

- `FiniteDiff`: numerical gradient and Hessian from [`scipy.differentiate`](https://docs.scipy.org/doc/scipy/reference/differentiate.html) when `LSFisVectorized` is `True`, and from [numdifftools](https://pypi.org/project/numdifftools/) otherwise. `scipy.differentiate` chooses its own step sizes, so `sor_fdm` applies only to numdifftools.
- `SR1`: quasi-Newton symmetric rank-one update — [Wikipedia: Symmetric rank-one](https://en.wikipedia.org/wiki/Symmetric_rank-one). It builds the Hessian from the gradients computed during FORM, so it needs no extra limit state function calls. The gradients come from the points FORM visits on its way to the design point, so the curvatures are approximate, even when every direction is measured. To check an SR1 result, run SORM again with `sor_fit_method: "FiniteDiff"` and compare. It requires `LSFisSmooth = True` (see [Smooth and Non-Smooth Functions](../problem-authoring/index.md#smooth-and-non-smooth-functions)).
- `Kiureghian`: point-fitting procedure following Der Kiureghian, A. (2022). *Structural and System Reliability*. Cambridge University Press. [→](https://doi.org/10.1017/9781108991889)
- `ZhaoPF`: point-fitting procedure following Zhao, Y.-G., and Ono, T. (1999b). "New approximations for SORM: Part 2." *J. Eng. Mech.*, ASCE, 125(1), 86–93. [→](https://ascelibrary.org/doi/10.1061/%28ASCE%290733-9399%281999%29125%3A1%2886%29)
- `AnalyticAll`: uses user-provided analytic gradient and Hessian from the problem definition.
- `null` (auto): Brinkpy uses `AnalyticAll` if the limit state function returns both its gradient and Hessian, because exact derivatives give the most accurate fit. Otherwise it uses the most accurate of the remaining methods for the chosen approximation: `Kiureghian` for `Paraboloid` and `ZhaoPF` for `Taylor2`. A validation note in the results reports which method was used.

**`sor_fit_delta_factor`**

- Applies to `ZhaoPF` and `Kiureghian` fit methods as a scaling factor on the method-recommended point-fitting step size. Keep default unless Brinkpy diagnostics suggest adjustment.

### IFFT Settings (for IFFT-based SORM)

Used by: SORM runs with `sor_method: "IFFT"`.

| Option | Type | Default | Range | Description |
|--------|------|---------|-------|-------------|
| `ifft_std_domain` | float | `16.0` | [2, 24] | Standard deviations covered when computing IFFT of characteristic functions |
| `ifft_n` | int | `4096` | [2^8, 2^16], powers of 2 | Number of points used in IFFT |
| `plot_ifft_funcs` | bool | `true` | - | Generate diagnostic plots for IFFT operations |

### SOSPA Settings (for SOSPA-based SORM)

Used by: SORM runs with `sor_method: "SOSPA_L"` or `"SOSPA_H"`.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `plot_sospa_funcs` | bool | `true` | Generate diagnostic plots for SOSPA characteristic functions and derivatives |

### Monte Carlo Settings

Used by: `analyze --include-mc` and `simulate`.

| Option | Type | Default | Range | Description |
|--------|------|---------|-------|-------------|
| `mc_n` | float or null | `null` | [1e3, 1e8] or `null` (auto) | Total number of Monte Carlo samples, spread over at least three cycles. `null` chooses the number of samples automatically (see below) |
| `mc_max_cv` | float | `0.05` | [0.01, 1.0] | If `mc_n` is `null`, Monte Carlo runs in cycles until the coefficient of variation (CV) of the estimated failure probability is <= `mc_max_cv` and at least three cycles have run. Halving `mc_max_cv` takes about four times as many samples |
| `mc_seed` | int or null | `null` | - | Random seed for Monte Carlo simulations. Set a value for repeatable results, or leave as `null` to allow small run-to-run differences |
| `mc_remove_oob` | bool | `true` | - | Remove out-of-bounds samples during Monte Carlo simulation (bounds or constraint violations) |

When `mc_n` is `null`, Brinkpy sizes the run to reach a CV of at most `mc_max_cv`:

- `analyze --include-mc` runs FORM, and SORM with `--include-sorm`, before Monte Carlo. From their estimate of the probability of failure, Brinkpy computes the number of samples needed, adds a margin because the estimate is approximate, and spreads them over at least three cycles. Each cycle size is rounded down to its leading digit, for example from 1,433 to 1,000 samples.
- `simulate` runs Monte Carlo first, even with `--include-form`, so there's no estimate yet. Brinkpy sizes the cycles as the run goes. The first cycle has 10,000 samples. After each cycle, Brinkpy uses the probability of failure estimated so far to compute how many more samples are needed, and runs them all in the next cycle. While no sample has failed yet, each next cycle is 10 times larger than the last.

In both cases the run continues until at least three cycles have run and the CV is at most `mc_max_cv`. The memory available on the server also limits the size of each cycle. Importance sampling chooses its sample sizes differently (see [Importance Sampling Settings](#importance-sampling-settings)).

### Importance Sampling Settings

Used by: `analyze --mc-with-is` and `simulate --mc-with-is`.

| Option | Type | Default | Values/Range | Description |
|--------|------|---------|--------------|-------------|
| `is_method` | str | `"kde"` | `"kde"`, `"mixture"`, `"mcmc"`, `"mpp_normal"` | Importance sampling proposal method: kernel density estimation (`kde`), Gaussian mixture (`mixture`), Markov chain Monte Carlo (`mcmc`), or a normal distribution centered at the most probable point (`mpp_normal`) |
| `is_kde_bandwidth` | str or float | `"scott"` | `"scott"`, `"silverman"` or positive float | Bandwidth selection method for KDE or numeric value |
| `is_mixture_components` | int | `6` | [1, 16] | Number of mixture components for mixture importance sampling methods |
| `is_mixture_cov_type` | str | `"full"` | `"full"`, `"tied"`, `"diag"`, `"spherical"` | Covariance type for mixture importance sampling methods |
| `is_fit_samples` | int | `2000` | [100, 100000] | Number of samples to collect for fitting the proposal distribution (for KDE and mixture importance sampling) |

### MCMC Importance Sampling Settings

Used by: importance sampling runs with `is_method: "mcmc"`.

| Option | Type | Default | Range | Description |
|--------|------|---------|-------|-------------|
| `is_mcmc_chains` | int | `5` | [1, 100] | Number of parallel Metropolis chains to run during MCMC proposal fitting. A practical starting point is about 2 times the number of stochastic variables |
| `is_mcmc_chain_length` | int | `500` | [100, 10000] | Number of samples kept from each MCMC chain after burn-in and thinning. Each chain runs `is_mcmc_burnin + is_mcmc_chain_length × is_mcmc_thinning` steps |
| `is_mcmc_thinning` | int | `3` | [1, 100] | Thinning interval: after burn-in, every `is_mcmc_thinning`-th step of each chain is kept. `1` keeps every step |
| `is_mcmc_burnin` | int | `200` | [100, 1000] | Number of initial steps discarded from each MCMC chain as burn-in |
| `is_mcmc_fit_method` | str | `"kde"` | `"kde"`, `"mixture"` | Method used to fit the MCMC proposal distribution |

#### Importance Sampling References

Use these references as starting points for method details and implementation background. Keep in mind that explanations on this page are intentionally brief and implementation-focused.

**`is_method: "kde"`**

- `KernelDensity` from scikit-learn — [sklearn.neighbors.KernelDensity](https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.KernelDensity.html). Bandwidth selection follows the `is_kde_bandwidth` option (`"scott"` or `"silverman"` rules, or a numeric value).

**`is_method: "mixture"`**

- `BayesianGaussianMixture` from scikit-learn — [sklearn.mixture.BayesianGaussianMixture](https://scikit-learn.org/stable/modules/generated/sklearn.mixture.BayesianGaussianMixture.html). Number of components and covariance type are controlled by `is_mixture_components` and `is_mixture_cov_type`.

**`is_method: "mcmc"`**

- Xiao, S., and Nowak, W. (2022). "Reliability sensitivity analysis based on a two-stage Markov chain Monte Carlo simulation." *Aerospace Science and Technology*, 130, 107938. [→](https://doi.org/10.1016/j.ast.2022.107938)
- Cotter, S. L., Roberts, G. O., Stuart, A. M., and White, D. (2013). "MCMC methods for functions: modifying old algorithms to make them faster." *Statistical Science*, 28(3), 424–446. [→](https://doi.org/10.1214/13-STS421)
- Roberts, G. O., and Rosenthal, J. S. (2007). "Coupling and ergodicity of adaptive Markov chain Monte Carlo algorithms." *Journal of Applied Probability*, 44(2), 458–475. [→](https://www.jstor.org/stable/27595854)

**`is_method: "mpp_normal"`**

- Centers the importance sampling proposal distribution on the Most Probable Point (MPP), also called the design point or failure point. The MPP is the point on the limit-state surface closest to the origin in standard normal space, found by FORM. A Gaussian proposal centered there concentrates samples near the dominant failure region. See the FORM method and the references listed on [Recommended Texts and References](../problem-authoring/recommended-texts.md).

!!! warning "Limitation: one most probable point"
    FORM finds a single MPP, so `mpp_normal` covers only the failure region around it. When the failure region has several separate parts, such as in series systems built with `numpy.minimum()`, the proposal distribution misses the other parts and the probability of failure is underestimated. For the series problem `AU2Problem`, `mpp_normal` gave β = 4.839, while `kde`, `mixture`, and `mcmc` all gave β ≈ 4.78. It also needed 1,264,000 samples to reach the target coefficient of variation, compared with 6,000 to 8,000 for the other methods. For such problems, use `kde`, `mixture`, or `mcmc`.

### Derivative Checking

These options validate user-provided derivatives against numerical finite differences.

Used by: any run where the problem file provides analytic derivatives.

The numerical derivatives of a vectorized limit state function or design objective function (`LSFisVectorized` or `DOFisVectorized` set to `True`) come from [`scipy.differentiate`](https://docs.scipy.org/doc/scipy/reference/differentiate.html), which chooses its own step sizes. If it fails, Brinkpy computes them with [numdifftools](https://pypi.org/project/numdifftools/) instead. The derivatives of other functions, and those of constraint functions, always come from numdifftools. The `*_diffs_check_method` options below choose the numdifftools method, so they normally have no effect on a vectorized function.

| Option | Type | Default | Values | Description |
|--------|------|---------|--------|-------------|
| `check_lsf_diffs_wrtx` | bool | `false` | - | Validate user-provided LSF derivatives against numerical diffs w.r.t. real-space variables |
| `check_lsf_diffs_wrtu` | bool | `true` | - | Validate user-provided LSF derivatives against numerical diffs w.r.t. standard-normal (U-space) variables |
| `lsf_diffs_check_method` | str | `"forward"` | `"central"`, `"forward"`, `"backward"`, `"complex"` | Method for LSF derivative checks |
| `check_varscf_diffs_wrtx` | bool | `false` | - | Validate user-provided stochastic variables constraints (real-space) |
| `check_varscf_diffs_wrtu` | bool | `true` | - | Validate user-provided stochastic variables constraints (U-space) |
| `varscf_diffs_check_method` | str | `"forward"` | `"central"`, `"forward"`, `"backward"`, `"complex"` | Method for stochastic variables constraint derivative checks |
| `check_dof_diffs` | bool | `true` | - | Validate user-provided design objective function derivatives against numerical diffs |
| `dof_diffs_check_method` | str | `"forward"` | `"central"`, `"forward"`, `"backward"`, `"complex"` | Method for design objective function derivative checks |
| `check_dcf_diffs` | bool | `true` | - | Validate user-provided design constraint function derivatives against numerical diffs |
| `dcf_diffs_check_method` | str | `"forward"` | `"central"`, `"forward"`, `"backward"`, `"complex"` | Method for design constraint function derivative checks |

### Example

A complete `reliability_options` section with the default values:

```yaml
reliability_options:
  # General
  alpha_direction: "outward"
  use_nearest_correlation: false
  max_minimize_attempts: 8

  # FORM
  form_xtol: 0.0001
  form_gtol: 0.0001
  form_maxiter: 1000
  form_random_start: false
  form_seed: null

  # Design
  design_xtol: 0.001
  design_gtol: 0.001
  design_maxiter: 1000
  design_random_start: false
  design_seed: null

  # SORM
  sor_method: "SOSPA_H"
  sor_approximation: "Paraboloid"
  sor_fit_method: null
  sor_fit_delta_factor: 1.0
  sor_fdm: "forward"
  sor_fdm_hess_form: "full"
  force_curvatures: false
  qn_epsilon: 1e-8

  # IFFT
  ifft_std_domain: 16.0
  ifft_n: 4096
  plot_ifft_funcs: true

  # SOSPA
  plot_sospa_funcs: true

  # Monte Carlo
  mc_n: null
  mc_max_cv: 0.05
  mc_seed: null
  mc_remove_oob: true

  # Importance Sampling
  is_method: "kde"
  is_kde_bandwidth: "scott"
  is_mixture_components: 6
  is_mixture_cov_type: "full"
  is_fit_samples: 2000
  is_mcmc_chains: 5
  is_mcmc_chain_length: 500
  is_mcmc_thinning: 3
  is_mcmc_burnin: 200
  is_mcmc_fit_method: "kde"

  # Derivative checking
  check_lsf_diffs_wrtx: false
  check_lsf_diffs_wrtu: true
  lsf_diffs_check_method: "forward"
  check_varscf_diffs_wrtx: false
  check_varscf_diffs_wrtu: true
  varscf_diffs_check_method: "forward"
  check_dof_diffs: true
  dof_diffs_check_method: "forward"
  check_dcf_diffs: true
  dcf_diffs_check_method: "forward"
```

---

## LSF Plot Options

Options for limit state function (LSF) 3D visualization.

Used by: `analyze --plot-lsf` and `simulate --plot-lsf`.

| Option | Type | Default | Range/Values | Description |
|--------|------|---------|--------------|-------------|
| `n_x_points` | int | `30` | [5, 60] | Number of grid points along the first variable axis |
| `n_y_points` | int | `29` | [5, 60] | Number of grid points along the second variable axis |
| `plot_base_point` | bool | `true` | - | Whether to plot the base point (mean of input variables) on the LSF surface |
| `plot_failure_point` | bool | `true` | - | Whether to plot the design point (Most Probable Point of Failure) on the LSF surface |
| `with_labels` | bool | `true` | - | Whether to add text labels to the base and failure points |
| `ignore_axis_funcs` | bool | `false` | - | Whether to ignore axis transformation functions and plot in original variable space |
| `view` | str or tuple | `"auto"` | `"auto"`, `"default"`, `"XY"`, `"XZ"`, `"YZ"`, `"-XY"`, `"-XZ"`, `"-YZ"` (case-insensitive) or tuple of 3 floats (elevation, azimuth, roll) in degrees | View orientation for 3D perspective |
| `cmap` | str or list | `"plasma"` | Valid matplotlib colormap name or list of shape (n, 4) with RGBA values in [0, 1] where 1 ≤ n ≤ 256 | Colormap specification |
| `type` | str | `"surface"` | `"contour"`, `"surface"` | Plot visualization type |

**Example:**
```yaml
lsf_plot_options:
  n_x_points: 30
  n_y_points: 29
  plot_base_point: true
  plot_failure_point: true
  with_labels: true
  ignore_axis_funcs: false
  view: "auto"
  cmap: "plasma"
  type: "surface"
```

---

## RFAD Plot Options

Options for reliability-based failure assessment diagram (RFAD) visualization.

Used by: `analyze --plot-rfad`.

| Option | Type | Default | Range/Values | Description |
|--------|------|---------|--------------|-------------|
| `n_x_points` | int | `30` | [5, 60] | Number of grid points along the first variable axis |
| `n_y_points` | int | `29` | [5, 60] | Number of grid points along the second variable axis |
| `plot_beta` | bool | `true` | - | Whether to plot the reliability index (β) contours |
| `plot_alphas` | bool | `true` | - | Whether to plot alpha values (normalized sensitivity factors) for each variable |
| `plot_base_point` | bool | `true` | - | Whether to plot the base point (mean of input variables) on the diagram |
| `with_labels` | bool | `true` | - | Whether to add text labels to the base point on the diagram |
| `ignore_axis_funcs` | bool | `false` | - | Whether to ignore axis transformation functions and plot in original variable space |
| `view` | str or tuple | `"auto"` | `"auto"`, `"default"`, `"XY"`, `"XZ"`, `"YZ"`, `"-XY"`, `"-XZ"`, `"-YZ"` (case-insensitive) or tuple of 3 floats (elevation, azimuth, roll) in degrees | View orientation for 3D perspective |
| `cmap` | str or list | `"plasma"` | Valid matplotlib colormap name or list of shape (n, 4) with RGBA values in [0, 1] where 1 ≤ n ≤ 256 | Colormap specification |
| `type` | str | `"surface"` | `"contour"`, `"surface"` | Plot visualization type |

**Example:**
```yaml
rfad_plot_options:
  n_x_points: 30
  n_y_points: 29
  plot_beta: true
  plot_alphas: true
  plot_base_point: true
  with_labels: true
  ignore_axis_funcs: false
  view: "auto"
  cmap: "plasma"
  type: "surface"
```

---

## Reporting Options

Options for saving analysis results and visualizations.

Used by: all commands. See [Result Files](../cli/results-files.md) for what each file contains.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `save_plots_to_pdf` | bool | `true` | Whether to save all generated plots in PDF format |
| `save_plots_to_pickle` | bool | `true` | Whether to save figure objects in pickle format for later retrieval and editing |
| `save_excel_summary` | bool | `true` | Whether to save the numerical results summary to an Excel file |

**Example:**
```yaml
reporting_options:
  save_plots_to_pdf: true
  save_plots_to_pickle: true
  save_excel_summary: true
```

---

## Notes

- Enum-style fields accept either the enum member name (case-insensitive) or the enum value
- Out-of-range or invalid values trigger a profile validation error
- Set `form_seed`, `design_seed`, and/or `mc_seed` to a non-null integer for repeatable results when random number generation is involved
