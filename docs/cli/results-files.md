# Result Files

Every run of `analyze`, `design`, or `simulate` saves its output files in a new folder inside `results/` in your project folder.

## Where Results Are Saved

Each run gets its own folder, named after the date and time of the run:

```text
results/<YYYY-MM-DD>/<HH-MM-SS>/
```

Inside that folder, files are named:

```text
<ProblemName>-<suffix>.<ext>
```

- `<ProblemName>` comes from the problem definition.
- `<suffix>` is the last 5 characters of the server request ID. It changes on every run.
- `<ext>` is the file type (see below).

The profile file is the exception. It is saved as `profile-<suffix>.yaml`.

## What Each File Contains

| File | Contents | Saved when |
|---|---|---|
| `.xlsx` | Summary of the results for the command you ran | `save_excel_summary` is `true` (default) |
| `.pdf` | All plots generated during the run | `save_plots_to_pdf` is `true` (default) and the run produces plots |
| `.pickle` | The same plots as Matplotlib figure objects, which you can reopen and edit | `save_plots_to_pickle` is `true` (default) and the run produces plots |
| `.json` | The problem definition as you entered it, plus all results | Always |
| `.py` | A copy of your original problem file | Always |
| `profile-<suffix>.yaml` | The profile used for the run | Always |

The Excel file is the main place to read your results. The JSON file contains the same results in raw form, so most users will not need it.

The `.py` and `.yaml` files are saved so that each results folder is self-contained. They let you check the problem setup and settings that produced the results, and reproduce the run later. They are also a useful reference when learning how problem files and profiles work.

## Choosing Which Files Are Saved

Three options in the `reporting_options` section of your profile control which files are created. All three are `true` by default:

```yaml
reporting_options:
  save_plots_to_pdf: true
  save_plots_to_pickle: true
  save_excel_summary: true
```

Set an option to `false` in your profile to skip that file. See [Reporting Options](../profiles/profile-reference.md#reporting-options) for details.

## Opening Saved Plots

To open the results automatically when a run finishes, including the plots, add `--open-results` (`-o`) to the command.

To reopen the plots from a `.pickle` file later, load the file in Python:

```python
import pickle
import matplotlib.pyplot as plt

with open("results/2026-10-30/14-05-12/AT610-ab12c.pickle", "rb") as f:
    figures = pickle.load(f)  # a list of Matplotlib figures

for fig in figures:
    plt.figure(fig.number)
plt.show()
```

Replace the path with the one for your run. Once loaded, the figures can be edited like any other Matplotlib figure, for example to change labels or styles for a report.

## Design Runs

`design` runs do not generate plots, so no `.pdf` or `.pickle` file is created for them.

!!! info "API-side file retention"
	Brinkpy does not retain run files on the API side after processing completes. Submitted problem modules and generated artifacts (for example `.xlsx`, `.pdf`, and `.pickle`) are removed using secure deletion (`srm`).
