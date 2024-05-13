#!/usr/bin/env bash
set -uxo pipefail

HERE=$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")
REPO_SRC_DIR=${REPO_SRC_DIR:=$HERE/..}
pushd $REPO_SRC_DIR

# note that space before slash is important
PATCHES="\
bootgen \
pyxrt \
aie-rt \
"

if [[ x"${APPLY_PATCHES:-true}" == x"true" ]]; then
  for PATCH in $PATCHES; do
    echo "applying $PATCH"
    git apply --ignore-space-change --ignore-whitespace patches/$PATCH.diff
    ERROR=$?
    if [ $ERROR != 0 ]; then
      git apply --ignore-space-change --ignore-whitespace --verbose --directory patches/$PATCH.diff -R --check
      ERROR=$?
      if [ $ERROR != 0 ]; then
        exit $ERROR
      fi
    fi
  done
fi

pushd $REPO_SRC_DIR
