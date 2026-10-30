# CLI Basics for Brinkpy Users

This page is for users who are new to command-line tools.

!!! note "Prerequisites"
    You need Python 3.10 or newer and a working terminal. An IDE is optional but recommended for editing problem files, especially if you are new to Python. If you are starting from scratch, see the [Getting Started with Python in VS Code](https://code.visualstudio.com/docs/python/python-tutorial) guide.

## What Is a CLI?

A command-line interface (CLI) lets you run software by typing commands in a terminal.

To run an analysis, design, or simulation with Brinkpy, the pattern is:

```text
brinkpy <command> <profile> [options]
```

Replace the parts in `< >` with your own values. Parts in `[ ]` are optional. A profile is a named settings file, and Brinkpy includes a built-in one called `default`.

Example:

```bash
brinkpy analyze default --include-sorm --plot-rfad
```

## First-Run Checklist

1. Create a project folder and move into it:

    ```bash
    mkdir brinkpy-work
    cd brinkpy-work
    ```

    Brinkpy reads and writes its `problems/`, `profiles/`, and `results/` folders in the folder you run it from, so always run it from your project folder.

2. Install Brinkpy:

    ```bash
    pip install brinkpy
    ```

3. Confirm the CLI is available:

    ```bash
    brinkpy --help
    ```

4. Copy packaged example problems:

    ```bash
    brinkpy examples cp
    ```

5. Run a first analysis and select one of the example problems from the file picker:

    ```bash
    brinkpy analyze
    ```

    The first time you run an analysis, Brinkpy asks you to sign in through your browser.

## Understanding Outputs

Brinkpy saves run outputs in timestamped folders inside `results/` in your project folder.

See [Result Files](results-files.md) for path and filename patterns.

## Useful Help Commands

```bash
brinkpy --help
brinkpy analyze --help
brinkpy design --help
brinkpy simulate --help
brinkpy profile --help
```

## Common Beginner Tips

- Use `cd <folder>` to move into your project folder before running commands.
- Start with packaged examples before editing your own problem modules.
- If a command fails, run `brinkpy --help` or `brinkpy <command> --help` and verify the options you entered.
