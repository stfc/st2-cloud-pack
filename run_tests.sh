#!/bin/sh
set -e

REPO_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

export ST2_REPO_PATH="/tmp/st2"
if [ ! -d "$ST2_REPO_PATH" ]; then
    git clone --depth=1 https://github.com/stackstorm/st2.git "$ST2_REPO_PATH"
fi

# Monkey patch nose to pytest until upstream has switched
echo "PATCH: Replace nosetests with pytest"
sed -ri 's/nosetests \${NOSE_OPTS\[\@\]}/pytest/g' "$ST2_REPO_PATH/st2common/bin/st2-run-pack-tests"

PYTHON_PATH=$PYTHON_PATH:"$REPO_DIR/lib" "$ST2_REPO_PATH/st2common/bin/st2-run-pack-tests" -p "$REPO_DIR" -c

# Generate coverage to consume locally
python -m pip install coverage~=4.4
coverage xml
