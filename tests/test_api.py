from custom_components.torque_logger_2025.api import TorqueReceiveDataView


def test_parse_fields_normalizes_pid():
    view = TorqueReceiveDataView({}, "", False)
    session = view.parse_fields({"session": "abc", "kFF1001": "42"})
    assert session == "abc"
    assert view.data["abc"]["value"]["ff1001"] == "42"