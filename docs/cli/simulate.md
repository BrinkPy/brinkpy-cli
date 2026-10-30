# Simulate: Monte Carlo Simulation

Run Monte Carlo simulation to estimate the failure probability, including rare events. Importance sampling is optional, and the First-Order and Second-Order Reliability Methods (FORM and SORM) can be included for comparison.

!!! info "Before your first run"
	If you want to test this command with packaged sample problems, first run:
	```bash
	brinkpy examples copy
	```
	Then select a problem file from the `problems/` folder in your project folder when the file picker opens.

## Basic Usage

Usage: `brinkpy simulate <profile> [OPTIONS]`

## Command Options

### Monte Carlo Options

- `--mc-with-is`, `-i`: Use importance sampling with Monte Carlo simulation

### Reliability Methods

- `--include-form`, `-f`: Include first-order reliability method (FORM) analysis
- `--include-sorm`, `-s`: Include second-order reliability method (SORM) analysis (automatically enables FORM)

### Plotting Options

- `--plot-lsf`, `-l`: Plot the limit state function (LSF)
- `--plot-pdfs`, `-p`: Plot the probability density functions (PDFs) of the random variables

### General Options

- `--open-results`, `-o`: Open result files after completion — including the Excel report, the PDF report, and any Matplotlib figures saved as pickle files

## Examples

### Basic Monte Carlo Simulation
```bash
brinkpy simulate default
```

### Monte Carlo with Importance Sampling
```bash
brinkpy simulate default --mc-with-is
```

### Monte Carlo with FORM, SORM, and Plots
```bash
brinkpy simulate default -f -s -l -p
```

### Importance Sampling with SORM and PDF Plots
```bash
brinkpy simulate default -i -s -p
```

### Using a Custom Profile
```bash
brinkpy simulate myprofile --include-form --plot-pdfs
```

Replace `myprofile` with the name of a profile you created. See [Profile Management](../profiles/index.md).

!!! tip "Combining short flags"
	Short flags can be merged into a single argument. For example:
	```bash
	brinkpy simulate default -f -s -l -p
	```
	is equivalent to:
	```bash
	brinkpy simulate default -fslp
	```
	Both forms are valid. The expanded form is easier to read, and the combined form is faster to type.

## Notes

- If `--include-sorm` is specified without `--include-form`, FORM is automatically enabled
- If the importance sampling method is set to `mpp_normal` in the profile, FORM is automatically enabled. See [Importance Sampling Settings](../profiles/profile-reference.md#importance-sampling-settings).
- If `--plot-lsf` is specified and `plot_failure_point` is enabled in the profile (the default), FORM is automatically enabled to locate the failure point. See [LSF Plot Options](../profiles/profile-reference.md#lsf-plot-options).
- Monte Carlo sample size is configured in the profile. See [Monte Carlo Settings](../profiles/profile-reference.md#monte-carlo-settings).

## Aliases

- `sim`: Short alias
