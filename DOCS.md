# Setup

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
