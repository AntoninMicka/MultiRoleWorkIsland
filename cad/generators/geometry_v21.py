"""Pure plan-geometry calculations for the MultiRoleWorkIsland V2.1 study.

The module intentionally has no FreeCAD dependency.  It is the executable
geometry contract for the ergonomic plan and can therefore be checked in CI.
All dimensions are millimetres and all angles are degrees.
"""

from __future__ import division

import math


STATIONS = (("A", 0.0), ("B", 120.0), ("C", 240.0))

# Primary desk: the user-facing edge and usable monitor-to-user depth are the
# two controlling dimensions required by M1.
USER_EDGE_WIDTH = 800.0
WORK_DEPTH = 550.0
MONITOR_EDGE_WIDTH = 700.0
PRIMARY_INNER_RADIUS = 640.0

# Shared arm envelope.  Each side desk stays on its side of the technical
# channel.  Its diagonal inner edge is derived from the primary/user zone.
ARM_OUTER_RADIUS = 1950.0
ARM_HALF_WIDTH = 800.0
TECH_CHANNEL_WIDTH = 400.0
SIDE_INNER_AT_CHANNEL = 700.0
SIDE_INNER_AT_OUTER = 980.0

# User and display reference positions used to aim all monitors.
USER_RADIUS = PRIMARY_INNER_RADIUS + WORK_DEPTH + 450.0
PRIMARY_MONITOR_RADIUS = PRIMARY_INNER_RADIUS + 55.0
SIDE_MONITOR_RADIUS = 1120.0
PRIMARY_MONITOR_WIDTH = 650.0
SIDE_MONITOR_WIDTH = 560.0

# Ergonomic reference zones.  They are design checks, not a substitute for a
# physical mock-up with users of different body sizes.
CHAIR_WIDTH = 470.0
CHAIR_DEPTH = 420.0
PRIMARY_LEGROOM_DEPTH = 400.0
PRIMARY_LEGROOM_WIDTH = 600.0
PRIMARY_COLUMN_RADIUS = PRIMARY_INNER_RADIUS + 70.0
LIFT_COLUMN_OUTER_RADIUS = 57.5
ENTRY_CORRIDOR_WIDTH = USER_EDGE_WIDTH
ENTRY_CORRIDOR_OUTER_RADIUS = USER_RADIUS + 700.0

# The central party outline has three 800 mm user-facing edges and three
# shorter joining edges.  Equal-radius, non-uniform angular spacing gives true
# threefold symmetry without degenerating into a regular hexagon.
CENTRAL_PARTY_RADIUS = 760.0
CENTRAL_USER_EDGE = 800.0


def _radians(angle_deg):
    return math.radians(angle_deg)


def rotate_point(point, angle_deg):
    """Rotate an XY point around the origin."""
    angle = _radians(angle_deg)
    cosine = math.cos(angle)
    sine = math.sin(angle)
    x, y = point
    return (x * cosine - y * sine, x * sine + y * cosine)


def local_to_world(radial, tangential, angle_deg):
    """Convert a station/arm-local radial+tangential point to world XY."""
    return rotate_point((radial, tangential), angle_deg)


def distance(point_a, point_b):
    return math.hypot(point_b[0] - point_a[0], point_b[1] - point_a[1])


def midpoint(point_a, point_b):
    return ((point_a[0] + point_b[0]) / 2.0, (point_a[1] + point_b[1]) / 2.0)


def primary_polygon(station_angle):
    """Return the primary trapezoid, ordered around its perimeter.

    The inner edge follows the primary monitor.  The outer 800 mm edge faces
    the user, and the distance between their midpoints is exactly WORK_DEPTH.
    """
    inner_half = MONITOR_EDGE_WIDTH / 2.0
    user_half = USER_EDGE_WIDTH / 2.0
    outer_radius = PRIMARY_INNER_RADIUS + WORK_DEPTH
    local_points = (
        (PRIMARY_INNER_RADIUS, -inner_half),
        (outer_radius, -user_half),
        (outer_radius, user_half),
        (PRIMARY_INNER_RADIUS, inner_half),
    )
    return tuple(rotate_point(point, station_angle) for point in local_points)


def _side_lane(kind):
    channel_half = TECH_CHANNEL_WIDTH / 2.0
    if kind == "S":
        return (60.0, -channel_half, -ARM_HALF_WIDTH)
    if kind == "T":
        return (-60.0, channel_half, ARM_HALF_WIDTH)
    raise ValueError("Side desk kind must be S or T: %s" % kind)


def side_polygon(kind, station_angle):
    """Return a side-desk polygon clipped away from the primary user zone."""
    arm_delta, channel_edge, outer_edge = _side_lane(kind)
    arm_angle = station_angle + arm_delta
    local_points = (
        (SIDE_INNER_AT_CHANNEL, channel_edge),
        (ARM_OUTER_RADIUS, channel_edge),
        (ARM_OUTER_RADIUS, outer_edge),
        (SIDE_INNER_AT_OUTER, outer_edge),
    )
    return tuple(local_to_world(radial, tangential, arm_angle) for radial, tangential in local_points)


def desk_polygons():
    """Return all nine P/S/T plan polygons keyed by station and role."""
    result = {}
    for station, angle in STATIONS:
        result[station + "P"] = primary_polygon(angle)
        result[station + "S"] = side_polygon("S", angle)
        result[station + "T"] = side_polygon("T", angle)
    return result


def _radial_rectangle(inner_radius, outer_radius, width, station_angle):
    half_width = width / 2.0
    points = (
        (inner_radius, -half_width),
        (outer_radius, -half_width),
        (outer_radius, half_width),
        (inner_radius, half_width),
    )
    return tuple(rotate_point(point, station_angle) for point in points)


def chair_polygon(station_angle):
    """Return the reference chair footprint centered on the seated user."""
    return _radial_rectangle(
        USER_RADIUS - CHAIR_DEPTH / 2.0,
        USER_RADIUS + CHAIR_DEPTH / 2.0,
        CHAIR_WIDTH,
        station_angle,
    )


def legroom_polygon(station_angle):
    """Return the unobstructed under-desk target zone in front of the user."""
    desk_outer = PRIMARY_INNER_RADIUS + WORK_DEPTH
    return _radial_rectangle(
        desk_outer - PRIMARY_LEGROOM_DEPTH,
        desk_outer,
        PRIMARY_LEGROOM_WIDTH,
        station_angle,
    )


def entry_corridor_polygon(station_angle):
    """Return a straight approach/exit corridor outside the primary desk."""
    desk_outer = PRIMARY_INNER_RADIUS + WORK_DEPTH
    return _radial_rectangle(
        desk_outer,
        ENTRY_CORRIDOR_OUTER_RADIUS,
        ENTRY_CORRIDOR_WIDTH,
        station_angle,
    )


def primary_column_position(station_angle):
    return local_to_world(PRIMARY_COLUMN_RADIUS, 0.0, station_angle)


def primary_column_legroom_clearance():
    """Radial clearance between the lift column and the legroom target zone."""
    legroom_inner = PRIMARY_INNER_RADIUS + WORK_DEPTH - PRIMARY_LEGROOM_DEPTH
    return legroom_inner - (PRIMARY_COLUMN_RADIUS + LIFT_COLUMN_OUTER_RADIUS)


def polygon_edges(polygon):
    for index, point in enumerate(polygon):
        yield point, polygon[(index + 1) % len(polygon)]


def _projection(polygon, axis):
    values = [point[0] * axis[0] + point[1] * axis[1] for point in polygon]
    return min(values), max(values)


def polygons_overlap(polygon_a, polygon_b, tolerance=1e-7):
    """Return True only for positive-area overlap of two convex polygons."""
    for polygon in (polygon_a, polygon_b):
        for start, end in polygon_edges(polygon):
            axis = (-(end[1] - start[1]), end[0] - start[0])
            a_min, a_max = _projection(polygon_a, axis)
            b_min, b_max = _projection(polygon_b, axis)
            if min(a_max, b_max) - max(a_min, b_min) <= tolerance:
                return False
    return True


def collision_pairs(polygons=None):
    """Return sorted desk-name pairs whose plan polygons overlap."""
    polygons = polygons or desk_polygons()
    names = sorted(polygons)
    collisions = []
    for index, name_a in enumerate(names):
        for name_b in names[index + 1:]:
            if polygons_overlap(polygons[name_a], polygons[name_b]):
                collisions.append((name_a, name_b))
    return collisions


def user_position(station_angle):
    return local_to_world(USER_RADIUS, 0.0, station_angle)


def _side_monitor_center(kind, station_angle):
    arm_delta, channel_edge, outer_edge = _side_lane(kind)
    return local_to_world(
        SIDE_MONITOR_RADIUS,
        (channel_edge + outer_edge) / 2.0,
        station_angle + arm_delta,
    )


def monitor_pose(kind, station_angle):
    """Return ``(x, y, facing_angle)`` with the display aimed at its user."""
    if kind == "P":
        center = local_to_world(PRIMARY_MONITOR_RADIUS, 0.0, station_angle)
    elif kind in ("S", "T"):
        center = _side_monitor_center(kind, station_angle)
    else:
        raise ValueError("Unknown monitor kind: %s" % kind)
    user = user_position(station_angle)
    facing = math.degrees(math.atan2(user[1] - center[1], user[0] - center[0]))
    return center[0], center[1], facing


def monitor_review(station_angle):
    """Return viewing distance and horizontal sight interval for each monitor."""
    user = user_position(station_angle)
    result = {}
    for kind in ("P", "S", "T"):
        x, y, facing = monitor_pose(kind, station_angle)
        viewing_distance = distance(user, (x, y))
        width = PRIMARY_MONITOR_WIDTH if kind == "P" else SIDE_MONITOR_WIDTH
        sight_angle = math.degrees(math.atan2(y - user[1], x - user[0]))
        half_span = math.degrees(math.atan2(width / 2.0, viewing_distance))
        result[kind] = {
            "distance": viewing_distance,
            "facing_angle": facing,
            "sight_angle": sight_angle,
            "half_angular_span": half_span,
        }
    return result


def angular_separation(angle_a, angle_b):
    return abs((angle_a - angle_b + 180.0) % 360.0 - 180.0)


def central_party_polygon():
    """Return the threefold-symmetric, non-regular central six-edge outline."""
    half_face_angle = math.degrees(
        math.asin(CENTRAL_USER_EDGE / (2.0 * CENTRAL_PARTY_RADIUS))
    )
    points = []
    for _station, station_angle in STATIONS:
        for angle in (station_angle - half_face_angle, station_angle + half_face_angle):
            points.append(local_to_world(CENTRAL_PARTY_RADIUS, 0.0, angle))
    return tuple(sorted(points, key=lambda point: math.atan2(point[1], point[0])))


def svg_plan():
    """Return a self-contained, dimensioned SVG plan for design review."""
    polygons = desk_polygons()
    central = central_party_polygon()
    scale = 0.22
    origin = 500.0

    def svg_point(point):
        return (origin + point[0] * scale, origin - point[1] * scale)

    def point_list(polygon):
        return " ".join("%.2f,%.2f" % svg_point(point) for point in polygon)

    colors = {"P": "#3f8dd3", "S": "#3db889", "T": "#ed8b35"}
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1000" viewBox="0 0 1000 1000">',
        '<rect width="1000" height="1000" fill="#fafafa"/>',
        '<g stroke="#25313b" stroke-width="1.5" fill-opacity="0.60">',
    ]
    for name in sorted(polygons):
        lines.append('<polygon id="desk-%s" points="%s" fill="%s"/>' % (
            name, point_list(polygons[name]), colors[name[-1]],
        ))
    lines.append('<g fill="none" stroke="#6b7280" stroke-dasharray="5 4">')
    for station, station_angle in STATIONS:
        lines.append('<polygon id="chair-%s" points="%s"/>' % (
            station, point_list(chair_polygon(station_angle)),
        ))
        lines.append('<polygon id="entry-%s" points="%s"/>' % (
            station, point_list(entry_corridor_polygon(station_angle)),
        ))
    lines.append('</g>')
    lines.extend((
        '<polygon id="central-party" points="%s" fill="#e8bd45" stroke-dasharray="8 5"/>' % point_list(central),
        '</g>',
        '<g font-family="sans-serif" font-size="15" fill="#1d2730" stroke="#1d2730" stroke-width="1">',
        '<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f"/>' % (
            svg_point((-USER_EDGE_WIDTH / 2.0, PRIMARY_INNER_RADIUS + WORK_DEPTH + 90.0))
            + svg_point((USER_EDGE_WIDTH / 2.0, PRIMARY_INNER_RADIUS + WORK_DEPTH + 90.0))
        ),
        '<text x="500" y="250" text-anchor="middle" stroke="none">user edge 800 mm</text>',
        '<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f"/>' % (
            svg_point((0.0, PRIMARY_INNER_RADIUS)) + svg_point((0.0, PRIMARY_INNER_RADIUS + WORK_DEPTH))
        ),
        '<text x="520" y="300" stroke="none">usable depth 550 mm</text>',
        '<text x="500" y="495" text-anchor="middle" stroke="none">technical channel 400 mm</text>',
        '</g>',
        '</svg>',
    ))
    return "\n".join(lines) + "\n"
