#!/bin/bash
set -e
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec bash "$BASE_DIR/scripts/build.sh" "$@"
