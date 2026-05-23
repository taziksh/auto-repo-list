from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from .config import load_config
from .providers.github import fetch_github_repos
from .render import render_docs, render_markdown


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a repository catalogue.")
    parser.add_argument(
        "command",
        choices=["build"],
        nargs="?",
        default="build",
        help="Command to run.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root. Defaults to the current directory.",
    )
    args = parser.parse_args()

    if args.command == "build":
        build(args.root)


def build(root: Path) -> None:
    config = load_config(root / "repo-list.config.json")
    repos = fetch_github_repos(config.github)
    generated_at = datetime.now().astimezone()

    (root / "README.md").write_text(
        render_markdown(config, repos, generated_at),
        encoding="utf-8",
    )
    (root / "DOCS.md").write_text(render_docs(), encoding="utf-8")

    print(f"Generated {len(repos)} repositories for {config.github.username}.")
