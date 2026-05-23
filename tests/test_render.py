from __future__ import annotations

import unittest
from datetime import datetime, timezone

from auto_repo_list.config import Config, GitHubConfig
from auto_repo_list.models import Repo
from auto_repo_list.render import render_markdown


class RenderMarkdownTests(unittest.TestCase):
    def test_repos_sort_by_stars_readme_presence_then_date(self) -> None:
        repos = [
            _repo(
                "older-with-readme",
                stars=1,
                has_readme=True,
                has_description=True,
                pushed_at="2024-01-01T00:00:00Z",
            ),
            _repo(
                "newer-without-readme",
                stars=1,
                has_readme=False,
                has_description=False,
                pushed_at="2026-01-01T00:00:00Z",
            ),
            _repo(
                "newer-with-readme",
                stars=1,
                has_readme=True,
                has_description=False,
                pushed_at="2026-01-01T00:00:00Z",
            ),
            _repo(
                "more-stars",
                stars=2,
                has_readme=False,
                has_description=False,
                pushed_at="2020-01-01T00:00:00Z",
            ),
        ]

        markdown = render_markdown(
            _config(), repos, datetime(2026, 5, 23, tzinfo=timezone.utc)
        )

        self.assertLess(markdown.index("more-stars"), markdown.index("newer-with-readme"))
        self.assertLess(
            markdown.index("newer-with-readme"), markdown.index("older-with-readme")
        )
        self.assertLess(
            markdown.index("older-with-readme"), markdown.index("newer-without-readme")
        )

    def test_description_presence_does_not_affect_order(self) -> None:
        repos = [
            _repo(
                "newer-without-description",
                stars=1,
                has_readme=False,
                has_description=False,
                pushed_at="2026-01-01T00:00:00Z",
            ),
            _repo(
                "older-with-description",
                stars=1,
                has_readme=False,
                has_description=True,
                pushed_at="2025-01-01T00:00:00Z",
            ),
        ]

        markdown = render_markdown(
            _config(), repos, datetime(2026, 5, 23, tzinfo=timezone.utc)
        )

        self.assertLess(
            markdown.index("newer-without-description"),
            markdown.index("older-with-description"),
        )


def _repo(
    name: str,
    *,
    stars: int,
    has_readme: bool,
    has_description: bool,
    pushed_at: str,
) -> Repo:
    return Repo(
        provider="github",
        name=name,
        full_name=f"taziksh/{name}",
        description="Description" if has_description else "No description provided.",
        has_description=has_description,
        has_readme=has_readme,
        url=f"https://github.com/taziksh/{name}",
        homepage="",
        language="Python",
        stars=stars,
        forks=0,
        pushed_at=pushed_at,
    )


def _config() -> Config:
    return Config(
        title="Test Catalogue",
        description="Test description.",
        github=GitHubConfig(
            username="taziksh",
            include_forks_with_stars=True,
            minimum_fork_stars=1,
        ),
    )


if __name__ == "__main__":
    unittest.main()
