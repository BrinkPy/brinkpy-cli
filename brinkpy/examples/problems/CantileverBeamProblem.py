# Description: A cantilever beam design problem. The objective is to minimize the weight.
# https://www.tandfonline.com/doi/full/10.1080/0305215X.2018.1440292
import numpy as np


def Problem():
    Problem = {
        "Name": "Cantilever Beam",
        "LimitStateFunction": cantilever_beam_func,
        "LSFisVectorized": True,
        "LSFisSmooth": False,
        "LSFreturnsGradient": False,
        "LSFreturnsHessian": False,
        "LSFreturnsLandR": False,
        "DeterministicVariables": {
            "name": ["mb", "mh", "L", "Do"],  # mb and mh are the mean values of b and h
            "value": [2.0, 4.0, 100.0, 2.25],
        },
        "StochasticVariables": {
            "name": ["b", "h", "Px", "Py", "E", "Sy"],
            "type": ["normal", "normal", "normal", "normal", "normal", "normal"],
            "mean": [0.0, 0.0, 500.0, 1000.0, 2.9e7, 3.9e4],
            "std": [0.01, 0.01, 50.0, 100.0, 1e5, 500.0],
            "lb": [-np.inf, -np.inf, 1e-3, 1e-3, 1e-3, 1e-3],
            "ub": [np.inf, np.inf, np.inf, np.inf, np.inf, np.inf],
        },
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
    }

    return Problem


def DOF(d, D):
    # Objective function, gradient vector and Hessian matrix
    # Volume of the cantilever beam
    mb, mh = d
    L, Do = D
    f = mb * mh * L
    g = []
    h = []
    if d.ndim == 1:
        g = np.array([mh * L, mb * L])
        h = np.array([[0.0, L], [L, 0.0]])

    return f, g, h


# h_over_b and its derivatives are used only when the DesignConstraints key is added (see the walkthrough)
def h_over_b(d, D):
    # d is a (n,) design variable array where n is the number of design variables
    # D is a (m,) deterministic variable array where m is the number of deterministic variables excluding the design variables
    mb, mh = d
    return mh / mb


def h_over_b_jacobian(d, D):
    # Jacobian of the constraint function with respect to the design variables
    # d is a (n,) design variable array where n is the number of design variables
    # D is a (m,) deterministic variable array where m is the number of deterministic variables excluding the design variables
    mb, mh = d
    return np.array([[-mh / (mb**2), 1.0 / mb]])


def h_over_b_hessian(d, v, D):
    # Hessian of np.dot(h_over_b, v)
    # d is a (n,) design variable array where n is the number of design variables
    # v is a (p,) Lagrange multiplier array where p is the number of outputs (here 1)
    # D is a (m,) deterministic variable array where m is the number of deterministic variables excluding the design variables
    mb, mh = d
    return v * np.array([[2 * mh / (mb**3), -1.0 / (mb**2)], [-1.0 / (mb**2), 0.0]])


def cantilever_beam_func(X, D):
    # X is a nxs matrix where n is the number of stochastic variables and s is the number of samples
    # If X.ndim == 1 then X is a (n,) matrix where n is the number of stochastic variables
    # D is a (m,) array where m is the number of deterministic variables

    b, h, Px, Py, E, Sy = X
    mb, mh, L, Do = D

    b = mb + b  # b is the deviation from the design mean mb
    h = mh + h

    # Two limit states:
    # 1) Maximum bending stress at the fixed end of the cantilever beam < Sy (normalized)
    # 2) Maximum deflection at the free end of the cantilever beam < Do (normalized)
    g1 = (Sy - (6 * L) / (b * h) * (Px / b + Py / h)) / Sy
    g2 = (Do - (4 * L**3 / E) * ((Px / (b**3 * h)) ** 2 + (Py / (b * h**3)) ** 2) ** 0.5) / Do

    g = np.minimum(g1, g2)

    Load = []
    Resistance = []
    gg = []
    gh = []

    return g, gg, gh, Load, Resistance
