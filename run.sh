#!/usr/bin/env bash
# Compatibility entry point for the repository-root build command.

set -Eeuo pipefail

script_dir="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
exec "$script_dir/tools/run_freecad.sh" "$@"
