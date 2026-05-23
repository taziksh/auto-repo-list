from __future__ import annotations

import json
import os
import re
from typing import Any
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

from auto_repo_list.config import GitHubConfig
from auto_repo_list.models import Repo

API_ROOT = "https://api.github.com"


def fetch_github_repos(config: GitHubConfig) -> list[Repo]:
    username = config.username.strip()

    if not username:
        raise RuntimeError(
            "No GitHub username configured. Set github.username in "
            "repo-list.config.json or GITHUB_USERNAME."
        )

    url = f"{API_ROOT}/users/{quote(username)}/repos?per_page=100&type=owner&sort=updated"
    repos = [_normalize_repo(repo) for repo in _fetch_all_pages(url)]
    return repos


def _fetch_all_pages(first_url: str) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    url = first_url

    while url:
        response_body, link_header = _fetch_json(url)
        results.extend(response_body)
        url = _next_page_url(link_header)

    return results


def _fetch_json(url: str) -> tuple[list[dict[str, Any]], str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = Request(url, headers=headers)

    try:
        with urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8")
            link_header = response.headers.get("Link", "")
    except HTTPError as error:
        body = error.read().decode("utf-8")
        raise RuntimeError(
            f"GitHub request failed ({error.code} {error.reason}): {body}"
        ) from error

    data = json.loads(body)
    if not isinstance(data, list):
        raise RuntimeError(f"Expected a list from GitHub, got {type(data).__name__}.")

    return data, link_header


def _normalize_repo(repo: dict[str, Any]) -> Repo:
    description = repo.get("description")
    return Repo(
        provider="github",
        name=repo["name"],
        full_name=repo["full_name"],
        description=description or "No description provided.",
        has_description=bool(description),
        url=repo["html_url"],
        homepage=_normalize_homepage(repo.get("homepage") or ""),
        language=repo.get("language") or "",
        stars=repo["stargazers_count"],
        forks=repo["forks_count"],
        topics=repo.get("topics") or [],
        updated_at=repo.get("updated_at") or "",
        pushed_at=repo.get("pushed_at") or "",
        is_fork=repo["fork"],
        archived=repo["archived"],
        disabled=repo.get("disabled", False),
    )


def _normalize_homepage(homepage: str) -> str:
    if not homepage:
        return ""
    if re.match(r"^https?://", homepage, flags=re.IGNORECASE):
        return homepage
    return f"https://{homepage}"


def _next_page_url(link_header: str) -> str:
    for part in link_header.split(","):
        match = re.search(r'<([^>]+)>;\s*rel="([^"]+)"', part)
        if match and match.group(2) == "next":
            return match.group(1)
    return ""
