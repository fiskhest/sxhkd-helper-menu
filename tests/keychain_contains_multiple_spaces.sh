#!/bin/bash
set -x
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
test=$(python ${SCRIPT_DIR}/../hkhelper.py -f ${SCRIPT_DIR}/sxhkdrc | grep -oP "(?<=[\w\+\-^])\s{2}(?=[\w\+\-^])" | wc -l)

if [[ "${test}" -gt 0 ]]; then
    echo "At least one keychain had multiple spaces in a row (indicating regex problems)"
    exit 1
else
    echo "All clear!"
    exit 0
fi

