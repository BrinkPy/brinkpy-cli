# Problem Definition

This section explains how to define a Brinkpy problem module (`*.py`) that can be selected from the `problems/` directory and solved by `analyze`, `design`, or `simulate` commands.

For result-folder location and output filename conventions, see [CLI Result Files](../cli/results-files.md).

## How This Section Is Organized

This page describes the problem file format: the top-level keys, the variables, the limit state function, and the plot keys. It uses short snippets from the packaged example problems to illustrate them.

The rest of the section teaches by example. The pages under **Analyze**, **Design**, **Simulate**, and **Plots** each walk through one or two packaged example problems: the problem file, the command that runs it, the result tables and figures, and how to read them. Use them as templates for your own problems. To run the examples yourself, copy them into your project folder with `brinkpy examples copy` (see [Packaged Example Problems](../examples.md)).

The [Results Tables Reference](results-tables.md) explains every column in the result files, and the example pages link to it. The **Design** group also has its own overview and a reference of the `DesignProblem` keys.

## Minimal File Pattern

A problem module should expose `Problem()` (or `problem()`) and return a dictionary.

```python
import numpy as np


def Problem():
    return {
        "Name": "MyProblem",
        "LimitStateFunction": LSF,
        "LSFisVectorized": True,
        "LSFisSmooth": True,
        "LSFisParallelizable": True,
        "LSFreturnsGradient": False,
        "LSFreturnsHessian": False,
        "LSFreturnsLandR": False,
        "DeterministicVariables": {"name": [], "value": []},
        "StochasticVariables": {
            "name": ["X1", "X2"],
            "type": ["normal", "normal"],
            "mean": [10.0, 4.0],
            "std": [1.0, 0.5],
        },
    }


def LSF(X, D):
    X1, X2 = X
    g = X1 - X2
    gg = []
    gh = []
    L = []
    R = []
    return g, gg, gh, L, R
```

## Top-Level Problem Keys

The sections below describe each key in detail.

| Key | Required | Type | Purpose | Example (`AT610`) |
|---|---|---|---|---|
| `Name` | Yes | `str` | Human-readable problem name used in outputs | `"AT610"` |
| `LimitStateFunction` | Yes | callable | Function implementing `g(X, D)` that returns `g, gg, gh, L, R` (see [Required Return Values](#required-return-values)) | `LSF` |
| `LSFisVectorized` | Yes | `bool` | Whether `LSF` can process batched samples (`X` with shape `(n_var, n_samples)`) | `True` |
| `LSFisSmooth` | Yes | `bool` | Whether the limit state function is smooth. Selects the optimizer for FORM and Inverse FORM (see [Smooth and Non-Smooth Functions](#smooth-and-non-smooth-functions)). | `True` |
| `LSFisParallelizable` | No (default `False`) | `bool` | Signals that evaluations are safe for parallel execution | `True` |
| `LSFreturnsGradient` | Yes | `bool` | Whether `LSF` returns the gradient `gg` for a single point. If `False`, Brinkpy ignores `gg`. | `True` |
| `LSFreturnsHessian` | Yes | `bool` | Whether `LSF` returns the Hessian `gh` for a single point. If `False`, Brinkpy ignores `gh`. | `True` |
| `LSFreturnsLandR` | Yes | `bool` | Whether `LSF` returns the load `L` and resistance `R`, used for the load and resistance histogram and partial factors. If `False`, Brinkpy ignores `L` and `R`. | `True` |
| `DeterministicVariables` | Yes | `dict` | Deterministic variables and fixed values | empty in `AT610` |
| `StochasticVariables` | Yes | `dict` | Random variable definition (names, distributions, moments, correlations) | `Y,Z,M` |
| `LSFplot` | Optional | `dict` | Axis mapping and limits for limit state function (LSF) plots | present in `AT610` |
| `RFADplot` | Optional | `dict` | Axis mapping and limits for reliability-based failure assessment diagram (RFAD) plots | present in `AT610` |
| `ISplot` | Optional | `dict` | Axis mapping for importance sampling (IS) diagnostic plots | present in `AT610` |
| `DesignProblem` | Required for `design` runs | `dict` | Design-specific definitions (objective, constraints, variables) | not used in `AT610` |

## Limit State Function Contract

Your `LSF` must accept:

- `X`: stochastic variables
- `D`: deterministic variables

Expected argument order:

- `X` follows the order of `StochasticVariables.name`.
- `D` follows the order of `DeterministicVariables.name`.

This means `X` is the stochastic-variable vector (or batch of vectors), while `D` is the deterministic state used by the problem definition.

Expected shape behavior:

- With `LSFisVectorized=True`, Brinkpy evaluates many points in a single call whenever it can (for example, all Monte Carlo samples at once). `X` then has shape `(n_var, n_samples)`, and each row corresponds to one variable in `StochasticVariables.name` order.
- Your function must still accept a single point, `X` with shape `(n_var,)`, because some steps evaluate one point at a time even with `LSFisVectorized=True`. This is why the worked example below checks `X.ndim == 1`.
- With `LSFisVectorized=False`, Brinkpy evaluates one point at a time, so `X` always has shape `(n_var,)`.
- `D` follows the deterministic-variable ordering from `DeterministicVariables.name`.

### Required return values

Always return all five values, in this order:

- `g`: the limit state function value, with failure when `g <= 0`. It has one value per point.
- `gg`: the gradient of `g` with respect to the stochastic variables (see [Gradient](#gradient-gg-definition)).
- `gh`: the Hessian of `g` with respect to the stochastic variables (see [Hessian](#hessian-gh-definition)).
- `L`: the load, or demand, with the same shape as `g`.
- `R`: the resistance, or capacity, with the same shape as `g`. Brinkpy assumes `g = R - L`.

The function returns the same five values whatever the flags say: `return g, gg, gh, L, R`. When a flag is `False`, Brinkpy ignores the matching values, so return `[]` in their place. For example, without load and resistance values:

- `return g, gg, gh, [], []`

Brinkpy never uses `gg` or `gh` from a vectorized call, where `X` holds many points. Compute them only for a single point and return `[]` otherwise, because derivatives for many points can use a lot of memory. `L` and `R` are needed in both cases.

### Gradient (`gg`) definition

For a single point (`X.ndim == 1`):

- `gg` is the derivative vector `dg/dx_i` in the same variable order as `name`.
- Shape should be `(n_var,)`.

For a vectorized call, return `[]`, as explained in [Required Return Values](#required-return-values).

### Hessian (`gh`) definition

For a single point (`X.ndim == 1`):

- `gh` is the matrix of second derivatives `d2g/(dx_i dx_j)`.
- Shape should be `(n_var, n_var)`.
- Keep symmetry when mathematically expected.

As with the gradient, return `[]` for a vectorized call.

## LSF Derivative Return Modes

Use the flags to match what your function returns:

| `LSFreturnsGradient` | `LSFreturnsHessian` | `LSF` expectation |
|---|---|---|
| `False` | `False` | Return `[]` for `gg` and `gh` |
| `True` | `False` | Return `gg` for a single point and `[]` for `gh` |
| `True` | `True` | Return `gg` and `gh` for a single point |

There is no mode that returns the Hessian without the gradient. A user-provided Hessian is defined in real space, and Brinkpy needs the gradient to transform it into the standard normal space used by FORM and SORM. In practice, if you can derive the Hessian analytically, the gradient is usually straightforward.

## Smooth and Non-Smooth Functions

`LSFisSmooth` tells Brinkpy whether the limit state function is smooth, meaning that it has no kinks, steps, or jumps, so its gradient changes continuously. Brinkpy uses it to choose the optimizer for FORM and Inverse FORM:

| `LSFisSmooth` | Optimizer | Kind |
|---|---|---|
| `True` | SciPy's [`trust-constr`](https://docs.scipy.org/doc/scipy/reference/optimize.minimize-trustconstr.html) | Uses gradients |
| `False` | SciPy's [`COBYQA`](https://docs.scipy.org/doc/scipy/reference/optimize.minimize-cobyqa.html) | Derivative-free |

`DOFisSmooth` makes the same choice for the design objective function in objective optimization (see [Design Keys](design/design-keys.md#additional-keys-for-objective-optimization)). In a design run, each flag applies to its own optimization: `DOFisSmooth` to the search for the optimal design, and `LSFisSmooth` to the FORM analysis inside it.

Set the flag to `False` when the function has kinks or steps, for example from `numpy.minimum()` or `numpy.maximum()` in series and parallel systems, `abs()`, `if` branches, or table lookups. Otherwise leave it `True`, because the optimizer that uses gradients is usually faster and more accurate.

The flag changes the following:

| | Smooth (`True`) | Non-smooth (`False`) |
|---|---|---|
| Analytic derivatives (`gg`, `gh`, or `g`, `h` for the design objective function) | Used when the matching `returns` flag is `True` | Not used |
| Bounds and constraints | Respected | Respected |
| Lagrange multipliers (`bnds_mult`, `constr_mult`) | Reported | Empty |
| Restarts to refine a result (counted in `min_tries`) | Can happen when there are bounds or constraints | None |
| `min_method` in the results | `trust-constr` | `COBYQA` |

!!! warning "SORM assumes a smooth limit state function"
    SORM approximates the limit state surface at the most probable point (MPP) with its curvatures, which assumes the function is smooth there. With `LSFisSmooth = False`, SORM still runs, but if the MPP lies on a kink, the curvatures do not describe the surface and the SORM result can be wrong. Check it with Monte Carlo or importance sampling.

## Worked LSF Example (`AT610Problem.py`)

In `AT610Problem.py`, the stochastic variables are `Y`, `Z`, and `M`, and there are no deterministic variables:

- `StochasticVariables.name = ["Y", "Z", "M"]`
- `DeterministicVariables.name = []`

The limit state function is:

```python
def LSF(X, D):
    Y, Z, M = X

    L = M  # Load
    R = Y * Z  # Resistance

    g = R - L

    gg = []
    gh = []
    if X.ndim == 1:
        gg = np.array([Z, Y, -1.0])
        gh = np.array([
            [0.0, 1.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 0.0, 0.0],
        ])

    return g, gg, gh, L, R
```

For that example:

- `R = Y * Z`
- `L = M`
- `g = R - L = YZ - M`

Analytical gradient:

- `dg/dY = Z`
- `dg/dZ = Y`
- `dg/dM = -1`

So:

```python
gg = np.array([Z, Y, -1.0])
```

Analytical Hessian:

- `d2g/dYdZ = 1`
- `d2g/dZdY = 1`
- all other second derivatives are zero

```python
gh = np.array([
    [0.0, 1.0, 0.0],
    [1.0, 0.0, 0.0],
    [0.0, 0.0, 0.0],
])
```

`AT610` sets both derivative flags to `True`, so Brinkpy uses the analytic gradient and Hessian during FORM convergence and SORM curvature fitting.

## `DeterministicVariables` Keys

| Key | Required | Type | Meaning |
|---|---|---|---|
| `name` | Yes | `list[str]` | Deterministic variable names (order matters) |
| `value` | Yes | `list[float]` | Deterministic values in same order as `name` |

Rules:

- `len(name)` must match `len(value)`.
- Keep deterministic variable order consistent with how `D` is unpacked inside `LSF(X, D)`.

## `StochasticVariables` Keys

Core keys used in all example problems:

| Key | Required | Type | Meaning |
|---|---|---|---|
| `name` | Yes | `list[str]` | Random variable names (defines variable order in `X`) |
| `type` | Yes | `list[str]` | Distribution per variable, e.g. `normal`, `lognormal`, `gumbelmax` |
| `mean` | Yes | `list[float]` | Mean values |
| `std` | Yes, unless `cv` is given | `list[float]` | Standard deviations |
| `cv` | Instead of `std` | `list[float]` | Coefficients of variation (standard deviation divided by mean) |
| `cor_list` | No | `list[list]` | Pairwise correlation entries `[var_i, var_j, rho]` |
| `cor` | No | `list[list]` | Full correlation matrix in variable order |

Advanced/optional fields can also be used depending on model needs:

| Key | Required | Type | Meaning |
|---|---|---|---|
| `lb` | Conditional | `list[float]` | Lower bounds per stochastic variable; required for some distributions and optional otherwise |
| `ub` | Conditional | `list[float]` | Upper bounds per stochastic variable; required for some distributions and optional otherwise |
| `truncated` | No | `list[bool]` | Whether each variable distribution is truncated to `[lb, ub]` |
| `constraints` | No | `list[dict]` | Linear or nonlinear constraints on functions of the stochastic variables (see [Constraints on Stochastic Variables](#constraints-on-stochastic-variables)) |

Rules:

- All lists must have the same length `n` (`name`, `type`, `mean`, and `std` or `cv`).
- Variable order in `name` must match `X` unpacking in `LSF`.
- If neither `cor_list` nor `cor` is provided, Brinkpy assumes zero correlation between all variables.
- `cor_list` references variable names from `name`.
- `cor`, when used, should be an `n x n` correlation matrix in the same variable order as `name`.
- Use either `cor_list` or `cor` to define correlation inputs.
- If defined, `lb`, `ub`, and `truncated` must each have length `n`.
- You can set individual bounds to `-np.inf` and `np.inf` to indicate no lower/upper bound for that variable.
- If `lb`, `ub`, and/or `truncated` are omitted, defaults are used: no bounds and `truncated=False` for all variables.
- Bounds and truncation have different effects. See [Bounds and Truncation](#bounds-and-truncation).
- `constraints`, when provided, is a list of constraint dictionaries. See [Constraints on Stochastic Variables](#constraints-on-stochastic-variables).

### Bounds and Truncation

Setting `lb` and `ub` does not by itself change a variable's distribution. Whether it does depends on `truncated`:

| | `truncated[i] = False` (default) | `truncated[i] = True` |
|---|---|---|
| Distribution | Unchanged. Values outside `[lb[i], ub[i]]` keep their probability. | Replaced by the truncated distribution: values outside `[lb[i], ub[i]]` have zero probability, and the density inside is scaled up so the total probability is still 1. |
| FORM, Inverse FORM, and `design` | The search for the most probable point (MPP) is restricted to `[lb[i], ub[i]]`. The bounds are passed as constraints to SciPy's `minimize`. | The bounds are still passed as constraints, and the search uses the truncated distribution. |
| Monte Carlo | Samples are drawn from the full distribution. Samples outside the bounds are reported in `%_oob` and removed when the profile option `mc_remove_oob` is `true`. | Samples are drawn from the truncated distribution, so none fall outside the bounds. |

SORM uses the MPP found by FORM, so the bounds affect SORM results in the same way.

Bounds without truncation are useful to keep the search for the MPP away from values where the limit state function is not defined, such as negative values inside a square root or logarithm, without changing the probability model.

!!! warning "When the MPP lies on a bound"
    With `truncated[i] = False`, the bounds restrict only where FORM and Inverse FORM search. If the MPP ends up on a bound, the result describes the constrained search, not the full distribution, so the reliability index (from FORM or SORM) or the design point (from Inverse FORM) may not reflect the actual probability of failure. Brinkpy reports this in a note that lists each active bound, whether it is the lower or upper bound, and about how much it affects the result. A bound counts as active when the MPP lies within 1% of it, or within 0.01 when the bound is between −1 and 1. The same values appear in the `bnds_mult` column of the results (see [Lagrange Multipliers for Bounds and Constraints](results-tables.md#lagrange-multipliers-for-bounds-and-constraints)). When a bound is active, decide whether values of the variable outside the bounds are physically possible:

    - If they are not, set `truncated[i] = True` so the distribution itself excludes them.
    - If they are, widen or remove the bounds.

For distributions that require `lb` and `ub` (beta, triangular, and uniform when defined by its bounds), the bounds are the limits of the distribution itself, so truncation does not change it.

### Constraints on Stochastic Variables

Bounds limit each variable on its own. Constraints limit functions of several variables, for example a ratio between two dimensions. In `PipecorrProblem.py`, the ratio of the defect depth to the wall thickness, `d / t`, must stay between 0.1 and 0.8, the range where the limit state function is valid (see [Stochastic Variable Constraints Example](design/stochastic-constraints.md)):

```python
"StochasticVariables": {
    ...
    "constraints": [
        {"fun": d_over_t, "lb": [0.1], "ub": [0.8], "jac": d_over_t_gradient},
        {"fun": l_over_Do, "lb": [0.0], "ub": [1.5]},
    ],
},
```

Brinkpy passes the constraints to SciPy's [`minimize`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html). Each dictionary uses the keys of SciPy's [`NonlinearConstraint`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.NonlinearConstraint.html) or [`LinearConstraint`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.LinearConstraint.html).

A nonlinear constraint uses these keys:

| Key | Required | Meaning |
|---|---|---|
| `fun` | Yes | Constraint function `fun(X, D)`, with `X` the stochastic variables in the order of `name` and `D` the deterministic variables, as in the limit state function. It returns one value per output. |
| `lb`, `ub` | At least one | Lists with the lower and upper limit of each output. A missing `lb` means no lower limits (`-np.inf`) and a missing `ub` means no upper limits (`np.inf`). Inside a list, use `-np.inf` or `np.inf` for an output with no limit on that side, and the same value in `lb` and `ub` for an equality. |
| `jac` | No | Function `jac(X, D)` that returns the gradient of each output with respect to `X`, one row per output. Without it, SciPy approximates the gradient with finite differences. |
| `hess` | No | Function `hess(X, v, D)` that returns the Hessian of the sum of the outputs weighted by `v`, as an `n x n` matrix. Without it, SciPy approximates the Hessian with a quasi-Newton (BFGS) update. |
| `keep_feasible` | No | Whether the optimizer must keep every iterate inside the limits. The default is `False`. See the warning below. |

A linear constraint limits weighted sums of the stochastic variables, such as `Y - 2 Po >= 0`. It uses these keys:

| Key | Required | Meaning |
|---|---|---|
| `A` | Yes | Matrix with one row per output and one column per stochastic variable. The outputs are `A @ X`. |
| `lb`, `ub` | At least one | Same as for a nonlinear constraint |
| `keep_feasible` | No | Same as for a nonlinear constraint |

A sum that is linear in real space is not linear in standard normal space, where FORM and Inverse FORM search. Brinkpy therefore turns each linear constraint into a nonlinear one, with `fun` returning `A @ X` and `jac` returning `A`. The results and notes name it `linear_k`, where k is its position in the `constraints` list, starting at 1, and each row of `A` is one of its outputs. To limit a single variable, use the variable's `lb` and `ub` instead (see [Bounds and Truncation](#bounds-and-truncation)).

A constraint function can return several outputs, with one entry per output in `lb` and `ub`. The results and notes identify each output by its number, starting at 1.

Both kinds of constraint are defined on the stochastic variables in real space. FORM and Inverse FORM search in standard normal space, so Brinkpy transforms each point of the search to real space before it evaluates the constraints.

When `jac` or `hess` is provided, Brinkpy checks it against finite differences before the analysis and reports the number of function calls in a note. The profile options `check_varscf_diffs_wrtx`, `check_varscf_diffs_wrtu`, and `varscf_diffs_check_method` control the check (see [Derivative Checking](../profiles/profile-reference.md#derivative-checking)).

Constraints affect each method as follows:

| Method | Effect |
|---|---|
| FORM, Inverse FORM, and `design` | The search for the MPP is restricted to the points that satisfy the constraints. The distributions are unchanged. |
| SORM | Uses the MPP found by FORM, so the constraints affect SORM results in the same way. |
| Monte Carlo | Samples are drawn from the full distributions. When the profile option `mc_remove_oob` is `true`, samples that violate a constraint are removed from the statistics and counted in `%_removed`, and a note reports the share removed by each constraint. |

The results include a table of the constraint values at the MPP (see [Stochastic Variables Constraints](results-tables.md#stochastic-variables-constraints)).

!!! warning "When the MPP lies on a constraint limit"
    As with bounds, if the MPP ends up on a constraint limit, the result describes the constrained search, not the full distribution. Brinkpy reports this in a note that lists each active limit, whether it is the lower or upper limit, and about how much it affects the result, in the units of the constraint's output. A limit counts as active when the constraint's value lies within 1% of it, or within 0.01 when the limit is between −1 and 1. Equalities are not listed. Decide whether values beyond the limit are physically possible, and if they are, widen the limit.

!!! warning "Setting `keep_feasible` to `True`"
    With `keep_feasible` set to `True`, the starting point of the search must already satisfy the constraint, or SciPy stops with an error and the run fails. Every step of the search must then stay inside the limits, which can slow the search or stop it short of a solution that lies on a limit. Set it to `True` only when the problem's functions cannot be evaluated outside the limits, for example when a value inside a square root or logarithm would become negative. `keep_feasible` has no effect on equalities.

## Supported Statistical Distributions

The table below lists all supported `StochasticVariables.type` values with their `scipy.stats` equivalents and natural parameters. Reference links to Wikipedia and SciPy documentation are provided for each distribution.

For each stochastic variable, you can define the distribution either with:

- `mean` and `std` (or `mean` and `cv`), or
- `param1` and `param2` (natural distribution parameters shown below, when applicable).

Per-variable input rule:

- The four lists (`mean`, `std`, `param1`, `param2`) can all be present in the same problem.
- For each variable index `i`, use exactly one pair:
    - either `mean[i]` and `std[i]`, with `param1[i] = None` and `param2[i] = None`
    - or `param1[i]` and `param2[i]`, with `mean[i] = None` and `std[i] = None`
- This allows mixed entry modes across variables in one model (for example, one variable by moments and another by natural parameters).

Example pattern (`None` marks the unused pair for that variable):

```python
"StochasticVariables": {
        "name":   ["X1",    "X2",    "X3"],
        "type":   ["normal", "gumbelmax", "uniform"],
        "mean":   [10.0,     None,     None],
        "std":    [2.0,      None,     None],
        "param1": [None,     100.0,    0.0],
        "param2": [None,     15.0,     20.0],
}
```

| Brinkpy `type` | `scipy.stats` equivalent | `mean` | `std` | `param1` | `param2` | `lb`/`ub` |
|---|---|---|---|---|---|---|
| `normal` | `norm` | Yes | Yes | `μ` | `σ` | Optional |
| `lognormal` | `lognorm` | Yes | Yes | `μ_ln` | `σ_ln` | Optional |
| `gumbelmax` | `gumbel_r` | Yes | Yes | `μ` | `β` | Optional |
| `gumbelmin` | `gumbel_l` | Yes | Yes | `μ` | `β` | Optional |
| `exponential` | `expon` | Yes | No | `λ` | `None` | Optional |
| `gamma` | `gamma` | Yes | Yes | `κ` | `θ` | Optional |
| `weibull` | `weibull_min` | Yes | Yes | `κ` | `λ` | Optional |
| `beta` | `beta` | Yes | Yes | `α` | `β` | Required |
| `triangular` | `triang` | Yes | No | `Mo` (mode) | `None` | Required |
| `uniform` | `uniform` | Yes | Yes | `a` | `b` | `*` |
| `frechet` | `invweibull` | Yes | Yes | `s` | `α` | Optional |
| `pareto` | `pareto` | Yes | Yes | `xm` | `α` | Optional |
| `rayleigh` | `rayleigh` | Yes | No | `σ` | `None` | Optional |

The `mean` and `std` columns show whether the distribution requires that value when it is defined by moments. The exponential, triangular, and Rayleigh distributions are fully defined by their mean, so they do not take `std`.

`*` A uniform distribution can be defined in any of three ways:

- By `mean` and `std`. Set `lb` and `ub` to `None`.
- By `param1` and `param2`, which are the lower and upper limits of the distribution. Set `lb` and `ub` to `None`.
- By `lb` and `ub`, which are then the lower and upper limits. Set `param1` and `param2` to `None`.

Greek symbols shown for `param1` and `param2` follow the standard notation used in the linked Wikipedia references (where applicable).

Parameterizations can differ across sources; Brinkpy follows the parameter definitions documented by the linked SciPy distributions.

For correlated non-normal variables, Brinkpy uses an isoprobabilistic transformation (Nataf) to map variables into standard normal space during reliability computations.

Reference links:

- `normal`: [Wikipedia](https://en.wikipedia.org/wiki/Normal_distribution), [SciPy `norm`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.norm.html)
- `lognormal`: [Wikipedia](https://en.wikipedia.org/wiki/Log-normal_distribution), [SciPy `lognorm`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.lognorm.html)
- `gumbelmax`: [NIST Gumbel](https://www.itl.nist.gov/div898/handbook/eda/section3/eda366g.htm), [SciPy `gumbel_r`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.gumbel_r.html)
- `gumbelmin`: [NIST Gumbel](https://www.itl.nist.gov/div898/handbook/eda/section3/eda366g.htm), [SciPy `gumbel_l`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.gumbel_l.html)
- `exponential`: [Wikipedia](https://en.wikipedia.org/wiki/Exponential_distribution), [SciPy `expon`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.expon.html)
- `gamma`: [Wikipedia](https://en.wikipedia.org/wiki/Gamma_distribution), [SciPy `gamma`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.gamma.html)
- `weibull`: [Wikipedia](https://en.wikipedia.org/wiki/Weibull_distribution), [SciPy `weibull_min`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.weibull_min.html)
- `beta`: [Wikipedia](https://en.wikipedia.org/wiki/Beta_distribution), [SciPy `beta`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.beta.html)
- `triangular`: [Wikipedia](https://en.wikipedia.org/wiki/Triangular_distribution), [SciPy `triang`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.triang.html)
- `uniform`: [Wikipedia](https://en.wikipedia.org/wiki/Continuous_uniform_distribution), [SciPy `uniform`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.uniform.html)
- `frechet`: [Wikipedia](https://en.wikipedia.org/wiki/Fr%C3%A9chet_distribution), [SciPy `invweibull`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.invweibull.html)
- `pareto`: [Wikipedia](https://en.wikipedia.org/wiki/Pareto_distribution), [SciPy `pareto`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pareto.html)
- `rayleigh`: [Wikipedia](https://en.wikipedia.org/wiki/Rayleigh_distribution), [SciPy `rayleigh`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.rayleigh.html)

Type strings are case-insensitive: both lowercase (for example `"lognormal"`) and camelCase (for example `"gumbelMax"`) are accepted.

## Plot Definition Keys (`LSFplot`, `RFADplot`, `ISplot`)

These blocks are optional for computation but needed for plot commands and richer diagnostics.

### `LSFplot`

`LSFplot` defines a 3D plot of the limit state function (LSF) over two stochastic variables on the x and y axes. It is used when running `brinkpy analyze -l` or `brinkpy simulate -l`. The plot style (surface or contour) and whether the mean point and design point are shown are set in the profile (see [LSF Plot Options](../profiles/profile-reference.md#lsf-plot-options)). For a worked example, see [Limit State Function](plots/limit-state-function.md).

**Required and optional keys:**

| Key | Type | Required | Meaning |
|---|---|---|---|
| `x_var` | `str` | Yes | Stochastic variable name for x axis |
| `x_lim` | `list[float]` | Yes | Plot window `[min, max]` for x axis |
| `y_var` | `str` | Yes | Stochastic variable name for y axis |
| `y_lim` | `list[float]` | Yes | Plot window `[min, max]` for y axis |
| `x_func` | `callable` or omitted | No | Transformation function `lambda S, D: ...` for x axis. If omitted, x axis displays `x_var` directly. |
| `y_func` | `callable` or omitted | No | Transformation function `lambda S, D: ...` for y axis. If omitted, y axis displays `y_var` directly. |
| `x_label` | `str` or omitted | No | Custom label for x axis (can include LaTeX). If omitted, defaults to variable name. |
| `y_label` | `str` or omitted | No | Custom label for y axis (can include LaTeX). If omitted, defaults to variable name. |
| `z_var` | `str` | No | Stochastic variable for the z axis. If omitted, the z axis shows the limit state function value (see below). |

**The z axis:**

- If `z_var` is omitted, the z axis shows the value of the limit state function, `g`.
- If `z_var` is defined, the z axis shows that variable. For each `(x, y)` point, Brinkpy finds the value of `z_var` that makes `g = 0`, so the plot shows the limit state surface. No `z_lim` is needed.

**Transformation function signature:**

- `x_func(S, D)` and `y_func(S, D)` receive:
  - `S`: array of stochastic variable values in the order defined in `StochasticVariables.name`.
  - `D`: array of deterministic variable values in the order defined in `DeterministicVariables.name`.
- Return a scalar value or array to be plotted.
- Typical use: combine multiple variables (e.g., `lambda S, D: S[0] * S[1]` for resistance as product) or apply scaling/Log transforms.

**Example from `AT68Problem.py`:**

```python
"LSFplot": {
    "x_var": "Y",
    "x_lim": [30.0, 50.0],
    "x_func": lambda S, D: S[0] * S[1],      # Resistance: product of Y and Z
    "x_label": "Resistance: Y*Z",
    "y_var": "M",
    "y_lim": [800, 1800],
    "y_func": lambda S, D: S[2],              # Load: just M
    "y_label": "Load: M",
}
```

Here, stochastic variables are indexed as `S[0]` for Y, `S[1]` for Z, and `S[2]` for M (in `StochasticVariables.name` order). Because `z_var` is omitted, the z axis shows the limit state function value, and failure occurs where `g ≤ 0`, that is, where resistance ≤ load.

### `RFADplot`

`RFADplot` defines the axes of a Reliability-based Failure Assessment Diagram (RFAD). Brinkpy sweeps the `x_param` of `x_var` across `x_lim` and the `y_param` of `y_var` across `y_lim`, computing the reliability index, probability of failure, and alpha vectors for each combination to produce an iso-reliability contour map. Run with `brinkpy analyze -r`.

**Required and optional keys:**

| Key | Type | Required | Meaning |
|---|---|---|---|
| `x_var` | `str` | Yes | Stochastic variable whose parameter is swept along the x axis |
| `x_param` | `str` | Yes | Parameter to sweep: `"mean"`, `"std"`, `"param1"`, or `"param2"` |
| `x_lim` | `list[float]` | Yes | Sweep range `[min, max]` for the x parameter |
| `y_var` | `str` | Yes | Stochastic variable whose parameter is swept along the y axis |
| `y_param` | `str` | Yes | Parameter to sweep: `"mean"`, `"std"`, `"param1"`, or `"param2"` |
| `y_lim` | `list[float]` | Yes | Sweep range `[min, max]` for the y parameter |
| `x_func` | `callable` or omitted | No | Transformation `lambda S, D: ...` mapping the swept stochastic values to the plotted x quantity. If omitted, the swept parameter value is plotted directly. |
| `y_func` | `callable` or omitted | No | Transformation `lambda S, D: ...` mapping the swept stochastic values to the plotted y quantity. If omitted, the swept parameter value is plotted directly. |
| `x_label` | `str` or omitted | No | Custom label for x axis (can include LaTeX). If omitted, defaults to variable name. |
| `y_label` | `str` or omitted | No | Custom label for y axis (can include LaTeX). If omitted, defaults to variable name. |

`x_func` and `y_func` follow the same signature as in `LSFplot`: they receive `S` (stochastic variable values array in `StochasticVariables.name` order) and `D` (deterministic variable values array) and return the quantity to plot.

**Example from `AT68Problem.py`:**

```python
"RFADplot": {
    "x_var": "Y",
    "x_param": "mean",
    "x_lim": [10.0, 70.0],
    "x_func": lambda S, D: S[0] * S[1],           # Resistance: μ(Y) * μ(Z)
    "x_label": "Resistance: \\mu(Y)*\\mu(Z)",
    "y_var": "M",
    "y_param": "mean",
    "y_lim": [500.0, 1500.0],
    "y_func": lambda S, D: S[2],                   # Load: μ(M)
    "y_label": "Load: \\mu(M)",
}
```

Here `S[0]` is Y, `S[1]` is Z, and `S[2]` is M. As Brinkpy sweeps `mean(Y)` and `mean(M)`, `x_func` converts the current Y mean into ` μ(Y)·μ(Z)` (resistance) and `y_func` passes `mean(M)` through as the load axis. The RFAD plots are included in the PDF result file. For a worked example, see [Failure Assessment Diagram](plots/rfad.md).

### `ISplot`

`ISplot` defines the axis variables and plot extents used for importance sampling (IS) proposal diagnostics when running `brinkpy simulate -i` or `brinkpy analyze -i` (in `analyze`, `-i` automatically enables Monte Carlo). If `ISplot` is omitted, IS proposal diagnostic figures are not generated.

| Key | Required if `ISplot` exists | Meaning |
|---|---|---|
| `x_var` | Yes | Stochastic variable name used on the x axis for IS proposal diagnostics |
| `x_lim` | No | Plot range `[min, max]` for the x axis |
| `y_var` | Yes | Stochastic variable name used on the y axis for IS proposal diagnostics |
| `y_lim` | No | Plot range `[min, max]` for the y axis |

If `x_lim` and `y_lim` are omitted, the axis limits are set automatically to show all sampled points. If they are defined, they set the initial plot range, and Brinkpy expands it automatically when sampled points fall outside it.

## Module Self-Containment

Problem modules may define additional variables, arrays, dictionaries, helper functions, and preprocessing logic beyond the required contracts such as `LimitStateFunction` and (for design runs) `DesignObjectiveFunction`.

All data structures and helper logic used by the problem must be defined inside the same problem module (`*.py`). External data files are not supported for problem execution.

## Submission Safety Validation

For platform safety, submitted problem modules are validated and may be rejected if they contain unsafe execution patterns.

When a module is rejected, the API returns a validation error describing the disallowed category.

## Common Authoring Pitfalls

- Variable order mismatch between `StochasticVariables.name` and `X` unpacking in `LSF`.
- Returning scalar `g` for vectorized inputs when an array is expected.
- Setting derivative flags to `True` but returning `[]` for the derivatives.
- Computing `gg` or `gh` in a vectorized call, which Brinkpy never uses.
- Returning only `g, gg, gh` instead of the full `g, gg, gh, L, R` contract.
- Defining `cor_list` pairs with variable names not present in `name`.
- Defining a `cor` matrix with the wrong size or variable order.
- Forgetting `DesignProblem` when running `brinkpy design ...`.

## Next Pages

- [FORM Only](analyze/form-only.md): analyze example using FORM only (`AT610`).
- [SORM and Monte Carlo](analyze/sorm-monte-carlo.md): analyze example using `-s -m` (`Chan3`).
- [Design Overview](design/index.md): design authoring overview and workflow split (Inverse FORM vs objective optimization).
- [Design Keys Reference](design/design-keys.md): `DesignProblem` key reference and validation checklist.
- [Inverse FORM Examples](design/inverse-form.md): worked inverse FORM examples (`AT625` single-case and `AT624` multi-case).
- [Objective Optimization](design/optimization.md): objective optimization example and checklist.
- [Classic Monte Carlo](simulate/classic-monte-carlo.md): simulation example using plain Monte Carlo (Chan2).
- [Importance Sampling](simulate/importance-sampling.md): simulation example using importance sampling (AU2).
- [MCMC Importance Sampling](simulate/importance-sampling-mcmc.md): the same problem with a Markov chain Monte Carlo (MCMC) proposal distribution (AU2).
- [Probability Density Functions](plots/probability-density-functions.md): plots of the probability density function of each stochastic variable (`AT68`).
- [Limit State Function](plots/limit-state-function.md): plots of the limit state function in x-space and u-space, with the profile options that control them (`AT68`).
- [Failure Assessment Diagram](plots/rfad.md): reliability-based failure assessment diagram (RFAD) plots of the probability of failure, the reliability index, and the alpha values over a grid of mean resistance and mean load (`AT68`).
