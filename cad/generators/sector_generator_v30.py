# -*- coding: utf-8 -*-
"""
MULTIFUNCTION WORK / PARTY ISLAND - PARTY LAYER CAD V3.0
=========================================================

Parametric FreeCAD generator for the complete three-station island.

Run headless (the file intentionally executes also when FreeCADCmd imports it):

    ./run.sh

or copy/rename it to ``sector_generator_v2.FCMacro`` and execute it as a macro.

Outputs (in the repository-root ``output_v30`` directory):

    island_concept_v30.FCStd
    island_concept_v30_WORK.step
    island_concept_v30_PARTY.step
    island_concept_v30_collision_report.json
    island_concept_v30_plan.svg
    island_concept_v30_party_plan.svg

The FCStd document contains independently switchable groups:

    00_STRUCTURE
    10_WORK_MODE       (visible by default)
    20_PARTY_MODE      (hidden by default)
    30_SERVICE_MODE    (hidden, provisional reference pose)
    90_MOTION_ENVELOPES (hidden by default)

V3.0 retains the closed V2.3 worktop layout and adds a continuous four-module
party layer: one central module covers the centre and P desks, while three arm
modules cover S/T pairs and their technical channels. All final party surfaces
are at 700 mm. Work mode shows the selected storage concept: arm modules stand
as channel-centred partitions and the central module parks overhead. Hinges,
locks and transformation kinematics remain open engineering work; this is not
manufacturing documentation.

Coordinate convention
---------------------
Station A faces the hub along angle 0 degrees. Stations B and C are rotated by
120 and 240 degrees. For each station:

* P is the central saddle desk.
* S occupies the clockwise/inner lane of the arm at station angle + 60 deg.
* T occupies the counter-clockwise/inner lane of the arm at station angle - 60 deg.

Consequently each physical arm contains two neighbouring station planes with a
300 mm central shaft. This corrects the left-lane sign ambiguity in V1.
"""

from __future__ import print_function

import math
import os
import json

import FreeCAD as App
import Part
import geometry_v30 as Geometry


# =============================================================================
# PARAMETERS - millimetres / degrees
# =============================================================================

DOCUMENT_NAME = "island_concept_v30"
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output_v30")

# Main plan geometry
ARM_LENGTH = 1500.0
ARM_WIDTH = 1600.0
SHAFT_GAP = Geometry.TECH_CHANNEL_WIDTH
HUB_RADIUS = 450.0
ARM_START = HUB_RADIUS

# P/S/T work planes
P_DEPTH = Geometry.WORK_DEPTH
P_WIDTH = Geometry.USER_EDGE_WIDTH
P_CORNER_RADIUS = 0.0
LANE_WIDTH = (ARM_WIDTH - SHAFT_GAP) / 2.0
DESK_THICKNESS = 40.0
DESK_CORNER_RADIUS = 90.0

# Nominal modes
WORK_HEIGHT = 750.0
PARTY_HEIGHT = Geometry.PARTY_SURFACE_HEIGHT
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
PARTY_COVER_THICKNESS = Geometry.PARTY_MODULE_THICKNESS
PARTY_SUPPORT_HEIGHT = PARTY_HEIGHT - PARTY_COVER_THICKNESS
PARTY_PARTITION_BOTTOM_HEIGHT = Geometry.PARTY_PARTITION_BOTTOM_HEIGHT
CENTRAL_PARTY_STORAGE_HEIGHT = Geometry.CENTRAL_PARTY_STORAGE_HEIGHT
PARTITION_HEIGHT = 720.0
PARTITION_THICKNESS = 40.0
CENTRAL_PARTY_TOP_RADIUS = Geometry.CENTRAL_PARTY_RADIUS

# Monitors - visual placeholders
P_MONITOR_WIDTH = Geometry.PRIMARY_MONITOR_WIDTH
SIDE_MONITOR_WIDTH = Geometry.SIDE_MONITOR_WIDTH
MONITOR_HEIGHT = 370.0
MONITOR_THICKNESS = 38.0
MONITOR_BEZEL = 18.0
MONITOR_BOTTOM_GAP = 95.0
MONITOR_PARK_DROP = 450.0
MONITOR_VIEW_RISE = 900.0
MONITOR_LIFT_DIA = Geometry.MONITOR_LIFT_RADIUS * 2.0

# Visual / export options
CREATE_STEP_EXPORTS = True
SHOW_REFERENCE_CHAIRS = True

COLORS = {
    "P": (0.25, 0.55, 0.88),       # blue
    "S": (0.24, 0.72, 0.55),       # green
    "T": (0.93, 0.55, 0.22),       # orange
    "PARTY": (0.92, 0.74, 0.27),   # gold
    "MECHANISM": (0.23, 0.31, 0.38),
    "LOCK": (0.82, 0.16, 0.14),
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


def oriented_box_center(length, width, height, center_x, center_y, z0, angle_deg, x0=None):
    """Create a box in a rotated frame and place its XY origin at a world point."""
    if x0 is None:
        x0 = -length / 2.0
    shape = Part.makeBox(
        length,
        width,
        height,
        App.Vector(x0, -width / 2.0, z0),
    )
    rotate_z(shape, angle_deg)
    shape.translate(App.Vector(center_x, center_y, 0.0))
    return shape


def polygon_prism(points, height, z0):
    """Extrude an ordered XY polygon into a plate."""
    vectors = [App.Vector(x, y, z0) for x, y in points]
    vectors.append(vectors[0])
    return Part.Face(Part.makePolygon(vectors)).extrude(App.Vector(0, 0, height))


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
        points = Geometry.primary_polygon(station_angle)
    elif kind in ("S", "T"):
        points = Geometry.side_polygon(kind, station_angle)
    else:
        raise ValueError("Unknown desk kind: " + str(kind))
    return polygon_prism(points, DESK_THICKNESS, z0)


def desk_column_location(kind, station_angle):
    if kind == "P":
        return Geometry.primary_column_position(station_angle)
    elif kind in ("S", "T"):
        points = Geometry.side_polygon(kind, station_angle)
    else:
        raise ValueError("Unknown desk kind: " + str(kind))
    return (
        sum(point[0] for point in points) / len(points),
        sum(point[1] for point in points) / len(points),
    )


def cylinder_at(x, y, diameter, height, z0):
    return Part.makeCylinder(
        diameter / 2.0,
        height,
        App.Vector(x, y, z0),
        App.Vector(0, 0, 1),
    )


def cylinder_between(start, end, diameter):
    direction = App.Vector(
        end[0] - start[0],
        end[1] - start[1],
        end[2] - start[2],
    )
    return Part.makeCylinder(
        diameter / 2.0,
        direction.Length,
        App.Vector(*start),
        direction,
    )


def column_inner_shape(kind, station_angle, top_height):
    x, y = desk_column_location(kind, station_angle)
    z0 = COLUMN_OUTER_HEIGHT * 0.70
    height = max(20.0, top_height - DESK_THICKNESS - z0)
    return cylinder_at(x, y, COLUMN_INNER_DIA, height, z0)


def monitor_frame_shape(angle_deg, center_x, center_y, lift_x, lift_y, desk_top, width):
    bottom = desk_top + MONITOR_BOTTOM_GAP
    body = oriented_box_center(
        MONITOR_THICKNESS,
        width,
        MONITOR_HEIGHT,
        center_x,
        center_y,
        bottom,
        angle_deg,
    )
    support = cylinder_at(
        lift_x,
        lift_y,
        MONITOR_LIFT_DIA,
        MONITOR_BOTTOM_GAP,
        desk_top,
    )
    return body.fuse(support)


def monitor_display_shape(angle_deg, center_x, center_y, desk_top, width):
    """Thin coloured front face on the outward side of the monitor body."""
    face_thickness = 3.0
    return oriented_box_center(
        face_thickness,
        width - 2.0 * MONITOR_BEZEL,
        MONITOR_HEIGHT - 2.0 * MONITOR_BEZEL,
        center_x,
        center_y,
        desk_top + MONITOR_BOTTOM_GAP + MONITOR_BEZEL,
        angle_deg,
        x0=MONITOR_THICKNESS / 2.0,
    )


def monitor_location(kind, station_angle):
    center_x, center_y, facing_angle = Geometry.monitor_pose(kind, station_angle)
    width = P_MONITOR_WIDTH if kind == "P" else SIDE_MONITOR_WIDTH
    return facing_angle, center_x, center_y, width


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


def build_party_mechanisms(doc, group):
    """Build review geometry for the selected M2 guides, axes and locks."""
    objects = []
    for arm_index, arm_angle in enumerate((60.0, 180.0, 300.0), 1):
        spec = Geometry.party_arm_mechanism(arm_angle)
        for guide_index, (x, y) in enumerate(spec["guide_points"], 1):
            guide = cylinder_at(
                x,
                y,
                Geometry.PARTY_GUIDE_DIAMETER,
                spec["lift_travel"],
                spec["party_axis_z"],
            )
            objects.append(add_feature(
                doc, group, guide,
                "MECH_Arm%d_Guide%d" % (arm_index, guide_index),
                "Arm %d synchronized vertical guide %d" % (arm_index, guide_index),
                COLORS["MECHANISM"], "MECHANISM",
                function="party arm vertical guide", transparency=20,
            ))
            stored_lock = cylinder_at(
                x,
                y,
                Geometry.PARTY_GUIDE_DIAMETER + 20.0,
                Geometry.PARTY_LOCK_PIN_DIAMETER,
                spec["stored_axis_z"] - Geometry.PARTY_LOCK_PIN_DIAMETER / 2.0,
            )
            objects.append(add_feature(
                doc, group, stored_lock,
                "MECH_Arm%d_StoredLock%d" % (arm_index, guide_index),
                "Arm %d stored-position lock %d - POSITION plus LOCK sensing" % (
                    arm_index, guide_index,
                ),
                COLORS["LOCK"], "MECHANISM",
                function="party arm stored mechanical lock",
            ))
        start_x, start_y = spec["axis_start"]
        end_x, end_y = spec["axis_end"]
        axis = cylinder_between(
            (start_x, start_y, spec["stored_axis_z"]),
            (end_x, end_y, spec["stored_axis_z"]),
            Geometry.PARTY_ARM_AXIS_DIAMETER,
        )
        objects.append(add_feature(
            doc, group, axis,
            "MECH_Arm%d_RotationAxis" % arm_index,
            "Arm %d longitudinal rotation axis" % arm_index,
            COLORS["MECHANISM"], "MECHANISM",
            function="party arm rotation axis",
        ))
        for lock_index, (x, y) in enumerate(spec["party_lock_points"], 1):
            lock = cylinder_at(
                x, y, Geometry.PARTY_LOCK_PIN_DIAMETER,
                PARTY_COVER_THICKNESS, PARTY_SUPPORT_HEIGHT,
            )
            objects.append(add_feature(
                doc, group, lock,
                "MECH_Arm%d_PartyLock%d" % (arm_index, lock_index),
                "Arm %d Party lock %d - POSITION plus LOCK sensing" % (
                    arm_index, lock_index,
                ),
                COLORS["LOCK"], "MECHANISM",
                function="party arm mechanical lock",
            ))

    central = Geometry.central_party_mechanism()
    for guide_index, (x, y) in enumerate(central["guide_points"], 1):
        guide = cylinder_at(
            x,
            y,
            Geometry.PARTY_GUIDE_DIAMETER,
            central["lift_travel"],
            central["party_center_z"],
        )
        objects.append(add_feature(
            doc, group, guide,
            "MECH_CentralGuide%d" % guide_index,
            "Central module synchronized telescopic guide %d" % guide_index,
            COLORS["MECHANISM"], "MECHANISM",
            function="central party vertical guide", transparency=20,
        ))
        stored_lock = cylinder_at(
            x,
            y,
            Geometry.PARTY_GUIDE_DIAMETER + 20.0,
            Geometry.PARTY_LOCK_PIN_DIAMETER,
            central["stored_center_z"] - Geometry.PARTY_LOCK_PIN_DIAMETER / 2.0,
        )
        objects.append(add_feature(
            doc, group, stored_lock,
            "MECH_CentralStoredLock%d" % guide_index,
            "Central stored-position lock %d - POSITION plus LOCK sensing" % guide_index,
            COLORS["LOCK"], "MECHANISM",
            function="central stored mechanical lock",
        ))
        lock = cylinder_at(
            x, y, Geometry.PARTY_LOCK_PIN_DIAMETER,
            PARTY_COVER_THICKNESS, PARTY_SUPPORT_HEIGHT,
        )
        objects.append(add_feature(
            doc, group, lock,
            "MECH_CentralPartyLock%d" % guide_index,
            "Central Party lock %d - POSITION plus LOCK sensing" % guide_index,
            COLORS["LOCK"], "MECHANISM",
            function="central party mechanical lock",
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
            angle, center_x, center_y, width = monitor_location(kind, station_angle)
            lift_x, lift_y = Geometry.monitor_lift_position(kind, station_angle)
            frame = monitor_frame_shape(
                angle, center_x, center_y, lift_x, lift_y, WORK_HEIGHT, width
            )
            display = monitor_display_shape(angle, center_x, center_y, WORK_HEIGHT, width)
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

    # Provisional M2 storage poses. Each rectangular arm module keeps its exact
    # dimensions and stands longitudinally in the technical channel. The
    # central module remains horizontal above the complete monitor zone.
    central_storage = polygon_prism(
        Geometry.central_party_polygon(),
        PARTY_COVER_THICKNESS,
        CENTRAL_PARTY_STORAGE_HEIGHT,
    )
    objects.append(add_feature(
        doc, group, central_storage,
        "WORK_PARTY_CentralStored",
        "Central party module - overhead storage",
        COLORS["PARTY"], "WORK", function="party storage module", transparency=35,
    ))
    seam_radius, arm_length, arm_half_width = Geometry.party_arm_dimensions()
    for arm_index, arm_angle in enumerate((60.0, 180.0, 300.0), 1):
        partition = local_box(
            arm_length,
            PARTY_COVER_THICKNESS,
            arm_half_width * 2.0,
            seam_radius,
            0.0,
            PARTY_PARTITION_BOTTOM_HEIGHT,
            arm_angle,
        )
        objects.append(add_feature(
            doc, group, partition,
            "WORK_PARTY_Arm%d_Stored" % arm_index,
            "Arm %d party module - vertical partition" % arm_index,
            COLORS["PARTY"], "WORK", function="party storage module", transparency=18,
        ))
    return objects


def build_party_mode(doc, group):
    objects, _ = build_mode_desks(doc, group, "PARTY", PARTY_SUPPORT_HEIGHT)

    central_top = polygon_prism(
        Geometry.central_party_polygon(),
        PARTY_COVER_THICKNESS,
        PARTY_HEIGHT - PARTY_COVER_THICKNESS,
    )
    objects.append(add_feature(
        doc, group, central_top,
        "PARTY_CentralTop",
        "Central party surface module",
        COLORS["PARTY"], "PARTY", function="party surface module",
    ))

    for arm_index, arm_angle in enumerate((60.0, 180.0, 300.0), 1):
        cover = polygon_prism(
            Geometry.party_arm_polygon(arm_angle),
            PARTY_COVER_THICKNESS,
            PARTY_HEIGHT - PARTY_COVER_THICKNESS,
        )
        objects.append(add_feature(
            doc, group, cover,
            "PARTY_Arm%d_Surface" % arm_index,
            "Arm %d party surface module" % arm_index,
            COLORS["PARTY"], "PARTY", function="party surface module",
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

    # Party-module storage is intentionally absent until the M2 kinematic
    # concept defines hinges/guides, locks and a recoverable intermediate pose.
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

            x, y = Geometry.monitor_lift_position(kind, station_angle)
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

    # Exact party-module sweeps replace the old conservative boxes only after
    # storage poses and hinge/guide axes are selected.
    return objects


def build_reference_chairs(doc, group):
    objects = []
    if not SHOW_REFERENCE_CHAIRS:
        return objects

    for station, station_angle in STATIONS:
        # A simple seat/back silhouette outside P gives the model an immediate scale cue.
        seat_radius = Geometry.USER_RADIUS
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
    party_seam_radius, party_arm_length, party_arm_half_width = Geometry.party_arm_dimensions()
    values = (
        ("ArmLength", ARM_LENGTH),
        ("ArmWidth", ARM_WIDTH),
        ("ShaftGap", SHAFT_GAP),
        ("HubRadius", HUB_RADIUS),
        ("UsableWorkDepth", Geometry.WORK_DEPTH),
        ("UserEdgeWidth", Geometry.USER_EDGE_WIDTH),
        ("MonitorEdgeWidth", Geometry.MONITOR_EDGE_WIDTH),
        ("PrimaryInnerRadius", Geometry.PRIMARY_INNER_RADIUS),
        ("PartyArmSeamRadius", party_seam_radius),
        ("PartyArmLength", party_arm_length),
        ("PartyArmWidth", party_arm_half_width * 2.0),
        ("WorkHeight", WORK_HEIGHT),
        ("PartySurfaceHeight", PARTY_HEIGHT),
        ("PartySupportHeight", PARTY_SUPPORT_HEIGHT),
        ("PartyPartitionBottomHeight", PARTY_PARTITION_BOTTOM_HEIGHT),
        ("CentralPartyStorageHeight", CENTRAL_PARTY_STORAGE_HEIGHT),
        ("PartyArmAxisDiameter", Geometry.PARTY_ARM_AXIS_DIAMETER),
        ("PartyGuideDiameter", Geometry.PARTY_GUIDE_DIAMETER),
        ("PartyLockPinDiameter", Geometry.PARTY_LOCK_PIN_DIAMETER),
        ("CentralPartyGuideRadius", Geometry.CENTRAL_PARTY_GUIDE_RADIUS),
        ("ServiceHeight", SERVICE_HEIGHT),
        ("SoftwareLiftMin", COL_SW_MIN),
        ("SoftwareLiftMax", COL_SW_MAX),
    )
    for name, value in values:
        params.addProperty("App::PropertyLength", name, "V3.0 dimensions")
        setattr(params, name, value)
    params.addProperty("App::PropertyString", "ModelStatus", "V3.0 metadata")
    params.ModelStatus = "Party storage poses selected - transformation kinematics not yet validated"
    return params


def cad_desk_collision_pairs(work_objects):
    """Check positive-volume intersections between generated WORK desk solids."""
    desks = []
    for obj in work_objects:
        try:
            if obj.Function.endswith("work plane"):
                desks.append(obj)
        except Exception:
            pass
    collisions = []
    for index, desk_a in enumerate(desks):
        for desk_b in desks[index + 1:]:
            common = desk_a.Shape.common(desk_b.Shape)
            if not common.isNull() and common.Volume > 1e-6:
                collisions.append((desk_a.Name, desk_b.Name, common.Volume))
    return collisions


def cad_party_storage_collision_pairs(work_objects):
    """Check stored party solids against Work desks and monitor bodies."""
    stored = []
    obstacles = []
    for obj in work_objects:
        try:
            if obj.Function == "party storage module":
                stored.append(obj)
            elif obj.Function.endswith("work plane") or obj.Function.endswith("monitor"):
                obstacles.append(obj)
        except Exception:
            pass
    collisions = []
    for module in stored:
        for obstacle in obstacles:
            common = module.Shape.common(obstacle.Shape)
            if not common.isNull() and common.Volume > 1e-6:
                collisions.append((module.Name, obstacle.Name, common.Volume))
    return collisions


def write_design_reports(cad_collisions, storage_collisions):
    """Write reviewable plan and collision evidence next to CAD artifacts."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    plan_collisions = Geometry.collision_pairs()
    nonparallel_desk_edges = Geometry.nonparallel_desk_edges()
    technical_channel_edge_failures = Geometry.technical_channel_edge_failures()
    side_lift_channel_clearance = (
        Geometry.TECH_CHANNEL_WIDTH / 2.0
        - Geometry.SIDE_LIFT_CHANNEL_OFFSET
        - Geometry.MONITOR_LIFT_RADIUS
    )
    monitor_lift_desk_collisions = Geometry.monitor_lift_desk_collisions()
    monitor_body_desk_collisions = Geometry.monitor_body_desk_collisions()
    monitor_body_collisions = Geometry.monitor_body_collisions()
    party_modules = Geometry.party_module_polygons()
    party_module_collisions = Geometry.collision_pairs(party_modules)
    party_coverage_failures = Geometry.party_coverage_failures()
    party_seam_failures = Geometry.party_seam_failures()
    party_height_valid = (
        PARTY_HEIGHT == Geometry.PARTY_SURFACE_HEIGHT
        and PARTY_SUPPORT_HEIGHT + PARTY_COVER_THICKNESS == PARTY_HEIGHT
    )
    frame_gaps = {}
    gap_violations = []
    for station, station_angle in STATIONS:
        primary = Geometry.monitor_body_polygon("P", station_angle)
        for kind in ("S", "T"):
            gap = Geometry.polygon_clearance(
                primary, Geometry.monitor_body_polygon(kind, station_angle)
            )
            name = "%sP-%s%s" % (station, station, kind)
            frame_gaps[name] = round(gap, 6)
            if not 20.0 <= gap <= 40.0:
                gap_violations.append((name, gap))
    failed = any((
        plan_collisions,
        nonparallel_desk_edges,
        technical_channel_edge_failures,
        side_lift_channel_clearance < 0.0,
        cad_collisions,
        storage_collisions,
        monitor_lift_desk_collisions,
        monitor_body_desk_collisions,
        monitor_body_collisions,
        party_module_collisions,
        party_coverage_failures,
        party_seam_failures,
        gap_violations,
        not party_height_valid,
    ))
    report = {
        "model": DOCUMENT_NAME,
        "units": "mm",
        "status": "fail" if failed else "pass",
        "layout": "monitors behind desk edges and inside technical channels",
        "desk_count": len(Geometry.desk_polygons()),
        "nonparallel_desk_edges": nonparallel_desk_edges,
        "technical_channel_edge_failures": technical_channel_edge_failures,
        "plan_collisions": [list(pair) for pair in plan_collisions],
        "cad_collisions": [
            {"desk_a": item[0], "desk_b": item[1], "volume": item[2]}
            for item in cad_collisions
        ],
        "party_storage": {
            "concept": "vertical arm partitions plus overhead central module",
            "arm_count": 3,
            "arm_z_range": list(Geometry.party_storage_ranges()["arm"]),
            "central_z_range": list(Geometry.party_storage_ranges()["central"]),
            "static_collisions": [
                {"module": item[0], "obstacle": item[1], "volume": item[2]}
                for item in storage_collisions
            ],
            "static_pose_status": "pass" if not storage_collisions else "fail",
            "kinematic_validation_status": "open",
        },
        "party_mechanisms": {
            "arm_concept": "two synchronized vertical carriages plus longitudinal 90 degree axis",
            "central_concept": "three synchronized telescopic vertical guides without rotation",
            "arm_axis_diameter": Geometry.PARTY_ARM_AXIS_DIAMETER,
            "guide_diameter": Geometry.PARTY_GUIDE_DIAMETER,
            "lock_pin_diameter": Geometry.PARTY_LOCK_PIN_DIAMETER,
            "arm_lift_travel": Geometry.party_arm_mechanism(60.0)["lift_travel"],
            "central_lift_travel": Geometry.central_party_mechanism()["lift_travel"],
            "party_lock_count_per_arm": 4,
            "stored_lock_count_per_arm": 2,
            "central_party_lock_count": 3,
            "position_confirmation": "independent position sensor required",
            "lock_confirmation": "independent lock sensor required",
            "load_validation_status": "open",
            "motion_validation_status": "open",
        },
        "monitor_lift_desk_collisions": [list(item) for item in monitor_lift_desk_collisions],
        "monitor_body_desk_collisions": [list(item) for item in monitor_body_desk_collisions],
        "monitor_body_collisions": [list(item) for item in monitor_body_collisions],
        "party_layer": {
            "module_count": len(party_modules),
            "module_names": sorted(party_modules),
            "module_collisions": [list(item) for item in party_module_collisions],
            "coverage_failures": [list(item) for item in party_coverage_failures],
            "seam_failures": party_seam_failures,
            "surface_height": PARTY_HEIGHT,
            "support_height": PARTY_SUPPORT_HEIGHT,
            "thickness": PARTY_COVER_THICKNESS,
            "height_valid": party_height_valid,
            "storage_pose_status": "concept-selected",
            "kinematic_validation_status": "open",
        },
        "adjacent_frame_gaps": frame_gaps,
        "frame_gap_violations": [list(item) for item in gap_violations],
        "parameters": {
            "user_edge_width": Geometry.USER_EDGE_WIDTH,
            "usable_work_depth": Geometry.WORK_DEPTH,
            "technical_channel_width": Geometry.TECH_CHANNEL_WIDTH,
            "side_desk_length": Geometry.SIDE_DESK_LENGTH,
            "side_desk_width": Geometry.SIDE_DESK_WIDTH,
            "side_lift_channel_edge_clearance": side_lift_channel_clearance,
            "central_user_edge": Geometry.CENTRAL_USER_EDGE,
            "primary_rear_edge_width": Geometry.MONITOR_EDGE_WIDTH,
            "monitor_frame_gap_min": 20.0,
            "monitor_frame_gap_max": 40.0,
        },
        "ergonomics": {
            "chair_width": Geometry.CHAIR_WIDTH,
            "chair_depth": Geometry.CHAIR_DEPTH,
            "legroom_depth": Geometry.PRIMARY_LEGROOM_DEPTH,
            "legroom_width": Geometry.PRIMARY_LEGROOM_WIDTH,
            "primary_column_legroom_clearance": Geometry.primary_column_legroom_clearance(),
            "entry_corridor_width": Geometry.ENTRY_CORRIDOR_WIDTH,
        },
        "monitor_poses": {},
    }
    for station, station_angle in STATIONS:
        for kind in ("P", "S", "T"):
            x, y, facing = Geometry.monitor_pose(kind, station_angle)
            report["monitor_poses"][station + kind] = {
                "x": round(x, 6),
                "y": round(y, 6),
                "facing_angle": round(facing, 6),
            }
        review = Geometry.monitor_review(station_angle)
        for kind in ("P", "S", "T"):
            report["monitor_poses"][station + kind].update({
                "viewing_distance": round(review[kind]["distance"], 6),
                "sight_angle": round(review[kind]["sight_angle"], 6),
                "half_angular_span": round(review[kind]["half_angular_span"], 6),
            })

    report_path = os.path.join(OUTPUT_DIR, DOCUMENT_NAME + "_collision_report.json")
    with open(report_path, "w", encoding="utf-8") as report_file:
        json.dump(report, report_file, indent=2, sort_keys=True)
        report_file.write("\n")

    plan_path = os.path.join(OUTPUT_DIR, DOCUMENT_NAME + "_plan.svg")
    with open(plan_path, "w", encoding="utf-8") as plan_file:
        plan_file.write(Geometry.svg_plan())

    party_plan_path = os.path.join(OUTPUT_DIR, DOCUMENT_NAME + "_party_plan.svg")
    with open(party_plan_path, "w", encoding="utf-8") as party_plan_file:
        party_plan_file.write(Geometry.svg_party_plan())

    App.Console.PrintMessage("Collision report: %s\n" % report_path)
    App.Console.PrintMessage("Dimensioned plan: %s\n" % plan_path)
    App.Console.PrintMessage("Party module plan: %s\n" % party_plan_path)
    if failed:
        raise RuntimeError(
            "V3.0 validation failed; see %s" % report_path
        )


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
    grp_mechanisms = add_group(doc, None, "PARTY_MECHANISMS", "05 - PARTY GUIDES / AXES / LOCKS")
    grp_work = add_group(doc, None, "WORK_MODE", "10 - WORK MODE (default)")
    grp_party = add_group(doc, None, "PARTY_MODE", "20 - PARTY MODE")
    grp_service = add_group(doc, None, "SERVICE_MODE", "30 - SERVICE MODE (provisional)")
    grp_reference = add_group(doc, None, "REFERENCE_GEOMETRY", "80 - REFERENCE / SCALE")
    grp_env = add_group(doc, None, "MOTION_ENVELOPES", "90 - MOTION ENVELOPES")

    static_objects = build_static_structure(doc, grp_structure)
    mechanism_objects = build_party_mechanisms(doc, grp_mechanisms)
    work_objects = build_work_mode(doc, grp_work)
    party_objects = build_party_mode(doc, grp_party)
    service_objects = build_service_mode(doc, grp_service)
    reference_objects = build_reference_chairs(doc, grp_reference)
    envelope_objects = build_motion_envelopes(doc, grp_env)

    doc.recompute()

    set_visibility(params, False)
    set_visibility(grp_structure, True)
    set_visibility(grp_mechanisms, False)
    set_visibility(grp_work, True)
    set_visibility(grp_party, False)
    set_visibility(grp_service, False)
    set_visibility(grp_reference, True)
    set_visibility(grp_env, False)

    # Return explicit lists so STEP export never attempts to export groups.
    return {
        "doc": doc,
        "static": static_objects,
        "mechanisms": mechanism_objects,
        "work": work_objects,
        "party": party_objects,
        "service": service_objects,
        "reference": reference_objects,
        "envelopes": envelope_objects,
    }


def main():
    App.Console.PrintMessage("Building multifunction island party-layer CAD V3.0...\n")
    built = build_island()
    doc = built["doc"]
    write_design_reports(
        cad_desk_collision_pairs(built["work"]),
        cad_party_storage_collision_pairs(built["work"]),
    )
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
