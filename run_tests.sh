#!/bin/sh
set -e

# set repo directory as st2-cloud-pack location
REPO_DIR=$(cd -- "$(dirname -- "$0")" && pwd)

export ST2_REPO_PATH="/tmp/st2"

# branch name on - https://github.com/stackstorm/st2
# currently the dev 3.9 branch
# WARNING: this is a dev branch so tests may fail due to upstream changes, but we're forced to use it as
# the stable branch uses python 3.8 with is EOL
export ST2_VERSION="v3.9"

if [ ! -d "$ST2_REPO_PATH" ]; then
    git clone --depth=1 -b "$ST2_VERSION" https://github.com/stackstorm/st2.git "$ST2_REPO_PATH"
fi

export PYTHONPATH="$PYTHONPATH:$REPO_DIR/lib"
"$ST2_REPO_PATH/st2common/bin/st2-run-pack-tests" -p "$REPO_DIR" -c
