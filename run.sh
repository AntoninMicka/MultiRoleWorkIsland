#!/usr/bin/env bash
# Compatibility entry point for the repository-root build command.

set -Eeuo pipefail

script_dir="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
if [[ "${1:-}" == "--configure" || "${1:-}" == "configure" ]]; then
    shift
    exec python3 "$script_dir/tools/parameter_editor.py" "$@"
fi
exec "$script_dir/tools/run_freecad.sh" "$@"
