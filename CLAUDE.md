# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

Provisioning and configuration scripts for a shared development VM. Scripts are deployed to `/opt/jcroots/devops-vm` on target machines via `setup.sh`, which downloads a GitHub release tarball.

## Commands

- **Lint and check:** `make check` (runs shellcheck on all `.sh` files and py_compile on `upgrade.py`)
- **Build Docker image:** `make docker` (calls `docker/build.sh`, tags as `jcroots/devops-vm`)
- **Check for version updates:** `python3 upgrade.py --dry-run` (or without `--dry-run` to apply)

## Architecture

- **`setup.sh`** — Bootstrap script. Takes a GitHub ref (tag/branch), downloads the tarball, and extracts to `/opt/jcroots/devops-vm` on the target host.
- **`upgrade.py`** — Automated version checker. Queries GitHub API (Cloud SQL Proxy) and Docker Hub (Debian base image) for latest versions, then updates the pinned values in `gcloud/sql-proxy-install.sh` and `docker/Dockerfile`. Add new version checks by appending to the `CHECKS` list.
- **`docker/`** — Debian-based dev container. `build.sh` builds with the current user's UID/GID. `devel.sh` runs an interactive shell with `$PWD` mounted. The container runs as a non-root user with sudo access.
- **`gcloud/`** — GCP service installation scripts. `sql-proxy-install.sh` downloads a pinned Cloud SQL Proxy version. `sql-proxy/` contains the systemd unit and wrapper script that reads connection config from `/usr/local/etc/deploy-vm.environment`. `ops-agent-install.sh` installs the Google Cloud Ops Agent.
- **`admin/add-gh-user.sh`** — Provisions a Linux user and pulls their SSH public keys from GitHub.
- **`.github/workflows/check.yml`** — GitHub Actions CI. Runs `make check` on every push to `main`.

## Conventions

- All shell scripts use `set -eu` (strict error handling).
- Pinned software versions are hardcoded as shell variables (e.g., `CSP_VERSION='2.21.2'`) — `upgrade.py` manages these via regex patterns.
- Scripts are intended to run as root on the target VM (except Docker scripts which run as the local user).
- Keep `CLAUDE.md` and `README.md` up to date when making changes that affect commands, architecture, or conventions documented in them.
