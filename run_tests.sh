#!/bin/sh
set -e

# set repo directory as st2-cloud-pack location
REPO_DIR=$(cd -- "$(dirname -- "$0")" && pwd)

export ST2_REPO_PATH="/tmp/st2"
export ST2_VERSION="v3.9"
if [ ! -d "$ST2_REPO_PATH" ]; then
    git clone --depth=1 -b "$ST2_VERSION" https://github.com/stackstorm/st2.git "$ST2_REPO_PATH"
fi

export PYTHONPATH="$PYTHONPATH:$REPO_DIR/lib"
"$ST2_REPO_PATH/st2common/bin/st2-run-pack-tests" -p "$REPO_DIR" -c
