from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GitHubConfig:
    username: str
    include_forks_with_stars: bool
    minimum_fork_stars: int


@dataclass(frozen=True)
class Config:
    title: str
    description: str
    github: GitHubConfig


def load_config(path: Path) -> Config:
    raw = json.loads(path.read_text(encoding="utf-8"))
    github = raw.get("github", {})

    username = (
        _env("GITHUB_USERNAME")
        or github.get("username")
        or _env("GITHUB_REPOSITORY_OWNER")
        or ""
    )

    return Config(
        title=_env("SITE_TITLE") or raw.get("title") or "Repository Catalogue",
        description=_env("SITE_DESCRIPTION")
        or raw.get("description")
        or "An automatically generated list of my public code repositories.",
        github=GitHubConfig(
            username=username,
            include_forks_with_stars=github.get("includeForksWithStars", True),
            minimum_fork_stars=int(github.get("minimumForkStars", 1)),
        ),
    )


def _env(name: str) -> str:
    return os.environ.get(name, "").strip()
