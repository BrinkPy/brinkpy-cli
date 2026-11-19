"""
Record what a brinkpy command prints and save it as an SVG image for the docs.

The image shows the terminal output exactly as a user sees it: colors, table lines, and emoji, in a terminal
window. Rich draws the SVG, positioning every character itself, so the tables line up in any browser.

Usage, from the project root (the folder with problems/):

    python scripts/terminal_svg.py OUTPUT.svg analyze default -s -r
        Only the opening lines: the profile notice, the command and profile line, any warnings, and the options
        table. Nothing is sent to the API.

    python scripts/terminal_svg.py --run-with problems/AT68Problem.py OUTPUT.svg analyze
        A full run against the API with that problem file. The file picker is replaced by the file given, so the
        image still shows the "Please select a problem file" line a user sees. The run's results are saved in
        results/ as usual. Set BRINKPY_API_URL to choose the API.

Regenerate the images in docs/cli/images/ when the CLI's output changes.
"""

import argparse
import contextlib
import sys
from pathlib import Path

from rich.console import Console

import brinkpy.brinkpy as cli
from brinkpy.utils import api_utils, auth_cli, profile_management, utilities

TERMINAL_WIDTH = 100


def main() -> None:
    parser = argparse.ArgumentParser(description="Save the terminal output of a brinkpy command as an SVG.")
    # --run-with goes before OUTPUT: everything after OUTPUT is the brinkpy command
    parser.add_argument("--run-with", type=Path, help="Run the command against the API with this problem file")
    parser.add_argument("output", type=Path, help="SVG file to write")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="The brinkpy command and its options")
    options = parser.parse_args()
    if not options.command:
        parser.error("Give the brinkpy command to record, for example: analyze default -s")

    # One recording console in place of the console of each CLI module
    console = Console(record=True, width=TERMINAL_WIDTH, force_terminal=True, color_system="truecolor")
    for module in (cli, api_utils, auth_cli, profile_management, utilities):
        module.console = console
    # A spinner redraws itself in place and disappears when its task ends, but a recording keeps every frame on
    # one line. Leave it out, so the image shows the terminal as it looks when the command finishes.
    console.status = lambda *args, **kwargs: contextlib.nullcontext()

    if options.run_with is None:
        cli.run_app = lambda *args, **kwargs: None  # Stop before the API
    else:
        problem_file = options.run_with.resolve()
        if not problem_file.is_file():
            parser.error(f"Problem file not found: {problem_file}")
        api_utils.get_problem_file_name = lambda problems_path: problem_file  # In place of the file picker

    command_line = "brinkpy " + " ".join(options.command)
    console.print(f"[bold green]$[/] {command_line}")
    try:
        cli.app(options.command, standalone_mode=False)
    except SystemExit:
        pass

    options.output.parent.mkdir(parents=True, exist_ok=True)
    console.save_svg(str(options.output), title=command_line)
    print(f"Saved {options.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
