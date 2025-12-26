#!/bin/bash
set -eu

cd /root

tmpdir=$(mktemp -d /tmp/devops-vm-gcloud-install-ops-agent.XXXXXXX)
cd "${tmpdir}"

curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh
/bin/bash add-google-cloud-ops-agent-repo.sh --also-install

cd /root
rm -rf "${tmpdir}"

exit 0
