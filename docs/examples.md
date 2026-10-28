# Packaged Example Problems

Brinkpy CLI includes packaged example problems to help you get started with reliability analysis, design optimization, and Monte Carlo simulation.

## Copying Examples to Working Directory

First, copy the packaged example problems into your current working directory:

```bash
brinkpy examples copy
```

Alias:

```bash
brinkpy examples cp
```

This creates a local `./problems/` folder in your current directory.

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

To see files copied into your local working directory, inspect `./problems/` directly.

## Using Example Problems

When you run analysis, design, or simulation, Brinkpy opens a file-selection dialog so you can choose a problem file from `./problems/`.

Analysis:

```bash
brinkpy analyze default --include-sorm --plot-rfad
```

Design optimization:

```bash
brinkpy design default --use-sorm
```

Monte Carlo simulation:

```bash
brinkpy simulate default --plot-pdfs
```

The problem file is selected at run time for each command and is not persisted as part of the command options.
