# fetch_cache_web.py

[`fetch_cache_web.py`](fetch_cache_web/scripts/fetch_cache_web.py) fetch web content into a named local cache for multiple reuse. Convert HTML to Markdown by default, refresh expired entries, and maintain a JSON manifest.

## Usage

Fetch and name a page:

```sh
uv run fetch_cache_web.py get https://example.com/guide.html --name guide
```

`get` prints only the cached file path. Reuse the stored URL by name:

```sh
uv run fetch_cache_web.py get guide
```

Inspect the full manifest or one entry:

```sh
uv run fetch_cache_web.py show
uv run fetch_cache_web.py show guide
```

Use `--refetch` to bypass a fresh entry, `--expiry-days N` to change the 30-day freshness window, `--skip-markdownify` to skip HTML-to-Markdown conversion, and `--cache-dir DIR` to select another cache folder. Run `uv run fetch_cache_web.py get --help` or `uv run fetch_cache_web.py show --help` for the complete manual.

Each cache directory contains fetched files and `manifest.json`. The manifest records every entry's name, URL, local path, and fetch time.

## Dependencies

- [Python 3.12 or later](https://docs.python.org/3.12/)
- [uv](https://docs.astral.sh/uv/)
- [markdownify](https://github.com/matthewwithanm/python-markdownify) `1.2.3` or later

The script contains PEP 723 metadata, so `uv run` can resolve its dependency without a separate installation step.

## Agentic Skill

The self-contained [`fetch_cache_web` skill](./fetch_cache_web/) can be installed as an Agentic Skill to teach compatible agents how to efficiently fetch frequently used web resources, manage named web content caches, and bundle the script into other skills.
