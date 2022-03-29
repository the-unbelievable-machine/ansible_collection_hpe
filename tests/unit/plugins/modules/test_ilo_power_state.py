from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest

from ansible_collections.unbelievable.hpe.plugins.modules.ilo_power_state import ILOPowerState  # type: ignore # noqa: E501


@pytest.mark.parametrize(
    "current_state, action, expected",
    [
        ("Off", "On", True),
        ("Off", "ForceRestart", True),
        ("Off", "PushPowerButton", True),
        ("Off", "GracefulRestart", True),
        ("Off", "ForceOff", False),
        ("Off", "GracefulShutdown", False),
        ("On", "On", False),
        ("On", "ForceRestart", True),
        ("On", "PushPowerButton", True),
        ("On", "GracefulRestart", True),
        ("On", "ForceOff", True),
        ("On", "GracefulShutdown", True),
    ],
)
def test_change_required(current_state, action, expected):
    result = ILOPowerState.change_required(current_state, action)
    assert expected == result
