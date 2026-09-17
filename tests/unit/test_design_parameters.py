import math

import pytest

from cad.generators import design_parameters
from cad.generators import geometry_v30 as geometry


def test_repository_configuration_matches_current_design():
    values = design_parameters.load_parameters()
    assert values["primary_depth"] == 400.0
    assert values["technical_channel_width"] == 300.0
    assert values["side_desk_length"] == 1200.0
    assert values["party_arm_length"] == 1200.0
    assert values["party_arm_length"] >= values["side_desk_length"]
    assert design_parameters.validate_parameters(values) == []


def test_configuration_round_trips_as_toml(tmp_path):
    path = tmp_path / "design_parameters.toml"
    values = dict(design_parameters.DEFAULTS)
    values["primary_depth"] = 425.0
    design_parameters.save_parameters(values, str(path))
    loaded = design_parameters.load_parameters(str(path))
    assert loaded == values
    assert "[geometry]" in path.read_text(encoding="utf-8")


def test_invalid_lift_channel_relationship_is_rejected():
    values = dict(design_parameters.DEFAULTS)
    values["technical_channel_width"] = 200.0
    values["side_lift_offset"] = 95.0
    values["monitor_lift_diameter"] = 90.0
    errors = design_parameters.validate_parameters(values)
    assert any("Lift S/T má k desce" in error for error in errors)


def test_party_mechanism_must_fit_inside_technical_channel():
    values = dict(design_parameters.DEFAULTS)
    values["party_guide_diameter"] = values["technical_channel_width"] + 1.0
    errors = design_parameters.validate_parameters(values)
    assert any("Vedení Party" in error for error in errors)


def test_party_arm_must_not_be_shorter_than_work_wing():
    values = dict(design_parameters.DEFAULTS)
    values["side_desk_length"] = 1200.0
    values["party_arm_length"] = 1199.0
    errors = design_parameters.validate_parameters(values)
    assert any("Délka Party ramene" in error for error in errors)


def test_geometry_recalculates_linked_values_from_inputs():
    original = dict(geometry.PARAMETERS)
    changed = dict(original)
    changed["primary_depth"] = 420.0
    changed["technical_channel_width"] = 320.0
    changed["side_desk_length"] = 1100.0
    changed["party_arm_length"] = 1350.0
    try:
        geometry.apply_parameters(changed)
        assert geometry.WORK_DEPTH == 420.0
        assert geometry.SIDE_DESK_WIDTH == 420.0
        assert geometry.TECH_CHANNEL_WIDTH == 320.0
        assert geometry.SIDE_DESK_LENGTH == 1100.0
        assert geometry.PARTY_ARM_LENGTH == 1350.0
        assert math.isclose(
            geometry.distance(
                geometry.side_polygon("S", 0.0)[0],
                geometry.side_polygon("S", 0.0)[1],
            ),
            1100.0,
            abs_tol=1e-9,
        )
        assert geometry.party_arm_dimensions()[1] == 1350.0
        assert geometry.party_seam_failures() == []
        assert geometry.party_coverage_failures() == []
        assert geometry.collision_pairs(geometry.party_module_polygons()) == []
        assert geometry.USER_RADIUS == (
            geometry.PRIMARY_INNER_RADIUS
            + changed["primary_depth"]
            + changed["user_clearance"]
        )
        front, rear = geometry.desk_front_rear_edges("S", geometry.side_polygon("S", 0.0))
        arm_delta, _channel_edge, _outer_edge = geometry._side_lane("S")
        front_local = geometry.rotate_point(front[0], -arm_delta)
        rear_local = geometry.rotate_point(rear[0], -arm_delta)
        assert math.isclose(abs(front_local[1] - rear_local[1]), 420.0, abs_tol=1e-9)
        assert geometry.technical_channel_edge_failures() == []
    finally:
        geometry.apply_parameters(original)


def test_save_refuses_invalid_parameters(tmp_path):
    values = dict(design_parameters.DEFAULTS)
    values["party_module_thickness"] = values["party_surface_height"]
    with pytest.raises(ValueError, match="Tloušťka party modulu"):
        design_parameters.save_parameters(values, str(tmp_path / "invalid.toml"))
