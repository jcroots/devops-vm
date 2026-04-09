#!/usr/bin/env python3
"""
upgrade.py - Check and update hardcoded software versions in installation scripts.

Targets:
  - Cloud SQL Proxy  -> gcloud/sql-proxy-install.sh
  - Debian forky slim -> docker/Dockerfile

Usage:
  python3 upgrade.py            # check and update
  python3 upgrade.py --dry-run  # check only, no file changes
"""

import json
import re
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

WORKSPACE = Path(__file__).parent

CSP_SCRIPT      = WORKSPACE / "gcloud/sql-proxy-install.sh"
DOCKER_DOCKERFILE = WORKSPACE / "docker/Dockerfile"


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def fetch_json(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} fetching {url}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error fetching {url}: {e.reason}") from e


# ---------------------------------------------------------------------------
# Version fetchers
# ---------------------------------------------------------------------------

def get_latest_cloud_sql_proxy():
    data = fetch_json(
        "https://api.github.com/repos/GoogleCloudPlatform/cloud-sql-proxy/releases/latest",
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    tag = data["tag_name"]  # e.g. "v2.15.0"
    return tag.lstrip("v")


def get_latest_debian_forky_slim():
    """Return the latest forky-YYYYMMDD-slim tag from Docker Hub."""
    url = (
        "https://hub.docker.com/v2/repositories/library/debian/tags"
        "?name=forky-&ordering=last_updated&page_size=100"
    )
    data = fetch_json(url)
    pattern = re.compile(r"^forky-(\d{8})-slim$")
    candidates = []
    for result in data.get("results", []):
        m = pattern.match(result["name"])
        if m:
            candidates.append((m.group(1), result["name"]))  # (date_str, full_tag)
    if not candidates:
        raise RuntimeError("No forky-YYYYMMDD-slim tags found on Docker Hub")
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]  # e.g. "forky-20260223-slim"


# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------

def read_current(path, pattern):
    """Extract current value using a regex with one capture group."""
    content = path.read_text()
    m = re.search(pattern, content)
    if not m:
        raise RuntimeError(f"Pattern {pattern!r} not found in {path}")
    return m.group(1)


def update_file(path, pattern, replacement, dry_run=False):
    """Replace first regex match in file. Returns True if content would change."""
    content = path.read_text()
    new_content, count = re.subn(pattern, replacement, content, count=1)
    if count == 0:
        raise RuntimeError(f"Pattern {pattern!r} not found in {path}")
    if new_content == content:
        return False
    if not dry_run:
        path.write_text(new_content)
    return True


# ---------------------------------------------------------------------------
# Per-tool check + update logic
# ---------------------------------------------------------------------------

def check(name, current, latest, path, search_pattern, replacement, dry_run):
    if current == latest:
        print(f"  ok        {current}")
        return False
    print(f"  outdated  {current} -> {latest}")
    changed = update_file(path, search_pattern, replacement, dry_run)
    if changed and not dry_run:
        print(f"  updated   {path.relative_to(WORKSPACE)}")
    elif changed and dry_run:
        print(f"  would update {path.relative_to(WORKSPACE)}")
    return changed


def run_cloud_sql_proxy(dry_run):
    print("[cloud-sql-proxy]")
    current = read_current(CSP_SCRIPT, r"CSP_VERSION='([^']+)'")
    latest  = get_latest_cloud_sql_proxy()
    return check(
        "cloud-sql-proxy", current, latest,
        CSP_SCRIPT,
        r"CSP_VERSION='[^']+'",
        f"CSP_VERSION='{latest}'",
        dry_run,
    )


def run_debian_forky(dry_run):
    print("[debian forky slim]")
    current = read_current(DOCKER_DOCKERFILE, r"FROM debian:(\S+)")
    latest  = get_latest_debian_forky_slim()
    return check(
        "debian", current, latest,
        DOCKER_DOCKERFILE,
        r"FROM debian:\S+",
        f"FROM debian:{latest}",
        dry_run,
    )


# ---------------------------------------------------------------------------
# Dockerfile timestamp stamping
# ---------------------------------------------------------------------------

def stamp_dockerfile(dry_run):
    """Update version label and JCROOTS_UPGRADE env in Dockerfile with current YYMMDD."""
    stamp = date.today().strftime("%y%m%d")
    print(f"[dockerfile stamp]")
    content = DOCKER_DOCKERFILE.read_text()
    new_content = re.sub(r'LABEL version="[^"]*"', f'LABEL version="{stamp}"', content)
    new_content = re.sub(r'ENV JCROOTS_UPGRADE=\S+', f'ENV JCROOTS_UPGRADE={stamp}', new_content)
    if new_content == content:
        print(f"  ok        {stamp}")
        return
    if dry_run:
        print(f"  would stamp {DOCKER_DOCKERFILE.relative_to(WORKSPACE)} -> {stamp}")
    else:
        DOCKER_DOCKERFILE.write_text(new_content)
        print(f"  stamped   {DOCKER_DOCKERFILE.relative_to(WORKSPACE)} -> {stamp}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

CHECKS = [
    run_cloud_sql_proxy,
    run_debian_forky,
]


def main():
    dry_run = "--dry-run" in sys.argv
    if dry_run:
        print("=== DRY-run mode: no files will be modified ===\n")

    dockerfile_before = DOCKER_DOCKERFILE.read_text()

    any_updated = False
    any_error   = False

    for fn in CHECKS:
        try:
            updated = fn(dry_run)
            any_updated = any_updated or updated
        except Exception as e:
            print(f"  ERROR: {e}")
            any_error = True
        print()

    dockerfile_changed = DOCKER_DOCKERFILE.read_text() != dockerfile_before
    if dockerfile_changed:
        stamp_dockerfile(dry_run)
        print()

    if any_error:
        print("Finished with errors.")
        sys.exit(1)
    elif any_updated and dry_run:
        print("Updates available (dry-run, no files changed).")
    elif any_updated:
        print("All updates applied.")
    else:
        print("Everything is up to date.")


if __name__ == "__main__":
    main()
