"""Shared text-file configuration for the V3.0 geometry and its editor."""

from __future__ import annotations

import os
import tempfile

try:
    import tomllib
except ImportError:  # pragma: no cover - FreeCAD currently embeds Python 3.11+
    tomllib = None


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config", "design_parameters.toml")

# key, Czech label, default, minimum, maximum, unit, short explanation
PARAMETER_SPECS = (
    ("primary_depth", "Hloubka P/S/T", 400.0, 250.0, 800.0, "mm", "Společná kolmá vzdálenost front–rear."),
    ("technical_channel_width", "Technologický kanál", 300.0, 180.0, 700.0, "mm", "Volná mezera mezi dvojicí S/T."),
    ("side_desk_length", "Délka S/T", 1000.0, 500.0, 1500.0, "mm", "Délka hlavních rovnoběžných hran S/T."),
    ("user_edge_width", "Čelní hrana P", 800.0, 500.0, 1200.0, "mm", "Hrana primární desky směrem k uživateli."),
    ("user_clearance", "Odstup uživatele", 550.0, 250.0, 800.0, "mm", "Odstup referenční polohy očí od čelní hrany P."),
    ("primary_monitor_radius", "P monitor – poloměr", 400.0, 200.0, 700.0, "mm", "Radiální poloha primárního monitoru."),
    ("side_monitor_radius", "S/T monitor Work – poloměr", 750.0, 450.0, 1200.0, "mm", "Radiální poloha těla S/T monitoru v režimu Work."),
    ("side_monitor_offset", "S/T monitor Work – od osy", 120.0, 0.0, 350.0, "mm", "Příčný posun těla monitoru od osy ramene."),
    ("side_lift_radius", "S/T lift – poloměr", 780.0, 450.0, 1200.0, "mm", "Radiální poloha osy liftu v kanálu."),
    ("side_lift_offset", "S/T lift – od osy", 85.0, 0.0, 300.0, "mm", "Příčná poloha osy liftu v kanálu."),
    ("primary_monitor_width", "Šířka P monitoru", 650.0, 300.0, 1000.0, "mm", "Půdorysná šířka primárního monitoru."),
    ("side_monitor_width", "Šířka S/T monitoru", 560.0, 300.0, 1000.0, "mm", "Půdorysná šířka bočního monitoru."),
    ("monitor_body_thickness", "Tloušťka monitoru", 38.0, 10.0, 120.0, "mm", "Půdorysná tloušťka těla monitoru."),
    ("monitor_lift_diameter", "Průměr liftu", 90.0, 30.0, 180.0, "mm", "Kontrolovaná půdorysná obálka liftu."),
    ("monitor_desk_clearance", "Rezerva lift–deska", 20.0, 0.0, 100.0, "mm", "Minimální plánovaná mezera od pracovní desky."),
    ("party_surface_height", "Výška Party", 700.0, 600.0, 1200.0, "mm", "Výška horní roviny party vrstvy."),
    ("party_module_thickness", "Tloušťka Party", 40.0, 15.0, 100.0, "mm", "Tloušťka horních party modulů."),
    ("party_partition_bottom_height", "Spodek uložené přepážky", 780.0, 760.0, 1200.0, "mm", "Spodní hrana svislého ramenního modulu ve Work."),
    ("party_storage_vertical_clearance", "Svislá mezera uložených modulů", 20.0, 20.0, 300.0, "mm", "Mezera mezi horní hranou přepážek a centrálním modulem."),
)

DEFAULTS = {spec[0]: spec[2] for spec in PARAMETER_SPECS}
SPEC_BY_KEY = {spec[0]: spec for spec in PARAMETER_SPECS}


def normalize_parameters(values):
    result = dict(DEFAULTS)
    for key, value in values.items():
        if key in result:
            result[key] = float(value)
    return result


def validate_parameters(values):
    values = normalize_parameters(values)
    errors = []
    for key, label, _default, minimum, maximum, unit, _help in PARAMETER_SPECS:
        value = values[key]
        if not minimum <= value <= maximum:
            errors.append("%s: %.3f %s není v rozsahu %.3f–%.3f %s" % (
                label, value, unit, minimum, maximum, unit,
            ))
    lift_clearance = (
        values["technical_channel_width"] / 2.0
        - values["side_lift_offset"]
        - values["monitor_lift_diameter"] / 2.0
    )
    if lift_clearance < values["monitor_desk_clearance"]:
        errors.append(
            "Lift S/T má k desce jen %.1f mm; požadováno je %.1f mm."
            % (lift_clearance, values["monitor_desk_clearance"])
        )
    if values["party_module_thickness"] >= values["party_surface_height"]:
        errors.append("Tloušťka party modulu musí být menší než jeho horní výška.")
    return errors


def load_parameters(path=CONFIG_PATH):
    values = dict(DEFAULTS)
    if not os.path.exists(path):
        return values
    if tomllib is None:
        raise RuntimeError("Python tomllib is required to read %s" % path)
    with open(path, "rb") as handle:
        document = tomllib.load(handle)
    geometry = document.get("geometry", {})
    if not isinstance(geometry, dict):
        raise ValueError("[geometry] must be a TOML table in %s" % path)
    unknown = sorted(set(geometry) - set(DEFAULTS))
    if unknown:
        raise ValueError("Unknown design parameter(s): %s" % ", ".join(unknown))
    values.update({key: float(value) for key, value in geometry.items()})
    errors = validate_parameters(values)
    if errors:
        raise ValueError("Invalid design parameters:\n- " + "\n- ".join(errors))
    return values


def render_parameters(values):
    values = normalize_parameters(values)
    lines = [
        "# MultiRoleWorkIsland V3.0 — editable geometry parameters",
        "# Units are millimetres. Derived relationships are defined in geometry_v30.py.",
        "",
        "[geometry]",
    ]
    for key, label, _default, _minimum, _maximum, unit, _help in PARAMETER_SPECS:
        lines.append("# %s [%s]" % (label, unit))
        lines.append("%s = %s" % (key, format(values[key], ".6g")))
    return "\n".join(lines) + "\n"


def save_parameters(values, path=CONFIG_PATH):
    values = normalize_parameters(values)
    errors = validate_parameters(values)
    if errors:
        raise ValueError("Invalid design parameters:\n- " + "\n- ".join(errors))
    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)
    descriptor, temporary_path = tempfile.mkstemp(prefix=".design-parameters-", suffix=".toml", dir=directory)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(render_parameters(values))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    except Exception:
        try:
            os.unlink(temporary_path)
        except OSError:
            pass
        raise
