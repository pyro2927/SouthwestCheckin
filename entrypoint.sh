#!/bin/sh
set -e

if [ "$1" != "/bin/sh" ]; then
  python -u ./checkin.py "$@"
else
  exec "$@"
fi
