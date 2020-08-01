#!/usr/bin/env bash

fname="hkhelper.py"
lbin="${HOME}/.local/bin"
mkdir -p ${lbin}

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"

if [[ ! -f "${lbin}/${fname}" ]]; then
    cp ${SCRIPT_DIR}/../rhkhm/__init__.py ${lbin}/${fname}
fi
