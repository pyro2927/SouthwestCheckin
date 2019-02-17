#!/bin/sh
set -e

if [ "$1" != "/bin/sh" ]; then
  python ./checkin.py $@
else
  exec "$@"
fi
