#!/bin/bash

# Release current content to target SAE version direcory
if [ -z "$1" ]; then
  echo `basename $0`" [target dir]"
  echo "	target dir: target dir related to release dir, such as hello02/1"
  exit -1
fi

TARGET=$1
[ -d "${TARGET}" ] || mkdir -p "${TARGET}"

PWD=`pwd`
for each in `ls ${PWD}`; do
  [[ ${TARGET} != ${each}* ]] && cp -r ${each} ${TARGET}
done

exit 0
