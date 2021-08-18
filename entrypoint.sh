#!/bin/sh
set -e

if [ "$1" != "/bin/sh" ]; then
  checkin "$@"
else
  exec "$@"
fi
