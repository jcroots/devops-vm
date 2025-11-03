#!/bin/bash
set -eu

NAME=${1:?'user name?'}

useradd -m -c "${NAME}" -d "/home/${NAME}" -s /bin/bash "${NAME}"

echo "${NAME} ALL=(ALL) NOPASSWD:ALL" >"/etc/sudoers.d/${NAME}"
chmod -v 0440 "/etc/sudoers.d/${NAME}"

install -v -m 0750 -o "${NAME}" -g "${NAME}" -d "/home/${NAME}/.ssh"

curl -sSL "https://github.com/${NAME}.keys" >"/home/${NAME}/.ssh/.authorized_keys.tmp"

install -v -m 0640 -o "${NAME}" -g "${NAME}" "/home/${NAME}/.ssh/.authorized_keys.tmp" "/home/${NAME}/.ssh/authorized_keys"

rm -f "/home/${NAME}/.ssh/.authorized_keys.tmp"

exit 0
