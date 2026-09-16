#!/usr/bin/env bash
# Build the MultiRoleWorkIsland concept model with a FreeCAD executable.

set -Eeuo pipefail

usage() {
    cat <<'EOF'
Usage: ./run.sh [OPTIONS] [GENERATOR]

Run the MultiRoleWorkIsland Python generator through FreeCAD, save a log,
and verify that the expected FCStd and STEP files were produced.

Options:
  --open              Open the generated FCStd in graphical FreeCAD afterwards.
  --freecadcmd PATH   Use an explicit FreeCAD executable.
  --output-dir PATH   Expected generator output directory.
  -h, --help          Show this help.

Defaults:
  GENERATOR   cad/generators/sector_generator_v2.py,
              cad/sector_generator_v2.py, or sector_generator_v2.py
  OUTPUT DIR  <project root>/output_v2

Environment:
  FREECADCMD          Alternative to --freecadcmd.
                      Auto-detection tries freecadcmd, FreeCADCmd, freecad,
                      then FreeCAD.
  QT_QPA_PLATFORM     Defaults to offscreen for the headless build.
EOF
}

die() {
    printf 'ERROR: %s\n' "$*" >&2
    exit 1
}

script_dir="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
project_root="$script_dir"
if [[ "$(basename -- "$script_dir")" == "tools" ]]; then
    project_root="$(CDPATH= cd -- "$script_dir/.." && pwd -P)"
fi
generator=""
freecad_cmd="${FREECADCMD:-}"
output_dir=""
open_after=0

while (($#)); do
    case "$1" in
        --open)
            open_after=1
            shift
            ;;
        --freecadcmd)
            (($# >= 2)) || die "--freecadcmd requires a path"
            freecad_cmd="$2"
            shift 2
            ;;
        --output-dir)
            (($# >= 2)) || die "--output-dir requires a path"
            output_dir="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        --)
            shift
            (($# <= 1)) || die "Only one generator may be specified"
            generator="${1:-}"
            shift "$#"
            ;;
        -*)
            die "Unknown option: $1"
            ;;
        *)
            [[ -z "$generator" ]] || die "Only one generator may be specified"
            generator="$1"
            shift
            ;;
    esac
done

if [[ -z "$generator" ]]; then
    if [[ -f "$project_root/cad/generators/sector_generator_v2.py" ]]; then
        generator="$project_root/cad/generators/sector_generator_v2.py"
    elif [[ -f "$project_root/cad/sector_generator_v2.py" ]]; then
        generator="$project_root/cad/sector_generator_v2.py"
    else
        generator="$project_root/sector_generator_v2.py"
    fi
elif [[ "$generator" != /* ]]; then
    generator="$PWD/$generator"
fi

[[ -f "$generator" ]] || die "Generator not found: $generator"
generator_dir="$(CDPATH= cd -- "$(dirname -- "$generator")" && pwd -P)"
generator="$generator_dir/$(basename -- "$generator")"

if [[ -z "$freecad_cmd" ]]; then
    if command -v freecadcmd >/dev/null 2>&1; then
        freecad_cmd="$(command -v freecadcmd)"
    elif command -v FreeCADCmd >/dev/null 2>&1; then
        freecad_cmd="$(command -v FreeCADCmd)"
    elif command -v freecad >/dev/null 2>&1; then
        freecad_cmd="$(command -v freecad)"
    elif command -v FreeCAD >/dev/null 2>&1; then
        freecad_cmd="$(command -v FreeCAD)"
    else
        die "No FreeCAD executable was found. Install FreeCAD or use --freecadcmd PATH."
    fi
fi
[[ -x "$freecad_cmd" ]] || die "FreeCAD is not executable: $freecad_cmd"

if [[ -z "$output_dir" ]]; then
    output_dir="$project_root/output_v2"
elif [[ "$output_dir" != /* ]]; then
    output_dir="$PWD/$output_dir"
fi

build_dir="$project_root/build/freecad"
mkdir -p -- "$build_dir"
timestamp="$(date -u +'%Y%m%dT%H%M%SZ')"
log_file="$build_dir/freecad-$timestamp.log"

printf 'Generator: %s\n' "$generator"
printf 'FreeCAD:    %s\n' "$freecad_cmd"
printf 'Output:     %s\n' "$output_dir"
printf 'Log:        %s\n' "$log_file"

export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-offscreen}"
export PYTHONUNBUFFERED=1

# Run from the generator directory so any relative project resources behave
# consistently. pipefail preserves FreeCAD's failure through tee.
(
    cd -- "$generator_dir"
    "$freecad_cmd" "$generator"
) 2>&1 | tee -- "$log_file"

fcstd="$output_dir/island_concept_v2.FCStd"
work_step="$output_dir/island_concept_v2_WORK.step"
party_step="$output_dir/island_concept_v2_PARTY.step"

missing=0
for artifact in "$fcstd" "$work_step" "$party_step"; do
    if [[ -s "$artifact" ]]; then
        printf 'OK: %s (%s bytes)\n' "$artifact" "$(stat -c '%s' -- "$artifact")"
    else
        printf 'MISSING OR EMPTY: %s\n' "$artifact" >&2
        missing=1
    fi
done
((missing == 0)) || die "FreeCAD finished, but one or more expected artifacts are missing"

printf 'Build completed successfully.\n'

if ((open_after)); then
    if command -v freecad >/dev/null 2>&1; then
        freecad "$fcstd" >/dev/null 2>&1 &
    elif command -v FreeCAD >/dev/null 2>&1; then
        FreeCAD "$fcstd" >/dev/null 2>&1 &
    else
        die "The model was built, but graphical FreeCAD was not found"
    fi
    printf 'Opening: %s\n' "$fcstd"
fi
