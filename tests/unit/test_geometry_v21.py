import math

from cad.generators import geometry_v21 as geometry


def _angle_delta(angle_a, angle_b):
    return abs((angle_a - angle_b + 180.0) % 360.0 - 180.0)


def test_primary_is_driven_by_user_edge_and_usable_depth():
    polygon = geometry.primary_polygon(0.0)
    assert geometry.distance(polygon[1], polygon[2]) == geometry.USER_EDGE_WIDTH
    assert geometry.distance(
        geometry.midpoint(polygon[0], polygon[3]),
        geometry.midpoint(polygon[1], polygon[2]),
    ) == geometry.WORK_DEPTH


def test_all_nine_work_surfaces_have_disjoint_plan_footprints():
    polygons = geometry.desk_polygons()
    assert len(polygons) == 9
    assert geometry.collision_pairs(polygons) == []


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
            assert 800.0 <= monitor["distance"] <= 1100.0
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


def test_svg_plan_contains_the_controlling_dimensions():
    svg = geometry.svg_plan()
    assert 'id="desk-AP"' in svg
    assert 'id="central-party"' in svg
    assert "user edge 800 mm" in svg
    assert "usable depth 550 mm" in svg
    assert "technical channel 400 mm" in svg


def test_chairs_and_straight_entry_corridors_do_not_cross_work_surfaces():
    desks = geometry.desk_polygons()
    for _station, station_angle in geometry.STATIONS:
        chair = geometry.chair_polygon(station_angle)
        corridor = geometry.entry_corridor_polygon(station_angle)
        assert all(not geometry.polygons_overlap(chair, desk) for desk in desks.values())
        assert all(not geometry.polygons_overlap(corridor, desk) for desk in desks.values())


def test_primary_lift_column_stays_out_of_legroom_zone():
    assert geometry.PRIMARY_LEGROOM_DEPTH == 400.0
    assert geometry.PRIMARY_LEGROOM_WIDTH == 600.0
    assert geometry.primary_column_legroom_clearance() >= 20.0
