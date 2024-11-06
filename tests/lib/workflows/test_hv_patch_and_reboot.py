from unittest.mock import MagicMock, patch
import pytest
from workflows.hv_patch_and_reboot import patch_and_reboot


@patch("workflows.hv_patch_and_reboot.schedule_downtime")
@pytest.mark.parametrize(
    "start_time, end_time",
    [
        ("01/12/24 12:00:00", "01/12/24 17:00:00"),
    ],
)
def test_hv_patch_and_reboot(mock_schedule_downtime, start_time, end_time):
    """
    Test the patch and reboot action on a hypervisor
    """
    icinga_account = MagicMock()
    name = "example_host"
    comment = f"starting downtime to patch and reboot host: {name}"

    patch_and_reboot(icinga_account, name, start_time, end_time)
    mock_schedule_downtime.assert_called_once_with(
        icinga_account=icinga_account,
        object_type="Host",
        name=name,
        start_time=start_time,
        end_time=end_time,
        is_fixed=True,
        comment=comment,
    )
