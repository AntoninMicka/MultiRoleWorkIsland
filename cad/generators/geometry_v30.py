"""Pure plan geometry for the closed V2.3 worktops and M2/V3.0 party layer.

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
MONITOR_EDGE_WIDTH = 1100.0
PRIMARY_INNER_RADIUS = 640.0

# Shared arm envelope.  Each side desk stays on its side of the technical
# channel.  Its diagonal inner edge is derived from the primary/user zone.
ARM_OUTER_RADIUS = 1950.0
ARM_HALF_WIDTH = 800.0
TECH_CHANNEL_WIDTH = 400.0
SIDE_DESK_LENGTH = 1000.0

# User and display reference positions used to aim all monitors.  The primary
# lift sits behind the rear P edge; paired side lifts sit inside the 400 mm
# channel rather than passing through their S/T desk surfaces.
USER_RADIUS = PRIMARY_INNER_RADIUS + WORK_DEPTH + 450.0
PRIMARY_MONITOR_RADIUS = 400.0
SIDE_MONITOR_RADIUS = 780.0
SIDE_MONITOR_CHANNEL_OFFSET = 130.0
PRIMARY_MONITOR_WIDTH = 650.0
SIDE_MONITOR_WIDTH = 560.0
MONITOR_BODY_THICKNESS = 38.0
MONITOR_LIFT_RADIUS = 45.0
MONITOR_DESK_CLEARANCE = 20.0

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

# The central V3.0 module follows the front corners of all three P desks. Its
# three user-facing edges stay 800 mm wide; alternate edges are exact seams to
# the three arm modules.
CENTRAL_PARTY_RADIUS = 760.0  # retained historical reference, not V3.0 extent
CENTRAL_USER_EDGE = 800.0
PARTY_MODULE_THICKNESS = 40.0
PARTY_SURFACE_HEIGHT = 700.0


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
    """Return a side desk whose front and rear edges are exactly parallel."""
    arm_delta, _channel_edge, _outer_edge = _side_lane(kind)
    arm_angle = station_angle + arm_delta
    primary = primary_polygon(station_angle)
    if kind == "S":
        rear_start, front_start = primary[3], primary[2]
    else:
        rear_start, front_start = primary[0], primary[1]
    extension = local_to_world(SIDE_DESK_LENGTH, 0.0, arm_angle)
    rear_end = (rear_start[0] + extension[0], rear_start[1] + extension[1])
    front_end = (front_start[0] + extension[0], front_start[1] + extension[1])
    return (rear_start, rear_end, front_end, front_start)


def cross_product(vector_a, vector_b):
    return vector_a[0] * vector_b[1] - vector_a[1] * vector_b[0]


def edges_parallel(start_a, end_a, start_b, end_b, tolerance=1e-7):
    vector_a = (end_a[0] - start_a[0], end_a[1] - start_a[1])
    vector_b = (end_b[0] - start_b[0], end_b[1] - start_b[1])
    scale = max(1.0, distance((0.0, 0.0), vector_a) * distance((0.0, 0.0), vector_b))
    return abs(cross_product(vector_a, vector_b)) <= tolerance * scale


def desk_front_rear_edges(name, polygon):
    """Return the user-facing and rear edge pair for a P/S/T desk polygon."""
    if name[-1] == "P":
        return ((polygon[1], polygon[2]), (polygon[0], polygon[3]))
    return ((polygon[3], polygon[2]), (polygon[0], polygon[1]))


def nonparallel_desk_edges():
    failures = []
    for name, polygon in sorted(desk_polygons().items()):
        front, rear = desk_front_rear_edges(name, polygon)
        if not edges_parallel(front[0], front[1], rear[0], rear[1]):
            failures.append(name)
    return failures


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
    arm_delta, _channel_edge, _outer_edge = _side_lane(kind)
    channel_offset = -SIDE_MONITOR_CHANNEL_OFFSET if kind == "S" else SIDE_MONITOR_CHANNEL_OFFSET
    return local_to_world(
        SIDE_MONITOR_RADIUS,
        channel_offset,
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


def monitor_body_polygon(kind, station_angle):
    """Return the plan footprint of a monitor body in its WORK orientation."""
    center_x, center_y, facing = monitor_pose(kind, station_angle)
    width = PRIMARY_MONITOR_WIDTH if kind == "P" else SIDE_MONITOR_WIDTH
    half_depth = MONITOR_BODY_THICKNESS / 2.0
    half_width = width / 2.0
    local_corners = (
        (-half_depth, -half_width),
        (half_depth, -half_width),
        (half_depth, half_width),
        (-half_depth, half_width),
    )
    return tuple(
        (center_x + rotated[0], center_y + rotated[1])
        for rotated in (rotate_point(point, facing) for point in local_corners)
    )


def monitor_body_polygons():
    result = {}
    for station, angle in STATIONS:
        for kind in ("P", "S", "T"):
            result[station + kind] = monitor_body_polygon(kind, angle)
    return result


def _point_segment_distance(point, start, end):
    edge_x = end[0] - start[0]
    edge_y = end[1] - start[1]
    length_squared = edge_x * edge_x + edge_y * edge_y
    if length_squared == 0.0:
        return distance(point, start)
    projection = (
        (point[0] - start[0]) * edge_x + (point[1] - start[1]) * edge_y
    ) / length_squared
    projection = max(0.0, min(1.0, projection))
    closest = (start[0] + projection * edge_x, start[1] + projection * edge_y)
    return distance(point, closest)


def point_in_polygon(point, polygon):
    """Return whether a point lies inside a polygon (edge points count inside)."""
    inside = False
    x, y = point
    for start, end in polygon_edges(polygon):
        if _point_segment_distance(point, start, end) <= 1e-7:
            return True
        if (start[1] > y) != (end[1] > y):
            crossing_x = (end[0] - start[0]) * (y - start[1]) / (end[1] - start[1]) + start[0]
            if x < crossing_x:
                inside = not inside
    return inside


def point_polygon_clearance(point, polygon):
    if point_in_polygon(point, polygon):
        return 0.0
    return min(_point_segment_distance(point, start, end) for start, end in polygon_edges(polygon))


def polygon_clearance(polygon_a, polygon_b):
    if polygons_overlap(polygon_a, polygon_b):
        return 0.0
    distances = [
        _point_segment_distance(point, start, end)
        for point in polygon_a
        for start, end in polygon_edges(polygon_b)
    ]
    distances.extend(
        _point_segment_distance(point, start, end)
        for point in polygon_b
        for start, end in polygon_edges(polygon_a)
    )
    return min(distances)


def monitor_lift_desk_collisions():
    """Report monitor lift centers that violate desk clearance in plan."""
    desks = desk_polygons()
    collisions = []
    required = MONITOR_LIFT_RADIUS + MONITOR_DESK_CLEARANCE
    for station, station_angle in STATIONS:
        for kind in ("P", "S", "T"):
            x, y, _facing = monitor_pose(kind, station_angle)
            monitor_name = station + kind
            for desk_name, desk in sorted(desks.items()):
                clearance = point_polygon_clearance((x, y), desk)
                if clearance < required - 1e-7:
                    collisions.append((monitor_name, desk_name, clearance))
    return collisions


def monitor_body_desk_collisions():
    desks = desk_polygons()
    collisions = []
    for monitor_name, monitor in sorted(monitor_body_polygons().items()):
        for desk_name, desk in sorted(desks.items()):
            if polygons_overlap(monitor, desk):
                collisions.append((monitor_name, desk_name))
    return collisions


def monitor_body_collisions():
    return collision_pairs(monitor_body_polygons())


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
    """Return the central module covering the centre and all three P desks."""
    points = []
    for _station, station_angle in STATIONS:
        primary = primary_polygon(station_angle)
        points.extend((primary[1], primary[2]))
    return tuple(sorted(points, key=lambda point: math.atan2(point[1], point[0])))


def party_arm_dimensions():
    """Return the arm-module seam radius, length and half-width."""
    primary = primary_polygon(0.0)
    seam_corner = rotate_point(primary[2], -60.0)
    seam_radius = seam_corner[0]
    half_width = abs(seam_corner[1])
    return seam_radius, SIDE_DESK_LENGTH, half_width


def party_arm_polygon(arm_angle):
    seam_radius, length, half_width = party_arm_dimensions()
    local_points = (
        (seam_radius, -half_width),
        (seam_radius + length, -half_width),
        (seam_radius + length, half_width),
        (seam_radius, half_width),
    )
    return tuple(local_to_world(radial, tangential, arm_angle) for radial, tangential in local_points)


def party_module_polygons():
    result = {"CENTRAL_TOP": central_party_polygon()}
    for index, arm_angle in enumerate((60.0, 180.0, 300.0), 1):
        result["PARTY_ARM_%d" % index] = party_arm_polygon(arm_angle)
    return result


def _sample_quadrilateral(polygon, steps=12):
    """Sample a convex quadrilateral, including edges, by bilinear interpolation."""
    samples = []
    for row in range(steps + 1):
        v = row / float(steps)
        left = (
            polygon[0][0] * (1.0 - v) + polygon[3][0] * v,
            polygon[0][1] * (1.0 - v) + polygon[3][1] * v,
        )
        right = (
            polygon[1][0] * (1.0 - v) + polygon[2][0] * v,
            polygon[1][1] * (1.0 - v) + polygon[2][1] * v,
        )
        for column in range(steps + 1):
            u = column / float(steps)
            samples.append((
                left[0] * (1.0 - u) + right[0] * u,
                left[1] * (1.0 - u) + right[1] * u,
            ))
    return samples


def point_covered_by_party(point):
    return any(point_in_polygon(point, module) for module in party_module_polygons().values())


def party_coverage_failures():
    """Return sampled worktop/monitor points not covered by the party layer."""
    failures = []
    sources = {}
    sources.update(desk_polygons())
    sources.update(("MONITOR_" + name, polygon) for name, polygon in monitor_body_polygons().items())
    for name, polygon in sorted(sources.items()):
        samples = _sample_quadrilateral(polygon)
        uncovered = [point for point in samples if not point_covered_by_party(point)]
        if uncovered:
            failures.append((name, len(uncovered)))
    return failures


def party_seam_failures(tolerance=1e-6):
    """Verify every arm inner edge matches one complete central-module edge."""
    central_edges = list(polygon_edges(central_party_polygon()))
    failures = []
    for name, arm in sorted(party_module_polygons().items()):
        if name == "CENTRAL_TOP":
            continue
        arm_edge = (arm[3], arm[0])
        matched = False
        for central_edge in central_edges:
            direct = distance(arm_edge[0], central_edge[0]) + distance(arm_edge[1], central_edge[1])
            reverse = distance(arm_edge[0], central_edge[1]) + distance(arm_edge[1], central_edge[0])
            if min(direct, reverse) <= tolerance:
                matched = True
                break
        if not matched:
            failures.append(name)
    return failures


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
    lines.append(
        '<polygon id="central-party" points="%s" fill="#e8bd45" stroke-dasharray="8 5"/>'
        % point_list(central)
    )
    lines.append('<g fill="#18212a" fill-opacity="0.88" stroke="#05090c">')
    for name, monitor in sorted(monitor_body_polygons().items()):
        lines.append('<polygon id="monitor-%s" points="%s"/>' % (name, point_list(monitor)))
        center_x, center_y, _facing = monitor_pose(name[-1], dict(STATIONS)[name[0]])
        svg_x, svg_y = svg_point((center_x, center_y))
        lines.append(
            '<circle id="monitor-lift-%s" cx="%.2f" cy="%.2f" r="%.2f" fill="#dbe4ea"/>'
            % (name, svg_x, svg_y, MONITOR_LIFT_RADIUS * scale)
        )
    lines.append('</g>')
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


def svg_party_plan():
    """Return a dedicated top view of the four-module V3.0 party surface."""
    scale = 0.22
    origin = 500.0

    def svg_point(point):
        return (origin + point[0] * scale, origin - point[1] * scale)

    def point_list(polygon):
        return " ".join("%.2f,%.2f" % svg_point(point) for point in polygon)

    def centroid(polygon):
        return (
            sum(point[0] for point in polygon) / len(polygon),
            sum(point[1] for point in polygon) / len(polygon),
        )

    modules = party_module_polygons()
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1000" viewBox="0 0 1000 1000">',
        '<rect width="1000" height="1000" fill="#fafafa"/>',
        '<text x="500" y="35" text-anchor="middle" font-family="sans-serif" font-size="20" fill="#1d2730">V3.0 party surface — top 700 mm</text>',
        '<g fill="none" stroke="#94a0aa" stroke-width="1.2" stroke-dasharray="5 4">',
    ]
    for name, desk in sorted(desk_polygons().items()):
        lines.append('<polygon id="reference-desk-%s" points="%s"/>' % (name, point_list(desk)))
    lines.extend((
        '</g>',
        '<g fill="#e8bd45" fill-opacity="0.82" stroke="#25313b" stroke-width="2">',
    ))
    for name, module in sorted(modules.items()):
        lines.append('<polygon id="%s" points="%s"/>' % (name.lower(), point_list(module)))
    lines.append('</g>')
    lines.append('<g font-family="sans-serif" font-size="14" fill="#1d2730">')
    for name, module in sorted(modules.items()):
        label_x, label_y = svg_point(centroid(module))
        lines.append('<text x="%.2f" y="%.2f" text-anchor="middle">%s</text>' % (
            label_x, label_y, name.replace("_", " "),
        ))
    lines.extend((
        '<text x="500" y="970" text-anchor="middle">Dashed outline: covered V2.3 worktops · solid lines: module seams</text>',
        '</g>',
        '</svg>',
    ))
    return "\n".join(lines) + "\n"
