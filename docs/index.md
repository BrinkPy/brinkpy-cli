# Brinkpy CLI: FORM, SORM, RBDO, and Monte Carlo Simulation in Python

Brinkpy CLI is a Python command-line tool for reliability analysis, reliability-based design optimization, and simulation workflows using profile-based configuration.

!!! quote "Why Brinkpy?"
    Every reliability problem has an edge: the limit-state surface where safe becomes failed. The reliability index measures how far you stand from that **brink**{ .brand-word }. FORM and SORM find the point where you are most likely to cross it, design keeps you a set distance back, and simulation samples both sides to count how often you go over. The ***py***{ .brand-word } is for Python.

It supports First-Order Reliability Method (FORM), Second-Order Reliability Method (SORM), Inverse FORM, Inverse SORM, Reliability-Based Design Optimization (RBDO), Monte Carlo simulation, and Importance Sampling for rare-event probability estimation, with correlated and non-normal random-variable support via Nataf transformation.

Run outputs include reliability metrics and design points, tabulated summaries (Excel/JSON), plot reports (PDF), and pickled Matplotlib figure objects for post-processing.

The documentation is written for practical use. Method descriptions are intentionally concise, and method-specific references are consolidated in the [Profile Options Reference](profiles/profile-reference.md).

## Who This Tool Is For

Brinkpy CLI was developed with academia in mind. The primary audience is students, instructors, and researchers working in risk and reliability, probabilistic failure analysis, and advanced probability and statistics.

Typical use cases include:

- Courses on risk and reliability methods, structural reliability, probabilistic analysis of failure, and advanced probability and statistics.
- Research at universities and research centers focused on reliability methods, failure analysis, code calibration and development, and related uncertainty-quantification workflows.

Recommended background readings are listed at [Recommended Texts and References](problem-authoring/recommended-texts.md).

## Core Workflows

Brinkpy CLI provides five core reliability workflows:

- **FORM**: Fast baseline reliability assessment.  
    → [Analyze Command](cli/analyze.md) | [FORM Example](problem-authoring/analyze/form-only.md)
- **SORM**: Curvature-aware reliability refinement at the MPP.  
    → [SORM + Monte Carlo Example](problem-authoring/analyze/sorm-monte-carlo.md)
- **Inverse FORM / Inverse SORM**: Reliability-targeted factor calibration and design-point back-calculation.  
    → [Design Command](cli/design.md) | [Inverse FORM Examples](problem-authoring/design/inverse-form.md)
- **RBDO**: Optimization under reliability constraints.  
    → [Design Command](cli/design.md) | [Optimization Examples](problem-authoring/design/optimization.md)
- **Monte Carlo + Importance Sampling**: Distribution-level failure-probability validation and tail exploration.  
    → [Simulate Command](cli/simulate.md) | [Classic Monte Carlo](problem-authoring/simulate/classic-monte-carlo.md) | [Importance Sampling](problem-authoring/simulate/importance-sampling.md)

## New to CLI?

A CLI (command-line interface) is a way to run tools by typing commands in a terminal window.

Brinkpy CLI uses this workflow because it reduces custom scripting for routine workflows, supports reproducible runs, and enables easy automation.

If you are new to terminal-based tools, start with [CLI Basics for Brinkpy Users](cli/basics.md) for a short orientation and first-run checklist.

## Requirements

- Python 3.10+
- Internet connection for API access and authentication

## Quick Start

1. Install the CLI (and required dependencies) from PyPI:

    ```bash
    pip install brinkpy
    ```

2. View available commands:

    ```bash
    brinkpy --help
    ```

3. Copy example problems:

    ```bash
    brinkpy examples cp
    ```

4. Run an analysis with the default profile:

    ```bash
    brinkpy analyze default --include-sorm --plot-rfad
    ```

## Execution Model

Brinkpy CLI runs computations through the hosted Brinkpy API. The CLI handles local orchestration (profile loading, problem-file selection, command options, and local result saving), while the numerical reliability/design/simulation solve is executed on the API side.

!!! info "Data handling and file retention"
    Brinkpy does not retain uploaded problem modules or generated run files on the API side after a run completes. The backend uses secure deletion (`srm`) to remove submitted problem files and generated artifacts (such as Excel, PDF, and pickled Matplotlib files) after processing.

## Pricing

!!! info "Pricing and Sustainability Notice"
    Brinkpy CLI is **free to use** at this time. The CLI communicates with a hosted API, and the associated computation and infrastructure costs are currently funded by the developer during this early phase of operation.

    To support ongoing maintenance and service delivery as usage grows, a monthly subscription of approximately **$8/month** is planned for a future release.

    Any transition from free access to a paid subscription model will be communicated in advance. Existing users will receive clear notice before any pricing changes take effect.

## Commands and Help

See [CLI Command Overview](cli/command-overview.md) for command behavior, usage patterns, and links to full option references for `analyze`, `design`, and `simulate`.

All commands support the `--help` flag for detailed usage information:

```bash
brinkpy --help
brinkpy analyze --help
brinkpy profile --help
```

## Configuration

Brinkpy CLI uses YAML profile files to configure run parameters across `analyze`, `design`, and `simulate`, including reliability methods, plotting options (LSF/RFAD), and reporting outputs.

For profile workflows and command usage, see [Profiles](profiles/index.md).
For complete option keys and defaults, see [Profile Options Reference](profiles/profile-reference.md).

## Authentication

Brinkpy CLI authenticates automatically the first time you run any command. If no valid token is found, you will be prompted to log in before the command proceeds.

For manual authentication and status checks, use `brinkpy user auth` and `brinkpy user id`.
See [Auth](auth.md) for full flow details and troubleshooting.

## Citing Brinkpy

If you use Brinkpy in journal papers, reports, theses, or other scholarly work, cite Brinkpy itself. Additionally, cite the underlying reliability methods (FORM, SORM, Monte Carlo, etc.) based on relevant academic sources in your field.

- Carrasco, C. (2026). *Brinkpy CLI*. Zenodo. <https://doi.org/10.5281/zenodo.23752820>

Include the exact Brinkpy version used in your work. For version-specific DOI citations, use the corresponding Zenodo release record.

## Software References

For third-party Python library citation guidance, see [Software and Library References](software-references.md). That section separates:

- CLI dependencies users install in their environment
- API dependencies documented for attribution/credit only

## Contact

For questions, feedback, or support, reach out at [brinkpy.app@gmail.com](mailto:brinkpy.app@gmail.com).
