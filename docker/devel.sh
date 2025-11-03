#!/bin/sh
set -eu
user=$(id -u -n)
exec docker run -it --rm -u "${user}" \
    --name devops-vm \
    --hostname vm.devops.local \
    -e "TERM=${TERM}" \
    -v "${PWD}:/home/${user}/src" \
    --workdir "/home/${user}/src" \
    jcroots/devops-vm
