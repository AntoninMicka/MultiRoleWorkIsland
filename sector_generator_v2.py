# -*- coding: utf-8 -*-
"""
MULTIFUNCTION WORK / PARTY ISLAND - CONCEPT CAD V2
==================================================

Parametric FreeCAD generator for the complete three-station island.

Run headless (the file intentionally executes also when FreeCADCmd imports it):

    freecadcmd sector_generator_v2.py

or copy/rename it to ``sector_generator_v2.FCMacro`` and execute it as a macro.

Outputs (next to this file, in ``output_v2``):

    island_concept_v2.FCStd
    island_concept_v2_WORK.step
    island_concept_v2_PARTY.step

The FCStd document contains independently switchable groups:

    00_STRUCTURE
    10_WORK_MODE       (visible by default)
    20_PARTY_MODE      (hidden by default)
    30_SERVICE_MODE    (hidden, provisional reference pose)
    90_MOTION_ENVELOPES (hidden by default)

V2 is a concept model, not manufacturing documentation. It makes the overall
layout, nine independently controlled P/S/T planes, monitor arrangement,
party covers and principal lift envelopes readable. Hinges, locks, fasteners,
actuators, cable chains and structural sizing still need engineering.

Coordinate convention
---------------------
Station A faces the hub along angle 0 degrees. Stations B and C are rotated by
120 and 240 degrees. For each station:

* P is the central saddle desk.
* S occupies the clockwise/inner lane of the arm at station angle + 60 deg.
* T occupies the counter-clockwise/inner lane of the arm at station angle - 60 deg.

Consequently each physical arm contains two neighbouring station planes with a
400 mm central shaft. This corrects the left-lane sign ambiguity in V1.
"""

from __future__ import print_function

import math
import os

import FreeCAD as App
import Part


# =============================================================================
# PARAMETERS - millimetres / degrees
# =============================================================================

DOCUMENT_NAME = "island_concept_v2"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output_v2")

# Main plan geometry
ARM_LENGTH = 1500.0
ARM_WIDTH = 1600.0
SHAFT_GAP = 400.0
HUB_RADIUS = 450.0
ARM_START = HUB_RADIUS

# P/S/T work planes
P_DEPTH = 850.0
P_WIDTH = 1300.0
P_CORNER_RADIUS = 140.0
LANE_WIDTH = (ARM_WIDTH - SHAFT_GAP) / 2.0
DESK_THICKNESS = 40.0
DESK_CORNER_RADIUS = 90.0

# Nominal modes
WORK_HEIGHT = 750.0
PARTY_HEIGHT = 700.0
SERVICE_HEIGHT = 1200.0  # provisional access pose

# Physical/software lift limits retained from V1
COL_STROKE_PHYS_MIN = 300.0
COL_STROKE_PHYS_MAX = 2000.0
COL_SW_OFFSET = 400.0
COL_SW_MIN = COL_STROKE_PHYS_MIN + COL_SW_OFFSET
COL_SW_MAX = COL_STROKE_PHYS_MAX + COL_SW_OFFSET

# Structure
CORE_HEIGHT = 680.0
CORE_TRIANGLE_RADIUS = 330.0
CORE_BASE_RADIUS = 430.0
CORE_BASE_HEIGHT = 100.0
COLUMN_OUTER_DIA = 115.0
COLUMN_INNER_DIA = 86.0
COLUMN_OUTER_HEIGHT = 430.0
FOOT_DIAMETER = 300.0
FOOT_HEIGHT = 28.0
FLOOR_RAIL_LENGTH = 1050.0
FLOOR_RAIL_WIDTH = 90.0
FLOOR_RAIL_HEIGHT = 55.0

# Party layer
ARM_PARTY_COVER_LENGTH = 1220.0
ARM_PARTY_COVER_START = HUB_RADIUS + 120.0
ARM_PARTY_COVER_WIDTH = SHAFT_GAP + 80.0
PARTY_COVER_THICKNESS = 40.0
PARTITION_HEIGHT = 720.0
PARTITION_THICKNESS = 40.0
CENTRAL_PARTY_TOP_RADIUS = 760.0

# Monitors - visual placeholders
P_MONITOR_WIDTH = 650.0
SIDE_MONITOR_WIDTH = 560.0
MONITOR_HEIGHT = 370.0
MONITOR_THICKNESS = 38.0
MONITOR_BEZEL = 18.0
MONITOR_BOTTOM_GAP = 95.0
MONITOR_PARK_DROP = 450.0
MONITOR_VIEW_RISE = 900.0
MONITOR_LIFT_DIA = 90.0

# Visual / export options
CREATE_STEP_EXPORTS = True
SHOW_REFERENCE_CHAIRS = True

COLORS = {
    "P": (0.25, 0.55, 0.88),       # blue
    "S": (0.24, 0.72, 0.55),       # green
    "T": (0.93, 0.55, 0.22),       # orange
    "PARTY": (0.92, 0.74, 0.27),   # gold
    "STRUCTURE": (0.22, 0.24, 0.28),
    "STRUCTURE_2": (0.42, 0.45, 0.50),
    "MONITOR": (0.075, 0.085, 0.10),
    "DISPLAY": (0.12, 0.38, 0.62),
    "SERVICE": (0.58, 0.38, 0.76),
    "ENVELOPE": (0.95, 0.20, 0.70),
    "REFERENCE": (0.60, 0.62, 0.66),
}

STATIONS = (
    ("A", 0.0),
    ("B", 120.0),
    ("C", 240.0),
)


# =============================================================================
# GEOMETRY HELPERS
# =============================================================================

def rotate_z(shape, angle_deg):
    """Rotate a shape around the global Z axis and return it."""
    if angle_deg:
        shape.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), angle_deg)
    return shape


def polar_xy(radius, angle_deg, tangential_offset=0.0):
    """Point in a frame whose local X is radial and local Y tangential."""
    a = math.radians(angle_deg)
    return (
        radius * math.cos(a) - tangential_offset * math.sin(a),
        radius * math.sin(a) + tangential_offset * math.cos(a),
    )


def rounded_plate(length, width, height, x0, y0, z0, radius, angle_deg=0.0):
    """Rounded rectangular prism made from two boxes and four cylinders.

    The local plate runs along +X. ``y0`` is its minimum local Y coordinate.
    Boolean fusion is intentionally used instead of edge-index filleting, whose
    edge numbering can vary between OpenCascade versions.
    """
    r = max(0.0, min(radius, length / 2.0, width / 2.0))
    if r < 0.01:
        return rotate_z(Part.makeBox(length, width, height, App.Vector(x0, y0, z0)), angle_deg)

    shape = Part.makeBox(length - 2.0 * r, width, height, App.Vector(x0 + r, y0, z0))
    shape = shape.fuse(
        Part.makeBox(length, width - 2.0 * r, height, App.Vector(x0, y0 + r, z0))
    )
    for cx in (x0 + r, x0 + length - r):
        for cy in (y0 + r, y0 + width - r):
            shape = shape.fuse(
                Part.makeCylinder(r, height, App.Vector(cx, cy, z0), App.Vector(0, 0, 1))
            )
    try:
        shape = shape.removeSplitter()
    except Exception:
        pass
    return rotate_z(shape, angle_deg)


def local_box(length, width, height, x0, y_center, z0, angle_deg):
    shape = Part.makeBox(
        length,
        width,
        height,
        App.Vector(x0, y_center - width / 2.0, z0),
    )
    return rotate_z(shape, angle_deg)


def regular_polygon_prism(radius, sides, height, z0, rotation_deg=0.0):
    points = []
    for i in range(sides):
        angle = math.radians(rotation_deg + i * 360.0 / sides)
        points.append(App.Vector(radius * math.cos(angle), radius * math.sin(angle), z0))
    points.append(points[0])
    wire = Part.makePolygon(points)
    face = Part.Face(wire)
    return face.extrude(App.Vector(0, 0, height))


def triangle_prism(radius, height, z0, rotation_deg=90.0):
    return regular_polygon_prism(radius, 3, height, z0, rotation_deg)


def lane_center_offset(lane_sign):
    """Tangential center of an arm lane in its own local frame."""
    return lane_sign * (SHAFT_GAP / 2.0 + LANE_WIDTH / 2.0)


def desk_shape(kind, station_angle, top_height):
    z0 = top_height - DESK_THICKNESS
    if kind == "P":
        return rounded_plate(
            P_DEPTH,
            P_WIDTH,
            DESK_THICKNESS,
            HUB_RADIUS + 70.0,
            -P_WIDTH / 2.0,
            z0,
            P_CORNER_RADIUS,
            station_angle,
        )

    if kind == "S":
        arm_angle = station_angle + 60.0
        lane_sign = -1.0  # side of +60 arm facing this station
    elif kind == "T":
        arm_angle = station_angle - 60.0
        lane_sign = +1.0  # side of -60 arm facing this station (fixed vs V1)
    else:
        raise ValueError("Unknown desk kind: " + str(kind))

    return rounded_plate(
        ARM_LENGTH,
        LANE_WIDTH,
        DESK_THICKNESS,
        ARM_START,
        lane_center_offset(lane_sign) - LANE_WIDTH / 2.0,
        z0,
        DESK_CORNER_RADIUS,
        arm_angle,
    )


def desk_column_location(kind, station_angle):
    if kind == "P":
        return polar_xy(HUB_RADIUS + 70.0 + P_DEPTH * 0.58, station_angle, 0.0)
    if kind == "S":
        return polar_xy(
            ARM_START + ARM_LENGTH * 0.58,
            station_angle + 60.0,
            lane_center_offset(-1.0),
        )
    if kind == "T":
        return polar_xy(
            ARM_START + ARM_LENGTH * 0.58,
            station_angle - 60.0,
            lane_center_offset(+1.0),
        )
    raise ValueError("Unknown desk kind: " + str(kind))


def cylinder_at(x, y, diameter, height, z0):
    return Part.makeCylinder(
        diameter / 2.0,
        height,
        App.Vector(x, y, z0),
        App.Vector(0, 0, 1),
    )


def column_inner_shape(kind, station_angle, top_height):
    x, y = desk_column_location(kind, station_angle)
    z0 = COLUMN_OUTER_HEIGHT * 0.70
    height = max(20.0, top_height - DESK_THICKNESS - z0)
    return cylinder_at(x, y, COLUMN_INNER_DIA, height, z0)


def monitor_frame_shape(angle_deg, radius, tangential_offset, desk_top, width):
    bottom = desk_top + MONITOR_BOTTOM_GAP
    body = local_box(
        MONITOR_THICKNESS,
        width,
        MONITOR_HEIGHT,
        radius - MONITOR_THICKNESS / 2.0,
        tangential_offset,
        bottom,
        angle_deg,
    )
    x, y = polar_xy(radius, angle_deg, tangential_offset)
    support = cylinder_at(
        x,
        y,
        MONITOR_LIFT_DIA,
        MONITOR_BOTTOM_GAP,
        desk_top,
    )
    return body.fuse(support)


def monitor_display_shape(angle_deg, radius, tangential_offset, desk_top, width):
    """Thin coloured front face on the outward side of the monitor body."""
    face_thickness = 3.0
    return local_box(
        face_thickness,
        width - 2.0 * MONITOR_BEZEL,
        MONITOR_HEIGHT - 2.0 * MONITOR_BEZEL,
        radius + MONITOR_THICKNESS / 2.0,
        tangential_offset,
        desk_top + MONITOR_BOTTOM_GAP + MONITOR_BEZEL,
        angle_deg,
    )


def monitor_location(kind, station_angle):
    if kind == "P":
        return station_angle, HUB_RADIUS + 145.0, 0.0, P_MONITOR_WIDTH
    if kind == "S":
        return (
            station_angle + 60.0,
            ARM_START + ARM_LENGTH * 0.42,
            lane_center_offset(-1.0),
            SIDE_MONITOR_WIDTH,
        )
    if kind == "T":
        return (
            station_angle - 60.0,
            ARM_START + ARM_LENGTH * 0.42,
            lane_center_offset(+1.0),
            SIDE_MONITOR_WIDTH,
        )
    raise ValueError("Unknown monitor kind: " + str(kind))


def vertical_bounding_envelope(shape, z_min, z_max):
    bb = shape.BoundBox
    return Part.makeBox(
        bb.XLength,
        bb.YLength,
        z_max - z_min,
        App.Vector(bb.XMin, bb.YMin, z_min),
    )


# =============================================================================
# DOCUMENT HELPERS
# =============================================================================

def set_style(obj, color, transparency=0, display_mode=None):
    """Styling is best-effort so headless FreeCAD builds remain valid."""
    try:
        obj.ViewObject.ShapeColor = color
        obj.ViewObject.LineColor = tuple(min(1.0, c * 0.72) for c in color)
        obj.ViewObject.Transparency = int(transparency)
        if display_mode:
            obj.ViewObject.DisplayMode = display_mode
    except Exception:
        pass


def set_visibility(obj, visible):
    try:
        obj.ViewObject.Visibility = bool(visible)
    except Exception:
        pass


def add_meta(obj, mode, station, function):
    for prop_name, value in (
        ("Mode", mode),
        ("Station", station),
        ("Function", function),
    ):
        try:
            obj.addProperty("App::PropertyString", prop_name, "Concept CAD")
            setattr(obj, prop_name, value)
        except Exception:
            pass


def add_feature(doc, group, shape, name, label, color, mode, station="", function="", transparency=0):
    obj = doc.addObject("Part::Feature", name)
    obj.Label = label
    obj.Shape = shape
    group.addObject(obj)
    add_meta(obj, mode, station, function)
    set_style(obj, color, transparency)
    return obj


def add_group(doc, parent, name, label):
    group = doc.addObject("App::DocumentObjectGroup", name)
    group.Label = label
    if parent is not None:
        parent.addObject(group)
    return group


def export_step(objects, filename):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, filename)
    exportable = []
    for obj in objects:
        try:
            if hasattr(obj, "Shape") and not obj.Shape.isNull():
                exportable.append(obj)
        except Exception:
            pass
    if not exportable:
        raise RuntimeError("No exportable shapes for " + filename)
    Part.export(exportable, path)
    App.Console.PrintMessage("STEP exported: %s\n" % path)
    return path


# =============================================================================
# BUILDERS
# =============================================================================

def build_static_structure(doc, group):
    objects = []

    objects.append(add_feature(
        doc, group,
        regular_polygon_prism(CORE_BASE_RADIUS, 6, CORE_BASE_HEIGHT, 0.0, 30.0),
        "CoreBase", "Central hexagonal base",
        COLORS["STRUCTURE"], "STATIC", function="central base",
    ))
    objects.append(add_feature(
        doc, group,
        triangle_prism(CORE_TRIANGLE_RADIUS, CORE_HEIGHT, CORE_BASE_HEIGHT, 90.0),
        "CoreTriangle", "Central triangular technical core",
        COLORS["STRUCTURE_2"], "STATIC", function="technical core",
    ))

    # Three floor rails make the support topology immediately legible.
    for arm_index, arm_angle in enumerate((60.0, 180.0, 300.0), 1):
        rail = local_box(
            FLOOR_RAIL_LENGTH,
            FLOOR_RAIL_WIDTH,
            FLOOR_RAIL_HEIGHT,
            HUB_RADIUS * 0.55,
            0.0,
            FOOT_HEIGHT,
            arm_angle,
        )
        objects.append(add_feature(
            doc, group, rail,
            "FloorRail_%d" % arm_index,
            "Floor rail %d" % arm_index,
            COLORS["STRUCTURE"], "STATIC", function="floor rail",
        ))

    # Nine controlled P/S/T units: base foot + fixed outer column.
    for station, station_angle in STATIONS:
        for kind in ("P", "S", "T"):
            x, y = desk_column_location(kind, station_angle)
            foot = cylinder_at(x, y, FOOT_DIAMETER, FOOT_HEIGHT, 0.0)
            outer = cylinder_at(x, y, COLUMN_OUTER_DIA, COLUMN_OUTER_HEIGHT, FOOT_HEIGHT)
            objects.append(add_feature(
                doc, group, foot,
                "%s_%s_Foot" % (station, kind),
                "%s/%s base foot" % (station, kind),
                COLORS["STRUCTURE"], "STATIC", station, "%s lift base" % kind,
            ))
            objects.append(add_feature(
                doc, group, outer,
                "%s_%s_ColumnOuter" % (station, kind),
                "%s/%s fixed column" % (station, kind),
                COLORS["STRUCTURE_2"], "STATIC", station, "%s outer column" % kind,
            ))

    return objects


def build_mode_desks(doc, group, mode, top_height, color_override=None, transparency=0):
    objects = []
    station_groups = {}
    for station, station_angle in STATIONS:
        station_group = add_group(
            doc, group,
            "%s_%s" % (mode, station),
            "%s - station %s" % (mode.replace("_", " ").title(), station),
        )
        station_groups[station] = station_group
        for kind in ("P", "S", "T"):
            color = color_override or COLORS[kind]
            objects.append(add_feature(
                doc, station_group,
                desk_shape(kind, station_angle, top_height),
                "%s_%s_%s_Desk" % (mode, station, kind),
                "%s/%s desk - %s" % (station, kind, mode),
                color, mode, station, "%s work plane" % kind, transparency,
            ))
            objects.append(add_feature(
                doc, station_group,
                column_inner_shape(kind, station_angle, top_height),
                "%s_%s_%s_ColumnInner" % (mode, station, kind),
                "%s/%s moving column - %s" % (station, kind, mode),
                COLORS["STRUCTURE_2"] if color_override is None else color_override,
                mode, station, "%s moving column" % kind, transparency,
            ))
    return objects, station_groups


def build_work_mode(doc, group):
    objects, station_groups = build_mode_desks(doc, group, "WORK", WORK_HEIGHT)

    # Nine real monitor placeholders. The three P monitors form the central triangle.
    for station, station_angle in STATIONS:
        station_group = station_groups[station]
        for kind in ("P", "S", "T"):
            angle, radius, offset, width = monitor_location(kind, station_angle)
            frame = monitor_frame_shape(angle, radius, offset, WORK_HEIGHT, width)
            display = monitor_display_shape(angle, radius, offset, WORK_HEIGHT, width)
            objects.append(add_feature(
                doc, station_group, frame,
                "WORK_%s_%s_MonitorBody" % (station, kind),
                "%s/%s monitor body" % (station, kind),
                COLORS["MONITOR"], "WORK", station, "%s monitor" % kind,
            ))
            objects.append(add_feature(
                doc, station_group, display,
                "WORK_%s_%s_MonitorDisplay" % (station, kind),
                "%s/%s display face" % (station, kind),
                COLORS["DISPLAY"], "WORK", station, "%s display" % kind,
            ))

    # Each physical arm owns one vertical party panel in work/hybrid position.
    for arm_index, arm_angle in enumerate((60.0, 180.0, 300.0), 1):
        panel = local_box(
            ARM_PARTY_COVER_LENGTH,
            PARTITION_THICKNESS,
            PARTITION_HEIGHT,
            ARM_PARTY_COVER_START,
            0.0,
            PARTY_HEIGHT,
            arm_angle,
        )
        objects.append(add_feature(
            doc, group, panel,
            "WORK_Arm%d_PartyPanelVertical" % arm_index,
            "Arm %d party panel - vertical/work position" % arm_index,
            COLORS["PARTY"], "WORK", function="vertical party/privacy panel",
        ))
    return objects


def build_party_mode(doc, group):
    objects, _ = build_mode_desks(doc, group, "PARTY", PARTY_HEIGHT)

    central_top = regular_polygon_prism(
        CENTRAL_PARTY_TOP_RADIUS,
        6,
        PARTY_COVER_THICKNESS,
        PARTY_HEIGHT,
        30.0,
    )
    objects.append(add_feature(
        doc, group, central_top,
        "PARTY_CentralHexTop",
        "Central hexagonal party top",
        COLORS["PARTY"], "PARTY", function="central monitor cover",
    ))

    for arm_index, arm_angle in enumerate((60.0, 180.0, 300.0), 1):
        cover = rounded_plate(
            ARM_PARTY_COVER_LENGTH,
            ARM_PARTY_COVER_WIDTH,
            PARTY_COVER_THICKNESS,
            ARM_PARTY_COVER_START,
            -ARM_PARTY_COVER_WIDTH / 2.0,
            PARTY_HEIGHT,
            70.0,
            arm_angle,
        )
        objects.append(add_feature(
            doc, group, cover,
            "PARTY_Arm%d_GapCover" % arm_index,
            "Arm %d party gap cover" % arm_index,
            COLORS["PARTY"], "PARTY", function="horizontal arm cover",
        ))
    return objects


def build_service_mode(doc, group):
    """Provisional service pose: desks high, monitors parked, covers vertical.

    This is deliberately a reference pose, not a verified motion sequence.
    """
    objects, _ = build_mode_desks(
        doc, group, "SERVICE", SERVICE_HEIGHT,
        color_override=COLORS["SERVICE"], transparency=25,
    )

    for arm_index, arm_angle in enumerate((60.0, 180.0, 300.0), 1):
        panel = local_box(
            ARM_PARTY_COVER_LENGTH,
            PARTITION_THICKNESS,
            PARTITION_HEIGHT,
            ARM_PARTY_COVER_START,
            0.0,
            PARTY_HEIGHT,
            arm_angle,
        )
        objects.append(add_feature(
            doc, group, panel,
            "SERVICE_Arm%d_PartyPanelStored" % arm_index,
            "Arm %d panel - stored for service" % arm_index,
            COLORS["SERVICE"], "SERVICE", function="stored party panel", transparency=25,
        ))
    return objects


def build_motion_envelopes(doc, group):
    objects = []
    for station, station_angle in STATIONS:
        for kind in ("P", "S", "T"):
            footprint = desk_shape(kind, station_angle, WORK_HEIGHT)
            env = vertical_bounding_envelope(footprint, COL_SW_MIN - DESK_THICKNESS, COL_SW_MAX)
            objects.append(add_feature(
                doc, group, env,
                "ENV_%s_%s_Desk" % (station, kind),
                "%s/%s desk full Z envelope" % (station, kind),
                COLORS["ENVELOPE"], "ENVELOPE", station, "%s desk travel" % kind, 82,
            ))

            angle, radius, offset, _ = monitor_location(kind, station_angle)
            x, y = polar_xy(radius, angle, offset)
            monitor_env = cylinder_at(
                x,
                y,
                MONITOR_LIFT_DIA + 35.0,
                (COL_SW_MAX + MONITOR_VIEW_RISE) - (COL_SW_MIN - MONITOR_PARK_DROP),
                COL_SW_MIN - MONITOR_PARK_DROP,
            )
            objects.append(add_feature(
                doc, group, monitor_env,
                "ENV_%s_%s_Monitor" % (station, kind),
                "%s/%s monitor lift envelope" % (station, kind),
                COLORS["DISPLAY"], "ENVELOPE", station, "%s monitor travel" % kind, 86,
            ))

    # Conservative bounding envelopes for lift -> rotate -> lower panel motion.
    for arm_index, arm_angle in enumerate((60.0, 180.0, 300.0), 1):
        vertical = local_box(
            ARM_PARTY_COVER_LENGTH,
            PARTITION_THICKNESS,
            PARTITION_HEIGHT,
            ARM_PARTY_COVER_START,
            0.0,
            PARTY_HEIGHT,
            arm_angle,
        )
        horizontal = rounded_plate(
            ARM_PARTY_COVER_LENGTH,
            ARM_PARTY_COVER_WIDTH,
            PARTY_COVER_THICKNESS,
            ARM_PARTY_COVER_START,
            -ARM_PARTY_COVER_WIDTH / 2.0,
            PARTY_HEIGHT,
            70.0,
            arm_angle,
        )
        fused = vertical.fuse(horizontal)
        bb = fused.BoundBox
        env = Part.makeBox(
            bb.XLength,
            bb.YLength,
            PARTITION_HEIGHT + 900.0,
            App.Vector(bb.XMin, bb.YMin, PARTY_HEIGHT - 50.0),
        )
        objects.append(add_feature(
            doc, group, env,
            "ENV_Arm%d_PartyPanel" % arm_index,
            "Arm %d party-panel conservative envelope" % arm_index,
            COLORS["PARTY"], "ENVELOPE", function="party panel sweep", transparency=86,
        ))
    return objects


def build_reference_chairs(doc, group):
    objects = []
    if not SHOW_REFERENCE_CHAIRS:
        return objects

    for station, station_angle in STATIONS:
        # A simple seat/back silhouette outside P gives the model an immediate scale cue.
        seat_radius = HUB_RADIUS + P_DEPTH + 420.0
        seat = local_box(420.0, 470.0, 65.0, seat_radius - 210.0, 0.0, 440.0, station_angle)
        back = local_box(70.0, 470.0, 620.0, seat_radius + 150.0, 0.0, 440.0, station_angle)
        objects.append(add_feature(
            doc, group, seat.fuse(back),
            "REF_%s_Chair" % station,
            "Station %s reference chair" % station,
            COLORS["REFERENCE"], "REFERENCE", station, "scale reference", transparency=55,
        ))
    return objects


def add_document_parameters(doc):
    params = doc.addObject("App::FeaturePython", "PARAMETERS")
    params.Label = "PARAMETERS - edit generator and regenerate"
    values = (
        ("ArmLength", ARM_LENGTH),
        ("ArmWidth", ARM_WIDTH),
        ("ShaftGap", SHAFT_GAP),
        ("HubRadius", HUB_RADIUS),
        ("PrimaryDepth", P_DEPTH),
        ("PrimaryWidth", P_WIDTH),
        ("WorkHeight", WORK_HEIGHT),
        ("PartyHeight", PARTY_HEIGHT),
        ("ServiceHeight", SERVICE_HEIGHT),
        ("SoftwareLiftMin", COL_SW_MIN),
        ("SoftwareLiftMax", COL_SW_MAX),
    )
    for name, value in values:
        params.addProperty("App::PropertyLength", name, "V2 dimensions")
        setattr(params, name, value)
    params.addProperty("App::PropertyString", "ModelStatus", "V2 metadata")
    params.ModelStatus = "Concept CAD - not manufacturing documentation"
    return params


def build_island():
    try:
        old = App.getDocument(DOCUMENT_NAME)
    except Exception:
        old = None
    if old is not None:
        App.closeDocument(DOCUMENT_NAME)
    doc = App.newDocument(DOCUMENT_NAME)

    params = add_document_parameters(doc)
    grp_structure = add_group(doc, None, "STRUCTURE", "00 - STATIC STRUCTURE")
    grp_work = add_group(doc, None, "WORK_MODE", "10 - WORK MODE (default)")
    grp_party = add_group(doc, None, "PARTY_MODE", "20 - PARTY MODE")
    grp_service = add_group(doc, None, "SERVICE_MODE", "30 - SERVICE MODE (provisional)")
    grp_reference = add_group(doc, None, "REFERENCE_GEOMETRY", "80 - REFERENCE / SCALE")
    grp_env = add_group(doc, None, "MOTION_ENVELOPES", "90 - MOTION ENVELOPES")

    static_objects = build_static_structure(doc, grp_structure)
    work_objects = build_work_mode(doc, grp_work)
    party_objects = build_party_mode(doc, grp_party)
    service_objects = build_service_mode(doc, grp_service)
    reference_objects = build_reference_chairs(doc, grp_reference)
    envelope_objects = build_motion_envelopes(doc, grp_env)

    doc.recompute()

    set_visibility(params, False)
    set_visibility(grp_structure, True)
    set_visibility(grp_work, True)
    set_visibility(grp_party, False)
    set_visibility(grp_service, False)
    set_visibility(grp_reference, True)
    set_visibility(grp_env, False)

    # Return explicit lists so STEP export never attempts to export groups.
    return {
        "doc": doc,
        "static": static_objects,
        "work": work_objects,
        "party": party_objects,
        "service": service_objects,
        "reference": reference_objects,
        "envelopes": envelope_objects,
    }


def main():
    App.Console.PrintMessage("Building multifunction island Concept CAD V2...\n")
    built = build_island()
    doc = built["doc"]
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    fcstd_path = os.path.join(OUTPUT_DIR, DOCUMENT_NAME + ".FCStd")
    doc.saveAs(fcstd_path)
    App.Console.PrintMessage("FCStd saved: %s\n" % fcstd_path)

    if CREATE_STEP_EXPORTS:
        export_step(
            built["static"] + built["work"],
            DOCUMENT_NAME + "_WORK.step",
        )
        export_step(
            built["static"] + built["party"],
            DOCUMENT_NAME + "_PARTY.step",
        )

    App.Console.PrintMessage(
        "Done. Open the FCStd file and toggle WORK/PARTY/SERVICE/ENVELOPES in the tree.\n"
    )


# FreeCADCmd commonly imports .py files as modules instead of assigning
# __name__ == '__main__'. This is an executable generator, so run explicitly at
# module load. It therefore works both as .py through FreeCADCmd and as .FCMacro.
main()
