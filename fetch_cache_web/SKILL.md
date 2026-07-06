---
name: fetch_cache_web
description: Fetches web URLs and caches them locally as files with a manifest inventory, friendly names, expiry, and optional HTML-to-Markdown conversion. Use when fetching reference URLs that will be re-read across runs, caching official docs or guidance locally, checking what is already cached via the manifest, converting fetched HTML pages to Markdown, or creating or updating an agentic skill that frequently fetches upstream web content and should bundle this capability.
---

# fetch_cache_web

A single PEP 723 script, `scripts/fetch_cache_web.py`, run from this skill directory with uv (no install step):

```sh
uv run scripts/fetch_cache_web.py get <url> --name <name>
```

That fetches the URL, converts HTML to Markdown, caches it under the friendly name, and prints the cached file path. The printed path is the whole output, designed for piping straight into a read step.

On later runs, the name alone reuses the cache (and its stored URL):

```sh
uv run scripts/fetch_cache_web.py get <name>
```

## Usage notes

- `show` prints the manifest inventory as JSON; `show <name-or-url>` prints one entry, `{}` if uncached. Check it before fetching to see what is already local.
- Entries are fresh for 30 days by default; tune with `--expiry-days`, or force a fresh fetch with `--refetch`.
- `--skip-markdownify` keeps the fetched content raw instead of converting HTML to Markdown. Content already in Markdown is never converted.
- `--cache-dir DIR` keeps a per-project or per-skill cache; default is `.cache` next to the script. Pass the same value to every `get` and `show` that should share a cache.

`uv run scripts/fetch_cache_web.py get --help` and `... show --help` are the authoritative flag reference.

## Bundle into another skill

When creating or updating an agentic skill that frequently fetches upstream web content, copy `scripts/fetch_cache_web.py` into that skill's `scripts/` directory. Keep the copied script self-contained and unchanged so the target skill remains independent after installation.

In the target `SKILL.md`, tell the agent which source URLs or manifest names to fetch, run the local copy as `uv run scripts/fetch_cache_web.py`, and reuse named cache entries within a run. Add `.cache/` to the target skill's `.gitignore`; do not commit fetched content unless it is intentionally maintained as a static reference.
