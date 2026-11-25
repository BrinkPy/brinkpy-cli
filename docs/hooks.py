from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

try:
    import tomllib
except Exception:  # pragma: no cover
    tomllib = None


def on_config(config):
    """Set header repo label to PyPI v<version> from pyproject.toml."""
    if tomllib is None:
        return config

    try:
        root = Path(config.config_file_path).resolve().parent
        pyproject_path = root / "pyproject.toml"
        with pyproject_path.open("rb") as f:
            data = tomllib.load(f)
        version = data["project"]["version"]
        config["repo_name"] = f"GitHub v{version}"
    except Exception:
        # Keep configured fallback when version cannot be read.
        pass

    return config


# An <a> tag with an absolute http(s) link and no target attribute yet
EXTERNAL_LINK = re.compile(r'<a\s(?![^>]*\btarget=)([^>]*\bhref="(https?://[^"]+)"[^>]*)>')


def on_page_content(html, page, config, files):
    """Open links to other sites in a new tab, so the docs stay open next to a reference.

    Links within the docs keep opening in the same tab. rel="noopener" keeps the opened page from controlling
    this one.
    """
    site_host = urlparse(str(config.get("site_url", ""))).hostname

    def add_target(match: re.Match) -> str:
        attributes, url = match.group(1), match.group(2)
        if urlparse(url).hostname == site_host:
            return match.group(0)
        return f'<a {attributes} target="_blank" rel="noopener">'

    return EXTERNAL_LINK.sub(add_target, html)


def on_post_build(config, **kwargs):
    """Write robots.txt with the sitemap URL for the active site_url."""
    site_url = str(config.get("site_url", "")).rstrip("/")
    if not site_url:
        return

    robots_path = Path(config["site_dir"]) / "robots.txt"
    robots_path.write_text(
        "User-agent: *\n" "Allow: /\n\n" f"Sitemap: {site_url}/sitemap.xml\n",
        encoding="utf-8",
    )
