---
description: "Why use Brinkpy when AI can write reliability code: checks on every run, many methods from one problem file, and verification against published results."
---

# Why Use Brinkpy

Every result Brinkpy produces can, in principle, be reproduced with general scientific libraries and your own code. A first-order reliability method (FORM) analysis of a simple problem takes a few dozen lines with SciPy. Scripts like that are easier than ever to write, including with AI assistants.

The harder question is whether the number is right. A script that runs and returns a reasonable-looking reliability index is not the same as a result you can trust. In reliability analysis, a wrong answer rarely looks wrong. Brinkpy is built around that problem.

## Checks on Every Run

Brinkpy checks the problem and the solution, not only the arithmetic:

- **Problem validation.** Before any analysis, Brinkpy checks the stochastic variable definitions and the output of the limit state function, and reports how many function calls the check needed.
- **Derivative checks.** When the limit state function returns its gradient or Hessian, Brinkpy compares them with finite differences before using them. The same applies to the derivatives of design objective and constraint functions. A wrong derivative is one of the most common errors in hand-written reliability code, and it can lead the solver to the wrong point without any sign of failure. See [Derivative Checking](profiles/profile-reference.md#derivative-checking).
- **Bounds and constraints handled by the solver.** Variable bounds, truncated distributions, and constraints on functions of the variables are passed to the solver as constraints. Brinkpy reports which limits are active at the solution and how strongly they affect the result. A constraint can, for example, keep the search inside the range where a fitted limit state function is valid, as in the [pipeline corrosion example](problem-authoring/design/stochastic-constraints.md). See [Bounds and Truncation](problem-authoring/index.md#bounds-and-truncation) and [Constraints on Stochastic Variables](problem-authoring/index.md#constraints-on-stochastic-variables).
- **Diagnostic notes.** Each run reports notes about anything that deserves attention, such as non-finite limit state function values, the cost of building an importance sampling proposal, or Markov chain Monte Carlo (MCMC) convergence statistics.

## Many Methods, One Problem File

The same problem file runs with every method, under the same conventions for signs, transformations, and results:

- FORM, and the second-order reliability method (SORM) with ten approximations, including the second-order saddlepoint approximation (SOSPA) and the inverse fast Fourier transform (IFFT) method.
- Inverse FORM and Inverse SORM for reliability-targeted design values and partial factors.
- Reliability-based design optimization with an objective function and constraints.
- Monte Carlo simulation, with importance sampling proposals built by kernel density estimation, Gaussian mixtures, MCMC, or a normal distribution at the most probable point.
- Plots of the probability density functions, the limit state function, and the reliability-based failure assessment diagram (RFAD).
- Correlated and non-normal variables through the Nataf transformation.

Comparing methods on the same problem, for example FORM against several SORM approximations and Monte Carlo, takes a change of command flags or profile options, not new code.

## Verification

Brinkpy is verified against published results. Every [packaged example](examples.md), and a larger set of problems from the literature, was checked against the results in the paper or book it comes from. The results agree, or the example's page explains the difference. These problems are part of the test suite of the Brinkpy API, which runs every time the API changes, so a change that breaks a known answer is caught before it is released.

## Reproducible Results

Each run saves a copy of the problem file, the profile with every setting used, a request ID, and the results in Excel, JSON, and PDF files. Another person can rerun the same problem with the same settings, or check exactly how a result was produced. See [CLI Result Files](cli/results-files.md).

## Who Benefits Most

- **Students and instructors** can focus on the methods and the results instead of debugging an implementation. The [walkthrough examples](problem-authoring/index.md#how-this-section-is-organized) use problems from standard textbooks.
- **Researchers** can compare methods on the same problem and cite a fixed, versioned tool. See [Citing Brinkpy](index.md#citing-brinkpy).
- **Engineers** who need reliability results but not a reliability code of their own get a checked implementation without writing one.
