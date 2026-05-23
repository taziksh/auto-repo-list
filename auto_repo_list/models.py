from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Repo:
    provider: str
    name: str
    full_name: str
    description: str
    has_description: bool
    url: str
    homepage: str
    language: str
    stars: int
    forks: int
    topics: list[str] = field(default_factory=list)
    updated_at: str = ""
    pushed_at: str = ""
    is_fork: bool = False
    archived: bool = False
    disabled: bool = False
