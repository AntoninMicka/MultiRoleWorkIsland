import math

from cad.generators import geometry_v30 as geometry


def _angle_delta(angle_a, angle_b):
    return abs((angle_a - angle_b + 180.0) % 360.0 - 180.0)


def test_primary_is_driven_by_user_edge_and_usable_depth():
    polygon = geometry.primary_polygon(0.0)
    assert geometry.WORK_DEPTH == 400.0
    assert geometry.distance(polygon[1], polygon[2]) == geometry.USER_EDGE_WIDTH
    assert geometry.distance(
        geometry.midpoint(polygon[0], polygon[3]),
        geometry.midpoint(polygon[1], polygon[2]),
    ) == geometry.WORK_DEPTH


def test_all_nine_work_surfaces_have_disjoint_plan_footprints():
    polygons = geometry.desk_polygons()
    assert len(polygons) == 9
    assert geometry.collision_pairs(polygons) == []


def test_front_and_rear_edges_are_parallel_on_every_desk():
    assert geometry.nonparallel_desk_edges() == []


def test_all_worktops_share_the_configured_front_to_rear_depth():
    assert geometry.WORK_DEPTH == geometry.SIDE_DESK_WIDTH == 400.0
    for _station, station_angle in geometry.STATIONS:
        for kind in ("S", "T"):
            front, rear = geometry.desk_front_rear_edges(
                kind, geometry.side_polygon(kind, station_angle)
            )
            arm_delta, _channel_edge, _outer_edge = geometry._side_lane(kind)
            front_local = geometry.rotate_point(front[0], -(station_angle + arm_delta))
            rear_local = geometry.rotate_point(rear[0], -(station_angle + arm_delta))
            assert math.isclose(
                abs(front_local[1] - rear_local[1]),
                geometry.WORK_DEPTH,
                abs_tol=1e-9,
            )


def test_side_desks_continue_primary_edges_without_transition_segments():
    for _station, station_angle in geometry.STATIONS:
        primary = geometry.primary_polygon(station_angle)
        secondary = geometry.side_polygon("S", station_angle)
        tertiary = geometry.side_polygon("T", station_angle)
        assert secondary[0] == primary[3]
        assert secondary[3] == primary[2]
        assert tertiary[0] == primary[0]
        assert tertiary[3] == primary[1]
        assert len(secondary) == len(tertiary) == 4


def test_side_desks_bound_a_300_mm_technical_channel():
    assert geometry.TECH_CHANNEL_WIDTH == 300.0
    assert geometry.technical_channel_edge_failures() == []
    for _station, station_angle in geometry.STATIONS:
        for kind in ("S", "T"):
            arm_delta, channel_edge, _outer_edge = geometry._side_lane(kind)
            polygon = geometry.side_polygon(kind, station_angle)
            for point in polygon[0:2]:
                local = geometry.rotate_point(point, -(station_angle + arm_delta))
                assert math.isclose(local[1], channel_edge, abs_tol=1e-9)


def test_side_monitors_face_their_station_user_instead_of_arm_axis():
    for _station, station_angle in geometry.STATIONS:
        user = geometry.user_position(station_angle)
        for kind, arm_delta in (("S", 60.0), ("T", -60.0)):
            x, y, facing = geometry.monitor_pose(kind, station_angle)
            expected = math.degrees(math.atan2(user[1] - y, user[0] - x))
            assert _angle_delta(facing, expected) < 1e-9
            assert _angle_delta(facing, station_angle + arm_delta) > 20.0


def test_all_monitors_have_reviewable_distance_and_do_not_mask_each_other():
    for _station, station_angle in geometry.STATIONS:
        review = geometry.monitor_review(station_angle)
        for monitor in review.values():
            assert 1000.0 <= monitor["distance"] <= 1400.0
        for kind_a, kind_b in (("P", "S"), ("P", "T"), ("S", "T")):
            monitor_a = review[kind_a]
            monitor_b = review[kind_b]
            separation = geometry.angular_separation(
                monitor_a["sight_angle"], monitor_b["sight_angle"]
            )
            assert separation > (
                monitor_a["half_angular_span"] + monitor_b["half_angular_span"]
            )


def test_central_party_outline_is_threefold_symmetric_and_not_regular():
    polygon = geometry.central_party_polygon()
    edge_lengths = [
        geometry.distance(start, end)
        for start, end in geometry.polygon_edges(polygon)
    ]
    user_edges = [length for length in edge_lengths if abs(length - 800.0) < 1e-7]
    joining_edges = [length for length in edge_lengths if abs(length - 800.0) >= 1e-7]
    assert len(user_edges) == 3
    assert len(joining_edges) == 3
    assert max(joining_edges) - min(joining_edges) < 1e-7
    assert abs(joining_edges[0] - 800.0) > 10.0


def test_party_layer_has_one_central_and_three_nonoverlapping_arm_modules():
    modules = geometry.party_module_polygons()
    assert sorted(modules) == ["CENTRAL_TOP", "PARTY_ARM_1", "PARTY_ARM_2", "PARTY_ARM_3"]
    assert geometry.collision_pairs(modules) == []


def test_party_module_seams_close_exactly_and_cover_work_layout():
    assert geometry.party_seam_failures() == []
    assert geometry.party_coverage_failures() == []


def test_party_surface_height_is_700_mm():
    assert geometry.PARTY_SURFACE_HEIGHT == 700.0


def test_work_storage_uses_vertical_arm_partitions_and_overhead_central_module():
    ranges = geometry.party_storage_ranges()
    _seam_radius, length, half_width = geometry.party_arm_dimensions()
    assert ranges["arm"] == (780.0, 1880.0)
    assert ranges["central"] == (1900.0, 1940.0)
    assert ranges["central"][0] - ranges["arm"][1] == 20.0
    for arm_angle in (60.0, 180.0, 300.0):
        footprint = geometry.party_storage_arm_polygon(arm_angle)
        edge_lengths = sorted(
            geometry.distance(start, end)
            for start, end in geometry.polygon_edges(footprint)
        )
        assert math.isclose(edge_lengths[0], geometry.PARTY_MODULE_THICKNESS)
        assert math.isclose(edge_lengths[-1], length)
        assert math.isclose(2.0 * half_width, 1100.0)


def test_party_arm_mechanism_has_two_guides_rotation_and_independent_locks():
    for arm_angle in (60.0, 180.0, 300.0):
        spec = geometry.party_arm_mechanism(arm_angle)
        assert len(spec["guide_points"]) == 2
        assert spec["rotation_degrees"] == 90.0
        assert spec["lift_travel"] == 650.0
        assert len(spec["party_lock_points"]) == 4
        assert spec["stored_lock_count"] == 2
        for point in spec["guide_points"]:
            local = geometry.rotate_point(point, -arm_angle)
            assert math.isclose(local[1], 0.0, abs_tol=1e-9)


def test_central_party_mechanism_has_three_synchronized_guides_and_locks():
    spec = geometry.central_party_mechanism()
    assert len(spec["guide_points"]) == 3
    assert len(spec["party_lock_points"]) == 3
    assert spec["stored_lock_count"] == 3
    assert spec["lift_travel"] == 1240.0
    for point in spec["guide_points"]:
        assert math.isclose(
            geometry.distance((0.0, 0.0), point),
            geometry.CENTRAL_PARTY_GUIDE_RADIUS,
            abs_tol=1e-9,
        )


def test_party_svg_names_all_four_modules():
    svg = geometry.svg_party_plan()
    assert 'id="central_top"' in svg
    assert 'id="party_arm_1"' in svg
    assert 'id="party_arm_2"' in svg
    assert 'id="party_arm_3"' in svg
    assert "top 700 mm" in svg


def test_svg_plan_contains_the_controlling_dimensions():
    svg = geometry.svg_plan()
    assert 'id="desk-AP"' in svg
    assert 'id="central-party"' in svg
    assert 'id="party-storage-arm-1"' in svg
    assert 'id="party-storage-arm-2"' in svg
    assert 'id="party-storage-arm-3"' in svg
    assert 'id="monitor-AP"' in svg
    assert 'id="monitor-lift-AS"' in svg
    assert "user edge 800 mm" in svg
    assert "primary depth 400 mm" in svg
    assert "technical channel 300 mm" in svg


def test_chairs_and_straight_entry_corridors_do_not_cross_work_surfaces():
    desks = geometry.desk_polygons()
    for _station, station_angle in geometry.STATIONS:
        chair = geometry.chair_polygon(station_angle)
        corridor = geometry.entry_corridor_polygon(station_angle)
        assert all(not geometry.polygons_overlap(chair, desk) for desk in desks.values())
        assert all(not geometry.polygons_overlap(corridor, desk) for desk in desks.values())


def test_primary_lift_column_stays_out_of_legroom_zone():
    assert geometry.PRIMARY_LEGROOM_DEPTH == (
        geometry.WORK_DEPTH - geometry.PRIMARY_REAR_SUPPORT_ZONE_DEPTH
    )
    assert geometry.PRIMARY_LEGROOM_DEPTH == 250.0
    assert geometry.PRIMARY_LEGROOM_WIDTH == 600.0
    assert geometry.primary_column_legroom_clearance() >= 20.0


def test_monitor_lifts_and_bodies_are_behind_desks_without_collisions():
    assert geometry.monitor_lift_desk_collisions() == []
    assert geometry.monitor_body_desk_collisions() == []
    assert geometry.monitor_body_collisions() == []


def test_monitor_arc_has_target_gap_between_adjacent_frames():
    for _station, station_angle in geometry.STATIONS:
        primary = geometry.monitor_body_polygon("P", station_angle)
        for kind in ("S", "T"):
            side = geometry.monitor_body_polygon(kind, station_angle)
            gap = geometry.polygon_clearance(primary, side)
            assert 20.0 <= gap <= 40.0


def test_side_monitor_lifts_use_the_technical_channel():
    assert geometry.TECH_CHANNEL_WIDTH == 300.0
    for _station, station_angle in geometry.STATIONS:
        for kind in ("S", "T"):
            arm_delta, _channel_edge, _outer_edge = geometry._side_lane(kind)
            x, y = geometry.monitor_lift_position(kind, station_angle)
            local = geometry.rotate_point((x, y), -(station_angle + arm_delta))
            assert (
                abs(local[1]) + geometry.MONITOR_LIFT_RADIUS
                <= geometry.TECH_CHANNEL_WIDTH / 2.0
            )
            monitor_x, monitor_y, _facing = geometry.monitor_pose(kind, station_angle)
            expected_translation = math.hypot(
                geometry.SIDE_LIFT_RADIUS - geometry.SIDE_MONITOR_RADIUS,
                geometry.SIDE_MONITOR_CHANNEL_OFFSET - geometry.SIDE_LIFT_CHANNEL_OFFSET,
            )
            assert math.isclose(
                geometry.distance((x, y), (monitor_x, monitor_y)),
                expected_translation,
                abs_tol=1e-9,
            )
