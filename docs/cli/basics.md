# CLI Basics for Brinkpy Users

This page is for users who are new to command-line tools.

!!! note "Prerequisites"
    You need Python installed and a working terminal. An IDE is optional but recommended for editing problem files, especially if you are new to Python. If you are starting from scratch, see the [Getting Started with Python in VS Code](https://code.visualstudio.com/docs/python/python-tutorial) guide.

## What Is a CLI?

A command-line interface (CLI) lets you run software by typing commands in a terminal.

For Brinkpy, the typical pattern is:

```text
brinkpy <command> <profile> [options]
```

Example:

```bash
brinkpy analyze default --include-sorm --plot-rfad
```

## Why Brinkpy Uses a CLI

- Reduced need for custom scripting in routine workflows
- Reproducible workflows for coursework and research
- Easy automation for repeated studies

## First-Run Checklist

1. Install Brinkpy:

    ```bash
    pip install brinkpy
    ```

2. Confirm the CLI is available:

    ```bash
    brinkpy --help
    ```

3. Copy packaged example problems:

    ```bash
    brinkpy examples cp
    ```

4. Run a first analysis and select one of the example problems from the file picker:

    ```bash
    brinkpy analyze default --include-sorm --plot-rfad
    ```

## Understanding Outputs

Brinkpy saves run outputs under timestamped folders in `results/`.

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

- Use `cd <folder>` to move into your project directory before running commands.
- Start with packaged examples before editing your own problem modules.
- If a command fails, run `brinkpy --help` or `<command> --help` and verify the options you entered.
