# `DesignProblem` Keys Reference

This page documents design-specific dictionary keys that are required in addition to the common problem keys described in [Problem Definition](../index.md).

Additional helper code is allowed, but design problems must remain self-contained in the same problem module file. See [Problem Definition](../index.md).

## Core `DesignProblem` Keys

| Key | Required | Type | Meaning |
|---|---|---|---|
| `TargetBeta` | Exactly one of `TargetBeta` / `TargetPf` | `float` | Target reliability index (β) |
| `TargetPf` | Exactly one of `TargetBeta` / `TargetPf` | `float` | Target probability of failure |
| `fractiles` | Yes for Inverse FORM, optional for objective optimization | `list[float]` | Fractile level for each stochastic variable, used to compute characteristic values and partial factors |
| `cases` | Optional (both design types) | `dict` | Named design scenarios overriding base stochastic definitions |

`TargetBeta` and `TargetPf` apply to both Inverse FORM and objective optimization.

In objective optimization, `fractiles` is optional because calibrating partial factors is not the main goal. When `fractiles` is provided, the results also include characteristic values and partial factors.

`cases` is not limited to Inverse FORM. It can be used in both Inverse FORM and objective optimization runs.
If `cases` is omitted, Brinkpy builds a `default` case from the top-level `StochasticVariables` definition.

## Additional Keys For Objective Optimization

When `DesignProblem` defines a `DesignObjectiveFunction`, Brinkpy runs objective optimization (as in `Sorensen81Problem.py`), and the following keys are required in `DesignProblem`. Keys that start with `DOF` refer to the design objective function (DOF).

| Key | Required | Type | Meaning |
|---|---|---|---|
| `DesignObjectiveFunction` | Yes | callable | Objective function that the design optimizer minimizes (see [Design Objective Function Contract](#design-objective-function-contract)) |
| `DOFisVectorized` | Yes | `bool` | Whether objective can process vectorized design inputs |
| `DOFisSmooth` | Yes | `bool` | Signals smooth objective behavior for derivative-based optimization |
| `DOFreturnsGradient` | Yes | `bool` | If `True`, objective must return gradient in single-point mode |
| `DOFreturnsHessian` | Yes | `bool` | If `True`, objective must return Hessian in single-point mode |
| `DesignVariables` | Yes | `list[str]` | Names of deterministic design variables to optimize |
| `InitialGuess` | Yes | `list[float]` | Starting point for optimization |
| `lb` | Yes | `list[float]` | Lower bounds for design variables |
| `ub` | Yes | `list[float]` | Upper bounds for design variables |

`DesignVariables` must be selected from `DeterministicVariables.name`.

!!! note "RBDO modeling assumption"
    In Brinkpy's objective-optimization workflow, the optimized variables are assumed to be deterministic design variables, not stochastic variables. This is the standard RBDO formulation: the optimizer chooses deterministic design values, and reliability is then evaluated with respect to the stochastic variables.

## Inverse FORM Pattern

Typical shape:

```python
"DesignProblem": {
    "TargetBeta": 2.0,
    "fractiles": [0.5, 0.5, 0.5],
    "cases": {
        "1": {
            "mean": [1.0, 0.01, 126.0],
            "cv": [0.10, 0.21, 0.26],
        }
    },
}
```

Rules:

- `fractiles` length must match the number of stochastic variables.
- Cases do not list variable names. Each array in a case follows the variable order of `StochasticVariables.name`.
- Each case defines `mean` and the same spread parameter as the top-level `StochasticVariables`: `std` if the top level uses `std`, or `cv` (coefficient of variation) if it uses `cv`. Arrays must have consistent lengths.
- If `cases` is not provided, a `default` case is created from `StochasticVariables`.

## Objective Optimization Pattern

Typical shape:

```python
"DesignProblem": {
    "DesignObjectiveFunction": DOF,
    "DOFisVectorized": True,
    "DOFisSmooth": True,
    "DOFreturnsGradient": True,
    "DOFreturnsHessian": True,
    "DesignVariables": ["z"],
    "InitialGuess": [1.0],
    "lb": [0.0],
    "ub": [np.inf],
    "TargetBeta": 3.8,
    "fractiles": [0.05, 0.5, 0.98],
}
```

Rules:

- `len(DesignVariables) == len(InitialGuess) == len(lb) == len(ub)`.
- Every entry in `DesignVariables` must appear in `DeterministicVariables.name`.
- Objective return contract must match `DOFreturnsGradient` and `DOFreturnsHessian` flags.
- Reliability target (`TargetBeta` or `TargetPf`) is still required because optimization is reliability-constrained.
- Keep naming and order consistent with how `D` is used in `LSF(X, D)`.
- `cases` can also be used here for multi-scenario optimization. If omitted, a `default` case is created from `StochasticVariables`.

## Design Objective Function Contract

!!! warning "Brinkpy always minimizes the objective function"
    Brinkpy searches for the design that makes `DesignObjectiveFunction` as **small** as possible, because it uses SciPy's [`minimize`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html) function. Write your objective so that a smaller value means a better design.

    To **maximize** a quantity, such as capacity or stiffness, return its negative. For example, return `-capacity` instead of `capacity`. If your function also returns derivatives, negate them too.

    The results report the value your function returns. If your function returned the negative of the capacity (`-capacity`), change the sign of the reported objective value to obtain the maximized capacity.

Your `DesignObjectiveFunction` must accept:

- `d`: the subset of deterministic-variable values being optimized
- `D`: the deterministic variables that are not design variables

Expected argument order:

- `d` follows the order of `DesignVariables`.
- `D` follows the order of `DeterministicVariables.name`, with the design variables removed.

This means `d` holds the values the optimizer changes, while `D` holds the remaining deterministic values, which stay fixed. This differs from `LSF(X, D)`, where `D` contains all deterministic variables, including the current values of the design variables.

Expected shape behavior:

- With `DOFisVectorized=True`, Brinkpy evaluates many points in a single call whenever it can. `d` then has shape `(n_design, n_samples)`, and each row corresponds to one design variable in `DesignVariables` order.
- Your function must still accept a single point, `d` with shape `(n_design,)`, because some steps evaluate one point at a time even with `DOFisVectorized=True`. This is why the worked example below checks `d.ndim == 1`.
- With `DOFisVectorized=False`, Brinkpy evaluates one point at a time, so `d` always has shape `(n_design,)`.
- `D` follows the deterministic-variable ordering from `DeterministicVariables.name`, with the design variables removed.

### Required return values

Always return:

- `f`: objective-function value(s) to be minimized
- `g`: gradient placeholder (`[]` when `DOFreturnsGradient=False` or not evaluated)
- `h`: Hessian placeholder (`[]` when `DOFreturnsHessian=False` or not evaluated)

The return signature remains:

- `return f, g, h`

Typical patterns are:

- Without derivatives: `return f, [], []`
- With derivatives in single-point mode: `return f, g, h`

### Gradient (`g`) definition

For a single point (`d.ndim == 1`):

- `g` is the derivative vector `df/dd_i` in the same order as `DesignVariables`.
- Shape should be `(n_design,)`.

For vectorized evaluations, return `[]` unless your implementation explicitly supports batched derivatives. In the current examples, derivatives are only returned in single-point mode.

### Hessian (`h`) definition

For a single point (`d.ndim == 1`):

- `h` is the matrix of second derivatives `d2f/(dd_i dd_j)`.
- Shape should be `(n_design, n_design)`.
- Keep symmetry when mathematically expected.

As with the gradient, `h` should only be returned for single-point evaluations in the standard pattern used by Brinkpy examples.

## DOF Derivative Return Modes

Use the flags to match what your objective function returns:

| `DOFreturnsGradient` | `DOFreturnsHessian` | `DesignObjectiveFunction` expectation |
|---|---|---|
| `False` | `False` | Return placeholders for `g`, `h` (often empty lists) |
| `True` | `False` | Return valid `g` in single-point mode. `h` can be a placeholder |
| `True` | `True` | Return valid `g` and `h` in single-point mode |

Brinkpy does not check for the combination of `DOFreturnsGradient=False` with `DOFreturnsHessian=True`. Whether it works depends on whether SciPy's `minimize` method accepts a Hessian without a gradient. In practice, if you can derive the Hessian analytically, the gradient is usually straightforward, so provide both.

## Worked DOF Example (`Sorensen81Problem.py`)

In `Sorensen81Problem.py`, the only design variable is `z`, so:

- `DesignVariables = ["z"]`
- `d = [z]`
- `D` is empty, because `z` is the only deterministic variable and it is the design variable

The objective function is:

```python
def DOF(d, D):
    z = d
    f = z

    g = []
    h = []
    if d.ndim == 1:
        g = np.array([1.0])
        h = np.array([[0.0]])

    return f, g, h
```

For that example:

- `f = z`
- `df/dz = 1`
- `d2f/dz2 = 0`

So the valid single-point derivative returns are:

```python
g = np.array([1.0])
h = np.array([[0.0]])
```

The `if d.ndim == 1` guard is important: it keeps vectorized objective evaluations lightweight while still providing derivatives when the optimizer needs them for single-point steps.

See [Objective Optimization Example](optimization.md) for a worked example and checklist.

## Validation Checklist

1. `DesignProblem` exists when running `brinkpy design ...`.
2. Exactly one of `TargetBeta` or `TargetPf` is provided.
3. If `fractiles` is provided, its length matches the number of stochastic variables. It is required for Inverse FORM and optional for objective optimization.
4. If `cases` are provided, each case defines `mean` and the same spread parameter (`std` or `cv`) as the top-level `StochasticVariables`, in the same variable order as `StochasticVariables.name`.
5. If `cases` are omitted, confirm the implicit `default` case from `StochasticVariables` is the intended scenario.
6. If analytic derivatives are advertised (`LSFreturnsGradient`/`LSFreturnsHessian`), `LSF` actually returns valid derivatives in single-point mode.
7. For objective optimization, `DesignObjectiveFunction` accepts `(d, D)`, with `d` in `DesignVariables` order and `D` holding the remaining deterministic variables in `DeterministicVariables.name` order.
8. For objective optimization, `DesignObjectiveFunction` and its derivative flags are consistent with the actual DOF return signature.
9. If analytic objective derivatives are advertised (`DOFreturnsGradient`/`DOFreturnsHessian`), the DOF returns valid derivatives in single-point mode and placeholders otherwise.
