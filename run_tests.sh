#!/bin/sh
set -e

REPO_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

export ST2_REPO_PATH="/tmp/st2"
if [ ! -d "$ST2_REPO_PATH" ]; then
    git clone --depth=1 https://github.com/stackstorm/st2.git "$ST2_REPO_PATH"
fi

"$ST2_REPO_PATH/st2common/bin/st2-run-pack-tests" -p "$REPO_DIR" -c
