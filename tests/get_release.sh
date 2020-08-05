#!/bin/bash

# set -x  # debugging
version_rel () {
    semantic_version_type=${1}
    if [ ! -z "${semantic_version_type##*[!0-9]*}" ]; then
        semantic_version_type=$((semantic_version_type + 1))
        true
    
    elif [[ ${semantic_version_type,,} == "major" ]]; then
        semantic_version_type=1

    elif [[ ${semantic_version_type,,} == "minor" ]]; then
        semantic_version_type=2

    elif [[ ${semantic_version_type,,} == "patch" ]]; then
        semantic_version_type=3

    else
        echo "Invalid semantic version type was passed to script."
        echo "The correct usage is a single digit or the string [major|minor|patch]"
        exit 1
    fi

    echo $(git describe --abbrev=0 --tags | cut -c2- | awk -F'.' "{print \$${semantic_version_type}}")
}

version_rel $@
