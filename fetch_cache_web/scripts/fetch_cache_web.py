#!/usr/bin/env -S uv run -s
# /// script
# requires-python = ">=3.12"
# dependencies = ["markdownify>=1.2.3"]
# ///
"""
Fetch a URL, convert HTML to Markdown, cache the result, and fetch from cache until expiry.

Usage:
  fetch_cache_web.py get <url-or-name> [--name NAME] [--cache-dir DIR] [--expiry-days N] [--refetch] [--skip-markdownify]
  fetch_cache_web.py show [<url-or-name>] [--name NAME] [--cache-dir DIR]

Without --name, the positional argument is tried as a cache name first, if not found, tries as a URL.
`--name` skips the URL lookup.

`get` prints the cached file path. `show` with no args prints the whole
manifest; with a target/--name, prints that entry or `{}` if uncached.
"""
import argparse
import hashlib
import json
import sys
import time
import urllib.request
from pathlib import Path

from markdownify import markdownify

DEFAULT_CACHE_DIR = Path(__file__).resolve().parent / ".cache"
DEFAULT_EXPIRY_DAYS = 30


def process_content(url, raw, content_type, skip_markdownify):
    if skip_markdownify or url.lower().endswith(".md") or "markdown" in (content_type or "").lower():
        return raw
    return markdownify(raw, heading_style="ATX")


class WebCache:
    def __init__(self, cache_dir):
        self.directory = cache_dir
        self.manifest_file = cache_dir / "manifest.json"
        self.manifest = json.loads(self.manifest_file.read_text()) if self.manifest_file.exists() else {}

    def resolve(self, target, name):
        if name:
            return name, target
        if target in self.manifest:
            return target, self.manifest[target]["url"]
        return None, target

    def get(self, args):
        self.directory.mkdir(parents=True, exist_ok=True)
        resolved_name, url = self.resolve(args.target, args.name)
        name = resolved_name or hashlib.sha256(url.encode()).hexdigest()[:16]
        cache_path = self.directory / f"{name}.md"
        entry = self.manifest.get(name)
        fresh = entry and cache_path.exists() and time.time() - entry["fetched_at"] < args.expiry_days * 86400
        if not args.refetch and fresh:
            print(cache_path)
            return

        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                raw = response.read().decode("utf-8", errors="replace")
                content_type = response.headers.get("Content-Type", "")
        except Exception as error:
            sys.exit(f"Fetch failed for {url}: {error}")

        cache_path.write_text(process_content(url, raw, content_type, args.skip_markdownify))
        self.manifest[name] = {"url": url, "file": str(cache_path.resolve()), "fetched_at": time.time()}
        self.manifest_file.write_text(json.dumps(self.manifest, indent=2, sort_keys=True))
        print(cache_path)

    def show(self, args):
        if not args.target and not args.name:
            entry = self.manifest
        else:
            name, url = self.resolve(args.target, args.name)
            entry = (
                self.manifest.get(name, {})
                if name
                else next((item for item in self.manifest.values() if item.get("url") == url), {})
            )
        print(json.dumps(entry, indent=2, sort_keys=True))


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest="verb", required=True)

    get_parser = subparsers.add_parser("get", help="Fetch (or reuse cached) URL, print the cached file path")
    get_parser.add_argument("target", help="Cache name or URL to fetch")
    get_parser.add_argument("--name", help="Friendly name for the cache entry (default: derived from the URL)")
    get_parser.add_argument(
        "--cache-dir",
        type=Path,
        default=DEFAULT_CACHE_DIR,
        help="Cache directory (default: .cache next to this script)",
    )
    get_parser.add_argument("--refetch", action="store_true", help="Ignore cache and fetch fresh")
    get_parser.add_argument(
        "--expiry-days",
        type=float,
        default=DEFAULT_EXPIRY_DAYS,
        help=f"Cache freshness window in days (default {DEFAULT_EXPIRY_DAYS})",
    )
    get_parser.add_argument(
        "--skip-markdownify",
        action="store_true",
        help="Never convert the fetched content to Markdown, even if it looks like HTML",
    )

    show_parser = subparsers.add_parser("show", help="Print the manifest, or a single cached entry")
    show_parser.add_argument("target", nargs="?", help="Cache name or URL to look up")
    show_parser.add_argument("--name", help="Cache entry name to look up directly")
    show_parser.add_argument(
        "--cache-dir",
        type=Path,
        default=DEFAULT_CACHE_DIR,
        help="Cache directory (default: .cache next to this script)",
    )
    return parser


def main():
    args = build_parser().parse_args()
    cache = WebCache(args.cache_dir)
    if args.verb == "get":
        cache.get(args)
    else:
        cache.show(args)


if __name__ == "__main__":
    main()
