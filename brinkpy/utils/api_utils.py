"""
api_utils.py
Utility functions for interacting with the Brinkpy API endpoint.
Copyright (c) 2025 Cesar Carrasco. All rights reserved.
"""

import importlib
import importlib.util
import json
import os
import pathlib
import pickle
import platform
import re
import shutil
import subprocess
import sys
import time
import traceback
from collections import OrderedDict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Tuple

import filedialpy
import numpy as np
import requests
from matplotlib import pyplot as plt
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from brinkpy.utils.auth_cli import get_token
from brinkpy.utils.icons import ICON_ASK, ICON_DOWN, ICON_ERR, ICON_INFO, ICON_OK, ICON_WARN
from brinkpy.utils.path_helpers import copy_examples_to_working_dir, get_problems_dir, get_results_dir
from brinkpy.utils.profile_management import save_result_yaml_profile
from brinkpy.utils.utilities import safe_write_json

console = Console()


def get_timestamped_results_dir(base_results_path: Path) -> Path:
    """
    Create and return a timestamped subdirectory for storing results.
    Structure: results/YYYY-MM-DD/HH-MM-SS/

    Args:
        base_results_path: Base results directory

    Returns:
        Path to the timestamped subdirectory
    """
    now = datetime.now()
    date_dir = base_results_path / now.strftime("%Y-%m-%d")
    time_dir = date_dir / now.strftime("%H-%M-%S")
    time_dir.mkdir(parents=True, exist_ok=True)
    return time_dir


def result_file_stem(problem_json: Dict) -> str:
    """
    Return the stem shared by the result files of a run: <name>-<suffix>.

    The name is the problem's Name with each space, dot, slash, and colon
    replaced by an underscore. The suffix is the last 5 characters of the
    request ID.

    Args:
        problem_json: Problem dictionary with name and Request_ID

    Returns:
        File name stem without extension
    """
    name = problem_json.get("name", "result").translate(str.maketrans(" ./:", "____"))
    request_id = problem_json.get("Request_ID", "unknown")
    return f"{name}-{request_id[-5:]}"


def cleanup_old_results(base_results_path: Path, days: int = 30) -> None:
    """
    Remove result directories older than the specified number of days.

    Args:
        base_results_path: Base results directory
        days: Remove results older than this many days (default: 30)
    """
    if not base_results_path.exists():
        return

    cutoff_date = datetime.now() - timedelta(days=days)
    removed_count = 0

    # Iterate through date directories (YYYY-MM-DD)
    for date_dir in base_results_path.iterdir():
        if not date_dir.is_dir():
            continue

        try:
            # Parse directory name as date
            dir_date = datetime.strptime(date_dir.name, "%Y-%m-%d")
            if dir_date < cutoff_date:
                shutil.rmtree(date_dir)
                removed_count += 1
                console.print(f"{ICON_OK} Removed old results: {date_dir.name}")
        except ValueError:
            # Skip directories that don't match the date format
            continue

    if removed_count > 0:
        console.print(f"{ICON_OK} Cleaned up {removed_count} old result director{'y' if removed_count == 1 else 'ies'}")
    else:
        console.print(f"{ICON_INFO} No old results to clean up (keeping last {days} days)")


DEFAULT_API_URL = "https://brinkpy.up.railway.app"
_api_url_notice_shown = False


def get_api_url() -> str:
    """
    Return the base URL of the Brinkpy API.

    Set BRINKPY_API_URL (for example in .env.local) to use a local API
    during development. An empty value uses the default API. When the URL
    is not the default, a notice is printed once per run.

    Returns:
        str: API base URL without a trailing slash.
    """
    global _api_url_notice_shown
    url = (os.getenv("BRINKPY_API_URL") or DEFAULT_API_URL).rstrip("/")
    if url != DEFAULT_API_URL and not _api_url_notice_shown:
        console.print(f"{ICON_INFO} Using API at {url} (from BRINKPY_API_URL).", style="dim")
        _api_url_notice_shown = True
    return url


def setup_paths():
    """
    Set up the paths for running Brinkpy application.

    Returns:
        tuple: (url, results_path, problems_path)
    """
    url = get_api_url()

    # Create the directory to store the results if it doesn't exist
    results_path = get_results_dir().resolve()
    results_path.mkdir(parents=True, exist_ok=True)

    # Define the path to the problems directory
    problems_path = get_problems_dir().resolve()
    problems_path.mkdir(parents=True, exist_ok=True)

    return url, results_path, problems_path


def serialize_obj(obj: Any) -> Any:
    """
    Recursively serialize an object for JSON compatibility.

    - Converts numpy arrays -> lists
    - numpy scalars -> Python scalars
    - container types are processed recursively
    - dict keys are converted to strings when not already str
    """
    # Fast path for JSON-safe scalars
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return obj

    # Numpy handling
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, np.generic):
        return obj.item()

    # Containers
    if isinstance(obj, dict):
        out: Dict[str, Any] = {}
        for k, v in obj.items():
            # JSON requires string keys
            if not isinstance(k, str):
                k = str(serialize_obj(k))
            out[k] = serialize_obj(v)
        return out

    if isinstance(obj, (list, tuple)):
        return [serialize_obj(v) for v in obj]

    # Fallback — attempt to use __dict__ if available, else str()
    if hasattr(obj, "__dict__"):
        try:
            return serialize_obj(vars(obj))
        except Exception:
            pass

    return str(obj)


# The folder of the brinkpy package, whose code is not the user's
_BRINKPY_PACKAGE_DIR = Path(__file__).resolve().parent.parent

# How many lines of the user's module a message shows: where the error happened and the calls that led there
MAX_USER_FRAMES_SHOWN = 3


def _exception_chain(e: BaseException) -> list[BaseException]:
    """
    The exception and the exceptions it was raised from or while handling, outermost first, following the same
    rules as Python's traceback printing (__cause__, or __context__ unless suppressed).
    """
    chain = []
    seen = set()
    current = e
    while current is not None and id(current) not in seen:
        chain.append(current)
        seen.add(id(current))
        if current.__cause__ is not None:
            current = current.__cause__
        elif not current.__suppress_context__:
            current = current.__context__
        else:
            current = None
    return chain


def _same_file(filename: str | None, module_path: Path) -> bool:
    if not filename or filename.startswith("<"):
        return False
    try:
        return Path(filename).resolve() == module_path
    except (OSError, ValueError):
        return False


def _code_owner(filename: str) -> str:
    """The name of the library a file belongs to (for example numpy), "Brinkpy" or "Python"."""
    if filename.startswith("<"):  # <frozen importlib._bootstrap>
        return "Python"
    try:
        path = Path(filename).resolve()
    except (OSError, ValueError):
        return "Python"
    if path.is_relative_to(_BRINKPY_PACKAGE_DIR):
        return "Brinkpy"
    parts = path.parts
    for packages_dir in ("site-packages", "dist-packages"):
        if packages_dir in parts:
            index = parts.index(packages_dir)
            return parts[index + 1].removesuffix(".py") if index + 1 < len(parts) else "Python"
    return "Python"


def _describe_frame(frame: traceback.FrameSummary) -> str:
    code = (frame.line or "").strip()
    location = f"line {frame.lineno}" if frame.name == "<module>" else f"line {frame.lineno}, in {frame.name}"
    return location + (f": {code}" if code else "")


def get_exception_source(e: BaseException, module_path: Path | None = None) -> str:
    """
    One-line description of an exception for the user, without a final period.

    With module_path, the user's problem module: if the module appears in the traceback of the exception or of the
    exceptions it was raised from, the description is the error type and message, then the line of the module where
    the error happened and up to two lines that called it. When the error was raised in a library called from the
    module (for example numpy.linalg), it says so. A syntax error gives the line it reports.

    Otherwise, or without module_path, the description is only the error type and message. Brinkpy's own file names
    and code are left out, since the user can't act on them.

    Args:
        e (BaseException): The exception.
        module_path (Path | None, optional): The user's problem module.

    Returns:
        str: The description for the user.
    """
    chain = _exception_chain(e)
    exc, frames = e, []
    if module_path is not None:
        module_path = Path(module_path).resolve()
        # The innermost exception that passed through the user's module is the one the user can fix
        for candidate in reversed(chain):
            candidate_frames = [
                frame for frame in traceback.extract_tb(candidate.__traceback__) if _same_file(frame.filename, module_path)
            ]
            if isinstance(candidate, SyntaxError) and _same_file(candidate.filename, module_path) and candidate.lineno:
                text = (candidate.text or "").strip()
                candidate_frames.append(traceback.FrameSummary(str(module_path), candidate.lineno, "<module>", line=text))
            if candidate_frames:
                exc, frames = candidate, candidate_frames
                break

    # A SyntaxError's message ends with "(file, line n)", which the location below replaces
    message = exc.msg if isinstance(exc, SyntaxError) and frames and exc.msg else str(exc)
    message = message.strip()
    description = f"{type(exc).__name__}: {message}" if message else type(exc).__name__
    if not frames:
        return description.rstrip(".")

    separator = " " if description.endswith((".", "!", "?")) else ". "
    last_frame = traceback.extract_tb(exc.__traceback__)[-1] if exc.__traceback__ else None
    if isinstance(exc, SyntaxError) or last_frame is None or _same_file(last_frame.filename, module_path):
        location = "In your problem module: "
    else:
        location = f"Raised in {_code_owner(last_frame.filename)}, called from your problem module: "

    shown = frames[::-1][:MAX_USER_FRAMES_SHOWN]  # Innermost first
    location += "; called from ".join(_describe_frame(frame) for frame in shown)
    if len(frames) > MAX_USER_FRAMES_SHOWN:
        location += "; ..."
    return description + separator + location


def _print_panel(body: Text, title: str, border_style: str) -> None:
    """Print a message in a Rich panel, the style the CLI uses for errors and warnings."""
    console.print()
    console.print(Panel(body, title=title, title_align="left", border_style=border_style))
    console.print()


def handle_rate_limit_error(response: requests.Response) -> None:
    """
    Handle rate limit errors with a friendly, multi-line output in a yellow panel.
    """
    body = Text()
    try:
        error_data = response.json()
    except json.JSONDecodeError:
        body.append(f"{ICON_INFO} Unable to parse rate limit response. Please wait and try again.", style="blue")
        _print_panel(body, "Rate limit exceeded", "yellow")
        return

    endpoint = error_data.get("endpoint", "Unknown endpoint")
    limit_type = error_data.get("limit_type", "unknown")
    limit_exceeded = error_data.get("limit_exceeded", "Unknown limit")
    all_limits = error_data.get("all_limits", "Unknown limits")
    reason = error_data.get("reason", "Rate limiting active")
    suggestion = error_data.get("suggestion", "Please wait 15 seconds before retrying")

    lines = [(f"{ICON_INFO} Endpoint: {endpoint}", "blue")]
    if limit_type == "per_minute":
        lines += [
            (f"{ICON_WARN} Minute Limit Exceeded: {limit_exceeded}", "yellow"),
            (f"{ICON_INFO} All Limits: {all_limits}", "blue"),
            (f"{ICON_INFO} This means you're making requests too quickly", "blue"),
        ]
    elif limit_type == "per_day":
        lines += [
            (f"{ICON_WARN} Daily Limit Exceeded: {limit_exceeded}", "yellow"),
            (f"{ICON_INFO} All Limits: {all_limits}", "blue"),
            (f"{ICON_INFO} You've used up your daily quota", "blue"),
        ]
    else:
        lines += [
            (f"{ICON_WARN} Limit Exceeded: {limit_exceeded}", "yellow"),
            (f"{ICON_INFO} All Limits: {all_limits}", "blue"),
        ]
    lines += [(f"{ICON_INFO} Reason: {reason}", "blue"), (f"{ICON_INFO} Suggestion: {suggestion}", "blue")]

    for i, (line, style) in enumerate(lines):
        body.append(("\n" if i else "") + line, style=style)
    _print_panel(body, "Rate limit exceeded", "yellow")


def handle_other_http_errors(response: requests.Response, context_msg: str = "Error") -> None:
    """
    Print an HTTP error message from a Response in a red panel.

    When the API sends detail as {"code": ..., "message": ...}, the message was written
    for the user (a Brinkpy error about their problem), so the panel is titled "Error".
    Any other detail gets the context and status code as the title.
    """
    msg, code = _extract_error_detail(response)
    if code:
        title = "Error"
    else:
        title = f"{context_msg} · status code {response.status_code}"
        try:
            error_data = response.json()
            msg = str(error_data.get("detail", error_data)) if isinstance(error_data, dict) else str(error_data)
        except json.JSONDecodeError:
            msg = response.text
    # Text, not markup, so brackets in the message, such as "d = [1, 1]", print as written
    _print_panel(Text(f"{ICON_ERR} {msg}"), title, "red")


def _extract_error_detail(response: requests.Response) -> tuple[str, str | None]:
    """Return (message, machine_code) from a FastAPI error response."""
    try:
        error_data = response.json()
    except json.JSONDecodeError:
        return response.text, None

    detail = error_data.get("detail", error_data)

    # Handle detail as dict: {"code": "subscription_required", "message": "..."}
    if isinstance(detail, dict):
        code = detail.get("code")
        msg = detail.get("message") or detail.get("detail") or str(detail)
        return str(msg), str(code) if code is not None else None

    # Handle detail as string or any other value
    return str(detail), None


def download_single_file(
    url: str,
    file_type: str,
    request_id: str,
    max_retries: int = 3,
    timeout: int = 30,
    headers: Dict[str, str] | None = None,
) -> requests.Response:
    """
    Download a single file with retry and backoff.

    Returns a successful requests.Response or raises last exception.
    """
    file_url = f"{url.rstrip('/')}/{file_type}"
    params = {"request_id": request_id}

    for attempt in range(max_retries + 1):
        try:
            resp = requests.get(file_url, params=params, timeout=timeout, headers=headers)
            resp.raise_for_status()
            return resp

        except requests.exceptions.RequestException as e:
            is_last = attempt == max_retries

            resp_obj = getattr(e, "response", None)
            if resp_obj is not None:
                status = resp_obj.status_code
                # Handle 429 (rate limit) - should retry
                if status == 429:
                    console.print(
                        f"{ICON_INFO} Rate limited downloading {file_type} (attempt {attempt + 1}/{max_retries + 1})",
                        style="blue",
                    )
                    handle_rate_limit_error(resp_obj)
                    if not is_last:
                        wait_time = (2**attempt) + (0.1 * attempt)
                        time.sleep(wait_time)
                        continue
                    else:
                        raise
                # Handle other 4xx client errors - don't retry
                elif 400 <= status < 500:
                    console.print(f"{ICON_ERR} Client error downloading {file_type} (status {status})", style="red")
                    handle_other_http_errors(resp_obj, f"Error downloading {file_type} file")
                    raise
                # 5xx server errors - retry
                elif status >= 500:
                    if not is_last:
                        wait_time = (2**attempt) + (0.1 * attempt)
                        console.print(
                            f"{ICON_WARN} Server error ({status}) downloading {file_type}, retrying in {wait_time:.1f}s..."
                        )
                        time.sleep(wait_time)
                        continue
                    else:
                        handle_other_http_errors(resp_obj, f"Failed to download {file_type} after retries")
                        raise
            else:
                # Network-level errors (no response) - retry
                if not is_last:
                    wait_time = (2**attempt) + (0.1 * attempt)
                    console.print(
                        f"{ICON_WARN} Network error downloading {file_type}: {e}. Retrying in {wait_time:.1f}s..."
                    )
                    time.sleep(wait_time)
                    continue
                else:
                    console.print(f"{ICON_ERR} Failed downloading {file_type} after retries: {e}")
                    raise


def download_results(
    url: str, problem_json: json, results_dir: Path, reporting_options: Dict, max_retries: int = 3
) -> Tuple[List[Path], List[bool]]:
    """
    Download excel/pdf/pickle files for a completed problem.
    Files are saved directly to the provided results_dir (should be timestamped).

    Args:
        url: API base URL
        problem_json: Problem dictionary with Request_ID
        results_dir: Directory to save results (typically timestamped)
        reporting_options: Options for what files to download
        max_retries: Number of retry attempts for failed downloads

    Returns (file_paths, downloaded_flags)
    """
    results_dir = Path(results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)

    file_types = ["xlsx", "pdf", "pickle"]

    should_download = [
        reporting_options["save_excel_summary"],
        reporting_options["save_plots_to_pdf"] and ("FigureHandles" in problem_json),
        reporting_options["save_plots_to_pickle"] and ("FigureHandles" in problem_json),
    ]

    request_id = problem_json.get("Request_ID", "unknown")
    stem = result_file_stem(problem_json)
    file_paths: List[Path] = [Path(results_dir, f"{stem}.{ft}") for ft in file_types]

    downloaded = [False] * len(file_types)

    for idx, (ftype, want, path) in enumerate(zip(file_types, should_download, file_paths)):
        if not want:
            continue

        try:
            console.print(f"{ICON_DOWN} Downloading {ftype} ...")
            # include auth header if available (some deployments may require it)
            headers = None
            # Attempt to get a token if present in reporting_options or environment (non-invasive)
            # (We'll not automatically fetch tokens here to avoid unexpected logins.)
            resp = download_single_file(url, ftype, request_id, max_retries=max_retries, headers=headers)
            with open(path, "wb") as f:
                f.write(resp.content)
            downloaded[idx] = True
            console.print(f"{ICON_OK} Saved {path.name}")
        except requests.exceptions.RequestException:
            console.print(f"{ICON_WARN} Skipping {ftype} (download failed)")
            downloaded[idx] = False

    # console.print()
    # if any(downloaded):
    #     console.print(f"{ICON_OK} Files saved to: {results_dir}")
    # else:
    #     console.print(f"{ICON_WARN} No files were downloaded to: {results_dir}")
    console.print()

    return file_paths, downloaded


def open_file_cross_platform(path: Path) -> None:
    """
    Open a file using the OS default application. Safe for macOS/Windows/Linux.
    """
    try:
        p = str(path)
        system = platform.system()
        if system == "Darwin":
            subprocess.call(["open", p])
        elif system == "Windows":
            # prefer os.startfile if available (simple)
            try:
                os.startfile(p)  # type: ignore[attr-defined]
            except Exception:
                # fallback to subprocess
                subprocess.Popen([p], shell=True)
        else:
            subprocess.call(["xdg-open", p])
    except Exception as e:
        console.print(f"{ICON_ERR} Failed to open {path.name}: {get_exception_source(e)}")


def open_result_files(file_paths: List[Path], file_downloaded: List[bool]) -> None:
    """
    Open downloaded files (skips pickle) using the system viewer.
    """
    for got, path in zip(file_downloaded, file_paths):
        if not got or path.suffix == ".pickle":
            continue
        open_file_cross_platform(path)


def show_pickle_plots(
    problem: Dict, file_paths: List[Path], reporting_options: Dict, file_downloaded: List[bool]
) -> None:
    """
    If pickled matplotlib figures were downloaded, load them, display them non-blocking,
    and wait for the user to hit return before closing.
    """
    if not (
        reporting_options["save_plots_to_pickle"]
        and file_downloaded
        and file_downloaded[2]
        and "FigureHandles" in problem
    ):
        return

    show_figures_from_pickle(file_paths[2], problem)


def recorded_plot_versions(pickle_path: Path, problem: Dict | None = None) -> Dict | None:
    """
    The library versions the API used to write the pickle ("PlotVersions"): from the run's results, or for a saved run
    from the .json file next to the pickle. None for runs from before the API recorded them.
    """
    if problem and isinstance(problem.get("PlotVersions"), dict):
        return problem["PlotVersions"]
    json_path = pickle_path.with_suffix(".json")
    try:
        with open(json_path, encoding="utf-8") as f:
            versions = json.load(f).get("PlotVersions")
        return versions if isinstance(versions, dict) else None
    except (OSError, ValueError, AttributeError):
        return None


def _major_minor(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in re.findall(r"\d+", version)[:2])


def plot_version_advice(recorded: Dict | None) -> list[str]:
    """
    Instructions when the local Matplotlib or NumPy can't be expected to open the pickle. A pickle opens reliably only
    with the same Matplotlib minor version (for example 3.11.x) and, for pickles written with NumPy 2, NumPy 2.
    """
    if not recorded:
        return []
    import matplotlib

    advice = []
    mpl_saved = str(recorded.get("matplotlib", ""))
    if mpl_saved and _major_minor(mpl_saved) != _major_minor(matplotlib.__version__):
        series = ".".join(str(n) for n in _major_minor(mpl_saved))
        advice.append(
            f"These plots were saved with Matplotlib {mpl_saved}, and you have {matplotlib.__version__}. "
            f'To open them, install the same series: pip install "matplotlib=={series}.*"'
        )
    np_saved = str(recorded.get("numpy", ""))
    if np_saved and _major_minor(np_saved)[:1] != _major_minor(np.__version__)[:1]:
        major = _major_minor(np_saved)[0]
        advice.append(
            f"These plots were saved with NumPy {np_saved}, and you have {np.__version__}. "
            f'To open them, install NumPy {major}: pip install "numpy>={major},<{major + 1}"'
        )
    return advice


def show_figures_from_pickle(pickle_path: Path, problem: Dict | None = None) -> bool:
    """
    Load the matplotlib figures pickled by the API, display them non-blocking,
    and wait for the user to hit return before closing.
    Returns True if the figures were displayed.
    """
    advice = plot_version_advice(recorded_plot_versions(pickle_path, problem))
    pdf_path = pickle_path.with_suffix(".pdf")
    pdf_hint = f"The same plots are in the PDF file: {pdf_path}" if pdf_path.exists() else None
    for line in advice:
        console.print(f"{ICON_WARN} {line}")

    try:
        with open(pickle_path, "rb") as f:
            figs_to_show = pickle.load(f)
    except Exception as e:
        console.print(f"{ICON_ERR} Could not open the plots in {pickle_path.name} ({type(e).__name__}: {e}).")
        if not advice:
            console.print(
                f"{ICON_INFO} Pickled plots open only with the Matplotlib and NumPy versions they were saved with, "
                "which is normally the version Brinkpy installs. Run 'pip install --upgrade brinkpy' to get it."
            )
        if pdf_hint:
            console.print(f"{ICON_INFO} {pdf_hint}")
        return False

    # API always pickles a list of Figure objects
    if not isinstance(figs_to_show, list) or not figs_to_show:
        console.print(f"{ICON_WARN} No valid matplotlib figures found in pickle.")
        return False

    # Display all figures
    for fig in figs_to_show:
        if isinstance(fig, plt.Figure):
            plt.figure(fig.number)

    plt.show(block=False)
    try:
        input("⌨️ Hit [return] to end")
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        plt.close("all")
    return True


def load_problem_from_module(problem_file_path: Path) -> Dict | None:
    """
    Load a problem module to check for errors prior to sending to the API.
    Temporarily disables bytecode generation to avoid __pycache__.
    Returns the problem dict or None on failure.
    """
    original_flag = getattr(sys, "dont_write_bytecode", False)
    try:
        # Prevent __pycache__ creation while importing user problem modules
        sys.dont_write_bytecode = True

        module_spec = importlib.util.spec_from_file_location(problem_file_path.stem, problem_file_path)
        if module_spec is None or module_spec.loader is None:
            raise ImportError(f"Could not create module spec for {problem_file_path}")

        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)

        problem_function = getattr(module, "Problem", None) or getattr(module, "problem", None)
        if problem_function is None:
            console.print(
                f"{ICON_ERR} The problem module {problem_file_path.name} does not define a Problem() (or problem()) function.\n"
            )
            return None
        return problem_function()
    except Exception as e:
        src = get_exception_source(e, problem_file_path)
        console.print(f"{ICON_ERR} Error loading problem module {problem_file_path.name}: {src}\n")
        return None
    finally:
        sys.dont_write_bytecode = original_flag


def validate_problem_module(problem_file_path: Path, run_configuration: Dict) -> bool:
    """
    Validate that the problem is well defined.
    This is a minimal check to catch errors before sending to the API.
    """
    problem = load_problem_from_module(problem_file_path)
    if problem is None:
        return False

    if run_configuration["run_type"].lower() == "design" and "DesignProblem" not in problem:
        console.print(
            f"{ICON_ERR} Design problem missing 'DesignProblem' key. Did you mean to run command 'analyze'?"
        )
        return False

    return True


def run_app(
    run_configuration: Dict,
    reporting_options: Dict,
    rfad_plot_options: Dict,
    lsf_plot_options: Dict,
    reliability_options: Dict,
    profile_name: str = "",
    open_results: bool = False,
    problem_file_path: Path | None = None,
) -> Dict:
    """
    Post the problem module and options to the API, then download and open results.
    Returns the problem dictionary returned by the server.
    """
    # 0) Setup paths
    url, results_path, problems_path = setup_paths()

    # 1) Get token
    access_token = get_token()
    if not access_token:
        console.print(f"{ICON_ERR} Authentication failed. Please try logging in again.")
        console.print(f"{ICON_INFO} Tip: Run the {run_configuration['run_type']} command once more to trigger login.")
        raise SystemExit(1)

    # 2a) If problems directory is empty, give users option to copy examples
    if not any(problems_path.glob("*.py")):
        console.print(f"{ICON_INFO} Problems directory is empty: {problems_path}")
        if console.input(
            f"{ICON_ASK} Would you like to copy example problem files to this directory? [Y/n]: "
        ).strip().lower() in [
            "",
            "y",
            "yes",
        ]:
            copy_examples_to_working_dir(problems_path)
            console.print(f"{ICON_OK} Example problem files copied to: {problems_path}\n")
        else:
            console.print(f"{ICON_WARN} No problem files available. Please add problem .py files to: {problems_path}\n")
            console.print(f"{ICON_INFO} Exiting.")
            raise SystemExit(1)

    # 2b) Ask user for problem file
    if problem_file_path is None:
        console.print(f"{ICON_INFO} Please select a problem file from the popup menu")
        selected_file = get_problem_file_name(Path(problems_path))
        if not selected_file:
            console.print(f"{ICON_ERR} No problem file selected. Exiting.\n")
            raise SystemExit(1)
    else:
        selected_file = str(problem_file_path)

    problem_file_path = Path(selected_file)
    valid = validate_problem_module(problem_file_path, run_configuration)
    if not valid:
        console.print(f"{ICON_ERR} Cannot proceed with invalid problem module: {problem_file_path.name}")
        raise SystemExit(1)

    console.print()
    console.print(f"{ICON_OK} Successfully validated problem module: {problem_file_path.name}")

    # 3) Build options (serialized)
    options_payload = {
        "run_configuration": run_configuration,
        "reporting_options": reporting_options,
        "rfad_plot_options": rfad_plot_options,
        "lsf_plot_options": lsf_plot_options,
        "reliability_options": reliability_options,
    }
    options = {"options": json.dumps(serialize_obj(options_payload))}

    # 4) POST to /run_app
    headers = {"Authorization": f"Bearer {access_token}"}
    post_resp = None
    try:
        with console.status(f"[bold green]Processing {problem_file_path.name}..."):
            with open(problem_file_path, "rb") as file_obj:
                files = {"file": file_obj}
                post_resp = requests.post(f"{url.rstrip('/')}/run_app", files=files, data=options, headers=headers)
                post_resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        # Distinguish between HTTP responses vs. network-level failures
        if post_resp is not None:
            if post_resp.status_code == 429:
                handle_rate_limit_error(post_resp)
            elif post_resp.status_code == 403:
                from brinkpy.utils.billing_cli import handle_run_refused  # imported here: billing_cli imports this module

                if not handle_run_refused(post_resp):
                    handle_other_http_errors(post_resp, "App request failed")
            else:
                handle_other_http_errors(post_resp, "App request failed")
        else:
            # Network-level error: connection refused, DNS failure, timeouts, etc.
            # Provide clearer guidance when the API host is unreachable.
            down_msg_printed = False
            try:
                # requests wraps underlying exceptions; check for ConnectionError/Timeout
                if isinstance(e, requests.exceptions.ConnectionError):
                    down_msg_printed = True
                    console.print(
                        f"{ICON_ERR} Unable to reach the API host (connection refused). The service may be temporarily unavailable.",
                        style="red",
                    )
                    console.print(
                        f"{ICON_INFO} Checked URL: {url}. Please try again later or contact support if the issue persists.",
                        style="blue",
                    )
                elif isinstance(e, requests.exceptions.Timeout):
                    down_msg_printed = True
                    console.print(
                        f"{ICON_ERR} API request timed out. The service may be temporarily unavailable or unreachable.",
                        style="red",
                    )
                    console.print(
                        f"{ICON_INFO} Checked URL: {url}. Please try again later or contact support.",
                        style="blue",
                    )
                else:
                    # Inspect the underlying error (e.g., OSError with errno ECONNREFUSED / 61)
                    cause = getattr(e, "__cause__", None) or getattr(e, "__context__", None)
                    if isinstance(cause, OSError) and getattr(cause, "errno", None) in {61, 111}:
                        # 61: macOS ECONNREFUSED, 111: Linux ECONNREFUSED
                        down_msg_printed = True
                        console.print(
                            f"{ICON_ERR} Connection refused when contacting the API. The service appears unavailable.",
                            style="red",
                        )
                        console.print(
                            f"{ICON_INFO} Checked URL: {url}. Please try again later or contact support.",
                            style="blue",
                        )
            except Exception:
                # Fall through to generic message
                pass

            if not down_msg_printed:
                console.print(f"{ICON_ERR} App request failed: {e}\n")
        sys.exit(1)

    # 5) Parse response
    problem_json = post_resp.json()
    request_id = problem_json.get("Request_ID", "unknown")
    console.print(
        f"{ICON_OK} {str(run_configuration['run_type']).capitalize()} run completed for problem: {problem_json.get('name')} with Request ID: {request_id}\n"
    )

    # 6) Print Info messages (if any) # Currently disabled to reduce console clutter
    # info_list = problem_json.get("Info", [])
    # if info_list:
    #     prefix = "\u2022 "
    #     wrapper = textwrap.TextWrapper(initial_indent=prefix, width=130, subsequent_indent=" " * len(prefix))
    #     console.print(f"{ICON_INFO} Messages:")
    #     for m in info_list:
    #         console.print(wrapper.fill(str(m)))
    # else:
    #     console.print(f"{ICON_INFO} Messages: None\n")
    # console.print()

    # 7) Create timestamped directory for this run
    timestamped_dir = get_timestamped_results_dir(results_path)
    rel_path = timestamped_dir.relative_to(results_path.parent)
    file_uri = timestamped_dir.as_uri()
    console.print(
        f"{ICON_OK} Result files, a copy of the problem file, and the profile will be saved to: [link={file_uri}]{rel_path}[/link]\n"
    )

    # 8) Save server returned problem to timestamped directory as JSON
    stem = result_file_stem(problem_json)
    out_json_path = Path(timestamped_dir, f"{stem}.json")
    try:
        safe_write_json(problem_json, out_json_path, indent=4)
        console.print(f"{ICON_OK} Saved problem JSON: {out_json_path.name}")
    except Exception as e:
        console.print(f"{ICON_WARN} Failed saving problem JSON to {out_json_path}: {e}")

    # 10) Download files to the timestamped directory
    file_paths, file_downloaded = download_results(url, problem_json, timestamped_dir, reporting_options, max_retries=3)

    # 11) Optional: Clean up old results (keeping last 30 days by default)
    # Uncomment the line below to enable automatic cleanup
    # cleanup_old_results(results_path, days=30)

    # 12) Save a copy of the problem .py file to the results directory for reference
    try:
        problem_py_copy_path = Path(timestamped_dir, f"{stem}.py")
        shutil.copy2(problem_file_path, problem_py_copy_path)
        console.print(f"{ICON_OK} Copied problem file to results: {problem_py_copy_path.name}")
    except Exception as e:
        console.print(f"{ICON_WARN} Failed copying problem .py file to results directory: {e}")

    # 13) Save profile to results directory
    profile_data = OrderedDict(
        {
            "name": profile_name,
            "description": f"Configuration profile for '{problem_json.get('name', problem_file_path.stem)}' run",
            "run_configuration": run_configuration,
            "reliability_options": reliability_options,
            "lsf_plot_options": lsf_plot_options,
            "rfad_plot_options": rfad_plot_options,
            "reporting_options": reporting_options,
        }
    )
    profile_path = Path(timestamped_dir, f"profile-{request_id[-5:]}.yaml")
    save_result_yaml_profile(profile_path, profile_data)
    console.print(f"{ICON_OK} Saved configuration profile: {profile_path.name}")

    # 14) Open files and show pickles
    if open_results:
        open_result_files(file_paths, file_downloaded)
        show_pickle_plots(problem_json, file_paths, reporting_options, file_downloaded)
    else:
        console.print()
        console.print(
            f"{ICON_INFO} Results are ready in: [link={file_uri}]{rel_path}[/link]. Use --open-results or -o to open them automatically when running the command.\n"
        )

    return problem_json


def get_problem_file_name(problems_path: Path) -> Path | None:
    """
    Prompt the user to select a problem file.
    Returns the Path or None.
    """
    # Preselect the most recently modified .py file
    py_files = [p for p in problems_path.glob("*.py") if p.is_file()]
    latest_py_file = max(py_files, default=None, key=lambda p: p.stat().st_mtime) if py_files else None

    selected_file = filedialpy.openFile(
        initial_dir=str(problems_path),
        filter="*.py",
        title="Select a problem file",
        initial_file=str(latest_py_file) if latest_py_file else "",
    )
    if selected_file is not None and Path(selected_file).is_file():
        return Path(selected_file)
    return None


def get_pickle_file_name(results_path: Path) -> Path | None:
    """
    Prompt the user to select a pickle file of saved plots.
    Returns the Path or None.
    """
    # Preselect the most recently modified .pickle file in any run folder
    pickle_files = [p for p in results_path.rglob("*.pickle") if p.is_file()]
    latest_pickle_file = max(pickle_files, default=None, key=lambda p: p.stat().st_mtime)

    selected_file = filedialpy.openFile(
        initial_dir=str(latest_pickle_file.parent if latest_pickle_file else results_path),
        filter="*.pickle",
        title="Select a plots file",
        initial_file=str(latest_pickle_file) if latest_pickle_file else "",
    )
    if selected_file is not None and Path(selected_file).is_file():
        return Path(selected_file)
    return None


def get_problem_file_name_tk(problems_path: Path) -> Path | None:
    """
    Prompt the user to select a problem file using tkinter's native file dialog.
    Returns the Path or None.

    Notes:
    - Uses `initialdir` and `initialfile` to preselect the most recently modified .py.
    - Works on macOS/Windows/Linux with a GUI environment.
    - Falls back to None if tkinter is unavailable or the dialog is cancelled.
    """
    try:
        # Lazy imports to avoid requiring Tk in headless contexts
        import tkinter as tk
        from tkinter import filedialog
    except Exception:
        return None

    # Determine a reasonable preselection: most recently modified .py file
    py_files = [p for p in problems_path.glob("*.py") if p.is_file()]
    latest_py_file = max(py_files, default=None, key=lambda p: p.stat().st_mtime) if py_files else None

    # Create a temporary root (hidden) for the dialog
    root = tk.Tk()
    try:
        root.withdraw()
        # Some platforms behave better if the window is lifted
        root.update_idletasks()

        selected = filedialog.askopenfilename(
            initialdir=str(problems_path),
            initialfile=latest_py_file.name if latest_py_file else "",
            title="Select a problem file",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")],
        )
    finally:
        # Ensure Tk resources are cleaned up
        try:
            root.destroy()
        except Exception:
            pass

    if selected:
        p = Path(selected)
        if p.is_file():
            return p
    return None


# api_utils.py

# api_utils.py

# api_utils.py
