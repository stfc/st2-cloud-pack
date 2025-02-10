#!/bin/sh
set -e

# set repo directory as st2-cloud-pack location
REPO_DIR=$(cd -- "$(dirname -- "$0")" && pwd)

export ST2_REPO_PATH="/tmp/st2"
if [ ! -d "$ST2_REPO_PATH" ]; then
    git clone --depth=1 https://github.com/stackstorm/st2.git "$ST2_REPO_PATH"
fi

export PYTHONPATH="$PYTHONPATH:$REPO_DIR/lib"
"$ST2_REPO_PATH/st2common/bin/st2-run-pack-tests" -p "$REPO_DIR" -c
