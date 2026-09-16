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
  GENERATOR   cad/generators/sector_generator_v22.py, falling back to V2.1/V2
  OUTPUT DIR  <project root>/output_v22 for V2.2 (matching older revisions)

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
freecad_console_args=()
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
    if [[ -f "$project_root/cad/generators/sector_generator_v22.py" ]]; then
        generator="$project_root/cad/generators/sector_generator_v22.py"
    elif [[ -f "$project_root/cad/generators/sector_generator_v21.py" ]]; then
        generator="$project_root/cad/generators/sector_generator_v21.py"
    elif [[ -f "$project_root/cad/generators/sector_generator_v2.py" ]]; then
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
generator_name="$(basename -- "$generator")"

case "$generator_name" in
    sector_generator_v22.py)
        model_name="island_concept_v22"
        default_output_name="output_v22"
        ;;
    sector_generator_v21.py)
        model_name="island_concept_v21"
        default_output_name="output_v21"
        ;;
    *)
        model_name="island_concept_v2"
        default_output_name="output_v2"
        ;;
esac

if [[ -z "$freecad_cmd" ]]; then
    if command -v freecadcmd >/dev/null 2>&1; then
        freecad_cmd="$(command -v freecadcmd)"
    elif command -v FreeCADCmd >/dev/null 2>&1; then
        freecad_cmd="$(command -v FreeCADCmd)"
    elif command -v freecad >/dev/null 2>&1; then
        freecad_cmd="$(command -v freecad)"
        freecad_console_args=(-c)
    elif command -v FreeCAD >/dev/null 2>&1; then
        freecad_cmd="$(command -v FreeCAD)"
        freecad_console_args=(-c)
    else
        die "No FreeCAD executable was found. Install FreeCAD or use --freecadcmd PATH."
    fi
fi
[[ -x "$freecad_cmd" ]] || die "FreeCAD is not executable: $freecad_cmd"
if ((${#freecad_console_args[@]} == 0)); then
    case "$(basename -- "$freecad_cmd")" in
        freecad|FreeCAD)
            freecad_console_args=(-c)
            ;;
    esac
fi

if [[ -z "$output_dir" ]]; then
    output_dir="$project_root/$default_output_name"
elif [[ "$output_dir" != /* ]]; then
    output_dir="$PWD/$output_dir"
fi

build_dir="$project_root/build/freecad"
mkdir -p -- "$build_dir"
timestamp="$(date -u +'%Y%m%dT%H%M%SZ')"
log_file="$build_dir/freecad-$timestamp.log"

printf 'Generator: %s\n' "$generator"
printf 'FreeCAD:    %s\n' "$freecad_cmd"
if ((${#freecad_console_args[@]})); then
    printf 'Mode:       console (%s)\n' "${freecad_console_args[*]}"
fi
printf 'Output:     %s\n' "$output_dir"
printf 'Log:        %s\n' "$log_file"

export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-offscreen}"
export PYTHONUNBUFFERED=1

# Run from the generator directory so any relative project resources behave
# consistently. pipefail preserves FreeCAD's failure through tee.
(
    cd -- "$generator_dir"
    "$freecad_cmd" "${freecad_console_args[@]}" "$generator"
) 2>&1 | tee -- "$log_file"

artifacts=(
    "$output_dir/$model_name.FCStd"
    "$output_dir/${model_name}_WORK.step"
    "$output_dir/${model_name}_PARTY.step"
)
if [[ "$model_name" == "island_concept_v21" || "$model_name" == "island_concept_v22" ]]; then
    artifacts+=(
        "$output_dir/${model_name}_collision_report.json"
        "$output_dir/${model_name}_plan.svg"
    )
fi

missing=0
for artifact in "${artifacts[@]}"; do
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
    fcstd="$output_dir/$model_name.FCStd"
    if command -v freecad >/dev/null 2>&1; then
        freecad "$fcstd" >/dev/null 2>&1 &
    elif command -v FreeCAD >/dev/null 2>&1; then
        FreeCAD "$fcstd" >/dev/null 2>&1 &
    else
        die "The model was built, but graphical FreeCAD was not found"
    fi
    printf 'Opening: %s\n' "$fcstd"
fi
