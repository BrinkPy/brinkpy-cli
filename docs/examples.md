# Packaged Example Problems

Brinkpy CLI includes packaged example problems to help you get started with reliability analysis, design optimization, and Monte Carlo simulation.

The examples are meant to be opened and modified. Use them as templates for your own problems, and see [Problem Definition](problem-authoring/index.md) for a full description of the problem file format.

## Copying Examples to Your Project Folder

First, copy the packaged example problems into your project folder (see [CLI Basics](cli/basics.md) if you have not set one up yet):

```bash
brinkpy examples copy
```

Alias:

```bash
brinkpy examples cp
```

This creates a `problems/` folder in your project folder and copies the examples into it.

Copying never overwrites files that already exist in `problems/`, so your edits are safe if you run the command again. To restore the original versions of the examples, add `--force`:

```bash
brinkpy examples copy --force
```

## Listing Available Examples

List the packaged example files available in your installed Brinkpy package:

```bash
brinkpy examples list
```

Alias:

```bash
brinkpy examples ls
```

This displays a table of packaged example problems.

To see the files copied into your project folder, open `problems/` directly.

## Available Examples

Every example works with `analyze` and `simulate`. Examples marked in the **Design** column also define a `DesignProblem` and work with `design`. Six examples have a step-by-step walkthrough in the documentation.

| Example | Source | Design | Walkthrough |
|---|---|:-:|---|
| `AT610Problem` | Ang and Tang (1990), Vol. II, Problem 6.10 | | [FORM](problem-authoring/analyze/form-only.md) |
| `AT622Problem` | Ang and Tang (1990), Vol. II, Problem 6.22 | ✓ | |
| `AT624Problem` | Ang and Tang (1990), Vol. II, Problem 6.24 | ✓ | [Inverse FORM](problem-authoring/design/inverse-form.md) |
| `AT625Problem` | Ang and Tang (1990), Vol. II, Problem 6.25 | ✓ | [Inverse FORM](problem-authoring/design/inverse-form.md) |
| `AT68Problem` | Ang and Tang (1990), Vol. II, Problem 6.8 | | |
| `AU1dProblem` | [Au and Beck (1999)](https://people.duke.edu/~hpgavin/risk/Au-1999.pdf), Example 1 | | |
| `AU2Problem` | [Au and Beck (1999)](https://people.duke.edu/~hpgavin/risk/Au-1999.pdf), Example 2 | | [Importance Sampling](problem-authoring/simulate/importance-sampling.md) |
| `AU3Problem` | [Au and Beck (1999)](https://people.duke.edu/~hpgavin/risk/Au-1999.pdf), Example 3 | | |
| `Chan1Problem` | [Chan and Low (2011)](https://onlinelibrary.wiley.com/doi/full/10.1002/nag.1057), Problem 1 | | |
| `Chan2Problem` | [Chan and Low (2011)](https://onlinelibrary.wiley.com/doi/full/10.1002/nag.1057), Problem 2 | | [Classic Monte Carlo](problem-authoring/simulate/classic-monte-carlo.md) |
| `Chan3Problem` | [Chan and Low (2011)](https://onlinelibrary.wiley.com/doi/full/10.1002/nag.1057), Problem 3 | | [SORM + Monte Carlo](problem-authoring/analyze/sorm-monte-carlo.md) |
| `Dai1Problem` | [Dai et al. (2014)](https://www.sciencedirect.com/science/article/pii/S0167473014000162), Example 1 | | |
| `Ji1Problem` | [Ji et al. (2024)](https://onlinelibrary.wiley.com/doi/10.1002/nag.3524), Problem 1 | ✓ | |
| `Ji2Problem` | [Ji et al. (2024)](https://onlinelibrary.wiley.com/doi/10.1002/nag.3524), Problem 2 | ✓ | |
| `PipecorrProblem` | [Netto et al. (2005)](https://www.sciencedirect.com/science/article/pii/S0143974X05000453) | ✓ | |
| `Sorensen81Problem` | [Sorensen (2004)](https://filelist.tudelft.nl/TBM/Over%20faculteit/Afdelingen/Values%2C%20Technology%20and%20Innovation/People/Full%20Professors/Pieter%20van%20Gelder/Citations/citatie215.pdf), Chapter 8, Problem 1 | ✓ | [Optimization](problem-authoring/design/optimization.md) |

Each example file also lists its source at the top.

## Using Example Problems

When you run analysis, design, or simulation, Brinkpy opens a file-selection dialog so you can choose a problem file from `problems/`.

Analysis:

```bash
brinkpy analyze
```

Design (choose an example marked in the **Design** column):

```bash
brinkpy design
```

Monte Carlo simulation:

```bash
brinkpy simulate
```

Each command runs with its default options and the built-in `default` profile. To learn what each command does and how to change its options, see [Command Overview](cli/command-overview.md).

Brinkpy asks which problem file to use each time you run a command. The choice is not saved in your profile.
