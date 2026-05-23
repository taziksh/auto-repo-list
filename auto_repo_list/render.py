from __future__ import annotations

from datetime import datetime

from .config import Config
from .models import Repo


def render_markdown(config: Config, repos: list[Repo], generated_at: datetime) -> str:
    projects, archived = _group_repos(repos, config)
    lines = [
        f"# {config.title}",
        "",
        config.description,
        "",
        "Generated "
        f"{_format_date(generated_at)} from GitHub user "
        f"[{config.github.username}](https://github.com/{config.github.username}).",
        "",
        "Inspired by "
        "[tristan-f-r/tristan-f-r.github.io]"
        "(https://github.com/tristan-f-r/tristan-f-r.github.io).",
        "",
        f"## Projects ({len(projects)})",
        "",
    ]

    if config.github.include_forks_with_stars:
        lines.extend(
            [
                "> Forks with "
                f"{config.github.minimum_fork_stars}+ star are included; "
                "other forks are hidden.",
                "",
            ]
        )

    lines.append(_render_repo_list(projects, show_stars=True))
    lines.extend(
        [
            f"## Archived ({len(archived)})",
            "",
            "> Archived repositories are listed separately.",
            "",
        ]
    )
    lines.append(_render_repo_list(archived, show_stars=True))
    lines.extend(
        [
            "",
            "## Setup",
            "",
            "See [DOCS.md](DOCS.md) for setup and customization notes.",
            "",
        ]
    )
    return "\n".join(lines)


def render_docs() -> str:
    return """# Setup

This repository generates a public catalogue of GitHub repositories.

The simple catalogue format is inspired by [tristan-f-r/tristan-f-r.github.io](https://github.com/tristan-f-r/tristan-f-r.github.io).

## Configure

Edit `repo-list.config.json`.

- `title` and `description` control the page heading.
- `github.username` can be left blank on GitHub Actions; it defaults to the repository owner.
- `github.includeForksWithStars` includes notable forks and hides the rest.
- `github.minimumForkStars` controls the fork threshold.

For local builds, run:

```sh
uv run python -m auto_repo_list build
```

## Publish

1. Push this repo to GitHub.
2. In the repository settings, enable GitHub Pages from the `main` branch root.
3. The included workflow refreshes `README.md` daily and on manual runs.

## Private Repositories

The default workflow lists public repositories. To include private repositories later, swap the provider to use the authenticated `/user/repos` endpoint and provide a token with metadata read access.

## Later Providers

The scanner is intentionally provider-shaped. Add future providers under `auto_repo_list/providers/`, normalize them to the same repository shape, and merge their results before rendering.
"""


def _group_repos(repos: list[Repo], config: Config) -> tuple[list[Repo], list[Repo]]:
    archived = sorted((repo for repo in repos if repo.archived), key=_repo_sort_key)
    projects = sorted(
        (
            repo
            for repo in repos
            if not repo.archived
            and (
                not repo.is_fork
                or (
                    config.github.include_forks_with_stars
                    and repo.stars >= config.github.minimum_fork_stars
                )
            )
        ),
        key=_repo_sort_key,
    )

    return projects, archived


def _repo_sort_key(repo: Repo) -> tuple[int, int, float, str]:
    return (
        -repo.stars,
        int(not repo.has_readme),
        -_repo_sort_timestamp(repo),
        repo.name.lower(),
    )


def _repo_sort_timestamp(repo: Repo) -> float:
    date = repo.pushed_at or repo.updated_at
    if not date:
        return 0

    return datetime.fromisoformat(date.replace("Z", "+00:00")).timestamp()


def _render_repo_list(repos: list[Repo], show_stars: bool) -> str:
    if not repos:
        return "_None yet._\n"

    lines = []
    for repo in repos:
        header = f"{repo.name} ({repo.stars})" if show_stars else repo.name
        homepage = f" ([homepage]({repo.homepage}))" if repo.homepage else ""
        language = f" - {repo.language}" if repo.language else ""
        lines.append(f"- [{header}]({repo.url}){homepage} - {repo.description}{language}")

    return "\n".join(lines) + "\n"


def _format_date(value: datetime) -> str:
    return value.strftime("%b %-d, %Y, %-I:%M %p %Z")
