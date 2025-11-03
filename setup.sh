#!/bin/bash
set -eu

GH_REF=${1:?'github ref name?'}

REPO='jcroots/devops-vm'
URL="https://github.com/${REPO}/archive/refs/${GH_REF}.tar.gz"

DESTDIR=/opt/jcroots/devops-vm

tmpfn=$(mktemp /tmp/devops-vm-setup-XXXXXXXX.tar.gz)

wget -q -O "${tmpfn}" "${URL}"

rm -rfv "${DESTDIR}"
install -v -m 0755 -o root -g root -d "${DESTDIR}"

tar -vxzf "${tmpfn}" -C "${DESTDIR}" --strip-components=1

rm -f "${tmpfn}"

echo "${DESTDIR} ${GH_REF} setup done!!"

exit 0
