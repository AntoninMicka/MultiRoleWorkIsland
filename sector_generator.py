# -*- coding: utf-8 -*-
"""
MULTIFUNKCNI OSTROV - 120° SECTOR GENERATOR
=============================================
Parametric FreeCAD macro. Run inside FreeCAD (Macro -> Execute, or the
Python console: exec(open('sector_generator.py').read())), or headless:

    freecadcmd sector_generator.py

Produces:
    output/sector_A.FCStd   - editable FreeCAD document, organized into groups
    output/sector_A.step    - STEP export of everything (one 120° wedge)
    output/island_full.step - optional full 3x mirrored preview (see BUILD_FULL_ASSEMBLY)

SCOPE OF THIS PASS
-------------------
Skeleton + motion envelopes only. Work surfaces, party panel, and central
core are represented as simplified flat plates / boxes / pie-wedges at their
NOMINAL reference positions (one solid per state: WORK_MODE, PARTY_MODE),
plus separate MOTION_ENVELOPES solids showing the full swept Z-range of
each moving part, so collisions between independently-moving elements can
be checked visually before any furniture-grade detailing is done.

COORDINATE / TILING CONVENTION
-------------------------------
One workstation = one user sitting in a "saddle" between two arms, facing
the center. This script builds ONE such wedge, spanning local angle -60°
to +60°, with:
    - the user's saddle / Primary desk (P) centered on local angle 0°
      (local +X axis), user faces -X (toward center)
    - the "right" shared arm centered on local angle +60° -> this wedge
      contributes its Secondary (S) desk = the INNER lane of that arm
      (the lane closest to angle 0, i.e. closest to this wedge's own saddle)
    - the "left" shared arm centered on local angle -60° -> this wedge
      contributes its Tertiary (T) desk = the INNER lane of that arm

Rotating this whole wedge by +120° and -120° and taking the union tiles
the full 360° island: each arm then automatically receives its OTHER lane
(S or T) from the neighboring wedge, because that neighbor's own "inner
lane toward its own saddle" lands exactly on the outer lane of THIS arm.
The party panel for each arm is only generated on the +60° edge of a wedge,
so a full 3x tiling yields exactly 3 panels (one per arm), not 6.

Verify this tiling assumption once you have FreeCAD open (set
BUILD_FULL_ASSEMBLY = True below) before doing anything else.
"""

import os
import math

import FreeCAD as App
import Part

# =========================================================================
# PARAMETERS (all mm / degrees) - edit these, nothing else should need to
# change for a basic re-tune.
# =========================================================================

# --- Overall geometry -----------------------------------------------------
SECTOR_ANGLE        = 120.0     # degrees, fixed by 3-fold symmetry
ARM_LENGTH          = 1500.0    # arm length from hub edge to arm tip (spec: 150 cm)
ARM_WIDTH           = 1600.0    # arm tangential width (spec: 160 cm)
SHAFT_GAP           = 400.0     # gap between S and T lanes within one arm (spec: ~40 cm)
HUB_RADIUS          = 450.0     # radius of central hub / structural core

# --- Primary (saddle) desk -------------------------------------------------
SADDLE_DEPTH         = 850.0    # radial depth of P worksurface
SADDLE_WIDTH         = 1300.0   # tangential width of P worksurface (at hub edge)
SADDLE_FILLET        = 150.0    # corner rounding hint (not yet applied as real fillet, see NOTES)

# --- Work surfaces (general) ----------------------------------------------
DESK_THK             = 40.0     # worksurface plate thickness

# --- Lifting columns (per surface) -----------------------------------------
COL_DIA              = 90.0     # column envelope diameter (simplified single-column stand-in)
COL_STROKE_PHYS_MIN  = 300.0    # physical column minimum extended height
COL_STROKE_PHYS_MAX  = 2000.0   # physical column maximum extended height
COL_SW_OFFSET        = 400.0    # software offset -> physical 300-2000 reported as 700-2400
COL_SW_MIN           = COL_STROKE_PHYS_MIN + COL_SW_OFFSET   # = 700  (software floor coordinate)
COL_SW_MAX           = COL_STROKE_PHYS_MAX + COL_SW_OFFSET   # = 2400 (software ceiling coordinate)

# --- Party layer ------------------------------------------------------------
PARTY_HEIGHT          = 700.0   # reference social/party worksurface height (spec)
PARTY_PANEL_THK        = 40.0
PARTY_PANEL_HEIGHT     = 750.0  # standing height of vertical work-mode privacy panel
PARTY_PANEL_LIFT_TRAVEL = 900.0 # extra Z envelope for telescopic lift+rotate motion

# --- Central core / hex party top ------------------------------------------
CORE_HEIGHT           = 750.0   # static structural triangular core height (top = mounting deck)
HEX_RADIUS            = HUB_RADIUS + 50.0   # party hex third radius (covers primary monitor triangle)

# --- Monitor lift envelopes --------------------------------------------------
MONITOR_PARK_DROP     = 450.0   # how far below desk top the monitor retracts (parking depth)
MONITOR_VIEW_RISE     = 900.0   # how far above desk top the monitor can rise for viewing
MONITOR_ENVELOPE_DIA  = 120.0   # simplified monitor lift carriage envelope diameter

# --- Assembly preview --------------------------------------------------------
BUILD_FULL_ASSEMBLY  = False    # set True to also generate the 3x-mirrored full island preview

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")


# =========================================================================
# HELPERS
# =========================================================================

def half_arm_box(arm_angle_deg, lane_sign, length, width, gap, x_offset, thickness, z):
    """
    Build the INNER half-lane of a shared arm.
    arm_angle_deg : centerline angle of the arm (e.g. +60 or -60)
    lane_sign     : -1 = inner lane (toward this wedge's own saddle at angle 0)
                     +1 = outer lane (belongs to the neighboring wedge - not normally used here)
    Box is built in the pre-rotation frame (arm along +X) then rotated into place.
    """
    lane_w = (width - gap) / 2.0
    lane_center_offset = lane_sign * (gap / 2.0 + lane_w / 2.0)
    box = Part.makeBox(
        length, lane_w, thickness,
        App.Vector(x_offset, lane_center_offset - lane_w / 2.0, z)
    )
    box.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), arm_angle_deg)
    return box


def column_at(arm_angle_deg, lane_sign, radial_pos, width, gap, z_bottom, z_top, dia=COL_DIA):
    """Simplified single-cylinder stand-in for a lifting column, placed under the
    centroid of a given lane at a given radial position along an arm (or 0 for P)."""
    lane_w = (width - gap) / 2.0 if width else 0.0
    lane_center_offset = lane_sign * (gap / 2.0 + lane_w / 2.0) if width else 0.0
    a = math.radians(arm_angle_deg)
    x = radial_pos * math.cos(a) - lane_center_offset * math.sin(a)
    y = radial_pos * math.sin(a) + lane_center_offset * math.cos(a)
    cyl = Part.makeCylinder(dia / 2.0, z_top - z_bottom, App.Vector(x, y, z_bottom), App.Vector(0, 0, 1))
    return cyl


def pie_wedge(radius, height, z, center_angle_deg, span_deg=SECTOR_ANGLE):
    """120°-wide pie slice (partial cylinder), centered on center_angle_deg."""
    wedge = Part.makeCylinder(radius, height, App.Vector(0, 0, z), App.Vector(0, 0, 1), span_deg)
    wedge.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), center_angle_deg - span_deg / 2.0)
    return wedge


def vertical_envelope(footprint_shape, z_bottom, z_top):
    """Turn a flat footprint solid into a tall envelope by re-extruding its
    outer face profile from z_bottom to z_top. Simplified: reuse the same
    2D footprint (project via bounding box) rather than true silhouette."""
    bb = footprint_shape.BoundBox
    box = Part.makeBox(
        bb.XLength, bb.YLength, z_top - z_bottom,
        App.Vector(bb.XMin, bb.YMin, z_bottom)
    )
    return box


# =========================================================================
# BUILD ONE SECTOR
# =========================================================================

def build_sector(doc_name="sector_A", rotation_deg=0.0):
    doc = App.newDocument(doc_name)

    grp_work = doc.addObject("App::DocumentObjectGroup", "WORK_MODE")
    grp_party = doc.addObject("App::DocumentObjectGroup", "PARTY_MODE")
    grp_env = doc.addObject("App::DocumentObjectGroup", "MOTION_ENVELOPES")
    grp_core = doc.addObject("App::DocumentObjectGroup", "STRUCTURE_CORE")

    def add(shape, name, group, rotate_final=True):
        if rotate_final and rotation_deg:
            shape.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), rotation_deg)
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        group.addObject(obj)
        return obj

    # ---- WORK MODE -------------------------------------------------------
    # Primary (P) desk - saddle worksurface, nominal WORK height
    p_desk = Part.makeBox(
        SADDLE_DEPTH, SADDLE_WIDTH, DESK_THK,
        App.Vector(HUB_RADIUS, -SADDLE_WIDTH / 2.0, COL_SW_MIN + 50.0)
    )
    add(p_desk, "P_Desk", grp_work)

    p_col = column_at(0.0, 0, HUB_RADIUS + SADDLE_DEPTH / 2.0, 0, 0, 0.0, COL_SW_MIN + 50.0)
    add(p_col, "P_Column", grp_work)

    # Secondary (S) desk = inner lane of the +60 deg arm
    s_desk = half_arm_box(+60.0, -1, ARM_LENGTH, ARM_WIDTH, SHAFT_GAP, HUB_RADIUS, DESK_THK, COL_SW_MIN + 50.0)
    add(s_desk, "S_HalfArm_Desk", grp_work)
    s_col = column_at(+60.0, -1, HUB_RADIUS + ARM_LENGTH / 2.0, ARM_WIDTH, SHAFT_GAP, 0.0, COL_SW_MIN + 50.0)
    add(s_col, "S_Column", grp_work)

    # Tertiary (T) desk = inner lane of the -60 deg arm
    t_desk = half_arm_box(-60.0, -1, ARM_LENGTH, ARM_WIDTH, SHAFT_GAP, HUB_RADIUS, DESK_THK, COL_SW_MIN + 50.0)
    add(t_desk, "T_HalfArm_Desk", grp_work)
    t_col = column_at(-60.0, -1, HUB_RADIUS + ARM_LENGTH / 2.0, ARM_WIDTH, SHAFT_GAP, 0.0, COL_SW_MIN + 50.0)
    add(t_col, "T_Column", grp_work)

    # Party panel - WORK-mode state: standing vertical, in the shaft of the +60 arm only
    # (so a full 3x tiling produces exactly 3 panels, one per arm - see module docstring)
    panel_len = ARM_LENGTH * 0.6   # panel covers the middle portion of the shaft, not full arm length
    panel_x0 = HUB_RADIUS + ARM_LENGTH * 0.2
    panel_work = Part.makeBox(
        panel_len, PARTY_PANEL_THK, PARTY_PANEL_HEIGHT,
        App.Vector(panel_x0, -PARTY_PANEL_THK / 2.0, PARTY_HEIGHT)
    )
    panel_work.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 60.0)
    add(panel_work, "PartyPanel_AB_WORK_state", grp_work)

    # Monitor lift envelopes (parked-to-viewing Z travel), one per desk, WORK snapshot
    # shown at mid-travel for reference; full range captured in MOTION_ENVELOPES below
    for name, ang, lane, r in [
        ("P_Monitor", 0.0, 0, HUB_RADIUS + SADDLE_DEPTH * 0.7),
        ("S_Monitor", 60.0, -1, HUB_RADIUS + ARM_LENGTH * 0.5),
        ("T_Monitor", -60.0, -1, HUB_RADIUS + ARM_LENGTH * 0.5),
    ]:
        mon = column_at(ang, lane, r, ARM_WIDTH if lane else 0, SHAFT_GAP if lane else 0,
                         COL_SW_MIN + 50.0 + DESK_THK, COL_SW_MIN + 50.0 + DESK_THK + 400.0,
                         dia=MONITOR_ENVELOPE_DIA)
        add(mon, name + "_nominal", grp_work)

    # ---- PARTY MODE --------------------------------------------------------
    # Party panel - PARTY-mode state: flipped flat, bridging the shaft gap
    panel_party = Part.makeBox(
        panel_len, SHAFT_GAP + 2 * PARTY_PANEL_THK, DESK_THK,
        App.Vector(panel_x0, -(SHAFT_GAP / 2.0 + PARTY_PANEL_THK), PARTY_HEIGHT)
    )
    panel_party.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 60.0)
    add(panel_party, "PartyPanel_AB_PARTY_state", grp_party)

    # Central hex party-top third (covers the primary monitor triangle in party mode)
    hex_third = pie_wedge(HEX_RADIUS, DESK_THK, PARTY_HEIGHT, center_angle_deg=0.0)
    add(hex_third, "CentralHex_Third_PARTY", grp_party)

    # ---- STRUCTURE (static) -------------------------------------------------
    core_third = pie_wedge(HUB_RADIUS, CORE_HEIGHT, 0.0, center_angle_deg=0.0)
    add(core_third, "CentralCore_Third_STATIC", grp_core)

    # ---- MOTION ENVELOPES ----------------------------------------------------
    add(vertical_envelope(p_desk, COL_SW_MIN, COL_SW_MAX), "P_Desk_ENVELOPE", grp_env)
    add(vertical_envelope(s_desk, COL_SW_MIN, COL_SW_MAX), "S_HalfArm_ENVELOPE", grp_env)
    add(vertical_envelope(t_desk, COL_SW_MIN, COL_SW_MAX), "T_HalfArm_ENVELOPE", grp_env)

    # Party panel envelope: bounding union of its WORK (vertical) and PARTY (horizontal)
    # states plus lift travel margin - represents the full Lift->Rotate->Lower sweep
    panel_env = panel_work.fuse(panel_party)
    panel_env_bb = panel_env.BoundBox
    panel_env_box = Part.makeBox(
        panel_env_bb.XLength, panel_env_bb.YLength,
        panel_env_bb.ZLength + PARTY_PANEL_LIFT_TRAVEL,
        App.Vector(panel_env_bb.XMin, panel_env_bb.YMin, PARTY_HEIGHT - 50.0)
    )
    add(panel_env_box, "PartyPanel_AB_ENVELOPE", grp_env)

    # Monitor full-travel envelopes (park depth below desk to full view rise above)
    for name, ang, lane, r in [
        ("P_Monitor", 0.0, 0, HUB_RADIUS + SADDLE_DEPTH * 0.7),
        ("S_Monitor", 60.0, -1, HUB_RADIUS + ARM_LENGTH * 0.5),
        ("T_Monitor", -60.0, -1, HUB_RADIUS + ARM_LENGTH * 0.5),
    ]:
        mon_env = column_at(
            ang, lane, r, ARM_WIDTH if lane else 0, SHAFT_GAP if lane else 0,
            COL_SW_MIN - MONITOR_PARK_DROP, COL_SW_MAX + MONITOR_VIEW_RISE,
            dia=MONITOR_ENVELOPE_DIA
        )
        add(mon_env, name + "_ENVELOPE", grp_env)

    doc.recompute()
    return doc


# =========================================================================
# EXPORT
# =========================================================================

def export_step(doc, filename):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, filename)
    objs = [o for o in doc.Objects if hasattr(o, "Shape")]
    Part.export(objs, path)
    print("STEP exported:", path)
    return path


if __name__ == "__main__":
    doc = build_sector("sector_A", rotation_deg=0.0)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    doc.saveAs(os.path.join(OUTPUT_DIR, "sector_A.FCStd"))
    export_step(doc, "sector_A.step")

    if BUILD_FULL_ASSEMBLY:
        doc_b = build_sector("sector_B", rotation_deg=120.0)
        doc_c = build_sector("sector_C", rotation_deg=240.0)
        # Merge all shapes into one compound doc for a full-island preview export
        full = App.newDocument("island_full")
        all_shapes = []
        for d in (doc, doc_b, doc_c):
            for o in d.Objects:
                if hasattr(o, "Shape"):
                    all_shapes.append(o.Shape)
        compound = Part.makeCompound(all_shapes)
        preview = full.addObject("Part::Feature", "IslandPreview")
        preview.Shape = compound
        full.recompute()
        export_step(full, "island_full.step")
        full.saveAs(os.path.join(OUTPUT_DIR, "island_full.FCStd"))

    print("Done.")
