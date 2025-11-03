#!/bin/bash
set -eu
TAG=${1:?'tag name?'}
REPO='jcroots/devops-vm'
URL="https://github.com/${REPO}/archive/refs/tags/${TAG}.tar.gz"

DESTDIR=/opt/jcroots/devops

tmpfn=$(mktemp /tmp/devops-vm-setup-XXXXXXXX.tar.gz)

wget -q -O "${tmpfn}" "${URL}"

rm -rfv "${DESTDIR}"
install -v -m 0755 -o root -g root -d "${DESTDIR}"

tar -vxzf "${tmpfn}" -C "${DESTDIR}" --strip-components=1

rm -f "${tmpfn}"

echo "${DESTDIR} ${TAG} setup done!!"

exit 0
