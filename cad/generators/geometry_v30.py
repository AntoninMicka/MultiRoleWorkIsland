"""Pure plan geometry for the closed V2.3 worktops and M2/V3.0 party layer.

The module intentionally has no FreeCAD dependency.  It is the executable
geometry contract for the ergonomic plan and can therefore be checked in CI.
All dimensions are millimetres and all angles are degrees.
"""

from __future__ import division

import math

try:
    from . import design_parameters as DesignParameters
except ImportError:  # Direct execution from the FreeCAD generator directory.
    import design_parameters as DesignParameters


STATIONS = (("A", 0.0), ("B", 120.0), ("C", 240.0))

# Fixed study references. Editable values are loaded from
# config/design_parameters.toml through apply_parameters() below.
ARM_OUTER_RADIUS = 1950.0
ARM_HALF_WIDTH = 800.0
CHAIR_WIDTH = 470.0
CHAIR_DEPTH = 420.0
PRIMARY_REAR_SUPPORT_ZONE_DEPTH = 150.0
PRIMARY_LEGROOM_WIDTH = 600.0
LIFT_COLUMN_OUTER_RADIUS = 57.5
CENTRAL_PARTY_RADIUS = 760.0  # retained historical reference, not V3.0 extent
CENTRAL_USER_EDGE = 800.0


def apply_parameters(parameters):
    """Apply validated independent inputs and recalculate every dependency."""
    values = DesignParameters.normalize_parameters(parameters)
    errors = DesignParameters.validate_parameters(values)
    if errors:
        raise ValueError("Invalid design parameters:\n- " + "\n- ".join(errors))

    global PARAMETERS
    global USER_EDGE_WIDTH, WORK_DEPTH, MONITOR_EDGE_WIDTH, PRIMARY_INNER_RADIUS
    global TECH_CHANNEL_WIDTH, SIDE_DESK_LENGTH, SIDE_DESK_WIDTH, USER_RADIUS
    global PRIMARY_MONITOR_RADIUS, SIDE_MONITOR_RADIUS, SIDE_MONITOR_CHANNEL_OFFSET
    global SIDE_LIFT_RADIUS, SIDE_LIFT_CHANNEL_OFFSET
    global PRIMARY_MONITOR_WIDTH, SIDE_MONITOR_WIDTH, MONITOR_BODY_THICKNESS
    global MONITOR_LIFT_RADIUS, MONITOR_DESK_CLEARANCE
    global PRIMARY_LEGROOM_DEPTH, PRIMARY_COLUMN_RADIUS
    global ENTRY_CORRIDOR_WIDTH, ENTRY_CORRIDOR_OUTER_RADIUS
    global PARTY_MODULE_THICKNESS, PARTY_SURFACE_HEIGHT
    global PARTY_PARTITION_BOTTOM_HEIGHT, PARTY_STORAGE_VERTICAL_CLEARANCE
    global CENTRAL_PARTY_STORAGE_HEIGHT
    global PARTY_ARM_AXIS_DIAMETER, PARTY_GUIDE_DIAMETER
    global PARTY_LOCK_PIN_DIAMETER, CENTRAL_PARTY_GUIDE_RADIUS

    PARAMETERS = dict(values)
    USER_EDGE_WIDTH = values["user_edge_width"]
    WORK_DEPTH = values["primary_depth"]
    TECH_CHANNEL_WIDTH = values["technical_channel_width"]
    SIDE_DESK_LENGTH = values["side_desk_length"]
    SIDE_DESK_WIDTH = WORK_DEPTH
    arm_sine = math.sin(math.radians(60.0))
    arm_cosine = math.cos(math.radians(60.0))
    primary_outer_radius = (
        TECH_CHANNEL_WIDTH / 2.0 + WORK_DEPTH + USER_EDGE_WIDTH / 4.0
    ) / arm_sine
    PRIMARY_INNER_RADIUS = primary_outer_radius - WORK_DEPTH
    rear_half_width = (
        arm_sine * PRIMARY_INNER_RADIUS - TECH_CHANNEL_WIDTH / 2.0
    ) / arm_cosine
    MONITOR_EDGE_WIDTH = 2.0 * rear_half_width
    USER_RADIUS = PRIMARY_INNER_RADIUS + WORK_DEPTH + values["user_clearance"]
    PRIMARY_MONITOR_RADIUS = values["primary_monitor_radius"]
    SIDE_MONITOR_RADIUS = values["side_monitor_radius"]
    SIDE_MONITOR_CHANNEL_OFFSET = values["side_monitor_offset"]
    SIDE_LIFT_RADIUS = values["side_lift_radius"]
    SIDE_LIFT_CHANNEL_OFFSET = values["side_lift_offset"]
    PRIMARY_MONITOR_WIDTH = values["primary_monitor_width"]
    SIDE_MONITOR_WIDTH = values["side_monitor_width"]
    MONITOR_BODY_THICKNESS = values["monitor_body_thickness"]
    MONITOR_LIFT_RADIUS = values["monitor_lift_diameter"] / 2.0
    MONITOR_DESK_CLEARANCE = values["monitor_desk_clearance"]
    PRIMARY_LEGROOM_DEPTH = WORK_DEPTH - PRIMARY_REAR_SUPPORT_ZONE_DEPTH
    PRIMARY_COLUMN_RADIUS = PRIMARY_INNER_RADIUS + 70.0
    ENTRY_CORRIDOR_WIDTH = USER_EDGE_WIDTH
    ENTRY_CORRIDOR_OUTER_RADIUS = USER_RADIUS + 700.0
    PARTY_MODULE_THICKNESS = values["party_module_thickness"]
    PARTY_SURFACE_HEIGHT = values["party_surface_height"]
    PARTY_PARTITION_BOTTOM_HEIGHT = values["party_partition_bottom_height"]
    PARTY_STORAGE_VERTICAL_CLEARANCE = values["party_storage_vertical_clearance"]
    CENTRAL_PARTY_STORAGE_HEIGHT = (
        PARTY_PARTITION_BOTTOM_HEIGHT
        + TECH_CHANNEL_WIDTH
        + 2.0 * WORK_DEPTH
        + PARTY_STORAGE_VERTICAL_CLEARANCE
    )
    PARTY_ARM_AXIS_DIAMETER = values["party_arm_axis_diameter"]
    PARTY_GUIDE_DIAMETER = values["party_guide_diameter"]
    PARTY_LOCK_PIN_DIAMETER = values["party_lock_pin_diameter"]
    CENTRAL_PARTY_GUIDE_RADIUS = values["central_party_guide_radius"]
    return dict(values)


apply_parameters(DesignParameters.load_parameters())


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
        return (60.0, -channel_half, -(channel_half + SIDE_DESK_WIDTH))
    if kind == "T":
        return (-60.0, channel_half, channel_half + SIDE_DESK_WIDTH)
    raise ValueError("Side desk kind must be S or T: %s" % kind)


def side_polygon(kind, station_angle):
    """Extrude the complete P side so P and S/T join without a transition."""
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


def technical_channel_edge_failures(tolerance=1e-7):
    """Return side desks whose inner edge does not bound the target channel."""
    failures = []
    for station, station_angle in STATIONS:
        for kind in ("S", "T"):
            arm_delta, channel_edge, _outer_edge = _side_lane(kind)
            polygon = side_polygon(kind, station_angle)
            for point in polygon[0:2]:
                local = rotate_point(point, -(station_angle + arm_delta))
                if abs(local[1] - channel_edge) > tolerance:
                    failures.append(station + kind)
                    break
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


def _side_lift_center(kind, station_angle):
    arm_delta, _channel_edge, _outer_edge = _side_lane(kind)
    channel_offset = -SIDE_LIFT_CHANNEL_OFFSET if kind == "S" else SIDE_LIFT_CHANNEL_OFFSET
    return local_to_world(
        SIDE_LIFT_RADIUS,
        channel_offset,
        station_angle + arm_delta,
    )


def monitor_lift_position(kind, station_angle):
    """Return the fixed lift axis; S/T bodies translate from it in WORK."""
    if kind == "P":
        return local_to_world(PRIMARY_MONITOR_RADIUS, 0.0, station_angle)
    if kind in ("S", "T"):
        return _side_lift_center(kind, station_angle)
    raise ValueError("Unknown monitor kind: %s" % kind)


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
            x, y = monitor_lift_position(kind, station_angle)
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


def party_storage_arm_polygon(arm_angle):
    """Return the Work-mode footprint of an arm module standing in the channel."""
    seam_radius, length, _half_width = party_arm_dimensions()
    half_thickness = PARTY_MODULE_THICKNESS / 2.0
    local_points = (
        (seam_radius, -half_thickness),
        (seam_radius + length, -half_thickness),
        (seam_radius + length, half_thickness),
        (seam_radius, half_thickness),
    )
    return tuple(local_to_world(x, y, arm_angle) for x, y in local_points)


def party_storage_ranges():
    """Return exact Z ranges for the provisional Work-mode storage poses."""
    _seam_radius, _length, half_width = party_arm_dimensions()
    partition_height = 2.0 * half_width
    return {
        "arm": (
            PARTY_PARTITION_BOTTOM_HEIGHT,
            PARTY_PARTITION_BOTTOM_HEIGHT + partition_height,
        ),
        "central": (
            CENTRAL_PARTY_STORAGE_HEIGHT,
            CENTRAL_PARTY_STORAGE_HEIGHT + PARTY_MODULE_THICKNESS,
        ),
    }


def party_arm_mechanism(arm_angle):
    """Return plan points and heights for one lift-and-rotate arm mechanism."""
    seam_radius, length, half_width = party_arm_dimensions()
    party_axis_z = PARTY_SURFACE_HEIGHT - PARTY_MODULE_THICKNESS / 2.0
    stored_axis_z = PARTY_PARTITION_BOTTOM_HEIGHT + half_width
    guide_points = (
        local_to_world(seam_radius, 0.0, arm_angle),
        local_to_world(seam_radius + length, 0.0, arm_angle),
    )
    lock_inset = min(80.0, length / 5.0)
    party_locks = tuple(
        local_to_world(radial, tangential, arm_angle)
        for radial in (seam_radius + lock_inset, seam_radius + length - lock_inset)
        for tangential in (-half_width + lock_inset, half_width - lock_inset)
    )
    return {
        "guide_points": guide_points,
        "axis_start": guide_points[0],
        "axis_end": guide_points[1],
        "party_axis_z": party_axis_z,
        "stored_axis_z": stored_axis_z,
        "rotation_degrees": 90.0,
        "lift_travel": stored_axis_z - party_axis_z,
        "party_lock_points": party_locks,
        "stored_lock_count": 2,
    }


def central_party_mechanism():
    """Return the three-point vertical guide concept for the central module."""
    party_center_z = PARTY_SURFACE_HEIGHT - PARTY_MODULE_THICKNESS / 2.0
    stored_center_z = CENTRAL_PARTY_STORAGE_HEIGHT + PARTY_MODULE_THICKNESS / 2.0
    guide_points = tuple(
        local_to_world(CENTRAL_PARTY_GUIDE_RADIUS, 0.0, angle)
        for angle in (0.0, 120.0, 240.0)
    )
    return {
        "guide_points": guide_points,
        "party_center_z": party_center_z,
        "stored_center_z": stored_center_z,
        "lift_travel": stored_center_z - party_center_z,
        "party_lock_points": guide_points,
        "stored_lock_count": 3,
    }


def _sample_convex_polygon(polygon, steps=12):
    """Sample a convex polygon as a fan of triangles, including its edges."""
    samples = []
    anchor = polygon[0]
    for index in range(1, len(polygon) - 1):
        point_b = polygon[index]
        point_c = polygon[index + 1]
        for row in range(steps + 1):
            weight_b = row / float(steps)
            for column in range(steps - row + 1):
                weight_c = column / float(steps)
                weight_a = 1.0 - weight_b - weight_c
                samples.append((
                    anchor[0] * weight_a + point_b[0] * weight_b + point_c[0] * weight_c,
                    anchor[1] * weight_a + point_b[1] * weight_b + point_c[1] * weight_c,
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
        samples = _sample_convex_polygon(polygon)
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
    for arm_index, arm_angle in enumerate((60.0, 180.0, 300.0), 1):
        lines.append(
            '<polygon id="party-storage-arm-%d" points="%s" fill="#e8bd45" '
            'fill-opacity="0.72" stroke-dasharray="4 3"/>'
            % (arm_index, point_list(party_storage_arm_polygon(arm_angle)))
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
        '<text x="520" y="300" stroke="none">primary depth %.0f mm</text>' % WORK_DEPTH,
        '<text x="500" y="495" text-anchor="middle" stroke="none">technical channel %.0f mm</text>'
        % TECH_CHANNEL_WIDTH,
        '<text x="500" y="965" text-anchor="middle" stroke="none">gold dashed: Work storage of party modules</text>',
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
