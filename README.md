# devops-vm

Provisioning and configuration scripts for a shared development VM.

## Setup

Deploy to a target machine by running `setup.sh` with a GitHub ref (tag or branch):

```sh
sudo ./setup.sh tags/v2512
```

This downloads the release tarball and extracts it to `/opt/jcroots/devops-vm`.

## Docker Dev Environment

Build and run a Debian-based dev container matched to your local user:

```sh
make docker        # build the image
docker/devel.sh    # run an interactive shell with $PWD mounted
```

## GCP Services

- **Cloud SQL Proxy:** `gcloud/sql-proxy-install.sh` installs a pinned version. `gcloud/sql-proxy/` has the systemd unit and wrapper script.
- **Ops Agent:** `gcloud/ops-agent-install.sh` installs the Google Cloud monitoring agent.

## User Management

Add a Linux user with their GitHub SSH keys:

```sh
sudo admin/add-gh-user.sh <github-username>
```

## Version Updates

Check for newer versions of pinned dependencies (Cloud SQL Proxy, Debian base image):

```sh
python3 upgrade.py --dry-run   # check only
python3 upgrade.py             # check and update files
```

## Linting

```sh
make check   # runs shellcheck on all .sh files
```
