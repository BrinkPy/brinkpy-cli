# Brinkpy CLI

Brinkpy CLI is a Python command-line tool for reliability analysis, reliability-based design optimization, and simulation workflows using profile-based configuration.

It supports First-Order Reliability Method (FORM), Second-Order Reliability Method (SORM), Inverse FORM, Inverse SORM, Monte Carlo simulation, and Importance Sampling for rare-event probability estimation. Workflows cover forward reliability evaluation, reliability-constrained design, and post-design simulation with a consistent problem-module interface and support for correlated non-normal variables via Nataf transformation.

Run outputs are designed for engineering decisions and reporting, including reliability metrics and design points, tabulated summaries (Excel/JSON), plot reports (PDF), and pickled Matplotlib figure objects for post-processing.

## What Brinkpy CLI Does

- Reliability analysis with FORM and SORM
- Reliability-based design with inverse FORM/SORM workflows
- Monte Carlo and importance sampling simulation
- Profile-based YAML configuration for repeatable runs

## Install and Quick Start

On first use, Brinkpy will prompt you to authenticate. If you do not already have an account, you can create one during the sign-in flow.

```zsh
# Install from PyPI
pip install brinkpy

# Show help
brinkpy --help

# Copy packaged example problems
brinkpy examples copy

# Run an analysis with the default profile
brinkpy analyze default --include-sorm --plot-rfad
```

## Profile Management

Profiles are YAML files under `profiles/` that control run options.

```zsh
# Create and edit a custom profile
brinkpy profile new custom
brinkpy profile nano custom
# or
brinkpy profile vim custom

# Validate, list, copy, rename
brinkpy profile validate custom
brinkpy profile list
brinkpy profile copy default mycopy
brinkpy profile rename oldname newname
```

## Full Documentation

Read the full documentation at:

- https://brinkpy.app/

## Requirements

- Python 3.10+
- Internet connection for API access and authentication

## Testing and Validation

Unit and integration tests are provided in the `tests/` directory.

```zsh
# Run unit tests
python -m unittest discover tests -p 'test_*.py' -v

# Run integration tests with real API calls
BRINKPY_RUN_API_TESTS=1 python -m unittest tests.test_cli_api_integration -v
```

See the [testing guide](https://github.com/BrinkPy/brinkpy-cli/blob/main/TESTING.md) for details on test structure and rate limit behavior.

## Notes

- Auth0 device flow uses public values (domain, client ID, audience). No client secret is used in the CLI.
